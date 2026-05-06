"""Unit + integration tests for the CQR layer.

Two layers under test:

1. :class:`cgem_ext.surrogate.conformal.MondrianCQR` — pure-numpy
   conformity-score machinery exercised on synthetic Gaussian fixtures
   without invoking XGBoost.
2. :class:`cgem_ext.surrogate.cqr.XGBQuantileSurrogate` and
   :class:`cgem_ext.surrogate.cqr.TwoStageXGBQuantileSurrogate` —
   XGBoost-backed quantile regressors plus the CQR layer, exercised on
   the same synthetic-fixture style as ``test_surrogate.py``.

All tests are static (no compiled CGEM binary required) so they run in
CI under the ``not needs_cgem_binary`` filter.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# ──────────────────────────────────────────────────────────────────────
# Shared synthetic fixture (mirrors tests/test_surrogate.py::_row /
# ::_fixture_df, kept local to avoid import-time coupling).
# ──────────────────────────────────────────────────────────────────────


def _row(
    *,
    g_peak,
    dgdt,
    duration,
    who,
    cm_label,
    deh,
    g_tol,
    cm_psi=0.0,
    cm_cov=0.0,
    cm_agsm=0.0,
    cm_pbg=0.0,
    hlap_min=100.0,
    c_bank_min=10.0,
    time_to_greyout=None,
    time_to_blackout=None,
    time_to_gloc=None,
    category="championship",
    maneuver="dummy",
    arm="standard",
):
    return {
        "row_id": f"{maneuver}_{who}_{cm_label}",
        "maneuver": maneuver,
        "maneuver_category": category,
        "arm": arm,
        "who_profile": who,
        "g_tolerance_multiplier": g_tol,
        "dehydration_label": "none" if deh == 0 else "mild",
        "dehydration_level": deh,
        "countermeasures_label": cm_label,
        "gsuit_max_psi": cm_psi,
        "gsuit_coverage_fraction": cm_cov,
        "agsm_effectiveness": cm_agsm,
        "pbg_max_mmhg": cm_pbg,
        "g_peak_abs": g_peak,
        "dgdt_max_g_per_s": dgdt,
        "profile_duration_s": duration,
        "status": "ok",
        "hlap_min": hlap_min,
        "c_bank_min": c_bank_min,
        "time_to_greyout_s": time_to_greyout,
        "time_to_blackout_s": time_to_blackout,
        "time_to_gloc_s": time_to_gloc,
        "event_greyout": 0 if time_to_greyout is None else 1,
        "event_blackout": 0 if time_to_blackout is None else 1,
        "event_gloc": 0 if time_to_gloc is None else 1,
    }


def _fixture_df(n=400, seed=0, heteroscedastic=False):
    """Synthetic fixture with two maneuver categories and an optional
    heteroscedasticity switch.

    When ``heteroscedastic=True`` the Gaussian noise on ``hlap_min``
    scales with G_peak — used to demonstrate that CQR achieves better
    coverage than the homoscedastic Mondrian baseline.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        g_peak = float(rng.uniform(2, 9))
        dgdt = float(rng.uniform(1, 12))
        duration = float(rng.uniform(5, 20))
        hlap = 110 - 4 * g_peak
        c_bank = max(0.5, 12 - 0.8 * g_peak)
        ttg = (
            max(0.5, 6 - 0.4 * g_peak + rng.normal(0, 0.2))
            if g_peak > 5
            else None
        )
        # sigma ranges ~0.5 .. ~4.5 across the G-peak grid.
        sigma = 0.5 + (g_peak / 9.0) * 4.0 if heteroscedastic else 1.0
        rows.append(
            _row(
                g_peak=g_peak,
                dgdt=dgdt,
                duration=duration,
                who=int(rng.integers(1, 7)),
                cm_label=str(rng.choice(["none", "agsm", "suit_agsm"])),
                deh=float(rng.choice([0.0, 0.3, 0.7])),
                g_tol=float(rng.choice([0.85, 1.0, 1.15])),
                hlap_min=hlap + rng.normal(0, sigma),
                c_bank_min=c_bank + rng.normal(0, 0.3),
                time_to_greyout=ttg,
                category=str(rng.choice(["championship", "military_acm"])),
            )
        )
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────
# MondrianCQR — pure-numpy correctness
# ──────────────────────────────────────────────────────────────────────


