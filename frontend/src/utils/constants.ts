/**
 * Application Constants
 * 
 * Scientific constants and thresholds based on validated aerospace physiology research.
 * 
 * Key References:
 * - Copeland & Whinnery (2023). DOT/FAA/AM-23/6. DOI: 10.21949/1524446
 * - Whinnery & Forster (2015). Visual Neuroscience, 32, E008. DOI: 10.1017/S095252381500005X
 * - Tripp et al. (2009). Human Factors, 51(6), 775-784. DOI: 10.1177/0018720809359631
 */

import type { 
  PhysiologicalThresholds, 
  PhysiologicalState, 
  StandardProfile,
  ManeuverExplanation 
} from '../types';

// =============================================================================
// PHYSIOLOGICAL THRESHOLDS
// =============================================================================

/**
 * Validated physiological thresholds based on centrifuge research.
 * These values represent typical onset points for visual and cognitive symptoms.
 */
export const PHYSIOLOGICAL_THRESHOLDS: PhysiologicalThresholds = {
  // Greyout typically begins around 4.1 G_eff due to reduced retinal perfusion
  greyout_geff: 4.1,
  // Blackout (complete loss of peripheral vision) around 5.0 G_eff
  blackout_geff: 5.0,
  // G-LOC (loss of consciousness) around 5.5 G_eff without countermeasures
  gloc_geff: 5.5,
  // Redout (negative G visual symptoms) around -2.0 Gz
  redout_g: -2.0,
  // Safe range for untrained individuals
  safe_g_range: [-1.0, 4.0],
  // Extended range for trained, G-suited pilots with AGSM
  trained_g_range: [-2.0, 9.0],
};

// =============================================================================
// STATE COLOR PALETTE
// =============================================================================

/**
 * Color scheme for physiological state visualization.
 * Designed for accessibility and scientific publication standards.
 */
export const STATE_COLORS: Record<PhysiologicalState | string, string> = {
  normal: '#22c55e',    // Green - safe operational state
  caution: '#f59e0b',   // Amber - increased vigilance required
  warning: '#f97316',   // Orange - approaching limits
  danger: '#ef4444',    // Red - immediate action required
  critical: '#a855f7',  // Purple - severe physiological stress
  greyout: '#6b7280',   // Gray - peripheral vision loss
  blackout: '#1f2937',  // Dark gray - complete vision loss
  gloc: '#000000',      // Black - unconsciousness
  redout: '#dc2626',    // Dark red - negative G symptoms
};

/**
 * Gradient colors for continuous data visualization
 */
export const CHART_GRADIENTS = {
  primary: ['#0ea5e9', '#3b82f6', '#6366f1'],
  accent: ['#22c55e', '#16a34a', '#15803d'],
  danger: ['#f87171', '#ef4444', '#dc2626'],
  warning: ['#fbbf24', '#f59e0b', '#d97706'],
  neutral: ['#94a3b8', '#64748b', '#475569'],
};

// =============================================================================
// STANDARD PILOT PROFILES
// =============================================================================

/**
 * Standard pilot physiology profiles (who=1..6)
 * Based on CGEM validation data representing population distributions.
 */
