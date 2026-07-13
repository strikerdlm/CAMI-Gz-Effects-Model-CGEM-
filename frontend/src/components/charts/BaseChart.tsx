/**
 * Base ECharts Component
 * 
 * Wrapper for ECharts with dark theme configuration optimized
 * for scientific publications in aerospace medicine.
 */

import React, { useRef, useEffect, useId } from 'react';
import * as echarts from 'echarts';
import { cn } from '../../utils';
import { ECHARTS_DARK_THEME } from '../../utils/constants';

// Using Record type for flexible ECharts options
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ChartOption = Record<string, any>;

export interface BaseChartProps {
  option: ChartOption;
  accessibleName: string;
  accessibleSummary: string;
  height?: number | string;
  className?: string;
  onChartReady?: (chart: echarts.ECharts) => void;
  loading?: boolean;
  notMerge?: boolean;
}

export const BaseChart: React.FC<BaseChartProps> = ({
  option,
  accessibleName,
  accessibleSummary,
  height = 400,
  className,
  onChartReady,
  loading = false,
  notMerge = false,
}) => {
  const summaryId = useId();
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize chart
    chartInstance.current = echarts.init(chartRef.current, undefined, {
      renderer: 'canvas',
    });
    chartRef.current.querySelectorAll('canvas').forEach((canvas) => {
      canvas.tabIndex = -1;
      canvas.setAttribute('aria-hidden', 'true');
    });

    // Apply base theme
    chartInstance.current.setOption({
      backgroundColor: 'transparent',
      textStyle: ECHARTS_DARK_THEME.textStyle,
      title: ECHARTS_DARK_THEME.title,
      legend: ECHARTS_DARK_THEME.legend,
      tooltip: ECHARTS_DARK_THEME.tooltip,
    });

    if (onChartReady) {
      onChartReady(chartInstance.current);
    }

    // Handle resize
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [onChartReady]);

  // Update chart options
  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.setOption(option, notMerge);
      
      if (loading) {
        chartInstance.current.showLoading({
          text: 'Loading...',
          color: '#0ea5e9',
          textColor: '#e2e8f0',
          maskColor: 'rgba(15, 23, 42, 0.8)',
        });
      } else {
        chartInstance.current.hideLoading();
      }
    }
  }, [option, loading, notMerge]);

  return (
    <div
      ref={chartRef}
      role="img"
      aria-label={accessibleName}
      aria-describedby={summaryId}
      className={cn('echarts-container', className)}
      style={{ height: typeof height === 'number' ? `${height}px` : height }}
    >
      <span id={summaryId} className="sr-only">{accessibleSummary}</span>
    </div>
  );
};

export default BaseChart;
