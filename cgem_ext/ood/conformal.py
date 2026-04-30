"""Split-conformal abstention threshold for OOD scores.

The Mahalanobis χ²(df, 0.95) cutoff is principled but assumes the
training feature distribution is exactly multivariate Gaussian; that's
rarely true in practice, especially with one-hot columns. Split-conformal
calibration sidesteps the assumption by tuning the threshold directly to
hit a target abstention rate on a held-out *calibration* slice.

Workflow:

    detector = MahalanobisOOD().fit(train_df)
    cal_scores = detector.score(val_df)
    abstainer = ConformalAbstention(alpha=0.05).calibrate(cal_scores)
    test_scores = detector.score(test_df)
    is_in = abstainer.is_in_envelope(test_scores)

The ``calibrate`` step picks the empirical ``1 - alpha`` quantile of the
calibration scores. Any future score above that threshold is flagged
as out-of-distribution. By construction, the abstention rate on
exchangeable in-distribution data converges to ``alpha`` (here 0.05).

References (cited in the paper):
- Vovk, Gammerman & Shafer (2005). *Algorithmic Learning in a Random World*.
- Shafer & Vovk (2008). *A Tutorial on Conformal Prediction*. JMLR.
- Romano, Patterson & Candès (2019). *Conformalized Quantile Regression*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


DEFAULT_ALPHA = 0.05


@dataclass(frozen=True)
class CalibrationInfo:
    """Snapshot of the calibration step, for the model card and logs."""

    n_calibration: int
    alpha: float
    threshold: float
    empirical_inenv_rate: float


class ConformalAbstention:
    """Distribution-free abstention threshold from a calibration slice.

    Parameters
    ----------
    alpha : float
        Target abstention rate on exchangeable in-distribution data.
        Default 0.05 (5%) per OSF pre-registration.
    """

    def __init__(self, *, alpha: float = DEFAULT_ALPHA) -> None:
        if not 0 < alpha < 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        self.alpha = float(alpha)
        self._threshold: Optional[float] = None
        self._info: Optional[CalibrationInfo] = None

    def calibrate(self, calibration_scores: np.ndarray) -> "ConformalAbstention":
        """Pick the (1 - alpha) empirical quantile as the threshold.

        ``calibration_scores`` should be the OOD scores produced by the
        upstream detector on the calibration slice (typically the val
        split). Higher score = more OOD.
        """
        scores = np.asarray(calibration_scores, dtype=float)
        scores = scores[~np.isnan(scores)]
        if scores.size < 20:
            raise ValueError(
                f"Need at least 20 calibration scores for split-conformal "
                f"(got {scores.size}); the asymptotic guarantee is meaningless"
                f" with fewer."
            )
        # Conformal quantile: ceil((n+1)(1-alpha)) / n at the right tail.
        n = scores.size
        q_level = min(1.0, np.ceil((n + 1) * (1 - self.alpha)) / n)
        threshold = float(np.quantile(scores, q_level, method="higher"))
        in_env_rate = float((scores <= threshold).sum()) / float(n)
        self._threshold = threshold
        self._info = CalibrationInfo(
            n_calibration=int(n),
            alpha=self.alpha,
            threshold=threshold,
            empirical_inenv_rate=in_env_rate,
        )
        return self

    def _check_calibrated(self) -> None:
        if self._threshold is None:
            raise RuntimeError("ConformalAbstention is not calibrated yet")

    def is_in_envelope(self, scores: np.ndarray) -> np.ndarray:
        """Boolean per score: ``True`` iff score ≤ calibrated threshold."""
        self._check_calibrated()
        scores = np.asarray(scores, dtype=float)
        return scores <= self._threshold  # type: ignore[operator]

    @property
    def threshold(self) -> float:
        self._check_calibrated()
        return self._threshold  # type: ignore[return-value]

    @property
    def info(self) -> CalibrationInfo:
        self._check_calibrated()
        return self._info  # type: ignore[return-value]


__all__ = [
    "CalibrationInfo",
    "ConformalAbstention",
    "DEFAULT_ALPHA",
]
