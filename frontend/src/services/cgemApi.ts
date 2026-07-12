/**
 * Typed axios client + React Query hooks for the FastAPI service.
 *
 * Base URL configurable via VITE_API_URL (default
 * http://localhost:8000). Each hook wraps a queryKey / mutationFn pair
 * so cached responses remain consistent across pages.
 */

import axios, { type AxiosError } from 'axios';
import {
  useMutation,
  useQuery,
  type UseMutationResult,
  type UseQueryResult,
} from '@tanstack/react-query';
import type {
  HealthResponse,
  PredictionRequest,
  PredictionResponse,
  RunCGEMRequest,
  CGEMRunResponse,
  SensitivityResponse,
  SweepRequest,
  SweepResponse,
  VersionResponse,
  TargetName,
} from './types';
import { useUserPrefs } from '../state/useUserPrefs';
import { queryKeys } from './queryKeys';

// ── HTTP client ──────────────────────────────────────────────────────
// Hooks capture the reactive preference URL and pass it explicitly so a
// request cannot silently switch backend while it is in flight.

export const cgemHttp = axios.create({
  timeout: 60_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export type ApiError = AxiosError<{ detail?: string }>;

// ── Raw client functions ─────────────────────────────────────────────

export async function getHealth(apiBaseUrl: string): Promise<HealthResponse> {
  const { data } = await cgemHttp.get<HealthResponse>('/healthz', { baseURL: apiBaseUrl });
  return data;
}

export async function getVersion(apiBaseUrl: string): Promise<VersionResponse> {
  const { data } = await cgemHttp.get<VersionResponse>('/version', { baseURL: apiBaseUrl });
  return data;
}

export async function getSensitivity(
  apiBaseUrl: string,
  target: TargetName,
): Promise<SensitivityResponse> {
  const { data } = await cgemHttp.get<SensitivityResponse>(`/sensitivity/${target}`, {
    baseURL: apiBaseUrl,
  });
  return data;
}

export async function postPredict(
  apiBaseUrl: string,
  req: PredictionRequest,
): Promise<PredictionResponse> {
  const { data } = await cgemHttp.post<PredictionResponse>('/predict', req, { baseURL: apiBaseUrl });
  return data;
}

export async function postSweep(apiBaseUrl: string, req: SweepRequest): Promise<SweepResponse> {
  const { data } = await cgemHttp.post<SweepResponse>('/sweep', req, { baseURL: apiBaseUrl });
  return data;
}

export async function postRunCgem(apiBaseUrl: string, req: RunCGEMRequest): Promise<CGEMRunResponse> {
  const { data } = await cgemHttp.post<CGEMRunResponse>('/run-cgem', req, { baseURL: apiBaseUrl });
  return data;
}

// ── React Query hooks ────────────────────────────────────────────────

export function useHealth(): UseQueryResult<HealthResponse, ApiError> {
  const { apiUrl } = useUserPrefs();
  return useQuery({
    queryKey: queryKeys.health(apiUrl),
    queryFn: () => getHealth(apiUrl),
    staleTime: 30_000,
  });
}

export function useVersion(): UseQueryResult<VersionResponse, ApiError> {
  const { apiUrl } = useUserPrefs();
  return useQuery({
    queryKey: queryKeys.version(apiUrl),
    queryFn: () => getVersion(apiUrl),
  });
}

export function useSensitivity(
  target: TargetName | null,
): UseQueryResult<SensitivityResponse, ApiError> {
  const { apiUrl } = useUserPrefs();
  return useQuery({
    queryKey: queryKeys.sensitivity(apiUrl, target),
    queryFn: () => getSensitivity(apiUrl, target as TargetName),
    enabled: target !== null,
  });
}

/** One-shot prediction. Returns a mutation so the caller controls when
 *  the request fires (matches the form-submission UX of PredictionPage). */
export function usePredict(): UseMutationResult<
  PredictionResponse,
  ApiError,
  PredictionRequest
> {
  const { apiUrl } = useUserPrefs();
  return useMutation({
    mutationKey: queryKeys.predict(apiUrl),
    mutationFn: (request) => postPredict(apiUrl, request),
    retry: false,
  });
}

export function useSweep(): UseMutationResult<SweepResponse, ApiError, SweepRequest> {
  const { apiUrl } = useUserPrefs();
  return useMutation({
    mutationKey: queryKeys.sweep(apiUrl),
    mutationFn: (request) => postSweep(apiUrl, request),
    retry: false,
  });
}

export function useRunCgem(): UseMutationResult<
  CGEMRunResponse,
  ApiError,
  RunCGEMRequest
> {
  const { apiUrl } = useUserPrefs();
  return useMutation({
    mutationKey: queryKeys.run(apiUrl),
    mutationFn: (request) => postRunCgem(apiUrl, request),
    retry: false,
  });
}

/** Helper: render the `detail` error message from a FastAPI 4xx/5xx. */
export function apiErrorMessage(err: unknown): string {
  if (!err) return 'Unknown error';
  if (typeof err === 'object' && err !== null) {
    const e = err as ApiError;
    if (e.response?.data?.detail) return e.response.data.detail;
    if (e.message) return e.message;
  }
  return String(err);
}
