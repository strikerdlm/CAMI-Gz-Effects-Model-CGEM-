import { Quaternion as ThreeQuaternion } from "three";
import type { CGEMRunResponse } from "../../services/types";
import type {
  FlightFrame,
  FlightSimulationResponse,
  PhysiologySample,
  Quaternion,
  Vec3,
} from "./types";

type FlightPhase = FlightSimulationResponse["phases"][number];

export function phaseForFrame(
  phases: FlightPhase[],
  frame: FlightFrame | null,
) {
  if (!frame) return undefined;
  // Metadata boundaries can precede the first frame of a new phase by one
  // integration step. Keep the briefing with the left-held sampled phase.
  let selected: FlightPhase | undefined;
  for (const phase of phases) {
    if (
      phase.name === frame.phase &&
      phase.start_s <= frame.t_s &&
      (!selected || phase.start_s >= selected.start_s)
    )
      selected = phase;
  }
  return selected;
}

export function phaseStartTime(
  frames: FlightFrame[],
  phase: FlightPhase,
): number | null {
  return (
    frames.find(
      (frame) =>
        frame.t_s >= phase.start_s &&
        frame.t_s <= phase.end_s &&
        frame.phase === phase.name,
    )?.t_s ?? null
  );
}

/** Rightmost sample at or before t. Native CGEM transitions remain discrete. */
function preceding(
  length: number,
  at: (i: number) => number,
  t: number,
): number {
  let lo = 0,
    hi = length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (at(mid) <= t) lo = mid + 1;
    else hi = mid;
  }
  return lo - 1;
}
const mix = (a: number, b: number, u: number) => a + (b - a) * u;
export function sampleFlight(
  frames: FlightFrame[],
  time: number,
): FlightFrame | null {
  if (!frames.length || !Number.isFinite(time)) return null;
  const i = preceding(frames.length, (k) => frames[k].t_s, time);
  if (i < 0) return frames[0];
  if (i >= frames.length - 1 || frames[i].t_s === time) return frames[i];
  const a = frames[i],
    b = frames[i + 1];
  const u = (time - a.t_s) / (b.t_s - a.t_s);
  const vec = (x: Vec3, y: Vec3): Vec3 =>
    x.map((v, k) => mix(v, y[k], u)) as Vec3;
  const q = new ThreeQuaternion(...a.quaternion)
    .slerp(new ThreeQuaternion(...b.quaternion), u)
    .normalize();
  // Body FRD -> world NED, matching the backend's rotation-matrix readouts.
  // Euler endpoints can change branch at vertical flight; never interpolate them.
  const { x, y, z, w } = q;
  const degrees = 180 / Math.PI;
  const heading =
    Math.atan2(2 * (x * y + w * z), 1 - 2 * (y * y + z * z)) * degrees;
  const pitch =
    Math.asin(Math.max(-1, Math.min(1, 2 * (w * y - x * z)))) * degrees;
  const roll =
    Math.atan2(2 * (y * z + w * x), 1 - 2 * (x * x + y * y)) * degrees;
  const controls = { ...a.controls },
    forces = { ...a.forces_n };
  for (const k of Object.keys(controls) as (keyof typeof controls)[])
    controls[k] = mix(a.controls[k], b.controls[k], u);
  for (const k of Object.keys(forces) as (keyof typeof forces)[])
    forces[k] = mix(a.forces_n[k], b.forces_n[k], u);
  return {
    ...a,
    t_s: time,
    position_m: vec(a.position_m, b.position_m),
    velocity_mps: vec(a.velocity_mps, b.velocity_mps),
    quaternion: q.toArray() as Quaternion,
    controls,
    forces_n: forces,
    ias_kts: mix(a.ias_kts, b.ias_kts, u),
    tas_kts: mix(a.tas_kts, b.tas_kts, u),
    altitude_ft: mix(a.altitude_ft, b.altitude_ft, u),
    vertical_speed_fpm: mix(a.vertical_speed_fpm, b.vertical_speed_fpm, u),
    heading_deg: ((heading % 360) + 360) % 360,
    pitch_deg: pitch,
    roll_deg: roll,
    alpha_deg: mix(a.alpha_deg, b.alpha_deg, u),
    gz: mix(a.gz, b.gz, u),
  };
}

export function samplePhysiology(
  result: CGEMRunResponse | null | undefined,
  time: number,
): PhysiologySample | null {
  if (!result || !Number.isFinite(time)) return null;
  const d = result.data,
    times = d["Time(s)"];
  const i = preceding(times.length, (k) => times[k], time);
  if (i < 0) return null;
  return {
    time_s: times[i],
    hlap: d["HLAP(mmHg)"][i],
    flow: d["F_con(dl/min)"][i],
    reserve: d["c_bank(s)"][i],
    conscious: d.Conscious[i],
    greyout: d.Greyout[i],
    blackout: d.Blackout[i],
  };
}

export function exportFramePlan(start: number, end: number, rate: number) {
  if (
    ![start, end, rate].every(Number.isFinite) ||
    start < 0 ||
    end <= start ||
    rate <= 0
  )
    throw new Error("Choose a valid video interval and playback rate.");
  const frameCount = Math.ceil(((end - start) / rate) * 30);
  return {
    frameCount,
    duration_s: frameCount / 30,
    simulationTime: (i: number) => Math.min(end, start + (i * rate) / 30),
  };
}
