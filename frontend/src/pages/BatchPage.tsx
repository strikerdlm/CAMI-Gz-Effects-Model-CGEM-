/**
 * Batch Analysis Page — Phase-6 wiring.
 *
 * Sweeps all 72 registered maneuvers through the FastAPI surrogate via
 * a single POST /sweep call. The backend evaluates the trained
 * XGBoost emulator (~50 µs/row) so even with 72 inputs the round-trip
 * is sub-second. Each row carries point + conformal CI + OOD flag,
 * which we project onto a sortable table.
 *
 * Falls back to a friendly "API unreachable" banner when the backend
 * is offline; the legacy mock sweep lives in services/mockData.ts but
 * is no longer the primary data source.
 */

import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  ArrowDownAZ,
  Check,
  Eye,
  Play,
  ShieldAlert,
} from 'lucide-react';

import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../data/maneuvers';
import { cn } from '../utils';
import {
  apiErrorMessage,
  cgemApiBaseURL,
  useSweep,
  useVersion,
} from '../services/cgemApi';
import type {
  PredictionRequest,
  PredictionResponse,
  SweepRequest,
} from '../services/types';

interface BatchRow {
  profileId: string;
  prediction: PredictionResponse;
}

type SortKey = 'profile' | 'gloc' | 'blackout' | 'greyout' | 'ood';

function getTarget(p: PredictionResponse, name: string) {
  return p.targets.find((t) => t.target === name);
}

function expectedTime(p: PredictionResponse, name: string): number | null {
  const t = getTarget(p, name);
  if (!t) return null;
  if (t.censored && t.expected_time_s !== null && t.expected_time_s !== undefined) {
    return t.expected_time_s;
  }
  return t.point;
}

function statusColor(p: PredictionResponse): string {
  const gloc = getTarget(p, 'time_to_gloc_s');
  const blackout = getTarget(p, 'time_to_blackout_s');
  const greyout = getTarget(p, 'time_to_greyout_s');
  const pGloc = gloc?.event_probability ?? 0;
  const pBlackout = blackout?.event_probability ?? 0;
  const pGreyout = greyout?.event_probability ?? 0;
  if (pGloc >= 0.5) return 'danger';
  if (pBlackout >= 0.5) return 'warning';
  if (pGreyout >= 0.5) return 'caution';
  return 'success';
}

const STATUS_STYLES: Record<string, string> = {
  success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  caution: 'bg-yellow-500/15 text-yellow-300 border-yellow-500/30',
  warning: 'bg-orange-500/15 text-orange-300 border-orange-500/30',
  danger: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
};