def test_mondrian_cqr_fit_widths_reflect_heteroscedasticity():
    from cgem_ext.surrogate.conformal import MondrianCQR

    rng = np.random.default_rng(0)
    n_per_stratum = 400
    strata = np.repeat(["a", "b", "c"], n_per_stratum)
    sigmas = {"a": 0.5, "b": 1.5, "c": 3.0}
    truth = rng.uniform(0, 10, len(strata))
    # Lower / upper quantile predictions: deliberately too tight so CQR
    # must inflate the bracket.
    q_lo = truth - 0.5
    q_hi = truth + 0.5
    # Add per-stratum noise to the *target* — this is what CQR must
    # absorb.
    target = truth.copy().astype(float)
    for stratum, sigma in sigmas.items():
        mask = strata == stratum
        target[mask] = target[mask] + rng.normal(0, sigma, mask.sum())

    cqr = MondrianCQR(alpha=0.10).fit(
        cal_q_lo=q_lo,
        cal_q_hi=q_hi,
        cal_targets=target,
        cal_strata=strata,
        min_per_stratum=20,
    )
    # Each stratum got calibrated.
    assert len(cqr.fit_info.strata) == 3
    quantiles = {s.name: s.quantile for s in cqr.fit_info.strata}
    # Higher-noise stratum has a larger conformity-score quantile.
    assert quantiles["c"] > quantiles["b"] > quantiles["a"]


def test_mondrian_cqr_coverage_near_nominal_on_heteroscedastic_data():
    from cgem_ext.surrogate.conformal import MondrianCQR

    rng = np.random.default_rng(1)
    alpha = 0.10
    n_cal_per_stratum = 400
    n_test_per_stratum = 400
    strata_names = ["a", "b", "c"]
    sigmas = {"a": 0.5, "b": 1.5, "c": 3.0}

    # Build calibration set
    cal_strata = np.repeat(strata_names, n_cal_per_stratum)
    cal_truth = rng.uniform(0, 10, len(cal_strata))
    cal_target = cal_truth.copy().astype(float)
    for s, sigma in sigmas.items():
        m = cal_strata == s
        cal_target[m] = cal_target[m] + rng.normal(0, sigma, m.sum())
    cal_q_lo = cal_truth - 0.5
    cal_q_hi = cal_truth + 0.5

    cqr = MondrianCQR(alpha=alpha).fit(
        cal_q_lo=cal_q_lo,
        cal_q_hi=cal_q_hi,
        cal_targets=cal_target,
        cal_strata=cal_strata,
    )

    # Fresh test set drawn the same way
    test_strata = np.repeat(strata_names, n_test_per_stratum)
    test_truth = rng.uniform(0, 10, len(test_strata))
    test_target = test_truth.copy().astype(float)
    for s, sigma in sigmas.items():
        m = test_strata == s
        test_target[m] = test_target[m] + rng.normal(0, sigma, m.sum())
    test_q_lo = test_truth - 0.5
    test_q_hi = test_truth + 0.5

    cov = cqr.coverage(
        test_q_lo=test_q_lo,
        test_q_hi=test_q_hi,
        test_targets=test_target,
        test_strata=test_strata,
    )
    # Overall coverage within ±5 pp of nominal on this benign synthetic.
    assert abs(cov["_overall"] - (1 - alpha)) < 0.05
    # Each stratum within ±10 pp (smaller-stratum sample noise).
    for s in strata_names:
        assert abs(cov[s] - (1 - alpha)) < 0.10


def test_mondrian_cqr_unseen_stratum_falls_back_to_global():
    from cgem_ext.surrogate.conformal import MondrianCQR

    rng = np.random.default_rng(2)
    cal_strata = np.repeat(["a", "b"], 100)
    cal_truth = rng.uniform(0, 10, 200)
    cal_target = cal_truth + rng.normal(0, 1.0, 200)
    cal_q_lo = cal_truth - 0.5
    cal_q_hi = cal_truth + 0.5

    cqr = MondrianCQR(alpha=0.10).fit(
        cal_q_lo=cal_q_lo,
        cal_q_hi=cal_q_hi,
        cal_targets=cal_target,
        cal_strata=cal_strata,
    )
    # Predict on an unseen stratum 'c' — should use the global quantile.
    test_strata = np.array(["c", "c", "c"])
    test_q_lo = np.array([0.0, 0.0, 0.0])
    test_q_hi = np.array([1.0, 1.0, 1.0])
    lo, hi = cqr.predict_interval(
        test_q_lo=test_q_lo, test_q_hi=test_q_hi, test_strata=test_strata
    )
    fallback = cqr.fit_info.fallback_quantile
    np.testing.assert_allclose(lo, test_q_lo - fallback)
    np.testing.assert_allclose(hi, test_q_hi + fallback)


