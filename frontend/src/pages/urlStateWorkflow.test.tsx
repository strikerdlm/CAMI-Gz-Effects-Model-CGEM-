import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { createMemoryRouter, MemoryRouter, RouterProvider, useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AnalysisPage } from './AnalysisPage';
import { BatchPage } from './BatchPage';
import { OverviewPage } from './OverviewPage';
import { PredictionPage } from './PredictionPage';
import { SimulatorPage } from './SimulatorPage';

const api = vi.hoisted(() => ({ predict: vi.fn(), run: vi.fn(), sweep: vi.fn() }));

vi.mock('../services/cgemApi', () => ({
  cgemApiBaseURL: 'http://localhost:8000', apiErrorMessage: String,
  useHealth: () => ({ data: { status: 'ok' } }),
  useVersion: () => ({ data: { package_version: 'test', cgem_binary_sha256: 'abcdef123', dataset_master_seed: 1 }, isError: false, isLoading: false }),
  usePredict: () => ({ data: { targets: [], ood: false, ood_score: 0, in_envelope: true, model_version: 'test', cgem_binary_sha256: 'abc', source: 'surrogate', resolved_maneuver: 'hammerhead', maneuver_category: 'training', calibration_scope: 'category' }, mutate: api.predict, isError: false, isPending: false }),
  useRunCgem: () => ({ data: { maneuver: 'hammerhead', pilot_profile: 'who_profile=2', duration_s: 1, time_to_greyout_s: null, time_to_blackout_s: null, time_to_gloc_s: null, data: { 'Time(s)': [0, 1], G: [1, 1], G_eff: [1, 1], 'HLAP(mmHg)': [100, 100], 'F_con(dl/min)': [1, 1], 'F_vis(dl/min)': [1, 1], 'F_bo(dl/min)': [1, 1], 'c_bank(s)': [7, 7], 'bo_bank(s)': [7, 7], Conscious: [1, 1], Greyout: [0, 0], Blackout: [0, 0] } }, mutate: api.run, isError: false, isPending: false }),
  useSweep: () => ({ data: undefined, mutate: api.sweep, isError: false, isPending: false }),
}));

vi.mock('../components/ui', () => ({
  ProfileSelector: ({ selectedProfileId, onSelect }: { selectedProfileId: string; onSelect: (id: string) => void }) => <button onClick={() => onSelect('hammerhead')}>Maneuver: {selectedProfileId}</button>,
  MetricCard: ({ label }: { label: string }) => <div>{label}</div>,
  OODBanner: () => <div data-testid="surrogate-result">Surrogate evidence</div>,
  PredictionTable: () => null, VariableInsightsPanel: () => null,
}));

vi.mock('../components/charts', () => ({
  GForceLineChart: () => null, CerebralFlowChart: () => <div data-testid="authoritative-chart" />,
  SensitivityChart: ({ target }: { target: string }) => <div data-testid="sensitivity-request">{target}</div>,
}));

vi.mock('../components/hud', () => ({
  Bezel: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SegmentReadout: ({ value }: { value: number }) => <output aria-label="telemetry-g">{value}</output>,
  RiskBadge: () => null, StatusStrip: ({ callsign }: { callsign: string }) => <div>{callsign}</div>,
  AttitudeIndicator: () => null,
  GTracePlayer: ({ maneuver, onTimeChange }: { maneuver: { id: string }; onTimeChange: (t: number, g: number) => void }) => <div><span data-testid="player-maneuver">{maneuver.id}</span><button onClick={() => onTimeChange(99, 9)}>Advance playback</button></div>,
}));

function LocationProbe() { const location = useLocation(); return <output aria-label="location">{location.pathname}{location.search}</output>; }
function renderRoute(path: string, element: React.ReactNode) {
  const pathname = path.split('?')[0];
  const router = createMemoryRouter([{ path: pathname, element: <>{element}<LocationProbe /></> }], { initialEntries: [path] });
  render(<RouterProvider router={router} />);
  return router;
}

