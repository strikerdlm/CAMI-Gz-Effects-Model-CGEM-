import React, { useEffect, useMemo, useRef, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { Maneuver } from '../../data/maneuvers';
import { flightTimeSeconds } from '../../data/maneuvers';

interface ConformalAnnotation {
  median_s: number;
  low_s: number;
  high_s: number;
  label: string;
}

interface GTracePlayerProps {
  maneuver: Maneuver;
  conformal?: ConformalAnnotation | null;
  height?: number;
  onTimeChange?: (t: number, g: number) => void;
}

/** Linearly interpolate Gz at time `t` over a piecewise-linear trace. */
function interpolateG(t: number, times: number[], gs: number[]): number {
  if (times.length === 0) return 0;
  if (t <= times[0]) return gs[0];
  if (t >= times[times.length - 1]) return gs[gs.length - 1];
  for (let i = 1; i < times.length; i++) {
    if (t < times[i]) {
      const f = (t - times[i - 1]) / (times[i] - times[i - 1]);
      return gs[i - 1] + f * (gs[i] - gs[i - 1]);
    }
  }
  return gs[gs.length - 1];
}

export const GTracePlayer: React.FC<GTracePlayerProps> = ({
  maneuver,
  conformal = null,
  height = 320,
  onTimeChange,
}) => {
  const times = useMemo(() => flightTimeSeconds(maneuver), [maneuver]);
  const gs = useMemo(() => maneuver.samples.map((s) => s.nz), [maneuver]);
  const duration = times.length > 0 ? times[times.length - 1] : 0;

  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<0.5 | 1 | 2>(1);
  const [t, setT] = useState(0);
  const lastFrameRef = useRef<number | null>(null);

  // Reset playhead when the maneuver changes.
  useEffect(() => {
    setT(0);
    setPlaying(false);
    lastFrameRef.current = null;
  }, [maneuver.id]);

  useEffect(() => {
    if (!playing) {
      lastFrameRef.current = null;
      return;
    }
    let raf = 0;
    const tick = (frameTime: number): void => {
      if (lastFrameRef.current === null) {
        lastFrameRef.current = frameTime;
      }
      const dt = (frameTime - lastFrameRef.current) / 1000;
      lastFrameRef.current = frameTime;
      setT((prev) => {
        const next = prev + dt * speed;
        if (next >= duration) {
          setPlaying(false);
          return duration;
        }
        return next;
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, speed, duration]);

  const currentG = useMemo(() => interpolateG(t, times, gs), [t, times, gs]);

  useEffect(() => {
    onTimeChange?.(t, currentG);
  }, [t, currentG, onTimeChange]);

  const option = useMemo<EChartsOption>(() => {
    const seriesData: [number, number][] = times.map((tt, i) => [tt, gs[i]]);
    /* eslint-disable @typescript-eslint/no-explicit-any */
    const markLines: any[] = [
      { xAxis: t, lineStyle: { color: '#FFB400', width: 1.5, type: 'solid' }, label: { show: false } },
      { yAxis: 5, lineStyle: { color: '#FF3B30', width: 0.5, type: 'dashed' }, label: { formatter: '5 G ALERT', color: '#FF3B30', fontFamily: 'IBM Plex Mono', fontSize: 9 } },
      { yAxis: 9, lineStyle: { color: '#FF3B30', width: 0.5, type: 'dashed' }, label: { formatter: '9 G LIMIT', color: '#FF3B30', fontFamily: 'IBM Plex Mono', fontSize: 9 } },
      { yAxis: 0, lineStyle: { color: '#37474f', width: 0.5, type: 'solid' }, label: { show: false } },
    ];
    const markAreas: any[] = [];
    if (conformal) {
      markAreas.push([
        { name: conformal.label, xAxis: conformal.low_s, itemStyle: { color: 'rgba(255,180,0,0.08)' } },
        { xAxis: conformal.high_s },
      ]);
      markLines.push({
        xAxis: conformal.median_s,
        lineStyle: { color: '#4FE773', width: 1.5, type: 'dashed' },
        label: { formatter: `T-LOC ${conformal.median_s.toFixed(1)}s`, color: '#4FE773', fontFamily: 'IBM Plex Mono', fontSize: 9 },
      });
    }
    /* eslint-enable @typescript-eslint/no-explicit-any */
    return {
      animation: false,
      grid: { left: 48, right: 16, top: 16, bottom: 32 },
      xAxis: {
        type: 'value',
        name: 't (s)',
        nameLocation: 'middle',
        nameGap: 22,
        nameTextStyle: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        axisLine: { lineStyle: { color: '#2a3530' } },
        axisLabel: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(42,53,48,0.4)' } },
      },
      yAxis: {
        type: 'value',
        name: '+Gz',
        nameTextStyle: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        axisLine: { lineStyle: { color: '#2a3530' } },
        axisLabel: { color: '#8c9692', fontFamily: 'IBM Plex Mono', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(42,53,48,0.4)' } },
      },
      series: [
        {
          type: 'line',
          data: seriesData,
          smooth: false,
          showSymbol: false,
          lineStyle: { color: '#FFB400', width: 2 },
          areaStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(255,180,0,0.35)' },
                { offset: 1, color: 'rgba(255,180,0,0.0)' },
              ],
            },
          },
          markLine: { silent: true, symbol: 'none', data: markLines },
          markArea: { silent: true, data: markAreas },
        },
      ],
    };
  }, [times, gs, t, conformal]);

  const reset = (): void => {
    setT(0);
    setPlaying(false);
  };

  return (
    <div className="flex flex-col gap-2">
      <ReactECharts option={option} style={{ height, width: '100%' }} notMerge={false} lazyUpdate />
      <div className="flex items-center gap-3 text-xs font-mono">
        <button
          onClick={() => setPlaying((p) => !p)}
          className="px-3 py-1 bg-hud-amber/10 border border-hud-amber/50 text-hud-amber hover:bg-hud-amber/20 rounded-sm tracking-callsign uppercase"
        >
          {playing ? '■ Stop' : '▶ Play'}
        </button>
        <button
          onClick={reset}
          className="px-3 py-1 bg-hud-panel border border-hud-line text-hud-ink-dim hover:text-hud-ink rounded-sm tracking-callsign uppercase"
        >
          ⟲ Rewind
        </button>
        <div className="flex gap-1">
          {([0.5, 1, 2] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={
                'px-2 py-1 rounded-sm border tracking-callsign uppercase ' +
                (speed === s
                  ? 'bg-hud-phosphor/20 border-hud-phosphor/60 text-hud-phosphor'
                  : 'bg-hud-panel border-hud-line text-hud-ink-faint hover:text-hud-ink')
              }
            >
              {s}×
            </button>
          ))}
        </div>
        <input
          type="range"
          min={0}
          max={Math.max(duration, 0.01)}
          step={0.05}
          value={t}
          onChange={(e) => { setT(Number(e.target.value)); setPlaying(false); }}
          className="flex-1 accent-hud-amber"
        />
        <span className="amber font-mono w-20 text-right tabular-nums">{t.toFixed(2)} s</span>
      </div>
    </div>
  );
};
