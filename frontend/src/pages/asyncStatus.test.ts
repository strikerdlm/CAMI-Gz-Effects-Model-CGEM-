import { describe, expect, it } from 'vitest';
import { batchSweepAnnouncement, predictionRunAnnouncement } from './asyncStatus';

describe('stable async status announcements', () => {
  it('announces prediction pending, success, and error states', () => {
    expect(predictionRunAnnouncement('surrogate', { isPending: true })).toBe('Running surrogate prediction.');
    expect(predictionRunAnnouncement('authoritative', { isSuccess: true })).toBe('Authoritative CGEM run complete.');
    expect(predictionRunAnnouncement('surrogate', { isError: true })).toBe('Surrogate prediction failed.');
  });

  it('announces batch sweep pending, success, and error states', () => {
    expect(batchSweepAnnouncement({ isPending: true })).toBe('Running batch sweep.');
    expect(batchSweepAnnouncement({ isSuccess: true })).toBe('Batch sweep complete.');
    expect(batchSweepAnnouncement({ isError: true })).toBe('Batch sweep failed.');
  });

  it('keeps the live region present but quiet before a run', () => {
    expect(predictionRunAnnouncement('surrogate', {})).toBe('');
    expect(batchSweepAnnouncement({})).toBe('');
  });
});
