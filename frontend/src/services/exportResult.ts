import type { CGEMRunResponse, PilotConfigRequest, PredictionRequest, PredictionResponse, VersionResponse } from './types';
export interface ExportSpec { filename: string; mediaType: 'application/json' | 'text/csv'; content: string }
export function sanitizeExportFilename(filename: string): string { return filename.split(/[\\/]/).pop()!.replace(/\s+/g, '-').replace(/[^a-zA-Z0-9._-]/g, ''); }
const stampForName = (timestamp: string) => timestamp.replace(/:/g, '-');
const jsonSpec = (maneuver: string, exportedAt: string, value: unknown): ExportSpec => ({ filename: sanitizeExportFilename(`cgem-${maneuver}-${stampForName(exportedAt)}.json`), mediaType: 'application/json', content: `${JSON.stringify(value, null, 2)}\n` });
export function buildPredictionJsonExport({ response, request, exportedAt }: { response: PredictionResponse; request: PredictionRequest; exportedAt: string }): ExportSpec {
  return jsonSpec(response.resolved_maneuver, exportedAt, { exported_at: exportedAt, source: response.source, maneuver: response.resolved_maneuver, maneuver_category: response.maneuver_category, model_version: response.model_version, cgem_binary_sha256: response.cgem_binary_sha256, calibration_scope: response.calibration_scope, ood: response.ood, in_envelope: response.in_envelope, ood_score: response.ood_score, input: request, targets: response.targets });
}
export function buildAuthoritativeJsonExport({ run, request, version, exportedAt }: { run: CGEMRunResponse; request: { maneuver: string; pilot: PilotConfigRequest }; version?: VersionResponse; exportedAt: string }): ExportSpec {
  return jsonSpec(run.maneuver, exportedAt, { exported_at: exportedAt, source: 'Fortran / authoritative CGEM', maneuver: run.maneuver, pilot_profile: run.pilot_profile, package_version: version?.package_version, cgem_binary_sha256: version?.cgem_binary_sha256, input: request, result: run, limitation: 'Research use only; not an operational flight-safety system' });
}
const csvCell = (value: unknown): string => { const text = value == null ? '' : typeof value === 'string' ? value : JSON.stringify(value); return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text; };
export function buildBatchCsvExport(args: { rows: Array<{ profileId: string; prediction: PredictionResponse }>; requestFor: (profileId: string) => PredictionRequest; exportedAt: string }): ExportSpec {
  const headers = ['exported_at','source','maneuver','maneuver_category','model_version','cgem_binary_sha256','calibration_scope','ood','in_envelope','ood_score','input','target','censored','point','lo','hi','event_probability','expected_time_s'];
  const records = args.rows.flatMap(({ profileId, prediction }) => prediction.targets.map((target) => [args.exportedAt, prediction.source, profileId, prediction.maneuver_category, prediction.model_version, prediction.cgem_binary_sha256, prediction.calibration_scope, prediction.ood, prediction.in_envelope, prediction.ood_score, args.requestFor(profileId), target.target, target.censored, target.point, target.lo, target.hi, target.event_probability, target.expected_time_s]));
  return { filename: sanitizeExportFilename(`cgem-batch-${stampForName(args.exportedAt)}.csv`), mediaType: 'text/csv', content: [headers, ...records].map((row) => row.map(csvCell).join(',')).join('\r\n') + '\r\n' };
}
export function downloadExport(spec: ExportSpec, documentRef: Document = document): void {
  const objectUrl = URL.createObjectURL(new Blob([spec.content], { type: spec.mediaType }));
  try { const anchor = documentRef.createElement('a'); anchor.href = objectUrl; anchor.download = sanitizeExportFilename(spec.filename); anchor.style.display = 'none'; documentRef.body.appendChild(anchor); anchor.click(); anchor.remove(); } finally { URL.revokeObjectURL(objectUrl); }
}
