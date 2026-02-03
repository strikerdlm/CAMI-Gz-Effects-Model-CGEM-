/**
 * Scientific Calculation Utilities
 * 
 * Functions for physiological data analysis and statistical calculations.
 * Based on validated aerospace physiology methods.
 */

import type { 
  Sample, 
  ProfileStats, 
  StateDurations, 
  PhysiologicalState,
  CGEMResult 
} from '../types';
import { PHYSIOLOGICAL_THRESHOLDS } from './constants';

// =============================================================================
// PROFILE ANALYSIS
// =============================================================================

/**
 * Calculate comprehensive statistics for a G-profile
 */
export function calculateProfileStats(samples: Sample[]): ProfileStats {
  if (samples.length === 0) {
    return {
      total_duration_s: 0,
      max_positive_g: 0,
      max_negative_g: 0,
      weighted_mean_g: 0,
      time_above_3g_s: 0,
      time_below_neg1g_s: 0,
      positive_g_dose: 0,
      negative_g_dose: 0,
      p95_abs_g: 0,
      rms_g: 0,
    };
  }

  const gValues = samples.map(s => s.nz);
  const durations = samples.map(s => s.duration_ms);
  const totalMs = durations.reduce((sum, d) => sum + d, 0);

  // Basic statistics
  const maxPositiveG = Math.max(...gValues, 0);
  const maxNegativeG = Math.min(...gValues, 0);

  // Weighted mean G
  const weightedSum = samples.reduce((sum, s) => sum + s.nz * s.duration_ms, 0);
  const weightedMeanG = totalMs > 0 ? weightedSum / totalMs : 0;

  // Time in specific G ranges
  const timeAbove3G = samples
    .filter(s => s.nz > 3.0)
    .reduce((sum, s) => sum + s.duration_ms, 0) / 1000;

  const timeBelowNeg1G = samples
    .filter(s => s.nz < -1.0)
    .reduce((sum, s) => sum + s.duration_ms, 0) / 1000;

  // G-dose calculations (integral of |G| over time)
  const positiveGDose = samples
    .filter(s => s.nz > 0)
    .reduce((sum, s) => sum + s.nz * (s.duration_ms / 1000), 0);

  const negativeGDose = samples
    .filter(s => s.nz < 0)
    .reduce((sum, s) => sum + Math.abs(s.nz) * (s.duration_ms / 1000), 0);

  // Weighted 95th percentile of |G|
  const p95AbsG = weightedPercentile(
    gValues.map(g => Math.abs(g)),
    durations,
    95
  );

  // Root Mean Square G
  const meanSquare = samples.reduce((sum, s) => 
    sum + (s.nz * s.nz) * s.duration_ms, 0) / Math.max(1, totalMs);
  const rmsG = Math.sqrt(meanSquare);

  return {
    total_duration_s: totalMs / 1000,
    max_positive_g: maxPositiveG,
    max_negative_g: maxNegativeG,
    weighted_mean_g: weightedMeanG,
    time_above_3g_s: timeAbove3G,
    time_below_neg1g_s: timeBelowNeg1G,
    positive_g_dose: positiveGDose,
    negative_g_dose: negativeGDose,
    p95_abs_g: p95AbsG,
    rms_g: rmsG,
  };
}

/**
 * Build time series arrays from samples for plotting
 */
export function buildTimeSeries(samples: Sample[]): { times: number[]; gValues: number[] } {
  const times: number[] = [];
  const gValues: number[] = [];
  let currentTime = 0;

  for (const sample of samples) {
    // Start point
    times.push(currentTime / 1000);
    gValues.push(sample.nz);
    // End point (step function)
    currentTime += sample.duration_ms;
    times.push(currentTime / 1000);
    gValues.push(sample.nz);
  }

  return { times, gValues };
}

// =============================================================================
// PHYSIOLOGICAL STATE CLASSIFICATION
// =============================================================================

/**
 * Classify physiological state based on G and G_eff values
 */
export function classifyPhysiologicalState(
  g: number, 
  geff: number
): PhysiologicalState {
  // Check for redout first (negative G)
  if (g < PHYSIOLOGICAL_THRESHOLDS.redout_g) {
    return 'redout';
  }

  // G-LOC threshold
  if (geff >= PHYSIOLOGICAL_THRESHOLDS.gloc_geff) {
    return 'gloc';
  }

  // Blackout threshold
  if (geff >= PHYSIOLOGICAL_THRESHOLDS.blackout_geff) {
    return 'blackout';
  }

  // Greyout threshold
  if (geff >= PHYSIOLOGICAL_THRESHOLDS.greyout_geff) {
    return 'greyout';
  }

  // Check if outside safe range
  const [minSafe, maxSafe] = PHYSIOLOGICAL_THRESHOLDS.safe_g_range;
  if (g < minSafe || g > maxSafe) {
    return 'caution';
  }

  return 'normal';
}

/**
 * Get human-readable state label
 */
export function getStateLabel(state: PhysiologicalState): string {
  const labels: Record<PhysiologicalState, string> = {
    normal: 'Normal',
    caution: 'Caution',
    greyout: 'Greyout Risk',
    blackout: 'Blackout Risk',
    gloc: 'G-LOC Risk',
    redout: 'Redout Risk',
  };
  return labels[state];
}

/**
 * Compute time spent in each physiological state
 */
