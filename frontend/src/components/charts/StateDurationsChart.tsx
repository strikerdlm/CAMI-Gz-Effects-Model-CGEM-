/**
 * State Durations Bar Chart
 * 
 * Horizontal bar chart showing time spent in each physiological state.
 * Critical for safety assessment and risk quantification.
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import { STATE_COLORS } from '../../utils/constants';
import type { StateDurations, PhysiologicalState } from '../../types';

interface StateDurationsChartProps {
  durations: StateDurations;
  title?: string;
  height?: number;
}

const STATE_LABELS: Record<PhysiologicalState, string> = {
  normal: 'Normal',
  caution: 'Caution',
  greyout: 'Greyout',
  blackout: 'Blackout',
  gloc: 'G-LOC',
  redout: 'Redout',
};

export const StateDurationsChart: React.FC<StateDurationsChartProps> = ({
  durations,
  title = 'Time in Physiological States',
  height = 350,
}) => {
  const option = useMemo<ChartOption>(() => {
    const states: PhysiologicalState[] = ['normal', 'caution', 'greyout', 'blackout', 'gloc', 'redout'];
    const labels = states.map(s => STATE_LABELS[s]);
    const values = states.map(s => durations[s] || 0);
    const colors = states.map(s => STATE_COLORS[s]);
    const totalTime = values.reduce((sum, v) => sum + v, 0);

    return {
      backgroundColor: 'transparent',
      title: {
        text: title,
        subtext: `Total: ${totalTime.toFixed(1)}s`,
        left: 'center',
        top: 10,
        textStyle: {
          color: '#f1f5f9',
          fontSize: 16,
          fontWeight: 600,
        },
        subtextStyle: {
          color: '#94a3b8',
          fontSize: 12,
        },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        textStyle: { color: '#f1f5f9' },
        formatter: (params: { name: string; data: { value: number }; color: string }[]) => {
          const p = params[0];
          const percent = totalTime > 0 ? ((p.data.value / totalTime) * 100).toFixed(1) : '0';
          return `<div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:12px;height:12px;border-radius:2px;background:${p.color};"></span>
                    <span style="font-weight:600;">${p.name}</span>
                  </div>
                  <div>Duration: ${p.data.value.toFixed(2)}s</div>
                  <div>Percentage: ${percent}%</div>`;
        },
      },
      grid: {
        left: 80,
        right: 60,
        top: 70,
        bottom: 30,
      },
      xAxis: {
        type: 'value',
        name: 'Duration (s)',
        nameLocation: 'middle',
        nameGap: 25,
        nameTextStyle: { color: '#94a3b8', fontSize: 12 },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: {
          lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' },
        },
      },
      yAxis: {
        type: 'category',
        data: labels,
        axisLabel: { color: '#e2e8f0', fontSize: 12, fontWeight: 500 },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      series: [{
        type: 'bar',
        data: values.map((value, i) => ({
          value,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [
                { offset: 0, color: colors[i] },
                { offset: 1, color: `${colors[i]}88` },
              ],
            },
            borderRadius: [0, 4, 4, 0],
          },
        })),
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          color: '#94a3b8',
          fontSize: 11,
          formatter: (params: { value: number }) => 
            params.value > 0 ? `${params.value.toFixed(1)}s` : '',
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
          },
        },
      }],
      animation: true,
      animationDuration: 600,
    };
  }, [durations, title]);

  const summary = (Object.keys(STATE_LABELS) as PhysiologicalState[])
    .map((state) => `${STATE_LABELS[state]} ${(durations[state] || 0).toFixed(1)} seconds`)
    .join('; ') + '.';
  return <BaseChart option={option} height={height} accessibleName={title} accessibleSummary={summary} />;
};

export default StateDurationsChart;
