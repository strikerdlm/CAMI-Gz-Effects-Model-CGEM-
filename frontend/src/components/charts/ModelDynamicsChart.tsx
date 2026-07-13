/**
 * Model Dynamics Chart
 *
 * Multi-axis visualization of key CGEM variables with synchronized event windows.
 * Designed to support scientific interpretation of model internals over time.
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import type { CGEMResult } from '../../types';
import { PHYSIOLOGICAL_THRESHOLDS } from '../../utils/constants';

export type ModelVariableKey = 'geff' | 'f_con' | 'c_bank' | 'bo_bank' | 'hlap';

interface ModelDynamicsChartProps {
  result: CGEMResult;
  title?: string;
  height?: number;
  focusVariable?: ModelVariableKey;
}

interface Interval {
  start: number;
  end: number;
}

const MAX_POINTS = 700;

function sampleByStep(values: number[], step: number): number[] {
  const sampled: number[] = [];
  for (let i = 0; i < values.length; i += step) {
    sampled.push(values[i]);
  }
  return sampled;
}

function extractIntervals(flags: number[], times: number[]): Interval[] {
  const intervals: Interval[] = [];
  if (flags.length === 0 || flags.length !== times.length) {
    return intervals;
  }

  let activeStart: number | null = null;
  for (let i = 0; i < flags.length; i++) {
    const active = flags[i] > 0;
    if (active && activeStart === null) {
      activeStart = times[i];
      continue;
    }
    if (!active && activeStart !== null) {
      intervals.push({ start: activeStart, end: times[i] });
      activeStart = null;
    }
  }

  if (activeStart !== null) {
    intervals.push({
      start: activeStart,
      end: times[times.length - 1],
    });
  }

  return intervals;
}

function buildMarkAreaData(
  intervals: Interval[],
  label: string,
  color: string
): Array<[Record<string, unknown>, Record<string, unknown>]> {
  const limitedIntervals = intervals.slice(0, 16);
  return limitedIntervals.map((interval, idx) => [
    {
      name: idx === 0 ? label : '',
      xAxis: interval.start,
      itemStyle: { color },
    },
    { xAxis: interval.end },
  ]);
}

export const ModelDynamicsChart: React.FC<ModelDynamicsChartProps> = ({
  result,
  title = 'CGEM Model Dynamics',
  height = 420,
  focusVariable,
}) => {
  const option = useMemo<ChartOption>(() => {
    const { times_s, geff_values, f_con_values, c_bank_values, bo_bank_values, hlap_values } = result;

    if (
      times_s.length === 0 ||
      geff_values.length !== times_s.length ||
      f_con_values.length !== times_s.length ||
      c_bank_values.length !== times_s.length ||
      bo_bank_values.length !== times_s.length ||
      hlap_values.length !== times_s.length
    ) {
      return {
        title: { text: title, left: 'center' },
        graphic: {
          type: 'text',
          left: 'center',
          top: 'middle',
          style: {
            text: 'No model dynamics available',
            fill: '#64748b',
            fontSize: 14,
          },
        },
      };
    }

    const step = Math.max(1, Math.ceil(times_s.length / MAX_POINTS));
    const sampledTimes = sampleByStep(times_s, step);
    const sampledGeff = sampleByStep(geff_values, step);
    const sampledFlow = sampleByStep(f_con_values, step);
    const sampledCBank = sampleByStep(c_bank_values, step);
    const sampledBOBank = sampleByStep(bo_bank_values, step);
    const sampledHlap = sampleByStep(hlap_values, step);

    const greyoutIntervals = extractIntervals(result.flags_ne2, times_s);
    const blackoutIntervals = extractIntervals(result.flags_non2, times_s);
    const glocIntervals = extractIntervals(result.flags_n2, times_s);

    const geffMin = Math.floor(Math.min(...sampledGeff, -1));
    const geffMax = Math.ceil(Math.max(...sampledGeff, PHYSIOLOGICAL_THRESHOLDS.gloc_geff + 1));
    const flowMax = Math.ceil(Math.max(...sampledFlow, 55));
    const reserveMax = Math.ceil(Math.max(...sampledCBank, ...sampledBOBank, 8));
    const hlapMax = Math.ceil(Math.max(...sampledHlap, 130));
    const hlapMin = Math.floor(Math.min(...sampledHlap, 60));

    const isFocus = (key: ModelVariableKey): boolean => !focusVariable || focusVariable === key;
    const seriesOpacity = (key: ModelVariableKey): number => (isFocus(key) ? 1 : 0.28);
    const seriesWidth = (key: ModelVariableKey, focusedWidth: number, baseWidth: number): number =>
      isFocus(key) ? focusedWidth : baseWidth;

    const markAreaData = [
      ...buildMarkAreaData(greyoutIntervals, 'Greyout', 'rgba(148, 163, 184, 0.12)'),
      ...buildMarkAreaData(blackoutIntervals, 'Blackout', 'rgba(251, 191, 36, 0.14)'),
      ...buildMarkAreaData(glocIntervals, 'G-LOC', 'rgba(239, 68, 68, 0.16)'),
    ];

    return {
      backgroundColor: 'transparent',
      title: {
        text: title,
        subtext: 'Aligned variables: G_eff, F_con, reserve banks, and HLAP with event windows',
        left: 'center',
        top: 8,
        textStyle: { color: '#f8fafc', fontSize: 16, fontWeight: 600 },
        subtextStyle: { color: '#94a3b8', fontSize: 11 },
      },
      legend: {
        top: 48,
        textStyle: { color: '#94a3b8', fontSize: 11 },
        data: ['G_eff', 'F_con', 'C_bank', 'BO_bank', 'HLAP'],
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(2, 6, 23, 0.96)',
        borderColor: 'rgba(51, 65, 85, 0.75)',
        borderWidth: 1,
        textStyle: { color: '#f8fafc' },
        formatter: (params: unknown) => {
          type TooltipItem = {
            marker: string;
            seriesName: string;
            data: [number, number];
          };

          const items = Array.isArray(params) ? (params as TooltipItem[]) : [params as TooltipItem];
          const axisTime = items[0]?.data?.[0] ?? 0;
          let html = `<div style="font-weight:600;margin-bottom:6px;">Time ${axisTime.toFixed(2)} s</div>`;
          for (const item of items) {
            const value = item.data?.[1] ?? 0;
            const unit =
              item.seriesName === 'G_eff'
                ? 'G'
                : item.seriesName === 'F_con'
                  ? 'dl/min'
                  : item.seriesName === 'HLAP'
                    ? 'mmHg'
                    : 's';
            html += `<div style="display:flex;align-items:center;gap:6px;">${item.marker}<span>${item.seriesName}: ${value.toFixed(2)} ${unit}</span></div>`;
          }
          return html;
        },
      },
      grid: {
        left: 66,
        right: 160,
        top: 86,
        bottom: 62,
      },
      xAxis: {
        type: 'value',
        name: 'Time (s)',
        nameLocation: 'middle',
        nameGap: 34,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' } },
      },
      yAxis: [
        {
          type: 'value',
          name: 'G_eff (G)',
          min: geffMin,
          max: geffMax,
          position: 'left',
          axisLine: { lineStyle: { color: '#38bdf8' } },
          axisLabel: { color: '#7dd3fc', fontSize: 10 },
          splitLine: { lineStyle: { color: 'rgba(71, 85, 105, 0.16)', type: 'dashed' } },
          nameTextStyle: { color: '#7dd3fc', fontSize: 10 },
        },
        {
          type: 'value',
          name: 'F_con (dl/min)',
          min: 0,
          max: flowMax,
          position: 'right',
          axisLine: { lineStyle: { color: '#4ade80' } },
          axisLabel: { color: '#86efac', fontSize: 10 },
          splitLine: { show: false },
          nameTextStyle: { color: '#86efac', fontSize: 10 },
        },
        {
          type: 'value',
          name: 'Reserve (s)',
          min: 0,
          max: reserveMax,
          position: 'right',
          offset: 56,
          axisLine: { lineStyle: { color: '#fbbf24' } },
          axisLabel: { color: '#fcd34d', fontSize: 10 },
          splitLine: { show: false },
          nameTextStyle: { color: '#fcd34d', fontSize: 10 },
        },
        {
          type: 'value',
          name: 'HLAP (mmHg)',
          min: hlapMin,
          max: hlapMax,
          position: 'left',
          offset: 56,
          axisLine: { lineStyle: { color: '#c084fc' } },
          axisLabel: { color: '#d8b4fe', fontSize: 10 },
          splitLine: { show: false },
          nameTextStyle: { color: '#d8b4fe', fontSize: 10 },
        },
      ],
      series: [
        {
          name: 'G_eff',
          type: 'line',
          yAxisIndex: 0,
          data: sampledTimes.map((time, idx) => [time, sampledGeff[idx]]),
          symbol: 'none',
          smooth: 0.18,
          lineStyle: {
            width: seriesWidth('geff', 3.2, 1.8),
            color: '#38bdf8',
            opacity: seriesOpacity('geff'),
          },
          markLine: {
            symbol: 'none',
            silent: true,
            lineStyle: { type: 'dashed', width: 1.2, color: 'rgba(14, 165, 233, 0.6)' },
            label: { color: '#bae6fd', fontSize: 10 },
            data: [
              { yAxis: PHYSIOLOGICAL_THRESHOLDS.greyout_geff, label: { formatter: 'Greyout G_eff' } },
              { yAxis: PHYSIOLOGICAL_THRESHOLDS.blackout_geff, label: { formatter: 'Blackout G_eff' } },
              { yAxis: PHYSIOLOGICAL_THRESHOLDS.gloc_geff, label: { formatter: 'G-LOC G_eff' } },
            ],
          },
          markArea: {
            silent: true,
            data: markAreaData,
          },
        },
        {
          name: 'F_con',
          type: 'line',
          yAxisIndex: 1,
          data: sampledTimes.map((time, idx) => [time, sampledFlow[idx]]),
          symbol: 'none',
          smooth: 0.15,
          lineStyle: {
            width: seriesWidth('f_con', 2.8, 1.8),
            color: '#4ade80',
            opacity: seriesOpacity('f_con'),
          },
          markLine: {
            symbol: 'none',
            silent: true,
            lineStyle: { type: 'dashed', width: 1.1, color: 'rgba(34, 197, 94, 0.6)' },
            label: { color: '#86efac', fontSize: 10, formatter: 'F_con threshold' },
            data: [{ yAxis: 19 }],
          },
        },
        {
          name: 'C_bank',
          type: 'line',
          yAxisIndex: 2,
          data: sampledTimes.map((time, idx) => [time, sampledCBank[idx]]),
          symbol: 'none',
          smooth: true,
          lineStyle: {
            width: seriesWidth('c_bank', 2.8, 1.6),
            color: '#f59e0b',
            opacity: seriesOpacity('c_bank'),
          },
        },
        {
          name: 'BO_bank',
          type: 'line',
          yAxisIndex: 2,
          data: sampledTimes.map((time, idx) => [time, sampledBOBank[idx]]),
          symbol: 'none',
          smooth: true,
          lineStyle: {
            width: seriesWidth('bo_bank', 2.8, 1.6),
            color: '#fb7185',
            type: 'dashed',
            opacity: seriesOpacity('bo_bank'),
          },
        },
        {
          name: 'HLAP',
          type: 'line',
          yAxisIndex: 3,
          data: sampledTimes.map((time, idx) => [time, sampledHlap[idx]]),
          symbol: 'none',
          smooth: 0.15,
          lineStyle: {
            width: seriesWidth('hlap', 2.8, 1.4),
            color: '#a855f7',
            opacity: seriesOpacity('hlap'),
          },
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: 0,
          filterMode: 'none',
        },
        {
          type: 'slider',
          xAxisIndex: 0,
          height: 20,
          bottom: 10,
          borderColor: 'rgba(71, 85, 105, 0.35)',
          backgroundColor: 'rgba(15, 23, 42, 0.54)',
          fillerColor: 'rgba(56, 189, 248, 0.2)',
          handleStyle: { color: '#38bdf8' },
          textStyle: { color: '#94a3b8', fontSize: 10 },
        },
      ],
      animation: true,
      animationDuration: 720,
      animationEasing: 'cubicOut',
    };
  }, [focusVariable, result, title]);

  const duration = result.times_s.length ? Math.max(...result.times_s) - Math.min(...result.times_s) : 0;
  const summary = `Model dynamics over ${duration.toFixed(1)} seconds for effective G, cerebral flow, compensation, blackout, and hydrostatic pressure.`;
  return <BaseChart option={option} height={height} accessibleName={title} accessibleSummary={summary} />;
};

export default ModelDynamicsChart;
