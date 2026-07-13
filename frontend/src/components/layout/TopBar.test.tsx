import { useEffect } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import { TopBar } from './TopBar';
import { ResultActionsProvider, useResultActions } from '../ui/ResultActions';
import type { ExportSpec } from '../../services/exportResult';

const api = vi.hoisted(() => ({ refetchHealth: vi.fn(), refetchVersion: vi.fn(), fetching: false }));
const exportsApi = vi.hoisted(() => ({ download: vi.fn() }));
vi.mock('../../services/exportResult', () => ({ downloadExport: exportsApi.download }));
vi.mock('../../services/cgemApi', () => ({
  useHealth: () => ({ data: { status: 'ok' }, isPending: false, isFetching: api.fetching, refetch: api.refetchHealth }),
  useVersion: () => ({ data: { package_version: '1.0' }, isFetching: api.fetching, refetch: api.refetchVersion }),
}));

function renderTopBar(path = '/simulator') {
  return render(<MemoryRouter initialEntries={[path]}><TopBar onOpenNavigation={vi.fn()} navigationTriggerRef={{ current: null }} sidebarCollapsed={false} reduceMotion={false} /></MemoryRouter>);
}
const spec: ExportSpec = { filename: 'result.json', mediaType: 'application/json', content: '{}' };
function RegisterExport({ value }: { value: ExportSpec | null }) { const { registerExport } = useResultActions(); useEffect(() => { const unregister = registerExport(value); return typeof unregister === 'function' ? unregister : undefined; }, [value, registerExport]); return null; }
function renderTopBarWithExport(value: ExportSpec | null) {
  return render(<MemoryRouter><ResultActionsProvider><RegisterExport value={value} /><TopBar onOpenNavigation={vi.fn()} navigationTriggerRef={{ current: null }} sidebarCollapsed={false} reduceMotion={false} /></ResultActionsProvider></MemoryRouter>);
}

describe('TopBar actions', () => {
  it('removes notifications and routes Help to the current contextual hash', () => {
    renderTopBar('/simulator');
    expect(screen.queryByTitle('Notifications')).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Help' })).toHaveAttribute('href', '/about#simulator');
  });

  it('refreshes both status sources and announces completion', async () => {
    const user = userEvent.setup();
    api.refetchHealth.mockResolvedValue({});
    api.refetchVersion.mockResolvedValue({});
    renderTopBar();
    await user.click(screen.getByRole('button', { name: 'Refresh API status' }));
    expect(api.refetchHealth).toHaveBeenCalled();
    expect(api.refetchVersion).toHaveBeenCalled();
    expect(await screen.findByRole('status')).toHaveTextContent('API status refreshed');
  });

  it('announces a query error returned by a realistic refetch', async () => {
    const user = userEvent.setup();
    api.refetchHealth.mockImplementation(async (options?: { throwOnError?: boolean }) => {
      if (options?.throwOnError) throw new Error('offline');
      return { error: new Error('offline') };
    });
    api.refetchVersion.mockResolvedValue({});
    renderTopBar();

    await user.click(screen.getByRole('button', { name: 'Refresh API status' }));

    expect(api.refetchHealth).toHaveBeenCalledWith({ throwOnError: true });
    expect(await screen.findByRole('status')).toHaveTextContent('API status refresh failed');
  });

  it('disables refresh and announces pending work while status queries are fetching', () => {
    api.fetching = true;
    renderTopBar();
    expect(screen.getByRole('button', { name: 'Refresh API status' })).toBeDisabled();
    expect(screen.getByRole('status')).toHaveTextContent('Refreshing API status');
    api.fetching = false;
  });

  it('shows export only for registered real content and announces success', async () => {
    const user = userEvent.setup();
    const view = renderTopBarWithExport(null);
    expect(screen.queryByRole('button', { name: 'Export current result' })).not.toBeInTheDocument();
    view.unmount();
    renderTopBarWithExport(spec);
    await user.click(await screen.findByRole('button', { name: 'Export current result' }));
    expect(exportsApi.download).toHaveBeenCalledWith(spec);
    expect(screen.getByRole('status')).toHaveTextContent('Export complete: result.json');
  });

  it('announces export errors', async () => {
    exportsApi.download.mockImplementationOnce(() => { throw new Error('blocked'); });
    renderTopBarWithExport(spec);
    await userEvent.click(await screen.findByRole('button', { name: 'Export current result' }));
    expect(screen.getByRole('status')).toHaveTextContent('Export failed');
  });

  it('does not let an export announcement mask a subsequent refresh', async () => {
    api.refetchHealth.mockResolvedValue({}); api.refetchVersion.mockResolvedValue({});
    renderTopBarWithExport(spec);
    await userEvent.click(await screen.findByRole('button', { name: 'Export current result' }));
    expect(screen.getByRole('status')).toHaveTextContent('Export complete');
    await userEvent.click(screen.getByRole('button', { name: 'Refresh API status' }));
    expect(await screen.findByRole('status')).toHaveTextContent('API status refreshed');
    expect(screen.getByRole('status')).not.toHaveTextContent('Export complete');
  });
});
