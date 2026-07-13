/**
 * Radar Summary Chart
 * 
 * Multi-dimensional radar visualization of key physiological metrics.
 * Provides at-a-glance risk assessment for aerospace physiology.
 */

import React, { useMemo } from 'react';
import { BaseChart, type ChartOption } from './BaseChart';
import type { CGEMResult, ProfileStats } from '../../types';
import { computeStateDurations } from '../../utils/calculations';

interface RadarSummaryChartProps {
  result: CGEMResult;
  stats: ProfileStats;
  title?: string;
  height?: number;
}

export const RadarSummaryChart: React.FC<RadarSummaryChartProps> = ({
  result,
  stats,
  title = 'Physiological Risk Summary',
  height = 400,
}) => {
  const option = useMemo<ChartOption>(() => {
    const { times_s, g_values, geff_values } = result;
    
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

    const durations = computeStateDurations(times_s, g_values, geff_values);
    const maxG = Math.max(...g_values.map(Math.abs));
    const maxGeff = Math.max(...geff_values);
    const timeAtRisk = durations.greyout + durations.blackout + durations.gloc;

    // Define radar indicators (max values for normalization)
    const indicators = [
      { name: 'Max |G|', max: Math.max(10, Math.ceil(maxG * 1.2)) },
      { name: 'Max G_eff', max: Math.max(8, Math.ceil(maxGeff * 1.2)) },
      { name: 'Time at Risk (s)', max: Math.max(5, Math.ceil(timeAtRisk * 1.5)) },
      { name: '+G Dose (G·s)', max: Math.max(50, Math.ceil(stats.positive_g_dose * 1.2)) },
      { name: 'RMS G', max: Math.max(5, Math.ceil(stats.rms_g * 1.5)) },
    ];

    const values = [
      maxG,
      maxGeff,
      timeAtRisk,
      stats.positive_g_dose,
      stats.rms_g,
    ];

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
        trigger: 'item',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        textStyle: { color: '#f1f5f9' },
      },
      legend: {
        data: ['Current Profile'],
        bottom: 10,
        textStyle: { color: '#94a3b8' },
      },
      radar: {
        center: ['50%', '55%'],
        radius: '65%',
        startAngle: 90,
        splitNumber: 4,
        shape: 'polygon',
        indicator: indicators,
        axisName: {
          color: '#e2e8f0',
          fontSize: 11,
          fontWeight: 500,
        },
        splitArea: {
          areaStyle: {
            color: [
              'rgba(34, 197, 94, 0.05)',
              'rgba(251, 191, 36, 0.05)',
              'rgba(249, 115, 22, 0.05)',
              'rgba(239, 68, 68, 0.05)',
            ],
          },
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(71, 85, 105, 0.3)',
          },
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(71, 85, 105, 0.4)',
          },
        },
      },
      series: [{
        name: 'Risk Profile',
        type: 'radar',
        data: [{
          value: values,
          name: 'Current Profile',
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#3b82f6',
          },
          lineStyle: {
            width: 2,
            color: '#3b82f6',
          },
          areaStyle: {
            color: {
              type: 'radial',
              x: 0.5,
              y: 0.5,
              r: 0.5,
              colorStops: [
                { offset: 0, color: 'rgba(59, 130, 246, 0.4)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0.1)' },
              ],
            },
          },
        }],
      }],
      animation: true,
      animationDuration: 800,
    };
  }, [result, stats, title]);

  const peakG = result.g_values.length ? Math.max(...result.g_values.map(Math.abs)) : 0;
  const peakGeff = result.geff_values.length ? Math.max(...result.geff_values.map(Math.abs)) : 0;
  const summary = `Risk profile: peak absolute G ${peakG.toFixed(1)}, peak effective G ${peakGeff.toFixed(1)}, positive G dose ${stats.positive_g_dose.toFixed(1)} G-seconds, RMS G ${stats.rms_g.toFixed(1)}.`;
  return <BaseChart option={option} height={height} accessibleName={title} accessibleSummary={summary} />;
};

export default RadarSummaryChart;
