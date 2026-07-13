import React, { useId, useMemo, useRef, useState } from 'react';
import { ChevronDown, Clock, Plane, Search } from 'lucide-react';

import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../../data/maneuvers';
import { cn } from '../../utils';
import { calculateProfileStats } from '../../utils/calculations';

interface ProfileSelectorProps {
  selectedProfileId: string;
  onSelect: (profileId: string) => void;
  className?: string;
  label?: string;
}

const formatProfileName = (id: string) => id.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

export const ProfileSelector: React.FC<ProfileSelectorProps> = ({ selectedProfileId, onSelect, className, label = 'Maneuver profile' }) => {
  const listId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const optionRefs = useRef<Array<HTMLLIElement | null>>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(-1);
  const selectedProfile = AEROBATIC_PROFILES[selectedProfileId];
  const profiles = useMemo(() => Object.values(AEROBATIC_PROFILES), []);
  const filteredProfiles = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return profiles.filter((profile) => !query || [profile.id, profile.description, profile.aircraft, ...profile.tags]
      .some((value) => value.toLowerCase().includes(query)));
  }, [profiles, searchQuery]);

  const close = (restoreFocus = false) => {
    setIsOpen(false); setActiveIndex(-1);
    if (restoreFocus) triggerRef.current?.focus();
  };
  const activate = (index: number) => {
    setActiveIndex(index);
    requestAnimationFrame(() => optionRefs.current[index]?.scrollIntoView?.({ block: 'nearest' }));
  };
  const choose = (index: number) => {
    const profile = filteredProfiles[index];
    if (!profile) return;
    onSelect(profile.id); close(true);
  };
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') { event.preventDefault(); close(true); return; }
    if (event.key === 'ArrowDown' && filteredProfiles.length) {
      event.preventDefault(); if (!isOpen) setIsOpen(true); activate(Math.min(activeIndex + 1, filteredProfiles.length - 1));
    } else if (event.key === 'ArrowUp' && filteredProfiles.length) {
      event.preventDefault(); if (!isOpen) setIsOpen(true); activate(activeIndex <= 0 ? filteredProfiles.length - 1 : activeIndex - 1);
    } else if (event.key === 'Enter' && isOpen && activeIndex >= 0) { event.preventDefault(); choose(activeIndex); }
  };

  React.useEffect(() => {
    const outside = (event: MouseEvent) => { if (!rootRef.current?.contains(event.target as Node)) close(false); };
    document.addEventListener('mousedown', outside);
    return () => document.removeEventListener('mousedown', outside);
  }, []);

  React.useEffect(() => {
    if (isOpen) searchInputRef.current?.focus();
  }, [isOpen]);

  return (
    <div ref={rootRef} className={cn('relative', className)} onKeyDown={handleKeyDown}>
      <button
        ref={triggerRef}
        type="button"
        role="combobox"
        aria-label={label}
        aria-haspopup="listbox"
        aria-controls={listId}
        aria-expanded={isOpen}
        aria-activedescendant={isOpen && activeIndex >= 0 ? `${listId}-${filteredProfiles[activeIndex]?.id}` : undefined}
        onClick={() => { setIsOpen((open) => !open); setActiveIndex(-1); }}
        className="flex min-w-0 w-full items-center justify-between gap-3 rounded-xl border border-surface-700/50 bg-surface-800/80 px-4 py-3 transition-colors hover:border-primary-500/50"
      >
        <span className="flex min-w-0 items-center gap-3"><span className="shrink-0 rounded-lg bg-primary-500/10 p-2"><Plane aria-hidden="true" className="h-5 w-5 text-primary-400" /></span>
          <span className="min-w-0 text-left"><span className="block truncate font-medium text-white">{selectedProfile ? formatProfileName(selectedProfileId) : 'Select profile'}</span>
            <span className="block line-clamp-1 text-xs text-surface-400">{selectedProfile?.description || 'Choose an aerobatic maneuver'}</span></span></span>
        <ChevronDown aria-hidden="true" className={cn('h-5 w-5 text-surface-400 transition-transform', isOpen && 'rotate-180')} />
      </button>
      {isOpen && <div className="absolute z-50 mt-2 max-h-[400px] w-full overflow-y-auto rounded-xl border border-surface-700/50 bg-surface-900 shadow-xl">
        <div className="sticky top-0 z-10 border-b border-surface-700/40 bg-surface-900 px-3 py-3">
          <label className="relative block"><span className="sr-only">Search maneuver profiles</span><Search aria-hidden="true" className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-surface-500" />
            <input
              ref={searchInputRef}
              role="combobox"
              aria-label="Search maneuver profiles"
              aria-autocomplete="list"
              aria-controls={listId}
              aria-expanded="true"
              aria-activedescendant={activeIndex >= 0 ? `${listId}-${filteredProfiles[activeIndex]?.id}` : undefined}
              value={searchQuery}
              onChange={(event) => { setSearchQuery(event.target.value); setActiveIndex(-1); }}
              className="h-8 w-full rounded-lg border border-surface-700/60 bg-surface-800/80 pl-9 pr-3 text-xs text-surface-100"
            /></label>
        </div>
        <ul id={listId} role="listbox" aria-label="Maneuver profiles" className="py-2">
          {filteredProfiles.map((profile, index) => {
            const stats = calculateProfileStats(profile.samples);
            return <li ref={(node) => { optionRefs.current[index] = node; }} id={`${listId}-${profile.id}`} key={profile.id} role="option" aria-selected={profile.id === selectedProfileId} onMouseEnter={() => setActiveIndex(index)} onMouseDown={(event) => event.preventDefault()} onClick={() => choose(index)} className={cn('cursor-pointer px-4 py-3 text-left hover:bg-surface-800/80', index === activeIndex && 'bg-primary-500/10')}>
              <span className="block font-medium text-white">{formatProfileName(profile.id)}</span><span className="mt-0.5 block text-xs text-surface-400">{profile.description}</span>
              <span className="mt-2 flex gap-3 text-xs text-surface-500"><span className="flex items-center gap-1"><Clock aria-hidden="true" className="h-3 w-3" />{stats.total_duration_s.toFixed(1)}s</span><span>Peak load: {stats.max_positive_g > 0 ? '+' : ''}{stats.max_positive_g.toFixed(1)} G</span></span>
            </li>;
          })}
        </ul>
        {!filteredProfiles.length && <p role="status" className="px-4 py-6 text-center text-sm text-surface-400">No profiles match your search.</p>}
      </div>}
    </div>
  );
};

export default ProfileSelector;
