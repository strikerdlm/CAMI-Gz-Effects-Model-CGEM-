import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { EvidenceRail } from './EvidenceRail';
import type { CGEMRunResponse, PredictionResponse } from '../../services/types';

const surrogate: PredictionResponse = {
  targets: [], ood: true, ood_score: 2.5, in_envelope: false,
  model_version: 'model-7', cgem_binary_sha256: '1234567890abcdef',
  resolved_maneuver: 'hammerhead', maneuver_category: 'training',
  calibration_scope: 'category', source: 'surrogate',
};

it('describes complete surrogate evidence without relying on color', () => {
  render(<EvidenceRail evidence={{ kind: 'surrogate', response: surrogate }} />);
  const rail = screen.getByRole('complementary', { name: 'Result evidence' });
  expect(rail).toHaveAccessibleDescription(/surrogate.*outside the training envelope/i);
  expect(screen.getByText('Surrogate')).toBeInTheDocument();
  expect(screen.getByText('Outside training envelope (OOD)')).toBeInTheDocument();
  expect(screen.getByText('Category', { selector: 'dd' })).toBeInTheDocument();
  expect(screen.getByText('12345678…')).toBeInTheDocument();
});

it('renders global calibration scope', () => {
  render(<EvidenceRail evidence={{ kind: 'surrogate', response: { ...surrogate, calibration_scope: 'global' } }} />);
  expect(screen.getByText('Global')).toBeInTheDocument();
});

it('describes authoritative evidence and omits unavailable version values', () => {
  const run: CGEMRunResponse = { maneuver: 'loop', pilot_profile: 'WHO 2', duration_s: 1,
    time_to_greyout_s: null, time_to_blackout_s: null, time_to_gloc_s: null,
    data: { 'Time(s)': [], G: [], G_eff: [], 'HLAP(mmHg)': [], 'F_con(dl/min)': [],
      'F_vis(dl/min)': [], 'F_bo(dl/min)': [], 'c_bank(s)': [], 'bo_bank(s)': [], Conscious: [], Greyout: [], Blackout: [] } };
  render(<EvidenceRail evidence={{ kind: 'authoritative', run }} />);
  expect(screen.getByText('Fortran / authoritative CGEM')).toBeInTheDocument();
  expect(screen.getByText('WHO 2')).toBeInTheDocument();
  expect(screen.getByText(/not an operational flight-safety system/i)).toBeInTheDocument();
  expect(screen.queryByText(/binary SHA/i)).not.toBeInTheDocument();
});

it('summarizes mixed batch evidence without claiming one maneuver', () => {
  render(<EvidenceRail evidence={{ kind: 'batch', responses: [surrogate, { ...surrogate, resolved_maneuver: 'loop', ood: false, in_envelope: true }] }} />);
  expect(screen.getByText('2 maneuvers')).toBeInTheDocument();
  expect(screen.getByText('1 outside training envelope (OOD); 1 inside')).toBeInTheDocument();
  expect(screen.queryByText('hammerhead')).not.toBeInTheDocument();
});

it('reports the currently filtered batch aggregate', () => {
  render(<EvidenceRail evidence={{ kind: 'batch', responses: [{ ...surrogate, ood: false, in_envelope: true }] }} />);
  expect(screen.getByText('1 maneuver')).toBeInTheDocument();
  expect(screen.getByText('0 outside training envelope (OOD); 1 inside')).toBeInTheDocument();
});
