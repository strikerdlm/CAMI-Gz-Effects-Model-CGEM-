"""Unit + integration tests for the cgem_ext.sensitivity subpackage.

Static API checks (no CGEM binary needed):
- SOBOL_PROBLEM dict shape and bounds well-formed
- fixed_feature_template returns the right shape and stamps the WHO
  one-hot correctly for int / "custom" / None
- SobolAnalyzer / MorrisAnalyzer construction and parameter handling

End-to-end checks (gated by needs_cgem_binary):
- SobolAnalyzer.run() against a trained surrogate on cgem_synthetic_v1
  produces well-formed indices (S1 in [0, ~1], ST >= S1, non-negative
  CIs, physically expected top driver per target)
- MorrisAnalyzer.run() produces well-formed mu_star / sigma rankings
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest


# ──────────────────────────────────────────────────────────────────────
# Static space + template checks
# ──────────────────────────────────────────────────────────────────────


def test_sobol_problem_shape():
    from cgem_ext.sensitivity import SOBOL_PROBLEM, SENSITIVITY_FEATURES

    assert SOBOL_PROBLEM["num_vars"] == len(SENSITIVITY_FEATURES) == 9
    assert list(SOBOL_PROBLEM["names"]) == list(SENSITIVITY_FEATURES)
    assert len(SOBOL_PROBLEM["bounds"]) == 9
    for low, high in SOBOL_PROBLEM["bounds"]:
        assert low < high


def test_fixed_feature_template_shape_and_one_hot():
    from cgem_ext.ood.features import FEATURE_COLUMNS
    from cgem_ext.sensitivity import fixed_feature_template

    template = fixed_feature_template(who_profile=2)
    assert template.shape == (len(FEATURE_COLUMNS),)
    # Exactly one WHO indicator is set
    who_cols = [i for i, n in enumerate(FEATURE_COLUMNS) if n.startswith("who_")]
    assert template[who_cols].sum() == pytest.approx(1.0)
    # who_2 is the one set
    assert template[FEATURE_COLUMNS.index("who_2")] == pytest.approx(1.0)


def test_fixed_feature_template_custom():
    from cgem_ext.ood.features import FEATURE_COLUMNS
    from cgem_ext.sensitivity import fixed_feature_template

    for arg in ("custom", None):
        template = fixed_feature_template(who_profile=arg)
        assert template[FEATURE_COLUMNS.index("who_custom")] == pytest.approx(1.0)


def test_fixed_feature_template_invalid_raises():
    from cgem_ext.sensitivity import fixed_feature_template

    with pytest.raises(ValueError):
        fixed_feature_template(who_profile=7)
    with pytest.raises(ValueError):
        fixed_feature_template(who_profile="nope")


def test_continuous_indices_in_range():
    from cgem_ext.ood.features import FEATURE_COLUMNS
    from cgem_ext.sensitivity.space import continuous_indices

    idx = continuous_indices()
    assert len(idx) == 9
    for i in idx:
        assert 0 <= i < len(FEATURE_COLUMNS)


# ──────────────────────────────────────────────────────────────────────
# Synthetic-surrogate analyzer checks (no CGEM binary)
# ──────────────────────────────────────────────────────────────────────


class _FakeSurrogate:
    """Minimal duck-type matching the .predict_array surface."""

    def __init__(self, fn):
        self._fn = fn
        self.spec = type("S", (), {"name": "fake"})()

    def predict_array(self, x):
        return np.asarray(self._fn(x), dtype=float)


def test_sobol_analyzer_on_linear_function():
    """y = a * g_peak + b * dehydration. S1 should rank g_peak >> all others
    when a >> b, regardless of the held-fixed who_profile defaults."""
    from cgem_ext.ood.features import FEATURE_COLUMNS
    from cgem_ext.sensitivity import SobolAnalyzer

    g_idx = FEATURE_COLUMNS.index("g_peak_abs")
    dur_idx = FEATURE_COLUMNS.index("profile_duration_s")

    def linear(x):
        return 5.0 * x[:, g_idx] + 0.1 * x[:, dur_idx]

    fake = _FakeSurrogate(linear)
    res = SobolAnalyzer(fake, target="linear_demo", n_base=128, seed=0).run()
    df = res.dataframe()
    top = df.sort_values("ST", ascending=False).iloc[0]
    assert top.feature == "g_peak_abs"
    # ST >= S1 within numerical tolerance (S1 is a lower bound on ST)
    for _, r in df.iterrows():
        assert r.ST + 0.05 >= r.S1
    # S1 sums to ~1 for a purely additive model (no interactions)
    assert 0.7 <= df["S1"].sum() <= 1.1


def test_morris_analyzer_on_linear_function():
    from cgem_ext.ood.features import FEATURE_COLUMNS
    from cgem_ext.sensitivity import MorrisAnalyzer

    g_idx = FEATURE_COLUMNS.index("g_peak_abs")

    def linear(x):
        return 5.0 * x[:, g_idx]

    fake = _FakeSurrogate(linear)
    res = MorrisAnalyzer(fake, target="linear_demo", n_trajectories=50, seed=0).run()
    df = res.dataframe()
    top = df.sort_values("mu_star", ascending=False).iloc[0]
    assert top.feature == "g_peak_abs"
    # All mu_star are non-negative
    assert (df["mu_star"] >= 0).all()
    # All conf values are non-negative
    assert (df["mu_star_conf"] >= 0).all()


def test_sobol_results_dataframe_shape():
    from cgem_ext.sensitivity import SENSITIVITY_FEATURES, SobolAnalyzer

    fake = _FakeSurrogate(lambda x: x.sum(axis=1))
    res = SobolAnalyzer(fake, target="t", n_base=64, seed=0).run()
    df = res.dataframe()
    assert len(df) == len(SENSITIVITY_FEATURES)
    assert {"feature", "S1", "S1_conf", "ST", "ST_conf"} <= set(df.columns)
    s2 = res.second_order_dataframe()
    # n choose 2 with n=9 -> 36 rows
    assert len(s2) == 36


def test_sobol_results_no_second_order():
    from cgem_ext.sensitivity import SobolAnalyzer

    fake = _FakeSurrogate(lambda x: x.sum(axis=1))
    res = SobolAnalyzer(
        fake, target="t", n_base=64, seed=0, calc_second_order=False
    ).run()
    s2 = res.second_order_dataframe()
    assert len(s2) == 0


# ──────────────────────────────────────────────────────────────────────
# End-to-end on canonical paper-1 dataset
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def synthetic_v1_df(repo_root):
    path = repo_root / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    if not path.is_file():
        pytest.skip("cgem_synthetic_v1.parquet not present")
    return pd.read_parquet(path)


@pytest.mark.needs_cgem_binary
def test_sobol_on_real_surrogate_hlap_min(synthetic_v1_df):
    """Headline sensitivity result on hlap_min: dehydration_level is the
    dominant driver in the custom arm. Expected top-S1 > 0.5; ST close
    to S1 (no strong interactions).
    """
    warnings.filterwarnings("ignore")
    from cgem_ext.data.splits import stratified_split
    from cgem_ext.sensitivity import SobolAnalyzer
    from cgem_ext.surrogate import build_surrogate

    sp = stratified_split(synthetic_v1_df, seed=42)
    train_df, _val, _test = sp.apply(synthetic_v1_df)

    surrogate = build_surrogate("hlap_min").fit(train_df)
    res = SobolAnalyzer(surrogate, target="hlap_min", n_base=256, seed=42).run()
    df = res.dataframe().sort_values("ST", ascending=False)
    top = df.iloc[0]
    assert top.feature == "dehydration_level"
    assert top.S1 > 0.5


@pytest.mark.needs_cgem_binary
def test_sobol_on_real_surrogate_c_bank(synthetic_v1_df):
    """c_bank_min should be dominated by g_peak_abs and profile_duration_s
    in the custom arm. Both should rank in the top 3 by ST.
    """
    warnings.filterwarnings("ignore")
    from cgem_ext.data.splits import stratified_split
    from cgem_ext.sensitivity import SobolAnalyzer
    from cgem_ext.surrogate import build_surrogate

    sp = stratified_split(synthetic_v1_df, seed=42)
    train_df, _val, _test = sp.apply(synthetic_v1_df)

    surrogate = build_surrogate("c_bank_min").fit(train_df)
    res = SobolAnalyzer(surrogate, target="c_bank_min", n_base=256, seed=42).run()
    top3 = res.dataframe().sort_values("ST", ascending=False).head(3)
    assert "g_peak_abs" in top3["feature"].values
    assert "profile_duration_s" in top3["feature"].values
