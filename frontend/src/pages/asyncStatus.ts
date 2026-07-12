interface MutationStatus {
  isPending?: boolean;
  isSuccess?: boolean;
  isError?: boolean;
}

export function predictionRunAnnouncement(
  kind: 'surrogate' | 'authoritative',
  status: MutationStatus,
): string {
  const label = kind === 'surrogate' ? 'Surrogate prediction' : 'Authoritative CGEM run';
  if (status.isPending) return kind === 'surrogate' ? 'Running surrogate prediction.' : 'Running authoritative CGEM.';
  if (status.isError) return `${label} failed.`;
  if (status.isSuccess) return `${label} complete.`;
  return '';
}

export function batchSweepAnnouncement(status: MutationStatus): string {
  if (status.isPending) return 'Running batch sweep.';
  if (status.isError) return 'Batch sweep failed.';
  if (status.isSuccess) return 'Batch sweep complete.';
  return '';
}
