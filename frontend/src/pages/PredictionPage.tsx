/**
 * Prediction Page — Phase-6 wiring
 *
 * Two prediction paths backed by the FastAPI service:
 *   • Surrogate (POST /predict)   — fast (~50 ms), conformal PI + OOD flag
 *   • Authoritative (POST /run-cgem) — Fortran subprocess (~3 s), full
 *     time-series + event scalars
 *
 * The form (profile picker + pilot config + countermeasures) drives both
 * paths. The page reports backend unavailability without inventing physiology.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
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
import { EvidenceRail } from '../components/ui/EvidenceRail';
import { useResultActions } from '../components/ui/ResultActions';
import { GForceLineChart, CerebralFlowChart } from '../components/charts';
import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../data/maneuvers';
import { STANDARD_PROFILES, DEFAULT_COUNTERMEASURES } from '../utils/constants';
import { buildTimeSeries } from '../utils/calculations';
import type { CGEMResult } from '../types';
import {
  apiErrorMessage,
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
import { predictionUrlState, type PredictionView } from '../services/urlState';
import { buildAuthoritativeJsonExport, buildPredictionJsonExport } from '../services/exportResult';
import { predictionRunAnnouncement } from './asyncStatus';

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
  const [searchParams, setSearchParams] = useSearchParams();
  const urlState = predictionUrlState.read(searchParams);
  const { maneuver: selectedProfileId, pilot: whoProfile, view } = urlState.value;
  const [customProfile, setCustomProfile] = useState(false);
  const effectiveWhoProfile = customProfile ? null : whoProfile;
  const updateUrl = (patch: Partial<typeof urlState.value>, replace = false) => setSearchParams(
    predictionUrlState.write({ ...urlState.value, ...patch }), { replace },
  );
  const setSelectedProfileId = (maneuver: string) => updateUrl({ maneuver });
  const setWhoProfile = (pilot: number) => updateUrl({ pilot });
  const setView = (nextView: PredictionView) => updateUrl({ view: nextView }, true);
  const [countermeasures, setCountermeasures] = useState({
    ...DEFAULT_COUNTERMEASURES,
    ...prefs.defaults,
  });

  const profile = AEROBATIC_PROFILES[selectedProfileId];
  const selectedStandardProfile = STANDARD_PROFILES.find((p) => p.id === effectiveWhoProfile);

  const versionQuery = useVersion();
  const predictMutation = usePredict();
  const runCgemMutation = useRunCgem();
  const { registerExport } = useResultActions();

  const requestBody = buildRequest(selectedProfileId, preferredPilot, effectiveWhoProfile, countermeasures);

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
  const showSurrogate = view === 'surrogate' || view === 'comparison';
  const showAuthoritative = view === 'authoritative' || view === 'comparison';
  useEffect(() => {
    const spec = showAuthoritative && runCgemMutation.data && runCgemMutation.variables
      ? buildAuthoritativeJsonExport({ run: runCgemMutation.data, request: runCgemMutation.variables, version: versionQuery.data, exportedAt: new Date(runCgemMutation.submittedAt || 0).toISOString() })
      : showSurrogate && prediction && predictMutation.variables
        ? buildPredictionJsonExport({ response: prediction, request: predictMutation.variables, exportedAt: new Date(predictMutation.submittedAt || 0).toISOString() }) : null;
    const unregister = registerExport(spec);
    return typeof unregister === 'function' ? unregister : undefined;
    // Mutation variables are the immutable submitted snapshot; submittedAt/data identify its completion.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showAuthoritative, showSurrogate, runCgemMutation.data, runCgemMutation.submittedAt, prediction, predictMutation.submittedAt, versionQuery.data, registerExport]);

  return (
    <div className="space-y-6">
      <p role="status" aria-live="polite" aria-atomic="true" className="sr-only">
        {predictionRunAnnouncement('surrogate', predictMutation)}{' '}
        {predictionRunAnnouncement('authoritative', runCgemMutation)}
      </p>
      {urlState.invalid.length > 0 && <p role="status" className="sr-only">Unsupported prediction URL settings were replaced with safe defaults.</p>}
      {/* Header */}
      <div
        className="instrument-panel rounded-2xl p-6"
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
              <code className="text-surface-300">{prefs.apiUrl}</code>
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
      </div>

      <div className="grid min-w-0 gap-6 lg:grid-cols-3">
        {/* ── Configuration panel ──────────────────────────────── */}
        <div className="min-w-0 space-y-6 lg:col-span-1">
          <div
            className="instrument-panel rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-400" />
              Maneuver Profile
            </h3>
            <ProfileSelector
              selectedProfileId={selectedProfileId}
              onSelect={setSelectedProfileId}
            />
          </div>

          <div
            className="instrument-panel rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-accent-400" />
              Subject Profile
            </h3>
            <select
              aria-label="Subject profile"
              name="subject-profile"
              value={customProfile ? 'custom' : whoProfile}
              onChange={(e) => {
                if (e.target.value === 'custom') setCustomProfile(true);
                else {
                  setCustomProfile(false);
                  setWhoProfile(parseInt(e.target.value));
                }
              }}
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
          </div>

          <div
            className="instrument-panel rounded-2xl p-5"
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
                  aria-label="G-suit pressure in PSI"
                  name="gsuit-pressure"
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
                  aria-label="AGSM effectiveness"
                  name="agsm-effectiveness"
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
                  aria-label="Dehydration level"
                  name="dehydration-level"
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
          </div>

          <div
            className="space-y-3"
          >
            <fieldset className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              <legend className="sr-only">Result view</legend>
              {(['surrogate', 'authoritative', 'comparison'] as const).map((option) => (
                <button key={option} type="button" aria-pressed={view === option} onClick={() => setView(option)} className="btn-secondary px-2 text-xs">
                  {option}
                </button>
              ))}
            </fieldset>
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
          </div>
        </div>

        {/* ── Results panel ────────────────────────────────────── */}
        <div className="min-w-0 space-y-6 lg:col-span-2">
          {showSurrogate && prediction && (
            <>
              <EvidenceRail evidence={{ kind: 'surrogate', response: prediction }} />
              <OODBanner
                ood={prediction.ood}
                oodScore={prediction.ood_score}
                modelVersion={prediction.model_version}
              />
              <PredictionTable targets={prediction.targets} />
            </>
          )}

          {showSurrogate && predictMutation.isError && (
            <div className="instrument-panel rounded-xl p-4 text-sm border border-rose-500/30">
              <p className="text-rose-300 font-semibold mb-1">Surrogate request failed</p>
              <p className="text-surface-400">{apiErrorMessage(predictMutation.error)}</p>
            </div>
          )}

          {/* Authoritative CGEM event-time cards */}
          {showAuthoritative && cgemRun && (
            <><EvidenceRail evidence={{ kind: 'authoritative', run: runCgemMutation.data!, version: versionQuery.data }} /><div
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
            </div></>
          )}

          {showAuthoritative && runCgemMutation.isError && (
            <div className="instrument-panel rounded-xl p-4 text-sm border border-rose-500/30">
              <p className="text-rose-300 font-semibold mb-1">CGEM subprocess failed</p>
              <p className="text-surface-400">{apiErrorMessage(runCgemMutation.error)}</p>
            </div>
          )}

          {/* G-Force chart */}
          <div
            className="chart-container"
          >
            <div className="chart-title">
              <Activity className="w-5 h-5 text-primary-400" />
              G-force profile with G_eff
            </div>
            {showAuthoritative && cgemRun ? (
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
          </div>

          {/* Cerebral flow chart — requires a CGEM run */}
          {showAuthoritative && cgemRun && (
            <div
              className="chart-container"
            >
              <div className="chart-title">
                <Brain className="w-5 h-5 text-accent-400" />
                Cerebral blood flow
              </div>
              <CerebralFlowChart result={cgemRun} height={350} />
            </div>
          )}

          {!(showSurrogate && prediction) && !(showAuthoritative && cgemRun)
            && !(showSurrogate && predictMutation.isPending)
            && !(showAuthoritative && runCgemMutation.isPending) && (
            <div
              className="instrument-panel rounded-xl p-6 text-center"
            >
              <Play className="w-12 h-12 text-primary-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">Ready to run</h3>
              <p className="text-surface-400 max-w-md mx-auto">
                Click <strong>Predict</strong> for a fast surrogate result with
                conformal PI + OOD flag, or <strong>Run authoritative CGEM</strong>
                {' '}for a full Fortran-binary simulation with time-series.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer / references */}
      <div
        className="instrument-panel rounded-xl p-4 text-sm text-surface-400 flex items-start gap-3"
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
          for the validated CGEM Fortran model and the project ROADMAP for the
          ongoing centrifuge-validation work.
        </p>
      </div>
    </div>
  );
};

export default PredictionPage;
