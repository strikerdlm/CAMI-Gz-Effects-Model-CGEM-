/**
 * Scientific Dashboard Page
 * 
 * Publication-quality ECharts visualizations for aerospace physiology analysis.
 * Designed for Q1 science journal publication standards.
 */

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  LayoutGrid,
  Maximize2,
  LineChart,
  BarChart3,
  PieChart,
  Activity,
  Download,
} from 'lucide-react';

import { ProfileSelector, MetricCard } from '../components/ui';
import {
  GForceLineChart,
  PhysiologicalHeatmap,
  RadarSummaryChart,
  GDistributionChart,
  StateDurationsChart,
  CerebralFlowChart,
} from '../components/charts';
import { AEROBATIC_PROFILES, simulateCGEMResult } from '../services/mockData';
import { DEFAULT_COUNTERMEASURES } from '../utils/constants';
import { calculateProfileStats, computeStateDurations } from '../utils/calculations';
import { cn } from '../utils';
import type { PilotConfig, CGEMResult } from '../types';

type ViewMode = 'grid' | 'single';
type ChartType = 'lines' | 'heatmap' | 'radar' | 'histogram' | 'durations' | 'flows';

const CHART_OPTIONS: { id: ChartType; label: string; icon: React.ElementType }[] = [
  { id: 'lines', label: 'G-Force Lines', icon: LineChart },
  { id: 'heatmap', label: 'State Heatmap', icon: LayoutGrid },
  { id: 'radar', label: 'Risk Radar', icon: PieChart },
  { id: 'histogram', label: 'G Distribution', icon: BarChart3 },
  { id: 'durations', label: 'State Durations', icon: BarChart3 },
  { id: 'flows', label: 'Cerebral Flow', icon: Activity },
];

