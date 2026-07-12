import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import { TopBar } from './TopBar';

const api = vi.hoisted(() => ({ refetchHealth: vi.fn(), refetchVersion: vi.fn(), fetching: false }));
vi.mock('../../services/cgemApi', () => ({
  useHealth: () => ({ data: { status: 'ok' }, isPending: false, isFetching: api.fetching, refetch: api.refetchHealth }),
  useVersion: () => ({ data: { package_version: '1.0' }, isFetching: api.fetching, refetch: api.refetchVersion }),
}));

function renderTopBar(path = '/simulator') {
  return render(<MemoryRouter initialEntries={[path]}><TopBar onOpenNavigation={vi.fn()} navigationTriggerRef={{ current: null }} sidebarCollapsed={false} reduceMotion={false} /></MemoryRouter>);
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

  it('disables refresh and announces pending work while status queries are fetching', () => {
    api.fetching = true;
    renderTopBar();
    expect(screen.getByRole('button', { name: 'Refresh API status' })).toBeDisabled();
    expect(screen.getByRole('status')).toHaveTextContent('Refreshing API status');
    api.fetching = false;
  });
});
