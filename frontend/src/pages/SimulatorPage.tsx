/**
 * Simulator — /simulator
 * --------------------------------------------------------------------
 * Three-column tactical-display layout:
 *   • Left: maneuver picker (71 + 1, grouped by Aresti / military category)
 *   • Center: status strip, kinematic attitude indicator, G-trace player
 *   • Right: live telemetry, /predict-driven T-LOC + 95 % conformal bracket,
 *           OOD status, pilot config snapshot
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  MANEUVERS,
  MANEUVERS_BY_CATEGORY,
  ORDERED_CATEGORIES,
  type Maneuver,
  type ManeuverCategory,
} from '../data/maneuvers';
import { attitudeAtTime } from '../utils/attitude';
import {
  Bezel,
  SegmentReadout,
  RiskBadge,
  StatusStrip,
  AttitudeIndicator,
  GTracePlayer,
} from '../components/hud';
import {
  usePredict,
  useHealth,
  apiErrorMessage,
} from '../services/cgemApi';
import type {
  PredictionRequest,
  TargetPrediction,
} from '../services/types';
import { pilotConfigFromPrefs } from '../services/pilotConfig';
import { useUserPrefs } from '../state/useUserPrefs';
import { readManeuverParam, setSearchParam } from '../services/urlState';
import { EvidenceRail } from '../components/ui/EvidenceRail';
import { useResultActions } from '../components/ui/ResultActions';
import { buildPredictionJsonExport } from '../services/exportResult';

const CATEGORY_LABELS: Record<ManeuverCategory, string> = {
  championship: 'CHAMPIONSHIP',
  military_acm: 'MILITARY ACM',
  extreme_post_stall: 'EXTREME / POST-STALL',
  training: 'TRAINING',
  conceptual: 'CONCEPTUAL',
};

export const SimulatorPage: React.FC = () => {
  const prefs = useUserPrefs();
  const pilot = useMemo(() => pilotConfigFromPrefs(prefs), [prefs]);
  const health = useHealth();
  const apiAlive = health.data?.status === 'ok';

  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = readManeuverParam(searchParams, 'hammerhead');
  const invalidManeuver = searchParams.has('maneuver') && searchParams.get('maneuver') !== selectedId;
  const setSelectedId = (id: string) => setSearchParams(
    setSearchParam(searchParams, 'maneuver', id, 'hammerhead'),
  );

  const maneuver = useMemo<Maneuver>(
    () => MANEUVERS.find((m) => m.id === selectedId) ?? MANEUVERS[0],
    [selectedId],
  );

  const [now, setNow] = useState<{ t: number; g: number }>({ t: 0, g: maneuver.samples[0]?.nz ?? 0 });

  useEffect(() => {
    setNow({ t: 0, g: maneuver.samples[0]?.nz ?? 0 });
  }, [maneuver]);

  const attitude = useMemo(
    () => attitudeAtTime(maneuver, now.t),
    [maneuver, now.t],
  );

  // Fire one /predict per maneuver change.
  const predictMutation = usePredict();
  const { registerExport } = useResultActions();
  const predictionRequest = useMemo<PredictionRequest>(() => ({ pilot, maneuver: { maneuver: maneuver.id } }), [pilot, maneuver.id]);
  useEffect(() => {
    if (!apiAlive) return;
    predictMutation.mutate(predictionRequest);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [maneuver.id, apiAlive, pilot, predictionRequest]);

  const exportSpec = useMemo(() => predictMutation.data && predictMutation.variables ? buildPredictionJsonExport({ response: predictMutation.data, request: predictMutation.variables, exportedAt: new Date(predictMutation.submittedAt || 0).toISOString() }) : null,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [predictMutation.data, predictMutation.submittedAt]);
  useEffect(() => { const unregister = registerExport(exportSpec); return typeof unregister === 'function' ? unregister : undefined; }, [exportSpec, registerExport]);

  const targets = predictMutation.data?.targets ?? [];
  const glocPred: TargetPrediction | undefined = targets.find((t) => t.target === 'time_to_gloc_s');
  const point = glocPred?.point ?? null;
  const lo = glocPred?.lo ?? null;
  const hi = glocPred?.hi ?? null;
  const eventProb = glocPred?.event_probability ?? null;
  const expectedT = glocPred?.expected_time_s ?? null;
  const conformal =
    point != null && lo != null && hi != null
      ? { median_s: point, low_s: lo, high_s: hi, label: '95% PI' }
      : null;

  const ood = predictMutation.data?.ood ?? false;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[260px_1fr_320px] gap-4 min-h-[calc(100vh-120px)]">
      {invalidManeuver && <p role="status" className="sr-only">The requested maneuver was unavailable. Showing hammerhead.</p>}
      {/* Left rail — maneuver picker */}
      <Bezel
        label={`MANEUVER LIBRARY · ${MANEUVERS.length}`}
        className="overflow-y-auto max-h-[calc(100vh-140px)]"
      >
        <div className="flex flex-col gap-4 mt-2">
          {ORDERED_CATEGORIES.map((cat) => (
            <div key={cat}>
              <div className="font-mono text-[10px] tracking-callsign text-hud-amber-dim mb-1 pl-1">
                {CATEGORY_LABELS[cat]} · {MANEUVERS_BY_CATEGORY[cat].length}
              </div>
              <ul className="flex flex-col gap-0.5">
                {MANEUVERS_BY_CATEGORY[cat].map((m) => {
                  const active = m.id === selectedId;
                  return (
                    <li key={m.id}>
                      <button
                        onClick={() => setSelectedId(m.id)}
                        className={
                          'w-full text-left px-2 py-1 rounded-sm font-mono text-xs flex justify-between items-center transition-colors ' +
                          (active
                            ? 'bg-hud-amber/15 text-hud-amber border border-hud-amber/40'
                            : 'border border-transparent text-hud-ink-dim hover:bg-hud-panel-2 hover:text-hud-ink')
                        }
                      >
                        <span className="truncate">{m.id.replace(/_/g, ' ')}</span>
                        <span className="text-[10px] text-hud-phosphor tabular-nums pl-2 whitespace-nowrap">
                          {m.peak_pos_gz >= 0 ? '+' : ''}{m.peak_pos_gz.toFixed(1)}G
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </Bezel>

      {/* Center — instrumentation */}
      <div className="flex flex-col gap-4 min-w-0">
        <StatusStrip
          mode={`SIM · ${maneuver.category.toUpperCase().replace('_', ' ')}`}
          callsign={maneuver.id.toUpperCase()}
        />
        <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-4">
          <Bezel label="ATTITUDE · KINEMATIC" status="caution" className="flex items-center justify-center min-h-[280px]">
            <AttitudeIndicator roll={attitude.roll} pitch={attitude.pitch} size={260} />
          </Bezel>
          <Bezel label="MANEUVER BRIEFING" status="ok" className="text-sm leading-relaxed text-hud-ink-dim">
            <div className="font-condensed text-2xl text-hud-ink mb-2 tracking-wide uppercase">
              {maneuver.id.replace(/_/g, ' ')}
            </div>
            <p className="mb-3">{maneuver.description}</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-xs">
              <div className="text-hud-ink-faint">AIRCRAFT</div>
              <div className="amber">{maneuver.aircraft}</div>
              <div className="text-hud-ink-faint">PEAK +Gz</div>
              <div className="amber">{maneuver.peak_pos_gz.toFixed(1)} G</div>
              <div className="text-hud-ink-faint">PEAK −Gz</div>
              <div className="amber">{maneuver.peak_neg_gz.toFixed(1)} G</div>
              <div className="text-hud-ink-faint">ONSET</div>
              <div className="amber">{maneuver.onset_rate_g_per_s.toFixed(2)} G/s</div>
              <div className="text-hud-ink-faint">DURATION</div>
              <div className="amber">{maneuver.total_duration_s.toFixed(1)} s</div>
              {maneuver.aresti_family != null && (
                <>
                  <div className="text-hud-ink-faint">ARESTI</div>
                  <div className="amber">
                    Fam {maneuver.aresti_family}
                    {maneuver.aresti_code ? ` · ${maneuver.aresti_code}` : ''}
                  </div>
                </>
              )}
              {maneuver.sustained_gz != null && maneuver.sustained_duration_s != null && (
                <>
                  <div className="text-hud-ink-faint">SUSTAINED</div>
                  <div className="amber">
                    {maneuver.sustained_gz.toFixed(1)} G · {maneuver.sustained_duration_s.toFixed(1)} s
                  </div>
                </>
              )}
            </div>
            {maneuver.hemodynamic_concern && (
              <div className="mt-3 pt-3 border-t border-hud-line text-hud-amber text-xs leading-snug">
                <span className="font-bold tracking-callsign">⚠ HEMO</span>
                {' '}
                {maneuver.hemodynamic_concern}
              </div>
            )}
          </Bezel>
        </div>
        <Bezel label="G-TRACE PLAYBACK" status="ok">
          <GTracePlayer
            maneuver={maneuver}
            conformal={conformal}
            height={300}
            onTimeChange={(t, g) => setNow({ t, g })}
          />
        </Bezel>
      </div>

      {/* Right rail — live readouts + prediction */}
      <div className="flex flex-col gap-4">
        {predictMutation.data && <EvidenceRail evidence={{ kind: 'surrogate', response: predictMutation.data }} />}
        <Bezel label="LIVE TELEMETRY" status="ok">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">+Gz NOW</span>
              <SegmentReadout value={now.g} unit="G" tone={now.g > 7 ? 'red' : 'amber'} size="xl" precision={2} width={5} />
            </div>
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">T ELAPSED</span>
              <SegmentReadout value={now.t} unit="s" tone="phosphor" size="md" precision={2} width={6} />
            </div>
          </div>
        </Bezel>

        <Bezel
          label={apiAlive ? 'PREDICTION · /predict' : 'PREDICTION · OFFLINE'}
          status={apiAlive ? (predictMutation.isError ? 'fail' : 'ok') : 'fail'}
        >
          {!apiAlive && (
            <div className="text-hud-red text-xs font-mono leading-relaxed">
              FastAPI service unreachable.<br />
              Start with:<br />
              <span className="amber">uvicorn cgem_ext.api.main:app --reload</span>
            </div>
          )}
          {apiAlive && predictMutation.isPending && (
            <div className="text-hud-amber font-mono text-xs animate-pulse-amber">QUERYING SURROGATE…</div>
          )}
          {apiAlive && predictMutation.isError && (
            <div className="text-hud-red font-mono text-xs">{apiErrorMessage(predictMutation.error)}</div>
          )}
          {apiAlive && predictMutation.isSuccess && glocPred && (
            <div className="space-y-3">
              <div className="flex justify-between items-baseline">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">CONDITIONAL TIME IF EVENT OCCURS</span>
                <SegmentReadout value={point} unit="s" tone="amber" size="lg" precision={1} width={5} />
              </div>
              <div className="flex justify-between items-center">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">95% PREDICTION INTERVAL</span>
                <span className="font-mono text-sm phosphor tabular-nums">
                  [{lo != null ? lo.toFixed(1) : '—'}, {hi != null ? hi.toFixed(1) : '—'}]
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">P × CONDITIONAL TIME</span>
                <SegmentReadout value={expectedT} unit="s" tone="phosphor" size="md" precision={1} width={5} />
              </div>
              <div className="flex justify-between items-center">
                <span className="font-mono text-[10px] text-hud-ink-faint tracking-callsign">EVENT PROBABILITY</span>
                <SegmentReadout value={eventProb} tone="ice" size="md" precision={3} width={5} />
              </div>
              <div className="pt-2 border-t border-hud-line flex justify-center gap-2 flex-wrap">
                {ood && <RiskBadge tier="OOD" />}
              </div>
              <p className="text-[10px] leading-relaxed text-hud-ink-faint font-mono">
                RESEARCH USE ONLY · PROBABILISTIC SURROGATE OUTPUT, NOT AN OBSERVED EVENT OR FLIGHT-SAFETY VERDICT
              </p>
            </div>
          )}
        </Bezel>

        <Bezel label="PILOT CONFIG" status="idle">
          <div className="grid grid-cols-2 gap-x-3 gap-y-1 font-mono text-xs">
            <div className="text-hud-ink-faint">WHO</div><div className="amber">{pilot.who_profile === null ? 'CUSTOM' : `FAA-${pilot.who_profile}`}</div>
            <div className="text-hud-ink-faint">G-SUIT</div><div className="amber">{pilot.gsuit_max_psi} psi · {(pilot.gsuit_coverage_fraction * 100).toFixed(0)}%</div>
            <div className="text-hud-ink-faint">AGSM</div><div className="amber">{pilot.agsm_effectiveness.toFixed(2)}</div>
            <div className="text-hud-ink-faint">PBG</div><div className="amber">{pilot.pbg_max_mmhg} mmHg</div>
            <div className="text-hud-ink-faint">DEHYD</div><div className="amber">{pilot.dehydration_level.toFixed(2)}</div>
            <div className="text-hud-ink-faint">CM</div><div className="amber uppercase">{pilot.countermeasures_label}</div>
          </div>
          <div className="mt-3 text-hud-ink-faint font-mono text-[11px]">
            Edit defaults in <a href="/settings" className="phosphor hover:underline">/settings</a>
          </div>
        </Bezel>
      </div>
    </div>
  );
};
