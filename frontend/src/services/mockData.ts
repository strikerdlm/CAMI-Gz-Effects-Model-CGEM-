/**
 * Mock Data Service
 * 
 * Provides static aerobatic profile data and simulated CGEM results
 * for frontend development and demonstration purposes.
 */

import type { 
  Sample, 
  AerobaticProfile, 
  CGEMResult,
  PilotConfig 
} from '../types';

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
  _config: PilotConfig
): CGEMResult {
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

  // Simulation parameters (based on CGEM model thresholds)
  const baselineFlow = 49.5; // dl/min - normal cerebral blood flow
  const greyoutGeff = 4.1;   // G_eff threshold for greyout onset
  const blackoutGeff = 5.0;  // G_eff threshold for blackout
  const glocGeff = 5.5;      // G_eff threshold for G-LOC

  let currentTime = 0;
  let consciousnessBank = 7.1; // seconds
  let blackoutBank = 5.0;

  let greyoutTime: number | null = null;
  let blackoutTime: number | null = null;
  let glocTime: number | null = null;

  // Process each sample at 10ms resolution
  for (const sample of profile.samples) {
    const steps = Math.max(1, Math.floor(sample.duration_ms / 10));
    const dt = sample.duration_ms / steps / 1000; // seconds per step

    for (let i = 0; i < steps; i++) {
      const g = sample.nz;
      
      // Simplified G_eff calculation (real CGEM is more complex)
      // G_eff accounts for cardiovascular response lag
      const geff = g > 1 ? g * 0.95 : g;

      // Simplified flow calculation
      const flowFactor = Math.max(0, 1 - (geff - 1) * 0.15);
      const cerebralFlow = baselineFlow * flowFactor;

      // Update reserve banks
      if (geff >= greyoutGeff) {
        consciousnessBank -= dt * (geff - greyoutGeff) * 0.5;
        blackoutBank -= dt * (geff - greyoutGeff) * 0.3;
      } else {
        // Recovery
        consciousnessBank = Math.min(7.1, consciousnessBank + dt * 0.5);
        blackoutBank = Math.min(5.0, blackoutBank + dt * 0.3);
      }

      consciousnessBank = Math.max(0, consciousnessBank);
      blackoutBank = Math.max(0, blackoutBank);

      // Determine flags
      const isGreyout = geff >= greyoutGeff && cerebralFlow < baselineFlow * 0.7;
      const isBlackout = geff >= blackoutGeff || blackoutBank <= 0;
      const isGLOC = geff >= glocGeff || consciousnessBank <= 0;

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

      // HLAP calculation (simplified)
      const baselineMAP = 93; // mmHg
      const hlap = baselineMAP + (g - 1) * 8;

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
