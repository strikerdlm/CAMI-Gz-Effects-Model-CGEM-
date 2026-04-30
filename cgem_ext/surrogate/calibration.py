"""Reliability diagrams and Expected Calibration Error (ECE) for surrogate predictions.

Provides two public functions:

* :func:`regression_calibration` — for continuous targets (``hlap_min``, ``c_bank_min``).
  Bins predictions, computes per-bin mean predicted vs mean observed, and ECE.
* :func:`classifier_calibration` — for the stage-1 classifier of censored targets.
  Bins predicted probabilities, computes per-bin mean probability vs observed event
  fraction, and ECE.

Both return a :class:`CalibrationResult` dataclass suitable for serialisation and
plotting (reliability diagrams — paper Figure 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class CalibrationResult:
    """Output of a calibration diagnostic."""

    target: str
    n_bins: int
    ece: float
    bin_centers: np.ndarray
    bin_predicted: np.ndarray
    bin_observed: np.ndarray
    bin_counts: np.ndarray
    bin_edges: np.ndarray = field(repr=False)

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "n_bins": self.n_bins,
            "ece": float(self.ece),
            "bin_centers": self.bin_centers.tolist(),
            "bin_predicted": self.bin_predicted.tolist(),
            "bin_observed": self.bin_observed.tolist(),
            "bin_counts": self.bin_counts.tolist(),
            "bin_edges": self.bin_edges.tolist(),
        }


def _equal_frequency_bins(y_pred: np.ndarray, n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (bin_indices, bin_edges) for equal-frequency binning."""
    edges = np.quantile(y_pred, np.linspace(0, 1, n_bins + 1))
    edges[0] = -np.inf
    edges[-1] = np.inf
    indices = np.digitize(y_pred, edges) - 1
    return np.clip(indices, 0, n_bins - 1), edges


def regression_calibration(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target: str = "",
    n_bins: int = 10,
) -> CalibrationResult:
    """Reliability diagram for a continuous regression target.

    Bins predictions into *n_bins* equal-frequency bins, computes the mean
    predicted value and mean observed value per bin, and the ECE.

    ECE = Σ (|bin| / N) · |mean(observed) − mean(predicted)|
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    valid = ~np.isnan(y_true) & ~np.isnan(y_pred)
    y_true, y_pred = y_true[valid], y_pred[valid]
    n = len(y_true)
    if n < n_bins * 2:
        raise ValueError(f"Need at least {n_bins * 2} valid rows, got {n}")

    bin_idx, edges = _equal_frequency_bins(y_pred, n_bins)
    bin_pred, bin_obs, bin_counts = [], [], []
    for b in range(n_bins):
        mask = bin_idx == b
        cnt = mask.sum()
        bin_counts.append(cnt)
        if cnt > 0:
            bin_pred.append(y_pred[mask].mean())
            bin_obs.append(y_true[mask].mean())
        else:
            bin_pred.append(0.0)
            bin_obs.append(0.0)

    bin_pred_arr = np.array(bin_pred, dtype=float)
    bin_obs_arr = np.array(bin_obs, dtype=float)
    bin_counts_arr = np.array(bin_counts, dtype=float)
    centers = np.array([(edges[i] + edges[i + 1]) / 2 for i in range(n_bins)])
    ece = float(np.sum((bin_counts_arr / n) * np.abs(bin_obs_arr - bin_pred_arr)))

    return CalibrationResult(
        target=target,
        n_bins=n_bins,
        ece=ece,
        bin_centers=centers,
        bin_predicted=bin_pred_arr,
        bin_observed=bin_obs_arr,
        bin_counts=bin_counts_arr,
        bin_edges=edges,
    )


def classifier_calibration(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target: str = "",
    n_bins: int = 10,
) -> CalibrationResult:
    """Reliability diagram for a binary classifier.

    Bins predicted probabilities into *n_bins* equal-frequency bins, computes
    the mean predicted probability and observed event fraction per bin, and ECE.

    ECE = Σ (|bin| / N) · |fraction(events) − mean(probability)|
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    valid = ~np.isnan(y_true) & ~np.isnan(y_prob)
    y_true, y_prob = y_true[valid], y_prob[valid]
    n = len(y_true)
    if n < n_bins * 2:
        raise ValueError(f"Need at least {n_bins * 2} valid rows, got {n}")

    bin_idx, edges = _equal_frequency_bins(y_prob, n_bins)
    bin_pred, bin_obs, bin_counts = [], [], []
    for b in range(n_bins):
        mask = bin_idx == b
        cnt = mask.sum()
        bin_counts.append(cnt)
        if cnt > 0:
            bin_pred.append(y_prob[mask].mean())
            bin_obs.append(y_true[mask].mean())
        else:
            bin_pred.append(0.0)
            bin_obs.append(0.0)

    bin_pred_arr = np.array(bin_pred, dtype=float)
    bin_obs_arr = np.array(bin_obs, dtype=float)
    bin_counts_arr = np.array(bin_counts, dtype=float)
    centers = np.array([(edges[i] + edges[i + 1]) / 2 for i in range(n_bins)])
    ece = float(np.sum((bin_counts_arr / n) * np.abs(bin_obs_arr - bin_pred_arr)))

    return CalibrationResult(
        target=target,
        n_bins=n_bins,
        ece=ece,
        bin_centers=centers,
        bin_predicted=bin_pred_arr,
        bin_observed=bin_obs_arr,
        bin_counts=bin_counts_arr,
        bin_edges=edges,
    )


__all__ = ["CalibrationResult", "classifier_calibration", "regression_calibration"]
