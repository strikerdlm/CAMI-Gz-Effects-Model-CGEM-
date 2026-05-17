#!/usr/bin/env python3
"""Export structured figure data for AMHP Paper 1 (Figs 1-4).

Loads ``cgem_synthetic_v1.parquet``, applies the OSF-pre-registered
stratified 70/15/15 split (seed=42), trains all 5 surrogates, calibrates
conformal intervals on the validation split, runs calibration diagnostics
(reliability diagrams + ECE), collects OOD scores from both in-distribution
and leave-one-group-out folds, and writes four JSON files to
``data/results/figures/``.

Usage::

    python scripts/generate_figure_data.py

Outputs (all under ``data/results/figures/``):

- ``parity_data.json``       — per-target (y_true, y_pred, category) for Fig 1
- ``coverage_data.json``     — per-target per-stratum coverage for Fig 2
- ``calibration_data.json``  — per-bin stats + ECE for Fig 3
- ``ood_scores.json``        — per-row Mahalanobis scores for Fig 4
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cgem_ext.data.splits import leave_one_group_out, stratified_split
from cgem_ext.ood import MahalanobisOOD
from cgem_ext.surrogate import (
    MondrianSplitConformal,
    TwoStageXGBSurrogate,
    XGBSurrogate,
    censored_targets,
    continuous_targets,
)
from cgem_ext.surrogate.calibration import (
    classifier_calibration,
    regression_calibration,
)

OUT_DIR = _REPO_ROOT / "data" / "results" / "figures"
DATASET = _REPO_ROOT / "data" / "datasets" / "cgem_synthetic_v1.parquet"
N_BINS = 10
SEED = 42


def _as_native(obj):
    """Recursively convert numpy types → native Python for JSON serialisation."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return [_as_native(x) for x in obj.tolist()]
    if isinstance(obj, dict):
        return {str(k): _as_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_as_native(x) for x in obj]
    return obj


def _validate_env() -> pd.DataFrame:
    if not DATASET.is_file():
        sys.exit(f"Dataset not found: {DATASET}")
    df = pd.read_parquet(DATASET)
    print(f"Loaded {len(df)} rows from {DATASET.name}")
    return df


def _export_json(name: str, data: dict) -> None:
    path = OUT_DIR / name
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(_as_native(data), fh, indent=2, ensure_ascii=False)
    size = os.path.getsize(path)
    print(f"  → {path.name}  ({size:,} bytes)")


# ──────────────────────────────────────────────────────────────────────
# Fig 1 — parity_data.json
# ──────────────────────────────────────────────────────────────────────


def _collect_parity(df: pd.DataFrame) -> dict:
    sp = stratified_split(df, seed=SEED)
    train_df, _val_df, test_df = sp.apply(df)
    targets_info = {}

    for spec in continuous_targets():
        model = XGBSurrogate(spec.name).fit(train_df)
        y_true = test_df[spec.name].to_numpy(dtype=float)
        y_pred = model.predict(test_df)
        valid = ~np.isnan(y_true) & ~np.isnan(y_pred)
        targets_info[spec.name] = {
            "units": spec.units,
            "description": spec.description,
            "y_true": y_true[valid].tolist(),
            "y_pred": y_pred[valid].tolist(),
            "category": test_df["maneuver_category"].to_numpy()[valid].tolist(),
        }

    for spec in censored_targets():
        model = TwoStageXGBSurrogate(spec.name).fit(train_df)
        ev_mask = test_df[spec.event_column].astype(int).to_numpy() == 1
        # Stage 1 — classifier parity (all rows)
        p_event = model.predict_event_probability(test_df)
        ev_all = test_df[spec.event_column].astype(int).to_numpy()
        valid_cls = ~np.isnan(ev_all) & ~np.isnan(p_event)
        targets_info[f"{spec.name}_classifier"] = {
            "units": "probability",
            "description": f"P({spec.event_column})",
            "y_true": ev_all[valid_cls].tolist(),
            "y_pred": p_event[valid_cls].tolist(),
            "category": test_df["maneuver_category"].to_numpy()[valid_cls].tolist(),
        }
        # Stage 2 — regressor parity (event=1 rows only)
        if ev_mask.sum() >= 5:
            cond_time = model.predict(test_df.loc[ev_mask])
            y_true_ev = test_df.loc[ev_mask, spec.name].to_numpy(dtype=float)
            valid_reg = ~np.isnan(y_true_ev) & ~np.isnan(cond_time)
            targets_info[f"{spec.name}_regressor"] = {
                "units": spec.units,
                "description": f"E[{spec.name} | event=1]",
                "y_true": y_true_ev[valid_reg].tolist(),
                "y_pred": cond_time[valid_reg].tolist(),
                "category": test_df.loc[ev_mask, "maneuver_category"].to_numpy()[valid_reg].tolist(),
            }

    return {"split": "test", "seed": SEED, "targets": targets_info}


# ──────────────────────────────────────────────────────────────────────
# Fig 2 — coverage_data.json
# ──────────────────────────────────────────────────────────────────────


