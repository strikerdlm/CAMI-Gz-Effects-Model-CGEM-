import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDownToLine,
  ArrowLeft,
  Check,
  ChevronRight,
  Expand,
  Pause,
  Play,
  RotateCcw,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { Link } from "react-router-dom";
import { cgemHttp } from "../../services/cgemApi";
import {
  AircraftViewport,
  FlightTrace,
  InstrumentDisplay,
} from "./FlightDisplays";
import {
  LESSONS,
  flagLabel,
  initialConfiguration,
  physiologyCaption,
} from "./lessonData";
import {
  sampleFlight,
  samplePhysiology,
  phaseForFrame,
  phaseStartTime,
} from "./timeline";
import type {
  FlightSimulationRequest,
  FlightSimulationResponse,
  SceneOptions,
} from "./types";
import { ExportDialog } from "./ExportDialog";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "@fontsource/ibm-plex-sans/600.css";
import "@fontsource/ibm-plex-mono/400.css";
import "./flight.css";

function errorMessage(error: unknown): string {
  const e = error as {
    response?: {
      data?: { detail?: string | { msg: string; loc: (string | number)[] }[] };
    };
    message?: string;
  };
  const detail = e.response?.data?.detail;
  if (Array.isArray(detail))
    return detail
      .map((d) => `${d.loc.slice(1).join(".")}: ${d.msg}`)
      .join("; ");
  return detail ?? e.message ?? "Unable to generate this lesson.";
}