export const STANDARD_PROFILES: StandardProfile[] = [
  {
    id: 1,
    label: 'Male: High Cerebrovascular Reserve',
    male: 1,
    howtall: 162.5,
    fnorm: 54.0,
    fcon: 18.0,
    flife: 8.0,
    beta: 2.0,
    bankcon: 15.0,
    BSP: 130.0,
    BDP: 90.0,
    MSP: 213.0,
    MDP: 98.0,
  },
  {
    id: 2,
    label: 'Male: Median Physiology',
    male: 1,
    howtall: 179.0,
    fnorm: 49.5,
    fcon: 19.0,
    flife: 9.0,
    beta: 2.5,
    bankcon: 7.1,
    BSP: 120.0,
    BDP: 80.0,
    MSP: 177.0,
    MDP: 80.0,
  },
  {
    id: 3,
    label: 'Male: Low Reserve, Tall Stature',
    male: 1,
    howtall: 195.6,
    fnorm: 45.0,
    fcon: 20.0,
    flife: 10.0,
    beta: 3.0,
    bankcon: 5.0,
    BSP: 100.0,
    BDP: 60.0,
    MSP: 147.0,
    MDP: 59.0,
  },
  {
    id: 4,
    label: 'Female: High Cerebrovascular Reserve',
    male: 0,
    howtall: 162.5,
    fnorm: 54.0,
    fcon: 18.0,
    flife: 8.0,
    beta: 2.0,
    bankcon: 15.0,
    BSP: 130.0,
    BDP: 90.0,
    MSP: 187.0,
    MDP: 93.0,
  },
  {
    id: 5,
    label: 'Female: Median Physiology',
    male: 0,
    howtall: 179.0,
    fnorm: 49.5,
    fcon: 19.0,
    flife: 9.0,
    beta: 2.5,
    bankcon: 7.1,
    BSP: 120.0,
    BDP: 80.0,
    MSP: 157.0,
    MDP: 76.0,
  },
  {
    id: 6,
    label: 'Female: Low Reserve, Tall Stature',
    male: 0,
    howtall: 195.6,
    fnorm: 45.0,
    fcon: 20.0,
    flife: 10.0,
    beta: 3.0,
    bankcon: 5.0,
    BSP: 100.0,
    BDP: 60.0,
    MSP: 131.0,
    MDP: 60.0,
  },
];

// =============================================================================
// DEFAULT CONFIGURATIONS
// =============================================================================

/**
 * Default countermeasures configuration (unprotected baseline)
 */
export const DEFAULT_COUNTERMEASURES = {
  gsuit_max_psi: 0.0,
  gsuit_coverage_fraction: 0.0,
  agsm_effectiveness: 0.0,
  pbg_max_mmhg: 0.0,
  pretest_other_strain_mmhg: 0.0,
  non_agsm_tensing_limit_mmhg: 0.0,
  seat_tilt_deg: 10.0,
  drug_delay_s: 0.0,
  dehydration_level: 0.0,
};

/**
 * Default custom physiology (median male values)
 */
export const DEFAULT_CUSTOM_PHYSIOLOGY = {
  male: 1 as const,
  height_cm: 179.0,
  baseline_systolic_bp: 120.0,
  baseline_diastolic_bp: 80.0,
  max_systolic_bp: 177.0,
  max_diastolic_bp: 80.0,
  g_tolerance_multiplier: 1.0,
  heart_response_tau_s: 2.5,
  conbank_s: 7.1,
  lifebank_s: 180.0,
};

// =============================================================================
// MANEUVER EXPLANATIONS
// =============================================================================

/**
 * Detailed physiological explanations for each aerobatic maneuver.
 * Content validated against aerospace medicine literature.
 */
