import { describe, expect, it } from 'vitest';

import { DEFAULT_PREFS } from '../state/useUserPrefs';
import {
  countermeasuresLabel,
  pilotConfigFromPrefs,
  pilotConfigWithOverrides,
} from './pilotConfig';

describe('pilot configuration contract', () => {
  it('derives the label from active protection', () => {
    expect(countermeasuresLabel({
      gsuit_max_psi: 0, gsuit_coverage_fraction: 0, agsm_effectiveness: 0,
    })).toBe('none');
    expect(countermeasuresLabel({
      gsuit_max_psi: 0, gsuit_coverage_fraction: 0, agsm_effectiveness: 0.4,
    })).toBe('agsm');
    expect(countermeasuresLabel({
      gsuit_max_psi: 3, gsuit_coverage_fraction: 0, agsm_effectiveness: 0.4,
    })).toBe('agsm');
    expect(countermeasuresLabel({
      gsuit_max_psi: 3, gsuit_coverage_fraction: 0.6, agsm_effectiveness: 0.4,
    })).toBe('suit_agsm');
  });

  it('maps persisted defaults to an API request', () => {
    const pilot = pilotConfigFromPrefs(DEFAULT_PREFS);
    expect(pilot.who_profile).toBe(DEFAULT_PREFS.defaults.who_profile);
    expect(pilot.gsuit_max_psi).toBe(DEFAULT_PREFS.defaults.gsuit_max_psi);
    expect(pilot.countermeasures_label).toBe('suit_agsm');
  });

  it('neutralizes custom-only physiology for standard profiles', () => {
    const pilot = pilotConfigFromPrefs({
      ...DEFAULT_PREFS,
      defaults: { ...DEFAULT_PREFS.defaults, dehydration_level: 0.8 },
    });
    expect(pilot.dehydration_level).toBe(0);
    expect(pilot.g_tolerance_multiplier).toBe(1);
  });

  it('re-derives the label after overrides', () => {
    const base = pilotConfigFromPrefs(DEFAULT_PREFS);
    const pilot = pilotConfigWithOverrides(base, {
      gsuit_max_psi: 0,
      agsm_effectiveness: 0,
    });
    expect(pilot.countermeasures_label).toBe('none');
  });
});
