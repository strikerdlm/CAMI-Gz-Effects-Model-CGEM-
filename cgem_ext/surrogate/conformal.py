"""Mondrian split-conformal prediction intervals for the surrogate.

Standard split-conformal yields one global interval; Mondrian
conformal stratifies the calibration step by a discrete *taxonomy*
variable (here, ``maneuver_category``) and returns per-stratum
intervals. The benefit: when a maneuver category is harder to predict
than another, its interval widens to compensate. Empirical coverage
remains at the nominal (1 − α) level *within* each stratum, which is
exactly the per-category guarantee paper-1 cares about.

The class is split into two layers so it composes cleanly with both
:class:`cgem_ext.surrogate.xgb.XGBSurrogate` and
:class:`cgem_ext.surrogate.xgb.TwoStageXGBSurrogate`:

* The caller is responsible for producing point predictions on the
  calibration slice and the test slice.
* :class:`MondrianSplitConformal` consumes those point predictions
  alongside the true targets (calibration) or the row category (test)
  and returns the bracket bounds.

Reference: Vovk, Lindsay, Nouretdinov, Gammerman (2003), *Mondrian
Confidence Machine*; and the modern reformulation in Romano, Patterson
& Candes (2019), *Conformalized Quantile Regression*.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

DEFAULT_ALPHA = 0.05


@dataclass(frozen=True)
class StratumInfo:
    name: str
    n_calibration: int
    quantile: float


@dataclass(frozen=True)
class MondrianFit:
    alpha: float
    strata: tuple[StratumInfo, ...]
    fallback_quantile: float


class MondrianSplitConformal:
    """Per-stratum split-conformal prediction intervals.

    Workflow::

        cp = MondrianSplitConformal(alpha=0.05).fit(
            cal_predictions=mh_pred_val,    # float ndarray, len = len(val_df)
            cal_targets=val_df["hlap_min"], # float ndarray
            cal_strata=val_df["maneuver_category"],
        )

        lo, hi = cp.predict_interval(
            test_predictions=mh_pred_test,
            test_strata=test_df["maneuver_category"],
        )

    A stratum that does not appear in calibration (rare for our use
    case but possible at deployment time) falls back to the global
    quantile across all calibration scores.
    """

    def __init__(self, *, alpha: float = DEFAULT_ALPHA) -> None:
        if not 0 < alpha < 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        self.alpha = float(alpha)
        self._fit: MondrianFit | None = None
        self._stratum_to_q: dict[str, float] = {}

    def fit(
        self,
        *,
        cal_predictions: np.ndarray,
        cal_targets: np.ndarray | pd.Series,
        cal_strata: np.ndarray | pd.Series,
        min_per_stratum: int = 20,
    ) -> MondrianSplitConformal:
        cal_predictions = np.asarray(cal_predictions, dtype=float)
        cal_targets = np.asarray(cal_targets, dtype=float)
        cal_strata = np.asarray(cal_strata)
        if not (len(cal_predictions) == len(cal_targets) == len(cal_strata)):
            raise ValueError(
                "cal_predictions, cal_targets, cal_strata must be aligned"
            )

        # Drop rows where the target is NaN (censored cases that should be
        # excluded from interval calibration for the time targets).
        finite = np.isfinite(cal_predictions) & np.isfinite(cal_targets)
        if not finite.any():
            raise ValueError("No finite (prediction, target) pairs to calibrate on.")
        cal_predictions = cal_predictions[finite]
        cal_targets = cal_targets[finite]
        cal_strata = cal_strata[finite]

        residuals = np.abs(cal_targets - cal_predictions)

        # Per-stratum quantile with finite-sample correction.
        strata: list[StratumInfo] = []
        self._stratum_to_q.clear()
        for stratum in np.unique(cal_strata):
            mask = cal_strata == stratum
            if mask.sum() < min_per_stratum:
                continue
            r = residuals[mask]
            n = len(r)
            q_level = min(1.0, np.ceil((n + 1) * (1 - self.alpha)) / n)
            q = float(np.quantile(r, q_level, method="higher"))
            self._stratum_to_q[str(stratum)] = q
            strata.append(StratumInfo(name=str(stratum), n_calibration=int(n), quantile=q))

        # Global fallback for unseen strata at inference time.
        n_global = len(residuals)
        q_level = min(1.0, np.ceil((n_global + 1) * (1 - self.alpha)) / n_global)
        fallback_q = float(np.quantile(residuals, q_level, method="higher"))

        self._fit = MondrianFit(
            alpha=self.alpha,
            strata=tuple(strata),
            fallback_quantile=fallback_q,
        )
        return self

    def _check_fitted(self) -> None:
        if self._fit is None:
            raise RuntimeError("MondrianSplitConformal is not fitted yet")

    def predict_interval(
        self,
        *,
        test_predictions: np.ndarray,
        test_strata: np.ndarray | pd.Series,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return ``(lo, hi)`` aligned to ``test_predictions``."""
        self._check_fitted()
        test_predictions = np.asarray(test_predictions, dtype=float)
        test_strata = np.asarray(test_strata)
        if len(test_predictions) != len(test_strata):
            raise ValueError("test_predictions and test_strata must align")

        widths = np.empty_like(test_predictions)
        for i, s in enumerate(test_strata):
            widths[i] = self._stratum_to_q.get(str(s), self._fit.fallback_quantile)  # type: ignore[union-attr]
        return test_predictions - widths, test_predictions + widths

    def coverage(
        self,
        *,
        test_predictions: np.ndarray,
        test_targets: np.ndarray | pd.Series,
        test_strata: np.ndarray | pd.Series,
    ) -> dict[str, float]:
        """Empirical per-stratum coverage on the test slice.

        Returns ``{stratum: coverage_rate, "_overall": rate, "_nominal": 1-alpha}``.
        Useful for tests/test_surrogate.py and the model card.
        """
        lo, hi = self.predict_interval(
            test_predictions=test_predictions, test_strata=test_strata
        )
        targets = np.asarray(test_targets, dtype=float)
        strata = np.asarray(test_strata)
        finite = np.isfinite(targets) & np.isfinite(lo) & np.isfinite(hi)
        out: dict[str, float] = {}
        if not finite.any():
            return {"_overall": float("nan"), "_nominal": 1 - self.alpha}
        in_env = (targets[finite] >= lo[finite]) & (targets[finite] <= hi[finite])
        for stratum in np.unique(strata[finite]):
            mask = strata[finite] == stratum
            if mask.any():
                out[str(stratum)] = float(in_env[mask].mean())
        out["_overall"] = float(in_env.mean())
        out["_nominal"] = 1 - self.alpha
        return out

    @property
    def fit_info(self) -> MondrianFit:
        self._check_fitted()
        return self._fit  # type: ignore[return-value]


__all__ = [
    "DEFAULT_ALPHA",
    "MondrianFit",
    "MondrianSplitConformal",
    "StratumInfo",
]
