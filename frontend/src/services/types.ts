/**
 * TypeScript types mirroring the Pydantic schemas in
 * cgem_ext/api/schemas.py.
 *
 * Hand-maintained for now. To regenerate from the committed OpenAPI
 * spec at docs/api/openapi.json:
 *
 *   npx openapi-typescript ../docs/api/openapi.json -o src/services/types.ts
 *
 * Any drift between this file and the Pydantic side is caught by the
 * Phase-5 contract tests in tests/test_api.py the next time the API
 * is exercised.
 */

// ── Pilot config + maneuver descriptors ──────────────────────────────

export type CountermeasuresLabel = 'none' | 'agsm' | 'suit_agsm';

export interface PilotConfigRequest {
  who_profile: number | null;        // 1..6, or null for the custom-arm subject
  g_tolerance_multiplier: number;
  dehydration_level: number;
  countermeasures_label: CountermeasuresLabel;
  gsuit_max_psi: number;
  gsuit_coverage_fraction: number;
  agsm_effectiveness: number;
  pbg_max_mmhg: number;
}

/** Named maneuvers are server-owned; inline inputs must be complete. */
export type ManeuverDescriptors =
  | {
      maneuver: string;
      g_peak_abs?: never;
      dgdt_max_g_per_s?: never;
      profile_duration_s?: never;
    }
  | {
      maneuver?: null;
      g_peak_abs: number;
      dgdt_max_g_per_s: number;
      profile_duration_s: number;
    };

// ── /predict + /sweep ────────────────────────────────────────────────

export interface PredictionRequest {
  maneuver: ManeuverDescriptors;
  pilot: PilotConfigRequest;
}

export interface TargetPrediction {
  target: string;
  censored: boolean;
  /** Continuous: direct surrogate output. Censored: E[time | event=1]. */
  point: number;
  /** Conformal lower bound on `point` (same scale). */
  lo: number | null;
  /** Conformal upper bound on `point`. */
  hi: number | null;
  /** P(event=1) for censored time targets. */
  event_probability?: number | null;
  /** Convenience: P(event) * point for censored time targets. */
  expected_time_s?: number | null;
}

export interface PredictionResponse {
  targets: TargetPrediction[];
  /** True if the input is outside CGEM's training envelope. */
  ood: boolean;
  ood_score: number;
  in_envelope: boolean;
  model_version: string;
  cgem_binary_sha256: string;
  resolved_maneuver: string;
  maneuver_category: string;
  calibration_scope: 'category' | 'global';
  source: string;
}

export interface SweepRequest {
  inputs: PredictionRequest[];
}

export interface SweepResponse {
  results: PredictionResponse[];
}

// ── /run-cgem (mirrors the v2.2.0 pulse-sim CGEMRun JSON shape) ──────

export interface CGEMRunData {
  'Time(s)': number[];
  G: number[];
  G_eff: number[];
  'HLAP(mmHg)': number[];
  'F_con(dl/min)': number[];
  'F_vis(dl/min)': number[];
  'F_bo(dl/min)': number[];
  'c_bank(s)': number[];
  'bo_bank(s)': number[];
  Conscious: number[];
  Greyout: number[];
  Blackout: number[];
}

export interface RunCGEMRequest {
  maneuver: string;
  pilot: PilotConfigRequest;
}

export interface CGEMRunResponse {
  maneuver: string;
  pilot_profile: string;
  duration_s: number;
  time_to_greyout_s: number | null;
  time_to_blackout_s: number | null;
  time_to_gloc_s: number | null;
  data: CGEMRunData;
}

// ── /sensitivity/{target} ────────────────────────────────────────────

export interface SobolFeatureIndex {
  feature: string;
  S1: number;
  S1_conf: number;
  ST: number;
  ST_conf: number;
}

export interface SensitivityResponse {
  target: string;
  censored: boolean;
  fixed_who_profile: string;
  sobol_n_base: number;
  indices: SobolFeatureIndex[];
}

// ── /version + /healthz ──────────────────────────────────────────────

export interface VersionResponse {
  package_version: string;
  cgem_binary_sha256: string;
  dataset_name: string;
  dataset_master_seed: number;
  targets: string[];
}

export interface HealthResponse {
  status: 'ok' | 'degraded';
  detail?: string | null;
}

// ── Default builders for forms ───────────────────────────────────────

export const DEFAULT_PILOT_CONFIG: PilotConfigRequest = {
  who_profile: 2,
  g_tolerance_multiplier: 1.0,
  dehydration_level: 0.0,
  countermeasures_label: 'none',
  gsuit_max_psi: 0.0,
  gsuit_coverage_fraction: 0.0,
  agsm_effectiveness: 0.0,
  pbg_max_mmhg: 0.0,
};

/** Surrogate target names — kept in sync with cgem_ext.surrogate.TARGETS. */
export const TARGET_NAMES = [
  'time_to_greyout_s',
  'time_to_blackout_s',
  'time_to_gloc_s',
  'hlap_min',
  'c_bank_min',
] as const;

export type TargetName = (typeof TARGET_NAMES)[number];
