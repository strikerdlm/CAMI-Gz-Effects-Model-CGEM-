/**
 * Cerebral Blood Flow Chart
 * 
 * Multi-series visualization of blood flow to critical brain regions.
 * Based on CGEM model outputs (F_con, F_vis, F_bo).
 * 
 * References:
 * - Copeland & Whinnery (2023). DOT/FAA/AM-23/6
 * - Ryoo et al. (2004). Medical Engineering & Physics, 26(9), 745-753
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import type { CGEMResult } from '../../types';

interface CerebralFlowChartProps {
  result: CGEMResult;
  title?: string;
  height?: number;
}

export const CerebralFlowChart: React.FC<CerebralFlowChartProps> = ({
  result,
  title = 'Cerebral Blood Flow',
  height = 400,
}) => {
  const option = useMemo<ChartOption>(() => {
    const { times_s, f_con_values, f_vis_values, f_bo_values } = result;

    if (!times_s || times_s.length === 0) {
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

    // Downsample if too many points
    const maxPoints = 500;
    const step = Math.max(1, Math.floor(times_s.length / maxPoints));
    
    const sampledTimes = times_s.filter((_, i) => i % step === 0);
    const sampledFcon = f_con_values.filter((_, i) => i % step === 0);
    const sampledFvis = f_vis_values.filter((_, i) => i % step === 0);
    const sampledFbo = f_bo_values.filter((_, i) => i % step === 0);

    // Flow thresholds (typical values from CGEM)
    const consciousnessThreshold = 19; // dl/min
    const visionThreshold = 25; // dl/min

    return {
      backgroundColor: 'transparent',
      title: {
        text: title,
        subtext: 'F_con: Consciousness | F_vis: Vision | F_bo: Blackout',
        left: 'center',
        top: 10,
        textStyle: {
          color: '#f1f5f9',
          fontSize: 16,
          fontWeight: 600,
        },
        subtextStyle: {
          color: '#94a3b8',
          fontSize: 11,
        },
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        textStyle: { color: '#f1f5f9' },
        formatter: (params: { data: [number, number]; seriesName: string; color: string }[]) => {
          const time = params[0]?.data[0]?.toFixed(2) || '0';
          let html = `<div style="font-weight:600;margin-bottom:4px;">Time: ${time}s</div>`;
          for (const item of params) {
            const value = item.data[1]?.toFixed(1) || '0';
            html += `<div style="display:flex;align-items:center;gap:6px;">
              <span style="width:10px;height:10px;border-radius:50%;background:${item.color};"></span>
              <span>${item.seriesName}: ${value} dl/min</span>
            </div>`;
          }
          return html;
        },
      },
      legend: {
        data: ['F_con (Consciousness)', 'F_vis (Vision)', 'F_bo (Blackout)'],
        top: 50,
        textStyle: { color: '#94a3b8', fontSize: 11 },
      },
      grid: {
        left: 60,
        right: 40,
        top: 90,
        bottom: 60,
      },
      xAxis: {
        type: 'value',
        name: 'Time (s)',
        nameLocation: 'middle',
        nameGap: 35,
        nameTextStyle: { color: '#94a3b8', fontSize: 12 },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: {
          lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' },
        },
      },
      yAxis: {
        type: 'value',
        name: 'Flow (dl/min)',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { color: '#94a3b8', fontSize: 12 },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: {
          lineStyle: { color: 'rgba(71, 85, 105, 0.2)', type: 'dashed' },
        },
        min: 0,
      },
      series: [
        {
          name: 'F_con (Consciousness)',
          type: 'line',
          data: sampledTimes.map((t, i) => [t, sampledFcon[i]]),
          symbol: 'none',
          lineStyle: { width: 2.5, color: '#3b82f6' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(59, 130, 246, 0.25)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0)' },
              ],
            },
          },
        },
        {
          name: 'F_vis (Vision)',
          type: 'line',
          data: sampledTimes.map((t, i) => [t, sampledFvis[i]]),
          symbol: 'none',
          lineStyle: { width: 2, color: '#22c55e' },
        },
        {
          name: 'F_bo (Blackout)',
          type: 'line',
          data: sampledTimes.map((t, i) => [t, sampledFbo[i]]),
          symbol: 'none',
          lineStyle: { width: 2, color: '#f59e0b', type: 'dashed' },
        },
      ],
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', width: 1.5 },
        data: [
          {
            yAxis: consciousnessThreshold,
            lineStyle: { color: 'rgba(239, 68, 68, 0.6)' },
            label: {
              formatter: 'LOC Threshold',
              color: '#ef4444',
              fontSize: 10,
            },
          },
          {
            yAxis: visionThreshold,
            lineStyle: { color: 'rgba(251, 191, 36, 0.6)' },
            label: {
              formatter: 'Vision Threshold',
              color: '#fbbf24',
              fontSize: 10,
            },
          },
        ],
      },
      dataZoom: [
        { type: 'inside', xAxisIndex: 0 },
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
    };
  }, [result, title]);

  return <BaseChart option={option} height={height} />;
};

export default CerebralFlowChart;
