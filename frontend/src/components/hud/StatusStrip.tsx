import React, { useEffect, useState } from 'react';

interface StatusStripProps {
  mode?: string;
  callsign?: string;
}

const fmt = (d: Date): string => d.toISOString().slice(11, 19) + 'Z';

export const StatusStrip: React.FC<StatusStripProps> = ({
  mode = 'TACTICAL',
  callsign = 'CGEM-1',
}) => {
  const [now, setNow] = useState<Date>(() => new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-callsign text-hud-ink-faint px-1 pb-2 border-b border-hud-line/60">
      <span><span className="text-hud-amber">●</span> {mode}</span>
      <span>{callsign}</span>
      <span>{fmt(now)}</span>
    </div>
  );
};
