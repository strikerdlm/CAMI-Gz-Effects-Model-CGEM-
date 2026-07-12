import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ProfileSelector } from './ProfileSelector';

describe('ProfileSelector', () => {
  it('has a named combobox and selects an option with arrow keys and Enter', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(<ProfileSelector selectedProfileId="hammerhead" onSelect={onSelect} />);
    const trigger = screen.getByRole('combobox', { name: 'Maneuver profile' });

    await user.click(trigger);
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
    await user.keyboard('{ArrowDown}{Enter}');

    expect(onSelect).toHaveBeenCalledOnce();
    expect(trigger).toHaveFocus();
  });

  it('moves focus to the searchable combobox and owns active option semantics', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(<ProfileSelector selectedProfileId="hammerhead" onSelect={onSelect} />);
    await user.click(screen.getByRole('combobox', { name: 'Maneuver profile' }));

    const search = await screen.findByRole('combobox', { name: 'Search maneuver profiles' });
    expect(search).toHaveFocus();
    expect(search).toHaveAttribute('aria-controls');
    expect(search).toHaveAttribute('aria-expanded', 'true');
    await user.type(search, 'hammer');
    await user.keyboard('{ArrowDown}');
    expect(search).toHaveAttribute('aria-activedescendant', expect.stringContaining('hammerhead'));
    await user.keyboard('{Enter}');
    expect(onSelect).toHaveBeenCalledWith('hammerhead');
    expect(screen.getByRole('combobox', { name: 'Maneuver profile' })).toHaveFocus();
  });

  it('closes with Escape and restores trigger focus', async () => {
    const user = userEvent.setup();
    render(<ProfileSelector selectedProfileId="hammerhead" onSelect={vi.fn()} label="Flight profile" />);
    const trigger = screen.getByRole('combobox', { name: 'Flight profile' });
    await user.click(trigger);
    await user.keyboard('{Escape}');

    expect(screen.queryByRole('listbox', { name: 'Maneuver profiles' })).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it('dismisses outside and uses neutral load wording without risk labels', async () => {
    const user = userEvent.setup();
    render(<><ProfileSelector selectedProfileId="hammerhead" onSelect={vi.fn()} /><button>Outside</button></>);
    await user.click(screen.getByRole('combobox', { name: 'Maneuver profile' }));

    expect(screen.queryByText(/^(Low|Medium|High)( Risk)?$/i)).not.toBeInTheDocument();
    expect(screen.getAllByText(/Peak load:/i).length).toBeGreaterThan(0);
    await user.click(screen.getByRole('button', { name: 'Outside' }));
    expect(screen.queryByRole('listbox', { name: 'Maneuver profiles' })).not.toBeInTheDocument();
  });
});
