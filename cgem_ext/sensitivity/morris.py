"""Morris elementary-effects screening driven by the surrogate.

Morris is much cheaper than Sobol — ``N * (d + 1)`` evaluations vs
``N * (2d + 2)`` — and produces two interpretable per-feature
statistics:

- ``mu_star`` (μ*) — mean absolute elementary effect; large = the
  feature has a strong overall influence.
- ``sigma`` — standard deviation of elementary effects; large =
  non-linear or interaction-heavy effect.

Used for cheap screening when you want to rank features quickly
across many surrogates or many fixed-pilot configurations. For the
paper-1 headline rankings we use the more expensive Sobol estimates
(:mod:`cgem_ext.sensitivity.sobol`) but Morris is reported in
supplementary as a robustness check.

API mirrors :class:`cgem_ext.sensitivity.SobolAnalyzer`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from SALib.analyze.morris import analyze as _morris_analyze
from SALib.sample.morris import sample as _morris_sample

from cgem_ext.sensitivity.sobol import _build_inference_matrix, _surrogate_predict_array
from cgem_ext.sensitivity.space import SENSITIVITY_FEATURES, SOBOL_PROBLEM

DEFAULT_N_TRAJECTORIES = 200  # ~ 200 * (d + 1) evals; d=9 -> 2,000 evals
DEFAULT_NUM_LEVELS = 8


@dataclass(frozen=True)
class MorrisFitInfo:
    target: str
    n_trajectories: int
    num_levels: int
    n_evaluations: int
    seed: int
    fixed_who_profile: int | str | None
    fixed_cm_ordinal: float


@dataclass(frozen=True)
class MorrisResults:
    info: MorrisFitInfo
    mu: np.ndarray  # signed mean elementary effect
    mu_star: np.ndarray  # mean absolute elementary effect
    sigma: np.ndarray  # standard deviation of elementary effects
    mu_star_conf: np.ndarray  # bootstrap CI for mu_star
    feature_names: tuple[str, ...]

    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "feature": self.feature_names,
                "mu": self.mu,
                "mu_star": self.mu_star,
                "sigma": self.sigma,
                "mu_star_conf": self.mu_star_conf,
            }
        )


class MorrisAnalyzer:
    """SALib Morris analyzer driven by a trained surrogate."""

    def __init__(
        self,
        surrogate,
        *,
        target: str | None = None,
        n_trajectories: int = DEFAULT_N_TRAJECTORIES,
        num_levels: int = DEFAULT_NUM_LEVELS,
        seed: int = 42,
        censored_path: str = "expected",
        who_profile: int | str | None = "custom",
        cm_ordinal: float = 0.0,
    ) -> None:
        self.surrogate = surrogate
        self.target: str = str(
            target or getattr(getattr(surrogate, "spec", None), "name", "<unknown>")
        )
        self.n_trajectories = int(n_trajectories)
        self.num_levels = int(num_levels)
        self.seed = int(seed)
        self.censored_path = str(censored_path)
        self.who_profile = who_profile
        self.cm_ordinal = float(cm_ordinal)

    def run(self) -> MorrisResults:
        problem = SOBOL_PROBLEM
        samples = _morris_sample(
            problem,
            N=self.n_trajectories,
            num_levels=self.num_levels,
            seed=self.seed,
        )
        x = _build_inference_matrix(
            samples, who_profile=self.who_profile, cm_ordinal=self.cm_ordinal
        )
        y = _surrogate_predict_array(self.surrogate, x, censored_path=self.censored_path)
        analysis = _morris_analyze(
            problem, samples, y, num_levels=self.num_levels, seed=self.seed
        )
        info = MorrisFitInfo(
            target=self.target,
            n_trajectories=self.n_trajectories,
            num_levels=self.num_levels,
            n_evaluations=int(samples.shape[0]),
            seed=self.seed,
            fixed_who_profile=self.who_profile,
            fixed_cm_ordinal=self.cm_ordinal,
        )
        return MorrisResults(
            info=info,
            mu=np.asarray(analysis["mu"], dtype=float),
            mu_star=np.asarray(analysis["mu_star"], dtype=float),
            sigma=np.asarray(analysis["sigma"], dtype=float),
            mu_star_conf=np.asarray(analysis["mu_star_conf"], dtype=float),
            feature_names=tuple(SENSITIVITY_FEATURES),
        )


__all__ = [
    "DEFAULT_NUM_LEVELS",
    "DEFAULT_N_TRAJECTORIES",
    "MorrisAnalyzer",
    "MorrisFitInfo",
    "MorrisResults",
]
