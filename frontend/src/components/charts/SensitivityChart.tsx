/**
 * Sobol sensitivity bar chart for one target.
 *
 * Pulls precomputed Sobol indices from the FastAPI service via
 * GET /sensitivity/{target} (data sourced from
 * data/results/sensitivity/sobol_first_total.csv on the server).
 */

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';
import { apiErrorMessage, useSensitivity } from '../../services/cgemApi';
import { useUserPrefs } from '../../state/useUserPrefs';
import type { TargetName } from '../../services/types';

interface SensitivityChartProps {
  target: TargetName;
  height?: number;
}

const FEATURE_LABELS: Record<string, string> = {
  g_peak_abs: 'G peak |Nz|',
  dgdt_max_g_per_s: 'dG/dt max',
  profile_duration_s: 'Profile duration',
  dehydration_level: 'Dehydration',
  g_tolerance_multiplier: 'G-tolerance',
  gsuit_max_psi: 'G-suit PSI',
  gsuit_coverage_fraction: 'G-suit coverage',
  agsm_effectiveness: 'AGSM',
  pbg_max_mmhg: 'PBG max',
};

export const SensitivityChart: React.FC<SensitivityChartProps> = ({ target, height = 360 }) => {
  const query = useSensitivity(target);
  const prefs = useUserPrefs();

  if (query.isLoading) {
    return (
      <div className="flex items-center justify-center text-surface-400" style={{ height }}>
        Loading sensitivity for {target}…
      </div>
    );
  }
  if (query.isError || !query.data) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-3 text-rose-400 text-sm text-center px-4"
        style={{ height }}
      >
        <p className="font-medium">Sensitivity request failed for {target}.</p>
        <p className="text-surface-400 max-w-xl">
          {query.error ? apiErrorMessage(query.error) : 'No sensitivity data was returned.'}
        </p>
        <p className="text-xs text-surface-500">
          API: <code className="text-surface-300">{prefs.apiUrl}</code>
        </p>
        <button
          type="button"
          onClick={() => void query.refetch()}
          disabled={query.isFetching}
          className="btn-secondary px-4 py-2"
        >
          {query.isFetching ? 'Retrying…' : 'Retry sensitivity'}
        </button>
      </div>
    );
  }

  // Sort features by ST (descending) for the headline ranking.
  const sorted = [...query.data.indices].sort((a, b) => b.ST - a.ST);
  const labels = sorted.map((r) => FEATURE_LABELS[r.feature] ?? r.feature);

  const option = {
    backgroundColor: 'transparent',
    grid: { left: '15%', right: '8%', top: '12%', bottom: '8%' },
    title: {
      text: `Sobol indices — ${target}`,
      subtext: `Fixed ${query.data.fixed_who_profile} arm · n_base=${query.data.sobol_n_base}`,
      textStyle: { color: '#e5e7eb', fontSize: 14, fontWeight: 600 },
      subtextStyle: { color: '#9ca3af', fontSize: 11 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#475569',
      textStyle: { color: '#e5e7eb' },
      formatter: (params: { name: string; value: number; seriesName: string }[]) => {
        if (!params || params.length === 0) return '';
        const name = params[0]?.name;
        const lines = params.map(
          (p) => `<span style="color:#cbd5e1">${p.seriesName}</span>: ${p.value.toFixed(3)}`,
        );
        return `<strong>${name}</strong><br/>${lines.join('<br/>')}`;
      },
    },
    legend: {
      data: ['First-order (S1)', 'Total-order (ST)'],
      textStyle: { color: '#cbd5e1' },
      top: 32,
    },
    xAxis: {
      type: 'value',
      max: 1.05,
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155', opacity: 0.4 } },
    },
    yAxis: {
      type: 'category',
      data: labels.slice().reverse(),
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#cbd5e1', fontSize: 12 },
    },
    series: [
      {
        name: 'First-order (S1)',
        type: 'bar',
        data: sorted.map((r) => r.S1).reverse(),
        itemStyle: { color: '#0ea5e9' },
        barGap: 0,
      },
      {
        name: 'Total-order (ST)',
        type: 'bar',
        data: sorted.map((r) => r.ST).reverse(),
        itemStyle: { color: '#a855f7' },
      },
    ],
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <ReactECharts option={option} style={{ height, width: '100%' }} />
    </motion.div>
  );
};

export default SensitivityChart;
