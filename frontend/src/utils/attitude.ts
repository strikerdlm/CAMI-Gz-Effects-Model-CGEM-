import type { Maneuver } from '../data/maneuvers';
import { flightTimeSeconds } from '../data/maneuvers';

export interface AttitudeState {
  pitch: number;
  roll: number;
}

/** Interpolate pitch/roll at playback time `t` (seconds). */
export function attitudeAtTime(maneuver: Maneuver, t: number): AttitudeState {
  const times = flightTimeSeconds(maneuver);
  const samples = maneuver.samples;
  if (times.length === 0 || samples.length === 0) {
    return { pitch: 0, roll: 0 };
  }

  const pitchSeries = samples.map((s) => s.pitch_deg ?? 0);
  const rollSeries = samples.map((s) => s.roll_deg ?? 0);

  if (t <= 0) {
    return { pitch: pitchSeries[0], roll: rollSeries[0] };
  }
  if (t >= times[times.length - 1]) {
    return {
      pitch: pitchSeries[pitchSeries.length - 1],
      roll: rollSeries[rollSeries.length - 1],
    };
  }

  for (let i = 1; i < times.length; i += 1) {
    if (t < times[i]) {
      const span = times[i] - times[i - 1];
      const f = span > 0 ? (t - times[i - 1]) / span : 0;
      return {
        pitch: pitchSeries[i - 1] + f * (pitchSeries[i] - pitchSeries[i - 1]),
        roll: lerpRoll(rollSeries[i - 1], rollSeries[i], f),
      };
    }
  }

  return {
    pitch: pitchSeries[pitchSeries.length - 1],
    roll: rollSeries[rollSeries.length - 1],
  };
}

/** Linear roll interpolation (supports snap-roll 0→360° sweeps). */
function lerpRoll(from: number, to: number, f: number): number {
  return from + (to - from) * f;
}