export const MANEUVER_EXPLANATIONS: Record<string, ManeuverExplanation> = {
  hammerhead: {
    description: 'A hammerhead turn (stall turn) involves a vertical climb until airspeed approaches zero, followed by a 180° yaw rotation and vertical descent. This classic aerobatic figure requires precise energy management.',
    physiological_effects: 'Initial positive G during pull-up causes blood pooling in lower extremities. The vertical climb reduces G-load to near zero, allowing blood redistribution. The descent phase may involve negative G, potentially causing redout.',
    risk_factors: [
      'Rapid G onset during pull-up phase',
      'Potential spatial disorientation during yaw rotation',
      'Negative G exposure during descent transition',
      'Vestibular stimulation from multi-axis motion'
    ],
    mitigation: [
      'Apply Anti-G straining maneuver (AGSM) during pull-up',
      'Use gradual G onset when operationally feasible',
      'Maintain proper head position during rotation',
      'Ensure adequate recovery altitude'
    ],
  },
  horizontal_rolling_360: {
    description: 'A 360° aileron roll performed while maintaining level flight altitude. The aircraft rotates about its longitudinal axis while the pilot experiences alternating G-forces.',
    physiological_effects: 'Alternating positive and negative G-forces as the aircraft rotates. Blood shifts between upper and lower body throughout the maneuver, challenging cardiovascular reflexes.',
    risk_factors: [
      'Rapid G transitions throughout rotation',
      'Potential spatial disorientation',
      'Vestibular effects from sustained rotation',
      'Cumulative cardiovascular stress'
    ],
    mitigation: [
      'Maintain strong visual reference',
      'Control roll rate to manageable level',
      'Prepare mentally for G transitions',
      'Limit consecutive roll sequences'
    ],
  },
  outside_360: {
    description: 'A 360° outside loop where the pilot experiences sustained negative G throughout the maneuver. This is one of the most physiologically demanding aerobatic figures.',
    physiological_effects: 'Sustained negative G causes blood to pool in the head, leading to increased intracranial and intraocular pressure. Risk of redout (red visual field from retinal engorgement) and severe discomfort.',
    risk_factors: [
      'Sustained negative G exposure (highly stressful)',
      'Significant redout risk',
      'Severe physical discomfort',
      'Risk of subconjunctival hemorrhage or petechiae'
    ],
    mitigation: [
      'Strictly limit negative G duration',
      'Use gradual entry and exit profiles',
      'Ensure proper restraint system fit',
      'Avoid if predisposing medical conditions exist'
    ],
  },
  high_g_turn: {
    description: 'A sustained high-G level turn with peak loads of 6-7 G and brief on/off modulation. Represents tactical combat maneuvering conditions.',
    physiological_effects: 'Sustained +Gz reduces cerebral perfusion significantly, leading to progressive visual symptoms (greyout, tunnel vision, blackout) and potential G-LOC without adequate countermeasures.',
    risk_factors: [
      'High G-onset rate challenging cardiovascular response',
      'Sustained +G exposure depleting physiological reserves',
      'Cumulative fatigue from repeated exposures',
      'Risk of Almost Loss of Consciousness (A-LOC)'
    ],
    mitigation: [
      'Employ continuous AGSM throughout maneuver',
      'Utilize properly fitted anti-G suit with PBG',
      'Manage G-onset rate when tactically feasible',
      'Monitor for prodromal symptoms and disengage if needed'
    ],
  },
  loop_standard: {
    description: 'A standard inside loop with 3-5 G during pull-up and pull-out phases. The foundational aerobatic maneuver demonstrating energy management.',
    physiological_effects: 'Peak +G occurs at entry and exit, potentially inducing greyout. Low/near-zero G over the top allows brief reperfusion and symptom recovery.',
    risk_factors: [
      'High entry speed increasing peak G',
      'Aggressive pull technique',
      'Potential disorientation at apex',
      'Altitude loss if energy mismanaged'
    ],
    mitigation: [
      'Proper energy management',
      'AGSM during pull phases',
      'Maintain adequate altitude margins',
      'Smooth, coordinated control inputs'
    ],
  },
  immelmann_turn: {
    description: 'A half-loop followed by a half-roll, resulting in a 180° direction reversal with altitude gain. Named after WWI ace Max Immelmann.',
    physiological_effects: '+G during half-loop can approach tolerance limits. The roll at the apex introduces vestibular stress while at relatively low G.',
    risk_factors: [
      'Rapid G-onset during initial pull',
      'Spatial disorientation during roll at apex',
      'Energy state misjudgment'
    ],
    mitigation: [
      'Controlled, gradual pull',
      'Strong AGSM application',
      'Clear visual reference before roll',
      'Practice standardized technique'
    ],
  },
  split_s: {
    description: 'Roll inverted followed by a descending half-loop with high +G pull-out. Trades altitude for airspeed and reverses direction.',
    physiological_effects: 'The pull-out phase generates the highest +G loading, presenting the primary risk for greyout/blackout. Significant altitude loss occurs.',
    risk_factors: [
      'High +G at pull-out (primary risk)',
      'Substantial altitude consumption',
      'Speed buildup during descent',
      'Disorientation during inverted phase'
    ],
    mitigation: [
      'Ensure adequate entry altitude',
      'Strong AGSM during pull-out',
      'Moderate pull-out G when possible',
      'Know aircraft limits and terrain clearance'
    ],
  },
  cuban_eight: {
    description: 'Two looping segments connected by half-rolls, tracing a horizontal figure-eight when viewed from the side. A classic competition maneuver.',
    physiological_effects: 'Repeated +G peaks during looping portions. Half-roll segments at low G provide brief recovery periods between high-G phases.',
    risk_factors: [
      'Cumulative +G exposure',
      'Potential disorientation from compound motion',
      'Fatigue over extended sequence',
      'Altitude management complexity'
    ],
    mitigation: [
      'Pace energy through the figure',
      'AGSM during all pull phases',
      'Maintain situational awareness',
      'Plan altitude margins for both loops'
    ],
  },
  vertical_eight: {
    description: 'A vertical figure-eight combining inside and outside loop elements with repeated +G and brief -G transitions.',
    physiological_effects: 'Alternating +/-G transitions can trigger the push-pull effect, where preceding negative G reduces subsequent +G tolerance. Highly demanding cardiovascular profile.',
    risk_factors: [
      'Push-pull effect reducing G tolerance',
      'Repeated +G peaks',
      'Brief -G inducing cephalad blood shifts',
      'Complex spatial orientation requirements'
    ],
    mitigation: [
      'Minimize -G phase duration',
      'Strong AGSM on all +G phases',
      'Adequate conditioning and rest',
      'Consider limiting repetitions'
    ],
  },
  triple_push_pull_loop: {
    description: 'Three successive push-pull loops: brief -G push into inverted arc followed by +G pull-up, repeated three times. A demanding physiological test profile.',
    physiological_effects: 'Alternating cephalad and caudad blood shifts stress cardiovascular autoregulation. Repeated transitions accumulate fatigue and may degrade baroreflex function.',
    risk_factors: [
      'Rapid +/-G transitions',
      'Potential redout during push phases',
      'Greyout/blackout risk during pulls',
      'Cumulative cardiovascular strain'
    ],
    mitigation: [
      'Moderate transition rates',
      'AGSM on all +G phases',
      'Limit -G exposure duration',
      'Ensure adequate hydration and rest'
    ],
  },
};

