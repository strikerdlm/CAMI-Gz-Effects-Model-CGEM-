"""Sobol sensitivity analysis driven by the trained surrogate.

We compute first-order (S1), total-order (ST) and second-order (S2)
Sobol indices over the 9 continuous features defined in
:mod:`cgem_ext.sensitivity.space`. The categorical / one-hot dimensions
are held fixed at canonical defaults so the indices have a physical
interpretation: "given a typical pilot, which input drives the output
the most?".

The surrogate makes the analysis tractable. SALib's Saltelli sampling
generates ``N * (2d + 2)`` evaluations for ``d`` features and a base
sample size ``N``. With ``d = 9`` and ``N = 1024`` that's 20,480
points — milliseconds for the surrogate, hours/days for the Fortran
binary. The cost saving is the load-bearing motivation for shipping
a fast emulator at all.

API:

    from cgem_ext.surrogate import build_surrogate
    from cgem_ext.sensitivity import SobolAnalyzer

    surrogate = build_surrogate("hlap_min").fit(train_df)
    res = SobolAnalyzer(surrogate, n_base=1024, seed=42).run()
    print(res.dataframe())   # one row per feature; S1, ST, S1_conf, ST_conf
    print(res.second_order_dataframe())  # one row per feature pair
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

import numpy as np
import pandas as pd
from SALib.analyze.sobol import analyze as _sobol_analyze
from SALib.sample.sobol import sample as _sobol_sample

from cgem_ext.ood.features import FEATURE_COLUMNS
from cgem_ext.sensitivity.space import (
    SENSITIVITY_FEATURES,
    SOBOL_PROBLEM,
    fixed_feature_template,
)


DEFAULT_N_BASE = 1024
DEFAULT_NUM_RESAMPLES = 100  # bootstrap replicates for SALib confidence intervals


class _Surrogate(Protocol):
    """Structural type for any object exposing a NumPy-array predict path.

    Both ``XGBSurrogate`` and ``TwoStageXGBSurrogate.predict`` (conditional
    time) satisfy this; the analyzer only needs ``predict_array``.
    """

    def predict_array(self, X: np.ndarray) -> np.ndarray: ...


# ── Result containers ───────────────────────────────────────────────


@dataclass(frozen=True)
class SobolFitInfo:
    target: str
    n_base: int
    n_evaluations: int
    seed: int
    fixed_who_profile: int | str | None
    fixed_cm_ordinal: float
    calc_second_order: bool


@dataclass(frozen=True)
class SobolResults:
    info: SobolFitInfo
    s1: np.ndarray
    s1_conf: np.ndarray
    st: np.ndarray
    st_conf: np.ndarray
    s2: Optional[np.ndarray]  # (d, d), nan on the diagonal
    s2_conf: Optional[np.ndarray]
    feature_names: tuple[str, ...]

    def dataframe(self) -> pd.DataFrame:
        """One row per feature with first- and total-order indices."""
        return pd.DataFrame(
            {
                "feature": self.feature_names,
                "S1": self.s1,
                "S1_conf": self.s1_conf,
                "ST": self.st,
                "ST_conf": self.st_conf,
            }
        )

    def second_order_dataframe(self) -> pd.DataFrame:
        """One row per (feature_i, feature_j), i < j."""
        if self.s2 is None:
            return pd.DataFrame(columns=["feature_i", "feature_j", "S2", "S2_conf"])
        rows = []
        d = len(self.feature_names)
        for i in range(d):
            for j in range(i + 1, d):
                rows.append(
                    {
                        "feature_i": self.feature_names[i],
                        "feature_j": self.feature_names[j],
                        "S2": float(self.s2[i, j]),
                        "S2_conf": float(self.s2_conf[i, j]) if self.s2_conf is not None else float("nan"),
                    }
                )
        return pd.DataFrame(rows)


# ── Wrapper that turns a Sobol-friendly array into FEATURE_COLUMNS rows ──


def _build_inference_matrix(
    sobol_samples: np.ndarray, *, who_profile: int | str | None, cm_ordinal: float
) -> np.ndarray:
    """Stamp the 9-d sample into the 17-d FEATURE_COLUMNS layout.

    Returns a 2-D float ndarray of shape (n_samples, len(FEATURE_COLUMNS))
    ready to feed any surrogate via its ``predict`` path.
    """
    template = fixed_feature_template(who_profile=who_profile, cm_ordinal=cm_ordinal)
    out = np.broadcast_to(template, (sobol_samples.shape[0], len(template))).copy()
    for i, name in enumerate(SENSITIVITY_FEATURES):
        col = FEATURE_COLUMNS.index(name)
        out[:, col] = sobol_samples[:, i]
    return out


def _surrogate_predict_array(
    surrogate, x: np.ndarray, *, censored_path: str = "expected"
) -> np.ndarray:
    """Run a surrogate against a FEATURE_COLUMNS-aligned matrix.

    Handles both single-stage (``XGBSurrogate``) and two-stage
    (``TwoStageXGBSurrogate``) models via their ``*_array`` methods,
    which skip ``extract_features`` because the matrix is already encoded.

    For two-stage censored targets the caller picks the path:

    - ``"expected"`` — ``P(event) * E[time | event=1]`` (default; reflects
      what a downstream consumer sees as "predicted time")
    - ``"conditional"`` — ``E[time | event=1]`` (regressor stage only)
    - ``"event"`` — ``P(event=1)`` (classifier stage only)
    """
    if hasattr(surrogate, "predict_event_probability_array"):
        if censored_path == "expected":
            return surrogate.predict_expected_time_array(x)
        if censored_path == "conditional":
            return surrogate.predict_array(x)
        if censored_path == "event":
            return surrogate.predict_event_probability_array(x)
        raise ValueError(f"unknown censored_path={censored_path!r}")
    return surrogate.predict_array(x)


# ── Analyzer ────────────────────────────────────────────────────────


class SobolAnalyzer:
    """SALib Sobol analyzer driven by a trained surrogate.

    Parameters
    ----------
    surrogate : XGBSurrogate or TwoStageXGBSurrogate (or any duck-type)
        Fitted surrogate from :mod:`cgem_ext.surrogate`.
    target : str
        Name of the target the surrogate was trained on (recorded in
        the result for traceability).
    n_base : int
        Saltelli base sample size; total evaluations = ``N * (2d + 2)``
        for ``calc_second_order=True``. Default 1024 (20,480 evals at
        d=9).
    seed : int
        RNG seed for the Saltelli sampler.
    calc_second_order : bool
        Whether to estimate S2 indices. Default True.
    censored_path : str
        For two-stage censored surrogates, which prediction path to
        feed Sobol on. Default ``"expected"`` (E[time]).
    who_profile : int
    cm_ordinal : float
        Held-fixed values for the categorical / one-hot dimensions.
    """

    def __init__(
        self,
        surrogate,
        *,
        target: Optional[str] = None,
        n_base: int = DEFAULT_N_BASE,
        seed: int = 42,
        calc_second_order: bool = True,
        censored_path: str = "expected",
        who_profile: int | str | None = "custom",
        cm_ordinal: float = 0.0,
    ) -> None:
        self.surrogate = surrogate
        self.target = target or getattr(getattr(surrogate, "spec", None), "name", "<unknown>")
        self.n_base = int(n_base)
        self.seed = int(seed)
        self.calc_second_order = bool(calc_second_order)
        self.censored_path = str(censored_path)
        self.who_profile = who_profile  # int 1..6, "custom", or None
        self.cm_ordinal = float(cm_ordinal)

    def run(self) -> SobolResults:
        problem = SOBOL_PROBLEM
        samples = _sobol_sample(
            problem,
            self.n_base,
            calc_second_order=self.calc_second_order,
            seed=self.seed,
        )
        x = _build_inference_matrix(
            samples, who_profile=self.who_profile, cm_ordinal=self.cm_ordinal
        )
        y = _surrogate_predict_array(self.surrogate, x, censored_path=self.censored_path)
        analysis = _sobol_analyze(
            problem,
            y,
            calc_second_order=self.calc_second_order,
            num_resamples=DEFAULT_NUM_RESAMPLES,
            seed=self.seed,
        )
        info = SobolFitInfo(
            target=self.target,
            n_base=self.n_base,
            n_evaluations=int(samples.shape[0]),
            seed=self.seed,
            fixed_who_profile=self.who_profile,
            fixed_cm_ordinal=self.cm_ordinal,
            calc_second_order=self.calc_second_order,
        )
        return SobolResults(
            info=info,
            s1=np.asarray(analysis["S1"], dtype=float),
            s1_conf=np.asarray(analysis["S1_conf"], dtype=float),
            st=np.asarray(analysis["ST"], dtype=float),
            st_conf=np.asarray(analysis["ST_conf"], dtype=float),
            s2=np.asarray(analysis["S2"], dtype=float) if self.calc_second_order else None,
            s2_conf=np.asarray(analysis["S2_conf"], dtype=float) if self.calc_second_order else None,
            feature_names=tuple(SENSITIVITY_FEATURES),
        )


__all__ = [
    "DEFAULT_N_BASE",
    "DEFAULT_NUM_RESAMPLES",
    "SobolAnalyzer",
    "SobolFitInfo",
    "SobolResults",
]