export default function FlightLab() {
  const [config, setConfig] = useState(initialConfiguration);
  const [simulation, setSimulation] = useState<FlightSimulationResponse | null>(
    null,
  );
  const [submitted, setSubmitted] = useState<FlightSimulationRequest | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [time, setTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [rate, setRate] = useState(1);
  const [settings, setSettings] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [baroDraft, setBaroDraft] = useState("1013.25");
  const [options, setOptions] = useState<SceneOptions>({
    view: "chase",
    showForces: false,
    showTrail: true,
    baroHpa: 1013.25,
  });
  const abort = useRef<AbortController | null>(null);
  const timeRef = useRef(0);
  const lab = useRef<HTMLDivElement>(null);
  const initial = useRef(config);
  const lesson = LESSONS.find((l) => l.id === config.scenario)!;
  const frame = useMemo(
    () => (simulation ? sampleFlight(simulation.frames, time) : null),
    [simulation, time],
  );
  const physiology = useMemo(
    () => samplePhysiology(simulation?.physiology.result, time),
    [simulation, time],
  );
  const phase = simulation
    ? phaseForFrame(simulation.phases, frame)
    : undefined;
  const seek = useCallback((t: number) => {
    setPlaying(false);
    timeRef.current = t;
    setTime(t);
  }, []);
  const generate = useCallback(async (request: FlightSimulationRequest) => {
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    setLoading(true);
    setError("");
    setSimulation(null);
    setPlaying(false);
    setTime(0);
    timeRef.current = 0;
    try {
      const { data } = await cgemHttp.post<FlightSimulationResponse>(
        "/simulate-flight",
        request,
        { signal: controller.signal, timeout: 90_000 },
      );
      if (controller.signal.aborted) return;
      setSimulation(data);
      setSubmitted(request);
    } catch (e) {
      if (!controller.signal.aborted) setError(errorMessage(e));
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => {
      void generate(initial.current);
    }, 0);
    return () => {
      clearTimeout(timer);
      abort.current?.abort();
    };
  }, [generate]);
  useEffect(() => {
    if (!playing || !simulation) return;
    let id = 0,
      last = performance.now(),
      t = timeRef.current;
    const step = (now: number) => {
      t = Math.min(simulation.duration_s, t + ((now - last) / 1000) * rate);
      last = now;
      timeRef.current = t;
      setTime(t);
      if (t >= simulation.duration_s) setPlaying(false);
      else id = requestAnimationFrame(step);
    };
    id = requestAnimationFrame(step);
    return () => cancelAnimationFrame(id);
  }, [playing, simulation, rate]);
  const changeConfig = (next: FlightSimulationRequest) => {
    abort.current?.abort();
    setConfig(next);
    setSimulation(null);
    setSubmitted(null);
    setLoading(false);
    setError("");
    seek(0);
  };
  const selectLesson = (id: FlightSimulationRequest["scenario"]) => {
    const next = { ...config, scenario: id, entry_ias_kts: null };
    changeConfig(next);
    void generate(next);
  };
  const togglePlay = () => {
    if (simulation && time >= simulation.duration_s) {
      timeRef.current = 0;
      setTime(0);
    }
    setPlaying((p) => !p);
  };
  const fullscreen = () => {
    if (document.fullscreenElement) void document.exitFullscreen();
    else
      void lab.current
        ?.requestFullscreen()
        .catch(() => setError("Fullscreen is unavailable in this browser."));
  };

  return (
    <div className="flight-lab" ref={lab}>
      <header className="flight-heading">
        <div>
          <div className="flight-eyebrow">CGEM / AIRCREW LEARNING LAB</div>
          <h1>The aircraft. The load. The response.</h1>
          <p>
            Explore G awareness from outside the aircraft and inside the model.
          </p>
        </div>
        <div className="flight-header-actions">
          <button
            onClick={() => setSettings(!settings)}
            aria-expanded={settings}
          >
            <SlidersHorizontal size={16} /> Setup
          </button>
          <button
            className="flight-primary"
            disabled={!simulation}
            onClick={() => {
              setPlaying(false);
              setExportOpen(true);
            }}
          >
            <ArrowDownToLine size={16} /> Export video
          </button>
        </div>
      </header>

      <nav className="flight-lessons" aria-label="Guided maneuvers">
        {LESSONS.map((l, i) => (
          <button
            key={l.id}
            className={l.id === config.scenario ? "selected" : ""}
            onClick={() => selectLesson(l.id)}
            aria-pressed={l.id === config.scenario}
          >
            <span className="flight-lesson-number">0{i + 1}</span>
            <span>
              <strong>{l.name}</strong>
              <small>{l.subtitle}</small>
            </span>
            {l.id === config.scenario && <span className="flight-active-dot" />}
          </button>
        ))}
      </nav>

      {settings && (
        <form
          className="flight-setup"
          onSubmit={(e) => {
            e.preventDefault();
            void generate(config);
            setSettings(false);
          }}
        >
          <div className="flight-section-heading">
            <h2>Flight & physiological conditions</h2>
            <button
              type="button"
              className="flight-icon"
              aria-label="Close setup"
              onClick={() => setSettings(false)}
            >
              <X size={18} />
            </button>
          </div>
          <div className="flight-fields">
            <label>
              Aircraft loading
              <select
                value={config.loading}
                onChange={(e) =>
                  changeConfig({
                    ...config,
                    loading: e.target.value as "solo" | "dual",
                  })
                }
              >
                <option value="solo">Solo · 820 kg · ±10 G</option>
                <option value="dual">Dual · 870 kg · ±8 G</option>
              </select>
            </label>
            <label>
              Entry IAS · kt
              <input
                type="number"
                min={80}
                max={190}
                step={1}
                value={
                  Number.isFinite(config.entry_ias_kts ?? lesson.entry)
                    ? (config.entry_ias_kts ?? lesson.entry)
                    : ""
                }
                onChange={(e) =>
                  changeConfig({
                    ...config,
                    entry_ias_kts: e.target.valueAsNumber,
                  })
                }
                required
              />
            </label>
            <label>
              Entry altitude · ft
              <input
                type="number"
                min={1000}
                max={16000}
                step={100}
                value={
                  Number.isFinite(config.altitude_ft) ? config.altitude_ft : ""
                }
                onChange={(e) =>
                  changeConfig({
                    ...config,
                    altitude_ft: e.target.valueAsNumber,
                  })
                }
                required
              />
            </label>
            <label>
              Pull target · G
              <input
                type="number"
                min={2}
                max={config.loading === "solo" ? 9 : 7}
                step={0.5}
                value={
                  Number.isFinite(config.intensity_g) ? config.intensity_g : ""
                }
                onChange={(e) =>
                  changeConfig({
                    ...config,
                    intensity_g: e.target.valueAsNumber,
                  })
                }
                required
              />
            </label>
            <label>
              CGEM subject
              <select
                value={config.pilot.who_profile ?? 4}
                onChange={(e) =>
                  changeConfig({
                    ...config,
                    pilot: {
                      ...config.pilot,
                      who_profile: Number(e.target.value),
                    },
                  })
                }
              >
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <option key={n} value={n}>
                    FAA subject {n}
                  </option>
                ))}
              </select>
            </label>
            <label>
              AGSM effectiveness
              <select
                value={config.pilot.agsm_effectiveness}
                onChange={(e) => {
                  const value = Number(e.target.value);
                  changeConfig({
                    ...config,
                    pilot: {
                      ...config.pilot,
                      agsm_effectiveness: value,
                      countermeasures_label: value ? "agsm" : "none",
                    },
                  });
                }}
              >
                <option value={0}>Off · relaxed</option>
                <option value={0.5}>0.5 · modeled comparison</option>
                <option value={1}>1.0 · modeled maximum</option>
              </select>
            </label>
          </div>
          <div className="flight-setup-footer">
            <p>
              No G-suit or pressure breathing. AGSM is a model input, not a
              measured maneuver proficiency. Altitude affects flight air data;
              CGEM does not model altitude hypoxia.
            </p>
            <button className="flight-primary" type="submit">
              Generate lesson <ChevronRight size={16} />
            </button>
          </div>
        </form>
      )}

      <div className="flight-status-line">
        <span>
          <span className="flight-active-dot" /> EXTRA 300L{" "}
          <span className="flight-muted">/</span>{" "}
          {config.loading === "solo" ? "820 kg · SOLO" : "870 kg · DUAL"}
        </span>
        <span className="flight-model-label">
          POH-checked educational dynamics
        </span>
        <span>
          {loading
            ? "Computing flight + CGEM…"
            : simulation
              ? `${simulation.frames.length.toLocaleString()} flight states · ${simulation.duration_s.toFixed(1)} s`
              : "Awaiting lesson"}
        </span>
      </div>

      {!simulation ? (
        <div className="flight-empty" role="status">
          <div className="flight-empty-orbit" />
          <h2>
            {loading
              ? "Building the flight and physiological response"
              : error
                ? "This lesson could not be generated"
                : "Ready to generate your lesson"}
          </h2>
          <p>
            {loading
              ? "Integrating aircraft forces, then passing the signed load history to the original CGEM."
              : error ||
                "Your updated conditions will recompute the aircraft motion and G exposure."}
          </p>
          {!loading && (
            <button
              className="flight-primary"
              onClick={() => void generate(config)}
            >
              Generate lesson
            </button>
          )}
        </div>
      ) : (
        <>
          <section
            className="flight-visuals"
            aria-label="Synchronized aircraft and instruments"
          >
            <div className="flight-world">
              <AircraftViewport
                simulation={simulation}
                time={time}
                options={options}
              />
              <div className="flight-world-top">
                <span className="flight-view-label">
                  {options.view === "cockpit"
                    ? "COCKPIT"
                    : options.view === "split"
                      ? "EXTERIOR + COCKPIT"
                      : "EXTERNAL AIRCRAFT"}
                </span>
                <button
                  className="flight-glass-button"
                  aria-label="Toggle fullscreen"
                  onClick={fullscreen}
                >
                  <Expand size={17} />
                </button>
              </div>
              <div className="flight-world-bottom">
                <div className="flight-load">
                  <span>NORMAL LOAD / Gz</span>
                  <strong>
                    {frame && frame.gz >= 0 ? "+" : ""}
                    {frame?.gz.toFixed(2)}
                    <small>G</small>
                  </strong>
                </div>
                <div className="flight-current-phase">
                  <span>MANEUVER PHASE</span>
                  <strong>{frame?.phase}</strong>
                </div>
              </div>
              <div className="flight-view-toolbar">
                <div role="group" aria-label="Camera view">
                  {(["chase", "orbit", "cockpit", "split"] as const).map(
                    (view) => (
                      <button
                        key={view}
                        aria-pressed={options.view === view}
                        onClick={() => setOptions({ ...options, view })}
                      >
                        {view === "chase"
                          ? "Chase"
                          : view === "orbit"
                            ? "Orbit"
                            : view === "cockpit"
                              ? "Cockpit"
                              : "Split"}
                      </button>
                    ),
                  )}
                </div>
                <div className="flight-overlays">
                  <button
                    aria-pressed={options.showTrail}
                    onClick={() =>
                      setOptions({ ...options, showTrail: !options.showTrail })
                    }
                  >
                    {options.showTrail && <Check size={12} />} Path
                  </button>
                  <button
                    aria-pressed={options.showForces}
                    onClick={() =>
                      setOptions({
                        ...options,
                        showForces: !options.showForces,
                      })
                    }
                  >
                    {options.showForces && <Check size={12} />} Forces
                  </button>
                </div>
              </div>
            </div>
            <aside className="flight-instrument-panel">
              <div className="flight-section-heading">
                <span>PRIMARY FLIGHT DISPLAY</span>
                <span className="flight-live-badge">LIVE</span>
              </div>
              {frame && (
                <InstrumentDisplay frame={frame} baroHpa={options.baroHpa} />
              )}
              <label className="flight-qnh">
                Barometric setting{" "}
                <input
                  aria-label="Barometric setting in hectopascals"
                  type="number"
                  min={950}
                  max={1050}
                  step={0.25}
                  value={baroDraft}
                  onChange={(e) => {
                    setBaroDraft(e.target.value);
                    if (
                      Number.isFinite(e.target.valueAsNumber) &&
                      e.target.valueAsNumber >= 950 &&
                      e.target.valueAsNumber <= 1050
                    )
                      setOptions({
                        ...options,
                        baroHpa: e.target.valueAsNumber,
                      });
                  }}
                  onBlur={() => setBaroDraft(String(options.baroHpa))}
                />{" "}
                hPa
              </label>
            </aside>
          </section>

          <section className="flight-playback" aria-label="Playback controls">
            <div className="flight-playback-buttons">
              <button
                className="flight-play-button"
                onClick={togglePlay}
                aria-label={playing ? "Pause lesson" : "Play lesson"}
              >
                {playing ? (
                  <Pause size={18} />
                ) : (
                  <Play size={18} fill="currentColor" />
                )}
              </button>
              <button
                className="flight-icon"
                onClick={() => seek(0)}
                aria-label="Restart lesson"
              >
                <RotateCcw size={17} />
              </button>
              <span className="flight-time">
                <strong>{time.toFixed(2)}</strong> /{" "}
                {simulation.duration_s.toFixed(2)} s
              </span>
            </div>
            <input
              className="flight-seek"
              type="range"
              min={0}
              max={simulation.duration_s}
              step={0.01}
              value={time}
              aria-label="Lesson time"
              onChange={(e) => seek(Number(e.target.value))}
            />
            <select
              className="flight-rate"
              aria-label="Playback speed"
              value={rate}
              onChange={(e) => setRate(Number(e.target.value))}
            >
              {[0.25, 0.5, 1, 2].map((r) => (
                <option key={r} value={r}>
                  {r}× speed
                </option>
              ))}
            </select>
          </section>

          <div className="flight-learning-grid">
            <section className="flight-card flight-exposure">
              <div className="flight-section-heading">
                <h2>G exposure</h2>
                <span className="flight-mono">SIGNED BODY-AXIS LOAD</span>
              </div>
              <div className="flight-trace-legend">
                <span>
                  <i /> Flight Gz
                </span>
                <span>
                  <i /> CGEM input samples
                </span>
                <span>Dashed · aircraft ±{simulation.aircraft.g_limit} G</span>
              </div>
              <FlightTrace simulation={simulation} time={time} />
              <div className="flight-phase-list">
                {simulation.phases.map((p, i) => {
                  const start = phaseStartTime(simulation.frames, p);
                  return (
                    <button
                      key={`${p.name}-${i}`}
                      className={phase === p ? "active" : ""}
                      disabled={start === null}
                      onClick={() => {
                        if (start !== null) seek(start);
                      }}
                    >
                      <span>{p.start_s.toFixed(1)}s</span>
                      {p.name}
                    </button>
                  );
                })}
              </div>
            </section>
            <section className="flight-card flight-physiology">
              <div className="flight-section-heading">
                <h2>Physiological response</h2>
                <span className="flight-mono">ORIGINAL CGEM</span>
              </div>
              {simulation.physiology.status === "unavailable" ? (
                <p className="flight-error" role="status">
                  {simulation.physiology.reason ??
                    "The physiological model is unavailable for this run."}
                </p>
              ) : (
                <>
                  <div className="flight-physiology-values">
                    <div>
                      <span>Head-level pressure</span>
                      <strong>
                        {physiology?.hlap.toFixed(1) ?? "—"}
                        <small>mmHg</small>
                      </strong>
                    </div>
                    <div>
                      <span>Consciousness flow</span>
                      <strong>
                        {physiology?.flow.toFixed(1) ?? "—"}
                        <small>dl/min</small>
                      </strong>
                    </div>
                    <div>
                      <span>Consciousness reserve</span>
                      <strong>
                        {physiology?.reserve.toFixed(2) ?? "—"}
                        <small>s</small>
                      </strong>
                    </div>
                  </div>
                  <div className="flight-flags">
                    {(["greyout", "blackout", "conscious"] as const).map(
                      (key) => (
                        <div key={key} data-state={physiology?.[key]}>
                          <span>
                            {key === "conscious"
                              ? "Consciousness"
                              : key === "greyout"
                                ? "Greyout"
                                : "Blackout"}
                          </span>
                          <strong>{flagLabel(physiology?.[key])}</strong>
                        </div>
                      ),
                    )}
                  </div>
                  <p className="flight-sample-note">
                    {physiology
                      ? `Native sample at ${physiology.time_s.toFixed(3)} s · held until the next reported value.`
                      : "Flight starts at 0 s. Physiological values appear at the first reported sample."}
                  </p>
                  <div
                    className="flight-predicted-events"
                    aria-label="First predicted loss events"
                  >
                    <span>First loss in this run</span>
                    {(
                      [
                        [
                          "Greyout",
                          simulation.physiology.result?.time_to_greyout_s,
                        ],
                        [
                          "Blackout",
                          simulation.physiology.result?.time_to_blackout_s,
                        ],
                        ["G-LOC", simulation.physiology.result?.time_to_gloc_s],
                      ] as const
                    ).map(([name, t]) =>
                      t != null ? (
                        <button key={name} onClick={() => seek(t)}>
                          {name} · {t.toFixed(3)} s
                        </button>
                      ) : (
                        <span key={name}>{name} · not reported</span>
                      ),
                    )}
                  </div>
                </>
              )}
              <p className="flight-subject-note">
                FAA subject {submitted?.pilot.who_profile} · AGSM{" "}
                {submitted?.pilot.agsm_effectiveness
                  ? submitted.pilot.agsm_effectiveness.toFixed(1)
                  : "off"}{" "}
                · no suit / PBG
              </p>
            </section>
          </div>

          <section className="flight-briefing">
            <div className="flight-briefing-number">
              {String(LESSONS.indexOf(lesson) + 1).padStart(2, "0")}
            </div>
            <div>
              <div className="flight-eyebrow">READ THE MANEUVER</div>
              <h2>{phase?.name ?? lesson.name}</h2>
              <p>{phase?.description ?? lesson.lesson}</p>
              <p className="flight-physiology-caption">
                {simulation.physiology.status === "available"
                  ? physiologyCaption(physiology)
                  : "The flight remains available for inspection; physiological predictions are unavailable."}
              </p>
            </div>
            <div className="flight-airdata">
              <span>
                IAS / TAS
                <strong>
                  {frame?.ias_kts.toFixed(0)} / {frame?.tas_kts.toFixed(0)}
                  <small>kt</small>
                </strong>
              </span>
              <span>
                ANGLE OF ATTACK
                <strong>
                  {frame?.alpha_deg.toFixed(1)}
                  <small>°</small>
                </strong>
              </span>
              <span>
                PRESSURE ALTITUDE
                <strong>
                  {frame?.altitude_ft.toFixed(0)}
                  <small>ft</small>
                </strong>
              </span>
            </div>
          </section>
          {!!simulation.events.length && (
            <div className="flight-events" role="status">
              {simulation.events.map((event, i) => (
                <p key={i}>
                  <strong>
                    {event.time_s.toFixed(2)} s ·{" "}
                    {event.kind.replaceAll("_", " ")}
                  </strong>{" "}
                  {event.message}
                </p>
              ))}
            </div>
          )}

          <details className="flight-sources">
            <summary>
              Model, aircraft limits & source notes{" "}
              <span>{simulation.provenance.model_version}</span>
            </summary>
            <div>
              <p>
                {simulation.provenance.flight_model}. Aircraft limits: V
                <sub>A</sub> {simulation.aircraft.va_kias} KIAS; V<sub>NE</sub>{" "}
                {simulation.aircraft.vne_kias} KIAS; ±
                {simulation.aircraft.g_limit} G at {simulation.aircraft.mass_kg}{" "}
                kg. These are aircraft limits, not physiological tolerance
                thresholds.
              </p>
              <p>
                The public Extra information manual and EASA type certificate
                anchor the aircraft parameters. Estimated aerodynamic and
                guidance coefficients have not been calibrated against
                flight-test recordings. Use this lesson to study the model; it
                is not an approved aircraft operating procedure.
              </p>
              <ul>
                {simulation.provenance.assumptions.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
              <p>
                TXi-style instruments follow the supplied photographs and the{" "}
                <a
                  href="https://static.garmin.com/pumac/190-01717-10_u.pdf"
                  target="_blank"
                  rel="noreferrer"
                >
                  Garmin TXi Pilot’s Guide
                </a>
                . This educational display does not emulate certified avionics,
                navigation, or AHRS failure behavior.
              </p>
              <ul>
                {simulation.provenance.source_urls.map((url, i) => (
                  <li key={url}>
                    <a href={url} target="_blank" rel="noreferrer">
                      Aircraft source {i + 1} · {new URL(url).hostname}
                    </a>
                  </li>
                ))}
              </ul>
              <div className="flight-hashes">
                Parameters: {simulation.provenance.parameter_sha256}
                <br />G trace: {simulation.provenance.trace_sha256}
                <br />
                CGEM binary:{" "}
                {simulation.physiology.binary_sha256 ?? "Unavailable"}
              </div>
            </div>
          </details>
        </>
      )}
      <footer className="flight-footer">
        <span>
          Guided aircraft simulation · axial G physiology · no pilot rendered
        </span>
        <Link to="/simulator?mode=trace">
          <ArrowLeft size={14} /> Open the full G-trace lesson library
        </Link>
      </footer>
      {exportOpen && simulation && (
        <ExportDialog
          simulation={simulation}
          options={options}
          rate={rate}
          subject={submitted?.pilot.who_profile ?? 4}
          agsm={submitted?.pilot.agsm_effectiveness ?? 0}
          onClose={() => setExportOpen(false)}
        />
      )}
    </div>
  );
}
