/**
 * Prediction table — renders the per-target output from POST /predict.
 *
 * Per the Phase-3 model card, censored time targets show
 *   P(event) · E[t | event=1]    (point + conformal CI on the same scale)
 *   plus a separate event probability badge
 * Continuous targets show
 *   point ± conformal interval
 */

import React from 'react';
import { motion } from 'framer-motion';
import type { TargetPrediction } from '../../services/types';

interface PredictionTableProps {
  targets: TargetPrediction[];
}

const TARGET_LABELS: Record<string, string> = {
  time_to_greyout_s: 'Time to greyout',
  time_to_blackout_s: 'Time to blackout',
  time_to_gloc_s: 'Time to G-LOC',
  hlap_min: 'HLAP min',
  c_bank_min: 'Consciousness bank min',
};

const formatRange = (lo: number | null, hi: number | null): string => {
  if (lo === null || hi === null) return '—';
  return `[${lo.toFixed(2)}, ${hi.toFixed(2)}]`;
};

export const PredictionTable: React.FC<PredictionTableProps> = ({ targets }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="overflow-hidden rounded-2xl border border-surface-700/50"
    >
      <table className="w-full text-sm">
        <thead className="bg-surface-800/60 text-surface-400 uppercase text-xs tracking-wider">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Target</th>
            <th className="px-4 py-3 text-right font-medium">P(event)</th>
            <th className="px-4 py-3 text-right font-medium">Point</th>
            <th className="px-4 py-3 text-right font-medium">95 % CI</th>
            <th className="px-4 py-3 text-right font-medium">Expected</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-700/50">
          {targets.map((t) => {
            const isCensored = t.censored;
            const label = TARGET_LABELS[t.target] ?? t.target;
            return (
              <tr key={t.target} className="hover:bg-surface-800/30 transition-colors">
                <td className="px-4 py-3 text-surface-200 font-medium">{label}</td>
                <td className="px-4 py-3 text-right text-surface-300 tabular-nums">
                  {isCensored && t.event_probability !== null && t.event_probability !== undefined
                    ? `${(t.event_probability * 100).toFixed(1)} %`
                    : '—'}
                </td>
                <td className="px-4 py-3 text-right text-white tabular-nums">
                  {t.point.toFixed(3)}
                </td>
                <td className="px-4 py-3 text-right text-surface-400 tabular-nums">
                  {formatRange(t.lo, t.hi)}
                </td>
                <td className="px-4 py-3 text-right text-surface-300 tabular-nums">
                  {isCensored && t.expected_time_s !== null && t.expected_time_s !== undefined
                    ? t.expected_time_s.toFixed(3)
                    : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="bg-surface-800/40 text-xs text-surface-500 px-4 py-2 leading-relaxed">
        For censored time targets the <em>Point</em> is the conditional time
        E[t | event=1] and the 95 % CI is the Mondrian split-conformal
        interval on that quantity. <em>Expected</em> = P(event) × Point.
        Continuous targets (HLAP, c-bank) report direct surrogate output ±
        conformal interval on the same scale.
      </p>
    </motion.div>
  );
};

export default PredictionTable;
