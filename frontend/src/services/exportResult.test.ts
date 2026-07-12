import { describe, expect, it, vi } from 'vitest';
import { buildBatchCsvExport, buildPredictionJsonExport, downloadExport, sanitizeExportFilename } from './exportResult';
import type { PredictionRequest, PredictionResponse } from './types';

const response: PredictionResponse = { targets: [{ target: 'x', censored: false, point: 1, lo: 0, hi: 2 }],
  ood: false, ood_score: 0.1, in_envelope: true, model_version: 'm1', cgem_binary_sha256: 'sha',
  resolved_maneuver: 'loop', maneuver_category: 'training', calibration_scope: 'global', source: 'surrogate' };
const request: PredictionRequest = { maneuver: { maneuver: 'loop' }, pilot: { who_profile: 2,
  g_tolerance_multiplier: 1, dehydration_level: 0, countermeasures_label: 'none', gsuit_max_psi: 0,
  gsuit_coverage_fraction: 0, agsm_effectiveness: 0, pbg_max_mmhg: 0 } };

describe('result exports', () => {
  it('builds deterministic provenance-complete JSON using caller timestamp', () => {
    const spec = buildPredictionJsonExport({ response, request, exportedAt: '2026-07-12T12:00:00.000Z' });
    expect(spec.mediaType).toBe('application/json');
    expect(spec.filename).toBe('cgem-loop-2026-07-12T12-00-00.000Z.json');
    expect(JSON.parse(spec.content)).toEqual({ exported_at: '2026-07-12T12:00:00.000Z', source: 'surrogate',
      maneuver: 'loop', maneuver_category: 'training', model_version: 'm1', cgem_binary_sha256: 'sha',
      calibration_scope: 'global', ood: false, in_envelope: true, ood_score: 0.1, input: request, targets: response.targets });
  });

  it('escapes RFC 4180 CSV and emits one row per target', () => {
    const csv = buildBatchCsvExport({ rows: [{ profileId: 'loop,"one"', prediction: response }],
      requestFor: () => request, exportedAt: '2026-07-12T12:00:00Z' });
    expect(csv.content).toContain('"loop,""one"""');
    expect(csv.content.split('\r\n')).toHaveLength(3);
    expect(csv.content).toContain('model_version');
    expect(csv.content).toContain('calibration_scope');
    expect(csv.content).toContain('input');
  });

  it('sanitizes filenames', () => expect(sanitizeExportFilename('../bad name?.json')).toBe('bad-name.json'));

  it('always revokes the object URL when a download click fails', () => {
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test');
    const revokeObjectURL = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    const anchor = document.createElement('a');
    vi.spyOn(anchor, 'click').mockImplementation(() => { throw new Error('blocked'); });
    vi.spyOn(document, 'createElement').mockReturnValueOnce(anchor);
    expect(() => downloadExport({ filename: 'result.json', mediaType: 'application/json', content: '{}' })).toThrow('blocked');
    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:test');
  });
});
