import type { FlightSimulationResponse } from "./types";

/** Fixed axes within a lesson, with separate aircraft-envelope markers. */
export function drawTrace(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  sim: FlightSimulationResponse,
  time: number,
) {
  ctx.save();
  ctx.clearRect(0, 0, width, height);
  const left = 38,
    right = width - 18,
    top = 15,
    bottom = height - 26;
  const extent = Math.max(
    sim.aircraft.g_limit + 1,
    ...sim.frames.map((f) => Math.abs(f.gz) + 1),
  );
  const x = (t: number) => left + (t / sim.duration_s) * (right - left);
  const y = (g: number) =>
    bottom - ((g + extent) / (2 * extent)) * (bottom - top);
  ctx.font = '11px "IBM Plex Mono", monospace';
  ctx.textBaseline = "middle";
  for (const g of [-sim.aircraft.g_limit, 0, 1, sim.aircraft.g_limit]) {
    ctx.strokeStyle =
      Math.abs(g) === sim.aircraft.g_limit ? "#bc796148" : "#34434c";
    ctx.lineWidth = 1;
    ctx.setLineDash(Math.abs(g) === sim.aircraft.g_limit ? [4, 5] : []);
    ctx.beginPath();
    ctx.moveTo(left, y(g));
    ctx.lineTo(right, y(g));
    ctx.stroke();
    ctx.fillStyle = "#9dabb9";
    ctx.textAlign = "right";
    if (g !== 0) ctx.fillText(`${g > 0 ? "+" : ""}${g}`, left - 8, y(g));
  }
  ctx.setLineDash([]);
  for (let i = 0; i <= 4; i++) {
    const t = (sim.duration_s * i) / 4;
    ctx.textAlign = "center";
    ctx.fillStyle = "#9dabb9";
    ctx.fillText(`${t.toFixed(0)}s`, x(t), height - 10);
  }
  ctx.strokeStyle = "#6ddad5";
  ctx.lineWidth = 2;
  ctx.beginPath();
  // One vertex per horizontal pixel, plus the final sample; no resampling of physiology.
  const step = Math.max(1, Math.floor(sim.frames.length / width));
  for (let i = 0; i < sim.frames.length; i += step) {
    const f = sim.frames[i];
    if (i === 0) ctx.moveTo(x(f.t_s), y(f.gz));
    else ctx.lineTo(x(f.t_s), y(f.gz));
  }
  const last = sim.frames[sim.frames.length - 1];
  ctx.lineTo(x(last.t_s), y(last.gz));
  ctx.stroke();
  const result = sim.physiology.result;
  if (result) {
    ctx.strokeStyle = "#f5c467";
    ctx.lineWidth = 2;
    ctx.beginPath();
    result.data["Time(s)"].forEach((t, i) => {
      const yy = y(result.data.G[i]);
      if (!i) ctx.moveTo(x(t), yy);
      else ctx.lineTo(x(t), yy);
    });
    ctx.stroke();
  }
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x(time), top);
  ctx.lineTo(x(time), bottom);
  ctx.stroke();
  ctx.restore();
}