describe('shareable research workflows', () => {
  beforeEach(() => vi.clearAllMocks());

  it('carries the Overview maneuver into the Simulator canonical URL', () => {
    render(<MemoryRouter initialEntries={['/?maneuver=hammerhead']}><OverviewPage /></MemoryRouter>);
    expect(screen.getByRole('link', { name: /Open in Simulator/ })).toHaveAttribute('href', '/simulator?maneuver=hammerhead');
  });

  it('renders Prediction sections according to view and keeps custom drafts out of the URL', () => {
    renderRoute('/prediction?maneuver=hammerhead&pilot=6&view=authoritative', <PredictionPage />);
    expect(screen.queryByTestId('surrogate-result')).toBeNull();
    expect(screen.getByText('Time to G-LOC')).toBeTruthy();
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'custom' } });
    expect(screen.getByLabelText('location')).toHaveTextContent('pilot=6');
    fireEvent.click(screen.getByRole('button', { name: 'surrogate' }));
    expect(screen.getByTestId('surrogate-result')).toBeTruthy();
    expect(screen.queryByText('Time to G-LOC')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'comparison' }));
    expect(screen.getByTestId('surrogate-result')).toBeTruthy();
    expect(screen.getByText('Time to G-LOC')).toBeTruthy();
  });

  it('falls back from an invalid Prediction maneuver before mutations receive it', () => {
    renderRoute('/prediction?maneuver=unsupported&view=comparison', <PredictionPage />);
    expect(screen.getByText(/Unsupported prediction URL settings/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /Predict \(surrogate/ }));
    expect(api.predict).toHaveBeenCalledWith(expect.objectContaining({ maneuver: { maneuver: 'high_g_turn' } }));
    expect(api.predict).not.toHaveBeenCalledWith(expect.objectContaining({ maneuver: { maneuver: 'unsupported' } }));
  });

  it('shows sensitivity only in Analysis sensitivity view and restores view through history', async () => {
    const router = renderRoute('/analysis', <AnalysisPage />);
    expect(screen.queryByTestId('sensitivity-request')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'sensitivity' }));
    expect(screen.getByTestId('sensitivity-request')).toBeTruthy();
    await router.navigate('/analysis?view=explanation');
    await waitFor(() => expect(screen.queryByTestId('sensitivity-request')).toBeNull());
    await router.navigate(-1);
    await waitFor(() => expect(screen.getByTestId('sensitivity-request')).toBeTruthy());
  });

  it('rejects invalid Simulator maneuvers and resets parent playback on URL navigation', async () => {
    const router = renderRoute('/simulator?maneuver=invalid', <SimulatorPage />);
    expect(screen.getByTestId('player-maneuver')).toHaveTextContent('hammerhead');
    expect(api.predict).not.toHaveBeenCalledWith(expect.objectContaining({ maneuver: { maneuver: 'invalid' } }));
    fireEvent.click(screen.getByRole('button', { name: 'Advance playback' }));
    expect(screen.getAllByLabelText('telemetry-g')[0]).toHaveTextContent('9');
    expect(screen.getByLabelText('location')).toHaveTextContent('/simulator?maneuver=invalid');
    await router.navigate('/simulator?maneuver=high_g_turn');
    await waitFor(() => expect(screen.getAllByLabelText('telemetry-g')[0]).not.toHaveTextContent('9'));
  });

  it('initializes and updates Batch filters without rerunning the sweep', () => {
    renderRoute('/batch?target=blackout&direction=asc&ood=ood&category=training', <BatchPage />);
    expect(screen.getByLabelText('Sort target')).toHaveValue('blackout');
    fireEvent.change(screen.getByLabelText('OOD filter'), { target: { value: 'all' } });
    expect(screen.getByLabelText('location')).not.toHaveTextContent('ood=');
    expect(api.sweep).not.toHaveBeenCalled();
  });
});