// =============================================================================
// ECHART THEME
// =============================================================================

/**
 * ECharts dark theme configuration for scientific publications
 */
export const ECHARTS_DARK_THEME = {
  backgroundColor: 'transparent',
  textStyle: {
    color: '#e2e8f0',
    fontFamily: 'Inter, system-ui, sans-serif',
  },
  title: {
    textStyle: {
      color: '#f1f5f9',
      fontSize: 16,
      fontWeight: 600,
    },
    subtextStyle: {
      color: '#94a3b8',
      fontSize: 12,
    },
  },
  legend: {
    textStyle: {
      color: '#cbd5e1',
    },
  },
  tooltip: {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: 'rgba(71, 85, 105, 0.5)',
    textStyle: {
      color: '#f1f5f9',
    },
  },
  axisLine: {
    lineStyle: {
      color: '#475569',
    },
  },
  splitLine: {
    lineStyle: {
      color: 'rgba(71, 85, 105, 0.3)',
    },
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#475569' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: 'rgba(71, 85, 105, 0.2)' } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: '#475569' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: 'rgba(71, 85, 105, 0.2)' } },
  },
};

// =============================================================================
// API CONFIGURATION
// =============================================================================

export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
};

// =============================================================================
// PUBLICATION EXPORT SETTINGS
// =============================================================================

export const PUBLICATION_EXPORT = {
  formats: ['svg', 'png', 'pdf'] as const,
  dpi: 300,
  width: 1200,
  height: 800,
  fontFamily: 'Inter, Arial, sans-serif',
  fontSize: {
    title: 18,
    axis: 12,
    legend: 11,
    annotation: 10,
  },
};
