"""Mahalanobis-distance OOD detector.

Robust covariance estimate (``sklearn.covariance.MinCovDet``) over the
fixed feature space defined in :mod:`cgem_ext.ood.features`. The
in-distribution envelope is the χ²(df, 0.95) cutoff on squared
Mahalanobis distance, where ``df`` equals the rank-effective feature
dimension. Pre-registered as the primary OOD backbone in
``docs/publication/osf_preregistration.md``.

The class is deliberately small. It exposes:

    fit(df)              — fit the MinCovDet on a labelled DataFrame
    score(df)            — squared Mahalanobis distance per row
    is_in_envelope(df)   — boolean array using the χ² threshold
    threshold_chi2       — the χ² cutoff (computed at fit time)
    feature_columns      — the ordered feature list (stable contract)

A small ``support_fraction`` is *not* used: we let ``MinCovDet`` choose
its default (``0.5 * (n_samples + n_features + 1) / n_samples``) which
is the canonical robust setting from Rousseeuw and Van Driessen (1999).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.covariance import MinCovDet

from cgem_ext.ood.features import FEATURE_COLUMNS, extract_features

DEFAULT_ALPHA = 0.05  # χ² right-tail mass; threshold = chi2.ppf(1-alpha, df)


@dataclass(frozen=True)
class FitInfo:
    """Diagnostic snapshot from a fit, for logging and the model card."""

    n_train: int
    n_features: int
    rank_effective: int
    threshold_chi2: float
    support_fraction: float
    location_norm: float


class MahalanobisOOD:
    """Robust-covariance Mahalanobis OOD detector.

    The fitted ``MinCovDet`` carries the location and scatter; we keep it
    around so callers can inspect ``.location_`` and ``.covariance_`` if
    they need to. Detector state can be persisted via ``joblib.dump`` on
    the instance — but at this size the practical workflow is to refit
    on demand.
    """

    feature_columns: tuple[str, ...] = FEATURE_COLUMNS

    def __init__(self, *, alpha: float = DEFAULT_ALPHA, random_state: int = 0) -> None:
        if not 0 < alpha < 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        self.alpha = float(alpha)
        self.random_state = int(random_state)
        self._mcd: MinCovDet | None = None
        self._threshold: float | None = None
        self._fit_info: FitInfo | None = None
        self._effective_columns: tuple[str, ...] | None = None

    # ── Fit / score ─────────────────────────────────────────────────

    def fit(self, df: pd.DataFrame) -> MahalanobisOOD:
        """Fit the robust covariance on the in-distribution slice ``df``.

        Constant columns (zero variance) are dropped from the feature
        matrix because ``MinCovDet`` will refuse to invert a singular
        scatter. The χ² degrees of freedom equal the number of retained
        columns. The dropped columns are recorded so ``score`` re-applies
        the same projection.
        """
        feats = extract_features(df)
        # Identify columns with non-zero variance on the training slice.
        variances = feats.var(axis=0, ddof=0)
        keep = [c for c in FEATURE_COLUMNS if variances.get(c, 0.0) > 1e-12]
        if len(keep) < 2:
            raise ValueError(
                f"Mahalanobis fit requires >= 2 non-constant features; "
                f"only {keep} survived."
            )
        x = feats[keep].to_numpy(dtype=float)
        mcd = MinCovDet(random_state=self.random_state)
        mcd.fit(x)

        self._mcd = mcd
        self._effective_columns = tuple(keep)
        df_eff = len(keep)
        self._threshold = float(chi2.ppf(1 - self.alpha, df=df_eff))
        self._fit_info = FitInfo(
            n_train=int(x.shape[0]),
            n_features=len(FEATURE_COLUMNS),
            rank_effective=df_eff,
            threshold_chi2=self._threshold,
            support_fraction=float(getattr(mcd, "support_fraction", float("nan")) or 0.0),
            location_norm=float(np.linalg.norm(mcd.location_)),
        )
        return self

    def _check_fitted(self) -> None:
        if self._mcd is None or self._threshold is None or self._effective_columns is None:
            raise RuntimeError("MahalanobisOOD instance is not fitted yet")

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Return the squared Mahalanobis distance for each row of ``df``.

        Higher = more out-of-distribution.
        """
        self._check_fitted()
        feats = extract_features(df)
        x = feats[list(self._effective_columns)].to_numpy(dtype=float)  # type: ignore[arg-type]
        return np.asarray(self._mcd.mahalanobis(x), dtype=float)  # type: ignore[union-attr]

    def is_in_envelope(self, df: pd.DataFrame) -> np.ndarray:
        """Boolean per row: ``True`` iff squared distance ≤ threshold."""
        return self.score(df) <= self.threshold_chi2

    # ── Properties ──────────────────────────────────────────────────

    @property
    def threshold_chi2(self) -> float:
        self._check_fitted()
        return self._threshold  # type: ignore[return-value]

    @property
    def fit_info(self) -> FitInfo:
        self._check_fitted()
        return self._fit_info  # type: ignore[return-value]

    @property
    def effective_columns(self) -> tuple[str, ...]:
        self._check_fitted()
        return self._effective_columns  # type: ignore[return-value]

    @property
    def location_(self) -> np.ndarray:
        self._check_fitted()
        return np.asarray(self._mcd.location_, dtype=float)  # type: ignore[union-attr]

    @property
    def covariance_(self) -> np.ndarray:
        self._check_fitted()
        return np.asarray(self._mcd.covariance_, dtype=float)  # type: ignore[union-attr]


# ── Convenience entry point ──────────────────────────────────────────


def is_in_envelope(
    train_df: pd.DataFrame, query_df: pd.DataFrame, *, alpha: float = DEFAULT_ALPHA
) -> np.ndarray:
    """One-shot helper: fit on ``train_df`` and return per-row booleans for ``query_df``."""
    return MahalanobisOOD(alpha=alpha).fit(train_df).is_in_envelope(query_df)


__all__ = [
    "DEFAULT_ALPHA",
    "FitInfo",
    "MahalanobisOOD",
    "is_in_envelope",
]
