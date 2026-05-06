"""Whinnery & Forster 2013 piecewise G-LOC time curve as a low-fidelity
analytical model.

Whinnery JE, Forster EM. (2013). *The +Gz-induced loss of consciousness
curve.* Extreme Physiology and Medicine 2(1):19.
DOI 10.1186/2046-7648-2-19 (open access, CC-BY).

The WF2013 paper analyses 888 centrifuge G-LOC episodes and reports
three regime-specific summary findings (verbatim from the abstract):

* **Rapid-onset regime** (onset rate ≥ 1.0 G/s): G-LOC occurs in a
  mean time of **9.10 s** and is **independent of the onset rate**.
* **Gradual-onset regime** (onset rate ≤ 0.2 G/s): G-LOC occurs in
  a mean time of **74.41 s**.
* **Transitional regime** (0.2 < onset rate < 1.0 G/s): not stated
  as a single value; we interpolate log-linearly between the two
  anchor points (onset 0.2 G/s → 74.41 s and onset 1.0 G/s →
  9.10 s) so the curve is continuous.

Two additional thresholds:

* G-LOC does not occur for sustained +Gz below **+4.7 Gz**
  (returns ``np.inf``).
* The minimum observed LOCINDTI across all WF2013 exposures is
  **5 s**; the model is clipped to ``≥ 5 s`` accordingly.

The model is exposed with the same uniform API as
:class:`cgem_ext.surrogate.lowfi.stoll.StollGTolerance` so a
multi-fidelity coupling layer can swap them. Its validity envelope
covers a wider onset-rate range than Stoll (``0.05 – 10 G/s``) but
the same +Gz threshold (``≥ 4.7 Gz`` for non-infinite predictions).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd

# ── Anchor constants (verbatim from WF2013 abstract) ──────────────────

G_THRESHOLD: Final[float] = 4.7
LOCINDTI_MIN: Final[float] = 5.0

# Onset-rate piecewise anchors:
GRADUAL_ONSET_MAX: Final[float] = 0.2  # G/s; ≤ this → 74.41 s
RAPID_ONSET_MIN: Final[float] = 1.0  # G/s; ≥ this → 9.10 s
GRADUAL_T_LOC: Final[float] = 74.41  # s
RAPID_T_LOC: Final[float] = 9.10  # s

# Validity envelope (matches WF2013 cohort coverage):
ONSET_RATE_MIN: Final[float] = 0.05
ONSET_RATE_MAX: Final[float] = 10.0
G_PEAK_MAX: Final[float] = 12.0


@dataclass(frozen=True)
class ValidityEnvelope:
    g_peak_min: float
    g_peak_max: float
    onset_rate_min: float
    onset_rate_max: float


_ENVELOPE = ValidityEnvelope(
    g_peak_min=G_THRESHOLD,
    g_peak_max=G_PEAK_MAX,
    onset_rate_min=ONSET_RATE_MIN,
    onset_rate_max=ONSET_RATE_MAX,
)


def _piecewise_t_loc(onset_rate: float | np.ndarray) -> np.ndarray:
    """Piecewise time-to-LOC as a function of onset rate.

    * onset ≤ 0.2 G/s  → 74.41 s
    * 0.2 < onset < 1.0 → log-linear interpolation between
      (0.2, 74.41) and (1.0, 9.10) in (log onset, t_loc) space.
    * onset ≥ 1.0 → 9.10 s.
    """
    onset = np.asarray(onset_rate, dtype=float)
    out = np.empty_like(onset, dtype=float)
    gradual_mask = onset <= GRADUAL_ONSET_MAX
    rapid_mask = onset >= RAPID_ONSET_MIN
    transitional_mask = ~gradual_mask & ~rapid_mask
    out[gradual_mask] = GRADUAL_T_LOC
    out[rapid_mask] = RAPID_T_LOC
    if transitional_mask.any():
        # Log-linear interpolation over onset rate (the natural
        # log-scale of the gradual-to-rapid transition).
        x = np.log(onset[transitional_mask])
        x_lo = np.log(GRADUAL_ONSET_MAX)
        x_hi = np.log(RAPID_ONSET_MIN)
        frac = (x - x_lo) / (x_hi - x_lo)
        out[transitional_mask] = (
            GRADUAL_T_LOC + frac * (RAPID_T_LOC - GRADUAL_T_LOC)
        )
    return out


class WhinneryForsterGLOC:
    """Low-fidelity piecewise G-LOC time curve (WF2013 anchors).

    Parallel API to :class:`StollGTolerance`. The two free anchors
    (gradual: 74.41 s, rapid: 9.10 s) are taken verbatim from the
    WF2013 abstract; no fitting at runtime.
    """

    g_threshold: float = G_THRESHOLD
    locindti_min: float = LOCINDTI_MIN
    validity_envelope: ValidityEnvelope = _ENVELOPE

    def predict_time_to_loc_s(
        self, g_peak_abs: float, dgdt_max_g_per_s: float
    ) -> float:
        """Predict time-to-LOC for a single ``(g_peak, onset_rate)`` row.

        Returns ``np.inf`` if ``g_peak_abs < g_threshold`` (LOC does
        not occur). Returns ``np.nan`` if inputs fall outside the
        published validity envelope. Otherwise returns the piecewise
        time-to-LOC, clipped at ``locindti_min`` from below.
        """
        if g_peak_abs < self.g_threshold:
            return float("inf")
        if g_peak_abs > self.validity_envelope.g_peak_max:
            return float("nan")
        if not (
            self.validity_envelope.onset_rate_min
            <= dgdt_max_g_per_s
            <= self.validity_envelope.onset_rate_max
        ):
            return float("nan")
        t = float(_piecewise_t_loc(np.asarray([dgdt_max_g_per_s]))[0])
        return max(self.locindti_min, t)

    def predict_array(self, X: np.ndarray | pd.DataFrame) -> np.ndarray:
        """Vectorised prediction over an Nx2 matrix or DataFrame.

        ``X`` columns: ``(g_peak_abs, dgdt_max_g_per_s)``. Returns a
        length-N float array; rows below the +Gz threshold are
        ``np.inf``; rows outside the validity envelope are ``np.nan``.
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
        below_threshold = g_peak < self.g_threshold
        out_of_env = (
            ~below_threshold
            & (
                (g_peak > self.validity_envelope.g_peak_max)
                | (onset < self.validity_envelope.onset_rate_min)
                | (onset > self.validity_envelope.onset_rate_max)
            )
        )
        in_envelope = ~below_threshold & ~out_of_env

        out = np.empty(len(arr), dtype=float)
        out[below_threshold] = np.inf
        out[out_of_env] = np.nan
        if in_envelope.any():
            t = _piecewise_t_loc(onset[in_envelope])
            out[in_envelope] = np.maximum(self.locindti_min, t)
        return out


__all__ = [
    "GRADUAL_ONSET_MAX",
    "GRADUAL_T_LOC",
    "G_THRESHOLD",
    "LOCINDTI_MIN",
    "RAPID_ONSET_MIN",
    "RAPID_T_LOC",
    "ValidityEnvelope",
    "WhinneryForsterGLOC",
]
