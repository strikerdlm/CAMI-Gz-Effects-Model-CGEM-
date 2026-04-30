"""Isolation Forest baseline OOD detector.

Fair-comparison baseline against ``MahalanobisOOD``. Same interface
(``fit``, ``score``, ``is_in_envelope``), default sklearn hyperparameters
as pre-registered. Scores are negated decision-function values so that
*higher = more OOD*, matching :class:`MahalanobisOOD`'s convention. The
in-envelope mask uses the IsolationForest's ``predict`` (1 = inlier).

The conformal-abstention layer (:mod:`cgem_ext.ood.conformal`) can be
stacked on top of this detector identically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from cgem_ext.ood.features import FEATURE_COLUMNS, extract_features


@dataclass(frozen=True)
class BaselineFitInfo:
    n_train: int
    n_features: int
    contamination: float | str
    n_estimators: int


class IsolationForestOOD:
    """sklearn IsolationForest baseline for the OOD detector evaluation."""

    feature_columns: tuple[str, ...] = FEATURE_COLUMNS

    def __init__(
        self,
        *,
        n_estimators: int = 100,
        contamination: float | str = "auto",
        random_state: int = 0,
    ) -> None:
        self.n_estimators = int(n_estimators)
        self.contamination = contamination
        self.random_state = int(random_state)
        self._model: Optional[IsolationForest] = None
        self._fit_info: Optional[BaselineFitInfo] = None

    def fit(self, df: pd.DataFrame) -> "IsolationForestOOD":
        feats = extract_features(df)
        x = feats.to_numpy(dtype=float)
        model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
        )
        model.fit(x)
        self._model = model
        self._fit_info = BaselineFitInfo(
            n_train=int(x.shape[0]),
            n_features=int(x.shape[1]),
            contamination=self.contamination,
            n_estimators=self.n_estimators,
        )
        return self

    def _check_fitted(self) -> None:
        if self._model is None:
            raise RuntimeError("IsolationForestOOD instance is not fitted yet")

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Return per-row OOD score; higher = more OOD."""
        self._check_fitted()
        feats = extract_features(df)
        x = feats.to_numpy(dtype=float)
        # decision_function is positive for inliers and negative for outliers;
        # negate so the convention matches MahalanobisOOD (higher = more OOD).
        return -np.asarray(self._model.decision_function(x), dtype=float)  # type: ignore[union-attr]

    def is_in_envelope(self, df: pd.DataFrame) -> np.ndarray:
        """Boolean per row using IsolationForest's own predict (1 = inlier)."""
        self._check_fitted()
        feats = extract_features(df)
        x = feats.to_numpy(dtype=float)
        return np.asarray(self._model.predict(x), dtype=int) == 1  # type: ignore[union-attr]

    @property
    def fit_info(self) -> BaselineFitInfo:
        self._check_fitted()
        return self._fit_info  # type: ignore[return-value]


__all__ = ["BaselineFitInfo", "IsolationForestOOD"]
