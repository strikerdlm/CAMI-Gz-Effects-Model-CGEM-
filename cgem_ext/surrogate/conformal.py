"""Mondrian split-conformal prediction intervals for the surrogate.

Two flavours of Mondrian-stratified conformal calibration are exposed:

* :class:`MondrianSplitConformal` — homoscedastic split-conformal on
  absolute residuals. The interval is symmetric around the point
  prediction and has a constant width *within each stratum*.
* :class:`MondrianCQR` — Conformalized Quantile Regression (Romano,
  Patterson & Candès 2019). The caller supplies lower- and upper-
  quantile predictions; the calibration step adjusts the bracket so
  that empirical (1 − α) coverage holds within each stratum, but the
  bracket *width* is allowed to vary with the input. CQR is the
  preferred layer when the conditional target distribution is
  heteroscedastic — for the CGEM time-to-G-LOC target the
  homoscedastic Mondrian under-covers (0.861 vs nominal 0.95), which
  CQR is designed to fix.

Both classes share the per-stratum (1 − α) quantile machinery via the
private :func:`_per_stratum_quantile` helper at module level.

The classes are split into layers so they compose cleanly with both
:class:`cgem_ext.surrogate.xgb.XGBSurrogate` /
:class:`cgem_ext.surrogate.xgb.TwoStageXGBSurrogate` (point predictors
fed to :class:`MondrianSplitConformal`) and the new
:class:`cgem_ext.surrogate.cqr.XGBQuantileSurrogate` /
:class:`cgem_ext.surrogate.cqr.TwoStageXGBQuantileSurrogate` (quantile
predictors fed to :class:`MondrianCQR`).

References:

* Vovk, Lindsay, Nouretdinov, Gammerman (2003), *Mondrian Confidence
  Machine*.
* Romano, Patterson & Candès (2019), *Conformalized Quantile
  Regression*, NeurIPS 32.
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


def _per_stratum_quantile(
    scores: np.ndarray | pd.Series,
    strata: np.ndarray | pd.Series,
    *,
    alpha: float,
    min_per_stratum: int,
) -> tuple[dict[str, float], float, list[StratumInfo]]:
    """Compute per-stratum and global (1 − α) quantiles with finite-sample
    correction.

    Strata with fewer than ``min_per_stratum`` calibration scores are
    omitted from the per-stratum dictionary; at inference time, rows
    in those strata fall back to the global quantile.

    The finite-sample correction follows Vovk et al. (2003) and Romano
    et al. (2019): the empirical quantile level is
    ``ceil((n + 1)(1 − α)) / n``. ``method="higher"`` is used to round
    upward to the nearest score, preserving conservative coverage.

    Scores can be negative (e.g., CQR conformity scores when the target
    is interior to the predicted interval); only finite values are used.
    """
    scores = np.asarray(scores, dtype=float)
    strata = np.asarray(strata)
    if len(scores) != len(strata):
        raise ValueError("scores and strata must align")
    finite = np.isfinite(scores)
    if not finite.any():
        raise ValueError("no finite scores available for calibration")
    scores = scores[finite]
    strata = strata[finite]

    stratum_to_q: dict[str, float] = {}
    info_list: list[StratumInfo] = []
    for stratum in np.unique(strata):
        mask = strata == stratum
        n = int(mask.sum())
        if n < min_per_stratum:
            continue
        s = scores[mask]
        q_level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
        q = float(np.quantile(s, q_level, method="higher"))
        stratum_to_q[str(stratum)] = q
        info_list.append(StratumInfo(name=str(stratum), n_calibration=n, quantile=q))

    n_global = len(scores)
    q_level_global = min(1.0, np.ceil((n_global + 1) * (1 - alpha)) / n_global)
    fallback_q = float(np.quantile(scores, q_level_global, method="higher"))

    return stratum_to_q, fallback_q, info_list


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

        stratum_to_q, fallback_q, strata = _per_stratum_quantile(
            residuals,
            cal_strata,
            alpha=self.alpha,
            min_per_stratum=min_per_stratum,
        )
        self._stratum_to_q = stratum_to_q
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


class MondrianCQR:
    """Per-stratum Conformalized Quantile Regression.

    The caller supplies lower- and upper-quantile predictions on the
    calibration slice and the test slice. The conformity score for a
    calibration row is::

        s_i = max(q_lo_i - y_i, y_i - q_hi_i)

    which is negative when the target is interior to the predicted
    interval and positive when it is outside. The per-stratum
    (1 − α) quantile of these scores is used at inference time to
    inflate (or deflate) the bracket::

        [q_lo(x) - q_s, q_hi(x) + q_s]

    where ``q_s`` is the per-stratum quantile (or the global fallback
    for unseen strata).

    The width of the bracket is allowed to vary with x — that is the
    advantage over :class:`MondrianSplitConformal` for heteroscedastic
    targets such as ``time_to_gloc_s``.

    Empirical (1 − α) coverage is preserved within each stratum that
    meets ``min_per_stratum`` calibration rows; the finite-sample
    correction matches Romano et al. (2019, Eq. 3).

    Reference: Romano, Patterson & Candès (2019), *Conformalized
    Quantile Regression*, NeurIPS 32.
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
        cal_q_lo: np.ndarray,
        cal_q_hi: np.ndarray,
        cal_targets: np.ndarray | pd.Series,
        cal_strata: np.ndarray | pd.Series,
        min_per_stratum: int = 20,
    ) -> MondrianCQR:
        cal_q_lo = np.asarray(cal_q_lo, dtype=float)
        cal_q_hi = np.asarray(cal_q_hi, dtype=float)
        cal_targets = np.asarray(cal_targets, dtype=float)
        cal_strata = np.asarray(cal_strata)
        if not (
            len(cal_q_lo) == len(cal_q_hi) == len(cal_targets) == len(cal_strata)
        ):
            raise ValueError(
                "cal_q_lo, cal_q_hi, cal_targets, cal_strata must be aligned"
            )

        finite = (
            np.isfinite(cal_q_lo)
            & np.isfinite(cal_q_hi)
            & np.isfinite(cal_targets)
        )
        if not finite.any():
            raise ValueError(
                "no finite (q_lo, q_hi, target) tuples to calibrate on"
            )
        cal_q_lo = cal_q_lo[finite]
        cal_q_hi = cal_q_hi[finite]
        cal_targets = cal_targets[finite]
        cal_strata = cal_strata[finite]

        # Romano et al. (2019), Eq. 1: s = max(q_lo - y, y - q_hi).
        scores = np.maximum(cal_q_lo - cal_targets, cal_targets - cal_q_hi)

        stratum_to_q, fallback_q, strata = _per_stratum_quantile(
            scores,
            cal_strata,
            alpha=self.alpha,
            min_per_stratum=min_per_stratum,
        )
        self._stratum_to_q = stratum_to_q
        self._fit = MondrianFit(
            alpha=self.alpha,
            strata=tuple(strata),
            fallback_quantile=fallback_q,
        )
        return self

    def _check_fitted(self) -> None:
        if self._fit is None:
            raise RuntimeError("MondrianCQR is not fitted yet")

    def predict_interval(
        self,
        *,
        test_q_lo: np.ndarray,
        test_q_hi: np.ndarray,
        test_strata: np.ndarray | pd.Series,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return ``(lo, hi)`` aligned to ``test_q_lo`` / ``test_q_hi``."""
        self._check_fitted()
        test_q_lo = np.asarray(test_q_lo, dtype=float)
        test_q_hi = np.asarray(test_q_hi, dtype=float)
        test_strata = np.asarray(test_strata)
        if not (len(test_q_lo) == len(test_q_hi) == len(test_strata)):
            raise ValueError("test_q_lo, test_q_hi, test_strata must align")

        widths = np.empty_like(test_q_lo)
        for i, s in enumerate(test_strata):
            widths[i] = self._stratum_to_q.get(
                str(s), self._fit.fallback_quantile  # type: ignore[union-attr]
            )
        return test_q_lo - widths, test_q_hi + widths

    def coverage(
        self,
        *,
        test_q_lo: np.ndarray,
        test_q_hi: np.ndarray,
        test_targets: np.ndarray | pd.Series,
        test_strata: np.ndarray | pd.Series,
    ) -> dict[str, float]:
        """Empirical per-stratum coverage on the test slice.

        Returns ``{stratum: coverage_rate, "_overall": rate, "_nominal": 1-alpha}``,
        matching :meth:`MondrianSplitConformal.coverage` for downstream
        consumers (model-card scripts, paper-1 figures).
        """
        lo, hi = self.predict_interval(
            test_q_lo=test_q_lo, test_q_hi=test_q_hi, test_strata=test_strata
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
    "MondrianCQR",
    "MondrianFit",
    "MondrianSplitConformal",
    "StratumInfo",
]