export function computeStateDurations(
  times: number[],
  gValues: number[],
  geffValues: number[]
): StateDurations {
  const durations: StateDurations = {
    normal: 0,
    caution: 0,
    greyout: 0,
    blackout: 0,
    gloc: 0,
    redout: 0,
  };

  if (times.length < 2 || times.length !== gValues.length || times.length !== geffValues.length) {
    return durations;
  }

  for (let i = 0; i < times.length - 1; i++) {
    const dt = Math.max(0, times[i + 1] - times[i]);
    const state = classifyPhysiologicalState(gValues[i], geffValues[i]);
    durations[state] += dt;
  }

  return durations;
}

// =============================================================================
// STATISTICAL FUNCTIONS
// =============================================================================

/**
 * Calculate weighted percentile
 * @param values - Array of values
 * @param weights - Array of weights (e.g., durations)
 * @param percentile - Desired percentile (0-100)
 */
export function weightedPercentile(
  values: number[],
  weights: number[],
  percentile: number
): number {
  if (values.length === 0 || weights.length === 0 || values.length !== weights.length) {
    return NaN;
  }

  if (percentile <= 0) return Math.min(...values);
  if (percentile >= 100) return Math.max(...values);

  // Create array of [value, weight] pairs and sort by value
  const pairs = values.map((v, i) => ({ value: v, weight: weights[i] }));
  pairs.sort((a, b) => a.value - b.value);

  // Calculate cumulative weights
  const totalWeight = pairs.reduce((sum, p) => sum + p.weight, 0);
  const cutoff = (percentile / 100) * totalWeight;

  let cumWeight = 0;
  for (const pair of pairs) {
    cumWeight += pair.weight;
    if (cumWeight >= cutoff) {
      return pair.value;
    }
  }

  return pairs[pairs.length - 1].value;
}

/**
 * Calculate moving average for smoothing
 */
export function movingAverage(values: number[], windowSize: number): number[] {
  const result: number[] = [];
  const halfWindow = Math.floor(windowSize / 2);

  for (let i = 0; i < values.length; i++) {
    const start = Math.max(0, i - halfWindow);
    const end = Math.min(values.length, i + halfWindow + 1);
    const window = values.slice(start, end);
    const avg = window.reduce((sum, v) => sum + v, 0) / window.length;
    result.push(avg);
  }

  return result;
}

/**
 * Calculate histogram bins
 */
export function calculateHistogram(
  values: number[],
  bins: number = 20
): { labels: string[]; counts: number[] } {
  if (values.length === 0) {
    return { labels: [], counts: [] };
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const binWidth = (max - min) / bins;

  const counts = new Array(bins).fill(0);
  const labels: string[] = [];

  for (let i = 0; i < bins; i++) {
    const binStart = min + i * binWidth;
    const binEnd = binStart + binWidth;
    labels.push(`${binStart.toFixed(1)}–${binEnd.toFixed(1)}`);
  }

  for (const value of values) {
    let binIndex = Math.floor((value - min) / binWidth);
    // Handle edge case where value equals max
    if (binIndex >= bins) binIndex = bins - 1;
    if (binIndex >= 0) counts[binIndex]++;
  }

  return { labels, counts };
}

// =============================================================================
// SIMULATION RESULT ANALYSIS
// =============================================================================

/**
 * Extract key metrics from CGEM simulation result
 */
export function extractResultMetrics(result: CGEMResult): {
  greyoutTime: string;
  blackoutTime: string;
  glocTime: string;
  maxG: number;
  maxGeff: number;
  duration: number;
} {
  const formatTime = (t: number | null): string => {
    return t !== null ? `${t.toFixed(2)}s` : '—';
  };

  return {
    greyoutTime: formatTime(result.time_to_greyout_s),
    blackoutTime: formatTime(result.time_to_blackout_s),
    glocTime: formatTime(result.time_to_gloc_s),
    maxG: result.g_values.length > 0 ? Math.max(...result.g_values) : 0,
    maxGeff: result.geff_values.length > 0 ? Math.max(...result.geff_values) : 0,
    duration: result.times_s.length > 0 ? result.times_s[result.times_s.length - 1] : 0,
  };
}

/**
 * Generate radar chart data from simulation results
 */
export function generateRadarData(
  result: CGEMResult,
  stats: ProfileStats
): { schema: Array<{ name: string; max: number }>; values: number[] } {
  const maxG = Math.max(...result.g_values.map(Math.abs), 1);
  const maxGeff = Math.max(...result.geff_values, 1);

  const durations = computeStateDurations(
    result.times_s,
    result.g_values,
    result.geff_values
  );

  const timeAboveGreyout = durations.greyout + durations.blackout + durations.gloc;
  const timeRedout = durations.redout;

  const schema = [
    { name: 'Max |G|', max: Math.ceil(maxG * 1.2) },
    { name: 'Max G_eff', max: Math.ceil(maxGeff * 1.2) },
    { name: 'Greyout+ (s)', max: Math.max(timeAboveGreyout * 1.2, 1) },
    { name: 'Redout (s)', max: Math.max(timeRedout * 1.2, 1) },
    { name: 'RMS G', max: Math.ceil(stats.rms_g * 1.5) },
  ];

  const values = [
    maxG,
    maxGeff,
    timeAboveGreyout,
    timeRedout,
    stats.rms_g,
  ];

  return { schema, values };
}

// =============================================================================
// FORMATTING UTILITIES
// =============================================================================

/**
 * Format G value with appropriate precision
 */
export function formatG(value: number, precision: number = 1): string {
  return value >= 0 ? `+${value.toFixed(precision)}G` : `${value.toFixed(precision)}G`;
}

/**
 * Format duration in human-readable format
 */
export function formatDuration(seconds: number): string {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`;
  }
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
}

/**
 * Format percentage
 */
export function formatPercent(value: number, precision: number = 1): string {
  return `${(value * 100).toFixed(precision)}%`;
}