def test_mondrian_cqr_alpha_validation():
    from cgem_ext.surrogate.conformal import MondrianCQR

    with pytest.raises(ValueError):
        MondrianCQR(alpha=0.0)
    with pytest.raises(ValueError):
        MondrianCQR(alpha=1.0)
    with pytest.raises(ValueError):
        MondrianCQR(alpha=-0.1)


def test_mondrian_cqr_fit_handles_misaligned_inputs():
    from cgem_ext.surrogate.conformal import MondrianCQR

    cqr = MondrianCQR(alpha=0.05)
    with pytest.raises(ValueError, match="aligned"):
        cqr.fit(
            cal_q_lo=np.zeros(10),
            cal_q_hi=np.ones(10),
            cal_targets=np.zeros(9),  # mismatch
            cal_strata=np.array(["a"] * 10),
        )


def test_mondrian_cqr_fit_rejects_all_nan_inputs():
    from cgem_ext.surrogate.conformal import MondrianCQR

    cqr = MondrianCQR(alpha=0.05)
    with pytest.raises(ValueError, match="finite"):
        cqr.fit(
            cal_q_lo=np.full(20, np.nan),
            cal_q_hi=np.full(20, np.nan),
            cal_targets=np.full(20, np.nan),
            cal_strata=np.array(["a"] * 20),
        )


# ──────────────────────────────────────────────────────────────────────
# XGBQuantileSurrogate — fit/predict on synthetic continuous target
# ──────────────────────────────────────────────────────────────────────


def test_xgb_quantile_rejects_censored_target():
    from cgem_ext.surrogate import XGBQuantileSurrogate

    with pytest.raises(ValueError, match="censored"):
        XGBQuantileSurrogate("time_to_greyout_s")


def test_xgb_quantile_alpha_validation():
    from cgem_ext.surrogate import XGBQuantileSurrogate

    with pytest.raises(ValueError, match="alpha"):
        XGBQuantileSurrogate("hlap_min", alpha=0.0)
    with pytest.raises(ValueError, match="alpha"):
        XGBQuantileSurrogate("hlap_min", alpha=1.0)


def test_xgb_quantile_fit_predict_interval():
    from cgem_ext.surrogate import XGBQuantileSurrogate

    df = _fixture_df(n=600, seed=0)
    train = df.iloc[:400].copy()
    cal = df.iloc[400:500].copy()
    test = df.iloc[500:].copy()

    sur = XGBQuantileSurrogate("hlap_min", alpha=0.10).fit(
        train, calibration_df=cal
    )
    point = sur.predict(test)
    lo, hi = sur.predict_interval(test)

    assert point.shape == (len(test),)
    assert lo.shape == (len(test),)
    assert hi.shape == (len(test),)
    # Bracket is well-ordered.
    assert np.all(lo <= hi + 1e-9)
    # Coverage on the held-out test slice within ±10 pp of nominal.
    cov = sur.coverage(test)
    assert abs(cov["_overall"] - 0.90) < 0.10


def test_xgb_quantile_predict_quantiles_sorted_after_crossing_guard():
    from cgem_ext.surrogate import XGBQuantileSurrogate

    df = _fixture_df(n=400, seed=1)
    train = df.iloc[:280].copy()
    cal = df.iloc[280:].copy()
    sur = XGBQuantileSurrogate("hlap_min", alpha=0.20).fit(
        train, calibration_df=cal
    )
    q_lo, q_hi = sur.predict_quantiles(cal)
    # The non-crossing guard enforces q_lo <= q_hi for every row.
    assert np.all(q_lo <= q_hi + 1e-9)


def test_xgb_quantile_unfitted_raises():
    from cgem_ext.surrogate import XGBQuantileSurrogate

    sur = XGBQuantileSurrogate("hlap_min")
    with pytest.raises(RuntimeError, match="not fitted"):
        _ = sur.fit_info
    with pytest.raises(RuntimeError, match="not fitted"):
        _ = sur.cqr


