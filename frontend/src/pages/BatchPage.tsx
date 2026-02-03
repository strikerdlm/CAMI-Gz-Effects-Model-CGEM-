/**
 * Batch Analysis Page
 * 
 * Run CGEM predictions for all aerobatic profiles simultaneously
 * and compare results in a unified view.
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  Activity,
  AlertTriangle,
  Check,
  Timer,
  Eye,
  Brain,
} from 'lucide-react';

import { AEROBATIC_PROFILES, simulateCGEMResult } from '../services/mockData';
import { DEFAULT_COUNTERMEASURES } from '../utils/constants';
import { calculateProfileStats } from '../utils/calculations';
import { cn } from '../utils';
import type { PilotConfig, CGEMResult, ProfileStats } from '../types';

interface BatchResult {
  profileId: string;
  profileName: string;
  result: CGEMResult;
  stats: ProfileStats;
}

export const BatchPage: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<BatchResult[]>([]);

  const profileIds = Object.keys(AEROBATIC_PROFILES);

  const handleRunBatch = async () => {
    setIsRunning(true);
    setProgress(0);
    setResults([]);

    const config: PilotConfig = {
      who_profile: 2,
      countermeasures: DEFAULT_COUNTERMEASURES,
    };

    const batchResults: BatchResult[] = [];

    for (let i = 0; i < profileIds.length; i++) {
      const profileId = profileIds[i];
      const profile = AEROBATIC_PROFILES[profileId];
      
      // Simulate async processing
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const result = simulateCGEMResult(profile, config);
      const stats = calculateProfileStats(profile.samples);
      
      batchResults.push({
        profileId,
        profileName: profileId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        result,
        stats,
      });

      setProgress(((i + 1) / profileIds.length) * 100);
      setResults([...batchResults]);
    }

    setIsRunning(false);
  };

  const formatTime = (time: number | null): string => {
    return time !== null ? `${time.toFixed(2)}s` : '—';
  };

  const getStatusColor = (result: CGEMResult): string => {
    if (result.time_to_gloc_s !== null) return 'danger';
    if (result.time_to_blackout_s !== null) return 'warning';
    if (result.time_to_greyout_s !== null) return 'caution';
    return 'success';
  };

  const statusColors: Record<string, string> = {
    success: 'bg-accent-500/20 text-accent-400 border-accent-500/30',
    caution: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    warning: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    danger: 'bg-danger-500/20 text-danger-400 border-danger-500/30',
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
              Batch Physiological Analysis
            </h2>
            <p className="text-surface-400 max-w-2xl">
              Run CGEM predictions for all {profileIds.length} aerobatic profiles
              simultaneously. Compare greyout, blackout, and G-LOC onset times
              across maneuvers.
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleRunBatch}
            disabled={isRunning}
            className="btn-primary min-w-[200px]"
          >
            {isRunning ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Run All Profiles
              </>
            )}
          </motion.button>
        </div>

        {/* Progress Bar */}
        {isRunning && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-surface-400">
                Processing profiles...
              </span>
              <span className="text-sm font-medium text-primary-400">
                {progress.toFixed(0)}%
              </span>
            </div>
            <div className="h-2 bg-surface-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                className="h-full bg-gradient-to-r from-primary-500 to-accent-500"
              />
            </div>
          </div>
        )}
      </motion.div>

      {/* Results Table */}
      {results.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl overflow-hidden"
        >
          <div className="p-4 border-b border-surface-700/50">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-400" />
              Results ({results.length} profiles)
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-surface-800/50">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-surface-300">
                    Profile
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-surface-300">
                    <div className="flex items-center justify-center gap-1">
                      <Timer className="w-4 h-4" />
                      Duration
                    </div>
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-surface-300">
                    Max G
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-surface-300">
                    <div className="flex items-center justify-center gap-1">
                      <Eye className="w-4 h-4" />
                      Greyout
                    </div>
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-surface-300">
                    <div className="flex items-center justify-center gap-1">
                      <Eye className="w-4 h-4" />
                      Blackout
                    </div>
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-surface-300">
                    <div className="flex items-center justify-center gap-1">
                      <Brain className="w-4 h-4" />
                      G-LOC
                    </div>
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-surface-300">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {results.map((batch, index) => {
                  const status = getStatusColor(batch.result);
                  return (
                    <motion.tr
                      key={batch.profileId}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b border-surface-700/30 hover:bg-surface-800/30 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <div className="font-medium text-white">
                          {batch.profileName}
                        </div>
                        <div className="text-xs text-surface-500">
                          {batch.stats.positive_g_dose.toFixed(1)} G·s dose
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center text-surface-300">
                        {batch.stats.total_duration_s.toFixed(1)}s
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          'font-semibold',
                          batch.stats.max_positive_g > 6 ? 'text-danger-400' :
                          batch.stats.max_positive_g > 4 ? 'text-warning-400' :
                          'text-surface-200'
                        )}>
                          +{batch.stats.max_positive_g.toFixed(1)}G
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          batch.result.time_to_greyout_s !== null 
                            ? 'text-yellow-400 font-medium' 
                            : 'text-surface-500'
                        )}>
                          {formatTime(batch.result.time_to_greyout_s)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          batch.result.time_to_blackout_s !== null 
                            ? 'text-orange-400 font-medium' 
                            : 'text-surface-500'
                        )}>
                          {formatTime(batch.result.time_to_blackout_s)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          batch.result.time_to_gloc_s !== null 
                            ? 'text-danger-400 font-medium' 
                            : 'text-surface-500'
                        )}>
                          {formatTime(batch.result.time_to_gloc_s)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border',
                          statusColors[status]
                        )}>
                          {status === 'success' && <Check className="w-3 h-3" />}
                          {status !== 'success' && <AlertTriangle className="w-3 h-3" />}
                          {status === 'success' ? 'Safe' : 
                           status === 'caution' ? 'Greyout' :
                           status === 'warning' ? 'Blackout' : 'G-LOC Risk'}
                        </span>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {results.length === 0 && !isRunning && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-12 text-center"
        >
          <Activity className="w-16 h-16 text-surface-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            Ready for Batch Analysis
          </h3>
          <p className="text-surface-400 max-w-md mx-auto mb-6">
            Click "Run All Profiles" to execute CGEM predictions for all 
            {' '}{profileIds.length} aerobatic maneuvers using the default 
            pilot configuration.
          </p>
          <p className="text-xs text-surface-500">
            Configuration: Median male (who=2), no countermeasures
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default BatchPage;
