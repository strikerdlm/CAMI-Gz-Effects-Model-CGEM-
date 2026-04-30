/**
 * OOD warning banner for the Prediction page.
 *
 * Renders an in-line alert when the API marks the input as out of
 * distribution. The Mahalanobis + split-conformal layer abstains at
 * a 5 % nominal rate on exchangeable in-distribution data, so seeing
 * this banner means the surrogate has not been validated for the
 * supplied (maneuver, pilot) combination.
 */

import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

interface OODBannerProps {
  ood: boolean;
  oodScore: number;
  modelVersion: string;
}

export const OODBanner: React.FC<OODBannerProps> = ({ ood, oodScore, modelVersion }) => {
  if (!ood) {
    return (
      <div className="glass-light rounded-xl p-3 text-sm flex items-start gap-3 border border-emerald-500/20">
        <ShieldAlert className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
        <div className="text-surface-300">
          <span className="text-emerald-300 font-medium">In envelope</span>{' '}
          (Mahalanobis score {oodScore.toFixed(1)}). Surrogate v{modelVersion}{' '}
          predictions are within the calibrated 95 % envelope.
        </div>
      </div>
    );
  }
  return (
    <div className="glass-light rounded-xl p-4 text-sm flex items-start gap-3 border border-amber-500/30">
      <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
      <div className="text-surface-200">
        <p className="text-amber-300 font-semibold mb-1">Out-of-distribution input</p>
        <p className="text-surface-400">
          Mahalanobis score {oodScore.toFixed(1)} exceeds the 95 % conformal
          threshold (calibrated on the validation slice of{' '}
          <code className="text-surface-300">cgem_synthetic_v1</code>). The
          surrogate is extrapolating; treat the predictions and conformal
          intervals as advisory. For an authoritative answer use the
          <em> Run authoritative CGEM</em> button to invoke the Fortran
          subprocess directly.
        </p>
      </div>
    </div>
  );
};

export default OODBanner;
