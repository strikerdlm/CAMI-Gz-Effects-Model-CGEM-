/**
 * Top Bar Component
 * 
 * Header with profile selector, status indicators, and quick actions.
 */

import React, { type RefObject } from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Bell,
  Search,
  Download,
  RefreshCw,
  HelpCircle,
  Menu,
} from 'lucide-react';
import { cn } from '../../utils';
import { useHealth, useVersion } from '../../services/cgemApi';
import { routeForPath } from '../../app/routes';

interface TopBarProps {
  onOpenNavigation: () => void;
  navigationTriggerRef: RefObject<HTMLButtonElement | null>;
  sidebarCollapsed: boolean;
  reduceMotion: boolean | null;
}

export const TopBar: React.FC<TopBarProps> = ({
  onOpenNavigation,
  navigationTriggerRef,
  sidebarCollapsed,
  reduceMotion,
}) => {
  const location = useLocation();
  const pageInfo = routeForPath(location.pathname);

  const health = useHealth();
  const version = useVersion();
  const apiState: 'ok' | 'down' | 'pending' = health.isPending
    ? 'pending'
    : health.data?.status === 'ok'
      ? 'ok'
      : 'down';
  const dotClass =
    apiState === 'ok'
      ? 'bg-hud-phosphor shadow-hud-glow-green'
      : apiState === 'down'
        ? 'bg-hud-red shadow-hud-glow-red'
        : 'bg-hud-amber shadow-hud-glow-amber animate-pulse-amber';
  const linkText =
    apiState === 'ok' ? 'API LINK' : apiState === 'down' ? 'NO LINK' : 'HANDSHAKE';
  const linkTextClass =
    apiState === 'ok' ? 'phosphor' : apiState === 'down' ? 'text-hud-red' : 'amber';

  return (
    <header
      className={cn(
        'shell-topbar fixed top-0 right-0 z-30 h-16',
        sidebarCollapsed && 'shell-topbar-collapsed',
        'bg-hud-bg/85 backdrop-blur-xl',
        'border-b border-hud-line/70',
        'flex items-center justify-between px-6',
        'transition-[left] duration-300'
      )}
    >
      {/* Left: Page Title */}
      <div className="flex items-center gap-4">
        <button
          ref={navigationTriggerRef}
          type="button"
          aria-label="Open navigation"
          onClick={onOpenNavigation}
          className="mobile-nav-trigger min-h-11 min-w-11 rounded-sm text-hud-ink-faint transition-colors hover:bg-hud-panel hover:text-hud-amber"
        >
          <Menu className="mx-auto h-5 w-5" aria-hidden="true" />
        </button>
        <motion.div
          key={location.pathname}
          data-title-transition
          data-motion-mode={reduceMotion ? 'reduced' : 'animated'}
          initial={reduceMotion ? false : { opacity: 0, x: -10 }}
          animate={reduceMotion ? { opacity: 1 } : { opacity: 1, x: 0 }}
          transition={reduceMotion ? undefined : { duration: 0.2 }}
        >
          <h1 className="font-condensed text-lg tracking-callsign uppercase text-hud-ink">
            {pageInfo.title}
          </h1>
          <p className="text-[11px] font-mono text-hud-ink-faint tracking-wide">
            {pageInfo.subtitle}
          </p>
        </motion.div>
      </div>

      {/* Center: Search */}
      <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-hud-ink-faint" />
          <input
            type="text"
            placeholder="SEARCH MANEUVER · TAG · CATEGORY"
            className={cn(
              'w-full pl-10 pr-4 py-1.5 rounded-sm font-mono text-xs tracking-callsign',
              'bg-hud-panel-2 border border-hud-line',
              'text-hud-amber placeholder:text-hud-ink-faint placeholder:tracking-callsign',
              'focus:outline-none focus:border-hud-amber',
              'transition-colors duration-200'
            )}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="shell-topbar-actions flex items-center gap-3">
        {/* API status indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-sm bg-hud-panel border border-hud-line">
          <span className={cn('w-2 h-2 rounded-full', dotClass)} />
          <span
            className={cn(
              'font-mono text-[11px] tracking-callsign uppercase',
              linkTextClass,
            )}
          >
            {linkText}
          </span>
          {version.data?.package_version && (
            <span className="font-mono text-[11px] text-hud-ink-faint">
              · v{version.data.package_version}
            </span>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => { void health.refetch(); void version.refetch(); }}
            aria-label="Refresh API status"
            className={cn(
              'p-2 rounded-sm transition-colors duration-200',
              'text-hud-ink-faint hover:text-hud-amber hover:bg-hud-panel'
            )}
            title="Refresh API status"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button className="shell-secondary-action p-2 rounded-sm transition-colors duration-200 text-hud-ink-faint hover:text-hud-amber hover:bg-hud-panel" title="Export">
            <Download className="w-4 h-4" />
          </button>
          <button className="shell-secondary-action p-2 rounded-sm transition-colors duration-200 text-hud-ink-faint hover:text-hud-amber hover:bg-hud-panel" title="Notifications">
            <Bell className="w-4 h-4" />
          </button>
          <button className="shell-secondary-action p-2 rounded-sm transition-colors duration-200 text-hud-ink-faint hover:text-hud-amber hover:bg-hud-panel" title="Help">
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>

        {/* Callsign */}
        <div className="shell-callsign pl-3 border-l border-hud-line">
          <div className="font-mono text-[11px] tracking-callsign text-hud-ink-faint leading-tight">
            <div className="amber">CGEM-1</div>
            <div>DLM · BOG</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
