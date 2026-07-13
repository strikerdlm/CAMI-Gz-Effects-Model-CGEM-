import React, { useId, useMemo, useRef, useState } from 'react';
import { Search } from 'lucide-react';

import { MANEUVERS } from '../../data/maneuvers';
import { cn } from '../../utils';

interface ManeuverSearchProps {
  onNavigate: (path: string) => void;
  className?: string;
}

const displayName = (id: string) => id.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

export function ManeuverSearch({ onNavigate, className }: ManeuverSearchProps) {
  const listId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const normalized = query.trim().toLowerCase();
  const results = useMemo(() => normalized
    ? MANEUVERS.filter((maneuver) => [
        maneuver.id, displayName(maneuver.id), maneuver.category, maneuver.aircraft,
        maneuver.description, ...maneuver.tags,
      ].some((value) => value.toLowerCase().includes(normalized))).slice(0, 8)
    : [], [normalized]);
  const active = activeIndex >= 0 ? results[activeIndex] : undefined;

  React.useEffect(() => {
    const dismiss = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', dismiss);
    return () => document.removeEventListener('mousedown', dismiss);
  }, []);

  const choose = (index: number) => {
    const maneuver = results[index];
    if (!maneuver) return;
    onNavigate(`/simulator?maneuver=${encodeURIComponent(maneuver.id)}`);
    setOpen(false);
    setQuery('');
    setActiveIndex(-1);
  };

  return (
    <div ref={rootRef} className={cn('relative w-full', className)}>
      <Search aria-hidden="true" className="absolute left-3 top-1/2 z-10 h-4 w-4 -translate-y-1/2 text-hud-ink-faint" />
      <input
        type="search"
        role="combobox"
        aria-label="Search maneuvers"
        aria-autocomplete="list"
        aria-controls={listId}
        aria-expanded={open && normalized.length > 0}
        aria-activedescendant={active ? `${listId}-${active.id}` : undefined}
        value={query}
        onFocus={() => normalized && setOpen(true)}
        onChange={(event) => { setQuery(event.target.value); setOpen(true); setActiveIndex(-1); }}
        onKeyDown={(event) => {
          if (event.key === 'ArrowDown' && results.length) {
            event.preventDefault(); setOpen(true); setActiveIndex((index) => Math.min(index + 1, results.length - 1));
          } else if (event.key === 'ArrowUp' && results.length) {
            event.preventDefault(); setActiveIndex((index) => index <= 0 ? results.length - 1 : index - 1);
          } else if (event.key === 'Enter' && activeIndex >= 0) {
            event.preventDefault(); choose(activeIndex);
          } else if (event.key === 'Escape') {
            event.preventDefault(); setOpen(false); setActiveIndex(-1);
          }
        }}
        placeholder="SEARCH MANEUVER · TAG · CATEGORY"
        className="w-full rounded-sm border border-hud-line bg-hud-panel-2 py-1.5 pl-10 pr-4 font-mono text-xs tracking-callsign text-hud-amber placeholder:text-hud-ink-faint focus:border-hud-amber focus:outline-none"
      />
      {open && normalized && (
        <div className="absolute top-full z-50 mt-2 w-full rounded-sm border border-hud-line bg-hud-panel-2 shadow-xl">
          {results.length ? (
            <ul id={listId} role="listbox" aria-label="Maneuver search results" className="max-h-80 overflow-y-auto py-1">
              {results.map((maneuver, index) => (
                <li
                  id={`${listId}-${maneuver.id}`}
                  key={maneuver.id}
                  role="option"
                  aria-selected={index === activeIndex}
                  className={cn('cursor-pointer px-3 py-2 text-xs text-hud-ink', index === activeIndex && 'bg-hud-amber/15 text-hud-amber')}
                  onMouseDown={(event) => event.preventDefault()}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={() => choose(index)}
                >
                  <span className="block font-medium">{displayName(maneuver.id)}</span>
                  <span className="block text-hud-ink-faint">{maneuver.aircraft} · {maneuver.category.replace(/_/g, ' ')}</span>
                </li>
              ))}
            </ul>
          ) : <p role="status" aria-live="polite" className="px-3 py-3 text-xs text-hud-ink-faint">No maneuvers found</p>}
        </div>
      )}
    </div>
  );
}
