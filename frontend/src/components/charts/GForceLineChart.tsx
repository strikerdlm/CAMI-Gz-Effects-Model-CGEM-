/**
 * G-Force Line Chart
 * 
 * Publication-quality visualization of G-force profiles over time
 * with physiological threshold zones and effective G overlay.
 * 
 * References:
 * - Whinnery & Forster (2015). Visual Neuroscience, 32, E008
 * - Tripp et al. (2009). Human Factors, 51(6), 775-784
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import { PHYSIOLOGICAL_THRESHOLDS } from '../../utils/constants';

interface GForceLineChartProps {
  times: number[];
  gValues: number[];
  geffValues?: number[];
  title?: string;
  height?: number;
  showThresholds?: boolean;
  showZones?: boolean;
}

export const GForceLineChart: React.FC<GForceLineChartProps> = ({
  times,
  gValues,
  geffValues,
  title = 'G-Force Profile',
  height = 400,
  showThresholds = true,
  showZones = true,
}) => {
  const option = useMemo<ChartOption>(() => {
    const minG = Math.min(...gValues, ...(geffValues || []), -3);
    const maxG = Math.max(...gValues, ...(geffValues || []), 8);

    // Create visual zones for physiological states
    const visualMapPieces = showZones ? [
      { gt: PHYSIOLOGICAL_THRESHOLDS.trained_g_range[1], color: 'rgba(239, 68, 68, 0.15)' },
      { gte: PHYSIOLOGICAL_THRESHOLDS.safe_g_range[1], lte: PHYSIOLOGICAL_THRESHOLDS.trained_g_range[1], color: 'rgba(251, 191, 36, 0.1)' },
      { gte: PHYSIOLOGICAL_THRESHOLDS.safe_g_range[0], lt: PHYSIOLOGICAL_THRESHOLDS.safe_g_range[1], color: 'rgba(34, 197, 94, 0.08)' },
      { gte: PHYSIOLOGICAL_THRESHOLDS.redout_g, lt: PHYSIOLOGICAL_THRESHOLDS.safe_g_range[0], color: 'rgba(251, 191, 36, 0.1)' },
      { lt: PHYSIOLOGICAL_THRESHOLDS.redout_g, color: 'rgba(239, 68, 68, 0.15)' },
    ] : undefined;

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
          fontFamily: 'Inter, system-ui, sans-serif',
        },
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        borderWidth: 1,
        textStyle: { color: '#f1f5f9' },
        formatter: (params: unknown) => {
          const p = params as { data: [number, number]; seriesName: string }[];
          const time = p[0]?.data[0]?.toFixed(2) || '0';
          let html = `<div style="font-weight:600;margin-bottom:4px;">Time: ${time}s</div>`;
          for (const item of p) {
            const value = item.data[1]?.toFixed(2) || '0';
            const color = item.seriesName === 'G-Force' ? '#3b82f6' : '#22c55e';
            html += `<div style="display:flex;align-items:center;gap:6px;">
              <span style="width:10px;height:10px;border-radius:50%;background:${color};"></span>
              <span>${item.seriesName}: ${value}G</span>
            </div>`;
          }
          return html;
        },
      },
      legend: {
        data: geffValues ? ['G-Force', 'G_eff'] : ['G-Force'],
        top: 40,
        textStyle: { color: '#94a3b8' },
      },
      grid: {
        left: 60,
        right: 40,
        top: 80,
        bottom: 60,
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        name: 'Time (s)',
        nameLocation: 'middle',
        nameGap: 35,
        nameTextStyle: {
          color: '#94a3b8',
          fontSize: 12,
          fontWeight: 500,
        },
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        splitLine: {
          lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' },
        },
        min: 0,
        max: Math.ceil(Math.max(...times)),
      },
      yAxis: {
        type: 'value',
        name: 'G-Force',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: {
          color: '#94a3b8',
          fontSize: 12,
          fontWeight: 500,
        },
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 11,
          formatter: (value: number) => `${value > 0 ? '+' : ''}${value}`,
        },
        splitLine: {
          lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' },
        },
        min: Math.floor(minG) - 1,
        max: Math.ceil(maxG) + 1,
      },
      visualMap: showZones ? {
        show: false,
        dimension: 1,
        pieces: visualMapPieces,
        seriesIndex: 0,
      } : undefined,
      series: [
        {
          name: 'G-Force',
          type: 'line',
          data: times.map((t, i) => [t, gValues[i]]),
          symbol: 'none',
          lineStyle: {
            width: 3,
            color: '#3b82f6',
          },
          areaStyle: showZones ? {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                { offset: 0.5, color: 'rgba(59, 130, 246, 0.1)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0)' },
              ],
            },
          } : undefined,
          markLine: showThresholds ? {
            silent: true,
            symbol: 'none',
            lineStyle: { type: 'dashed', width: 1.5 },
            label: {
              position: 'end',
              fontSize: 10,
              fontWeight: 500,
            },
            data: [
              {
                yAxis: 0,
                lineStyle: { color: 'rgba(148, 163, 184, 0.5)' },
                label: { formatter: '0G', color: '#94a3b8' },
              },
              {
                yAxis: PHYSIOLOGICAL_THRESHOLDS.safe_g_range[1],
                lineStyle: { color: 'rgba(251, 191, 36, 0.6)' },
                label: { formatter: '+4 G reference', color: '#fbbf24' },
              },
              {
                yAxis: PHYSIOLOGICAL_THRESHOLDS.redout_g,
                lineStyle: { color: 'rgba(239, 68, 68, 0.6)' },
                label: { formatter: 'Redout', color: '#ef4444' },
              },
            ],
          } : undefined,
        },
        ...(geffValues ? [{
          name: 'G_eff',
          type: 'line' as const,
          data: times.map((t, i) => [t, geffValues[i]]),
          symbol: 'none',
          lineStyle: {
            width: 2.5,
            color: '#22c55e',
            type: 'dashed',
          },
        }] : []),
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
          borderColor: 'rgba(71, 85, 105, 0.3)',
          backgroundColor: 'rgba(15, 23, 42, 0.5)',
          fillerColor: 'rgba(59, 130, 246, 0.2)',
          handleStyle: { color: '#3b82f6' },
          textStyle: { color: '#94a3b8', fontSize: 10 },
        },
      ],
      animation: true,
      animationDuration: 800,
      animationEasing: 'cubicOut',
    };
  }, [times, gValues, geffValues, title, showThresholds, showZones]);

  return <BaseChart option={option} height={height} />;
};

export default GForceLineChart;
