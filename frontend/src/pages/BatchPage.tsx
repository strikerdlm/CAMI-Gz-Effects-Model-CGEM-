/**
 * Batch Analysis Page — Phase-6 wiring.
 *
 * Sweeps all 72 registered maneuvers through the FastAPI surrogate via
 * a single POST /sweep call. The backend evaluates the trained
 * XGBoost emulator (~50 µs/row) so even with 72 inputs the round-trip
 * is sub-second. Each row carries point + conformal PI + OOD flag,
 * which we project onto a sortable table.
 *
 * Reports a friendly "API unreachable" banner when the backend is offline.
 */

import React, { useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
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
import { batchUrlState, type BatchCategory, type BatchDirection, type BatchOod, type BatchTarget } from '../services/urlState';

interface BatchRow {
  profileId: string;
  prediction: PredictionResponse;
}

type SortKey = BatchTarget;

function getTarget(p: PredictionResponse, name: string) {
  return p.targets.find((t) => t.target === name);
}

// This pure comparator is exported for deterministic ranking tests.
// eslint-disable-next-line react-refresh/only-export-components
export function compareEventRisk(
  a: PredictionResponse,
  b: PredictionResponse,
  targetName: string,
): number {
  const left = getTarget(a, targetName);
  const right = getTarget(b, targetName);
  const probabilityOrder =
    (right?.event_probability ?? -1) - (left?.event_probability ?? -1);
  if (probabilityOrder !== 0) return probabilityOrder;
  const conditionalTimeOrder = (left?.point ?? Infinity) - (right?.point ?? Infinity);
  if (conditionalTimeOrder !== 0) return conditionalTimeOrder;
  return a.resolved_maneuver.localeCompare(b.resolved_maneuver);
}

const STATUS_STYLES: Record<string, string> = {
  'in envelope': 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  OOD: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
};

export const BatchPage: React.FC = () => {
  const profileIds = useMemo(() => Object.keys(AEROBATIC_PROFILES), []);
  const versionQuery = useVersion();
  const sweepMutation = useSweep();
  const [searchParams, setSearchParams] = useSearchParams();
  const parsed = batchUrlState.read(searchParams);
  const { target: sortKey, direction, ood, category } = parsed.value;
  const updateUrl = (patch: Partial<typeof parsed.value>) => setSearchParams(
    batchUrlState.write({ ...parsed.value, ...patch }), { replace: true },
  );

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
    const items = rows.filter(({ profileId, prediction }) =>
      (category === 'all' || AEROBATIC_PROFILES[profileId]?.category === category)
      && (ood === 'all' || (ood === 'ood' ? prediction.ood : !prediction.ood)),
    );
    items.sort((a, b) => {
      let order: number;
      switch (sortKey) {
        case 'profile':
          order = a.profileId.localeCompare(b.profileId); break;
        case 'ood':
          order = Number(b.prediction.ood) - Number(a.prediction.ood); break;
        case 'greyout':
          order = compareEventRisk(a.prediction, b.prediction, 'time_to_greyout_s'); break;
        case 'blackout':
          order = compareEventRisk(a.prediction, b.prediction, 'time_to_blackout_s'); break;
        case 'gloc':
        default:
          order = compareEventRisk(a.prediction, b.prediction, 'time_to_gloc_s');
      }
      return direction === 'desc' ? order : -order;
    });
    return items;
  }, [rows, sortKey, direction, ood, category]);

  const apiReachable = !versionQuery.isError;
  const oodCount = rows.filter((r) => r.prediction.ood).length;

  return (
    <div className="space-y-6">
      {parsed.invalid.length > 0 && <p role="status" className="sr-only">Unsupported batch URL filters were replaced with safe defaults.</p>}
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
              Each row reports conditional point estimate, conformal 95 % PI, event
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

      <div className="glass-light rounded-xl p-3">
        <SortControl sortKey={sortKey} direction={direction} ood={ood} category={category} update={updateUrl} />
      </div>

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
            label="G-LOC probability ≥ 50%"
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
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-800/60 text-xs uppercase tracking-wider text-surface-400">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Maneuver</th>
                  <th className="px-4 py-3 text-right font-medium">Status</th>
                  <th className="px-4 py-3 text-right font-medium">Greyout event probability</th>
                  <th className="px-4 py-3 text-right font-medium">Greyout conditional time if event occurs</th>
                  <th className="px-4 py-3 text-right font-medium">Blackout event probability</th>
                  <th className="px-4 py-3 text-right font-medium">Blackout conditional time if event occurs</th>
                  <th className="px-4 py-3 text-right font-medium">G-LOC event probability</th>
                  <th className="px-4 py-3 text-right font-medium">G-LOC conditional time if event occurs</th>
                  <th className="px-4 py-3 text-right font-medium">OOD score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/40">
                {sortedRows.map(({ profileId, prediction }) => {
                  const status = prediction.ood ? 'OOD' : 'in envelope';
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
                        {fmtProbability(prediction, 'time_to_greyout_s')}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmtConditionalTime(prediction, 'time_to_greyout_s')}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmtProbability(prediction, 'time_to_blackout_s')}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmtConditionalTime(prediction, 'time_to_blackout_s')}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmtProbability(prediction, 'time_to_gloc_s')}
                      </td>
                      <td className="px-4 py-2 text-right tabular-nums text-surface-300">
                        {fmtConditionalTime(prediction, 'time_to_gloc_s')}
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
  direction: BatchDirection;
  ood: BatchOod;
  category: BatchCategory;
  update: (patch: Partial<ReturnType<typeof batchUrlState.read>['value']>) => void;
}> = ({ sortKey, direction, ood, category, update }) => (
  <div className="flex flex-wrap items-center gap-2 text-xs text-surface-400">
    <ArrowDownAZ className="w-4 h-4" />
    <select
      value={sortKey}
      aria-label="Sort target"
      onChange={(e) => update({ target: e.target.value as SortKey })}
      className="bg-surface-800/60 border border-surface-700 rounded-md px-2 py-1 text-surface-200"
    >
      <option value="gloc">Sort: G-LOC risk ↓</option>
      <option value="blackout">Sort: Blackout risk ↓</option>
      <option value="greyout">Sort: Greyout risk ↓</option>
      <option value="ood">Sort: OOD first</option>
      <option value="profile">Sort: profile name</option>
    </select>
    <select aria-label="Sort direction" value={direction} onChange={(e) => update({ direction: e.target.value as BatchDirection })} className="bg-surface-800/60 border border-surface-700 rounded-md px-2 py-1 text-surface-200">
      <option value="desc">Descending</option><option value="asc">Ascending</option>
    </select>
    <select aria-label="OOD filter" value={ood} onChange={(e) => update({ ood: e.target.value as BatchOod })} className="bg-surface-800/60 border border-surface-700 rounded-md px-2 py-1 text-surface-200">
      <option value="all">All envelopes</option><option value="in-envelope">In envelope</option><option value="ood">OOD only</option>
    </select>
    <select aria-label="Maneuver category" value={category} onChange={(e) => update({ category: e.target.value as BatchCategory })} className="bg-surface-800/60 border border-surface-700 rounded-md px-2 py-1 text-surface-200">
      <option value="all">All categories</option><option value="championship">Championship</option><option value="military_acm">Military ACM</option><option value="extreme_post_stall">Extreme/post-stall</option><option value="training">Training</option><option value="conceptual">Conceptual</option>
    </select>
  </div>
);

const fmtProbability = (prediction: PredictionResponse, name: string): string => {
  const target = getTarget(prediction, name);
  return target?.event_probability == null
    ? '—'
    : `${(target.event_probability * 100).toFixed(0)}%`;
};

const fmtConditionalTime = (prediction: PredictionResponse, name: string): string => {
  const target = getTarget(prediction, name);
  return target ? `${target.point.toFixed(2)}s` : '—';
};

export default BatchPage;
