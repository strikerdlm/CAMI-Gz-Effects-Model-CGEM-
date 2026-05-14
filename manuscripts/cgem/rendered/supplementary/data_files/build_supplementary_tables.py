"""Build numeric tables for IJNMBE supplementary material.

Produces:
  data/results/supplementary/table_s1_rf_baseline.json
  data/results/supplementary/table_s2_per_stratum_coverage.json

These JSON artifacts back Table S1 (RandomForest baseline vs XGBoost main
table) and Table S2 (per-target, per-stratum Mondrian conformal coverage
with Clopper-Pearson exact 95 % binomial CIs and bootstrap-resampled
coverage CIs) that the IJNMBE manuscript cites in §3.2 and §3.3.

The frozen dataset (`data/datasets/cgem_synthetic_v1.parquet`), the
OSF-pre-registered split (master seed 42, stratified by maneuver
category, dropping status != "ok" rows), and the Mondrian conformal
calibrator are all reused verbatim from `cgem_ext`. The CQR vs Mondrian
numbers for `time_to_gloc_s` are taken from the committed JSON artifact
`data/results/cqr/cqr_vs_mondrian_time_to_gloc.json` rather than
recomputed, so the supplementary table is auditable against the same
numbers cited in §3.3.

Usage:
    cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
    /root/.venvs/cgem-ci/bin/python scripts/build_supplementary_tables.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta as _beta

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from cgem_ext.data.splits import stratified_split  # noqa: E402
from cgem_ext.surrogate.baseline import (  # noqa: E402
    RFSurrogate,
    TwoStageRFSurrogate,
)
from cgem_ext.surrogate.conformal import MondrianSplitConformal  # noqa: E402
from cgem_ext.surrogate.targets import TARGETS  # noqa: E402
from cgem_ext.surrogate.xgb import (  # noqa: E402
    TwoStageXGBSurrogate,
    XGBSurrogate,
)

DATASET = REPO / "data" / "datasets" / "cgem_synthetic_v1.parquet"
OUT_DIR = REPO / "data" / "results" / "supplementary"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
ALPHA = 0.05
NOMINAL = 1.0 - ALPHA
N_BOOT = 1000

# Strata that appear in the test split (4 maneuver categories)
STRATA = ("championship", "conceptual", "extreme_post_stall", "military_acm")


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def clopper_pearson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    """Exact two-sided Clopper-Pearson binomial CI."""
    if n == 0:
        return (float("nan"), float("nan"))
    alpha = 1.0 - conf
    lo = 0.0 if k == 0 else _beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def bootstrap_coverage_ci(
    indicators: np.ndarray, n_boot: int = N_BOOT, conf: float = 0.95, seed: int = SEED
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of {0,1} indicators."""
    if indicators.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = indicators.size
    means = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        means[b] = indicators[idx].mean()
    alpha = 1.0 - conf
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def bootstrap_metric_ci(
    fn, *arrays, n_boot: int = N_BOOT, conf: float = 0.95, seed: int = SEED
) -> tuple[float, float, float]:
    """Generic percentile bootstrap CI for any (arrays...) -> scalar fn.

    Returns (point, lo, hi). Resampling is paired across all arrays.
    """
    arrays = [np.asarray(a) for a in arrays]
    n = arrays[0].size
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    point = float(fn(*arrays))
    boots = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boots[b] = fn(*[a[idx] for a in arrays])
    alpha = 1.0 - conf
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return point, float(lo), float(hi)


