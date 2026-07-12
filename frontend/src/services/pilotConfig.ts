import type { UserPrefs } from '../state/useUserPrefs';
import type { CountermeasuresLabel, PilotConfigRequest } from './types';

type ProtectionInput = Pick<
  PilotConfigRequest,
  'gsuit_max_psi' | 'gsuit_coverage_fraction' | 'agsm_effectiveness'
>;

const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, Number.isFinite(value) ? value : min));

function normalize(pilot: PilotConfigRequest): PilotConfigRequest {
  const standard = pilot.who_profile !== null;
  const normalized = {
    ...pilot,
    who_profile: standard ? Math.round(clamp(pilot.who_profile!, 1, 6)) : null,
    g_tolerance_multiplier: standard ? 1 : clamp(pilot.g_tolerance_multiplier, 0.5, 2),
    dehydration_level: standard ? 0 : clamp(pilot.dehydration_level, 0, 1),
    gsuit_max_psi: clamp(pilot.gsuit_max_psi, 0, 20),
    gsuit_coverage_fraction: clamp(pilot.gsuit_coverage_fraction, 0, 1),
    agsm_effectiveness: clamp(pilot.agsm_effectiveness, 0, 1),
    pbg_max_mmhg: clamp(pilot.pbg_max_mmhg, 0, 60),
  };
  return { ...normalized, countermeasures_label: countermeasuresLabel(normalized) };
}

export function countermeasuresLabel(input: ProtectionInput): CountermeasuresLabel {
  if (input.agsm_effectiveness <= 0) return 'none';
  return input.gsuit_max_psi > 0 && input.gsuit_coverage_fraction > 0
    ? 'suit_agsm'
    : 'agsm';
}

export function pilotConfigFromPrefs(prefs: UserPrefs): PilotConfigRequest {
  const pilot: PilotConfigRequest = {
    who_profile: prefs.defaults.who_profile,
    g_tolerance_multiplier: 1,
    dehydration_level: prefs.defaults.dehydration_level,
    countermeasures_label: 'none',
    gsuit_max_psi: prefs.defaults.gsuit_max_psi,
    gsuit_coverage_fraction: prefs.defaults.gsuit_coverage_fraction,
    agsm_effectiveness: prefs.defaults.agsm_effectiveness,
    pbg_max_mmhg: prefs.defaults.pbg_max_mmhg,
  };
  return normalize(pilot);
}

export function pilotConfigWithOverrides(
  base: PilotConfigRequest,
  overrides: Partial<PilotConfigRequest>,
): PilotConfigRequest {
  const pilot = { ...base, ...overrides };
  return normalize(pilot);
}
