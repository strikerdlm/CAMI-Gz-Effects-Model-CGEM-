"""Global sensitivity analysis driven by the trained surrogate (Phase 4).

Two analyzers exposed:

- :class:`SobolAnalyzer` — Saltelli sampling + Sobol decomposition
  (first-, total-, second-order indices with bootstrap CIs).
- :class:`MorrisAnalyzer` — elementary-effects screening (mu, mu_star,
  sigma per feature). Cheaper; used as a robustness check.

Both run over the 9 continuous features defined in
:mod:`cgem_ext.sensitivity.space`; the categorical / one-hot
dimensions are held fixed at canonical defaults (who_profile=2,
cm=none) so the indices have a clean physical interpretation.

The surrogate makes Phase 4 tractable. A 10⁴-sample Saltelli study
runs in ~seconds vs days against the Fortran subprocess — that
speedup is the load-bearing reason the surrogate exists.

See ``docs/architecture/ML_LAYER.md`` and ``data/results/sensitivity/``
for paper-1 figures.
"""

from cgem_ext.sensitivity.morris import MorrisAnalyzer, MorrisResults
from cgem_ext.sensitivity.sobol import SobolAnalyzer, SobolResults
from cgem_ext.sensitivity.space import (
    SENSITIVITY_BOUNDS,
    SENSITIVITY_FEATURES,
    SOBOL_PROBLEM,
    fixed_feature_template,
)

__all__ = [
    "SENSITIVITY_BOUNDS",
    "SENSITIVITY_FEATURES",
    "SOBOL_PROBLEM",
    "MorrisAnalyzer",
    "MorrisResults",
    "SobolAnalyzer",
    "SobolResults",
    "fixed_feature_template",
]
