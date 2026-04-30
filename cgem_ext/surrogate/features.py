"""Feature space for the surrogate emulator.

The surrogate consumes the same 17-dimensional feature space as the OOD
detector (:mod:`cgem_ext.ood.features`). Re-using one frozen feature
contract has two benefits:

1. The OOD detector and the surrogate see identical inputs at inference
   time, so the OOD ``ood: bool`` flag in the FastAPI ``/predict``
   response is meaningful for the very prediction it accompanies.
2. Reproducibility — one place to bump the feature version when the
   parquet schema changes.

We re-export :func:`extract_features` and ``FEATURE_COLUMNS`` here for
discoverability; the implementations live in ``cgem_ext.ood.features``.

We additionally expose the **monotonicity hints** that the XGBoost
backbone uses. These encode physiological priors the regressor must
respect (e.g. higher G-peak should not *increase* time-to-G-LOC). The
hints are aligned to ``FEATURE_COLUMNS`` order: +1 monotone-increasing,
-1 monotone-decreasing, 0 unconstrained.
"""

from __future__ import annotations

from cgem_ext.ood.features import FEATURE_COLUMNS, extract_features

# Default monotonicity vector (most features unconstrained). Per-target
# overrides live in :mod:`cgem_ext.surrogate.targets`.
ZERO_MONOTONICITY: tuple[int, ...] = tuple(0 for _ in FEATURE_COLUMNS)


def feature_index(name: str) -> int:
    """Return the column index of ``name`` in :data:`FEATURE_COLUMNS`.

    Use this when building per-target monotonicity vectors so the index
    is sourced from the contract rather than hard-coded.
    """
    if name not in FEATURE_COLUMNS:
        raise KeyError(
            f"{name!r} is not in FEATURE_COLUMNS; available: {FEATURE_COLUMNS}"
        )
    return FEATURE_COLUMNS.index(name)


__all__ = [
    "FEATURE_COLUMNS",
    "ZERO_MONOTONICITY",
    "extract_features",
    "feature_index",
]
