"""RandomForest baselines for the surrogate emulator.

Sanity baselines with the same fit/predict API as the XGBoost
surrogates, so paper-1 can publish a fair comparison and `tests/test_surrogate.py`
can swap one for the other in a single line.

These models do not consume the monotonicity hints (sklearn's
RandomForest doesn't support them); the comparison is therefore
intentionally apples-to-oranges in that respect, and the paper
discussion notes that XGBoost's monotonicity is part of the
contribution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from cgem_ext.surrogate.features import extract_features
from cgem_ext.surrogate.targets import TargetSpec, get_target


@dataclass(frozen=True)
class FitInfo:
    target: str
    censored: bool
    n_train: int
    n_train_event: int


_DEFAULT_REGRESSOR = dict(
    n_estimators=400,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    n_jobs=-1,
    random_state=42,
)
_DEFAULT_CLASSIFIER = dict(
    n_estimators=400,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    n_jobs=-1,
    random_state=42,
)


class RFSurrogate:
    """RandomForestRegressor on a continuous target."""

    def __init__(self, target: str, **rf_kwargs) -> None:
        spec = get_target(target)
        if spec.censored:
            raise ValueError(f"{target!r} is censored; use TwoStageRFSurrogate.")
        self.spec: TargetSpec = spec
        params = {**_DEFAULT_REGRESSOR, **rf_kwargs}
        self._regressor = RandomForestRegressor(**params)
        self._fit_info: Optional[FitInfo] = None

    def fit(self, df: pd.DataFrame) -> "RFSurrogate":
        feats = extract_features(df)
        y = df[self.spec.name].astype(float).to_numpy()
        if np.isnan(y).any():
            raise ValueError(f"Target {self.spec.name!r} has NaNs.")
        self._regressor.fit(feats.to_numpy(dtype=float), y)
        self._fit_info = FitInfo(
            target=self.spec.name, censored=False, n_train=int(len(df)), n_train_event=-1
        )
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self._fit_info is None:
            raise RuntimeError("RFSurrogate is not fitted")
        feats = extract_features(df)
        return np.asarray(self._regressor.predict(feats.to_numpy(dtype=float)), dtype=float)

    @property
    def fit_info(self) -> FitInfo:
        if self._fit_info is None:
            raise RuntimeError("RFSurrogate is not fitted")
        return self._fit_info


class TwoStageRFSurrogate:
    """RandomForestClassifier + RandomForestRegressor for censored time targets."""

    def __init__(self, target: str, **rf_kwargs) -> None:
        spec = get_target(target)
        if not spec.censored:
            raise ValueError(f"{target!r} is continuous; use RFSurrogate.")
        self.spec: TargetSpec = spec
        cls_params = {**_DEFAULT_CLASSIFIER, **rf_kwargs.get("classifier_kwargs", {})}
        reg_params = {**_DEFAULT_REGRESSOR, **rf_kwargs.get("regressor_kwargs", {})}
        self._classifier = RandomForestClassifier(**cls_params)
        self._regressor = RandomForestRegressor(**reg_params)
        self._fit_info: Optional[FitInfo] = None

    def fit(self, df: pd.DataFrame) -> "TwoStageRFSurrogate":
        if self.spec.event_column is None:  # pragma: no cover
            raise ValueError(f"{self.spec.name!r} has no event_column declared")
        feats = extract_features(df)
        x = feats.to_numpy(dtype=float)
        events = df[self.spec.event_column].astype(int).to_numpy()
        self._classifier.fit(x, events)
        mask = events == 1
        if mask.sum() < 10:
            raise ValueError(
                f"{self.spec.name!r}: only {mask.sum()} event rows; need >= 10."
            )
        y = df.loc[mask, self.spec.name].astype(float).to_numpy()
        self._regressor.fit(x[mask], y)
        self._fit_info = FitInfo(
            target=self.spec.name,
            censored=True,
            n_train=int(len(df)),
            n_train_event=int(mask.sum()),
        )
        return self

    def predict_event_probability(self, df: pd.DataFrame) -> np.ndarray:
        if self._fit_info is None:
            raise RuntimeError("TwoStageRFSurrogate is not fitted")
        feats = extract_features(df)
        proba = self._classifier.predict_proba(feats.to_numpy(dtype=float))
        # If only one class was seen during training, predict_proba has 1 column.
        if proba.shape[1] == 1:
            only_class = self._classifier.classes_[0]
            return np.full(proba.shape[0], 1.0 if only_class == 1 else 0.0)
        return np.asarray(proba[:, 1], dtype=float)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self._fit_info is None:
            raise RuntimeError("TwoStageRFSurrogate is not fitted")
        feats = extract_features(df)
        return np.asarray(self._regressor.predict(feats.to_numpy(dtype=float)), dtype=float)

    def predict_expected_time(self, df: pd.DataFrame) -> np.ndarray:
        return self.predict_event_probability(df) * self.predict(df)

    @property
    def fit_info(self) -> FitInfo:
        if self._fit_info is None:
            raise RuntimeError("TwoStageRFSurrogate is not fitted")
        return self._fit_info


def build_baseline(target: str, **kwargs) -> RFSurrogate | TwoStageRFSurrogate:
    spec = get_target(target)
    if spec.censored:
        return TwoStageRFSurrogate(target, **kwargs)
    return RFSurrogate(target, **kwargs)


__all__ = [
    "FitInfo",
    "RFSurrogate",
    "TwoStageRFSurrogate",
    "build_baseline",
]
