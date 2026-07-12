/**
 * Mock Data Service
 * 
 * Test/development fixtures only. These heuristic results must never feed
 * production result views or be represented as authoritative CGEM output.
 */

import type { 
  Sample, 
  AerobaticProfile, 
  CGEMResult,
  PilotConfig 
} from '../types';
import { PHYSIOLOGICAL_THRESHOLDS, STANDARD_PROFILES } from '../utils/constants';

// =============================================================================
// AEROBATIC PROFILE DATA
// =============================================================================

/**
 * Hammerhead (stall turn) profile
 */
const hammerheadSamples: Sample[] = [
  { nz: 0.0, duration_ms: 1000 },
  { nz: 3.5, duration_ms: 2000 },
  { nz: 2.0, duration_ms: 1500 },
  { nz: 0.3, duration_ms: 1000 },
  { nz: 0.0, duration_ms: 1500 },
  { nz: -0.5, duration_ms: 800 },
  { nz: 0.0, duration_ms: 500 },
  { nz: 2.5, duration_ms: 1500 },
  { nz: 1.0, duration_ms: 1000 },
];

/**
 * High-G turn profile (tactical maneuver)
 */
const highGTurnSamples: Sample[] = [
  { nz: 1.0, duration_ms: 1000 },
  { nz: 3.0, duration_ms: 500 },
  { nz: 5.0, duration_ms: 800 },
  { nz: 6.5, duration_ms: 3000 },
  { nz: 7.0, duration_ms: 2000 },
  { nz: 6.5, duration_ms: 2500 },
  { nz: 5.5, duration_ms: 1500 },
  { nz: 4.0, duration_ms: 1000 },
  { nz: 2.0, duration_ms: 800 },
  { nz: 1.0, duration_ms: 500 },
];

/**
 * Standard loop profile
 */
const loopStandardSamples: Sample[] = [
  { nz: 1.0, duration_ms: 1000 },
  { nz: 3.5, duration_ms: 1500 },
  { nz: 4.5, duration_ms: 1000 },
  { nz: 3.0, duration_ms: 1000 },
  { nz: 1.5, duration_ms: 800 },
  { nz: 0.5, duration_ms: 1000 },
  { nz: 0.0, duration_ms: 500 },
  { nz: 1.0, duration_ms: 800 },
  { nz: 3.0, duration_ms: 1000 },
  { nz: 4.0, duration_ms: 800 },
  { nz: 3.0, duration_ms: 600 },
  { nz: 1.0, duration_ms: 500 },
];

/**
 * Outside 360 loop profile (sustained negative G)
 */
const outside360Samples: Sample[] = [
  { nz: 1.0, duration_ms: 500 },
  { nz: 0.0, duration_ms: 300 },
  { nz: -1.0, duration_ms: 800 },
  { nz: -2.0, duration_ms: 1500 },
  { nz: -2.5, duration_ms: 2000 },
  { nz: -2.0, duration_ms: 1500 },
  { nz: -1.0, duration_ms: 800 },
  { nz: 0.0, duration_ms: 300 },
  { nz: 1.0, duration_ms: 500 },
];

/**
 * Immelmann turn profile
 */
const immelmannSamples: Sample[] = [
  { nz: 1.0, duration_ms: 800 },
  { nz: 3.0, duration_ms: 1200 },
  { nz: 4.5, duration_ms: 1500 },
  { nz: 4.0, duration_ms: 1000 },
  { nz: 2.5, duration_ms: 800 },
  { nz: 1.0, duration_ms: 600 },
  { nz: 0.5, duration_ms: 400 },
  { nz: 1.0, duration_ms: 500 },
];

/**
 * Split-S profile
 */
const splitSSamples: Sample[] = [
  { nz: 1.0, duration_ms: 500 },
  { nz: 0.5, duration_ms: 300 },
  { nz: 0.0, duration_ms: 500 },
  { nz: -0.5, duration_ms: 400 },
  { nz: 2.0, duration_ms: 800 },
  { nz: 4.0, duration_ms: 1200 },
  { nz: 5.0, duration_ms: 1500 },
  { nz: 4.0, duration_ms: 800 },
  { nz: 2.0, duration_ms: 500 },
  { nz: 1.0, duration_ms: 400 },
];

/**
 * Cuban Eight profile
 */
