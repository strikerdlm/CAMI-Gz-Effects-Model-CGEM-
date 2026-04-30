"""Unit + smoke tests for the cgem_ext.ood subpackage.

The static tests (synthetic fixtures) validate the API contract:
feature extraction shape and encoding, MinCovDet fit + chi^2 threshold,
conformal calibration coverage, IsolationForest baseline behaviour, and
the public one-shot helpers.

The dataset-level tests (gated by ``needs_cgem_binary`` because they
load the canonical paper-1 parquet which is generated from the binary)
exercise the detectors end-to-end on the real synthetic dataset and
record the empirical leave-one-group-out AUROC for both the
Mahalanobis backbone and the IsolationForest baseline. Those AUROC
checks use a *sanity* threshold (>= 0.5, i.e. better than random), not
a research-grade threshold; the headline numbers are a paper-1 result
and live in the OOD model card.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ──────────────────────────────────────────────────────────────────────
# Synthetic fixtures — no CGEM binary needed
# ──────────────────────────────────────────────────────────────────────


def _row(
    *,
    who_profile,
    cm_label,
    g_peak_abs=5.0,
    dgdt=4.0,
    duration=12.0,
    dehydration_level=0.0,
    g_tol=1.0,
    cm_psi=0.0,
    cm_cov=0.0,
    cm_agsm=0.0,
    cm_pbg=0.0,
    maneuver="dummy",
    category="championship",
    arm="standard",
    status="ok",
):
    """Build one synthetic row matching the parquet schema."""
    return {
        "row_id": f"{maneuver}_{who_profile}_{cm_label}",
        "maneuver": maneuver,
        "maneuver_category": category,
        "arm": arm,
        "who_profile": who_profile,
        "g_tolerance_multiplier": g_tol,
        "dehydration_label": "none" if dehydration_level == 0 else "mild",
        "dehydration_level": dehydration_level,
        "countermeasures_label": cm_label,
        "gsuit_max_psi": cm_psi,
        "gsuit_coverage_fraction": cm_cov,
        "agsm_effectiveness": cm_agsm,
        "pbg_max_mmhg": cm_pbg,
        "g_peak_abs": g_peak_abs,
        "dgdt_max_g_per_s": dgdt,
        "profile_duration_s": duration,
        "status": status,
    }


def _fixture_df(n=200, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        rows.append(
            _row(
                who_profile=int(rng.integers(1, 7)),
                cm_label=str(rng.choice(["none", "agsm", "suit_agsm"])),
                g_peak_abs=float(rng.uniform(2, 9)),
                dgdt=float(rng.uniform(1, 12)),
                duration=float(rng.uniform(5, 20)),
                dehydration_level=float(rng.choice([0.0, 0.3, 0.7])),
                g_tol=float(rng.choice([0.85, 1.0, 1.15])),
                category=str(rng.choice(["championship", "military_acm"])),
            )
        )
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────
# Feature extraction
# ──────────────────────────────────────────────────────────────────────


def test_feature_columns_stable():
    from cgem_ext.ood.features import FEATURE_COLUMNS, NUMERIC_FEATURES, WHO_LEVELS

    # The column ordering is part of the contract; never change without
    # re-fitting downstream models.
    assert FEATURE_COLUMNS[: len(NUMERIC_FEATURES)] == NUMERIC_FEATURES
    assert FEATURE_COLUMNS[len(NUMERIC_FEATURES) : len(NUMERIC_FEATURES) + len(WHO_LEVELS)] == WHO_LEVELS
    assert FEATURE_COLUMNS[-1] == "cm_ordinal"


def test_extract_features_shape():
    from cgem_ext.ood.features import FEATURE_COLUMNS, extract_features

    df = _fixture_df(n=50)
    feats = extract_features(df)
    assert feats.shape == (50, len(FEATURE_COLUMNS))
    assert list(feats.columns) == list(FEATURE_COLUMNS)
    assert feats.dtypes.unique().tolist() == [np.dtype("float64")]


def test_extract_features_who_one_hot():
    from cgem_ext.ood.features import WHO_LEVELS, extract_features

    rows = [
        _row(who_profile=1, cm_label="none"),
        _row(who_profile=6, cm_label="agsm"),
        _row(who_profile=None, cm_label="suit_agsm"),
    ]
    feats = extract_features(pd.DataFrame(rows))
    # Each row's WHO_LEVELS slice should sum to exactly 1.
    who_block = feats[list(WHO_LEVELS)].to_numpy()
    np.testing.assert_array_equal(who_block.sum(axis=1), np.ones(3))
    assert feats.iloc[0]["who_1"] == 1.0
    assert feats.iloc[1]["who_6"] == 1.0
    assert feats.iloc[2]["who_custom"] == 1.0


def test_extract_features_cm_ordinal():
    from cgem_ext.ood.features import extract_features

    rows = [
        _row(who_profile=2, cm_label="none"),
        _row(who_profile=2, cm_label="agsm"),
        _row(who_profile=2, cm_label="suit_agsm"),
    ]
    feats = extract_features(pd.DataFrame(rows))
    np.testing.assert_array_equal(
        feats["cm_ordinal"].to_numpy(), np.array([0.0, 1.0, 2.0])
    )


def test_extract_features_missing_columns_raises():
    from cgem_ext.ood.features import extract_features

    df = pd.DataFrame([{"who_profile": 1, "countermeasures_label": "none"}])
    with pytest.raises(KeyError, match="missing required columns"):
        extract_features(df)


# ──────────────────────────────────────────────────────────────────────
# MahalanobisOOD
# ──────────────────────────────────────────────────────────────────────


def test_mahalanobis_fit_and_threshold():
    from cgem_ext.ood import MahalanobisOOD

    df = _fixture_df(n=200, seed=0)
    mh = MahalanobisOOD().fit(df)
    info = mh.fit_info
    assert info.n_train == 200
    assert info.rank_effective <= 17  # FEATURE_COLUMNS length
    # chi2(df=k, q=0.95) is monotonic in df; must be positive.
    assert mh.threshold_chi2 > 0


def test_mahalanobis_score_shape_and_nonneg():
    from cgem_ext.ood import MahalanobisOOD

    df = _fixture_df(n=120, seed=1)
    train, query = df.iloc[:100], df.iloc[100:]
    mh = MahalanobisOOD().fit(train)
    s = mh.score(query)
    assert s.shape == (20,)
    # squared Mahalanobis distance is non-negative
    assert (s >= 0).all()


def test_mahalanobis_in_envelope_consistent_with_threshold():
    from cgem_ext.ood import MahalanobisOOD

    df = _fixture_df(n=200, seed=2)
    mh = MahalanobisOOD().fit(df)
    s = mh.score(df)
    in_env = mh.is_in_envelope(df)
    np.testing.assert_array_equal(in_env, s <= mh.threshold_chi2)


def test_mahalanobis_unfitted_raises():
    from cgem_ext.ood import MahalanobisOOD

    mh = MahalanobisOOD()
    with pytest.raises(RuntimeError, match="not fitted"):
        _ = mh.threshold_chi2


def test_mahalanobis_invalid_alpha_raises():
    from cgem_ext.ood import MahalanobisOOD

    with pytest.raises(ValueError):
        MahalanobisOOD(alpha=-0.1)
    with pytest.raises(ValueError):
        MahalanobisOOD(alpha=1.5)


# ──────────────────────────────────────────────────────────────────────
# ConformalAbstention
# ──────────────────────────────────────────────────────────────────────


def test_conformal_calibrate_threshold_at_target_quantile():
    from cgem_ext.ood import ConformalAbstention

    rng = np.random.default_rng(0)
    cal = rng.normal(loc=0, scale=1, size=1000)
    abst = ConformalAbstention(alpha=0.05).calibrate(cal)
    # ~95% of calibration data should be in-envelope (score <= threshold).
    in_env_rate = (cal <= abst.threshold).mean()
    assert 0.93 <= in_env_rate <= 0.97


def test_conformal_finite_sample_correction():
    """For small n, the conformal quantile uses ceil((n+1)*(1-a))/n and so
    should *over*-cover slightly. We verify that the empirical in-envelope
    rate on the calibration set itself is >= (1 - alpha).
    """
    from cgem_ext.ood import ConformalAbstention

    rng = np.random.default_rng(0)
    cal = rng.normal(loc=0, scale=1, size=100)
    abst = ConformalAbstention(alpha=0.05).calibrate(cal)
    in_env_rate = (cal <= abst.threshold).mean()
    assert in_env_rate >= 0.95


def test_conformal_too_few_samples_raises():
    from cgem_ext.ood import ConformalAbstention

    with pytest.raises(ValueError, match="at least 20"):
        ConformalAbstention().calibrate(np.array([1.0, 2.0, 3.0]))


def test_conformal_unfitted_raises():
    from cgem_ext.ood import ConformalAbstention

    abst = ConformalAbstention()
    with pytest.raises(RuntimeError, match="not calibrated"):
        _ = abst.threshold


def test_conformal_pipeline_integration():
    """Mahalanobis + Conformal together — abstention rate matches alpha."""
    from cgem_ext.ood import ConformalAbstention, MahalanobisOOD

    df = _fixture_df(n=300, seed=3)
    train, val, test = df.iloc[:200], df.iloc[200:250], df.iloc[250:]
    mh = MahalanobisOOD().fit(train)
    abst = ConformalAbstention(alpha=0.10).calibrate(mh.score(val))
    test_in = abst.is_in_envelope(mh.score(test))
    # On exchangeable data, in-env rate ~= 1 - alpha (with finite-sample wiggle).
    assert 0.80 <= test_in.mean() <= 1.0


# ──────────────────────────────────────────────────────────────────────
# IsolationForestOOD baseline
# ──────────────────────────────────────────────────────────────────────


def test_isolation_forest_fit_and_score():
    from cgem_ext.ood import IsolationForestOOD

    df = _fixture_df(n=200, seed=4)
    iso = IsolationForestOOD(random_state=42).fit(df)
    s = iso.score(df)
    assert s.shape == (200,)
    # Score is (signed) decision-function negated; finite values.
    assert np.all(np.isfinite(s))


def test_isolation_forest_in_envelope_returns_majority_inliers():
    from cgem_ext.ood import IsolationForestOOD

    df = _fixture_df(n=200, seed=5)
    iso = IsolationForestOOD(random_state=42, contamination=0.1).fit(df)
    in_env = iso.is_in_envelope(df)
    # With contamination=0.1, predict() flags ~10% as outliers; 90% in-env.
    assert in_env.mean() >= 0.85


# ──────────────────────────────────────────────────────────────────────
# One-shot helper
# ──────────────────────────────────────────────────────────────────────


def test_is_in_envelope_helper():
    from cgem_ext.ood import is_in_envelope

    df = _fixture_df(n=200, seed=6)
    train, query = df.iloc[:150], df.iloc[150:]
    mask = is_in_envelope(train, query)
    assert mask.shape == (50,)
    assert mask.dtype == bool


# ──────────────────────────────────────────────────────────────────────
# End-to-end on the canonical paper-1 dataset
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def synthetic_v1_df(repo_root):
    path = repo_root / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    if not path.is_file():
        pytest.skip("cgem_synthetic_v1.parquet not present")
    return pd.read_parquet(path)


@pytest.mark.needs_cgem_binary
def test_calibration_coverage_on_test_split(synthetic_v1_df):
    """Headline conformal calibration result: empirical in-envelope rate
    on the test split is within +/-2pp of the nominal 95%."""
    from sklearn.metrics import roc_auc_score  # noqa: F401  (also covers import)

    from cgem_ext.data.splits import stratified_split
    from cgem_ext.ood import ConformalAbstention, MahalanobisOOD

    sp = stratified_split(synthetic_v1_df, seed=42)
    train_df, val_df, test_df = sp.apply(synthetic_v1_df)

    mh = MahalanobisOOD().fit(train_df)
    abst = ConformalAbstention(alpha=0.05).calibrate(mh.score(val_df))
    in_env_rate = abst.is_in_envelope(mh.score(test_df)).mean()

    # H3a target from the OSF preregistration.
    assert abs(in_env_rate - 0.95) <= 0.02, (
        f"Test in-envelope rate {in_env_rate:.3f} deviates >2pp from nominal 0.95"
    )


@pytest.mark.needs_cgem_binary
def test_logo_auroc_better_than_random(synthetic_v1_df):
    """Sanity check: LOGO AUROC > 0.5 (better than random) for at least
    one of the held-out categories. The paper-grade thresholds live in
    the OOD model card / OSF preregistration, not here.
    """
    from sklearn.metrics import roc_auc_score

    from cgem_ext.data.splits import leave_one_group_out
    from cgem_ext.ood import IsolationForestOOD, MahalanobisOOD

    aurocs_mh = {}
    aurocs_iso = {}
    for gs in leave_one_group_out(synthetic_v1_df):
        train_g, test_g = gs.apply(synthetic_v1_df)
        if len(train_g) < 50 or len(test_g) < 5:
            continue
        mh_g = MahalanobisOOD().fit(train_g)
        iso_g = IsolationForestOOD(random_state=42).fit(train_g)
        in_dist_sample = train_g.sample(min(500, len(train_g)), random_state=0)
        eval_set = pd.concat([in_dist_sample, test_g], ignore_index=True)
        y = np.concatenate([np.zeros(len(in_dist_sample)), np.ones(len(test_g))])
        aurocs_mh[gs.held_out] = roc_auc_score(y, mh_g.score(eval_set))
        aurocs_iso[gs.held_out] = roc_auc_score(y, iso_g.score(eval_set))

    assert aurocs_mh and aurocs_iso, "No LOGO folds were evaluated"

    # At least one detector on at least one fold should be better than random.
    best_mh = max(aurocs_mh.values())
    best_iso = max(aurocs_iso.values())
    assert best_mh > 0.5 or best_iso > 0.5, (
        f"Both detectors are at-or-below random across all folds: "
        f"max Mahalanobis={best_mh:.3f}, max IsolationForest={best_iso:.3f}"
    )
