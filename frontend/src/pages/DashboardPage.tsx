/**
 * Scientific Dashboard Page
 * 
 * Publication-quality ECharts visualizations for aerospace physiology analysis.
 * Designed for Q1 science journal publication standards.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutGrid,
  Maximize2,
  LineChart,
  BarChart3,
  PieChart,
  Activity,
  Download,
  Brain,
  Shield,
  Star,
} from 'lucide-react';

import { MetricCard, ProfileSelector, VariableInsightsPanel } from '../components/ui';
import {
  ModelDynamicsChart,
  GForceLineChart,
  PhysiologicalHeatmap,
  RadarSummaryChart,
  GDistributionChart,
  StateDurationsChart,
  CerebralFlowChart,
  type ModelVariableKey,
} from '../components/charts';
import { MANEUVERS_BY_ID } from '../data/maneuvers';
import { DEFAULT_COUNTERMEASURES } from '../utils/constants';
import {
  cgemApiBaseURL,
  useHealth,
  useRunCgem,
  useVersion,
  apiErrorMessage,
} from '../services/cgemApi';
import { adaptCgemRun } from '../services/runCgemAdapter';
import { calculateProfileStats, computeStateDurations } from '../utils/calculations';
import { cn } from '../utils';
import type { CGEMResult, Countermeasures } from '../types';
import type { RunCGEMRequest, PilotConfigRequest } from '../services/types';
import { pilotConfigFromPrefs, pilotConfigWithOverrides } from '../services/pilotConfig';
import { useUserPrefs } from '../state/useUserPrefs';
import { dashboardUrlState, type DashboardChart, type DashboardLayout, type DashboardPreset } from '../services/urlState';

type ViewMode = DashboardLayout;
type ChartType = DashboardChart;

const CHART_OPTIONS: { id: ChartType; label: string; icon: React.ElementType }[] = [
  { id: 'lines', label: 'G-Force Lines', icon: LineChart },
  { id: 'heatmap', label: 'State Heatmap', icon: LayoutGrid },
  { id: 'radar', label: 'Risk Radar', icon: PieChart },
  { id: 'histogram', label: 'G Distribution', icon: BarChart3 },
  { id: 'durations', label: 'State Durations', icon: BarChart3 },
  { id: 'flows', label: 'Cerebral Flow', icon: Activity },
];

interface PilotPreset {
  id: DashboardPreset;
  label: string;
  summary: string;
  whoProfile: number;
  tag: 'balanced' | 'aggressive' | 'protected' | 'degraded';
  countermeasureOverrides: Partial<Countermeasures>;
}

const PILOT_PRESETS: PilotPreset[] = [
  {
    id: 'elite_balanced',
    label: 'Elite Balanced',
    summary: 'Standard profile 2 with moderate AGSM and G-suit support.',
    whoProfile: 2,
    tag: 'balanced',
    countermeasureOverrides: {
      agsm_effectiveness: 0.45,
      gsuit_max_psi: 3.0,
    },
  },
  {
    id: 'aggressive_sortie',
    label: 'Aggressive Sortie',
    summary: 'High maneuver stress with limited protection margin.',
    whoProfile: 3,
    tag: 'aggressive',
    countermeasureOverrides: {
      agsm_effectiveness: 0.25,
      gsuit_max_psi: 1.5,
    },
  },
  {
    id: 'max_protection',
    label: 'Max Protection',
    summary: 'High reserve profile with tuned G-suit and strong AGSM.',
    whoProfile: 1,
    tag: 'protected',
    countermeasureOverrides: {
      agsm_effectiveness: 0.7,
      gsuit_max_psi: 5.0,
    },
  },
  {
    id: 'degraded_state',
    label: 'Degraded State',
    summary: 'Standard profile 6 with limited active protection.',
    whoProfile: 6,
    tag: 'degraded',
    countermeasureOverrides: {
      agsm_effectiveness: 0.1,
      gsuit_max_psi: 0.5,
    },
  },
];

const PRESET_STYLES: Record<PilotPreset['tag'], string> = {
  balanced: 'border-primary-500/35 bg-primary-500/10 text-primary-300',
  aggressive: 'border-warning-500/35 bg-warning-500/10 text-warning-300',
  protected: 'border-accent-500/35 bg-accent-500/10 text-accent-300',
  degraded: 'border-danger-500/35 bg-danger-500/10 text-danger-300',
};

const ApiStatusBanner: React.FC = () => {
  const versionQuery = useVersion();
  const status = versionQuery.isLoading
    ? { label: 'connecting…', color: 'text-amber-400 border-amber-500/30' }
    : versionQuery.isError
    ? { label: 'unreachable', color: 'text-rose-400 border-rose-500/30' }
    : { label: 'online', color: 'text-emerald-400 border-emerald-500/30' };
  return (
    <div className={`glass-light rounded-xl p-3 text-xs border flex items-center justify-between gap-3 ${status.color}`}>
      <div className="text-surface-400">
        <span className="text-surface-500">CGEM API:</span>{' '}
        <code className="text-surface-300">{cgemApiBaseURL}</code>{' '}
        <span className="text-surface-500">·</span>{' '}
        <span className={status.color.split(' ')[0]}>{status.label}</span>
        {versionQuery.data && (
          <>
            {' '}
            <span className="text-surface-500">·</span>{' '}
            <span className="text-surface-300">
              v{versionQuery.data.package_version}
            </span>{' '}
            <span className="text-surface-500">·</span>{' '}
            <span className="text-surface-400">
              binary {versionQuery.data.cgem_binary_sha256.slice(0, 8)}…
            </span>{' '}
            <span className="text-surface-500">·</span>{' '}
            <span className="text-surface-400">
              dataset seed {versionQuery.data.dataset_master_seed}
            </span>
          </>
        )}
      </div>
    </div>
  );
};

export const DashboardPage: React.FC = () => {
  const prefs = useUserPrefs();
  const [searchParams, setSearchParams] = useSearchParams();
  const urlState = dashboardUrlState.read(searchParams);
  const { maneuver: selectedProfileId, layout: viewMode, chart: selectedChart, preset: selectedPresetId } = urlState.value;
  const updateUrl = (patch: Partial<typeof urlState.value>, replace = false) => setSearchParams(
    dashboardUrlState.write({ ...urlState.value, ...patch }), { replace },
  );
  const setSelectedProfileId = (maneuver: string) => updateUrl({ maneuver });
  const setViewMode = (layout: ViewMode) => updateUrl({ layout }, true);
  const setSelectedChart = (chart: ChartType) => updateUrl({ chart }, true);
  const setSelectedPresetId = (preset: DashboardPreset) => updateUrl({ preset });
  const [focusedVariable, setFocusedVariable] = useState<ModelVariableKey>('geff');

  const profile = MANEUVERS_BY_ID[selectedProfileId];
  const selectedPreset = useMemo(
    () => PILOT_PRESETS.find((preset) => preset.id === selectedPresetId) ?? PILOT_PRESETS[0],
    [selectedPresetId]
  );

  const profileDisplayName = useMemo(
    () => selectedProfileId.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()),
    [selectedProfileId]
  );

  const stats = useMemo(() =>
    profile ? calculateProfileStats(profile.samples) : null,
    [profile]
  );

  // ── Real-API path ────────────────────────────────────────────────────
  // Fire /run-cgem on the authoritative FastAPI service.
  const health = useHealth();
  const apiAlive = health.data?.status === 'ok';
  const runCgem = useRunCgem();

  useEffect(() => {
    if (!apiAlive || !profile) return;
    const overrides: Partial<PilotConfigRequest> = {
      who_profile: selectedPreset.whoProfile,
      // Standard Fortran profiles override custom physiology fields.
      dehydration_level: 0,
      gsuit_max_psi:
        selectedPreset.countermeasureOverrides.gsuit_max_psi ??
        DEFAULT_COUNTERMEASURES.gsuit_max_psi ??
        0,
      gsuit_coverage_fraction:
        selectedPreset.countermeasureOverrides.gsuit_coverage_fraction ??
        DEFAULT_COUNTERMEASURES.gsuit_coverage_fraction ??
        0.6,
      agsm_effectiveness:
        selectedPreset.countermeasureOverrides.agsm_effectiveness ??
        DEFAULT_COUNTERMEASURES.agsm_effectiveness ??
        0,
      pbg_max_mmhg: selectedPreset.countermeasureOverrides.pbg_max_mmhg ?? 0,
    };
    const pilot = pilotConfigWithOverrides(pilotConfigFromPrefs(prefs), overrides);
    const req: RunCGEMRequest = { maneuver: selectedProfileId, pilot };
    runCgem.mutate(req);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProfileId, selectedPresetId, apiAlive, prefs]);

  const result = useMemo<CGEMResult | null>(() => {
    if (apiAlive && runCgem.data) {
      try {
        return adaptCgemRun(runCgem.data);
      } catch (e) {
        console.error('Failed to adapt /run-cgem response', e);
      }
    }
    return null;
  }, [apiAlive, runCgem.data]);

  const durations = useMemo(() => {
    if (!result) return null;
    return computeStateDurations(result.times_s, result.g_values, result.geff_values);
  }, [result]);

  if (!profile || !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-surface-400 font-mono">No maneuver selected.</p>
      </div>
    );
  }
  if (apiAlive && runCgem.isPending) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-2">
        <p className="amber font-mono text-sm tracking-callsign animate-pulse-amber">RUNNING CGEM · /run-cgem</p>
        <p className="text-surface-500 text-xs font-mono">Fortran core · ~9 ms / sample</p>
      </div>
    );
  }
  if (apiAlive && runCgem.isError) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-2">
        <p className="text-hud-red font-mono text-sm tracking-callsign">CGEM CALL FAILED</p>
        <p className="text-surface-500 text-xs font-mono">{apiErrorMessage(runCgem.error)}</p>
      </div>
    );
  }
  if (!result || !durations) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3 text-center px-6">
        <p className="text-hud-red font-mono tracking-callsign">CGEM RESULTS UNAVAILABLE</p>
        <p className="text-surface-400 text-sm max-w-xl">
          No physiological result is shown while the authoritative API is offline.
          Start <code>uvicorn cgem_ext.api.main:app</code> at {cgemApiBaseURL}.
          This research interface is not an operational flight-safety system.
        </p>
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
      {urlState.invalid.length > 0 && <p role="status" className="sr-only">Unsupported dashboard URL settings were replaced with safe defaults.</p>}
      <ApiStatusBanner />

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
                aria-pressed={viewMode === 'grid'}
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
                aria-pressed={viewMode === 'single'}
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
            onSelect={setSelectedProfileId}
            className="max-w-md"
          />
          <div className="hidden xl:flex items-center gap-2 px-3 py-2 rounded-xl border border-surface-700/60 bg-surface-900/70">
            <Shield className="w-4 h-4 text-primary-300" />
            <div>
              <p className="text-xs text-surface-500">Pilot preset</p>
              <p className="text-sm text-surface-200 font-medium">{selectedPreset.label}</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Premium Preset Selection */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-5"
      >
        <div className="flex items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Star className="w-4 h-4 text-warning-300" />
              Elite Profile Presets
            </h3>
            <p className="text-xs text-surface-400 mt-1">
              Switch physiology + countermeasure contexts for high-fidelity comparison.
            </p>
          </div>
          <div className="text-xs text-surface-500">
            Selected maneuver: <span className="text-surface-300">{profileDisplayName}</span>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3">
          {PILOT_PRESETS.map((preset) => {
            const isSelected = preset.id === selectedPresetId;
            return (
              <button
                key={preset.id}
                onClick={() => setSelectedPresetId(preset.id)}
                className={cn(
                  'text-left rounded-xl border p-3 transition-all duration-200',
                  isSelected
                    ? PRESET_STYLES[preset.tag]
                    : 'border-surface-700/60 bg-surface-900/55 hover:border-surface-600 text-surface-300'
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold">{preset.label}</p>
                  <span className="text-[10px] uppercase tracking-wide">WHO {preset.whoProfile}</span>
                </div>
                <p className="text-xs mt-2 leading-relaxed text-surface-300/90">{preset.summary}</p>
              </button>
            );
          })}
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

      {/* Model Dynamics Studio */}
      <div className="grid xl:grid-cols-[minmax(0,1.75fr)_minmax(320px,1fr)] gap-6">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          className="chart-container premium-panel"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <div className="chart-title mb-0">
              <Brain className="w-5 h-5 text-primary-300" />
              Premium Model Dynamics
            </div>
            <span className="text-xs text-surface-500">
              Focus variable: <span className="text-surface-300">{focusedVariable}</span>
            </span>
          </div>
          <p className="text-xs text-surface-400 mb-3">
            Coupled visualization of CGEM internals with synchronized impairment windows for
            greyout, blackout, and G-LOC onset analysis.
          </p>
          <ModelDynamicsChart
            result={result}
            title="Integrated Physiological Response"
            height={430}
            focusVariable={focusedVariable}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <VariableInsightsPanel
            result={result}
            selectedVariable={focusedVariable}
            onSelect={setFocusedVariable}
          />
        </motion.div>
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
