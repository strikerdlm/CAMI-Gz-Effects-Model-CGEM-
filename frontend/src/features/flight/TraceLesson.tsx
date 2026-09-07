import { useCallback, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  MANEUVERS,
  MANEUVERS_BY_CATEGORY,
  ORDERED_CATEGORIES,
} from "../../data/maneuvers";
import { GTracePlayer } from "../../components/hud/GTracePlayer";
import "./flight.css";

export default function TraceLesson() {
  const [params, setParams] = useSearchParams();
  const maneuver =
    MANEUVERS.find((m) => m.id === params.get("id")) ?? MANEUVERS[0];
  const [now, setNow] = useState({ t: 0, g: maneuver.samples[0]?.nz ?? 1 });
  const onTimeChange = useCallback(
    (t: number, g: number) => setNow({ t, g }),
    [],
  );
  return (
    <div className="flight-lab flight-trace-lesson">
      <header className="flight-heading">
        <div>
          <div className="flight-eyebrow">CGEM / G-TRACE LIBRARY</div>
          <h1>Maneuver exposure lessons</h1>
          <p>Catalog G profiles for physiological study.</p>
        </div>
        <Link to="/simulator" className="flight-primary">
          Open Extra 300L simulation →
        </Link>
      </header>
      <div className="flight-trace-layout">
        <aside className="flight-card">
          <label>
            Registered maneuver
            <select
              value={maneuver.id}
              onChange={(e) => setParams({ id: e.target.value })}
            >
              {ORDERED_CATEGORIES.map((cat) => (
                <optgroup key={cat} label={cat.replaceAll("_", " ")}>
                  {MANEUVERS_BY_CATEGORY[cat].map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.id.replaceAll("_", " ")}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
          <h2>{maneuver.id.replaceAll("_", " ")}</h2>
          <p>{maneuver.description}</p>
          <p className="flight-muted">Catalog aircraft: {maneuver.aircraft}</p>
          <p>{maneuver.hemodynamic_concern}</p>
        </aside>
        <section className="flight-card">
          <div className="flight-section-heading">
            <h2>G-trace playback</h2>
            <strong className="flight-mono">
              {now.g.toFixed(2)} G · {now.t.toFixed(2)} s
            </strong>
          </div>
          <GTracePlayer
            maneuver={maneuver}
            onTimeChange={onTimeChange}
            height={380}
          />
          <p className="flight-sample-note">
            This catalog trace does not define aircraft attitude, airspeed,
            altitude, or a flyable Extra 300L trajectory. Advanced and
            other-aircraft profiles remain trace lessons. Select a core lesson
            to see force-derived aircraft motion and its CGEM response.
          </p>
          <Link to={`/dashboard?id=${encodeURIComponent(maneuver.id)}`}>
            Open the scientific dashboard →
          </Link>
        </section>
      </div>
    </div>
  );
}
