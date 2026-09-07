import { useEffect, useRef, useState } from "react";
import { ArrowDownToLine, X } from "lucide-react";
import { exportFramePlan } from "./timeline";
import type { FlightSimulationResponse, SceneOptions } from "./types";

export function ExportDialog({
  simulation,
  options,
  rate,
  subject,
  agsm,
  onClose,
}: {
  simulation: FlightSimulationResponse;
  options: SceneOptions;
  rate: number;
  subject: number;
  agsm: number;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const abort = useRef<AbortController | null>(null);
  const [start, setStart] = useState(0),
    [end, setEnd] = useState(simulation.duration_s);
  const [progress, setProgress] = useState<number | null>(null);
  const [status, setStatus] = useState(""),
    [error, setError] = useState("");
  const [capable, setCapable] = useState<boolean | null>(null);
  useEffect(() => {
    dialog.current?.showModal();
    let active = true;
    void import("./video")
      .then((video) => video.canExportMp4())
      .then((ok) => {
        if (active) setCapable(ok);
      })
      .catch(() => {
        if (active) setCapable(false);
      });
    return () => {
      active = false;
      abort.current?.abort();
    };
  }, []);
  const valid =
    Number.isFinite(start) &&
    Number.isFinite(end) &&
    start >= 0 &&
    end > start &&
    end <= simulation.duration_s;
  const duration = valid ? exportFramePlan(start, end, rate).duration_s : 0;
  const exporting = progress !== null;
  async function renderVideo() {
    const controller = new AbortController();
    abort.current = controller;
    setProgress(0);
    setError("");
    setStatus("Rendering exact frames…");
    try {
      const { exportMp4 } = await import("./video");
      const blob = await exportMp4(simulation, {
        start,
        end,
        rate,
        scene: options,
        subject,
        agsm,
        signal: controller.signal,
        onProgress: setProgress,
      });
      if (controller.signal.aborted) return;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `CGEM-Extra300L-${simulation.scenario}-${start.toFixed(2)}-${end.toFixed(2)}.mp4`;
      anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 30_000);
      setStatus(
        `Video ready · ${(blob.size / 1024 / 1024).toFixed(1)} MB downloaded.`,
      );
    } catch (e) {
      if (controller.signal.aborted)
        setStatus("Export cancelled. The lesson is unchanged.");
      else {
        setError(
          e instanceof Error ? e.message : "The video could not be exported.",
        );
        setStatus("");
      }
    } finally {
      setProgress(null);
    }
  }
  return (
    <dialog
      ref={dialog}
      className="flight-modal"
      onCancel={(e) => {
        e.preventDefault();
        if (exporting) abort.current?.abort();
        else onClose();
      }}
      aria-labelledby="flight-export-title"
    >
      <div className="flight-section-heading">
        <h2 id="flight-export-title">Export this lesson</h2>
        <button
          className="flight-icon"
          aria-label="Close export"
          disabled={exporting}
          onClick={onClose}
        >
          <X size={18} />
        </button>
      </div>
      <p>
        Silent MP4 · 1920 × 1080 · 30 fps. Includes the aircraft, live
        instruments, G trace, and CGEM response at the same simulation time.
      </p>
      <div className="flight-export-fields">
        <label>
          Start · simulation seconds
          <input
            type="number"
            min={0}
            max={simulation.duration_s}
            step={0.01}
            value={Number.isFinite(start) ? start : ""}
            disabled={exporting}
            onChange={(e) => setStart(e.target.valueAsNumber)}
          />
        </label>
        <label>
          End · simulation seconds
          <input
            type="number"
            min={0}
            max={simulation.duration_s}
            step={0.01}
            value={Number.isFinite(end) ? end : ""}
            disabled={exporting}
            onChange={(e) => setEnd(e.target.valueAsNumber)}
          />
        </label>
      </div>
      <p>
        {rate}× playback · {valid ? duration.toFixed(2) : "—"} s video ·{" "}
        {options.view} camera. Orbit exports use the reference camera angle.
      </p>
      {capable === null && (
        <p role="status">Checking H.264 encoding support…</p>
      )}
      {capable === false && (
        <p className="flight-error" role="alert">
          H.264 encoding at 1080p is unavailable in this browser. Use a browser
          with WebCodecs H.264 encoding enabled.
        </p>
      )}
      {!valid && (
        <p className="flight-error">
          Choose an interval inside this lesson, with the end after the start.
        </p>
      )}
      {error && (
        <p className="flight-error" role="alert">
          {error}
        </p>
      )}
      {exporting && (
        <>
          <progress
            value={progress}
            max={1}
            aria-label="Video export progress"
          />
          <p>
            {Math.round(progress * 100)}% · {status}
          </p>
        </>
      )}
      {!exporting && status && <p role="status">{status}</p>}
      <div className="flight-export-actions">
        {exporting ? (
          <button onClick={() => abort.current?.abort()}>Cancel export</button>
        ) : (
          <>
            <button onClick={onClose}>Close</button>
            <button
              className="flight-primary"
              disabled={!valid || !capable}
              onClick={() => void renderVideo()}
            >
              <ArrowDownToLine size={16} /> Render MP4
            </button>
          </>
        )}
      </div>
    </dialog>
  );
}
