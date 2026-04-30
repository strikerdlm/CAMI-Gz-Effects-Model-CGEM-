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

// ── HTTP client ──────────────────────────────────────────────────────

const baseURL =
  (import.meta as unknown as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ??
  'http://localhost:8000';

export const cgemHttp = axios.create({
  baseURL,
  timeout: 60_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export type ApiError = AxiosError<{ detail?: string }>;

// ── Raw client functions ─────────────────────────────────────────────

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await cgemHttp.get<HealthResponse>('/healthz');
  return data;
}

export async function getVersion(): Promise<VersionResponse> {
  const { data } = await cgemHttp.get<VersionResponse>('/version');
  return data;
}

export async function getSensitivity(target: TargetName): Promise<SensitivityResponse> {
  const { data } = await cgemHttp.get<SensitivityResponse>(`/sensitivity/${target}`);
  return data;
}

export async function postPredict(req: PredictionRequest): Promise<PredictionResponse> {
  const { data } = await cgemHttp.post<PredictionResponse>('/predict', req);
  return data;
}

export async function postSweep(req: SweepRequest): Promise<SweepResponse> {
  const { data } = await cgemHttp.post<SweepResponse>('/sweep', req);
  return data;
}

export async function postRunCgem(req: RunCGEMRequest): Promise<CGEMRunResponse> {
  const { data } = await cgemHttp.post<CGEMRunResponse>('/run-cgem', req);
  return data;
}

// ── React Query hooks ────────────────────────────────────────────────

export function useHealth(): UseQueryResult<HealthResponse, ApiError> {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    staleTime: 30_000,
  });
}

export function useVersion(): UseQueryResult<VersionResponse, ApiError> {
  return useQuery({
    queryKey: ['version'],
    queryFn: getVersion,
  });
}

export function useSensitivity(
  target: TargetName | null,
): UseQueryResult<SensitivityResponse, ApiError> {
  return useQuery({
    queryKey: ['sensitivity', target],
    queryFn: () => getSensitivity(target as TargetName),
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
  return useMutation({
    mutationFn: postPredict,
    retry: false,
  });
}

export function useSweep(): UseMutationResult<SweepResponse, ApiError, SweepRequest> {
  return useMutation({
    mutationFn: postSweep,
    retry: false,
  });
}

export function useRunCgem(): UseMutationResult<
  CGEMRunResponse,
  ApiError,
  RunCGEMRequest
> {
  return useMutation({
    mutationFn: postRunCgem,
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

export { baseURL as cgemApiBaseURL };
