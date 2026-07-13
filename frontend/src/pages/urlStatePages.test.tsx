import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { createMemoryRouter, RouterProvider, useLocation } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import { DashboardPage } from './DashboardPage';

const mutate = vi.fn();

vi.mock('../services/cgemApi', () => ({
  cgemApiBaseURL: 'http://localhost:8000',
  useHealth: () => ({ data: { status: 'ok' } }),
  useRunCgem: () => ({ data: {
    maneuver: 'high_g_turn', pilot_profile: 'who_profile=2', duration_s: 1,
    time_to_greyout_s: null, time_to_blackout_s: null, time_to_gloc_s: null,
    data: { 'Time(s)': [0, 1], G: [1, 1], G_eff: [1, 1], 'HLAP(mmHg)': [100, 100], 'F_con(dl/min)': [1, 1], 'F_vis(dl/min)': [1, 1], 'F_bo(dl/min)': [1, 1], 'c_bank(s)': [7, 7], 'bo_bank(s)': [7, 7], Conscious: [1, 1], Greyout: [0, 0], Blackout: [0, 0] },
  }, isError: false, isPending: false, mutate }),
  useVersion: () => ({ data: undefined, isError: true, isLoading: false }),
  apiErrorMessage: String,
}));

vi.mock('../components/charts', () => ({
  ModelDynamicsChart: () => null, GForceLineChart: () => null,
  PhysiologicalHeatmap: () => null, RadarSummaryChart: () => null,
  GDistributionChart: () => null, StateDurationsChart: () => null,
  CerebralFlowChart: () => null,
}));

vi.mock('../components/ui', () => ({
  MetricCard: () => null,
  VariableInsightsPanel: () => null,
  ProfileSelector: ({ selectedProfileId, onSelect }: { selectedProfileId: string; onSelect: (id: string) => void }) => (
    <button type="button" onClick={() => onSelect('hammerhead')}>Maneuver: {selectedProfileId}</button>
  ),
}));

function LocationProbe() {
  const location = useLocation();
  return <output aria-label="location">{location.pathname}{location.search}</output>;
}

function renderDashboard(url: string) {
  const router = createMemoryRouter([{
    path: '/dashboard',
    element: <><DashboardPage /><LocationProbe /></>,
  }], { initialEntries: [url] });
  render(<RouterProvider router={router} />);
  return router;
}

describe('URL-backed page controls', () => {
  it('initializes dashboard controls from a non-default URL', () => {
    renderDashboard('/dashboard?maneuver=hammerhead&preset=max_protection&chart=flows&layout=single');
    expect(screen.getByRole('complementary', { name: 'Result evidence' })).toHaveTextContent('Fortran / authoritative CGEM');
    expect(screen.getByRole('button', { name: 'Maneuver: hammerhead' })).toBeTruthy();
    expect(screen.getByTitle('Single Chart')).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getAllByText('Cerebral Flow').find((node) => node.closest('button'))?.closest('button')).toHaveClass('text-primary-400');
  });

  it('pushes maneuver selections and replaces transient layout changes', async () => {
    const router = renderDashboard('/dashboard');
    fireEvent.click(screen.getByRole('button', { name: /Maneuver:/ }));
    expect(screen.getByLabelText('location')).toHaveTextContent('/dashboard?maneuver=hammerhead');
    fireEvent.click(screen.getByTitle('Single Chart'));
    expect(screen.getByLabelText('location')).toHaveTextContent('/dashboard?maneuver=hammerhead&layout=single');
    await router.navigate(-1);
    await waitFor(() => expect(screen.getByLabelText('location')).toHaveTextContent('/dashboard'));
  });

  it('rejects invalid URL values before an authoritative request', () => {
    renderDashboard('/dashboard?maneuver=unsupported&preset=nope&chart=bad&layout=wide');
    expect(screen.getByText(/Unsupported dashboard URL settings/)).toHaveTextContent(/safe defaults/i);
    expect(screen.getByRole('button', { name: 'Maneuver: high_g_turn' })).toBeTruthy();
    expect(mutate).not.toHaveBeenCalledWith(expect.objectContaining({ maneuver: 'unsupported' }));
  });
});
