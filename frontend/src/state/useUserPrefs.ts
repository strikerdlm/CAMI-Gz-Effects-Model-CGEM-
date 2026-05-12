/**
 * Tiny localStorage-backed preference store.
 * Why not Zustand: this is a 6-field config, no need for a library.
 * Why useSyncExternalStore: React 18+ recommendation for external stores;
 * gives us cross-component reactivity without context plumbing.
 */
import { useSyncExternalStore } from 'react';

export interface UserPrefs {
  apiUrl: string;
  phosphorColor: 'amber' | 'green';
  units: 'G' | 'm_per_s2';
  defaults: {
    who_profile: number;
    gsuit_max_psi: number;
    gsuit_coverage_fraction: number;
    agsm_effectiveness: number;
    pbg_max_mmhg: number;
    dehydration_level: number;
  };
}

export const PREFS_STORAGE_KEY = 'cgem.prefs.v1';

const ENV_URL: string | undefined = (() => {
  try {
    return (import.meta as unknown as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL;
  } catch {
    return undefined;
  }
})();

export const DEFAULT_PREFS: UserPrefs = {
  apiUrl: ENV_URL ?? 'http://localhost:8000',
  phosphorColor: 'amber',
  units: 'G',
  defaults: {
    who_profile: 4,
    gsuit_max_psi: 5,
    gsuit_coverage_fraction: 0.6,
    agsm_effectiveness: 0.5,
    pbg_max_mmhg: 0,
    dehydration_level: 0,
  },
};

function readFromStorage(): UserPrefs {
  if (typeof localStorage === 'undefined') return DEFAULT_PREFS;
  try {
    const raw = localStorage.getItem(PREFS_STORAGE_KEY);
    if (!raw) return DEFAULT_PREFS;
    const parsed = JSON.parse(raw) as Partial<UserPrefs>;
    return {
      ...DEFAULT_PREFS,
      ...parsed,
      defaults: { ...DEFAULT_PREFS.defaults, ...(parsed.defaults ?? {}) },
    };
  } catch {
    return DEFAULT_PREFS;
  }
}

let current: UserPrefs = readFromStorage();
const listeners = new Set<() => void>();

function subscribe(cb: () => void): () => void {
  listeners.add(cb);
  return () => { listeners.delete(cb); };
}

function getSnapshot(): UserPrefs {
  return current;
}

export function updateUserPrefs(patch: Partial<UserPrefs>): void {
  current = {
    ...current,
    ...patch,
    defaults: { ...current.defaults, ...(patch.defaults ?? {}) },
  };
  try {
    localStorage.setItem(PREFS_STORAGE_KEY, JSON.stringify(current));
  } catch {
    // Ignore quota / privacy-mode errors; in-memory copy still works.
  }
  listeners.forEach((cb) => cb());
}

export function useUserPrefs(): UserPrefs {
  return useSyncExternalStore(subscribe, getSnapshot, () => DEFAULT_PREFS);
}

/** Synchronous read for non-React code (e.g. axios interceptor). */
export function readUserPrefs(): UserPrefs {
  return current;
}

// Cross-tab sync
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === PREFS_STORAGE_KEY) {
      current = readFromStorage();
      listeners.forEach((cb) => cb());
    }
  });
}
