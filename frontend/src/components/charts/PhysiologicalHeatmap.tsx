/**
 * Physiological State Heatmap
 * 
 * Temporal heatmap showing physiological parameter status over time.
 * Designed for publication-quality output in aerospace medicine journals.
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import type { CGEMResult } from '../../types';

interface PhysiologicalHeatmapProps {
  result: CGEMResult;
  title?: string;
  height?: number;
}

export const PhysiologicalHeatmap: React.FC<PhysiologicalHeatmapProps> = ({
  result,
  title = 'Physiological State Timeline',
  height = 300,
}) => {
  const option = useMemo<ChartOption>(() => {
    const { times_s, flags_n2, flags_ne2, flags_non2 } = result;
    
    if (!times_s || times_s.length === 0) {
      return {
        title: { text: title, left: 'center' },
        graphic: {
          type: 'text',
          left: 'center',
          top: 'middle',
          style: {
            text: 'No data available',
            fill: '#64748b',
            fontSize: 14,
          },
        },
      };
    }

    const parameters = ['Consciousness', 'Vision', 'Blackout'];
    
    // Build heatmap data: [timeIndex, paramIndex, value]
    const data: [number, number, number][] = [];
    
    // Sample every nth point to avoid overcrowding
    const sampleRate = Math.max(1, Math.floor(times_s.length / 100));
    
    for (let i = 0; i < times_s.length; i += sampleRate) {
      // Consciousness (inverted: 0 = conscious = green)
      data.push([i, 0, flags_n2[i] === 0 ? 1 : 0]);
      // Vision (inverted: 0 = normal = green)
      data.push([i, 1, flags_ne2[i] === 0 ? 1 : 0]);
      // Blackout (inverted: 0 = no blackout = green)
      data.push([i, 2, flags_non2[i] === 0 ? 1 : 0]);
    }

    const timeLabels = times_s
      .filter((_, i) => i % sampleRate === 0)
      .map(t => t.toFixed(1));

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
        position: 'top',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        textStyle: { color: '#f1f5f9' },
        formatter: (params: { data: [number, number, number] }) => {
          const [timeIdx, paramIdx, value] = params.data;
          const time = timeLabels[Math.floor(timeIdx / sampleRate)] || '0';
          const param = parameters[paramIdx];
          const status = value === 1 ? 'Normal' : 'Impaired';
          const color = value === 1 ? '#22c55e' : '#ef4444';
          return `<div style="font-weight:600;">${param}</div>
                  <div>Time: ${time}s</div>
                  <div style="color:${color};font-weight:500;">${status}</div>`;
        },
      },
      grid: {
        left: 100,
        right: 40,
        top: 60,
        bottom: 50,
      },
      xAxis: {
        type: 'category',
        data: timeLabels,
        name: 'Time (s)',
        nameLocation: 'middle',
        nameGap: 30,
        nameTextStyle: { color: '#94a3b8', fontSize: 12 },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 10,
          interval: Math.floor(timeLabels.length / 10),
        },
        splitLine: { show: false },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      yAxis: {
        type: 'category',
        data: parameters,
        axisLabel: { color: '#e2e8f0', fontSize: 12 },
        axisLine: { lineStyle: { color: '#475569' } },
        splitLine: { show: false },
      },
      visualMap: {
        show: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 5,
        min: 0,
        max: 1,
        calculable: false,
        inRange: {
          color: ['#ef4444', '#22c55e'],
        },
        textStyle: { color: '#94a3b8', fontSize: 10 },
        text: ['Normal', 'Impaired'],
      },
      series: [{
        type: 'heatmap',
        data: data,
        itemStyle: {
          borderColor: 'rgba(15, 23, 42, 0.8)',
          borderWidth: 1,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      }],
      animation: true,
      animationDuration: 600,
    };
  }, [result, title]);

  const impaired = (flags: number[]) => flags.filter((flag) => flag > 0).length;
  const summary = `Timeline with ${result.times_s.length} samples: consciousness impaired ${impaired(result.flags_n2)} samples; vision impaired ${impaired(result.flags_ne2)} samples; blackout ${impaired(result.flags_non2)} samples.`;
  return <BaseChart option={option} height={height} accessibleName={title} accessibleSummary={summary} />;
};

export default PhysiologicalHeatmap;
