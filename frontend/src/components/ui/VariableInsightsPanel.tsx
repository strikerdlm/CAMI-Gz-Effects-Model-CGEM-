/**
 * Variable Insights Panel
 *
 * Interactive explanation panel for key CGEM variables.
 * Selecting a variable highlights it in the model dynamics chart.
 */

import React, { useMemo } from 'react';
import { Activity, Brain, Eye, Gauge, Shield } from 'lucide-react';
import { cn } from '../../utils';
import type { CGEMResult } from '../../types';
import type { ModelVariableKey } from '../charts/ModelDynamicsChart';
import { PHYSIOLOGICAL_THRESHOLDS } from '../../utils/constants';

interface VariableInsightsPanelProps {
  result: CGEMResult;
  selectedVariable: ModelVariableKey;
  onSelect: (variable: ModelVariableKey) => void;
  className?: string;
}

type InsightStatus = 'stable' | 'watch' | 'critical';

interface VariableInsight {
  key: ModelVariableKey;
  label: string;
  unit: string;
  formula: string;
  explanation: string;
  primaryValue: string;
  secondaryMetric: string;
  status: InsightStatus;
  accentClass: string;
  icon: React.ElementType;
}

function durationMatching(values: number[], times: number[], predicate: (value: number) => boolean): number {
  if (values.length < 2 || values.length !== times.length) {
    return 0;
  }

  let durationSeconds = 0;
  for (let i = 0; i < values.length - 1; i++) {
    if (!predicate(values[i])) {
      continue;
    }
    const dt = Math.max(0, times[i + 1] - times[i]);
    durationSeconds += dt;
  }
  return durationSeconds;
}

