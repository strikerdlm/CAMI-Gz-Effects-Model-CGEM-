import type { Page, Route } from '@playwright/test';

const TARGETS = [
  'time_to_greyout_s',
  'time_to_blackout_s',
  'time_to_gloc_s',
  'hlap_min',
  'c_bank_min',
] as const;

const binarySha = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';

const target = (name: (typeof TARGETS)[number], index: number) => ({
  target: name,
  censored: name.startsWith('time_to_'),
  point: name.startsWith('time_to_') ? 12 + index : name === 'hlap_min' ? 42 : 1.2,
  lo: name.startsWith('time_to_') ? 10 + index : name === 'hlap_min' ? 38 : 0.9,
  hi: name.startsWith('time_to_') ? 15 + index : name === 'hlap_min' ? 47 : 1.5,
  event_probability: name.startsWith('time_to_') ? 0.2 + index * 0.1 : null,
  expected_time_s: name.startsWith('time_to_') ? (12 + index) * (0.2 + index * 0.1) : null,
});

function prediction(maneuver = 'hammerhead', index = 0) {
  return {
    targets: TARGETS.map(target),
    ood: index % 3 === 1,
    ood_score: index % 3 === 1 ? 2.4 : 0.35,
    in_envelope: index % 3 !== 1,
    model_version: 'phase1-e2e-model',
    cgem_binary_sha256: binarySha,
    source: 'surrogate',
    resolved_maneuver: maneuver,
    maneuver_category: maneuver.includes('turn') ? 'operational_training' : 'aerobatic',
    calibration_scope: 'category',
  };
}

const authoritative = {
  maneuver: 'hammerhead',
  pilot_profile: 'who_profile_2',
  duration_s: 4,
  time_to_greyout_s: 2.5,
  time_to_blackout_s: null,
  time_to_gloc_s: null,
  data: {
    'Time(s)': [0, 1, 2, 3, 4],
    G: [1, 3, 6, 3, 1],
    G_eff: [1, 2.7, 5.2, 2.9, 1.1],
    'HLAP(mmHg)': [90, 75, 55, 68, 85],
    'F_con(dl/min)': [7.2, 6.8, 5.8, 6.4, 7],
    'F_vis(dl/min)': [4.1, 3.8, 2.9, 3.5, 4],
    'F_bo(dl/min)': [9.5, 8.9, 7.4, 8.3, 9.2],
    'c_bank(s)': [1.4, 1.2, 0.8, 1, 1.3],
    'bo_bank(s)': [2.2, 2, 1.4, 1.8, 2.1],
    Conscious: [1, 1, 1, 1, 1],
    Greyout: [0, 0, 1, 0, 0],
    Blackout: [0, 0, 0, 0, 0],
  },
};

async function json(route: Route, body: unknown) {
  await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
}

export async function installApiFixtures(page: Page): Promise<void> {
  await page.route('**/healthz', (route) => json(route, { status: 'ok', detail: 'Phase 1 browser fixture' }));
  await page.route('**/version', (route) => json(route, {
    package_version: '2.2.0-e2e',
    cgem_binary_sha256: binarySha,
    dataset_name: 'phase1-browser-fixture',
    dataset_master_seed: 20260712,
    targets: [...TARGETS],
  }));
  await page.route('**/predict', async (route) => {
    const request = route.request().postDataJSON() as { maneuver?: { maneuver?: string } };
    await json(route, prediction(request.maneuver?.maneuver));
  });
  await page.route('**/run-cgem', async (route) => {
    const request = route.request().postDataJSON() as { maneuver?: string };
    await json(route, { ...authoritative, maneuver: request.maneuver ?? authoritative.maneuver });
  });
  await page.route('**/sweep', async (route) => {
    const request = route.request().postDataJSON() as { inputs?: Array<{ maneuver?: { maneuver?: string } }> };
    await json(route, { results: (request.inputs ?? []).map((input, index) => prediction(input.maneuver?.maneuver, index)) });
  });
  await page.route('**/sensitivity/*', async (route) => {
    const targetName = decodeURIComponent(new URL(route.request().url()).pathname.split('/').pop() ?? 'time_to_gloc_s');
    await json(route, {
      target: targetName,
      censored: targetName.startsWith('time_to_'),
      fixed_who_profile: 'custom arm',
      sobol_n_base: 1024,
      indices: [
        { feature: 'g_peak_abs', S1: 0.42, S1_conf: 0.03, ST: 0.58, ST_conf: 0.04 },
        { feature: 'agsm_effectiveness', S1: 0.21, S1_conf: 0.02, ST: 0.31, ST_conf: 0.03 },
      ],
    });
  });
}
