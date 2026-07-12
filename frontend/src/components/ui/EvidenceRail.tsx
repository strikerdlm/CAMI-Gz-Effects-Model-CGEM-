import type { CGEMRunResponse, PredictionResponse, VersionResponse } from '../../services/types';
import { useId } from 'react';

export type Evidence =
  | { kind: 'surrogate'; response: PredictionResponse }
  | { kind: 'authoritative'; run: CGEMRunResponse; version?: VersionResponse };

export function EvidenceRail({ evidence }: { evidence: Evidence }) {
  const summaryId = useId();
  const fields: Array<[string, string]> = evidence.kind === 'surrogate'
    ? [['Source', 'Surrogate'], ['Maneuver', evidence.response.resolved_maneuver], ['Category', evidence.response.maneuver_category], ['Calibration scope', evidence.response.calibration_scope === 'global' ? 'Global' : 'Category'], ['Envelope', evidence.response.ood ? 'Outside training envelope (OOD)' : 'Inside training envelope'], ['Model version', evidence.response.model_version], ['CGEM binary SHA', evidence.response.cgem_binary_sha256 ? `${evidence.response.cgem_binary_sha256.slice(0, 8)}…` : '']]
    : [['Source', 'Fortran / authoritative CGEM'], ['Maneuver', evidence.run.maneuver], ['Pilot profile', evidence.run.pilot_profile], ['Package version', evidence.version?.package_version ?? ''], ['CGEM binary SHA', evidence.version?.cgem_binary_sha256 ? `${evidence.version.cgem_binary_sha256.slice(0, 8)}…` : ''], ['Limitation', 'Research use only; not an operational flight-safety system']];
  const summary = evidence.kind === 'surrogate'
    ? `Surrogate result for ${evidence.response.resolved_maneuver}; ${evidence.response.ood ? 'outside the training envelope' : 'inside the training envelope'}; ${evidence.response.calibration_scope} calibration scope.`
    : `Authoritative Fortran CGEM result for ${evidence.run.maneuver}, pilot profile ${evidence.run.pilot_profile}; research use only.`;
  return <aside aria-label="Result evidence" aria-describedby={summaryId} className="instrument-panel rounded-xl border border-hud-line p-4">
    <p id={summaryId} className="sr-only">{summary}</p>
    <h3 className="mb-3 font-condensed text-sm uppercase tracking-callsign text-hud-ink">Result evidence</h3>
    <dl className="grid gap-2 text-xs sm:grid-cols-2 lg:grid-cols-3">{fields.filter(([, value]) => value).map(([label, value]) => <div key={label}><dt className="font-mono text-hud-ink-faint">{label}</dt><dd className="mt-0.5 text-hud-ink">{value}</dd></div>)}</dl>
  </aside>;
}
