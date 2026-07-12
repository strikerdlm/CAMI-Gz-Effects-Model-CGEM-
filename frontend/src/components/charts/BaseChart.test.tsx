import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { BaseChart } from './BaseChart';

const canvas = document.createElement('canvas');
canvas.tabIndex = 0;

vi.mock('echarts', () => ({
  init: vi.fn((element: HTMLElement) => {
    element.appendChild(canvas);
    return ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    showLoading: vi.fn(),
    hideLoading: vi.fn(),
    });
  }),
}));

describe('BaseChart', () => {
  beforeEach(() => {
    canvas.tabIndex = 0;
    vi.mocked(document.createElement).mockRestore?.();
  });

  it('exposes a named image with a data-derived summary', () => {
    render(
      <BaseChart
        option={{}}
        accessibleName="G-force profile"
        accessibleSummary="Duration 12.0 seconds; peak G 7.5; peak effective G 6.8."
      />,
    );

    const chart = screen.getByRole('img', { name: 'G-force profile' });
    expect(chart).toHaveTextContent('Duration 12.0 seconds; peak G 7.5; peak effective G 6.8.');
    expect(chart).toHaveAccessibleDescription(
      'Duration 12.0 seconds; peak G 7.5; peak effective G 6.8.',
    );
  });

  it('does not make the generated canvas an artificial tab stop', () => {
    render(
      <BaseChart option={{}} accessibleName="Chart" accessibleSummary="Summary." />,
    );

    expect(canvas).toHaveAttribute('tabindex', '-1');
  });
});
