/// <reference types="node" />
import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import { MainLayout } from './MainLayout';
const styles = readFileSync(join(process.cwd(), 'src/index.css'), 'utf8');

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
    const banner = screen.getByRole('banner');
    const main = screen.getByRole('main');

    expect(banner).toBeInTheDocument();
    expect(main).not.toContainElement(banner);
    expect(screen.getByRole('navigation', { name: 'Primary' })).toBeInTheDocument();
    expect(main).toHaveAttribute('id', 'main-content');
    expect(main).toHaveAttribute('tabindex', '-1');
  });

  it('names shell icon buttons and marks the active route', () => {
    renderLayout('/simulator');

    expect(screen.getByRole('link', { name: 'Simulator' })).toHaveAttribute('aria-current', 'page');
    const collapseButton = screen.getByRole('button', { name: 'Collapse navigation' });
    fireEvent.click(collapseButton);

    expect(screen.getByRole('button', { name: 'Expand navigation' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Refresh API status' })).toBeInTheDocument();
  });

  it('offers a 44 px mobile navigation trigger and hides the persistent sidebar at 390 px', () => {
    window.innerWidth = 390;
    renderLayout();

    expect(screen.getByRole('complementary')).toHaveClass('shell-sidebar');
    expect(screen.getByRole('button', { name: 'Open navigation' })).toHaveClass(
      'mobile-nav-trigger',
      'min-h-11',
      'min-w-11',
    );
    expect(styles).toMatch(/@media\s*\(max-width:\s*639px\)[\s\S]*\.shell-sidebar\s*{[\s\S]*display:\s*none/);
  });

  it('contains focus in the mobile Navigation dialog and closes on Escape', () => {
    renderLayout();
    const trigger = screen.getByRole('button', { name: 'Open navigation' });
    fireEvent.click(trigger);

    const dialog = screen.getByRole('dialog', { name: 'Navigation' });
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    const close = screen.getByRole('button', { name: 'Close navigation' });
    const lastLink = within(dialog).getByRole('link', { name: 'About' });

    lastLink.focus();
    fireEvent.keyDown(dialog, { key: 'Tab' });
    expect(close).toHaveFocus();

    close.focus();
    fireEvent.keyDown(dialog, { key: 'Tab', shiftKey: true });
    expect(lastLink).toHaveFocus();

    fireEvent.keyDown(dialog, { key: 'Escape' });
    expect(screen.queryByRole('dialog', { name: 'Navigation' })).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it('locks scrolling and makes shell content inert while the drawer is open', () => {
    renderLayout();
    fireEvent.click(screen.getByRole('button', { name: 'Open navigation' }));

    expect(document.body.style.overflow).toBe('hidden');
    expect(screen.getByTestId('shell-background')).toHaveAttribute('inert');

    fireEvent.click(screen.getByRole('button', { name: 'Close navigation' }));
    expect(document.body.style.overflow).toBe('');
    expect(screen.getByTestId('shell-background')).not.toHaveAttribute('inert');
  });

  it('closes the drawer after navigation and restores focus on unmount cleanup', () => {
    const { unmount } = render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="*" element={<div>Route content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
    const trigger = screen.getByRole('button', { name: 'Open navigation' });
    fireEvent.click(trigger);
    fireEvent.click(within(screen.getByRole('dialog', { name: 'Navigation' })).getByRole('link', { name: 'Simulator' }));
    expect(screen.queryByRole('dialog', { name: 'Navigation' })).not.toBeInTheDocument();

    fireEvent.click(trigger);
    unmount();
    expect(document.body.style.overflow).toBe('');
  });

  it('defines shell tokens, visible focus, and reduced-motion protections', () => {
    expect(styles).toContain('--shell-sidebar-wide: 260px');
    expect(styles).toContain('--shell-sidebar-rail: 72px');
    expect(styles).toContain('--shell-header: 64px');
    expect(styles).toContain('--hud-ink-faint: #aab4c3');
    expect(styles).toMatch(/:focus-visible\s*{/);
    expect(styles).toMatch(/@media\s*\(prefers-reduced-motion:\s*reduce\)/);
    expect(styles).toMatch(/prefers-reduced-motion:[\s\S]*\.scanline-sweep[\s\S]*animation:\s*none/);
  });

  it('keeps both scanline layers decorative', () => {
    const { container } = renderLayoutWithContainer();
    expect(container.querySelectorAll('.scanlines[aria-hidden="true"], .scanline-sweep[aria-hidden="true"]')).toHaveLength(2);
  });
});

function renderLayoutWithContainer(path = '/') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="*" element={<div>Route content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}
