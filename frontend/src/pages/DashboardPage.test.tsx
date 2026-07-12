import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import { DashboardPage } from './DashboardPage';

const apiState = vi.hoisted(() => ({
  healthStatus: 'degraded',
  runData: undefined as unknown,
}));

vi.mock('../services/cgemApi', () => ({
  cgemApiBaseURL: 'http://localhost:8000',
  useHealth: () => ({ data: { status: apiState.healthStatus } }),
  useRunCgem: () => ({
    data: apiState.runData,
    error: null,
    isError: false,
    isPending: false,
    mutate: vi.fn(),
  }),
  useVersion: () => ({ data: undefined, isError: true, isLoading: false }),
  apiErrorMessage: (error: unknown) => String(error),
}));

describe('Dashboard offline state', () => {
  const renderPage = () => render(<MemoryRouter><DashboardPage /></MemoryRouter>);
  beforeEach(() => {
    apiState.healthStatus = 'degraded';
    apiState.runData = undefined;
  });

  it('does not present fixture physiology as authoritative CGEM output', () => {
    renderPage();

    expect(screen.getByText(/CGEM results unavailable/i)).toBeTruthy();
    expect(screen.getByText(/No physiological result is shown/i)).toBeTruthy();
    expect(screen.queryByText('Max G_eff')).toBeNull();
    expect(screen.queryByText('Integrated Physiological Response')).toBeNull();
  });

  it('does not display a cached authoritative result after health degrades', () => {
    apiState.runData = {
      maneuver: 'high_g_turn',
      pilot_profile: 'who_profile=2',
      duration_s: 0,
      time_to_greyout_s: null,
      time_to_blackout_s: null,
      time_to_gloc_s: null,
      data: {
        'Time(s)': [0], G: [1], G_eff: [1], 'HLAP(mmHg)': [100],
        'F_con(dl/min)': [1], 'F_vis(dl/min)': [1], 'F_bo(dl/min)': [1],
        'c_bank(s)': [7], 'bo_bank(s)': [7], Conscious: [1], Greyout: [0], Blackout: [0],
      },
    };

    renderPage();

    expect(screen.getByText(/CGEM results unavailable/i)).toBeTruthy();
    expect(screen.queryByText('Max G_eff')).toBeNull();
  });
});
