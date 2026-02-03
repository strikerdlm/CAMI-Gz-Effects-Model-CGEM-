/**
 * Overview Page
 * 
 * Main entry point for profile selection and G-force visualization.
 * Displays profile statistics and basic physiological metrics.
 */

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Gauge, 
  Timer, 
  TrendingUp, 
  TrendingDown,
  Activity,
  AlertTriangle,
  Zap,
} from 'lucide-react';

import { ProfileSelector, MetricCard } from '../components/ui';
import { GForceLineChart } from '../components/charts';
import { AEROBATIC_PROFILES } from '../services/mockData';
import { calculateProfileStats, buildTimeSeries } from '../utils/calculations';
import { cn } from '../utils';

export const OverviewPage: React.FC = () => {
  const [selectedProfileId, setSelectedProfileId] = useState('high_g_turn');
  
  const profile = AEROBATIC_PROFILES[selectedProfileId];
  const stats = useMemo(() => 
    profile ? calculateProfileStats(profile.samples) : null, 
    [profile]
  );
  const timeSeries = useMemo(() => 
    profile ? buildTimeSeries(profile.samples) : { times: [], gValues: [] },
    [profile]
  );

  if (!profile || !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-surface-400">Loading profile data...</p>
      </div>
    );
  }

  const getRiskLevel = (): { level: string; color: string } => {
    if (stats.max_positive_g > 6 || stats.max_negative_g < -2) {
      return { level: 'High Risk', color: 'text-danger-400' };
    }
    if (stats.max_positive_g > 4 || stats.max_negative_g < -1) {
      return { level: 'Moderate Risk', color: 'text-warning-400' };
    }
    return { level: 'Low Risk', color: 'text-accent-400' };
  };

  const riskInfo = getRiskLevel();

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Aerobatic Maneuver Profile
            </h2>
            <p className="text-surface-400 max-w-2xl">
              Select a maneuver profile to visualize G-force characteristics and 
              review physiological risk factors. Data represents typical G-loading 
              patterns from in-flight measurements.
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl',
              'bg-surface-800/60 border border-surface-700/50'
            )}>
              <AlertTriangle className={cn('w-5 h-5', riskInfo.color)} />
              <span className={cn('font-semibold', riskInfo.color)}>
                {riskInfo.level}
              </span>
            </div>
          </div>
        </div>

        {/* Profile Selector */}
        <div className="mt-6">
          <ProfileSelector
            selectedProfileId={selectedProfileId}
            onSelect={setSelectedProfileId}
            className="max-w-xl"
          />
        </div>
      </motion.div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricCard
          label="Duration"
          value={stats.total_duration_s.toFixed(1)}
          unit="s"
          icon={<Timer className="w-5 h-5 text-primary-400" />}
        />
        <MetricCard
          label="Max +G"
          value={`+${stats.max_positive_g.toFixed(1)}`}
          unit="G"
          icon={<TrendingUp className="w-5 h-5 text-danger-400" />}
          color={stats.max_positive_g > 6 ? 'danger' : stats.max_positive_g > 4 ? 'warning' : 'default'}
        />
        <MetricCard
          label="Max −G"
          value={stats.max_negative_g.toFixed(1)}
          unit="G"
          icon={<TrendingDown className="w-5 h-5 text-warning-400" />}
          color={stats.max_negative_g < -2 ? 'danger' : stats.max_negative_g < -1 ? 'warning' : 'default'}
        />
        <MetricCard
          label="Mean G"
          value={stats.weighted_mean_g.toFixed(2)}
          unit="G"
          icon={<Activity className="w-5 h-5 text-accent-400" />}
        />
        <MetricCard
          label="+G Dose"
          value={stats.positive_g_dose.toFixed(1)}
          unit="G·s"
          icon={<Zap className="w-5 h-5 text-primary-400" />}
        />
        <MetricCard
          label="RMS G"
          value={stats.rms_g.toFixed(2)}
          unit="G"
          icon={<Gauge className="w-5 h-5 text-surface-400" />}
        />
      </div>

      {/* Main Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="chart-container"
      >
        <div className="chart-title">
          <Activity className="w-5 h-5 text-primary-400" />
          Normal Acceleration vs Time
        </div>
        <GForceLineChart
          times={timeSeries.times}
          gValues={timeSeries.gValues}
          title={profile.id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          height={450}
          showThresholds={true}
          showZones={true}
        />
      </motion.div>

      {/* Additional Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid md:grid-cols-2 gap-6"
      >
        {/* Exposure Times */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Timer className="w-5 h-5 text-warning-400" />
            Exposure Analysis
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-surface-800/50 rounded-lg">
              <span className="text-surface-300">Time above +3G</span>
              <span className="font-semibold text-warning-400">
                {stats.time_above_3g_s.toFixed(2)}s
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-800/50 rounded-lg">
              <span className="text-surface-300">Time below −1G</span>
              <span className="font-semibold text-danger-400">
                {stats.time_below_neg1g_s.toFixed(2)}s
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-800/50 rounded-lg">
              <span className="text-surface-300">P95 |G|</span>
              <span className="font-semibold text-surface-200">
                {stats.p95_abs_g.toFixed(2)}G
              </span>
            </div>
          </div>
        </div>

        {/* Profile Description */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-primary-400" />
            Profile Description
          </h3>
          <p className="text-surface-300 leading-relaxed">
            {profile.description}
          </p>
          <div className="mt-4 pt-4 border-t border-surface-700/50">
            <div className="flex items-center gap-2 text-sm text-surface-400">
              <span className="font-medium">Source:</span>
              <code className="px-2 py-0.5 bg-surface-800 rounded text-surface-300">
                {profile.filename}
              </code>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Scientific Reference */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-light rounded-xl p-4 text-sm text-surface-400"
      >
        <p>
          <strong className="text-surface-300">Note:</strong> G-force profiles are derived from 
          in-flight measurements of aerobatic maneuvers. Physiological thresholds are based on 
          validated centrifuge research. See{' '}
          <a 
            href="https://doi.org/10.21949/1524446" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-primary-400 hover:underline"
          >
            Copeland & Whinnery (2023)
          </a>{' '}
          for CGEM model details and validation.
        </p>
      </motion.div>
    </div>
  );
};

export default OverviewPage;
