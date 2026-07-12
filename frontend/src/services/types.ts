/**
 * Stable frontend-facing names for generated API wire contracts.
 * UI-only literals, defaults, and helpers remain handwritten here.
 */
export type {
  CGEMRunData,
  CGEMRunResponse,
  HealthResponse,
  ManeuverDescriptors,
  PilotConfigRequest,
  PredictionRequest,
  PredictionResponse,
  RunCGEMRequest,
  SensitivityResponse,
  SobolFeatureIndex,
  SweepRequest,
  SweepResponse,
  TargetPrediction,
  VersionResponse,
} from './wireTypes';

import type { PilotConfigRequest } from './wireTypes';

export type CountermeasuresLabel = PilotConfigRequest['countermeasures_label'];

export const DEFAULT_PILOT_CONFIG: PilotConfigRequest = {
  who_profile: 2,
  g_tolerance_multiplier: 1,
  dehydration_level: 0,
  countermeasures_label: 'none',
  gsuit_max_psi: 0,
  gsuit_coverage_fraction: 0,
  agsm_effectiveness: 0,
  pbg_max_mmhg: 0,
};

export const TARGET_NAMES = [
  'time_to_greyout_s',
  'time_to_blackout_s',
  'time_to_gloc_s',
  'hlap_min',
  'c_bank_min',
] as const;

export type TargetName = (typeof TARGET_NAMES)[number];
