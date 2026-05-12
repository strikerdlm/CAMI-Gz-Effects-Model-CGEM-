import React from 'react';
import clsx from 'clsx';

interface BezelProps {
  label?: string;
  status?: 'ok' | 'caution' | 'fail' | 'idle';
  className?: string;
  children: React.ReactNode;
}

const statusColor: Record<NonNullable<BezelProps['status']>, string> = {
  ok: 'text-hud-phosphor',
  caution: 'text-hud-amber',
  fail: 'text-hud-red',
  idle: 'text-hud-ink-faint',
};

export const Bezel: React.FC<BezelProps> = ({ label, status = 'idle', className, children }) => (
  <div className={clsx('bezel p-4', className)}>
    {label && (
      <span className={clsx('bezel-label', statusColor[status])}>
        {label}
      </span>
    )}
    {children}
  </div>
);
