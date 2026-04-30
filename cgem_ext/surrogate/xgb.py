"""XGBoost surrogate emulators for CGEM outputs.

Two flavours of model:

* :class:`XGBSurrogate` — single XGBoost regressor for a continuous
  target (``hlap_min``, ``c_bank_min``).
* :class:`TwoStageXGBSurrogate` — XGBoost classifier for the event flag
  followed by an XGBoost regressor on the time conditional on the event,
  for the right-censored time targets (``time_to_*``).

Both classes use the per-target monotonicity vectors from
:mod:`cgem_ext.surrogate.targets`. The default hyperparameters are
deliberately conservative: 400 trees, depth 6, eta 0.05, subsample 0.9.
A formal Optuna search is deferred to ``scripts/optuna_search.py``
(Phase-3 polish); the OSF preregistration locks the hyperparameter
search space at posting time.

Both APIs return a flat ``np.ndarray`` of point predictions per row
(``predict``) and, for the two-stage model, an additional event-
probability vector (``predict_event_probability``). The Mondrian
conformal layer (:mod:`cgem_ext.surrogate.conformal`) consumes those
arrays unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from xgboost import XGBClassifier, XGBRegressor

from cgem_ext.surrogate.features import extract_features
from cgem_ext.surrogate.targets import TargetSpec, get_target

# ── Default hyperparameters ──────────────────────────────────────────


def _default_regressor_params(monotonicity: tuple[int, ...]) -> dict:
    return dict(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
        monotone_constraints=tuple(monotonicity),
        verbosity=0,
    )


def _default_classifier_params() -> dict:
    return dict(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
        verbosity=0,
        eval_metric="logloss",
    )


# ── Shared bookkeeping ───────────────────────────────────────────────


@dataclass(frozen=True)
class FitInfo:
    target: str
    censored: bool
    n_train: int
    n_train_event: int  # event_col == 1 count (None for continuous targets)
    feature_columns: tuple[str, ...]


# ── Single-stage continuous surrogate ────────────────────────────────


class XGBSurrogate:
    """Single XGBoost regressor for one continuous CGEM target.

    Parameters
    ----------
    target : str
        Name of the target column. Must be a continuous (non-censored)
        target from :mod:`cgem_ext.surrogate.targets`.
    **xgb_kwargs
        Override default XGBRegressor kwargs.
    """

    def __init__(self, target: str, **xgb_kwargs) -> None:
        spec = get_target(target)
        if spec.censored:
            raise ValueError(
                f"{target!r} is censored; use TwoStageXGBSurrogate instead."
            )
        self.spec: TargetSpec = spec
        params = _default_regressor_params(spec.monotonicity)
        params.update(xgb_kwargs)
        self._regressor = XGBRegressor(**params)
        self._fit_info: FitInfo | None = None

    def fit(self, df: pd.DataFrame) -> XGBSurrogate:
        feats = extract_features(df)
        y = df[self.spec.name].astype(float).to_numpy()
        if np.isnan(y).any():
            raise ValueError(
                f"Continuous target {self.spec.name!r} has NaNs; "
                f"continuous targets must be fully observed."
            )
        self._regressor.fit(feats.to_numpy(dtype=float), y)
        self._fit_info = FitInfo(
            target=self.spec.name,
            censored=False,
            n_train=len(df),
            n_train_event=-1,
            feature_columns=tuple(feats.columns.tolist()),
        )
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self._fit_info is None:
            raise RuntimeError("XGBSurrogate is not fitted")
        feats = extract_features(df)
        return self.predict_array(feats.to_numpy(dtype=float))

    def predict_array(self, x: np.ndarray) -> np.ndarray:
        """Predict from an already-encoded FEATURE_COLUMNS-aligned matrix.

        Used by sensitivity / SHAP runners that build the feature matrix
        themselves (e.g. via ``cgem_ext.sensitivity._build_inference_matrix``)
        and don't have raw dataset columns to feed ``extract_features``.
        """
        if self._fit_info is None:
            raise RuntimeError("XGBSurrogate is not fitted")
        return np.asarray(self._regressor.predict(np.asarray(x, dtype=float)), dtype=float)

    @property
    def fit_info(self) -> FitInfo:
        if self._fit_info is None:
            raise RuntimeError("XGBSurrogate is not fitted")
        return self._fit_info


# ── Two-stage censored surrogate ─────────────────────────────────────


class TwoStageXGBSurrogate:
    """Classifier + regressor for a right-censored time target.

    Stage 1 (``self._classifier``): XGBoost classifier on the binary
    ``event_*`` flag.
    Stage 2 (``self._regressor``): XGBoost regressor on the time, fit
    only on rows where ``event_* == 1``.

    Two prediction paths:

    - :meth:`predict_event_probability` — P(event) from stage 1.
    - :meth:`predict` — conditional time E[time | event=1] from stage 2.

    The expected time E[time] = P(event) * E[time | event=1] is provided
    by :meth:`predict_expected_time` for downstream consumers that want
    a single scalar per row.
    """

    def __init__(self, target: str, **xgb_kwargs) -> None:
        spec = get_target(target)
        if not spec.censored:
            raise ValueError(
                f"{target!r} is continuous; use XGBSurrogate instead."
            )
        self.spec: TargetSpec = spec
        cls_params = _default_classifier_params()
        cls_params.update(xgb_kwargs.get("classifier_kwargs", {}))
        reg_params = _default_regressor_params(spec.monotonicity)
        reg_params.update(xgb_kwargs.get("regressor_kwargs", {}))
        self._classifier = XGBClassifier(**cls_params)
        self._regressor = XGBRegressor(**reg_params)
        self._fit_info: FitInfo | None = None

    def fit(self, df: pd.DataFrame) -> TwoStageXGBSurrogate:
        if self.spec.event_column is None:  # pragma: no cover  (defensive)
            raise ValueError(f"{self.spec.name!r} has no event_column declared")
        feats = extract_features(df)
        x = feats.to_numpy(dtype=float)
        events = df[self.spec.event_column].astype(int).to_numpy()
        # Stage 1: fit classifier on all rows.
        self._classifier.fit(x, events)
        # Stage 2: fit regressor only on event=1 rows.
        mask = events == 1
        if mask.sum() < 10:
            raise ValueError(
                f"{self.spec.name!r}: only {mask.sum()} event rows available; "
                f"need >= 10 to fit the conditional regressor."
            )
        y = df.loc[mask, self.spec.name].astype(float).to_numpy()
        if np.isnan(y).any():
            raise ValueError(
                f"{self.spec.name!r}: time target carries NaN on event=1 rows; "
                f"the dataset is malformed."
            )
        self._regressor.fit(x[mask], y)
        self._fit_info = FitInfo(
            target=self.spec.name,
            censored=True,
            n_train=len(df),
            n_train_event=int(mask.sum()),
            feature_columns=tuple(feats.columns.tolist()),
        )
        return self

    def predict_event_probability(self, df: pd.DataFrame) -> np.ndarray:
        """Return P(event=1) per row."""
        if self._fit_info is None:
            raise RuntimeError("TwoStageXGBSurrogate is not fitted")
        feats = extract_features(df)
        return self.predict_event_probability_array(feats.to_numpy(dtype=float))

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Return E[time | event=1] per row (conditional on the event)."""
        if self._fit_info is None:
            raise RuntimeError("TwoStageXGBSurrogate is not fitted")
        feats = extract_features(df)
        return self.predict_array(feats.to_numpy(dtype=float))

    def predict_array(self, x: np.ndarray) -> np.ndarray:
        """Conditional time E[time | event=1] from a FEATURE_COLUMNS-aligned matrix."""
        if self._fit_info is None:
            raise RuntimeError("TwoStageXGBSurrogate is not fitted")
        return np.asarray(self._regressor.predict(np.asarray(x, dtype=float)), dtype=float)

    def predict_event_probability_array(self, x: np.ndarray) -> np.ndarray:
        """P(event=1) from a FEATURE_COLUMNS-aligned matrix."""
        if self._fit_info is None:
            raise RuntimeError("TwoStageXGBSurrogate is not fitted")
        proba = self._classifier.predict_proba(np.asarray(x, dtype=float))
        return np.asarray(proba[:, 1], dtype=float)

    def predict_expected_time_array(self, x: np.ndarray) -> np.ndarray:
        """E[time] = P(event) * E[time | event=1] from a FEATURE_COLUMNS-aligned matrix."""
        return self.predict_event_probability_array(x) * self.predict_array(x)

    def predict_expected_time(self, df: pd.DataFrame) -> np.ndarray:
        """Return E[time] = P(event) * E[time | event=1] per row.

        For rows where the model assigns negligible event probability
        the expected time will be near zero; downstream consumers should
        check the event probability before using the expected-time
        scalar as a "time-to-event" prediction.
        """
        return self.predict_event_probability(df) * self.predict(df)

    @property
    def fit_info(self) -> FitInfo:
        if self._fit_info is None:
            raise RuntimeError("TwoStageXGBSurrogate is not fitted")
        return self._fit_info


# ── Convenience factory ──────────────────────────────────────────────


def build_surrogate(target: str, **kwargs) -> XGBSurrogate | TwoStageXGBSurrogate:
    """Return the appropriate surrogate type for the given target."""
    spec = get_target(target)
    if spec.censored:
        return TwoStageXGBSurrogate(target, **kwargs)
    return XGBSurrogate(target, **kwargs)


__all__ = [
    "FitInfo",
    "TwoStageXGBSurrogate",
    "XGBSurrogate",
    "build_surrogate",
]
