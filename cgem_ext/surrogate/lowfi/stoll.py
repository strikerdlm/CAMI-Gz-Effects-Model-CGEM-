"""Stoll 1956 sustained-G tolerance curve as a low-fidelity analytical
model of human +Gz tolerance.

Stoll, A. M. (1956). *Human tolerance to positive G as determined by
the physiological end points.* J Aviat Med 27(4):356–367.

The original Stoll curve plotted *sustained +Gz* against *time at that
+Gz* before the onset of grayout / blackout. It is monotonically
decreasing: higher sustained +Gz produces shorter tolerance time.
Stoll's data were taken at fixed plateaus following rapid onset to
the plateau; the curve does NOT model gradual onset directly. For
the purposes of low-fidelity G-LOC time prediction in this package
we treat the Stoll curve as the time-to-LOC for a *rapid-onset*
exposure to a sustained +Gz plateau.

The closed form fitted here follows the parametric form widely used
in the aerospace-medicine literature (e.g. Burton 1988, summarised
in Whinnery & Forster 2013 [13]):

    t_loc(G) = a / (G - G_threshold) ** b           for G > G_threshold
    t_loc(G) = inf                                   for G ≤ G_threshold

with ``G_threshold = 4.7`` (the minimum +Gz level below which G-LOC
does not occur, anchored on the WF2013 abstract finding) and the
exponent / scale parameters fitted to reproduce the WF2013 +Gz-level
curve anchors:

* G = +7 Gz, t = 9.65 s.
* G = +9.4 Gz (experimental ceiling), t = 5–9 s (the WF2013 minimum
  observed LOCINDTI).

Two parameters (``a``, ``b``) are fitted analytically by passing
through the (7, 9.65) and (9.4, 5.0) anchors; this gives a positive
``b`` and a positive ``a``. The fit is fixed at module import time
so the model is fully deterministic.

The Stoll curve has a *narrow* validity envelope:

* Domain: ``g_peak_abs ∈ [4.7, 12]`` Gz, ``dgdt_max_g_per_s ≥ 1.0`` G/s
  (rapid onset).
* Outside that domain :meth:`StollGTolerance.predict_time_to_loc_s`
  returns ``np.nan``.

Reference for the threshold and the WF2013 anchors:
Whinnery JE, Forster EM (2013). *The +Gz-induced loss of consciousness
curve.* Extreme Physiology and Medicine 2(1):19.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd

# ── Anchor constants (locked at module import) ────────────────────────

G_THRESHOLD: Final[float] = 4.7
ANCHOR_G_LOW: Final[float] = 7.0
ANCHOR_T_LOW: Final[float] = 9.65
ANCHOR_G_HIGH: Final[float] = 9.4
ANCHOR_T_HIGH: Final[float] = 5.0


def _fit_a_b(
    g_lo: float, t_lo: float, g_hi: float, t_hi: float, g_thr: float
) -> tuple[float, float]:
    """Fit ``a, b`` so that ``t = a / (G - g_thr) ** b`` passes through
    the two anchor points.

    Solving for ``b`` from the ratio of the two equations::

        t_lo / t_hi = ((g_hi - g_thr) / (g_lo - g_thr)) ** b
        b = log(t_lo / t_hi) / log((g_hi - g_thr) / (g_lo - g_thr))

    and then ``a = t_lo * (g_lo - g_thr) ** b``.
    """
    num = np.log(t_lo / t_hi)
    den = np.log((g_hi - g_thr) / (g_lo - g_thr))
    b = num / den
    a = t_lo * (g_lo - g_thr) ** b
    return float(a), float(b)


_FITTED_A, _FITTED_B = _fit_a_b(
    ANCHOR_G_LOW,
    ANCHOR_T_LOW,
    ANCHOR_G_HIGH,
    ANCHOR_T_HIGH,
    G_THRESHOLD,
)


@dataclass(frozen=True)
class ValidityEnvelope:
    g_peak_min: float
    g_peak_max: float
    onset_rate_min: float


_ENVELOPE = ValidityEnvelope(g_peak_min=4.7, g_peak_max=12.0, onset_rate_min=1.0)


class StollGTolerance:
    """Low-fidelity Stoll-1956-style G-tolerance curve.

    A pure-Python, NumPy-vectorised analytical function. No fitting,
    no hyperparameters, no calibration step at construction time —
    the two free parameters ``a, b`` are pre-fitted at module import
    against the WF2013 anchor points and locked in.

    The model is intentionally simple to keep the multi-fidelity
    coupling (Week 6) interpretable: a single inverse-power
    relationship in (G - G_threshold), zero pilot-configuration
    inputs, no countermeasure modelling.
    """

    a: float = _FITTED_A
    b: float = _FITTED_B
    g_threshold: float = G_THRESHOLD
    validity_envelope: ValidityEnvelope = _ENVELOPE

    def predict_time_to_loc_s(
        self, g_peak_abs: float, dgdt_max_g_per_s: float
    ) -> float:
        """Predict time-to-LOC for a single (g_peak, onset_rate) row.

        Returns ``np.nan`` if the inputs fall outside the published
        validity envelope (g < threshold, g > 12 Gz, or onset rate
        below the rapid-onset cutoff).
        """
        if not (
            self.validity_envelope.g_peak_min
            <= g_peak_abs
            <= self.validity_envelope.g_peak_max
        ):
            return float("nan")
        if dgdt_max_g_per_s < self.validity_envelope.onset_rate_min:
            return float("nan")
        return float(self.a / (g_peak_abs - self.g_threshold) ** self.b)

    def predict_array(self, X: np.ndarray | pd.DataFrame) -> np.ndarray:
        """Vectorised prediction over an Nx2 matrix or DataFrame.

        ``X`` columns: ``(g_peak_abs, dgdt_max_g_per_s)``. Returns a
        length-N float array; rows outside the validity envelope are
        ``np.nan``.
        """
        if isinstance(X, pd.DataFrame):
            arr = X[["g_peak_abs", "dgdt_max_g_per_s"]].to_numpy(dtype=float)
        else:
            arr = np.asarray(X, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != 2:
            raise ValueError(
                "X must have shape (N, 2) with columns "
                "(g_peak_abs, dgdt_max_g_per_s)"
            )
        g_peak = arr[:, 0]
        onset = arr[:, 1]
        in_envelope = (
            (g_peak >= self.validity_envelope.g_peak_min)
            & (g_peak <= self.validity_envelope.g_peak_max)
            & (onset >= self.validity_envelope.onset_rate_min)
        )
        out = np.full(len(arr), np.nan, dtype=float)
        if in_envelope.any():
            g_in = g_peak[in_envelope]
            out[in_envelope] = self.a / (g_in - self.g_threshold) ** self.b
        return out


__all__ = ["G_THRESHOLD", "StollGTolerance", "ValidityEnvelope"]
