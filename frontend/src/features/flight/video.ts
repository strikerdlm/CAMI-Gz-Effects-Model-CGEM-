import { Quality, canEncodeVideo } from "mediabunny";
import { VideoEncoderClient, abortable } from "./videoEncoder";
import { FlightScene } from "./scene";
import { drawPfd } from "./instruments";
import { drawTrace } from "./trace";
import {
  exportFramePlan,
  sampleFlight,
  samplePhysiology,
  phaseForFrame,
} from "./timeline";
import { flagLabel, LESSONS } from "./lessonData";
import type { FlightSimulationResponse, SceneOptions } from "./types";

const WIDTH = 1920,
  HEIGHT = 1080;
const quality = new Quality({ bitrate: 8_000_000 });
export const canExportMp4 = async () =>
  typeof Worker !== "undefined" &&
  typeof OffscreenCanvas !== "undefined" &&
  typeof createImageBitmap !== "undefined" &&
  (await canEncodeVideo("avc", { width: WIDTH, height: HEIGHT, quality }));
export interface VideoOptions {
  start: number;
  end: number;
  rate: number;
  scene: SceneOptions;
  subject: number;
  agsm: number;
  signal: AbortSignal;
  onProgress: (fraction: number) => void;
}
function text(
  ctx: CanvasRenderingContext2D,
  s: string,
  x: number,
  y: number,
  size: number,
  color = "#edf2f6",
  mono = false,
) {
  ctx.font = `400 ${size}px "IBM Plex ${mono ? "Mono" : "Sans"}", ${mono ? "monospace" : "sans-serif"}`;
  ctx.textBaseline = "middle";
  ctx.textAlign = "left";
  ctx.fillStyle = color;
  ctx.fillText(s, x, y);
}
function fittedText(
  ctx: CanvasRenderingContext2D,
  s: string,
  x: number,
  y: number,
  maxWidth: number,
  size: number,
  color: string,
) {
  ctx.font = `400 ${size}px "IBM Plex Sans", sans-serif`;
  while (ctx.measureText(s).width > maxWidth && s.length > 3)
    s = s.slice(0, -2).trimEnd() + "…";
  text(ctx, s, x, y, size, color);
}
/** A separate scene renders absolute timestamps; export never advances the viewer's clock. */
export async function exportMp4(
  sim: FlightSimulationResponse,
  options: VideoOptions,
): Promise<Blob> {
  const plan = exportFramePlan(options.start, options.end, options.rate);
  if (options.end > sim.duration_s)
    throw new Error("The video interval exceeds the lesson duration.");
  options.signal.throwIfAborted();
  if (!(await abortable(canExportMp4(), options.signal)))
    throw new Error(
      "This browser cannot encode H.264 at 1080p. Open the lab in a browser with WebCodecs H.264 encoding enabled.",
    );
  await abortable(document.fonts.ready, options.signal);
  options.signal.throwIfAborted();
  const canvas = document.createElement("canvas");
  canvas.width = WIDTH;
  canvas.height = HEIGHT;
  const ctx = canvas.getContext("2d", { alpha: false });
  if (!ctx) throw new Error("Video composition canvas is unavailable.");
  const view = document.createElement("canvas");
  const pfd = document.createElement("canvas");
  pfd.width = 600;
  pfd.height = 760;
  const pctx = pfd.getContext("2d")!;
  const trace = document.createElement("canvas");
  trace.width = 1336;
  trace.height = 170;
  const tctx = trace.getContext("2d")!;
  let renderError: string | null = null;
  const scene = new FlightScene(view, (message: string) => {
    renderError = message;
  });
  let encoder: VideoEncoderClient | undefined;
  try {
    encoder = new VideoEncoderClient(
      new Worker(new URL("./videoEncoder.worker.ts", import.meta.url), {
        type: "module",
      }),
      options.signal,
    );
    scene.setSimulation(sim);
    scene.resize(1340, 630, 1);
    await encoder.start(WIDTH, HEIGHT);
    for (let i = 0; i < plan.frameCount; i++) {
      options.signal.throwIfAborted();
      const time = plan.simulationTime(i),
        f = sampleFlight(sim.frames, time)!;
      const phys = samplePhysiology(sim.physiology.result, time);
      scene.render(time, options.scene);
      if (renderError) throw new Error(renderError);
      drawPfd(pctx, 600, 760, f, { baroHpa: options.scene.baroHpa });
      drawTrace(tctx, trace.width, trace.height, sim, time);
      ctx.fillStyle = "#0c141c";
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
      text(ctx, "CGEM / AIRCREW LEARNING LAB", 32, 32, 15, "#f1b59e", true);
      text(
        ctx,
        `EXTRA 300L  ·  ${LESSONS.find((l) => l.id === sim.scenario)?.name}`,
        32,
        74,
        31,
      );
      text(
        ctx,
        `${sim.aircraft.mass_kg} kg  ·  ${options.rate}× playback  ·  t = ${time.toFixed(2)} s`,
        1330,
        48,
        17,
        "#afc6d3",
        true,
      );
      ctx.drawImage(view, 32, 110, 1340, 630);
      ctx.fillStyle = "#081421cf";
      ctx.fillRect(32, 660, 1340, 80);
      text(
        ctx,
        `${f.gz >= 0 ? "+" : ""}${f.gz.toFixed(2)} G`,
        53,
        704,
        40,
        "#fff",
        true,
      );
      text(ctx, f.phase, 390, 704, 25);
      text(
        ctx,
        `${f.ias_kts.toFixed(0)} KIAS  /  ${f.altitude_ft.toFixed(0)} ft`,
        1010,
        704,
        20,
        "#c8dce7",
        true,
      );
      ctx.drawImage(pfd, 1424, 110, 448, 567.5);
      text(
        ctx,
        "ORIGINAL CGEM · PHYSIOLOGICAL RESPONSE",
        1424,
        709,
        14,
        "#83d8cd",
        true,
      );
      for (const [j, label, value] of [
        [0, "Head-level pressure", phys ? `${phys.hlap.toFixed(1)} mmHg` : "—"],
        [
          1,
          "Consciousness flow",
          phys ? `${phys.flow.toFixed(1)} dl/min` : "—",
        ],
        [
          2,
          "Consciousness reserve",
          phys ? `${phys.reserve.toFixed(2)} s` : "—",
        ],
      ] as const) {
        text(ctx, label, 1424, 754 + j * 39, 17, "#aebdca");
        text(ctx, value, 1705, 754 + j * 39, 18);
      }
      text(
        ctx,
        `Greyout: ${flagLabel(phys?.greyout)}   Blackout: ${flagLabel(phys?.blackout)}`,
        1424,
        888,
        16,
      );
      text(
        ctx,
        `Consciousness: ${flagLabel(phys?.conscious)}`,
        1424,
        920,
        18,
        phys?.conscious === 1 ? "#ff9b8f" : "#d9e5ec",
      );
      text(
        ctx,
        phys
          ? `Native sample ${phys.time_s.toFixed(3)} s · held`
          : sim.physiology.status === "unavailable"
            ? "CGEM unavailable"
            : "Awaiting first native sample",
        1424,
        956,
        14,
        "#a0b5c4",
      );
      text(
        ctx,
        `Subject ${options.subject} · AGSM ${options.agsm.toFixed(1)} · no suit / PBG`,
        1424,
        988,
        14,
        "#a0b5c4",
      );
      const phase = phaseForFrame(sim.phases, f);
      fittedText(ctx, phase?.description ?? "", 32, 778, 1340, 20, "#d8c7b5");
      text(
        ctx,
        `SIGNED Gz  ·  Flight / CGEM samples  ·  Dashed aircraft limit ±${sim.aircraft.g_limit} G`,
        32,
        815,
        14,
        "#a6c2cc",
        true,
      );
      ctx.drawImage(trace, 32, 837);
      text(
        ctx,
        "POH-checked educational dynamics · estimated coefficients · axial physiology · not flight-test calibrated",
        32,
        1033,
        16,
        "#b8c8d5",
      );
      text(
        ctx,
        `${sim.provenance.model_version}  /  Trace ${sim.provenance.trace_sha256.slice(0, 16)}`,
        32,
        1061,
        12,
        "#8ba0b0",
        true,
      );
      // Transfer one composed frame at a time and await encoder backpressure.
      // If bitmap creation settles after cancellation, add() closes it without sending.
      const activeEncoder = encoder;
      await abortable(
        createImageBitmap(canvas).then((bitmap) =>
          activeEncoder.add(bitmap, i / 30, 1 / 30),
        ),
        options.signal,
      );
      options.signal.throwIfAborted();
      options.onProgress((i + 1) / plan.frameCount);
      // Let the browser paint progress and deliver cancellation events between batches.
      if (i % 8 === 0)
        await new Promise<void>((resolve) => window.setTimeout(resolve, 0));
    }
    options.signal.throwIfAborted();
    const buffer = await encoder.finalize();
    options.signal.throwIfAborted();
    return new Blob([buffer], { type: "video/mp4" });
  } finally {
    try {
      encoder?.dispose();
    } finally {
      scene.dispose();
      view.width = 0;
      canvas.width = 0;
      pfd.width = 0;
      trace.width = 0;
    }
  }
}
