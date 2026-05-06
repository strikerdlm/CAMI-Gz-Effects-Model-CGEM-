"""Kennedy & O'Hagan multi-fidelity coupling between an analytical
low-fidelity G-tolerance model and the high-fidelity CGEM surrogate.

The auto-regressive Kennedy & O'Hagan (2000) scheme writes the
high-fidelity output as a scaled low-fidelity output plus a
GP-modelled discrepancy term::

    z_high(x) = ρ · z_low(x) + δ(x)

where ``ρ`` is a scaling factor (often ≈ 1 when both fidelities
predict the same physical quantity) and ``δ(x)`` is a Gaussian
process capturing systematic departures of the high-fidelity model
from the scaled low-fidelity model.

This module implements the scheme in pure NumPy / scikit-learn,
without GPy or emukit, so it adds no Cython build dependencies. The
low-fidelity source is one of the analytical models in
:mod:`cgem_ext.surrogate.lowfi` (Stoll 1956 or Whinnery & Forster
2013); the high-fidelity source is a small set of CGEM evaluations
(or, equivalently, a trained surrogate's median predictions).

API::

    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC())
    mf.fit(x_high, y_high)             # x_high: (n, 2); y_high: (n,)
    mean = mf.predict(x_query)         # length-m mean
    mean, std = mf.predict(x_query, return_std=True)

The ``predict`` method returns a Gaussian posterior at each query
point. ``predict_interval(x_query, alpha=0.05)`` returns a 95 % bracket
``[mean − 1.96·std, mean + 1.96·std]`` for callers that prefer a
bracket-shaped output matching the conformal layer.

Reference:

* Kennedy MC, O'Hagan A. (2000). *Predicting the output from a
  complex computer code when fast approximations are available.*
  Biometrika 87(1):1–13.
* Peherstorfer B, Willcox K, Gunzburger M. (2018). *Survey of
  multifidelity methods in uncertainty propagation, inference, and
  optimization.* SIAM Rev 60(3):550–591.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (
    ConstantKernel,
    Matern,
    WhiteKernel,
)


class LowFidelityModel(Protocol):
    """Structural typing for the low-fidelity source.

    Any object exposing ``predict_array(X) -> np.ndarray`` over an Nx2
    matrix of ``(g_peak_abs, dgdt_max_g_per_s)`` is a valid low-fidelity
    source. Both classes in :mod:`cgem_ext.surrogate.lowfi` qualify.
    """

    def predict_array(self, X: np.ndarray | pd.DataFrame) -> np.ndarray: ...


@dataclass(frozen=True)
class MultiFidelityFitInfo:
    n_high_fidelity_points: int
    rho: float
    discrepancy_kernel: str
    log_marginal_likelihood: float


class MultiFidelityNARGP:
    """Kennedy-O'Hagan auto-regressive multi-fidelity model.

    Parameters
    ----------
    low_fidelity : LowFidelityModel
        Analytical or pre-trained model exposing ``predict_array`` over
        ``(g_peak_abs, dgdt_max_g_per_s)``. Returned NaNs / infinities
        are handled gracefully: NaN low-fidelity predictions are
        excluded from training (they cannot be scaled by ``ρ``);
        infinite low-fidelity predictions (e.g., below the +Gz LOC
        threshold) are clipped to a large finite ceiling.
    rho : float, default 1.0
        Multiplicative scaling between low- and high-fidelity. Held
        fixed at construction time; learning ρ requires a hierarchical
        GP that this minimal implementation does not pursue.
    inf_clip_value : float, default 200.0
        Replacement value for ``np.inf`` low-fidelity outputs. Chosen
        so that the discrepancy GP can fit it as a "very long
        time-to-LOC" without numerical issues.
    random_state : int, default 42
        Seed for the GP optimiser's restarts.
    """

    def __init__(
        self,
        low_fidelity: LowFidelityModel,
        *,
        rho: float = 1.0,
        inf_clip_value: float = 200.0,
        random_state: int = 42,
    ) -> None:
        self.low_fidelity = low_fidelity
        self.rho = float(rho)
        self.inf_clip_value = float(inf_clip_value)
        self.random_state = random_state

        # Discrepancy GP: Matern-5/2 kernel with a learnable
        # length-scale per input dimension (anisotropic) plus a constant
        # scale and a small Gaussian noise term.
        kernel = (
            ConstantKernel(1.0, (1e-3, 1e3))
            * Matern(length_scale=[1.0, 1.0], length_scale_bounds=(1e-2, 1e3), nu=2.5)
            + WhiteKernel(noise_level=1e-3, noise_level_bounds=(1e-6, 1e1))
        )
        self._gp = GaussianProcessRegressor(
            kernel=kernel,
            normalize_y=True,
            n_restarts_optimizer=5,
            random_state=random_state,
        )
        self._fit_info: MultiFidelityFitInfo | None = None

    # ── Helpers ───────────────────────────────────────────────────────

    def _coerce(self, X: np.ndarray | pd.DataFrame) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            arr = X[["g_peak_abs", "dgdt_max_g_per_s"]].to_numpy(dtype=float)
        else:
            arr = np.asarray(X, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != 2:
            raise ValueError(
                "X must have shape (N, 2) with columns "
                "(g_peak_abs, dgdt_max_g_per_s)"
            )
        return arr

    def _low_fidelity_clipped(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return (z_low_clipped, valid_mask).

        ``valid_mask`` excludes rows where the low-fidelity model
        returned NaN (out of envelope). ``z_low_clipped`` replaces
        ``np.inf`` with ``self.inf_clip_value`` so the GP discrepancy
        is well-defined.
        """
        z_low = np.asarray(self.low_fidelity.predict_array(X), dtype=float)
        valid_mask = ~np.isnan(z_low)
        z_low_clipped = z_low.copy()
        z_low_clipped[np.isinf(z_low_clipped)] = self.inf_clip_value
        return z_low_clipped, valid_mask

    # ── Public API ────────────────────────────────────────────────────

    def fit(
        self,
        X: np.ndarray | pd.DataFrame,
        y: np.ndarray,
    ) -> MultiFidelityNARGP:
        """Fit the discrepancy GP on the high-fidelity training set.

        Parameters
        ----------
        X : array-like, shape (n, 2)
            Columns are ``(g_peak_abs, dgdt_max_g_per_s)``.
        y : array-like, shape (n,)
            High-fidelity target (e.g., CGEM-emitted ``time_to_gloc_s``
            or surrogate median).
        """
        arr = self._coerce(X)
        y_arr = np.asarray(y, dtype=float)
        if len(arr) != len(y_arr):
            raise ValueError("X and y must have the same length")

        z_low_clipped, valid = self._low_fidelity_clipped(arr)
        if not valid.any():
            raise ValueError(
                "All training rows are out of the low-fidelity validity "
                "envelope; cannot compute residuals."
            )
        x_train = arr[valid]
        y_train = y_arr[valid]
        z_low_train = z_low_clipped[valid]

        residuals = y_train - self.rho * z_low_train
        self._gp.fit(x_train, residuals)
        kernel_repr = str(self._gp.kernel_).replace("\n", " ")
        self._fit_info = MultiFidelityFitInfo(
            n_high_fidelity_points=int(valid.sum()),
            rho=self.rho,
            discrepancy_kernel=kernel_repr,
            log_marginal_likelihood=float(
                self._gp.log_marginal_likelihood_value_
            ),
        )
        return self

    def _check_fitted(self) -> None:
        if self._fit_info is None:
            raise RuntimeError("MultiFidelityNARGP is not fitted")

    def predict(
        self, X: np.ndarray | pd.DataFrame, *, return_std: bool = False
    ) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """Predict high-fidelity output at query points.

        Returns the posterior mean (and optionally the posterior
        standard deviation). Rows where the low-fidelity model is out
        of envelope (NaN) propagate NaN through the prediction —
        callers should filter those before using the output.
        """
        self._check_fitted()
        arr = self._coerce(X)
        z_low_clipped, valid = self._low_fidelity_clipped(arr)

        mean = np.full(len(arr), np.nan, dtype=float)
        std = np.full(len(arr), np.nan, dtype=float)
        if valid.any():
            x_in = arr[valid]
            d_mean, d_std = self._gp.predict(x_in, return_std=True)
            mean[valid] = self.rho * z_low_clipped[valid] + d_mean
            std[valid] = d_std
        if return_std:
            return mean, std
        return mean

    def predict_interval(
        self, X: np.ndarray | pd.DataFrame, *, alpha: float = 0.05
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return ``(lo, hi)`` Gaussian-quantile bracket per row.

        At ``alpha=0.05`` the half-width is 1.95996·std (z-score for
        the two-sided 95 % CI). Rows out of low-fidelity envelope
        propagate NaN.
        """
        if not 0 < alpha < 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        from scipy.stats import norm

        z = float(norm.ppf(1.0 - alpha / 2.0))
        mean, std = self.predict(X, return_std=True)
        return mean - z * std, mean + z * std

    @property
    def fit_info(self) -> MultiFidelityFitInfo:
        self._check_fitted()
        return self._fit_info  # type: ignore[return-value]


__all__ = [
    "LowFidelityModel",
    "MultiFidelityFitInfo",
    "MultiFidelityNARGP",
]
