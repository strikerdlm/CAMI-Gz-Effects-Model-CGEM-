"""Out-of-distribution detection for CGEM inputs.

Pre-registered detector (paper 1):
    :class:`MahalanobisOOD`        — robust covariance + chi^2(0.95)
    :class:`ConformalAbstention`   — split-conformal threshold tuning

Baseline (for fair AUROC comparison):
    :class:`IsolationForestOOD`    — sklearn IsolationForest

The fixed feature space lives in :mod:`cgem_ext.ood.features`; both
detectors consume it identically so the leave-one-group-out evaluation
in :mod:`tests.test_ood` is apples-to-apples.

Public one-shot helper:
    :func:`is_in_envelope`         — fit on train_df, query query_df

See ``docs/publication/osf_preregistration.md`` and
``docs/models/ood_card.md`` for the detector specification.
"""

from cgem_ext.ood.baseline import IsolationForestOOD
from cgem_ext.ood.conformal import ConformalAbstention
from cgem_ext.ood.features import FEATURE_COLUMNS, extract_features
from cgem_ext.ood.mahalanobis import MahalanobisOOD, is_in_envelope

__all__ = [
    "FEATURE_COLUMNS",
    "ConformalAbstention",
    "IsolationForestOOD",
    "MahalanobisOOD",
    "extract_features",
    "is_in_envelope",
]
