/**
 * Physiological Analysis Page
 * 
 * Detailed maneuver explanations, risk factors, and mitigation strategies.
 */

import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  AlertTriangle,
  Shield,
  Activity,
  ChevronDown,
  ExternalLink,
  BookOpen,
} from 'lucide-react';

import { ProfileSelector } from '../components/ui';
import { SensitivityChart } from '../components/charts';
import { MANEUVERS_BY_ID as AEROBATIC_PROFILES } from '../data/maneuvers';
import { MANEUVER_EXPLANATIONS } from '../utils/constants';
import { calculateProfileStats } from '../utils/calculations';
import { cn } from '../utils';
import { TARGET_NAMES, type TargetName } from '../services/types';
import { analysisUrlState, readManeuverParam, setSearchParam, type AnalysisView } from '../services/urlState';

interface SectionHeaderProps {
  id: string;
  icon: React.ElementType;
  title: string;
  color: string;
  isExpanded: boolean;
  onToggle: (sectionId: string) => void;
}

const SectionHeader: React.FC<SectionHeaderProps> = ({
  id,
  icon: Icon,
  title,
  color,
  isExpanded,
  onToggle,
}) => (
  <button
    onClick={() => onToggle(id)}
    className="w-full flex items-center justify-between p-4 hover:bg-surface-800/50 transition-colors"
  >
    <div className="flex items-center gap-3">
      <div className={cn('p-2 rounded-lg', color)}>
        <Icon className="w-5 h-5" />
      </div>
      <span className="font-semibold text-white">{title}</span>
    </div>
    <ChevronDown
      className={cn('w-5 h-5 text-surface-400 transition-transform', isExpanded && 'rotate-180')}
    />
  </button>
);