export const DashboardPage: React.FC = () => {
  const [selectedProfileId, setSelectedProfileId] = useState('high_g_turn');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedChart, setSelectedChart] = useState<ChartType>('lines');
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_isLoading, setIsLoading] = useState(false);

  const profile = AEROBATIC_PROFILES[selectedProfileId];
  const stats = useMemo(() => 
    profile ? calculateProfileStats(profile.samples) : null, 
    [profile]
  );

  // Run simulation for selected profile
  const result = useMemo<CGEMResult | null>(() => {
    if (!profile) return null;
    const config: PilotConfig = {
      who_profile: 2, // Default median male
      countermeasures: DEFAULT_COUNTERMEASURES,
    };
    return simulateCGEMResult(profile, config);
  }, [profile]);

  const durations = useMemo(() => {
    if (!result) return null;
    return computeStateDurations(result.times_s, result.g_values, result.geff_values);
  }, [result]);

  if (!profile || !stats || !result || !durations) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-surface-400">Loading dashboard data...</p>
      </div>
    );
  }

  const renderChart = (chartType: ChartType, height: number = 350) => {
    switch (chartType) {
      case 'lines':
        return (
          <GForceLineChart
            times={result.times_s}
            gValues={result.g_values}
            geffValues={result.geff_values}
            title="G-Force and Effective G vs Time"
            height={height}
          />
        );
      case 'heatmap':
        return (
          <PhysiologicalHeatmap
            result={result}
            title="Physiological State Timeline"
            height={height}
          />
        );
      case 'radar':
        return (
          <RadarSummaryChart
            result={result}
            stats={stats}
            title="Risk Assessment Radar"
            height={height}
          />
        );
      case 'histogram':
        return (
          <GDistributionChart
            gValues={result.g_values}
            title="G-Force Distribution"
            height={height}
          />
        );
      case 'durations':
        return (
          <StateDurationsChart
            durations={durations}
            title="Time in Physiological States"
            height={height}
          />
        );
      case 'flows':
        return (
          <CerebralFlowChart
            result={result}
            title="Cerebral Blood Flow Dynamics"
            height={height}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Scientific Visualization Dashboard
            </h2>
            <p className="text-surface-400 max-w-2xl">
              Publication-quality ECharts for aerospace physiology research.
              Export charts in SVG/PNG format for journal submissions.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* View Mode Toggle */}
            <div className="flex items-center gap-1 p-1 bg-surface-800/80 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'p-2 rounded-lg transition-all',
                  viewMode === 'grid' 
                    ? 'bg-primary-500/20 text-primary-400' 
                    : 'text-surface-400 hover:text-white'
                )}
                title="Grid View"
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('single')}
                className={cn(
                  'p-2 rounded-lg transition-all',
                  viewMode === 'single' 
                    ? 'bg-primary-500/20 text-primary-400' 
                    : 'text-surface-400 hover:text-white'
                )}
                title="Single Chart"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>

            <button className="btn-secondary">
              <Download className="w-4 h-4" />
              Export All
            </button>
          </div>
        </div>

        {/* Profile Selector */}
        <div className="mt-6 flex items-center gap-4">
          <ProfileSelector
            selectedProfileId={selectedProfileId}
            onSelect={(id) => {
              setIsLoading(true);
              setSelectedProfileId(id);
              setTimeout(() => setIsLoading(false), 300);
            }}
            className="max-w-md"
          />
        </div>
      </motion.div>

      {/* Quick Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricCard
          label="Max G"
          value={`+${Math.max(...result.g_values).toFixed(1)}`}
          unit="G"
          size="sm"
        />
        <MetricCard
          label="Max G_eff"
          value={Math.max(...result.geff_values).toFixed(1)}
          unit="G"
          size="sm"
        />
        <MetricCard
          label="Duration"
          value={result.times_s[result.times_s.length - 1].toFixed(1)}
          unit="s"
          size="sm"
        />
        <MetricCard
          label="Greyout"
          value={result.time_to_greyout_s?.toFixed(2) || '—'}
          unit="s"
          size="sm"
          color={result.time_to_greyout_s ? 'warning' : 'default'}
        />
        <MetricCard
          label="Blackout"
          value={result.time_to_blackout_s?.toFixed(2) || '—'}
          unit="s"
          size="sm"
          color={result.time_to_blackout_s ? 'danger' : 'default'}
        />
        <MetricCard
          label="G-LOC"
          value={result.time_to_gloc_s?.toFixed(2) || '—'}
          unit="s"
          size="sm"
          color={result.time_to_gloc_s ? 'danger' : 'default'}
        />
      </div>

      {/* Chart Selection (Single View) */}
      {viewMode === 'single' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap gap-2"
        >
          {CHART_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              onClick={() => setSelectedChart(opt.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
                selectedChart === opt.id
                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                  : 'bg-surface-800/60 text-surface-400 hover:text-white hover:bg-surface-800'
              )}
            >
              <opt.icon className="w-4 h-4" />
              {opt.label}
            </button>
          ))}
        </motion.div>
      )}

      {/* Charts */}
      {viewMode === 'grid' ? (
        <div className="grid md:grid-cols-2 gap-6">
          {CHART_OPTIONS.map((opt, index) => (
            <motion.div
              key={opt.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="chart-container"
            >
              <div className="chart-title">
                <opt.icon className="w-5 h-5 text-primary-400" />
                {opt.label}
              </div>
              {renderChart(opt.id, 320)}
            </motion.div>
          ))}
        </div>
      ) : (
        <motion.div
          key={selectedChart}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="chart-container"
        >
          <div className="chart-title text-lg">
            {CHART_OPTIONS.find(o => o.id === selectedChart)?.icon && (
              React.createElement(
                CHART_OPTIONS.find(o => o.id === selectedChart)!.icon,
                { className: 'w-6 h-6 text-primary-400' }
              )
            )}
            {CHART_OPTIONS.find(o => o.id === selectedChart)?.label}
          </div>
          {renderChart(selectedChart, 550)}
        </motion.div>
      )}

      {/* Citation Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="glass-light rounded-xl p-4"
      >
        <h4 className="text-sm font-semibold text-surface-300 mb-2">
          Suggested Citation
        </h4>
        <p className="text-xs text-surface-400 font-mono bg-surface-800/50 p-3 rounded-lg">
          Dashboard generated using G-Effects Safety Management System based on CGEM v1.1.0.1.
          Model reference: Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow-based 
          computer modeling of Gz-induced effects (DOT/FAA/AM-23/6). Office of Aerospace Medicine, 
          FAA. DOI: https://doi.org/10.21949/1524446
        </p>
      </motion.div>
    </div>
  );
};

export default DashboardPage;