def test_xgb_quantile_smoke_under_heteroscedasticity():
    """Smoke test: both CQR and the homoscedastic Mondrian baseline
    deliver coverage within ±10 pp of nominal on a heteroscedastic
    synthetic fixture.

    This is *not* a manuscript-grade comparison of CQR vs Mondrian.
    The synthetic Gaussian fixture is too benign to demonstrate the
    CQR advantage cleanly, and a passing assertion here would be
    over-claimed evidence for the manuscript.

    The genuine empirical anchor lives in
    :func:`test_cqr_fixes_time_to_gloc_under_coverage` (gated by the
    ``needs_cgem_binary`` marker), which fits both layers on the
    OSF-pre-registered ``cgem_synthetic_v1`` split and reports actual
    per-stratum coverage on ``time_to_gloc_s``.
    """
    from cgem_ext.surrogate import (
        MondrianSplitConformal,
        XGBQuantileSurrogate,
        XGBSurrogate,
    )

    df = _fixture_df(n=900, seed=42, heteroscedastic=True)
    train = df.iloc[:600].copy()
    cal = df.iloc[600:750].copy()
    test = df.iloc[750:].copy()

    cqr = XGBQuantileSurrogate("hlap_min", alpha=0.10).fit(
        train, calibration_df=cal
    )
    cov_cqr = cqr.coverage(test)

    base = XGBSurrogate("hlap_min").fit(train)
    cal_pred = base.predict(cal)
    msc = MondrianSplitConformal(alpha=0.10).fit(
        cal_predictions=cal_pred,
        cal_targets=cal["hlap_min"].to_numpy(),
        cal_strata=cal["maneuver_category"].to_numpy(),
    )
    test_pred = base.predict(test)
    cov_msc = msc.coverage(
        test_predictions=test_pred,
        test_targets=test["hlap_min"].to_numpy(),
        test_strata=test["maneuver_category"].to_numpy(),
    )

    # Both methods deliver coverage within a reasonable band on the
    # synthetic fixture — neither pathologically over- nor under-covers.
    assert 0.80 <= cov_cqr["_overall"] <= 1.0
    assert 0.80 <= cov_msc["_overall"] <= 1.0


@pytest.mark.needs_cgem_binary
def test_cqr_fixes_time_to_gloc_under_coverage():
    """Empirical anchor: CQR's coverage on ``time_to_gloc_s`` should
    be closer to the nominal 95 % than the existing homoscedastic
    Mondrian under-coverage of 0.861 reported in the OSF
    pre-registered held-out split.

    Loads ``data/datasets/cgem_synthetic_v1.parquet`` (the canonical
    paper-1 dataset), reproduces the 70/15/15 stratified split with
    master seed 42, fits :class:`TwoStageXGBQuantileSurrogate`, and
    asserts:

    1. CQR coverage on event-positive ``time_to_gloc_s`` rows is at
       least 0.90 — within 5 pp of nominal 0.95.
    2. CQR coverage is strictly closer to 0.95 than the existing
       homoscedastic Mondrian point estimate of 0.861.

    This test is gated by ``needs_cgem_binary`` because it loads the
    full parquet (which is generated from the compiled CGEM binary
    and lives on the developer machine). CI runs ``-m "not
    needs_cgem_binary"`` and skips it; a manual run via
    ``pytest tests/test_cqr.py::test_cqr_fixes_time_to_gloc_under_coverage``
    is what the manuscript Section 3.3 cites.

    Pre-registration: the success threshold (≥ 0.90) is locked in the
    OSF amendment authored before this test is first executed; any
    failure must be reported transparently in Section 3.3 rather than
    silently relaxed.
    """
    from pathlib import Path

    from cgem_ext.data.splits import stratified_split
    from cgem_ext.surrogate import TwoStageXGBQuantileSurrogate

    parquet_path = (
        Path(__file__).parent.parent
        / "data"
        / "datasets"
        / "cgem_synthetic_v1.parquet"
    )
    if not parquet_path.exists():
        pytest.skip(f"canonical dataset not found at {parquet_path}")

    df = pd.read_parquet(parquet_path)
    # Apply the same status filter the splitter uses internally so the
    # index arrays line up with the DataFrame view.
    if "status" in df.columns:
        df = df[df["status"] == "ok"].reset_index(drop=True)
    split = stratified_split(df, seed=42)
    train_df = df.iloc[split.train_idx].copy()
    val_df = df.iloc[split.val_idx].copy()
    test_df = df.iloc[split.test_idx].copy()

    model = TwoStageXGBQuantileSurrogate(
        "time_to_gloc_s", alpha=0.05
    ).fit(train_df, calibration_df=val_df)
    cov = model.coverage(test_df)

    # Empirical-anchor primary assertion: coverage on event-positive
    # rows of the held-out test split is within 5 pp of nominal.
    assert cov["_overall"] >= 0.90, (
        f"CQR coverage on time_to_gloc_s is {cov['_overall']:.3f} "
        f"(< 0.90); the OSF-amended success threshold is not met. "
        f"Per-stratum: {cov}"
    )

    # Comparison to the homoscedastic Mondrian baseline result of 0.861
    # reported in §3.3 of manuscript.md (commit 1f1a816).
    baseline_under_coverage = 0.861
    nominal = 1 - 0.05
    assert abs(cov["_overall"] - nominal) < abs(baseline_under_coverage - nominal), (
        f"CQR coverage {cov['_overall']:.3f} is not closer to nominal "
        f"{nominal:.3f} than the homoscedastic Mondrian baseline "
        f"{baseline_under_coverage:.3f}."
    )


