import type { TargetName } from './types';

export const queryKeys = {
  health: (url: string) => ['cgem', url, 'health'] as const,
  version: (url: string) => ['cgem', url, 'version'] as const,
  sensitivity: (url: string, target: TargetName | null) =>
    ['cgem', url, 'sensitivity', target] as const,
  predict: (url: string) => ['cgem', url, 'predict'] as const,
  sweep: (url: string) => ['cgem', url, 'sweep'] as const,
  run: (url: string) => ['cgem', url, 'run-cgem'] as const,
};
