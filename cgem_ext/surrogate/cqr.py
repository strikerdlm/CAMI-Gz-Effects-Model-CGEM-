"""XGBoost quantile-regression surrogates with Conformalized Quantile
Regression (CQR) calibration.

Two flavours of surrogate, mirroring :mod:`cgem_ext.surrogate.xgb`:

* :class:`XGBQuantileSurrogate` — three XGBoost quantile regressors
  (lower α/2, median, upper 1 − α/2) sharing the per-target monotonicity
  vectors from :mod:`cgem_ext.surrogate.targets`, plus a
  :class:`MondrianCQR` calibration layer. Replaces
  :class:`cgem_ext.surrogate.xgb.XGBSurrogate` +
  :class:`cgem_ext.surrogate.conformal.MondrianSplitConformal` for
  continuous targets when the conditional target distribution is
  heteroscedastic and a homoscedastic interval would over- or
  under-cover.
* :class:`TwoStageXGBQuantileSurrogate` — same two-stage classifier-
  then-regressor pattern as
  :class:`cgem_ext.surrogate.xgb.TwoStageXGBSurrogate`, but the
  conditional regressor is :class:`XGBQuantileSurrogate`. The motivating
  use case is the ``time_to_gloc_s`` target, where the existing
  homoscedastic Mondrian conformal layer under-covers (0.861 vs nominal
  0.95) on event-positive rows.

XGBoost 2.0+ exposes the quantile loss via ``objective="reg:quantileerror"``
with ``quantile_alpha`` and ``tree_method="hist"``. Monotonicity
constraints are applied per quantile head; non-crossing of the quantile
heads is not guaranteed by XGBoost, so the predicted ``(q_lo, q_hi)``
pair is post-hoc sorted via ``np.minimum`` / ``np.maximum`` to keep the
CQR conformity score well-defined.

Reference:

* Romano, Patterson & Candès (2019), *Conformalized Quantile
  Regression*, NeurIPS 32.
* Chen & Guestrin (2016), *XGBoost: a scalable tree boosting system*.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from xgboost import XGBClassifier, XGBRegressor

from cgem_ext.surrogate.conformal import DEFAULT_ALPHA, MondrianCQR
from cgem_ext.surrogate.features import extract_features
from cgem_ext.surrogate.targets import TargetSpec, get_target


def _quantile_regressor_params(
    *, monotonicity: tuple[int, ...], quantile_alpha: float
) -> dict:
    """Default XGBoost params for a single quantile regressor.

    Mirrors :func:`cgem_ext.surrogate.xgb._default_regressor_params`
    except that ``objective`` and ``quantile_alpha`` switch on the
    quantile loss. ``tree_method="hist"`` is required for the quantile
    objective in XGBoost 2.x.
    """
    return dict(
        objective="reg:quantileerror",
        quantile_alpha=float(quantile_alpha),
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
    """Mirror :func:`cgem_ext.surrogate.xgb._default_classifier_params`."""
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


@dataclass(frozen=True)
class CQRFitInfo:
    target: str
    censored: bool
    alpha: float
    n_train: int
    n_train_event: int
    n_calibration: int
    feature_columns: tuple[str, ...]


class XGBQuantileSurrogate:
    """Three XGBoost quantile regressors + Mondrian-CQR calibration.

    Workflow::

        sur = XGBQuantileSurrogate(target="hlap_min", alpha=0.05)
        sur.fit(train_df=train, calibration_df=val)
        median = sur.predict(test_df)
        lo, hi = sur.predict_interval(test_df)

    The three heads are trained on ``train_df`` only; the calibration
    layer consumes ``calibration_df`` (the held-out validation slice).
    The median head doubles as the point predictor, so ``predict``
    returns a single point estimate. ``predict_interval`` runs through
    :class:`MondrianCQR` and returns the calibrated bracket.

    Parameters
    ----------
    target : str
        Continuous target name from :mod:`cgem_ext.surrogate.targets`.
    alpha : float, default 0.05
        Miscoverage level. Lower / upper quantile heads train at
        ``alpha / 2`` and ``1 - alpha / 2``.
    **xgb_kwargs
        Override defaults; merged into each head's hyperparameters.

    Notes
    -----
    Quantile crossing — ``q_lo > q_hi`` for a single row — is possible
    when the monotonicity constraints are tight relative to the target
    structure. After raw prediction we sort ``(q_lo, q_hi)`` row-wise
    to keep the CQR conformity score well-defined; this is equivalent
    to taking the marginal envelope of the two heads.
    """

    def __init__(
        self, target: str, *, alpha: float = DEFAULT_ALPHA, **xgb_kwargs
    ) -> None:
        spec = get_target(target)
        if spec.censored:
            raise ValueError(
                f"{target!r} is censored; use TwoStageXGBQuantileSurrogate "
                f"instead."
            )
        self._init_from_spec(spec=spec, alpha=alpha, **xgb_kwargs)

    @classmethod
    def _from_spec_unchecked(
        cls,
        *,
        spec: TargetSpec,
        alpha: float = DEFAULT_ALPHA,
        **xgb_kwargs,
    ) -> XGBQuantileSurrogate:
        """Construct from a (possibly proxy) spec without the censored check.

        Used internally by :class:`TwoStageXGBQuantileSurrogate` to wrap
        the conditional event-positive regressor without tripping the
        constructor's censored guard.
        """
        instance = cls.__new__(cls)
        instance._init_from_spec(spec=spec, alpha=alpha, **xgb_kwargs)
        return instance

    def _init_from_spec(
        self, *, spec: TargetSpec, alpha: float, **xgb_kwargs
    ) -> None:
        if not 0 < alpha < 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        self.spec: TargetSpec = spec
        self.alpha = float(alpha)
        lo_alpha = alpha / 2.0
        hi_alpha = 1.0 - alpha / 2.0
        lo_params = _quantile_regressor_params(
            monotonicity=spec.monotonicity, quantile_alpha=lo_alpha
        )
        hi_params = _quantile_regressor_params(
            monotonicity=spec.monotonicity, quantile_alpha=hi_alpha
        )
        med_params = _quantile_regressor_params(
            monotonicity=spec.monotonicity, quantile_alpha=0.5
        )
        for params in (lo_params, hi_params, med_params):
            params.update(xgb_kwargs)
        self._regressor_lo = XGBRegressor(**lo_params)
        self._regressor_hi = XGBRegressor(**hi_params)
        self._regressor_med = XGBRegressor(**med_params)
        self._cqr: MondrianCQR | None = None
        self._fit_info: CQRFitInfo | None = None

    def fit(
        self,
        train_df: pd.DataFrame,
        *,
        calibration_df: pd.DataFrame,
        stratum_column: str = "maneuver_category",
    ) -> XGBQuantileSurrogate:
        train_feats = extract_features(train_df)
        x_train = train_feats.to_numpy(dtype=float)
        y_train = train_df[self.spec.name].astype(float).to_numpy()
        if np.isnan(y_train).any():
            raise ValueError(
                f"Continuous target {self.spec.name!r} has NaNs in train_df; "
                f"continuous targets must be fully observed."
            )
        self._regressor_lo.fit(x_train, y_train)
        self._regressor_med.fit(x_train, y_train)
        self._regressor_hi.fit(x_train, y_train)

        # Calibrate the CQR layer on the held-out calibration slice.
        cal_feats = extract_features(calibration_df)
        x_cal = cal_feats.to_numpy(dtype=float)
        y_cal = calibration_df[self.spec.name].astype(float).to_numpy()
        if stratum_column not in calibration_df.columns:
            raise ValueError(
                f"calibration_df missing stratum column {stratum_column!r}"
            )
        cal_strata = calibration_df[stratum_column].to_numpy()

        q_lo_cal, q_hi_cal = self._predict_quantiles_array(x_cal)

        self._cqr = MondrianCQR(alpha=self.alpha).fit(
            cal_q_lo=q_lo_cal,
            cal_q_hi=q_hi_cal,
            cal_targets=y_cal,
            cal_strata=cal_strata,
        )
        self._fit_info = CQRFitInfo(
            target=self.spec.name,
            censored=False,
            alpha=self.alpha,
            n_train=len(train_df),
            n_train_event=-1,
            n_calibration=len(calibration_df),
            feature_columns=tuple(train_feats.columns.tolist()),
        )
        return self

    def _check_fitted(self) -> None:
        if self._fit_info is None or self._cqr is None:
            raise RuntimeError("XGBQuantileSurrogate is not fitted")

    def _predict_quantiles_array(
        self, x: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Predict raw lower/upper quantiles, sorted to enforce non-crossing."""
        x = np.asarray(x, dtype=float)
        q_lo_raw = np.asarray(self._regressor_lo.predict(x), dtype=float)
        q_hi_raw = np.asarray(self._regressor_hi.predict(x), dtype=float)
        # Quantile crossing guard: enforce q_lo <= q_hi row-wise.
        q_lo = np.minimum(q_lo_raw, q_hi_raw)
        q_hi = np.maximum(q_lo_raw, q_hi_raw)
        return q_lo, q_hi

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Return the median (point) prediction per row."""
        self._check_fitted()
        feats = extract_features(df)
        return self.predict_array(feats.to_numpy(dtype=float))

    def predict_array(self, x: np.ndarray) -> np.ndarray:
        """Median prediction from a FEATURE_COLUMNS-aligned matrix."""
        self._check_fitted()
        return np.asarray(
            self._regressor_med.predict(np.asarray(x, dtype=float)),
            dtype=float,
        )

    def predict_quantiles(
        self, df: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return raw, uncalibrated ``(q_lo, q_hi)`` per row.

        Useful for diagnostics — the CQR conformity score depends on
        the raw heads, and the calibrated bracket from
        :meth:`predict_interval` differs by the per-stratum quantile
        offset.
        """
        self._check_fitted()
        feats = extract_features(df)
        return self._predict_quantiles_array(feats.to_numpy(dtype=float))

    def predict_interval(
        self,
        df: pd.DataFrame,
        *,
        stratum_column: str = "maneuver_category",
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calibrated CQR bracket per row."""
        self._check_fitted()
        if stratum_column not in df.columns:
            raise ValueError(f"df missing stratum column {stratum_column!r}")
        feats = extract_features(df)
        q_lo, q_hi = self._predict_quantiles_array(feats.to_numpy(dtype=float))
        strata = df[stratum_column].to_numpy()
        return self._cqr.predict_interval(  # type: ignore[union-attr]
            test_q_lo=q_lo, test_q_hi=q_hi, test_strata=strata
        )

    def coverage(
        self,
        df: pd.DataFrame,
        *,
        stratum_column: str = "maneuver_category",
    ) -> dict[str, float]:
        """Empirical per-stratum coverage on a held-out slice."""
        self._check_fitted()
        feats = extract_features(df)
        q_lo, q_hi = self._predict_quantiles_array(feats.to_numpy(dtype=float))
        strata = df[stratum_column].to_numpy()
        targets = df[self.spec.name].astype(float).to_numpy()
        return self._cqr.coverage(  # type: ignore[union-attr]
            test_q_lo=q_lo,
            test_q_hi=q_hi,
            test_targets=targets,
            test_strata=strata,
        )

    @property
    def fit_info(self) -> CQRFitInfo:
        self._check_fitted()
        return self._fit_info  # type: ignore[return-value]

    @property
    def cqr(self) -> MondrianCQR:
        """Expose the calibrated MondrianCQR layer for diagnostics."""
        self._check_fitted()
        return self._cqr  # type: ignore[return-value]


class TwoStageXGBQuantileSurrogate:
    """Classifier + quantile-regressor for a right-censored time target.

    Stage 1 (``self._classifier``): XGBoost classifier on the binary
    ``event_*`` flag (matches :class:`cgem_ext.surrogate.xgb.TwoStageXGBSurrogate`
    so that the event-probability output of the two architectures is
    directly comparable).

    Stage 2: an :class:`XGBQuantileSurrogate` on the rows where
    ``event_* == 1``. The conformal calibration is applied to the
    event-positive subset of the calibration slice; rows where the event
    did not occur during the maneuver are excluded from time-interval
    calibration but still contribute to the classifier-stage probability
    diagnostics.

    Parameters
    ----------
    target : str
        Censored time target name from :mod:`cgem_ext.surrogate.targets`.
    alpha : float, default 0.05
        Miscoverage level for the time interval (passed to
        :class:`XGBQuantileSurrogate`).
    **xgb_kwargs
        ``classifier_kwargs`` and ``regressor_kwargs`` keys override the
        respective default hyperparameter dictionaries.
    """

    def __init__(
        self, target: str, *, alpha: float = DEFAULT_ALPHA, **xgb_kwargs
    ) -> None:
        spec = get_target(target)
        if not spec.censored:
            raise ValueError(
                f"{target!r} is continuous; use XGBQuantileSurrogate instead."
            )
        if not 0 < alpha < 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        self.spec: TargetSpec = spec
        self.alpha = float(alpha)

        cls_params = _default_classifier_params()
        cls_params.update(xgb_kwargs.get("classifier_kwargs", {}))
        self._classifier = XGBClassifier(**cls_params)

        # Stage-2 regressor operates on the event=1 subset of train and
        # calibration slices, treating the time as a continuous target.
        # Build a proxy continuous TargetSpec sharing the censored
        # target's monotonicity vector, then construct the regressor via
        # XGBQuantileSurrogate's unchecked factory.
        proxy_spec = TargetSpec(
            name=spec.name,
            censored=False,
            event_column=None,
            description=(
                f"Proxy continuous spec for {spec.name} "
                f"(event-positive subset only)"
            ),
            units=spec.units,
            monotonicity=spec.monotonicity,
        )
        regressor_kwargs = xgb_kwargs.get("regressor_kwargs", {})
        self._regressor = XGBQuantileSurrogate._from_spec_unchecked(
            spec=proxy_spec, alpha=alpha, **regressor_kwargs
        )
        self._fit_info: CQRFitInfo | None = None

    def fit(
        self,
        train_df: pd.DataFrame,
        *,
        calibration_df: pd.DataFrame,
        stratum_column: str = "maneuver_category",
    ) -> TwoStageXGBQuantileSurrogate:
        if self.spec.event_column is None:  # pragma: no cover (defensive)
            raise ValueError(f"{self.spec.name!r} has no event_column declared")

        # Stage 1 — classifier on all rows.
        train_feats = extract_features(train_df)
        x_train = train_feats.to_numpy(dtype=float)
        events_train = train_df[self.spec.event_column].astype(int).to_numpy()
        self._classifier.fit(x_train, events_train)

        # Stage 2 — quantile regressor on event=1 rows only.
        train_event = train_df[train_df[self.spec.event_column] == 1].copy()
        cal_event = calibration_df[
            calibration_df[self.spec.event_column] == 1
        ].copy()
        if len(train_event) < 10:
            raise ValueError(
                f"{self.spec.name!r}: only {len(train_event)} event-positive "
                f"rows available for the conditional regressor; need >= 10."
            )
        if len(cal_event) < 10:
            raise ValueError(
                f"{self.spec.name!r}: only {len(cal_event)} event-positive "
                f"calibration rows; CQR layer cannot be calibrated reliably."
            )
        self._regressor.fit(
            train_event,
            calibration_df=cal_event,
            stratum_column=stratum_column,
        )

        self._fit_info = CQRFitInfo(
            target=self.spec.name,
            censored=True,
            alpha=self.alpha,
            n_train=len(train_df),
            n_train_event=len(train_event),
            n_calibration=len(cal_event),
            feature_columns=tuple(train_feats.columns.tolist()),
        )
        return self

    def _check_fitted(self) -> None:
        if self._fit_info is None:
            raise RuntimeError("TwoStageXGBQuantileSurrogate is not fitted")

    def predict_event_probability(self, df: pd.DataFrame) -> np.ndarray:
        """Return P(event=1) per row."""
        self._check_fitted()
        feats = extract_features(df)
        return self.predict_event_probability_array(
            feats.to_numpy(dtype=float)
        )

    def predict_event_probability_array(self, x: np.ndarray) -> np.ndarray:
        """P(event=1) from a FEATURE_COLUMNS-aligned matrix."""
        self._check_fitted()
        proba = self._classifier.predict_proba(np.asarray(x, dtype=float))
        return np.asarray(proba[:, 1], dtype=float)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Median time E[time | event=1] per row."""
        self._check_fitted()
        return self._regressor.predict(df)

    def predict_interval(
        self,
        df: pd.DataFrame,
        *,
        stratum_column: str = "maneuver_category",
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calibrated CQR bracket on the conditional time per row.

        Note that the bracket is conditional on the event having
        occurred — for rows with very low ``predict_event_probability``,
        the time interval has no operational meaning and downstream
        consumers should consult the event probability before using the
        time bracket.
        """
        self._check_fitted()
        return self._regressor.predict_interval(
            df, stratum_column=stratum_column
        )

    def predict_expected_time(self, df: pd.DataFrame) -> np.ndarray:
        """E[time] = P(event) * E[time | event=1] per row."""
        return self.predict_event_probability(df) * self.predict(df)

    def coverage(
        self,
        df: pd.DataFrame,
        *,
        stratum_column: str = "maneuver_category",
    ) -> dict[str, float]:
        """Empirical per-stratum coverage on event-positive rows of ``df``.

        Coverage is computed only on rows where the event actually
        occurred; rows with ``event_* == 0`` are excluded because the
        time target is censored on those rows and an interval has no
        defined target value to cover.
        """
        self._check_fitted()
        if self.spec.event_column is None:  # pragma: no cover (defensive)
            raise ValueError(f"{self.spec.name!r} has no event_column declared")
        df_event = df[df[self.spec.event_column] == 1].copy()
        return self._regressor.coverage(
            df_event, stratum_column=stratum_column
        )

    @property
    def fit_info(self) -> CQRFitInfo:
        self._check_fitted()
        return self._fit_info  # type: ignore[return-value]


def build_quantile_surrogate(
    target: str, *, alpha: float = DEFAULT_ALPHA, **kwargs
) -> XGBQuantileSurrogate | TwoStageXGBQuantileSurrogate:
    """Return the appropriate quantile-surrogate type for the target.

    Parallel to :func:`cgem_ext.surrogate.xgb.build_surrogate`.
    """
    spec = get_target(target)
    if spec.censored:
        return TwoStageXGBQuantileSurrogate(target, alpha=alpha, **kwargs)
    return XGBQuantileSurrogate(target, alpha=alpha, **kwargs)


__all__ = [
    "CQRFitInfo",
    "TwoStageXGBQuantileSurrogate",
    "XGBQuantileSurrogate",
    "build_quantile_surrogate",
]