const cubanEightSamples: Sample[] = [
  { nz: 1.0, duration_ms: 500 },
  { nz: 3.5, duration_ms: 1200 },
  { nz: 4.0, duration_ms: 1000 },
  { nz: 2.5, duration_ms: 800 },
  { nz: 1.0, duration_ms: 600 },
  { nz: 0.5, duration_ms: 500 },
  { nz: 1.0, duration_ms: 500 },
  { nz: 3.5, duration_ms: 1200 },
  { nz: 4.0, duration_ms: 1000 },
  { nz: 2.5, duration_ms: 800 },
  { nz: 1.0, duration_ms: 600 },
];

/**
 * Vertical Eight profile
 */
const verticalEightSamples: Sample[] = [
  { nz: 1.0, duration_ms: 400 },
  { nz: 4.0, duration_ms: 1500 },
  { nz: 2.0, duration_ms: 800 },
  { nz: 0.5, duration_ms: 500 },
  { nz: -0.5, duration_ms: 400 },
  { nz: -1.0, duration_ms: 600 },
  { nz: 0.0, duration_ms: 300 },
  { nz: 4.0, duration_ms: 1500 },
  { nz: 2.0, duration_ms: 800 },
  { nz: 1.0, duration_ms: 400 },
];

/**
 * Triple push-pull loop profile
 */
const triplePushPullLoopSamples: Sample[] = [
  // First push-pull
  { nz: 1.0, duration_ms: 300 },
  { nz: -1.5, duration_ms: 800 },
  { nz: 0.0, duration_ms: 200 },
  { nz: 4.5, duration_ms: 1200 },
  { nz: 2.0, duration_ms: 500 },
  // Second push-pull
  { nz: -1.5, duration_ms: 800 },
  { nz: 0.0, duration_ms: 200 },
  { nz: 4.5, duration_ms: 1200 },
  { nz: 2.0, duration_ms: 500 },
  // Third push-pull
  { nz: -1.5, duration_ms: 800 },
  { nz: 0.0, duration_ms: 200 },
  { nz: 4.5, duration_ms: 1200 },
  { nz: 1.0, duration_ms: 400 },
];

/**
 * Horizontal rolling 360 profile
 */
const horizontalRolling360Samples: Sample[] = [
  { nz: 1.0, duration_ms: 500 },
  { nz: 0.5, duration_ms: 400 },
  { nz: -0.5, duration_ms: 500 },
  { nz: -1.0, duration_ms: 600 },
  { nz: -0.5, duration_ms: 500 },
  { nz: 0.5, duration_ms: 400 },
  { nz: 1.0, duration_ms: 500 },
];

// =============================================================================
// PROFILE REGISTRY
// =============================================================================

export const AEROBATIC_PROFILES: Record<string, AerobaticProfile> = {
  hammerhead: {
    id: 'hammerhead',
    filename: 'hammerhead.txt',
    description: 'Hammerhead (stall-turn): vertical climb, 180° yaw, vertical descent',
    samples: hammerheadSamples,
  },
  high_g_turn: {
    id: 'high_g_turn',
    filename: 'high_g_turn.txt',
    description: 'Sustained high-G level turn with 6–7 G plateau and on/off modulation',
    samples: highGTurnSamples,
  },
  loop_standard: {
    id: 'loop_standard',
    filename: 'loop_standard.txt',
    description: 'Standard loop with 3–5 G pull-up and pull-out phases',
    samples: loopStandardSamples,
  },
  outside_360: {
    id: 'outside_360',
    filename: 'outside360.txt',
    description: '360° outside loop sustaining −G throughout',
    samples: outside360Samples,
  },
  immelmann_turn: {
    id: 'immelmann_turn',
    filename: 'immelmann_turn.txt',
    description: 'Half-loop to half-roll Immelmann with high +G pull-up',
    samples: immelmannSamples,
  },
  split_s: {
    id: 'split_s',
    filename: 'split_s.txt',
    description: 'Split-S: roll inverted then descending half-loop with high +G pull-out',
    samples: splitSSamples,
  },
  cuban_eight: {
    id: 'cuban_eight',
    filename: 'cuban_eight.txt',
    description: 'Cuban Eight: two looping segments joined by half-rolls',
    samples: cubanEightSamples,
  },
  vertical_eight: {
    id: 'vertical_eight',
    filename: 'vertical_eight.txt',
    description: 'Vertical figure eight with repeated +G exposures and brief −G transitions',
    samples: verticalEightSamples,
  },
  triple_push_pull_loop: {
    id: 'triple_push_pull_loop',
    filename: 'triple_push_pull_loop.txt',
    description: 'Triple push–pull loop: repeated push (−G) then pull (+G) ×3',
    samples: triplePushPullLoopSamples,
  },
  horizontal_rolling_360: {
    id: 'horizontal_rolling_360',
    filename: 'horizontalrolling360.txt',
    description: '360° aileron roll while maintaining level flight',
    samples: horizontalRolling360Samples,
  },
};

