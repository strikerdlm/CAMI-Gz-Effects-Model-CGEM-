import { MANEUVERS_BY_ID, type ManeuverCategory } from '../data/maneuvers';
import { TARGET_NAMES, type TargetName } from './types';

export interface UrlStateResult<T> {
  value: T;
  invalid: string[];
}

export function readManeuverParam(params: URLSearchParams, fallback = 'high_g_turn'): string {
  const requested = params.get('maneuver');
  return requested && requested in MANEUVERS_BY_ID ? requested : fallback;
}

export function readEnumParam<T extends string>(
  params: URLSearchParams,
  key: string,
  allowed: readonly T[],
  fallback: T,
): T {
  const requested = params.get(key);
  return requested !== null && allowed.includes(requested as T) ? requested as T : fallback;
}

export function readIntParam(
  params: URLSearchParams,
  key: string,
  fallback: number,
  minimum = Number.MIN_SAFE_INTEGER,
  maximum = Number.MAX_SAFE_INTEGER,
): number {
  const requested = params.get(key);
  if (requested === null || !/^-?\d+$/.test(requested)) return fallback;
  const value = Number(requested);
  return Number.isSafeInteger(value) && value >= minimum && value <= maximum ? value : fallback;
}

export function setSearchParam(
  params: URLSearchParams,
  key: string,
  value: string,
  defaultValue?: string,
): URLSearchParams {
  const next = new URLSearchParams(params);
  if (value === defaultValue || value === '') next.delete(key);
  else next.set(key, value);
  return next;
}

function invalidKeys(
  params: URLSearchParams,
  validators: Readonly<Record<string, (value: string) => boolean>>,
): string[] {
  return Object.keys(validators).filter((key) => {
    const value = params.get(key);
    return value !== null && !validators[key](value);
  });
}

function ordered(entries: readonly [string, string, string][]): URLSearchParams {
  let params = new URLSearchParams();
  for (const [key, value, defaultValue] of entries) {
    params = setSearchParam(params, key, value, defaultValue);
  }
  return params;
}

const isManeuver = (value: string) => value in MANEUVERS_BY_ID;
const oneOf = <T extends string>(allowed: readonly T[]) => (value: string) => allowed.includes(value as T);

export type PredictionView = 'surrogate' | 'authoritative' | 'comparison';
export interface PredictionUrlState { maneuver: string; pilot: number; view: PredictionView }
const PREDICTION_VIEWS = ['surrogate', 'authoritative', 'comparison'] as const;
export const predictionUrlState = {
  defaults: { maneuver: 'high_g_turn', pilot: 2, view: 'surrogate' } satisfies PredictionUrlState,
  read(params: URLSearchParams): UrlStateResult<PredictionUrlState> {
    const value = {
      maneuver: readManeuverParam(params),
      pilot: readIntParam(params, 'pilot', 2, 1, 6),
      view: readEnumParam(params, 'view', PREDICTION_VIEWS, 'surrogate'),
    };
    return { value, invalid: invalidKeys(params, {
      maneuver: isManeuver,
      pilot: (v) => /^[1-6]$/.test(v),
      view: oneOf(PREDICTION_VIEWS),
    }) };
  },
  write(value: PredictionUrlState): URLSearchParams {
    return ordered([
      ['maneuver', value.maneuver, 'high_g_turn'],
      ['pilot', String(value.pilot), '2'],
      ['view', value.view, 'surrogate'],
    ]);
  },
};

