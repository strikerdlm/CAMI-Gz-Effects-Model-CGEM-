"""Multi-fidelity vs single-fidelity benchmark on the time_to_gloc_s
target.

Compares three predictors at a matched high-fidelity training budget:

1. **WF2013 low-fidelity alone** — analytical model from
   :mod:`cgem_ext.surrogate.lowfi`. Free predictions; serves as the
   floor.
2. **MultiFidelityNARGP** — Kennedy-O'Hagan / NARGP coupling
   (low_fidelity = WhinneryForsterGLOC, high_fidelity = the same
   subset of cgem_synthetic_v1 rows that the single-fidelity model
   trains on).
3. **XGBoost single-stage regressor** — :class:`XGBSurrogate` trained
   on the same high-fidelity subset. Apples-to-apples baseline.

Each predictor is scored on the OSF-pre-registered held-out test
split (event-positive rows of ``time_to_gloc_s``). The benchmark is
run at multiple high-fidelity budgets ``n_high ∈ {20, 50, 100, 300,
1000}`` to characterise the data-efficiency curve. Results are
written to ``data/results/h6/multifidelity_benchmark.json``.

The benchmark uses only the (g_peak_abs, dgdt_max_g_per_s) input
columns since both low-fidelity models accept that schema. The
single-fidelity XGBoost is given the same two-feature input for
fairness.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

from cgem_ext.data.splits import stratified_split
from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

BUDGETS: list[int] = [20, 50, 100, 300, 1000]
TARGET = "time_to_gloc_s"
EVENT_COL = "event_gloc"
RNG_SEED = 42


def _features_2d(df: pd.DataFrame) -> np.ndarray:
    return df[["g_peak_abs", "dgdt_max_g_per_s"]].to_numpy(dtype=float)


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    finite = ~np.isnan(y_pred) & ~np.isinf(y_pred) & ~np.isnan(y_true)
    if not finite.any():
        return float("nan")
    return float(np.sqrt(mean_squared_error(y_true[finite], y_pred[finite])))


def _coverage(y_true: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> float:
    finite = (
        ~np.isnan(lo) & ~np.isinf(lo)
        & ~np.isnan(hi) & ~np.isinf(hi)
        & ~np.isnan(y_true)
    )
    if not finite.any():
        return float("nan")
    inside = (y_true[finite] >= lo[finite]) & (y_true[finite] <= hi[finite])
    return float(inside.mean())


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    syn_path = repo / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    out_dir = repo / "data" / "results" / "h6"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "multifidelity_benchmark.json"

    if not syn_path.exists():
        raise SystemExit(f"missing synthetic parquet at {syn_path}")

    syn = pd.read_parquet(syn_path)
    if "status" in syn.columns:
        syn = syn[syn["status"] == "ok"].reset_index(drop=True)
    split = stratified_split(syn, seed=RNG_SEED)
    train_df = syn.iloc[split.train_idx].copy()
    test_df = syn.iloc[split.test_idx].copy()

    # Restrict to event-positive rows (the only ones with a valid
    # time_to_gloc_s ground truth).
    train_event = train_df[train_df[EVENT_COL] == 1].copy()
    test_event = test_df[test_df[EVENT_COL] == 1].copy()
    print(
        f"[MF-bench] train (event=1): n={len(train_event)}; "
        f"test (event=1): n={len(test_event)}"
    )

    rng = np.random.default_rng(RNG_SEED)
    train_event_ordered = train_event.sample(
        frac=1.0, random_state=RNG_SEED
    ).reset_index(drop=True)
    test_X = _features_2d(test_event)
    test_y = test_event[TARGET].astype(float).to_numpy()

    wf = WhinneryForsterGLOC()
    pred_lowfi = wf.predict_array(test_X)
    rmse_lowfi = _rmse(test_y, pred_lowfi)

    rows: list[dict] = []
    for n_high in BUDGETS:
        if n_high > len(train_event_ordered):
            continue
        sub = train_event_ordered.iloc[:n_high]
        sub_X = _features_2d(sub)
        sub_y = sub[TARGET].astype(float).to_numpy()

        # Multi-fidelity NARGP
        mf = MultiFidelityNARGP(low_fidelity=wf, random_state=RNG_SEED).fit(
            sub_X, sub_y
        )
        mf_mean, mf_std = mf.predict(test_X, return_std=True)
        mf_lo, mf_hi = mf.predict_interval(test_X, alpha=0.05)
        rmse_mf = _rmse(test_y, mf_mean)
        cov_mf = _coverage(test_y, mf_lo, mf_hi)

        # XGBoost single-stage baseline (2-feature variant)
        xgb = XGBRegressor(
            n_estimators=400,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=RNG_SEED,
            n_jobs=-1,
            tree_method="hist",
            verbosity=0,
        ).fit(sub_X, sub_y)
        pred_xgb = xgb.predict(test_X)
        rmse_xgb = _rmse(test_y, np.asarray(pred_xgb, dtype=float))

        rows.append(
            {
                "n_high_fidelity": n_high,
                "rmse_low_fidelity_only": rmse_lowfi,
                "rmse_multifidelity_nargp": rmse_mf,
                "rmse_xgb_single_fidelity": rmse_xgb,
                "coverage_multifidelity_nargp_alpha05": cov_mf,
            }
        )
        print(
            f"[MF-bench] n_high={n_high:>4}: "
            f"RMSE WF2013 alone={rmse_lowfi:.3f}; "
            f"MF-NARGP={rmse_mf:.3f} (cov {cov_mf:.3f}); "
            f"XGB-2D={rmse_xgb:.3f}"
        )

    summary = {
        "_meta": {
            "produced_by": "scripts/run_multifidelity_benchmark.py",
            "synthetic_dataset": str(syn_path.relative_to(repo)),
            "split_seed": RNG_SEED,
            "target": TARGET,
            "event_column": EVENT_COL,
            "n_test_event_positive": int(len(test_event)),
            "low_fidelity_model": (
                "cgem_ext.surrogate.lowfi.WhinneryForsterGLOC"
            ),
            "high_fidelity_subset_strategy": (
                "first n_high rows of train_event after seed-42 shuffle"
            ),
        },
        "rows": rows,
    }
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"[MF-bench] wrote {out_path}")


if __name__ == "__main__":
    main()
