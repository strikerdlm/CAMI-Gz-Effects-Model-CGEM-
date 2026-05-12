import React from 'react';
import clsx from 'clsx';

interface SegmentReadoutProps {
  value: number | string | null | undefined;
  unit?: string;
  precision?: number;
  width?: number;
  tone?: 'amber' | 'phosphor' | 'red' | 'ice';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  prefix?: string;
}

const toneCls: Record<NonNullable<SegmentReadoutProps['tone']>, string> = {
  amber: 'amber',
  phosphor: 'phosphor',
  red: 'text-hud-red drop-shadow-[0_0_8px_rgba(255,59,48,0.5)]',
  ice: 'text-hud-ice drop-shadow-[0_0_8px_rgba(111,211,255,0.5)]',
};

const sizeCls: Record<NonNullable<SegmentReadoutProps['size']>, string> = {
  sm: 'text-base',
  md: 'text-xl',
  lg: 'text-3xl',
  xl: 'text-5xl',
};

export const SegmentReadout: React.FC<SegmentReadoutProps> = ({
  value,
  unit,
  precision = 1,
  width = 0,
  tone = 'amber',
  size = 'md',
  prefix,
}) => {
  let body = '----';
  if (typeof value === 'number' && Number.isFinite(value)) {
    body = value.toFixed(precision);
  } else if (typeof value === 'string') {
    body = value;
  }
  const padded = width > 0 ? body.padStart(width, ' ') : body;
  return (
    <span className={clsx('font-mono tabular-nums tracking-tight', toneCls[tone], sizeCls[size])}>
      {prefix && <span className="text-hud-ink-faint pr-1">{prefix}</span>}
      <span>{padded}</span>
      {unit && <span className="text-hud-ink-faint text-[0.55em] pl-1 align-baseline">{unit}</span>}
    </span>
  );
};
