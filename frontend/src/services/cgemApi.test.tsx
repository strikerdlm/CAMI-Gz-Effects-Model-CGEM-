import type { PropsWithChildren } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cgemHttp, useHealth } from './cgemApi';
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
});
