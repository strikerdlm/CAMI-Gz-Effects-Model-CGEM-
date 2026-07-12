import type { PropsWithChildren } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { UseMutationResult } from '@tanstack/react-query';
import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cgemHttp, useHealth, usePredict, useRunCgem, useSweep } from './cgemApi';
import { DEFAULT_PREFS, updateUserPrefs } from '../state/useUserPrefs';

afterEach(() => {
  updateUserPrefs({ apiUrl: DEFAULT_PREFS.apiUrl });
  vi.restoreAllMocks();
});

describe('reactive API scoping', () => {
  it('refetches under a new cache scope when the preferred API URL changes', async () => {
    const get = vi.spyOn(cgemHttp, 'get').mockResolvedValue({ data: { status: 'ok' } });
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: PropsWithChildren) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );

    updateUserPrefs({ apiUrl: 'http://a' });
    renderHook(() => useHealth(), { wrapper });
    await waitFor(() => expect(get).toHaveBeenCalledWith('/healthz', { baseURL: 'http://a' }));

    act(() => updateUserPrefs({ apiUrl: 'http://b' }));
    await waitFor(() => expect(get).toHaveBeenCalledWith('/healthz', { baseURL: 'http://b' }));
    expect(client.getQueryData(['cgem', 'http://a', 'health'])).toEqual({ status: 'ok' });
    expect(client.getQueryData(['cgem', 'http://b', 'health'])).toEqual({ status: 'ok' });
  });

  const mutationCases = [
    {
      name: 'predict', hook: usePredict,
      request: { maneuver: { maneuver: 'demo' }, pilot: {} },
      a: { source: 'a' }, b: { source: 'b' },
    },
    {
      name: 'sweep', hook: useSweep, request: { inputs: [] },
      a: { results: [{ source: 'a' }] }, b: { results: [{ source: 'b' }] },
    },
    {
      name: 'run-cgem', hook: useRunCgem,
      request: { maneuver: 'demo', pilot: {} },
      a: { maneuver: 'a' }, b: { maneuver: 'b' },
    },
  ] as const;

  it.each(mutationCases)(
    'detaches a stale $name result when the API URL changes',
    async ({ hook, request, a, b }) => {
      let resolveA!: (value: { data: unknown }) => void;
      let resolveB!: (value: { data: unknown }) => void;
      const responseA = new Promise<{ data: unknown }>((resolve) => {
        resolveA = resolve;
      });
      const responseB = new Promise<{ data: unknown }>((resolve) => {
        resolveB = resolve;
      });
      const post = vi.spyOn(cgemHttp, 'post')
        .mockImplementationOnce(() => responseA)
        .mockImplementationOnce(() => responseB);
      const client = new QueryClient();
      const wrapper = ({ children }: PropsWithChildren) => (
        <QueryClientProvider client={client}>{children}</QueryClientProvider>
      );
      updateUserPrefs({ apiUrl: 'http://a' });
      const { result } = renderHook(
        () => hook() as UseMutationResult<unknown, Error, unknown>,
        { wrapper },
      );

      let oldRequest!: Promise<unknown>;
      act(() => {
        oldRequest = result.current.mutateAsync(request);
      });
      await waitFor(() => expect(post).toHaveBeenCalledTimes(1));
      act(() => updateUserPrefs({ apiUrl: 'http://b' }));
      await act(async () => {
        resolveA({ data: a });
        await oldRequest;
      });
      expect(result.current.data).toBeUndefined();
      expect(result.current.isSuccess).toBe(false);

      let newRequest!: Promise<unknown>;
      act(() => {
        newRequest = result.current.mutateAsync(request);
      });
      await waitFor(() => expect(post).toHaveBeenCalledTimes(2));
      await act(async () => {
        resolveB({ data: b });
        await newRequest;
      });
      await waitFor(() => expect(result.current.data).toEqual(b));
      expect(result.current.isSuccess).toBe(true);
    },
  );
});
