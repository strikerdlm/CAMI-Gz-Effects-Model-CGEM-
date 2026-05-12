/**
 * Build-time maneuver catalog: 72 aerobatic / military / extreme post-stall
 * profiles joined with maneuvers_catalog.CATALOG metadata.
 *
 * Source of truth: `scripts/export_maneuvers_json.py` (run automatically
 * via the frontend `prebuild` hook).
 */
import raw from './maneuvers.json';

export type ManeuverCategory =
  | 'championship'
  | 'military_acm'
  | 'extreme_post_stall'
  | 'training'
  | 'conceptual';

export interface ManeuverSample {
  nz: number;
  duration_ms: number;
}

export interface Maneuver {
  id: string;
  filename: string;
  category: ManeuverCategory;
  description: string;
  aircraft: string;
  peak_pos_gz: number;
  peak_neg_gz: number;
  onset_rate_g_per_s: number;
  total_duration_s: number;
  aresti_family: number | null;
  aresti_code: string | null;
  sustained_gz: number | null;
  sustained_duration_s: number | null;
  hemodynamic_concern: string;
  source: string;
  tags: string[];
  samples: ManeuverSample[];
}

export const MANEUVERS: Maneuver[] = raw as Maneuver[];

export const MANEUVERS_BY_ID: Record<string, Maneuver> = Object.fromEntries(
  MANEUVERS.map((m) => [m.id, m]),
);

const CATEGORY_ORDER: ManeuverCategory[] = [
  'championship',
  'military_acm',
  'extreme_post_stall',
  'training',
  'conceptual',
];

export const MANEUVERS_BY_CATEGORY: Record<ManeuverCategory, Maneuver[]> = (() => {
  const out: Record<ManeuverCategory, Maneuver[]> = {
    championship: [],
    military_acm: [],
    extreme_post_stall: [],
    training: [],
    conceptual: [],
  };
  for (const m of MANEUVERS) out[m.category].push(m);
  // Sort within each category by peak +Gz (descending) for picker readability.
  for (const cat of CATEGORY_ORDER) {
    out[cat].sort((a, b) => b.peak_pos_gz - a.peak_pos_gz);
  }
  return out;
})();

export const ORDERED_CATEGORIES = CATEGORY_ORDER;

/** Cumulative flight time in seconds, one entry per sample. */
export function flightTimeSeconds(m: Maneuver): number[] {
  let t = 0;
  return m.samples.map((s) => {
    t += s.duration_ms / 1000;
    return t;
  });
}
