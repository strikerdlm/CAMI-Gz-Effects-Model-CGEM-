import { describe, expect, it } from 'vitest';

import {
  analysisUrlState,
  batchUrlState,
  dashboardUrlState,
  predictionUrlState,
  readEnumParam,
  readIntParam,
  readManeuverParam,
  setSearchParam,
} from './urlState';

describe('URL state primitives', () => {
  it('accepts catalog maneuvers and rejects unsupported IDs', () => {
    expect(readManeuverParam(new URLSearchParams('maneuver=hammerhead'))).toBe('hammerhead');
    expect(readManeuverParam(new URLSearchParams('maneuver=not-real'), 'high_g_turn')).toBe('high_g_turn');
  });

  it('reads allowlisted enums and bounded integers', () => {
    expect(readEnumParam(new URLSearchParams('view=comparison'), 'view', ['surrogate', 'comparison'] as const, 'surrogate')).toBe('comparison');
    expect(readEnumParam(new URLSearchParams('view=nope'), 'view', ['surrogate', 'comparison'] as const, 'surrogate')).toBe('surrogate');
    expect(readIntParam(new URLSearchParams('pilot=6'), 'pilot', 2, 1, 6)).toBe(6);
    expect(readIntParam(new URLSearchParams('pilot=99'), 'pilot', 2, 1, 6)).toBe(2);
  });

  it('writes immutably and omits defaults', () => {
    const original = new URLSearchParams('keep=yes&view=comparison');
    const next = setSearchParam(original, 'view', 'surrogate', 'surrogate');
    expect(original.toString()).toBe('keep=yes&view=comparison');
    expect(next.toString()).toBe('keep=yes');
  });
});

describe('page schemas', () => {
  it('canonicalizes prediction state and all supported views', () => {
    for (const view of ['surrogate', 'authoritative', 'comparison'] as const) {
      const state = predictionUrlState.read(new URLSearchParams(`maneuver=hammerhead&pilot=6&view=${view}`));
      expect(state.value).toEqual({ maneuver: 'hammerhead', pilot: 6, view });
      expect(predictionUrlState.write(state.value).toString()).toBe(
        `maneuver=hammerhead&pilot=6${view === 'surrogate' ? '' : `&view=${view}`}`,
      );
    }
    expect(predictionUrlState.write(predictionUrlState.defaults).toString()).toBe('');
  });

  it('round trips dashboard state in deterministic order', () => {
    const input = new URLSearchParams('layout=single&chart=flows&preset=max_protection&maneuver=hammerhead');
    const parsed = dashboardUrlState.read(input);
    expect(parsed.invalid).toEqual([]);
    expect(dashboardUrlState.write(parsed.value).toString()).toBe('maneuver=hammerhead&preset=max_protection&chart=flows&layout=single');
  });

  it('round trips batch target, direction, OOD and category filters', () => {
    const parsed = batchUrlState.read(new URLSearchParams('category=military_acm&ood=ood&direction=asc&target=blackout'));
    expect(parsed.value).toEqual({ target: 'blackout', direction: 'asc', ood: 'ood', category: 'military_acm' });
    expect(batchUrlState.write(parsed.value).toString()).toBe('target=blackout&direction=asc&ood=ood&category=military_acm');
  });

  it('round trips analysis target/view and reports material invalid values', () => {
    const parsed = analysisUrlState.read(new URLSearchParams('view=sensitivity&target=time_to_blackout_s'));
    expect(analysisUrlState.write(parsed.value).toString()).toBe('target=time_to_blackout_s&view=sensitivity');
    const invalid = analysisUrlState.read(new URLSearchParams('target=made_up&view=wrong'));
    expect(invalid.value).toEqual(analysisUrlState.defaults);
    expect(invalid.invalid).toEqual(['target', 'view']);
  });
});
