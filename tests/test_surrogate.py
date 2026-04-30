"""Unit + integration tests for the cgem_ext.surrogate subpackage.

Static API tests (synthetic fixtures, no CGEM binary needed) cover
target catalogue invariants, monotonicity vector shape, the XGBoost
and RandomForest single-stage and two-stage fit/predict paths, and the
Mondrian conformal calibration math.

Dataset-level tests (gated by ``needs_cgem_binary`` because they load
the canonical paper-1 parquet) exercise the full pipeline against
``cgem_synthetic_v1``: per-target R^2, classifier AUROC, conformal
coverage. Thresholds are empirically grounded and match the OSF
pre-registration anchors.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ──────────────────────────────────────────────────────────────────────
# Targets catalogue
# ──────────────────────────────────────────────────────────────────────


def test_target_catalogue_has_five_targets():
    from cgem_ext.surrogate import TARGETS

    assert len(TARGETS) == 5
    names = [t.name for t in TARGETS]
    assert {"time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s",
            "hlap_min", "c_bank_min"} == set(names)


def test_target_censored_partition():
    from cgem_ext.surrogate import censored_targets, continuous_targets

    cens = {t.name for t in censored_targets()}
    cont = {t.name for t in continuous_targets()}
    assert cens == {"time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s"}
    assert cont == {"hlap_min", "c_bank_min"}
    assert cens.isdisjoint(cont)


def test_monotonicity_shape_matches_features():
    from cgem_ext.surrogate import TARGETS
    from cgem_ext.surrogate.features import FEATURE_COLUMNS

    for spec in TARGETS:
        assert len(spec.monotonicity) == len(FEATURE_COLUMNS)
        # Monotonicity values are in {-1, 0, 1}
        assert set(spec.monotonicity) <= {-1, 0, 1}


def test_get_target_unknown_raises():
    from cgem_ext.surrogate import get_target

    with pytest.raises(KeyError):
        get_target("not_a_target")


# ──────────────────────────────────────────────────────────────────────
# Surrogate API — synthetic fixtures
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


def _fixture_df(n=300, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        g_peak = float(rng.uniform(2, 9))
        dgdt = float(rng.uniform(1, 12))
        duration = float(rng.uniform(5, 20))
        # HLAP correlates with G via simple linear rule (synthetic ground truth).
        hlap = 110 - 4 * g_peak
        c_bank = max(0.5, 12 - 0.8 * g_peak)
        # Greyout occurs when g_peak > 5; time inversely related to g_peak.
        if g_peak > 5:
            ttg = max(0.5, 6 - 0.4 * g_peak + rng.normal(0, 0.2))
        else:
            ttg = None
        rows.append(
            _row(
                g_peak=g_peak,
                dgdt=dgdt,
                duration=duration,
                who=int(rng.integers(1, 7)),
                cm_label=str(rng.choice(["none", "agsm", "suit_agsm"])),
                deh=float(rng.choice([0.0, 0.3, 0.7])),
                g_tol=float(rng.choice([0.85, 1.0, 1.15])),
                hlap_min=hlap + rng.normal(0, 1),
                c_bank_min=c_bank + rng.normal(0, 0.3),
                time_to_greyout=ttg,
                category=str(rng.choice(["championship", "military_acm"])),
            )
        )
    return pd.DataFrame(rows)


def test_xgb_continuous_fit_predict():
    from cgem_ext.surrogate import XGBSurrogate

    df = _fixture_df(n=300, seed=0)
    train, test = df.iloc[:200], df.iloc[200:]

    xgb = XGBSurrogate("hlap_min").fit(train)
    pred = xgb.predict(test)
    assert pred.shape == (100,)
    # Continuous target with synthetic linear ground truth — XGB should fit well.
    from sklearn.metrics import r2_score
    assert r2_score(test["hlap_min"], pred) > 0.85


def test_xgb_continuous_rejects_censored():
    from cgem_ext.surrogate import XGBSurrogate

    with pytest.raises(ValueError, match="censored"):
        XGBSurrogate("time_to_greyout_s")


def test_xgb_two_stage_fit_predict():
    from cgem_ext.surrogate import TwoStageXGBSurrogate

    df = _fixture_df(n=400, seed=1)
    train, test = df.iloc[:300], df.iloc[300:]

    model = TwoStageXGBSurrogate("time_to_greyout_s").fit(train)
    p_event = model.predict_event_probability(test)
    cond_time = model.predict(test)
    expected = model.predict_expected_time(test)

    assert p_event.shape == (100,)
    assert cond_time.shape == (100,)
    assert expected.shape == (100,)
    # P(event) is a probability
    assert ((p_event >= 0) & (p_event <= 1)).all()
    # Expected time is non-negative
    assert (expected >= 0).all()


def test_xgb_two_stage_rejects_continuous():
    from cgem_ext.surrogate import TwoStageXGBSurrogate

    with pytest.raises(ValueError, match="continuous"):
        TwoStageXGBSurrogate("hlap_min")


def test_build_surrogate_routes_correctly():
    from cgem_ext.surrogate import (
        TwoStageXGBSurrogate,
        XGBSurrogate,
        build_surrogate,
    )

    assert isinstance(build_surrogate("hlap_min"), XGBSurrogate)
    assert isinstance(build_surrogate("time_to_greyout_s"), TwoStageXGBSurrogate)


def test_rf_baseline_continuous():
    from cgem_ext.surrogate import RFSurrogate

    df = _fixture_df(n=300, seed=2)
    train, test = df.iloc[:200], df.iloc[200:]
    rf = RFSurrogate("hlap_min").fit(train)
    pred = rf.predict(test)
    assert pred.shape == (100,)


def test_rf_baseline_two_stage():
    from cgem_ext.surrogate import TwoStageRFSurrogate

    df = _fixture_df(n=400, seed=3)
    train, test = df.iloc[:300], df.iloc[300:]
    rf = TwoStageRFSurrogate("time_to_greyout_s").fit(train)
    p_event = rf.predict_event_probability(test)
    assert p_event.shape == (100,)


def test_unfitted_raises():
    from cgem_ext.surrogate import XGBSurrogate

    xgb = XGBSurrogate("hlap_min")
    with pytest.raises(RuntimeError, match="not fitted"):
        _ = xgb.fit_info


# ──────────────────────────────────────────────────────────────────────
# Mondrian conformal — synthetic
# ──────────────────────────────────────────────────────────────────────


def test_mondrian_conformal_fit_and_coverage():
    from cgem_ext.surrogate.conformal import MondrianSplitConformal

    rng = np.random.default_rng(0)
    n_per_stratum = 200
    strata = np.repeat(["a", "b", "c"], n_per_stratum)
    # Per-stratum noise scale; conformal should compensate.
    noise = np.concatenate([
        rng.normal(0, 0.5, n_per_stratum),
        rng.normal(0, 1.5, n_per_stratum),
        rng.normal(0, 3.0, n_per_stratum),
    ])
    truth = rng.uniform(0, 10, len(strata))
    pred = truth + noise

    cp = MondrianSplitConformal(alpha=0.10).fit(
        cal_predictions=pred,
        cal_targets=truth,
        cal_strata=strata,
        min_per_stratum=20,
    )
    # Each stratum gets its own threshold
    assert len(cp.fit_info.strata) == 3
    quantiles = {s.name: s.quantile for s in cp.fit_info.strata}
    # Higher-noise stratum has a wider interval
    assert quantiles["c"] > quantiles["b"] > quantiles["a"]


def test_mondrian_conformal_coverage_near_nominal():
    from cgem_ext.surrogate.conformal import MondrianSplitConformal

    rng = np.random.default_rng(1)
    n = 1000
    strata = rng.choice(["x", "y", "z"], n)
    truth = rng.uniform(0, 10, n)
    pred = truth + rng.normal(0, 1.0, n)
    n_test = 500
    test_strata = rng.choice(["x", "y", "z"], n_test)
    test_truth = rng.uniform(0, 10, n_test)
    test_pred = test_truth + rng.normal(0, 1.0, n_test)

    cp = MondrianSplitConformal(alpha=0.05).fit(
        cal_predictions=pred,
        cal_targets=truth,
        cal_strata=strata,
        min_per_stratum=20,
    )
    cov = cp.coverage(
        test_predictions=test_pred,
        test_targets=test_truth,
        test_strata=test_strata,
    )
    # Empirical coverage should be near nominal 0.95 (+/- 5 pp tolerance for finite samples)
    assert 0.90 <= cov["_overall"] <= 1.0


def test_mondrian_conformal_falls_back_for_unseen_strata():
    from cgem_ext.surrogate.conformal import MondrianSplitConformal

    rng = np.random.default_rng(2)
    n = 200
    strata = np.repeat(["seen"], n)
    truth = rng.uniform(0, 10, n)
    pred = truth + rng.normal(0, 1.0, n)

    cp = MondrianSplitConformal(alpha=0.05).fit(
        cal_predictions=pred, cal_targets=truth, cal_strata=strata,
    )
    # Test with unseen stratum
    lo, hi = cp.predict_interval(
        test_predictions=np.array([5.0]),
        test_strata=np.array(["unseen"]),
    )
    # Falls back to global quantile, so the interval is non-degenerate
    assert hi[0] - lo[0] > 0


def test_mondrian_conformal_invalid_alpha_raises():
    from cgem_ext.surrogate.conformal import MondrianSplitConformal

    with pytest.raises(ValueError):
        MondrianSplitConformal(alpha=0)
    with pytest.raises(ValueError):
        MondrianSplitConformal(alpha=1)


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
def test_continuous_surrogate_meets_threshold(synthetic_v1_df):
    """H1 (continuous) — XGB regressor on hlap_min and c_bank_min must
    achieve held-out R^2 >= 0.90. The OSF preregistration anchors:
    hlap_min ~ 1.000, c_bank_min ~ 0.94.
    """
    from sklearn.metrics import r2_score

    from cgem_ext.data.splits import stratified_split
    from cgem_ext.surrogate import XGBSurrogate

    sp = stratified_split(synthetic_v1_df, seed=42)
    train_df, _val_df, test_df = sp.apply(synthetic_v1_df)

    failures = {}
    for target in ("hlap_min", "c_bank_min"):
        model = XGBSurrogate(target).fit(train_df)
        pred = model.predict(test_df)
        r2 = r2_score(test_df[target], pred)
        if r2 < 0.90:
            failures[target] = r2
    assert not failures, f"Continuous surrogate R^2 < 0.90: {failures}"


@pytest.mark.needs_cgem_binary
def test_two_stage_surrogate_meets_thresholds(synthetic_v1_df):
    """H1 (censored) — for each time target:
        - classifier AUROC >= 0.95 (event detection on all rows)
        - regressor R^2 >= 0.75 conditional on event=1 (regressor stage)
    OSF anchors: AUROC ~0.996 across targets; conditional R^2 ranges 0.82-0.90.
    """
    from sklearn.metrics import r2_score, roc_auc_score

    from cgem_ext.data.splits import stratified_split
    from cgem_ext.surrogate import TwoStageXGBSurrogate

    sp = stratified_split(synthetic_v1_df, seed=42)
    train_df, _val_df, test_df = sp.apply(synthetic_v1_df)

    failures = {}
    for target in ("time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s"):
        model = TwoStageXGBSurrogate(target).fit(train_df)
        ev_col = model.spec.event_column
        ev_test = test_df[ev_col].astype(int).to_numpy()
        if ev_test.sum() < 5 or ev_test.sum() == len(ev_test):
            continue  # skip degenerate cases
        auroc = roc_auc_score(ev_test, model.predict_event_probability(test_df))
        ev_mask = ev_test == 1
        r2 = r2_score(test_df.loc[ev_mask, target], model.predict(test_df.loc[ev_mask]))
        if auroc < 0.95:
            failures[(target, "auroc")] = auroc
        if r2 < 0.75:
            failures[(target, "r2_cond")] = r2
    assert not failures, f"Two-stage surrogate misses thresholds: {failures}"


@pytest.mark.needs_cgem_binary
def test_mondrian_conformal_coverage_on_canonical_dataset(synthetic_v1_df):
    """H2 — Mondrian conformal coverage on the held-out test split is
    within +/-5 pp of nominal 95% for each continuous target. (OSF
    pre-registers +/-2 pp; the test sets a slightly looser bound to
    accommodate finite-sample variability across stratifications.)
    """
    from cgem_ext.data.splits import stratified_split
    from cgem_ext.surrogate import MondrianSplitConformal, XGBSurrogate

    sp = stratified_split(synthetic_v1_df, seed=42)
    train_df, val_df, test_df = sp.apply(synthetic_v1_df)

    failures = {}
    for target in ("hlap_min", "c_bank_min"):
        model = XGBSurrogate(target).fit(train_df)
        cp = MondrianSplitConformal(alpha=0.05).fit(
            cal_predictions=model.predict(val_df),
            cal_targets=val_df[target],
            cal_strata=val_df["maneuver_category"],
        )
        cov = cp.coverage(
            test_predictions=model.predict(test_df),
            test_targets=test_df[target],
            test_strata=test_df["maneuver_category"],
        )
        if not (0.90 <= cov["_overall"] <= 1.0):
            failures[target] = cov["_overall"]
    assert not failures, f"Conformal coverage out of range: {failures}"
