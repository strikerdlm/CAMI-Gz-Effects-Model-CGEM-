/**
 * G-Effects Safety Management Dashboard - TypeScript Type Definitions
 * 
 * Based on the FAA CGEM (Combined G-Effects Model) for aerospace physiology.
 * These types support publication-quality scientific visualization.
 * 
 * References:
 * - Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow-based computer modeling 
 *   of Gz-induced effects (DOT/FAA/AM-23/6). DOI: https://doi.org/10.21949/1524446
 * - Copeland, K. (2021). CGEM User's Guide (DOT/FAA/AM-23/5). DOI: https://doi.org/10.21949/1524438
 */

// =============================================================================
// CORE DATA TYPES
// =============================================================================

/**
 * A single sample point in an aerobatic G-profile.
 * Represents instantaneous normal acceleration and its duration.
 */
export interface Sample {
  /** Normal acceleration in G-units (+Gz positive, -Gz negative) */
  nz: number;
  /** Duration this acceleration is maintained, in milliseconds */
  duration_ms: number;
}

/**
 * Aerobatic maneuver profile definition
 */
export interface AerobaticProfile {
  /** Unique identifier (e.g., 'hammerhead', 'loop_standard') */
  id: string;
  /** Source filename */
  filename: string;
  /** Human-readable description */
  description: string;
  /** G-profile samples */
  samples: Sample[];
}

/**
 * Complete profiles dictionary
 */
export type ProfilesDict = Record<string, AerobaticProfile>;

// =============================================================================
// PILOT CONFIGURATION
// =============================================================================

/**
 * Standard pilot physiology profile presets (who=1..6)
 * Based on CGEM Subject() routine parameters
 */
export interface StandardProfile {
  id: number;
  label: string;
  male: 0 | 1;
  /** Height in centimeters (affects heart-brain distance) */
  howtall: number;
  /** Normal cerebral blood flow (dl/min) */
  fnorm: number;
  /** Consciousness threshold flow (dl/min) */
  fcon: number;
  /** Life-critical flow threshold (dl/min) */
  flife: number;
  /** Heart response time constant (seconds) */
  beta: number;
  /** Consciousness reserve bank (seconds) */
  bankcon: number;
  /** Baseline systolic blood pressure (mmHg) */
  BSP: number;
  /** Baseline diastolic blood pressure (mmHg) */
  BDP: number;
  /** Maximum systolic blood pressure (mmHg) */
  MSP: number;
  /** Maximum diastolic blood pressure (mmHg) */
  MDP: number;
}

/**
 * Custom pilot physiology configuration
 */
export interface CustomPhysiology {
  male: 0 | 1;
  height_cm: number;
  baseline_systolic_bp: number;
  baseline_diastolic_bp: number;
  max_systolic_bp: number;
  max_diastolic_bp: number;
  g_tolerance_multiplier: number;
  heart_response_tau_s: number;
  conbank_s: number;
  lifebank_s: number;
}

/**
 * Countermeasures and environmental factors
 */
export interface Countermeasures {
  /** G-suit maximum inflation pressure (PSI) */
  gsuit_max_psi: number;
  /** G-suit body coverage fraction (0.0-0.7) */
  gsuit_coverage_fraction: number;
  /** Anti-G straining maneuver effectiveness (0.0-1.0) */
  agsm_effectiveness: number;
  /** Positive pressure breathing maximum (mmHg) */
  pbg_max_mmhg: number;
  /** Pre-test muscle strain (mmHg) */
  pretest_other_strain_mmhg: number;
  /** Non-AGSM tensing limit (mmHg) */
  non_agsm_tensing_limit_mmhg: number;
  /** Seat tilt from vertical (degrees) */
  seat_tilt_deg: number;
  /** Drug-induced heart rate delay (seconds) */
  drug_delay_s: number;
  /** Dehydration level (0.0-1.0) */
  dehydration_level: number;
}

/**
 * Complete pilot configuration for CGEM simulation
 */
export interface PilotConfig {
  /** Standard profile ID (1-6) or null for custom */
  who_profile: number | null;
  /** Custom physiology (used when who_profile is null) */
  customPhysiology?: CustomPhysiology;
  /** Countermeasures and environmental factors */
  countermeasures: Countermeasures;
}

// =============================================================================
// SIMULATION RESULTS
// =============================================================================

/**
 * CGEM simulation result
 */
export interface CGEMResult {
  /** Time to greyout onset (seconds), null if not reached */
  time_to_greyout_s: number | null;
  /** Time to blackout onset (seconds), null if not reached */
  time_to_blackout_s: number | null;
  /** Time to G-LOC (seconds), null if not reached */
  time_to_gloc_s: number | null;
  
  /** Time series - timestamps in seconds */
  times_s: number[];
  /** G-force values at each timestamp */
  g_values: number[];
  /** Effective G values accounting for countermeasures */
  geff_values: number[];
  
  /** Consciousness flag (0=conscious, 1=unconscious) */
  flags_n2: number[];
  /** Vision flag (0=normal, 1=impaired) */
  flags_ne2: number[];
  /** Blackout flag (0=no blackout, 1=blackout) */
  flags_non2: number[];
  
