import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import { MainLayout } from './MainLayout';

vi.mock('../../services/cgemApi', () => ({
  useHealth: () => ({
    data: { status: 'ok' },
    isPending: false,
    refetch: vi.fn(),
  }),
  useVersion: () => ({ data: { package_version: '1.0.0' }, refetch: vi.fn() }),
}));

function renderLayout(path = '/') {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="*" element={<div>Route content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe('MainLayout semantics', () => {
  it('provides a skip target and named page landmarks', () => {
    renderLayout();

    expect(screen.getByRole('link', { name: 'Skip to main content' })).toHaveAttribute(
      'href',
      '#main-content',
    );
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Primary' })).toBeInTheDocument();
    expect(screen.getByRole('main')).toHaveAttribute('id', 'main-content');
    expect(screen.getByRole('main')).toHaveAttribute('tabindex', '-1');
  });

  it('names shell icon buttons and marks the active route', () => {
    renderLayout('/simulator');

    expect(screen.getByRole('button', { name: 'Collapse navigation' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Refresh API status' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Simulator' })).toHaveAttribute('aria-current', 'page');
  });
});
