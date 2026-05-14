"""Materialize the frozen OSF-pre-registered artifacts cited in the
manuscript supplementary list and OSF preregistration text.

Outputs:
  docs/publication/osf_search_spaces.json
  docs/publication/osf_split_indices.parquet
  manuscripts/ijnmbe/rendered/supplementary/osf_search_spaces.json
  manuscripts/ijnmbe/rendered/supplementary/osf_split_indices.parquet

The search-space JSON records the Optuna search bounds frozen at OSF
posting time. The split-indices Parquet records the integer indices of
the OSF-pre-registered train/val/test partition (stratified, seed=42,
status=="ok").

Usage:
    cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
    /root/.venvs/cgem-ci/bin/python scripts/build_osf_artifacts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from cgem_ext.data.splits import stratified_split  # noqa: E402

DATASET = REPO / "data" / "datasets" / "cgem_synthetic_v1.parquet"
DOCS_DIR = REPO / "docs" / "publication"
SUP_DIR = REPO / "manuscripts" / "ijnmbe" / "rendered" / "supplementary"
SUP_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────
# Search spaces (frozen at OSF posting time)
# ──────────────────────────────────────────────────────────────────────

SEARCH_SPACES = {
    "_meta": {
        "purpose": "OSF-pre-registered Optuna search-space envelope for the XGBoost surrogate "
                   "and the IsolationForest OOD baseline. Frozen at OSF posting time; the "
                   "production models use the defaults below (no Optuna search executed for "
                   "paper 1 — defaults selected to be conservative and reproducible; the "
                   "Optuna sweep is paper-2 scope per `scripts/optuna_search.py` placeholder).",
        "rng_seed": 42,
        "cv": "stratified KFold(n_splits=5, shuffle=True, random_state=42) on the train split only",
        "selection_objective": (
            "Per-target: regressors → 5-fold cross-validated R² on train-internal folds; "
            "classifiers → 5-fold cross-validated AUROC on train-internal folds. "
            "No test-set tuning."
        ),
    },
    "xgboost_regressor": {
        "n_estimators":     {"distribution": "int_uniform", "low": 100, "high": 1000, "default": 400},
        "max_depth":        {"distribution": "int_uniform", "low": 3,   "high": 10,   "default": 6},
        "learning_rate":    {"distribution": "log_uniform", "low": 0.01, "high": 0.2,  "default": 0.05},
        "subsample":        {"distribution": "uniform",     "low": 0.6,  "high": 1.0,  "default": 0.9},
        "colsample_bytree": {"distribution": "uniform",     "low": 0.6,  "high": 1.0,  "default": 0.9},
        "reg_lambda":       {"distribution": "log_uniform", "low": 1e-3, "high": 10.0, "default": 1.0},
        "tree_method":      {"choices": ["hist"], "default": "hist"},
        "monotone_constraints": {
            "policy": "per-target, locked at OSF posting (see cgem_ext.surrogate.targets.TARGETS)",
            "default": "per-target tuple from TargetSpec.monotonicity",
        },
        "random_state":     42,
    },
    "xgboost_classifier": {
        "n_estimators":     {"distribution": "int_uniform", "low": 100, "high": 1000, "default": 400},
        "max_depth":        {"distribution": "int_uniform", "low": 3,   "high": 10,   "default": 5},
        "learning_rate":    {"distribution": "log_uniform", "low": 0.01, "high": 0.2,  "default": 0.05},
        "subsample":        {"distribution": "uniform",     "low": 0.6,  "high": 1.0,  "default": 0.9},
        "colsample_bytree": {"distribution": "uniform",     "low": 0.6,  "high": 1.0,  "default": 0.9},
        "reg_lambda":       {"distribution": "log_uniform", "low": 1e-3, "high": 10.0, "default": 1.0},
        "tree_method":      {"choices": ["hist"], "default": "hist"},
        "eval_metric":      {"choices": ["logloss", "auc"], "default": "logloss"},
        "random_state":     42,
    },
    "cqr_quantile_regressor": {
        "_note": "Two XGBRegressor heads (low/high pinball loss). Same envelope as the "
                 "point regressor above; the head-specific alpha/quantile is locked at "
                 "{0.05, 0.95} for nominal 90 % conditional intervals before bracket "
                 "widening to nominal 95 % via conformal correction.",
        "alpha_low":  {"value": 0.025},
        "alpha_high": {"value": 0.975},
    },
    "random_forest_baseline": {
        "_note": "sklearn defaults — frozen as documented baseline. No tuning.",
        "n_estimators": 400,
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "random_state": 42,
    },
    "mahalanobis_ood": {
        "_note": "Robust covariance via MinCovDet (sklearn). No tunable hyperparameters.",
        "covariance_estimator": "MinCovDet(random_state=42)",
        "feature_space": "17-dimensional (9 numeric + 7 categorical + 1 ordinal, one-hot encoded)",
    },
    "isolation_forest_ood": {
        "_note": "sklearn defaults — frozen as documented baseline.",
        "n_estimators": 100,
        "contamination": "auto",
        "max_samples": "auto",
        "random_state": 42,
    },
    "conformal": {
        "alpha": 0.05,
        "min_per_stratum": {"regressor": 20, "classifier": 5},
        "strata": ["championship", "conceptual", "extreme_post_stall", "military_acm"],
    },
    "sensitivity": {
        "sobol": {"sampler": "saltelli", "N_base": 1024, "total_evals_per_target": 20480},
        "morris": {"sampler": "morris", "N_trajectories": 100, "num_levels": 4},
    },
}


def write_search_spaces():
    text = json.dumps(SEARCH_SPACES, indent=2)
    for path in (DOCS_DIR / "osf_search_spaces.json", SUP_DIR / "osf_search_spaces.json"):
        path.write_text(text)
        print(f"  written: {path}")


# ──────────────────────────────────────────────────────────────────────
# Split indices (frozen)
# ──────────────────────────────────────────────────────────────────────


def write_split_indices():
    df = pd.read_parquet(DATASET)
    df_ok = df[df["status"] == "ok"].reset_index(drop=True)
    split = stratified_split(df_ok, seed=42, drop_status_error=False)

    n = len(df_ok)
    assignment = np.empty(n, dtype="<U5")
    assignment[split.train_idx] = "train"
    assignment[split.val_idx] = "val"
    assignment[split.test_idx] = "test"

    out = pd.DataFrame({
        "row_index": np.arange(n, dtype=np.int64),
        "split": assignment,
        "maneuver_category": df_ok["maneuver_category"].to_numpy(),
        "maneuver": df_ok["maneuver"].to_numpy() if "maneuver" in df_ok.columns else "",
        "who_profile": df_ok["who_profile"].to_numpy() if "who_profile" in df_ok.columns else 0,
    })
    for path in (DOCS_DIR / "osf_split_indices.parquet", SUP_DIR / "osf_split_indices.parquet"):
        out.to_parquet(path, index=False)
        print(f"  written: {path}  (n_train={len(split.train_idx)}, n_val={len(split.val_idx)}, n_test={len(split.test_idx)})")


def main() -> int:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    write_search_spaces()
    write_split_indices()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
