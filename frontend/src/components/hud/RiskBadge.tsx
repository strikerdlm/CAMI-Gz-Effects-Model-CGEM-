import React from 'react';
import clsx from 'clsx';

export type RiskTier = 'CLEAR' | 'CAUTION' | 'WARNING' | 'G-LOC' | 'OOD';

interface RiskBadgeProps {
  tier: RiskTier;
  pulse?: boolean;
  className?: string;
}

const tierStyle: Record<RiskTier, string> = {
  CLEAR:   'bg-hud-phosphor/10 text-hud-phosphor border-hud-phosphor/50 shadow-hud-glow-green',
  CAUTION: 'bg-hud-amber/10 text-hud-amber border-hud-amber/60 shadow-hud-glow-amber',
  WARNING: 'bg-hud-amber/20 text-hud-amber border-hud-amber shadow-hud-glow-amber',
  'G-LOC': 'bg-hud-red/15 text-hud-red border-hud-red shadow-hud-glow-red',
  OOD:     'bg-hud-ice/10 text-hud-ice border-hud-ice/60',
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({ tier, pulse, className }) => (
  <span
    className={clsx(
      'inline-flex items-center gap-2 px-3 py-1 rounded-sm border font-mono font-semibold text-xs tracking-callsign uppercase',
      tierStyle[tier],
      pulse && 'animate-pulse-amber',
      className,
    )}
  >
    <span className="w-1.5 h-1.5 rounded-full bg-current" />
    {tier}
  </span>
);
