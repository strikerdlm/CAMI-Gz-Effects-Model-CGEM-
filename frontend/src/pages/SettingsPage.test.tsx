import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { SettingsPage } from './SettingsPage';

vi.mock('../services/cgemApi', () => ({
  useHealth: () => ({ data: { status: 'ok' }, isError: false, isPending: false }),
  useVersion: () => ({ data: { package_version: 'test', cgem_binary_sha256: 'abc', dataset_name: 'fixture', dataset_master_seed: 1, targets: [] } }),
}));

function renderSettings() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}><SettingsPage /></QueryClientProvider>);
}

describe('SettingsPage Phase 1 controls', () => {
  it('labels the API URL input and provides 44px Apply and Default targets', () => {
    renderSettings();
    const input = screen.getByRole('textbox', { name: 'Base URL' });
    expect(input).toHaveAttribute('id', 'api-base-url');
    expect(input).toHaveAttribute('name', 'api-base-url');
    expect(screen.getByRole('button', { name: 'Apply' })).toHaveClass('min-h-11');
    expect(screen.getByRole('button', { name: 'Default' })).toHaveClass('min-h-11');
  });

  it('does not expose inert phosphor or acceleration-unit controls', () => {
    renderSettings();
    expect(screen.queryByText('Phosphor primary')).not.toBeInTheDocument();
    expect(screen.queryByText('Acceleration units')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'amber' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '+Gz' })).not.toBeInTheDocument();
  });
});
