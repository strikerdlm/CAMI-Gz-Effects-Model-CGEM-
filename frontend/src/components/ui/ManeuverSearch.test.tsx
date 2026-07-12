import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ManeuverSearch } from './ManeuverSearch';

describe('ManeuverSearch', () => {
  it('navigates to the active matching maneuver with the keyboard', async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(<ManeuverSearch onNavigate={onNavigate} />);

    const search = screen.getByRole('combobox', { name: 'Search maneuvers' });
    await user.type(search, 'hammer');
    expect(search).toHaveAttribute('aria-expanded', 'true');
    await user.keyboard('{ArrowDown}{Enter}');

    expect(onNavigate).toHaveBeenCalledWith('/simulator?maneuver=hammerhead');
  });

  it('closes its result list on Escape', async () => {
    const user = userEvent.setup();
    render(<ManeuverSearch onNavigate={vi.fn()} />);
    const search = screen.getByRole('combobox', { name: 'Search maneuvers' });

    await user.type(search, 'hammer');
    expect(screen.getByRole('listbox', { name: 'Maneuver search results' })).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('listbox', { name: 'Maneuver search results' })).not.toBeInTheDocument();
  });

  it('politely announces when there are no matches', async () => {
    const user = userEvent.setup();
    render(<ManeuverSearch onNavigate={vi.fn()} />);
    await user.type(screen.getByRole('combobox', { name: 'Search maneuvers' }), 'no such maneuver xyz');

    expect(screen.getByRole('status')).toHaveTextContent('No maneuvers found');
  });
});