def r2_score(y: np.ndarray, yhat: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    if y.size < 2:
        return float("nan")
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    if ss_tot == 0.0:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def rmse(y: np.ndarray, yhat: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    if y.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def mae(y: np.ndarray, yhat: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    if y.size == 0:
        return float("nan")
    return float(np.mean(np.abs(y - yhat)))


# ──────────────────────────────────────────────────────────────────────
# Table S1: RandomForest baseline vs XGBoost main table
# ──────────────────────────────────────────────────────────────────────


def build_table_s1(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    """Fit RF + XGB for every target, then collect parallel metrics."""
    rows: list[dict] = []

    for spec in TARGETS:
        name = spec.name
        censored = spec.censored
        print(f"  fitting RF/XGB for {name} (censored={censored}) …", flush=True)

        # Build RF and XGB models
        if censored:
            rf = TwoStageRFSurrogate(name).fit(train_df)
            xgb = TwoStageXGBSurrogate(name).fit(train_df)
            event_col = spec.event_column
            assert event_col is not None
            test_event_mask = test_df[event_col].astype(int).to_numpy() == 1
            test_event_df = test_df[test_event_mask].reset_index(drop=True)
            y_true = test_event_df[name].astype(float).to_numpy()
            # (1) Stage-2 regressor only (conditional on event=1) — the
            # *correct* operational metric for the two-stage XGB framework.
            rf_yhat = rf.predict(test_event_df)
            xgb_yhat = xgb.predict(test_event_df)
            # (2) Damped expected-time prediction P(event) * E[time | event]
            # evaluated on event-positive rows. This is the failure mode
            # cited in the manuscript: P(event) < 1 systematically damps
            # the prediction below the true event time on rows where the
            # event DID happen. RF P(event) is lower than XGB's on
            # event-positive rows (~0.8 vs ~0.9), so RF gets a much
            # larger negative R^2.
            rf_damped = rf.predict_expected_time(test_event_df)
            xgb_damped = xgb.predict_expected_time(test_event_df)
            row = {
                "target": name,
                "censored": True,
                "n_test_event": int(test_event_mask.sum()),
                "n_test_total": int(len(test_df)),
                # Stage-2 conditional metrics (the right comparison)
                "rf_r2_event": bootstrap_metric_ci(r2_score, y_true, rf_yhat),
                "rf_rmse_event": bootstrap_metric_ci(rmse, y_true, rf_yhat),
                "rf_mae_event": bootstrap_metric_ci(mae, y_true, rf_yhat),
                "xgb_r2_event": bootstrap_metric_ci(r2_score, y_true, xgb_yhat),
                "xgb_rmse_event": bootstrap_metric_ci(rmse, y_true, xgb_yhat),
                "xgb_mae_event": bootstrap_metric_ci(mae, y_true, xgb_yhat),
                # Damped P*E expected-time evaluated on event-positive rows
                "rf_r2_damped_event": bootstrap_metric_ci(r2_score, y_true, rf_damped),
                "xgb_r2_damped_event": bootstrap_metric_ci(r2_score, y_true, xgb_damped),
                "rf_p_event_mean_on_event_pos": float(
                    rf.predict_event_probability(test_event_df).mean()
                ),
                "xgb_p_event_mean_on_event_pos": float(
                    xgb.predict_event_probability(test_event_df).mean()
                ),
                "units": getattr(spec, "units", "") or "",
            }
        else:
            rf = RFSurrogate(name).fit(train_df)
            xgb = XGBSurrogate(name).fit(train_df)
            y_true = test_df[name].astype(float).to_numpy()
            rf_yhat = rf.predict(test_df)
            xgb_yhat = xgb.predict(test_df)
            row = {
                "target": name,
                "censored": False,
                "n_test_event": int(len(test_df)),
                "n_test_total": int(len(test_df)),
                "rf_r2_event": bootstrap_metric_ci(r2_score, y_true, rf_yhat),
                "rf_rmse_event": bootstrap_metric_ci(rmse, y_true, rf_yhat),
                "rf_mae_event": bootstrap_metric_ci(mae, y_true, rf_yhat),
                "xgb_r2_event": bootstrap_metric_ci(r2_score, y_true, xgb_yhat),
                "xgb_rmse_event": bootstrap_metric_ci(rmse, y_true, xgb_yhat),
                "xgb_mae_event": bootstrap_metric_ci(mae, y_true, xgb_yhat),
                "rf_r2_damped_event": None,
                "xgb_r2_damped_event": None,
                "rf_p_event_mean_on_event_pos": None,
                "xgb_p_event_mean_on_event_pos": None,
                "units": getattr(spec, "units", "") or "",
            }
        rows.append(row)
        print(
            f"    RF R²={row['rf_r2_event'][0]:.3f} | "
            f"XGB R²={row['xgb_r2_event'][0]:.3f}",
            flush=True,
        )

    return {
        "_meta": {
            "produced_by": "scripts/build_supplementary_tables.py::build_table_s1",
            "dataset": str(DATASET.relative_to(REPO)),
            "split": "stratified_split(seed=42, drop_status_error=True, val=0.15, test=0.15)",
            "n_boot": N_BOOT,
            "rf_defaults": "n_estimators=400, max_depth=None, random_state=42 (cgem_ext.surrogate.baseline._DEFAULT_*)",
            "note": (
                "RF expected-time prediction (P(event) * E[time | event]) is "
                "evaluated on the full test split — this is the metric that "
                "produces the large-negative-R^2 values cited in manuscript §3.2."
            ),
        },
        "rows": rows,
    }


# ──────────────────────────────────────────────────────────────────────
# Table S2: per-target, per-stratum Mondrian conformal coverage with
# Clopper-Pearson exact 95 % binomial CIs and bootstrap-resampled coverage
# ──────────────────────────────────────────────────────────────────────


def _fit_mondrian_for_target(
    spec, train_df: pd.DataFrame, val_df: pd.DataFrame
) -> tuple:
    """Return (model, calibrator, label) tuples for a target.

    For a continuous target, returns one tuple. For a censored target,
    returns two tuples: the binary classifier on event-occurrence, and the
    two-stage regressor's event-time prediction on event-positive rows.
    """
    if spec.censored:
        # Two-stage: fit on train, calibrate classifier on val (full),
        # calibrate regressor on val (event-positive rows).
        model = TwoStageXGBSurrogate(spec.name).fit(train_df)
        assert spec.event_column is not None
        # Classifier calibrator — calibrate on probability of event,
        # against the observed event indicator.
        cls_cal = MondrianSplitConformal(alpha=ALPHA)
        proba = model.predict_event_probability(val_df)
        events = val_df[spec.event_column].astype(int).to_numpy()
        cls_cal.fit(
            cal_predictions=proba,
            cal_targets=events.astype(float),
            cal_strata=val_df["maneuver_category"].to_numpy(),
        )
        # Regressor calibrator — fit on val event-positive rows.
        val_event_mask = events == 1
        val_event = val_df[val_event_mask].reset_index(drop=True)
        reg_cal = MondrianSplitConformal(alpha=ALPHA)
        reg_yhat = model.predict(val_event)
        reg_y = val_event[spec.name].astype(float).to_numpy()
        reg_cal.fit(
            cal_predictions=reg_yhat,
            cal_targets=reg_y,
            cal_strata=val_event["maneuver_category"].to_numpy(),
        )
        return (
            ("classifier", model, cls_cal),
            ("regressor", model, reg_cal),
        )
    else:
        model = XGBSurrogate(spec.name).fit(train_df)
        cal = MondrianSplitConformal(alpha=ALPHA)
        yhat = model.predict(val_df)
        y = val_df[spec.name].astype(float).to_numpy()
        cal.fit(
            cal_predictions=yhat,
            cal_targets=y,
            cal_strata=val_df["maneuver_category"].to_numpy(),
        )
        return (("regressor", model, cal),)


def _coverage_indicators_continuous(
    model, calibrator, test_df: pd.DataFrame, target: str
) -> tuple[np.ndarray, np.ndarray]:
    """Return (indicator∈{0,1}, stratum) for each test row."""
    strata = test_df["maneuver_category"].to_numpy()
    yhat = model.predict(test_df)
    lo, hi = calibrator.predict_interval(test_predictions=yhat, test_strata=strata)
    y = test_df[target].astype(float).to_numpy()
    ind = ((y >= lo) & (y <= hi)).astype(int)
    return ind, strata


def _coverage_indicators_classifier(
    model, calibrator, test_df: pd.DataFrame, event_col: str
) -> tuple[np.ndarray, np.ndarray]:
    strata = test_df["maneuver_category"].to_numpy()
    proba = model.predict_event_probability(test_df)
    lo, hi = calibrator.predict_interval(test_predictions=proba, test_strata=strata)
    y = test_df[event_col].astype(int).to_numpy().astype(float)
    ind = ((y >= lo) & (y <= hi)).astype(int)
    return ind, strata


def _coverage_indicators_regressor(
    model, calibrator, test_df: pd.DataFrame, spec
) -> tuple[np.ndarray, np.ndarray]:
    """Regressor coverage is on event-positive rows only."""
    assert spec.event_column is not None
    mask = test_df[spec.event_column].astype(int).to_numpy() == 1
    test_event = test_df[mask].reset_index(drop=True)
    strata = test_event["maneuver_category"].to_numpy()
    yhat = model.predict(test_event)
    lo, hi = calibrator.predict_interval(test_predictions=yhat, test_strata=strata)
    y = test_event[spec.name].astype(float).to_numpy()
    ind = ((y >= lo) & (y <= hi)).astype(int)
    return ind, strata


def build_table_s2(
    train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame
) -> dict:
    """Fit Mondrian conformal per (target, stage), then compute coverage
    overall and per stratum with Clopper-Pearson CIs + bootstrap CIs."""

    cqr_path = REPO / "data" / "results" / "cqr" / "cqr_vs_mondrian_time_to_gloc.json"
    cqr_data = json.loads(cqr_path.read_text())

    rows: list[dict] = []

    for spec in TARGETS:
        print(f"  Mondrian on {spec.name} …", flush=True)
        stages = _fit_mondrian_for_target(spec, train_df, val_df)

        for stage_name, model, cal in stages:
            if spec.censored and stage_name == "classifier":
                target_col = (
                    spec.event_column if spec.event_column else spec.name
                )
                row_label = f"{spec.name} (classifier)"
                ind, strata = _coverage_indicators_classifier(
                    model, cal, test_df, spec.event_column  # type: ignore[arg-type]
                )
            elif spec.censored and stage_name == "regressor":
                row_label = f"{spec.name} (regressor, Mondrian)"
                ind, strata = _coverage_indicators_regressor(model, cal, test_df, spec)
            else:
                row_label = f"{spec.name} (Mondrian)"
                ind, strata = _coverage_indicators_continuous(
                    model, cal, test_df, spec.name
                )

            row = {"target": row_label, "censored": spec.censored, "strata": {}}
            # Overall
            n_overall = int(ind.size)
            k_overall = int(ind.sum())
            point_overall = float(k_overall / n_overall) if n_overall else float("nan")
            cp_lo, cp_hi = clopper_pearson(k_overall, n_overall)
            bs_lo, bs_hi = bootstrap_coverage_ci(ind)
            row["overall"] = {
                "n": n_overall,
                "k": k_overall,
                "coverage": point_overall,
                "cp_lo": cp_lo,
                "cp_hi": cp_hi,
                "bs_lo": bs_lo,
                "bs_hi": bs_hi,
            }
            # Per-stratum
            for s in STRATA:
                mask_s = strata == s
                n_s = int(mask_s.sum())
                k_s = int(ind[mask_s].sum())
                point_s = float(k_s / n_s) if n_s else float("nan")
                cp_lo_s, cp_hi_s = clopper_pearson(k_s, n_s)
                bs_lo_s, bs_hi_s = bootstrap_coverage_ci(ind[mask_s])
                row["strata"][s] = {
                    "n": n_s,
                    "k": k_s,
                    "coverage": point_s,
                    "cp_lo": cp_lo_s,
                    "cp_hi": cp_hi_s,
                    "bs_lo": bs_lo_s,
                    "bs_hi": bs_hi_s,
                }
            rows.append(row)

    # Append the CQR row from the committed artifact (this is the
    # PRIMARY conformal layer for time_to_gloc_s under OSF amendment H5).
    cqr_row = {
        "target": "time_to_gloc_s (regressor, CQR — primary, OSF-amended H5)",
        "censored": True,
        "overall": {
            "n": cqr_data["_meta"]["n_test_event_positive"],
            "k": int(round(cqr_data["cqr"]["_overall"] * cqr_data["_meta"]["n_test_event_positive"])),
            "coverage": cqr_data["cqr"]["_overall"],
            # CP from committed (n=36)
            "cp_lo": 0.855,
            "cp_hi": 0.999,
            "bs_lo": None,
            "bs_hi": None,
        },
        "strata": {
            "championship": {
                "n": 1,
                "k": int(round(cqr_data["cqr"]["championship"])),
                "coverage": cqr_data["cqr"]["championship"],
                "cp_lo": clopper_pearson(int(round(cqr_data["cqr"]["championship"])), 1)[0],
                "cp_hi": clopper_pearson(int(round(cqr_data["cqr"]["championship"])), 1)[1],
                "bs_lo": None,
                "bs_hi": None,
            },
            "conceptual": {"n": 0, "k": 0, "coverage": float("nan"), "cp_lo": float("nan"), "cp_hi": float("nan"), "bs_lo": None, "bs_hi": None},
            "extreme_post_stall": {"n": 0, "k": 0, "coverage": float("nan"), "cp_lo": float("nan"), "cp_hi": float("nan"), "bs_lo": None, "bs_hi": None},
            "military_acm": {
                "n": 35,
                "k": int(round(cqr_data["cqr"]["military_acm"] * 35)),
                "coverage": cqr_data["cqr"]["military_acm"],
                "cp_lo": 0.847,
                "cp_hi": 0.999,
                "bs_lo": None,
                "bs_hi": None,
            },
        },
    }
    rows.append(cqr_row)

    return {
        "_meta": {
            "produced_by": "scripts/build_supplementary_tables.py::build_table_s2",
            "dataset": str(DATASET.relative_to(REPO)),
            "split": "stratified_split(seed=42, drop_status_error=True)",
            "nominal_coverage": NOMINAL,
            "alpha": ALPHA,
            "n_boot": N_BOOT,
            "cqr_source": "data/results/cqr/cqr_vs_mondrian_time_to_gloc.json",
            "note": (
                "Per-stratum coverage on event-positive rows of censored "
                "regressors carries small n in some strata (championship "
                "n=1, conceptual n=0, extreme_post_stall n=0 for "
                "time_to_gloc_s); Clopper-Pearson CIs are exact and are "
                "the inferentially conservative choice at small n."
            ),
        },
        "rows": rows,
    }


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────


def main() -> int:
    print(f"Loading dataset: {DATASET}")
    df = pd.read_parquet(DATASET)
    print(f"  n_rows={len(df)}, columns={len(df.columns)}")

    print("Computing OSF-pre-registered split (seed=42, drop_status_error=True)…")
    split = stratified_split(df, seed=SEED, drop_status_error=True)
    print(f"  {split!r}")

    train_df, val_df, test_df = split.apply(
        df[df["status"] == "ok"].reset_index(drop=True)
    )
    print(f"  train={len(train_df)} val={len(val_df)} test={len(test_df)}")

    print("\n=== Building Table S1 (RF vs XGB) ===")
    s1 = build_table_s1(train_df, test_df)
    s1_path = OUT_DIR / "table_s1_rf_baseline.json"
    s1_path.write_text(json.dumps(s1, indent=2, default=float))
    print(f"  written: {s1_path}")

    print("\n=== Building Table S2 (per-stratum Mondrian + bootstrap + Clopper-Pearson) ===")
    s2 = build_table_s2(train_df, val_df, test_df)
    s2_path = OUT_DIR / "table_s2_per_stratum_coverage.json"
    s2_path.write_text(json.dumps(s2, indent=2, default=float))
    print(f"  written: {s2_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
