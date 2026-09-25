import { useEffect, useRef, useState } from "react";
import { drawPfd } from "./instruments";
import { drawTrace } from "./trace";
import type {
  FlightFrame,
  FlightSimulationResponse,
  SceneOptions,
} from "./types";
import type { FlightScene } from "./scene";

export function AircraftViewport({
  simulation,
  time,
  options,
}: {
  simulation: FlightSimulationResponse;
  time: number;
  options: SceneOptions;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const scene = useRef<FlightScene | null>(null);
  const state = useRef({ time, options });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    state.current = { time, options };
    scene.current?.render(time, options);
  }, [time, options]);
  useEffect(() => {
    let cancelled = false;
    const node = canvas.current!;
    let observer: ResizeObserver | undefined;
    setLoading(true);
    setError("");
    void import("./scene")
      .then(({ FlightScene }) => {
        if (cancelled) return;
        try {
          setError("");
          const renderer = new FlightScene(node, (message) => {
            if (!cancelled) setError(message);
          });
          scene.current = renderer;
          void renderer.ready
            .then(() => {
              if (!cancelled) setLoading(false);
            })
            .catch((e: unknown) => {
              if (!cancelled) {
                setLoading(false);
                setError(
                  e instanceof Error
                    ? e.message
                    : "Could not load the aircraft model.",
                );
              }
            });
          renderer.setSimulation(simulation);
          observer = new ResizeObserver(() => {
            renderer.resize(
              node.clientWidth,
              node.clientHeight,
              window.devicePixelRatio,
            );
            renderer.render(state.current.time, state.current.options);
          });
          observer.observe(node);
          renderer.resize(
            node.clientWidth,
            node.clientHeight,
            window.devicePixelRatio,
          );
          renderer.render(state.current.time, state.current.options);
        } catch (e) {
          setLoading(false);
          setError(
            e instanceof Error ? e.message : "The 3D renderer could not start.",
          );
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setLoading(false);
          setError(
            e instanceof Error ? e.message : "Could not load the 3D renderer.",
          );
        }
      });
    return () => {
      cancelled = true;
      observer?.disconnect();
      scene.current?.dispose();
      scene.current = null;
    };
  }, [simulation]);
  return (
    <>
      <canvas
        ref={canvas}
        aria-label="Three-dimensional Extra 300 aircraft simulation"
        aria-busy={loading}
        className="flight-scene"
      />
      {loading && !error && (
        <div className="flight-scene-status" role="status">
          Loading Extra 300 model…
        </div>
      )}
      {error && (
        <div className="flight-scene-error" role="alert">
          {error}
        </div>
      )}
    </>
  );
}

export function InstrumentDisplay({
  frame,
  baroHpa,
}: {
  frame: FlightFrame;
  baroHpa: number;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    let active = true;
    const ctx = canvas.current?.getContext("2d");
    if (ctx) drawPfd(ctx, 600, 760, frame, { baroHpa });
    void document.fonts.ready.then(() => {
      if (active && ctx) drawPfd(ctx, 600, 760, frame, { baroHpa });
    });
    return () => {
      active = false;
    };
  }, [frame, baroHpa]);
  return (
    <canvas
      ref={canvas}
      width={600}
      height={760}
      className="flight-pfd"
      aria-label={`Flight instruments: ${frame.ias_kts.toFixed(0)} knots indicated, ${frame.altitude_ft.toFixed(0)} feet pressure altitude, ${frame.gz.toFixed(2)} G`}
    />
  );
}

export function FlightTrace({
  simulation,
  time,
}: {
  simulation: FlightSimulationResponse;
  time: number;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const node = canvas.current!;
    const draw = () => {
      const dpr = Math.min(window.devicePixelRatio, 2);
      node.width = node.clientWidth * dpr;
      node.height = node.clientHeight * dpr;
      const ctx = node.getContext("2d");
      if (ctx) {
        ctx.scale(dpr, dpr);
        drawTrace(ctx, node.clientWidth, node.clientHeight, simulation, time);
      }
    };
    draw();
    const observer = new ResizeObserver(draw);
    observer.observe(node);
    return () => observer.disconnect();
  }, [simulation, time]);
  return (
    <canvas
      ref={canvas}
      className="flight-trace-canvas"
      aria-label="Signed Gz exposure over the maneuver, with aircraft structural limits and CGEM input samples"
    />
  );
}