def _collect_coverage(df: pd.DataFrame) -> dict:
    sp = stratified_split(df, seed=SEED)
    train_df, val_df, test_df = sp.apply(df)
    coverage_info = {}

    for spec in continuous_targets():
        model = XGBSurrogate(spec.name).fit(train_df)
        cp = MondrianSplitConformal(alpha=0.05).fit(
            cal_predictions=model.predict(val_df),
            cal_targets=val_df[spec.name],
            cal_strata=val_df["maneuver_category"],
        )
        cov = cp.coverage(
            test_predictions=model.predict(test_df),
            test_targets=test_df[spec.name],
            test_strata=test_df["maneuver_category"],
        )
        coverage_info[spec.name] = cov

    for spec in censored_targets():
        model = TwoStageXGBSurrogate(spec.name).fit(train_df)
        # Stage 1 classifier calibration
        cp_cls = MondrianSplitConformal(alpha=0.05).fit(
            cal_predictions=model.predict_event_probability(val_df),
            cal_targets=val_df[spec.event_column].astype(int),
            cal_strata=val_df["maneuver_category"],
        )
        cov_cls = cp_cls.coverage(
            test_predictions=model.predict_event_probability(test_df),
            test_targets=test_df[spec.event_column].astype(int),
            test_strata=test_df["maneuver_category"],
        )
        coverage_info[f"{spec.name}_classifier"] = cov_cls

        # Stage 2 regressor calibration (event=1 rows only)
        ev_val = val_df[spec.event_column].astype(int).to_numpy(dtype=bool)
        ev_test = test_df[spec.event_column].astype(int).to_numpy(dtype=bool)
        if ev_val.sum() >= 20 and ev_test.sum() >= 5:
            cp_reg = MondrianSplitConformal(alpha=0.05).fit(
                cal_predictions=model.predict(val_df.loc[ev_val]),
                cal_targets=val_df.loc[ev_val, spec.name],
                cal_strata=val_df.loc[ev_val, "maneuver_category"],
            )
            cov_reg = cp_reg.coverage(
                test_predictions=model.predict(test_df.loc[ev_test]),
                test_targets=test_df.loc[ev_test, spec.name],
                test_strata=test_df.loc[ev_test, "maneuver_category"],
            )
            coverage_info[f"{spec.name}_regressor"] = cov_reg

    return {
        "alpha": 0.05,
        "nominal_coverage": 0.95,
        "split": "test",
        "seed": SEED,
        "targets": coverage_info,
    }


# ──────────────────────────────────────────────────────────────────────
# Fig 3 — calibration_data.json
# ──────────────────────────────────────────────────────────────────────


def _collect_calibration(df: pd.DataFrame) -> dict:
    sp = stratified_split(df, seed=SEED)
    train_df, _val_df, test_df = sp.apply(df)
    cal_info = {}

    for spec in continuous_targets():
        model = XGBSurrogate(spec.name).fit(train_df)
        y_true = test_df[spec.name].to_numpy(dtype=float)
        y_pred = model.predict(test_df)
        result = regression_calibration(y_true, y_pred, target=spec.name, n_bins=N_BINS)
        cal_info[spec.name] = result.to_dict()

    for spec in censored_targets():
        model = TwoStageXGBSurrogate(spec.name).fit(train_df)
        y_true = test_df[spec.event_column].astype(int).to_numpy()
        y_prob = model.predict_event_probability(test_df)
        result = classifier_calibration(y_true, y_prob, target=spec.name, n_bins=N_BINS)
        cal_info[spec.name] = result.to_dict()

    return {"n_bins": N_BINS, "split": "test", "seed": SEED, "targets": cal_info}


# ──────────────────────────────────────────────────────────────────────
# Fig 4 — ood_scores.json
# ──────────────────────────────────────────────────────────────────────


def _collect_ood(df: pd.DataFrame) -> dict:
    from cgem_ext.ood import ConformalAbstention

    sp = stratified_split(df, seed=SEED)
    train_df, val_df, test_df = sp.apply(df)

    mh = MahalanobisOOD().fit(train_df)

    # Chi² threshold (parametric, assumes MVN)
    chi2_threshold = float(mh.threshold_chi2)
    test_scores = mh.score(test_df)
    chi2_in_env = (test_scores <= chi2_threshold).tolist()
    chi2_in_env_rate = float(np.mean(chi2_in_env))

    # Conformal abstention (distribution-free, per OSF pre-registration H3a)
    abst = ConformalAbstention(alpha=0.05).calibrate(mh.score(val_df))
    conf_threshold = float(abst.threshold)
    conf_in_env = abst.is_in_envelope(test_scores).tolist()
    conf_in_env_rate = float(np.mean(conf_in_env))

    id_data = {
        "scores": test_scores.tolist(),
        "chi2_threshold": chi2_threshold,
        "chi2_is_in_envelope": chi2_in_env,
        "chi2_in_envelope_rate": chi2_in_env_rate,
        "conformal_threshold": conf_threshold,
        "conformal_is_in_envelope": conf_in_env,
        "conformal_in_envelope_rate": conf_in_env_rate,
        "category": test_df["maneuver_category"].tolist(),
        "row_id": test_df["row_id"].tolist(),
    }

    # LOGO folds — hold out each category, score as "OOD"
    logo_folds = {}
    for gs in leave_one_group_out(df):
        train_g, test_g = gs.apply(df)
        if len(train_g) < 50 or len(test_g) < 5:
            continue
        mh_fold = MahalanobisOOD().fit(train_g)
        scores = mh_fold.score(test_g)
        logo_folds[gs.held_out] = {
            "scores": scores.tolist(),
            "chi2_threshold": float(mh_fold.threshold_chi2),
            "n_train": len(train_g),
            "n_test": len(test_g),
        }

    return {
        "in_distribution": id_data,
        "logo_folds": logo_folds,
    }


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────


def main() -> None:
    df = _validate_env()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [
        ("parity_data.json", _collect_parity),
        ("coverage_data.json", _collect_coverage),
        ("calibration_data.json", _collect_calibration),
        ("ood_scores.json", _collect_ood),
    ]

    for filename, collector in tasks:
        print(f"Building {filename} ...")
        data = collector(df)
        _export_json(filename, data)

    print(f"\nAll exports written to {OUT_DIR}")


if __name__ == "__main__":
    main()