// =============================================================================
// CGEM RESULT SIMULATION
// =============================================================================

/**
 * Simulate CGEM model output based on G-profile and pilot configuration.
 * This is a simplified model for demonstration - the real CGEM Fortran
 * model provides more accurate physiological predictions.
 */
export function simulateCGEMResult(
  profile: AerobaticProfile,
  config: PilotConfig
): CGEMResult {
  const clamp = (value: number, min: number, max: number): number =>
    Math.min(max, Math.max(min, value));

  // Build time series from samples
  const times_s: number[] = [];
  const g_values: number[] = [];
  const geff_values: number[] = [];
  const flags_n2: number[] = [];
  const flags_ne2: number[] = [];
  const flags_non2: number[] = [];
  const c_bank_values: number[] = [];
  const bo_bank_values: number[] = [];
  const f_con_values: number[] = [];
  const f_vis_values: number[] = [];
  const f_bo_values: number[] = [];
  const hlap_values: number[] = [];

  const matchedProfile = config.who_profile
    ? STANDARD_PROFILES.find((candidate) => candidate.id === config.who_profile)
    : undefined;

  const customPhysiology = config.customPhysiology;
  const baselineFlow = matchedProfile?.fnorm ?? (customPhysiology ? 49.5 * customPhysiology.g_tolerance_multiplier : 49.5);
  const baseConsciousnessBank = matchedProfile?.bankcon ?? customPhysiology?.conbank_s ?? 7.1;
  const baseBlackoutBank = Math.max(3.5, baseConsciousnessBank * 0.72);
  const responseTauSeconds = matchedProfile?.beta ?? customPhysiology?.heart_response_tau_s ?? 2.5;

  const baselineSystolic = matchedProfile?.BSP ?? customPhysiology?.baseline_systolic_bp ?? 120;
  const baselineDiastolic = matchedProfile?.BDP ?? customPhysiology?.baseline_diastolic_bp ?? 80;
  const baselineMAP = (baselineSystolic + 2 * baselineDiastolic) / 3;

  const agsmEffectiveness = clamp(config.countermeasures.agsm_effectiveness, 0, 1);
  const gSuitPressurePsi = clamp(config.countermeasures.gsuit_max_psi, 0, 10);
  const seatTiltDegrees = clamp(config.countermeasures.seat_tilt_deg, 0, 45);
  const dehydrationLevel = clamp(config.countermeasures.dehydration_level, 0, 1);
  const pbgFactor = clamp(config.countermeasures.pbg_max_mmhg / 120, 0, 1);

  const toleranceBoost = 1 + agsmEffectiveness * 0.06 + gSuitPressurePsi * 0.008 + seatTiltDegrees * 0.0015 - dehydrationLevel * 0.08;
  const thresholdScale = clamp(toleranceBoost, 0.82, 1.22);

  const greyoutGeff = PHYSIOLOGICAL_THRESHOLDS.greyout_geff * thresholdScale;
  const blackoutGeff = PHYSIOLOGICAL_THRESHOLDS.blackout_geff * thresholdScale;
  const glocGeff = PHYSIOLOGICAL_THRESHOLDS.gloc_geff * thresholdScale;

  let currentTime = 0;
  let consciousnessBank = baseConsciousnessBank;
  let blackoutBank = baseBlackoutBank;
  let effectiveGState = 1.0;

  let greyoutTime: number | null = null;
  let blackoutTime: number | null = null;
  let glocTime: number | null = null;

  // Process each sample at 10ms resolution
  for (const sample of profile.samples) {
    const steps = Math.max(1, Math.floor(sample.duration_ms / 10));
    const dt = sample.duration_ms / steps / 1000; // seconds per step

    for (let i = 0; i < steps; i++) {
      const g = sample.nz;
      
      // Countermeasure-informed effective G estimate with response lag.
      const positiveLoad = Math.max(0, g - 1);
      const protectionOffset =
        positiveLoad *
        (agsmEffectiveness * 0.34 + gSuitPressurePsi * 0.02 + seatTiltDegrees * 0.003 + pbgFactor * 0.16);
      const dehydrationPenalty = positiveLoad * dehydrationLevel * 0.08;

      const targetGeff = g - protectionOffset + dehydrationPenalty;
      const lagGain = dt / (responseTauSeconds + dt);
      effectiveGState += (targetGeff - effectiveGState) * lagGain;
      const geff = effectiveGState;

      // Perfusion model with positive-G suppression and limited negative-G augmentation.
      const geffPositiveLoad = Math.max(0, geff - 1);
      const geffNegativeLoad = Math.max(0, -geff);
      const perfusionRatio =
        1 - geffPositiveLoad * 0.16 + geffNegativeLoad * 0.04 - dehydrationLevel * 0.06;
      const cerebralFlow = baselineFlow * Math.max(0.18, perfusionRatio);

      // Update reserve banks
      if (geff >= greyoutGeff) {
        const geffExcess = geff - greyoutGeff;
        const protectionFactor = 1 - Math.min(0.6, agsmEffectiveness * 0.35 + gSuitPressurePsi * 0.03 + pbgFactor * 0.2);
        consciousnessBank -= dt * geffExcess * 0.55 * protectionFactor;
        blackoutBank -= dt * geffExcess * 0.35 * protectionFactor;
      } else {
        // Recovery when load drops below threshold.
        const recoveryRate = Math.max(0.16, 0.56 - dehydrationLevel * 0.22);
        consciousnessBank = Math.min(baseConsciousnessBank, consciousnessBank + dt * recoveryRate);
        blackoutBank = Math.min(baseBlackoutBank, blackoutBank + dt * recoveryRate * 0.66);
      }

      consciousnessBank = Math.max(0, consciousnessBank);
      blackoutBank = Math.max(0, blackoutBank);

      // Determine flags
      const isGreyout = geff >= greyoutGeff || cerebralFlow < baselineFlow * 0.64;
      const isBlackout = geff >= blackoutGeff || blackoutBank <= 0.2;
      const isGLOC = geff >= glocGeff || consciousnessBank <= 0.2;

      // Record event times
      if (isGreyout && greyoutTime === null) {
        greyoutTime = currentTime;
      }
      if (isBlackout && blackoutTime === null) {
        blackoutTime = currentTime;
      }
      if (isGLOC && glocTime === null) {
        glocTime = currentTime;
      }

      // HLAP estimate with seat-tilt and AGSM compensation.
      const hlap = baselineMAP + (g - 1) * (7.5 + seatTiltDegrees * 0.05) + agsmEffectiveness * 4;

      // Store values
      times_s.push(currentTime);
      g_values.push(g);
      geff_values.push(geff);
      flags_n2.push(isGLOC ? 1 : 0);
      flags_ne2.push(isGreyout ? 1 : 0);
      flags_non2.push(isBlackout ? 1 : 0);
      c_bank_values.push(consciousnessBank);
      bo_bank_values.push(blackoutBank);
      f_con_values.push(cerebralFlow);
      f_vis_values.push(cerebralFlow * 0.9);
      f_bo_values.push(cerebralFlow * 0.85);
      hlap_values.push(hlap);

      currentTime += dt;
    }
  }

  return {
    time_to_greyout_s: greyoutTime,
    time_to_blackout_s: blackoutTime,
    time_to_gloc_s: glocTime,
    times_s,
    g_values,
    geff_values,
    flags_n2,
    flags_ne2,
    flags_non2,
    c_bank_values,
    bo_bank_values,
    f_con_values,
    f_vis_values,
    f_bo_values,
    hlap_values,
  };
}

/**
 * Get all profile IDs
 */
export function getProfileIds(): string[] {
  return Object.keys(AEROBATIC_PROFILES);
}

/**
 * Get profile by ID
 */
export function getProfile(id: string): AerobaticProfile | undefined {
  return AEROBATIC_PROFILES[id];
}