  /** Consciousness reserve bank values */
  c_bank_values: number[];
  /** Blackout reserve bank values */
  bo_bank_values: number[];
  
  /** Cerebral blood flow for consciousness */
  f_con_values: number[];
  /** Retinal blood flow (central vision) */
  f_vis_values: number[];
  /** Retinal blood flow (peripheral vision) */
  f_bo_values: number[];
  
  /** Heart-level arterial pressure (mmHg) */
  hlap_values: number[];
}

// =============================================================================
// PHYSIOLOGICAL ANALYSIS
// =============================================================================

/**
 * Physiological thresholds for visual/cognitive impairment
 * Based on validated centrifuge and flight data
 */
export interface PhysiologicalThresholds {
  /** G_eff threshold for greyout onset */
  greyout_geff: number;
  /** G_eff threshold for blackout onset */
  blackout_geff: number;
  /** G_eff threshold for G-LOC */
  gloc_geff: number;
  /** Negative G threshold for redout */
  redout_g: number;
  /** Safe G range for untrained individuals [min, max] */
  safe_g_range: [number, number];
  /** Safe G range for trained pilots [min, max] */
  trained_g_range: [number, number];
}

/**
 * Physiological state classification
 */
export type PhysiologicalState = 
  | 'normal'
  | 'caution'
  | 'greyout'
  | 'blackout'
  | 'gloc'
  | 'redout';

/**
 * Duration spent in each physiological state
 */
export type StateDurations = Record<PhysiologicalState, number>;

/**
 * Profile statistics summary
 */
export interface ProfileStats {
  /** Total duration in seconds */
  total_duration_s: number;
  /** Maximum positive G */
  max_positive_g: number;
  /** Maximum negative G (most negative value) */
  max_negative_g: number;
  /** Weighted mean G (by duration) */
  weighted_mean_g: number;
  /** Time spent above +3G threshold */
  time_above_3g_s: number;
  /** Time spent below -1G threshold */
  time_below_neg1g_s: number;
  /** Positive G dose (G·s integral) */
  positive_g_dose: number;
  /** Negative G dose (G·s integral) */
  negative_g_dose: number;
  /** 95th percentile of |G| */
  p95_abs_g: number;
  /** Root mean square G */
  rms_g: number;
}

// =============================================================================
// MANEUVER ANALYSIS
// =============================================================================

/**
 * Detailed maneuver explanation with physiological effects
 */
export interface ManeuverExplanation {
  /** Full description of the maneuver */
  description: string;
  /** Physiological effects on the pilot */
  physiological_effects: string;
  /** Risk factors specific to this maneuver */
  risk_factors: string[];
  /** Recommended mitigation strategies */
  mitigation: string[];
}

/**
 * Maneuver explanations dictionary
 */
export type ManeuverExplanations = Record<string, ManeuverExplanation>;

// =============================================================================
// CHART DATA TYPES
// =============================================================================

/**
 * Data point for scatter plots with physiological state
 */
export interface StateScatterPoint {
  g: number;
  geff: number;
  time: number;
  state: PhysiologicalState;
}

/**
 * Radar chart metric schema
 */
export interface RadarMetric {
  name: string;
  max: number;
}

/**
 * Histogram data
 */
export interface HistogramData {
  labels: string[];
  values: number[];
}

/**
 * Heatmap data for physiological parameters
 */
export interface HeatmapData {
  params: string[];
  matrix: number[][];
  times: number[];
}

/**
 * Complete dashboard data payload
 */
export interface DashboardData {
  times: number[];
  g: number[];
  geff: number[];
  thresholds: PhysiologicalThresholds;
  durations: StateDurations;
  hist: HistogramData;
  heat: HeatmapData;
  radar: {
    schema: RadarMetric[];
    values: number[];
  };
  scatter: StateScatterPoint[];
  banks: {
    c_bank: number[];
    bo_bank: number[];
  };
  flows: {
    f_con: number[];
    f_vis: number[];
    f_bo: number[];
  };
  hlap: number[];
  profile: string;
}

// =============================================================================
// API TYPES
// =============================================================================

/**
 * API request for running CGEM simulation
 */
export interface RunSimulationRequest {
  profile_id: string;
  pilot_config: PilotConfig;
}

/**
 * API response from CGEM simulation
 */
export interface RunSimulationResponse {
  result: CGEMResult;
  tmp_dir: string;
}

/**
 * Batch simulation result
 */
export interface BatchSimulationResult {
  profile_id: string;
  profile_name: string;
  result: CGEMResult;
  stats: ProfileStats;
}

// =============================================================================
// UI STATE TYPES
// =============================================================================

/**
 * Dashboard layout mode
 */
export type LayoutMode = 'grid' | 'single';

/**
 * Available chart types for single-chart view
 */
export type ChartType = 
  | 'lines'
  | 'heatmap'
  | 'histogram'
  | 'radar'
  | 'scatter'
  | 'durations'
  | 'flows'
  | 'banks'
  | 'hlap'
  | '3d';

/**
 * Navigation tabs
 */
export type NavigationTab = 
  | 'overview'
  | 'prediction'
  | 'dashboard'
  | 'batch'
  | 'analysis';

/**
 * Theme mode
 */
export type ThemeMode = 'dark' | 'light' | 'system';
