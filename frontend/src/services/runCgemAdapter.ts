/**
 * Adapter: convert the API's `CGEMRunResponse.data` shape (with
 * Fortran-friendly keys like "Time(s)", "HLAP(mmHg)") into the legacy
 * `CGEMResult` shape that the chart components consume.
 *
 * This is the only place that bridges the two; touch carefully — it is
 * the contract between the validated /run-cgem JSON and every chart on
 * DashboardPage.
 */
import type { CGEMRunResponse } from './types';
import type { CGEMResult } from '../types';

export function adaptCgemRun(resp: CGEMRunResponse): CGEMResult {
  const d = resp.data;
  // The API's Conscious/Greyout/Blackout arrays are 1 when the state is
  // active (conscious=1 means conscious). Frontend flags treat 1 as the
  // *impaired* state — so we invert Conscious and copy Greyout/Blackout.
  const conscious = d.Conscious ?? [];
  const greyout = d.Greyout ?? [];
  const blackout = d.Blackout ?? [];
  return {
    time_to_greyout_s: resp.time_to_greyout_s,
    time_to_blackout_s: resp.time_to_blackout_s,
    time_to_gloc_s: resp.time_to_gloc_s,
    times_s: d['Time(s)'] ?? [],
    g_values: d.G ?? [],
    geff_values: d.G_eff ?? [],
    flags_n2: conscious.map((c) => (c > 0.5 ? 0 : 1)),
    flags_ne2: greyout.map((v) => (v > 0.5 ? 1 : 0)),
    flags_non2: blackout.map((v) => (v > 0.5 ? 1 : 0)),
    c_bank_values: d['c_bank(s)'] ?? [],
    bo_bank_values: d['bo_bank(s)'] ?? [],
    f_con_values: d['F_con(dl/min)'] ?? [],
    f_vis_values: d['F_vis(dl/min)'] ?? [],
    f_bo_values: d['F_bo(dl/min)'] ?? [],
    hlap_values: d['HLAP(mmHg)'] ?? [],
  };
}