export const AnalysisPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const parsed = analysisUrlState.read(searchParams);
  const selectedProfileId = readManeuverParam(searchParams);
  const sobolTarget = parsed.value.target;
  const analysisView = parsed.value.view;
  const setSelectedProfileId = (maneuver: string) => setSearchParams(setSearchParam(searchParams, 'maneuver', maneuver, 'high_g_turn'));
  const updateAnalysis = (patch: Partial<typeof parsed.value>) => {
    const next = analysisUrlState.write({ ...parsed.value, ...patch });
    const maneuver = searchParams.get('maneuver');
    if (maneuver) next.set('maneuver', selectedProfileId);
    setSearchParams(next, { replace: true });
  };
  const setSobolTarget = (target: TargetName) => updateAnalysis({ target });
  const setAnalysisView = (view: AnalysisView) => updateAnalysis({ view });
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['description', 'effects'])
  );

  const profile = AEROBATIC_PROFILES[selectedProfileId];
  const explanation = MANEUVER_EXPLANATIONS[selectedProfileId];
  const stats = profile ? calculateProfileStats(profile.samples) : null;

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  return (
    <div className="space-y-6">
      {(parsed.invalid.length > 0 || (searchParams.has('maneuver') && searchParams.get('maneuver') !== selectedProfileId)) && (
        <p role="status" className="sr-only">Unsupported analysis URL settings were replaced with safe defaults.</p>
      )}
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <h2 className="text-2xl font-bold text-white mb-2">
          Physiological Analysis
        </h2>
        <p className="text-surface-400 max-w-2xl mb-6">
          Comprehensive analysis of maneuver-specific physiological effects,
          risk factors, and evidence-based mitigation strategies.
        </p>

        <ProfileSelector
          selectedProfileId={selectedProfileId}
          onSelect={setSelectedProfileId}
          className="max-w-xl"
        />
        <div className="mt-4 flex gap-2" aria-label="Analysis view">
          {(['explanation', 'sensitivity'] as const).map((view) => (
            <button key={view} type="button" aria-pressed={analysisView === view} onClick={() => setAnalysisView(view)} className="btn-secondary">{view}</button>
          ))}
        </div>
      </motion.div>

      {/* Global sensitivity (Phase-4 Sobol indices, served by /sensitivity) */}
      {analysisView === 'sensitivity' && <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <div>
            <h3 className="text-lg font-semibold text-white">
              Global sensitivity (Sobol indices)
            </h3>
            <p className="text-sm text-surface-400 max-w-2xl">
              First-order (S1) and total-order (ST) Sobol indices computed via
              the surrogate at <code>n_base = 1024</code> on the custom-arm
              input space. Loaded from{' '}
              <code className="text-surface-300">
                data/results/sensitivity/sobol_first_total.csv
              </code>{' '}
              via <code>GET /sensitivity/{'{target}'}</code>.
            </p>
          </div>
          <select
            value={sobolTarget}
            onChange={(e) => setSobolTarget(e.target.value as TargetName)}
            className="bg-surface-800/60 border border-surface-700 rounded-md px-3 py-2 text-sm text-surface-200"
          >
            {TARGET_NAMES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <SensitivityChart target={sobolTarget} height={380} />
      </motion.div>}

      {analysisView === 'explanation' && <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Analysis */}
        <div className="lg:col-span-2 space-y-4">
          {explanation ? (
            <>
              {/* Description */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass rounded-2xl overflow-hidden"
              >
                <SectionHeader
                  id="description"
                  icon={FileText}
                  title="Maneuver Description"
                  color="bg-primary-500/20 text-primary-400"
                  isExpanded={expandedSections.has('description')}
                  onToggle={toggleSection}
                />
                <AnimatePresence>
                  {expandedSections.has('description') && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6">
                        <p className="text-surface-300 leading-relaxed">
                          {explanation.description}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* Physiological Effects */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass rounded-2xl overflow-hidden"
              >
                <SectionHeader
                  id="effects"
                  icon={Activity}
                  title="Physiological Effects"
                  color="bg-accent-500/20 text-accent-400"
                  isExpanded={expandedSections.has('effects')}
                  onToggle={toggleSection}
                />
                <AnimatePresence>
                  {expandedSections.has('effects') && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6">
                        <p className="text-surface-300 leading-relaxed">
                          {explanation.physiological_effects}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* Risk Factors */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass rounded-2xl overflow-hidden"
              >
                <SectionHeader
                  id="risks"
                  icon={AlertTriangle}
                  title="Risk Factors"
                  color="bg-warning-500/20 text-warning-400"
                  isExpanded={expandedSections.has('risks')}
                  onToggle={toggleSection}
                />
                <AnimatePresence>
                  {expandedSections.has('risks') && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 space-y-2">
                        {explanation.risk_factors.map((risk, i) => (
                          <div
                            key={i}
                            className="flex items-start gap-3 p-3 bg-warning-500/5 rounded-lg border border-warning-500/20"
                          >
                            <AlertTriangle className="w-4 h-4 text-warning-400 mt-0.5 flex-shrink-0" />
                            <span className="text-surface-300">{risk}</span>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* Mitigation Strategies */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-2xl overflow-hidden"
              >
                <SectionHeader
                  id="mitigation"
                  icon={Shield}
                  title="Mitigation Strategies"
                  color="bg-accent-500/20 text-accent-400"
                  isExpanded={expandedSections.has('mitigation')}
                  onToggle={toggleSection}
                />
                <AnimatePresence>
                  {expandedSections.has('mitigation') && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 space-y-2">
                        {explanation.mitigation.map((strategy, i) => (
                          <div
                            key={i}
                            className="flex items-start gap-3 p-3 bg-accent-500/5 rounded-lg border border-accent-500/20"
                          >
                            <Shield className="w-4 h-4 text-accent-400 mt-0.5 flex-shrink-0" />
                            <span className="text-surface-300">{strategy}</span>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </>
          ) : (
            <div className="glass rounded-2xl p-12 text-center">
              <FileText className="w-12 h-12 text-surface-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">
                Analysis Not Available
              </h3>
              <p className="text-surface-400">
                Detailed physiological analysis for this maneuver is not yet documented.
              </p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Quick Stats */}
          {stats && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass rounded-2xl p-5"
            >
              <h3 className="text-lg font-semibold text-white mb-4">
                Profile Statistics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-surface-400">Duration</span>
                  <span className="text-white font-medium">
                    {stats.total_duration_s.toFixed(1)}s
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-surface-400">Max +G</span>
                  <span className="text-danger-400 font-medium">
                    +{stats.max_positive_g.toFixed(1)}G
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-surface-400">Max −G</span>
                  <span className="text-warning-400 font-medium">
                    {stats.max_negative_g.toFixed(1)}G
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-surface-400">+G Dose</span>
                  <span className="text-white font-medium">
                    {stats.positive_g_dose.toFixed(1)} G·s
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {/* References */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-5"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-primary-400" />
              Key References
            </h3>
            <div className="space-y-3 text-sm">
              <a
                href="https://doi.org/10.21949/1524446"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 p-3 bg-surface-800/50 rounded-lg hover:bg-surface-800 transition-colors group"
              >
                <ExternalLink className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-surface-200 group-hover:text-white">
                    Copeland & Whinnery (2023)
                  </p>
                  <p className="text-xs text-surface-500">
                    CGEM Model Documentation
                  </p>
                </div>
              </a>
              <a
                href="https://doi.org/10.1017/S095252381500005X"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 p-3 bg-surface-800/50 rounded-lg hover:bg-surface-800 transition-colors group"
              >
                <ExternalLink className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-surface-200 group-hover:text-white">
                    Whinnery & Forster (2015)
                  </p>
                  <p className="text-xs text-surface-500">
                    Visual Neuroscience
                  </p>
                </div>
              </a>
              <a
                href="https://doi.org/10.1177/0018720809359631"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 p-3 bg-surface-800/50 rounded-lg hover:bg-surface-800 transition-colors group"
              >
                <ExternalLink className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-surface-200 group-hover:text-white">
                    Tripp et al. (2009)
                  </p>
                  <p className="text-xs text-surface-500">
                    Human Factors
                  </p>
                </div>
              </a>
            </div>
          </motion.div>
        </div>
      </div>}
    </div>
  );
};

export default AnalysisPage;
