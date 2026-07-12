import { describe, expect, it } from 'vitest';

import type { PredictionResponse } from '../services/types';
import { compareEventRisk, compareProfileNames } from './BatchPage';

function prediction(
  probability: number,
  conditionalTime: number,
  maneuver = 'test',
): PredictionResponse {
  return {
    targets: [{
      target: 'time_to_gloc_s', censored: true, point: conditionalTime,
      lo: null, hi: null, event_probability: probability,
      expected_time_s: probability * conditionalTime,
    }],
    ood: false, ood_score: 0, in_envelope: true,
    model_version: 'test', cgem_binary_sha256: 'abc', source: 'surrogate',
    resolved_maneuver: maneuver, maneuver_category: 'training',
    calibration_scope: 'category',
  };
}

describe('batch event-risk ranking', () => {
  it('ranks higher event probability first, independent of P times time', () => {
    const highRisk = prediction(0.8, 12);
    const lowRisk = prediction(0.1, 2);
    expect([lowRisk, highRisk].sort((a, b) => compareEventRisk(a, b, 'time_to_gloc_s'))[0])
      .toBe(highRisk);
  });

  it('uses earlier conditional time as a tie-breaker', () => {
    const early = prediction(0.5, 4);
    const late = prediction(0.5, 9);
    expect([late, early].sort((a, b) => compareEventRisk(a, b, 'time_to_gloc_s'))[0])
      .toBe(early);
  });

  it('uses maneuver ID as the stable final tie-breaker', () => {
    const alpha = prediction(0.5, 4, 'alpha');
    const bravo = prediction(0.5, 4, 'bravo');
    expect([bravo, alpha].sort((a, b) => compareEventRisk(a, b, 'time_to_gloc_s'))[0])
      .toBe(alpha);
  });
});

describe('batch profile-name direction', () => {
  it('sorts profile names Z–A for descending', () => {
    expect(['alpha', 'charlie', 'bravo'].sort((a, b) => compareProfileNames(a, b, 'desc')))
      .toEqual(['charlie', 'bravo', 'alpha']);
  });

  it('sorts profile names A–Z for ascending', () => {
    expect(['charlie', 'alpha', 'bravo'].sort((a, b) => compareProfileNames(a, b, 'asc')))
      .toEqual(['alpha', 'bravo', 'charlie']);
  });
});
