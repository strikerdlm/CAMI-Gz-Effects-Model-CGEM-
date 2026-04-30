"""Fast ML surrogate of CGEM with calibrated uncertainty (Phase 3).

Per-target XGBoost emulators (with monotonicity constraints from
:mod:`cgem_ext.surrogate.targets`) and RandomForest baselines, both
exposed behind matched ``fit / predict`` APIs so the LOGO comparison
in tests + paper-1 is apples-to-apples.

Censored time targets (greyout / blackout / G-LOC) use a two-stage
classifier-then-regressor pattern; continuous targets (HLAP_min,
c_bank_min) use a single regressor.

The Mondrian split-conformal layer in :mod:`cgem_ext.surrogate.conformal`
turns point predictions into per-maneuver-category prediction
intervals at a target nominal coverage (default 95%).

See ``docs/architecture/ML_LAYER.md`` and ``docs/publication/Q1_PAPER_PLAN.md``
for the design rationale; ``docs/models/emulator_card.md`` for the
trained-model card; ``tests/test_surrogate.py`` for the contract.
"""

from cgem_ext.surrogate.baseline import (
    RFSurrogate,
    TwoStageRFSurrogate,
    build_baseline,
)
from cgem_ext.surrogate.conformal import MondrianSplitConformal
from cgem_ext.surrogate.features import FEATURE_COLUMNS, extract_features
from cgem_ext.surrogate.targets import (
    TARGETS,
    TargetSpec,
    censored_targets,
    continuous_targets,
    get_target,
)
from cgem_ext.surrogate.xgb import (
    TwoStageXGBSurrogate,
    XGBSurrogate,
    build_surrogate,
)

__all__ = [
    "FEATURE_COLUMNS",
    "TARGETS",
    "MondrianSplitConformal",
    "RFSurrogate",
    "TargetSpec",
    "TwoStageRFSurrogate",
    "TwoStageXGBSurrogate",
    "XGBSurrogate",
    "build_baseline",
    "build_surrogate",
    "censored_targets",
    "continuous_targets",
    "extract_features",
    "get_target",
]