export const BatchPage: React.FC = () => {
  const profileIds = useMemo(() => Object.keys(AEROBATIC_PROFILES), []);
  const versionQuery = useVersion();
  const sweepMutation = useSweep();
  const [sortKey, setSortKey] = useState<SortKey>('gloc');

  const handleRunSweep = () => {
    const inputs: PredictionRequest[] = profileIds.map((id) => ({
      maneuver: { maneuver: id },
      pilot: {
        who_profile: 2,
        g_tolerance_multiplier: 1.0,
        dehydration_level: 0.0,
        countermeasures_label: 'none',
        gsuit_max_psi: 0.0,
        gsuit_coverage_fraction: 0.0,
        agsm_effectiveness: 0.0,
        pbg_max_mmhg: 0.0,
      },
    }));
    const body: SweepRequest = { inputs };
    sweepMutation.mutate(body);
  };

  const rows: BatchRow[] = useMemo(() => {
    if (!sweepMutation.data) return [];
    return profileIds.map((id, i) => ({
      profileId: id,
      prediction: sweepMutation.data!.results[i],
    }));
  }, [sweepMutation.data, profileIds]);

  const sortedRows = useMemo(() => {
    const items = [...rows];
    items.sort((a, b) => {
      switch (sortKey) {
        case 'profile':
          return a.profileId.localeCompare(b.profileId);
        case 'ood':
          return Number(b.prediction.ood) - Number(a.prediction.ood);
        case 'greyout':
          return (
            (expectedTime(a.prediction, 'time_to_greyout_s') ?? Infinity) -
            (expectedTime(b.prediction, 'time_to_greyout_s') ?? Infinity)
          );
        case 'blackout':
          return (
            (expectedTime(a.prediction, 'time_to_blackout_s') ?? Infinity) -
            (expectedTime(b.prediction, 'time_to_blackout_s') ?? Infinity)
          );
        case 'gloc':
        default:
          return (
            (expectedTime(a.prediction, 'time_to_gloc_s') ?? Infinity) -
            (expectedTime(b.prediction, 'time_to_gloc_s') ?? Infinity)
          );
      }
    });
    return items;
  }, [rows, sortKey]);

  const apiReachable = !versionQuery.isError;
  const oodCount = rows.filter((r) => r.prediction.ood).length;

  return (
    <div className="space-y-6">
      {/* Header + run button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Batch Physiological Analysis
            </h2>
            <p className="text-surface-400 max-w-2xl">
              Sweep all {profileIds.length} registered maneuvers through the
              FastAPI surrogate (POST <code>/sweep</code>) at the default
              pilot configuration (who_profile = 2, no countermeasures).
              Each row reports point estimate, conformal 95 % CI, event
              probability, and OOD flag.
            </p>
            <div className="mt-2 text-xs text-surface-500">
              API: <code className="text-surface-300">{cgemApiBaseURL}</code> ·{' '}
              {versionQuery.isLoading
                ? 'connecting…'
                : versionQuery.isError
                ? 'unreachable'
                : `v${versionQuery.data?.package_version}`}
            </div>
          </div>

          <button
            onClick={handleRunSweep}
            disabled={!apiReachable || sweepMutation.isPending}
            className="btn-primary min-w-[200px]"
          >
            {sweepMutation.isPending ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Sweeping…
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Run All Profiles
              </>
            )}
          </button>
        </div>

        {!apiReachable && (
          <div className="mt-4 glass-light rounded-xl p-3 text-sm border border-rose-500/30 text-rose-300">
            API unreachable. Start it with{' '}
            <code className="text-surface-200">uvicorn cgem_ext.api.main:app</code>.
          </div>
        )}
      </motion.div>

      {/* Sweep error banner */}
      {sweepMutation.isError && (
        <div className="glass-light rounded-xl p-4 text-sm border border-rose-500/30">
          <p className="text-rose-300 font-semibold mb-1">Sweep failed</p>
          <p className="text-surface-400">{apiErrorMessage(sweepMutation.error)}</p>
        </div>
      )}

      {/* Summary cards */}
      {rows.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          <SummaryCard
            label="Maneuvers swept"
            value={String(rows.length)}
            icon={<Activity className="w-5 h-5 text-primary-400" />}
          />
          <SummaryCard
            label="In envelope"
            value={String(rows.length - oodCount)}
            icon={<Check className="w-5 h-5 text-emerald-400" />}
          />
          <SummaryCard
            label="OOD flagged"
            value={String(oodCount)}
            icon={<ShieldAlert className="w-5 h-5 text-amber-400" />}
          />
          <SummaryCard
            label="High G-LOC risk"
            value={String(
              rows.filter(
                (r) =>
                  (getTarget(r.prediction, 'time_to_gloc_s')?.event_probability ?? 0) >= 0.5,
              ).length,
            )}
            icon={<Eye className="w-5 h-5 text-rose-400" />}
          />
        </motion.div>
      )}

      {/* Results table */}
      {rows.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-surface-700/50 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Per-maneuver predictions</h3>
            <SortControl sortKey={sortKey} setSortKey={setSortKey} />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-800/60 text-xs uppercase tracking-wider text-surface-400">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Maneuver</th>
                  <th className="px-4 py-3 text-right font-medium">Status</th>
                  <th className="px-4 py-3 text-right font-medium">Greyout E[t]</th>
                  <th className="px-4 py-3 text-right font-medium">Blackout E[t]</th>
                  <th className="px-4 py-3 text-right font-medium">G-LOC E[t]</th>
                  <th className="px-4 py-3 text-right font-medium">OOD score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/40">
                {sortedRows.map(({ profileId, prediction }) => {
                  const status = statusColor(prediction);
                  return (
                    <tr key={profileId} className="hover:bg-surface-800/30 transition-colors">
                      <td className="px-4 py-2 text-surface-200 font-medium">
                        {profileId.replace(/_/g, ' ')}
                      </td>
                      <td className="px-4 py-2 text-right">
                        <span
                          className={cn(
                            'inline-block px-2 py-0.5 rounded-md text-xs border',
                            STATUS_STYLES[status],
                          )}
                        >
                          {status}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmt(expectedTime(prediction, 'time_to_greyout_s'))}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmt(expectedTime(prediction, 'time_to_blackout_s'))}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmt(expectedTime(prediction, 'time_to_gloc_s'))}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums">
                        <span
                          className={cn(
                            'tabular-nums',
                            prediction.ood ? 'text-amber-300' : 'text-surface-400',
                          )}
                        >
                          {prediction.ood_score.toFixed(1)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Empty state */}
      {rows.length === 0 && !sweepMutation.isPending && !sweepMutation.isError && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-light rounded-xl p-8 text-center"
        >
          <AlertTriangle className="w-10 h-10 text-warning-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">Ready to sweep</h3>
          <p className="text-surface-400 max-w-md mx-auto text-sm">
            Click <strong>Run All Profiles</strong> to send a single
            POST <code>/sweep</code> request with all {profileIds.length}{' '}
            registered maneuvers. The surrogate evaluates them in milliseconds.
          </p>
        </motion.div>
      )}
    </div>
  );
};

const SummaryCard: React.FC<{ label: string; value: string; icon: React.ReactNode }> = ({
  label,
  value,
  icon,
}) => (
  <div className="glass-light rounded-xl p-4 flex items-center gap-3">
    <div className="bg-surface-800/60 rounded-lg p-2">{icon}</div>
    <div>
      <div className="text-xs uppercase tracking-wider text-surface-500">{label}</div>
      <div className="text-2xl font-semibold text-white tabular-nums">{value}</div>
    </div>
  </div>
);

const SortControl: React.FC<{
  sortKey: SortKey;
  setSortKey: (k: SortKey) => void;
}> = ({ sortKey, setSortKey }) => (
  <div className="flex items-center gap-2 text-xs text-surface-400">
    <ArrowDownAZ className="w-4 h-4" />
    <select
      value={sortKey}
      onChange={(e) => setSortKey(e.target.value as SortKey)}
      className="bg-surface-800/60 border border-surface-700 rounded-md px-2 py-1 text-surface-200"
    >
      <option value="gloc">Sort: G-LOC time ↑</option>
      <option value="blackout">Sort: Blackout time ↑</option>
      <option value="greyout">Sort: Greyout time ↑</option>
      <option value="ood">Sort: OOD first</option>
      <option value="profile">Sort: profile name</option>
    </select>
  </div>
);

const fmt = (v: number | null | undefined): string =>
  v === null || v === undefined ? '—' : v.toFixed(2);

export default BatchPage;
