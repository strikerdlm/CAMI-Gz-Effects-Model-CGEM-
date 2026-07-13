/**
 * G-Force Distribution Histogram
 * 
 * Statistical distribution of G-force values throughout the maneuver.
 * Helps identify predominant G-loading patterns.
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import { calculateHistogram } from '../../utils/calculations';
import { PHYSIOLOGICAL_THRESHOLDS } from '../../utils/constants';

interface GDistributionChartProps {
  gValues: number[];
  title?: string;
  height?: number;
  bins?: number;
}

export const GDistributionChart: React.FC<GDistributionChartProps> = ({
  gValues,
  title = 'G-Force Distribution',
  height = 350,
  bins = 20,
}) => {
  const option = useMemo<ChartOption>(() => {
    if (!gValues || gValues.length === 0) {
      return {
        title: { text: title, left: 'center' },
        graphic: {
          type: 'text',
          left: 'center',
          top: 'middle',
          style: { text: 'No data available', fill: '#64748b' },
        },
      };
    }

    const { labels, counts } = calculateHistogram(gValues, bins);

    // Color bars based on G-force zone
    const getBarColor = (label: string): string => {
      const match = label.match(/([-\d.]+)/);
      if (!match) return '#3b82f6';
      const g = parseFloat(match[1]);
      
      if (g < PHYSIOLOGICAL_THRESHOLDS.redout_g) return '#ef4444';
      if (g < PHYSIOLOGICAL_THRESHOLDS.safe_g_range[0]) return '#f59e0b';
      if (g <= PHYSIOLOGICAL_THRESHOLDS.safe_g_range[1]) return '#22c55e';
      if (g <= PHYSIOLOGICAL_THRESHOLDS.trained_g_range[1]) return '#f59e0b';
      return '#ef4444';
    };

    const barColors = labels.map(getBarColor);

    return {
      backgroundColor: 'transparent',
      title: {
        text: title,
        left: 'center',
        top: 10,
        textStyle: {
          color: '#f1f5f9',
          fontSize: 16,
          fontWeight: 600,
        },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        textStyle: { color: '#f1f5f9' },
        formatter: (params: { name: string; data: number }[]) => {
          const p = params[0];
          return `<div style="font-weight:600;">G Range: ${p.name}</div>
                  <div>Samples: ${p.data}</div>`;
        },
      },
      grid: {
        left: 50,
        right: 30,
        top: 60,
        bottom: 80,
      },
      xAxis: {
        type: 'category',
        data: labels,
        name: 'G-Force Range',
        nameLocation: 'middle',
        nameGap: 50,
        nameTextStyle: { color: '#94a3b8', fontSize: 12 },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 9,
          rotate: 45,
          interval: Math.floor(labels.length / 10),
        },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      yAxis: {
        type: 'value',
        name: 'Count',
        nameLocation: 'middle',
        nameGap: 35,
        nameTextStyle: { color: '#94a3b8', fontSize: 12 },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: {
          lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' },
        },
      },
      series: [{
        type: 'bar',
        data: counts.map((count, i) => ({
          value: count,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: barColors[i] },
                { offset: 1, color: `${barColors[i]}99` },
              ],
            },
            borderRadius: [4, 4, 0, 0],
          },
        })),
        barWidth: '70%',
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
  }, [gValues, title, bins]);

  const min = gValues.length ? Math.min(...gValues) : 0;
  const max = gValues.length ? Math.max(...gValues) : 0;
  const summary = gValues.length
    ? `G-force values range from ${min.toFixed(1)} to ${max.toFixed(1)} G across ${bins} bins.`
    : 'No G-force distribution data available.';
  return <BaseChart option={option} height={height} accessibleName={title} accessibleSummary={summary} />;
};

export default GDistributionChart;