export type DashboardChart = 'lines' | 'heatmap' | 'radar' | 'histogram' | 'durations' | 'flows';
export type DashboardLayout = 'grid' | 'single';
export type DashboardPreset = 'elite_balanced' | 'aggressive_sortie' | 'max_protection' | 'degraded_state';
export interface DashboardUrlState { maneuver: string; preset: DashboardPreset; chart: DashboardChart; layout: DashboardLayout }
const DASHBOARD_PRESETS = ['elite_balanced', 'aggressive_sortie', 'max_protection', 'degraded_state'] as const;
const DASHBOARD_CHARTS = ['lines', 'heatmap', 'radar', 'histogram', 'durations', 'flows'] as const;
const DASHBOARD_LAYOUTS = ['grid', 'single'] as const;
export const dashboardUrlState = {
  defaults: { maneuver: 'high_g_turn', preset: 'elite_balanced', chart: 'lines', layout: 'grid' } satisfies DashboardUrlState,
  read(params: URLSearchParams): UrlStateResult<DashboardUrlState> {
    return { value: {
      maneuver: readManeuverParam(params),
      preset: readEnumParam(params, 'preset', DASHBOARD_PRESETS, 'elite_balanced'),
      chart: readEnumParam(params, 'chart', DASHBOARD_CHARTS, 'lines'),
      layout: readEnumParam(params, 'layout', DASHBOARD_LAYOUTS, 'grid'),
    }, invalid: invalidKeys(params, { maneuver: isManeuver, preset: oneOf(DASHBOARD_PRESETS), chart: oneOf(DASHBOARD_CHARTS), layout: oneOf(DASHBOARD_LAYOUTS) }) };
  },
  write(value: DashboardUrlState): URLSearchParams {
    return ordered([['maneuver', value.maneuver, 'high_g_turn'], ['preset', value.preset, 'elite_balanced'], ['chart', value.chart, 'lines'], ['layout', value.layout, 'grid']]);
  },
};

export type BatchTarget = 'profile' | 'gloc' | 'blackout' | 'greyout' | 'ood';
export type BatchDirection = 'asc' | 'desc';
export type BatchOod = 'all' | 'in-envelope' | 'ood';
export type BatchCategory = 'all' | ManeuverCategory;
export interface BatchUrlState { target: BatchTarget; direction: BatchDirection; ood: BatchOod; category: BatchCategory }
const BATCH_TARGETS = ['profile', 'gloc', 'blackout', 'greyout', 'ood'] as const;
const DIRECTIONS = ['asc', 'desc'] as const;
const OOD_FILTERS = ['all', 'in-envelope', 'ood'] as const;
const CATEGORIES = ['all', 'championship', 'military_acm', 'extreme_post_stall', 'training', 'conceptual'] as const;
export const batchUrlState = {
  defaults: { target: 'gloc', direction: 'desc', ood: 'all', category: 'all' } satisfies BatchUrlState,
  read(params: URLSearchParams): UrlStateResult<BatchUrlState> {
    return { value: { target: readEnumParam(params, 'target', BATCH_TARGETS, 'gloc'), direction: readEnumParam(params, 'direction', DIRECTIONS, 'desc'), ood: readEnumParam(params, 'ood', OOD_FILTERS, 'all'), category: readEnumParam(params, 'category', CATEGORIES, 'all') }, invalid: invalidKeys(params, { target: oneOf(BATCH_TARGETS), direction: oneOf(DIRECTIONS), ood: oneOf(OOD_FILTERS), category: oneOf(CATEGORIES) }) };
  },
  write(value: BatchUrlState): URLSearchParams {
    return ordered([['target', value.target, 'gloc'], ['direction', value.direction, 'desc'], ['ood', value.ood, 'all'], ['category', value.category, 'all']]);
  },
};

export type AnalysisView = 'explanation' | 'sensitivity';
export interface AnalysisUrlState { target: TargetName; view: AnalysisView }
const ANALYSIS_VIEWS = ['explanation', 'sensitivity'] as const;
export const analysisUrlState = {
  defaults: { target: 'time_to_gloc_s', view: 'explanation' } satisfies AnalysisUrlState,
  read(params: URLSearchParams): UrlStateResult<AnalysisUrlState> {
    return { value: { target: readEnumParam(params, 'target', TARGET_NAMES, 'time_to_gloc_s'), view: readEnumParam(params, 'view', ANALYSIS_VIEWS, 'explanation') }, invalid: invalidKeys(params, { target: oneOf(TARGET_NAMES), view: oneOf(ANALYSIS_VIEWS) }) };
  },
  write(value: AnalysisUrlState): URLSearchParams {
    return ordered([['target', value.target, 'time_to_gloc_s'], ['view', value.view, 'explanation']]);
  },
};
