import type {
  ScenarioId,
  FlightSimulationRequest,
  PhysiologySample,
} from "./types";
import { DEFAULT_PILOT_CONFIG } from "../../services/types";
import { readUserPrefs } from "../../state/useUserPrefs";

export const LESSONS: {
  id: ScenarioId;
  name: string;
  subtitle: string;
  entry: number;
  lesson: string;
}[] = [
  {
    id: "coordinated_turn",
    name: "Steep turn",
    subtitle: "Sustained positive G",
    entry: 140,
    lesson:
      "Bank redirects lift into the turn. Maintaining altitude requires more lift than weight, increasing the load along the body axis. Compare a brief pull with sustained exposure.",
  },
  {
    id: "loop",
    name: "Inside loop",
    subtitle: "Energy & changing load",
    entry: 180,
    lesson:
      "A pull bends the flight path upward. Speed converts to altitude during the climb and returns during descent. Aircraft attitude alone does not tell you the G load.",
  },
  {
    id: "aileron_roll",
    name: "Aileron roll",
    subtitle: "Attitude versus G",
    entry: 120,
    lesson:
      "A rolling aircraft can pass through inverted attitudes without sustaining negative G. Follow the signed load and changing flight path together; roll angle is not a G meter.",
  },
  {
    id: "immelmann",
    name: "Immelmann",
    subtitle: "Climb & reversal",
    entry: 180,
    lesson:
      "A half loop trades speed for altitude, followed by a half roll toward upright flight. Observe how the load changes between the pull and the roll.",
  },
  {
    id: "split_s",
    name: "Split-S",
    subtitle: "Descent & recovery",
    entry: 120,
    lesson:
      "A half roll precedes a descending half loop. The aircraft gains kinetic energy as it descends. Watch IAS, available height, and normal load through recovery.",
  },
  {
    id: "cuban_eight",
    name: "Cuban eight",
    subtitle: "Repeated exposure",
    entry: 180,
    lesson:
      "Two looping arcs and rolling descending lines create repeated G exposures. CGEM carries its physiological state across the entire sequence, including recovery intervals.",
  },
];
export const initialConfiguration = (): FlightSimulationRequest => ({
  scenario: "coordinated_turn",
  entry_ias_kts: null,
  altitude_ft: 6000,
  loading: "solo",
  intensity_g: 4,
  pilot: {
    ...DEFAULT_PILOT_CONFIG,
    who_profile: readUserPrefs().defaults.who_profile,
  },
});
export const flagLabel = (flag: number | undefined) =>
  flag === 0
    ? "Baseline"
    : flag === 1
      ? "Loss"
      : flag === 2
        ? "Recovery"
        : "Awaiting sample";
export function physiologyCaption(sample: PhysiologySample | null): string {
  if (!sample) return "Awaiting the first native CGEM sample.";
  if (sample.conscious === 1)
    return "CGEM predicts loss of consciousness at this point in the exposure.";
  if (sample.blackout === 1)
    return "CGEM predicts blackout: the modeled visual response has crossed its loss criterion.";
  if (sample.greyout === 1)
    return "CGEM predicts greyout while the consciousness flag remains unchanged.";
  if ([sample.conscious, sample.blackout, sample.greyout].includes(2))
    return "A CGEM recovery flag is active. Recovery follows the modeled pressure, flow, and reserve response.";
  return "Track head-level arterial pressure and the consciousness reserve as the exposure develops. A baseline flag is not an individual fitness assessment.";
}