export const VariableInsightsPanel: React.FC<VariableInsightsPanelProps> = ({
  result,
  selectedVariable,
  onSelect,
  className,
}) => {
  const insights = useMemo<VariableInsight[]>(() => {
    const maxGeff = Math.max(...result.geff_values, 0);
    const geffRiskDuration = durationMatching(
      result.geff_values,
      result.times_s,
      (value) => value >= PHYSIOLOGICAL_THRESHOLDS.greyout_geff
    );

    const minFlow = Math.min(...result.f_con_values, Number.POSITIVE_INFINITY);
    const lowFlowDuration = durationMatching(result.f_con_values, result.times_s, (value) => value < 19);

    const maxCBank = Math.max(...result.c_bank_values, 1);
    const minCBank = Math.min(...result.c_bank_values, maxCBank);
    const cBankDropPct = ((maxCBank - minCBank) / maxCBank) * 100;

    const maxBOBank = Math.max(...result.bo_bank_values, 1);
    const minBOBank = Math.min(...result.bo_bank_values, maxBOBank);
    const boBankDropPct = ((maxBOBank - minBOBank) / maxBOBank) * 100;

    const maxHlap = Math.max(...result.hlap_values, 0);
    const minHlap = Math.min(...result.hlap_values, 0);
    const hlapExcursion = maxHlap - minHlap;

    const geffStatus: InsightStatus =
      maxGeff >= PHYSIOLOGICAL_THRESHOLDS.gloc_geff
        ? 'critical'
        : maxGeff >= PHYSIOLOGICAL_THRESHOLDS.blackout_geff
          ? 'watch'
          : 'stable';

    const flowStatus: InsightStatus = minFlow < 19 ? 'critical' : minFlow < 25 ? 'watch' : 'stable';
    const cBankStatus: InsightStatus = minCBank < 0.8 ? 'critical' : cBankDropPct > 60 ? 'watch' : 'stable';
    const boBankStatus: InsightStatus = minBOBank < 0.8 ? 'critical' : boBankDropPct > 60 ? 'watch' : 'stable';
    const hlapStatus: InsightStatus = hlapExcursion > 70 ? 'watch' : 'stable';

    return [
      {
        key: 'geff',
        label: 'G_eff',
        unit: 'G',
        formula: 'G_eff = Gz corrected by physiological response lag',
        explanation:
          'Effective acceleration loading that maps better to symptom onset than raw Gz alone.',
        primaryValue: `${maxGeff.toFixed(2)} G`,
        secondaryMetric: `${geffRiskDuration.toFixed(2)} s above greyout threshold`,
        status: geffStatus,
        accentClass: 'text-sky-300 border-sky-400/40 bg-sky-500/10',
        icon: Activity,
      },
      {
        key: 'f_con',
        label: 'F_con',
        unit: 'dl/min',
        formula: 'F_con = cerebral flow supporting consciousness reserve',
        explanation:
          'Primary flow variable used to estimate cerebral perfusion sufficiency for sustained consciousness.',
        primaryValue: `${minFlow.toFixed(2)} dl/min`,
        secondaryMetric: `${lowFlowDuration.toFixed(2)} s below 19 dl/min`,
        status: flowStatus,
        accentClass: 'text-emerald-300 border-emerald-400/40 bg-emerald-500/10',
        icon: Brain,
      },
      {
        key: 'c_bank',
        label: 'C_bank',
        unit: 's',
        formula: 'C_bank(t+dt) = C_bank(t) - depletion + recovery',
        explanation:
          'Consciousness reserve buffer in seconds; once near zero, G-LOC probability sharply increases.',
        primaryValue: `${minCBank.toFixed(2)} s`,
        secondaryMetric: `${cBankDropPct.toFixed(1)}% reserve consumed`,
        status: cBankStatus,
        accentClass: 'text-amber-300 border-amber-400/40 bg-amber-500/10',
        icon: Shield,
      },
      {
        key: 'bo_bank',
        label: 'BO_bank',
        unit: 's',
        formula: 'BO_bank tracks vision reserve against sustained +G stress',
        explanation:
          'Blackout reserve variable estimating available visual tolerance before complete vision loss.',
        primaryValue: `${minBOBank.toFixed(2)} s`,
        secondaryMetric: `${boBankDropPct.toFixed(1)}% reserve consumed`,
        status: boBankStatus,
        accentClass: 'text-rose-300 border-rose-400/40 bg-rose-500/10',
        icon: Eye,
      },
      {
        key: 'hlap',
        label: 'HLAP',
        unit: 'mmHg',
        formula: 'HLAP = heart-level arterial pressure response to +G/-G',
        explanation:
          'Pressure proxy driving perfusion dynamics and contributing to reserve bank depletion/recovery.',
        primaryValue: `${maxHlap.toFixed(1)} mmHg`,
        secondaryMetric: `${hlapExcursion.toFixed(1)} mmHg excursion`,
        status: hlapStatus,
        accentClass: 'text-violet-300 border-violet-400/40 bg-violet-500/10',
        icon: Gauge,
      },
    ];
  }, [result]);

  const selectedInsight = insights.find((insight) => insight.key === selectedVariable) ?? insights[0];
  if (!selectedInsight) {
    return null;
  }

  const statusLabel: Record<InsightStatus, string> = {
    stable: 'Stable',
    watch: 'Watch',
    critical: 'Critical',
  };

  const statusClass: Record<InsightStatus, string> = {
    stable: 'text-emerald-300 bg-emerald-500/15 border-emerald-400/30',
    watch: 'text-amber-300 bg-amber-500/15 border-amber-400/30',
    critical: 'text-rose-300 bg-rose-500/15 border-rose-400/30',
  };

  return (
    <div className={cn('instrument-panel rounded-2xl p-4 space-y-3', className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-white">Variable Explanations</h3>
        <span className="text-xs text-surface-400">CGEM internals</span>
      </div>

      <div className="space-y-2">
        {insights.map((insight) => {
          const Icon = insight.icon;
          const isSelected = insight.key === selectedVariable;
          return (
            <button
              type="button"
              aria-pressed={isSelected}
              key={insight.key}
              onClick={() => onSelect(insight.key)}
              className={cn(
                'w-full min-h-11 text-left rounded-xl p-3 border transition-colors duration-200',
                insight.accentClass,
                isSelected ? 'ring-1 ring-white/25 shadow-lg shadow-black/25' : 'opacity-80 hover:opacity-100'
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2">
                  <Icon className="w-4 h-4 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold">{insight.label}</p>
                    <p className="text-xs text-surface-200/90 mt-0.5">{insight.primaryValue}</p>
                  </div>
                </div>
                <span className={cn('px-2 py-0.5 text-[11px] rounded-full border', statusClass[insight.status])}>
                  {statusLabel[insight.status]}
                </span>
              </div>
              <p className="text-[11px] text-surface-300 mt-2">{insight.secondaryMetric}</p>
            </button>
          );
        })}
      </div>

      <div className="rounded-xl border border-surface-700/60 bg-surface-900/55 p-3">
        <div className="flex items-center justify-between gap-3">
          <h4 className="text-sm font-semibold text-white">{selectedInsight.label}</h4>
          <span className="text-xs text-surface-400">{selectedInsight.unit}</span>
        </div>
        <p className="text-xs text-surface-300 mt-2 leading-relaxed">{selectedInsight.explanation}</p>
        <p className="text-[11px] text-primary-300 mt-2 font-mono">{selectedInsight.formula}</p>
      </div>
    </div>
  );
};

export default VariableInsightsPanel;
