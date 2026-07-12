import { useEffect, useRef, type RefObject } from 'react';
import { NavLink } from 'react-router-dom';
import { X } from 'lucide-react';

import { APP_ROUTES } from '../../app/routes';
import { cn } from '../../utils';

interface MobileNavDrawerProps {
  open: boolean;
  onClose: () => void;
  triggerRef: RefObject<HTMLButtonElement | null>;
}

const focusableSelector = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',');

export function MobileNavDrawer({ open, onClose, triggerRef }: MobileNavDrawerProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    const trigger = triggerRef.current;
    const background = document.querySelector<HTMLElement>('[data-shell-background]');
    background?.setAttribute('inert', '');
    document.body.style.overflow = 'hidden';
    closeRef.current?.focus();

    return () => {
      background?.removeAttribute('inert');
      document.body.style.overflow = previousOverflow;
      trigger?.focus();
    };
  }, [open, triggerRef]);

  if (!open) return null;

  function handleKeyDown(event: React.KeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key !== 'Tab') return;

    const focusable = Array.from(
      dialogRef.current?.querySelectorAll<HTMLElement>(focusableSelector) ?? [],
    );
    const first = focusable[0];
    const last = focusable.at(-1);
    if (!first || !last) return;

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <div className="mobile-nav-layer fixed inset-0 z-[110]">
      <div
        className="absolute inset-0 bg-black/70"
        aria-hidden="true"
        onClick={onClose}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="mobile-navigation-title"
        onKeyDown={handleKeyDown}
        className="relative flex h-full w-[min(86vw,320px)] flex-col border-r border-hud-line bg-hud-panel shadow-2xl"
      >
        <div className="flex min-h-16 items-center justify-between border-b border-hud-line px-4">
          <h2 id="mobile-navigation-title" className="font-condensed tracking-callsign text-hud-ink">
            Navigation
          </h2>
          <button
            ref={closeRef}
            type="button"
            aria-label="Close navigation"
            onClick={onClose}
            className="min-h-11 min-w-11 rounded-sm text-hud-ink-faint transition-colors hover:bg-hud-bezel hover:text-hud-amber"
          >
            <X className="mx-auto h-5 w-5" aria-hidden="true" />
          </button>
        </div>
        <nav aria-label="Mobile primary" className="custom-scrollbar flex-1 overflow-y-auto p-3">
          {APP_ROUTES.map((route) => (
            <NavLink
              key={route.id}
              to={route.path}
              onClick={onClose}
              className={({ isActive }) => cn(
                'mb-1 block rounded-sm px-4 py-3 font-mono text-sm transition-colors',
                isActive
                  ? 'bg-hud-amber/15 text-hud-amber'
                  : 'text-hud-ink-faint hover:bg-hud-bezel hover:text-hud-ink',
              )}
            >
              {route.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}
