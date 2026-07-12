import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';

import type { TargetPrediction } from '../../services/types';
import { PredictionTable } from './PredictionTable';

const targets: TargetPrediction[] = [
  {
    target: 'time_to_gloc_s',
    censored: true,
    point: 7.5,
    lo: 6,
    hi: 9,
    event_probability: 0.2,
    expected_time_s: 1.5,
  },
  {
    target: 'hlap_min',
    censored: false,
    point: 82,
    lo: 78,
    hi: 86,
  },
];

describe('PredictionTable target semantics', () => {
  afterEach(cleanup);

  it('distinguishes conditional event time from continuous point estimates', () => {
    render(<PredictionTable targets={targets} />);

    expect(screen.getByRole('columnheader', { name: 'Point estimate' })).toBeTruthy();
    expect(screen.getByText('Conditional time if event occurs')).toBeTruthy();
    expect(screen.getByText('Direct surrogate output')).toBeTruthy();
  });
});