# ──────────────────────────────────────────────────────────────────────
# TwoStageXGBQuantileSurrogate — censored target end-to-end
# ──────────────────────────────────────────────────────────────────────


def test_two_stage_xgb_quantile_rejects_continuous_target():
    from cgem_ext.surrogate import TwoStageXGBQuantileSurrogate

    with pytest.raises(ValueError, match="continuous"):
        TwoStageXGBQuantileSurrogate("hlap_min")


def test_two_stage_xgb_quantile_fit_and_predict_interval():
    from cgem_ext.surrogate import TwoStageXGBQuantileSurrogate

    df = _fixture_df(n=900, seed=3)
    # Ensure enough event-positive rows in train and cal for the stage-2
    # quantile regressor to fit.
    train = df.iloc[:600].copy()
    cal = df.iloc[600:750].copy()
    test = df.iloc[750:].copy()

    model = TwoStageXGBQuantileSurrogate(
        "time_to_greyout_s", alpha=0.10
    ).fit(train, calibration_df=cal)

    p_event = model.predict_event_probability(test)
    cond_time = model.predict(test)
    expected = model.predict_expected_time(test)

    assert p_event.shape == (len(test),)
    assert cond_time.shape == (len(test),)
    assert expected.shape == (len(test),)
    assert ((p_event >= 0) & (p_event <= 1)).all()
    assert (expected >= 0).all()

    # Bracket on event-positive rows is well-ordered.
    test_event = test[test["event_greyout"] == 1]
    if len(test_event) >= 5:
        lo, hi = model.predict_interval(test_event)
        assert np.all(lo <= hi + 1e-9)


def test_two_stage_xgb_quantile_coverage_on_event_positive_rows():
    from cgem_ext.surrogate import TwoStageXGBQuantileSurrogate

    df = _fixture_df(n=1200, seed=4)
    train = df.iloc[:800].copy()
    cal = df.iloc[800:1000].copy()
    test = df.iloc[1000:].copy()

    model = TwoStageXGBQuantileSurrogate(
        "time_to_greyout_s", alpha=0.10
    ).fit(train, calibration_df=cal)

    test_event = test[test["event_greyout"] == 1].copy()
    if len(test_event) < 10:
        pytest.skip("Insufficient event-positive rows in test slice")
    cov = model.coverage(test)
    # Empirical coverage on the event-positive subset within a generous
    # band — small n inflates binomial CIs.
    assert 0.65 <= cov["_overall"] <= 1.0


def test_build_quantile_surrogate_routes_correctly():
    from cgem_ext.surrogate import (
        TwoStageXGBQuantileSurrogate,
        XGBQuantileSurrogate,
        build_quantile_surrogate,
    )

    assert isinstance(
        build_quantile_surrogate("hlap_min"), XGBQuantileSurrogate
    )
    assert isinstance(
        build_quantile_surrogate("time_to_greyout_s"),
        TwoStageXGBQuantileSurrogate,
    )
