/**
 * Prediction page
 *
 * Two prediction paths backed by the FastAPI service:
 *   • Surrogate (POST /predict)   — fast (~50 ms), conformal PI + OOD flag
 *   • Authoritative (POST /run-cgem) — Fortran subprocess (~3 s), full
 *     time-series + event scalars
 *
 * The form (profile picker + pilot config + countermeasures) drives both
 * paths. The page reports backend unavailability without inventing physiology.
 */

import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  Brain,
  Eye,
  FlaskConical,
  Play,
  Settings,
  User,
  Zap,
} from 'lucide-react';

import {
  MetricCard,
  OODBanner,
  PredictionTable,
  ProfileSelector,
} from '../components/ui';
import { GForceLineChart, CerebralFlowChart } from '../components/charts';
import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../data/maneuvers';
import { STANDARD_PROFILES, DEFAULT_COUNTERMEASURES } from '../utils/constants';
import { buildTimeSeries } from '../utils/calculations';
import type { CGEMResult } from '../types';
import {
  apiErrorMessage,
  cgemApiBaseURL,
  usePredict,
  useRunCgem,
  useVersion,
} from '../services/cgemApi';
import type {
  CGEMRunResponse,
  PilotConfigRequest,
  PredictionRequest,
  PredictionResponse,
} from '../services/types';
import { pilotConfigFromPrefs, pilotConfigWithOverrides } from '../services/pilotConfig';
import { useUserPrefs } from '../state/useUserPrefs';

/** Map the local Countermeasures + who_profile to a PredictionRequest body. */
function buildRequest(
  selectedProfileId: string,
  basePilot: PilotConfigRequest,
  whoProfile: number | null,
  cm: typeof DEFAULT_COUNTERMEASURES,
): PredictionRequest {
  return {
    maneuver: { maneuver: selectedProfileId },
    pilot: pilotConfigWithOverrides(basePilot, {
      who_profile: whoProfile,
      dehydration_level: cm.dehydration_level,
      gsuit_max_psi: cm.gsuit_max_psi,
      gsuit_coverage_fraction: cm.gsuit_coverage_fraction,
      agsm_effectiveness: cm.agsm_effectiveness,
      pbg_max_mmhg: cm.pbg_max_mmhg ?? 0,
    }),
  };
}

/** Adapt a CGEMRunResponse into the shape the legacy charts expect. */
function adaptCGEMRunToResult(r: CGEMRunResponse): CGEMResult {
  return {
    time_to_greyout_s: r.time_to_greyout_s,
    time_to_blackout_s: r.time_to_blackout_s,
    time_to_gloc_s: r.time_to_gloc_s,
    times_s: r.data['Time(s)'],
    g_values: r.data.G,
    geff_values: r.data.G_eff,
    flags_n2: r.data.Conscious,
    flags_ne2: r.data.Greyout,
    flags_non2: r.data.Blackout,
    c_bank_values: r.data['c_bank(s)'],
    bo_bank_values: r.data['bo_bank(s)'],
    f_con_values: r.data['F_con(dl/min)'],
    f_vis_values: r.data['F_vis(dl/min)'],
    f_bo_values: r.data['F_bo(dl/min)'],
    hlap_values: r.data['HLAP(mmHg)'],
  };
}

const formatTime = (t: number | null | undefined): string =>
  t === null || t === undefined ? '—' : `${t.toFixed(2)}s`;

