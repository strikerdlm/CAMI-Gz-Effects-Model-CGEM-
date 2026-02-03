/**
 * Prediction Page
 * 
 * CGEM model configuration and simulation runner.
 * Allows customization of pilot physiology and countermeasures.
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  User,
  Settings,
  Activity,
  AlertTriangle,
  Eye,
  Brain,
} from 'lucide-react';

import { ProfileSelector, MetricCard } from '../components/ui';
import { GForceLineChart, CerebralFlowChart } from '../components/charts';
import { AEROBATIC_PROFILES, simulateCGEMResult } from '../services/mockData';
import { STANDARD_PROFILES, DEFAULT_COUNTERMEASURES } from '../utils/constants';
import { buildTimeSeries } from '../utils/calculations';
import type { PilotConfig, CGEMResult } from '../types';

export const PredictionPage: React.FC = () => {
  const [selectedProfileId, setSelectedProfileId] = useState('high_g_turn');
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<CGEMResult | null>(null);

  // Pilot configuration state
  const [whoProfile, setWhoProfile] = useState<number | null>(2);
  const [countermeasures, setCountermeasures] = useState(DEFAULT_COUNTERMEASURES);

  const profile = AEROBATIC_PROFILES[selectedProfileId];

  const selectedStandardProfile = STANDARD_PROFILES.find(p => p.id === whoProfile);

  const handleRunSimulation = async () => {
    if (!profile) return;
    
    setIsRunning(true);
    
    // Simulate async operation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const config: PilotConfig = {
      who_profile: whoProfile,
      countermeasures,
    };
    
    const simulationResult = simulateCGEMResult(profile, config);
    setResult(simulationResult);
    setIsRunning(false);
  };

  const formatEventTime = (time: number | null): string => {
    return time !== null ? `${time.toFixed(2)}s` : '—';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <h2 className="text-2xl font-bold text-white mb-2">
          CGEM Physiological Prediction
        </h2>
        <p className="text-surface-400 max-w-3xl">
          Configure pilot parameters and run the Combined G-Effects Model simulation.
          The CGEM predicts greyout, blackout, and G-LOC onset times based on cerebral 
          blood flow modeling and validated physiological thresholds.
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Profile Selection */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-400" />
              Maneuver Profile
            </h3>
            <ProfileSelector
              selectedProfileId={selectedProfileId}
              onSelect={setSelectedProfileId}
            />
          </motion.div>

          {/* Pilot Profile */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-accent-400" />
              Subject Profile
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Standard Profile (who)
                </label>
                <select
                  value={whoProfile ?? 'custom'}
                  onChange={(e) => setWhoProfile(
                    e.target.value === 'custom' ? null : parseInt(e.target.value)
                  )}
                  className="select-field"
                >
                  <option value="custom">Custom Configuration</option>
                  {STANDARD_PROFILES.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label} (who={p.id})
                    </option>
                  ))}
                </select>
              </div>

              {selectedStandardProfile && (
                <div className="bg-surface-800/50 rounded-lg p-3 text-sm space-y-1">
                  <p className="text-surface-300">
                    <span className="text-surface-500">Sex:</span>{' '}
                    {selectedStandardProfile.male === 1 ? 'Male' : 'Female'}
                  </p>
                  <p className="text-surface-300">
                    <span className="text-surface-500">Height:</span>{' '}
                    {selectedStandardProfile.howtall} cm
                  </p>
                  <p className="text-surface-300">
                    <span className="text-surface-500">Baseline BP:</span>{' '}
                    {selectedStandardProfile.BSP}/{selectedStandardProfile.BDP} mmHg
                  </p>
                  <p className="text-surface-300">
                    <span className="text-surface-500">Heart τ:</span>{' '}
                    {selectedStandardProfile.beta}s
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Countermeasures */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-warning-400" />
              Countermeasures
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  G-Suit Pressure (PSI)
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  step="0.5"
                  value={countermeasures.gsuit_max_psi}
                  onChange={(e) => setCountermeasures({
                    ...countermeasures,
                    gsuit_max_psi: parseFloat(e.target.value)
                  })}
                  className="w-full"
                />
                <span className="text-sm text-surface-400">
                  {countermeasures.gsuit_max_psi} PSI
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  AGSM Effectiveness
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={countermeasures.agsm_effectiveness}
                  onChange={(e) => setCountermeasures({
                    ...countermeasures,
                    agsm_effectiveness: parseFloat(e.target.value)
                  })}
                  className="w-full"
                />
                <span className="text-sm text-surface-400">
                  {(countermeasures.agsm_effectiveness * 100).toFixed(0)}%
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Dehydration Level
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={countermeasures.dehydration_level}
                  onChange={(e) => setCountermeasures({
                    ...countermeasures,
                    dehydration_level: parseFloat(e.target.value)
                  })}
                  className="w-full"
                />
                <span className="text-sm text-surface-400">
                  {(countermeasures.dehydration_level * 100).toFixed(0)}%
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Seat Tilt (°)
                </label>
                <input
                  type="number"
                  min="0"
                  max="45"
                  value={countermeasures.seat_tilt_deg}
                  onChange={(e) => setCountermeasures({
                    ...countermeasures,
                    seat_tilt_deg: parseFloat(e.target.value) || 0
                  })}
                  className="input-field"
                />
              </div>
            </div>
          </motion.div>

          {/* Run Button */}
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            onClick={handleRunSimulation}
            disabled={isRunning}
            className="btn-primary w-full"
          >
            {isRunning ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Running CGEM Model...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Run Prediction
              </>
            )}
          </motion.button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Event Time Metrics */}
          {result && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="grid grid-cols-3 gap-4"
            >
              <MetricCard
                label="Time to Greyout"
                value={formatEventTime(result.time_to_greyout_s)}
                icon={<Eye className="w-5 h-5 text-surface-400" />}
                color={result.time_to_greyout_s !== null ? 'warning' : 'default'}
              />
              <MetricCard
                label="Time to Blackout"
                value={formatEventTime(result.time_to_blackout_s)}
                icon={<Eye className="w-5 h-5 text-danger-400" />}
                color={result.time_to_blackout_s !== null ? 'danger' : 'default'}
              />
              <MetricCard
                label="Time to G-LOC"
                value={formatEventTime(result.time_to_gloc_s)}
                icon={<Brain className="w-5 h-5 text-purple-400" />}
                color={result.time_to_gloc_s !== null ? 'danger' : 'default'}
              />
            </motion.div>
          )}

          {/* G-Force Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="chart-container"
          >
            <div className="chart-title">
              <Activity className="w-5 h-5 text-primary-400" />
              G-Force Profile with G_eff
            </div>
            {result ? (
              <GForceLineChart
                times={result.times_s}
                gValues={result.g_values}
                geffValues={result.geff_values}
                title="Predicted G and Effective G vs Time"
                height={350}
              />
            ) : profile ? (
              <GForceLineChart
                times={buildTimeSeries(profile.samples).times}
                gValues={buildTimeSeries(profile.samples).gValues}
                title={profile.id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                height={350}
              />
            ) : (
              <div className="h-[350px] flex items-center justify-center text-surface-400">
                Select a profile and run simulation
              </div>
            )}
          </motion.div>

          {/* Cerebral Flow Chart */}
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="chart-container"
            >
              <div className="chart-title">
                <Brain className="w-5 h-5 text-accent-400" />
                Cerebral Blood Flow
              </div>
              <CerebralFlowChart
                result={result}
                height={350}
              />
            </motion.div>
          )}

          {/* Instructions */}
          {!result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-light rounded-xl p-6 text-center"
            >
              <AlertTriangle className="w-12 h-12 text-warning-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">
                Ready to Run Simulation
              </h3>
              <p className="text-surface-400 max-w-md mx-auto">
                Configure pilot parameters in the left panel, then click 
                "Run Prediction" to execute the CGEM physiological model.
              </p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Reference Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="glass-light rounded-xl p-4 text-sm text-surface-400"
      >
        <p>
          <strong className="text-surface-300">CGEM Model Reference:</strong>{' '}
          Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow-based 
          computer modeling of Gz-induced effects (DOT/FAA/AM-23/6).{' '}
          <a 
            href="https://doi.org/10.21949/1524446" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-primary-400 hover:underline"
          >
            DOI: 10.21949/1524446
          </a>
        </p>
      </motion.div>
    </div>
  );
};

export default PredictionPage;