export const PredictionPage: React.FC = () => {
  const prefs = useUserPrefs();
  const preferredPilot = useMemo(() => pilotConfigFromPrefs(prefs), [prefs]);
  const [selectedProfileId, setSelectedProfileId] = useState('high_g_turn');
  const [whoProfile, setWhoProfile] = useState<number | null>(preferredPilot.who_profile);
  const [countermeasures, setCountermeasures] = useState({
    ...DEFAULT_COUNTERMEASURES,
    ...prefs.defaults,
  });

  const profile = AEROBATIC_PROFILES[selectedProfileId];
  const selectedStandardProfile = STANDARD_PROFILES.find((p) => p.id === whoProfile);

  const versionQuery = useVersion();
  const predictMutation = usePredict();
  const runCgemMutation = useRunCgem();

  const requestBody = useMemo(
    () => buildRequest(selectedProfileId, preferredPilot, whoProfile, countermeasures),
    [selectedProfileId, preferredPilot, whoProfile, countermeasures],
  );

  const handlePredict = () => {
    predictMutation.mutate(requestBody);
  };

  const handleRunCgem = () => {
    runCgemMutation.mutate({
      maneuver: selectedProfileId,
      pilot: requestBody.pilot,
    });
  };

  const prediction: PredictionResponse | undefined = predictMutation.data;
  const cgemRun: CGEMResult | null = runCgemMutation.data
    ? adaptCGEMRunToResult(runCgemMutation.data)
    : null;

  const apiReachable = !versionQuery.isError;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              CGEM Physiological Prediction
            </h2>
            <p className="text-surface-400 max-w-3xl">
              Configure pilot parameters and run the surrogate emulator
              (fast) or invoke the validated FAA Fortran binary
              (authoritative). Both paths share the same form below.
            </p>
          </div>
          <div className="text-xs text-surface-400 text-right space-y-1">
            <div>
              <span className="text-surface-500">API:</span>{' '}
              <code className="text-surface-300">{cgemApiBaseURL}</code>
            </div>
            <div>
              <span className="text-surface-500">Status:</span>{' '}
              {versionQuery.isLoading ? (
                <span className="text-amber-400">connecting…</span>
              ) : versionQuery.isError ? (
                <span className="text-rose-400">unreachable</span>
              ) : (
                <span className="text-emerald-400">
                  v{versionQuery.data?.package_version} ·{' '}
                  {versionQuery.data?.cgem_binary_sha256.slice(0, 8)}…
                </span>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Configuration panel ──────────────────────────────── */}
        <div className="lg:col-span-1 space-y-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-400" />
              Maneuver Profile
            </h3>
            <ProfileSelector
              selectedProfileId={selectedProfileId}
              onSelect={setSelectedProfileId}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-accent-400" />
              Subject Profile
            </h3>
            <select
              value={whoProfile ?? 'custom'}
              onChange={(e) =>
                setWhoProfile(e.target.value === 'custom' ? null : parseInt(e.target.value))
              }
              className="select-field w-full"
            >
              <option value="custom">Custom Configuration</option>
              {STANDARD_PROFILES.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} (who={p.id})
                </option>
              ))}
            </select>
            {selectedStandardProfile && (
              <div className="bg-surface-800/50 rounded-lg p-3 mt-3 text-sm space-y-1">
                <p className="text-surface-300">
                  <span className="text-surface-500">Sex:</span>{' '}
                  {selectedStandardProfile.male === 1 ? 'Male' : 'Female'}
                </p>
                <p className="text-surface-300">
                  <span className="text-surface-500">Height:</span>{' '}
                  {selectedStandardProfile.howtall} cm
                </p>
                <p className="text-surface-300">
                  <span className="text-surface-500">Baseline BP:</span>{' '}
                  {selectedStandardProfile.BSP}/{selectedStandardProfile.BDP} mmHg
                </p>
              </div>
            )}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-warning-400" />
              Countermeasures
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  G-suit pressure (PSI)
                </label>
                <input
                  type="range"
                  min={0}
                  max={10}
                  step={0.5}
                  value={countermeasures.gsuit_max_psi}
                  onChange={(e) =>
                    setCountermeasures({
                      ...countermeasures,
                      gsuit_max_psi: parseFloat(e.target.value),
                    })
                  }
                  className="w-full"
                />
                <span className="text-sm text-surface-400">
                  {countermeasures.gsuit_max_psi} PSI
                </span>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  AGSM effectiveness
                </label>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={countermeasures.agsm_effectiveness}
                  onChange={(e) =>
                    setCountermeasures({
                      ...countermeasures,
                      agsm_effectiveness: parseFloat(e.target.value),
                    })
                  }
                  className="w-full"
                />
                <span className="text-sm text-surface-400">
                  {(countermeasures.agsm_effectiveness * 100).toFixed(0)} %
                </span>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Dehydration level
                </label>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={countermeasures.dehydration_level}
                  onChange={(e) =>
                    setCountermeasures({
                      ...countermeasures,
                      dehydration_level: parseFloat(e.target.value),
                    })
                  }
                  className="w-full"
                />
                <span className="text-sm text-surface-400">
                  {(countermeasures.dehydration_level * 100).toFixed(0)} %
                </span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <button
              onClick={handlePredict}
              disabled={!apiReachable || predictMutation.isPending}
              className="btn-primary w-full"
            >
              {predictMutation.isPending ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Running surrogate…
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Predict (surrogate, fast)
                </>
              )}
            </button>
            <button
              onClick={handleRunCgem}
              disabled={!apiReachable || runCgemMutation.isPending}
              className="btn-secondary w-full"
            >
              {runCgemMutation.isPending ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Running CGEM…
                </>
              ) : (
                <>
                  <FlaskConical className="w-5 h-5" />
                  Run authoritative CGEM
                </>
              )}
            </button>
            {!apiReachable && (
              <p className="text-xs text-rose-400 text-center">
                API unreachable. Start it via{' '}
                <code>uvicorn cgem_ext.api.main:app</code>.
              </p>
            )}
          </motion.div>
        </div>

        {/* ── Results panel ────────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-6">
          {prediction && (
            <>
              <OODBanner
                ood={prediction.ood}
                oodScore={prediction.ood_score}
                modelVersion={prediction.model_version}
              />
              <PredictionTable targets={prediction.targets} />
            </>
          )}

          {predictMutation.isError && (
            <div className="glass-light rounded-xl p-4 text-sm border border-rose-500/30">
              <p className="text-rose-300 font-semibold mb-1">Surrogate request failed</p>
              <p className="text-surface-400">{apiErrorMessage(predictMutation.error)}</p>
            </div>
          )}

          {/* Authoritative CGEM event-time cards */}
          {cgemRun && (
            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              className="grid grid-cols-3 gap-4"
            >
              <MetricCard
                label="Time to Greyout"
                value={formatTime(cgemRun.time_to_greyout_s)}
                icon={<Eye className="w-5 h-5 text-surface-400" />}
                color={cgemRun.time_to_greyout_s !== null ? 'warning' : 'default'}
              />
              <MetricCard
                label="Time to Blackout"
                value={formatTime(cgemRun.time_to_blackout_s)}
                icon={<Eye className="w-5 h-5 text-danger-400" />}
                color={cgemRun.time_to_blackout_s !== null ? 'danger' : 'default'}
              />
              <MetricCard
                label="Time to G-LOC"
                value={formatTime(cgemRun.time_to_gloc_s)}
                icon={<Brain className="w-5 h-5 text-purple-400" />}
                color={cgemRun.time_to_gloc_s !== null ? 'danger' : 'default'}
              />
            </motion.div>
          )}

          {runCgemMutation.isError && (
            <div className="glass-light rounded-xl p-4 text-sm border border-rose-500/30">
              <p className="text-rose-300 font-semibold mb-1">CGEM subprocess failed</p>
              <p className="text-surface-400">{apiErrorMessage(runCgemMutation.error)}</p>
            </div>
          )}

          {/* G-Force chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="chart-container"
          >
            <div className="chart-title">
              <Activity className="w-5 h-5 text-primary-400" />
              G-force profile with G_eff
            </div>
            {cgemRun ? (
              <GForceLineChart
                times={cgemRun.times_s}
                gValues={cgemRun.g_values}
                geffValues={cgemRun.geff_values}
                title="Predicted G and effective G vs time (Fortran)"
                height={350}
              />
            ) : profile ? (
              <GForceLineChart
                times={buildTimeSeries(profile.samples).times}
                gValues={buildTimeSeries(profile.samples).gValues}
                title={profile.id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                height={350}
              />
            ) : (
              <div className="h-[350px] flex items-center justify-center text-surface-400">
                Select a profile and run a prediction
              </div>
            )}
          </motion.div>

          {/* Cerebral flow chart — requires a CGEM run */}
          {cgemRun && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="chart-container"
            >
              <div className="chart-title">
                <Brain className="w-5 h-5 text-accent-400" />
                Cerebral blood flow
              </div>
              <CerebralFlowChart result={cgemRun} height={350} />
            </motion.div>
          )}

          {!prediction && !cgemRun && !predictMutation.isPending && !runCgemMutation.isPending && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-light rounded-xl p-6 text-center"
            >
              <Play className="w-12 h-12 text-primary-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">Ready to run</h3>
              <p className="text-surface-400 max-w-md mx-auto">
                Click <strong>Predict</strong> for a fast surrogate result with
                conformal PI + OOD flag, or <strong>Run authoritative CGEM</strong>
                {' '}for a full Fortran-binary simulation with time-series.
              </p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Footer / references */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="glass-light rounded-xl p-4 text-sm text-surface-400 flex items-start gap-3"
      >
        <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
        <p>
          The surrogate emulator and OOD detector are validated against
          <code className="text-surface-300"> cgem_synthetic_v1</code>, not
          centrifuge subjects. See{' '}
          <a
            href="https://doi.org/10.21949/1524446"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-400 hover:underline"
          >
            Copeland & Whinnery (2023)
          </a>{' '}
          for the validated CGEM Fortran model.
        </p>
      </motion.div>
    </div>
  );
};

export default PredictionPage;
