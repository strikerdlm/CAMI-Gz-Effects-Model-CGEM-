"""Build SHAP TreeExplainer importance data for each surrogate target.

Outputs:
  data/results/supplementary/shap_importance.json
  manuscripts/ijnmbe/rendered/supplementary/shap_importance.json

The committed JSON gives, for every (target, feature) pair, the
mean(|SHAP|) over the held-out test split — the canonical feature
importance summary. Source code is `cgem_ext.surrogate.xgb` + the
`shap` package (TreeExplainer is the analytical exact path for tree
ensembles).

The actual SHAP plots are generated downstream from this JSON via the
ECharts pipeline (`scripts/build_figure_options.py`) so the
supplementary artifact stays small and language-agnostic.

Usage:
    cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
    /root/.venvs/cgem-ci/bin/python scripts/build_shap_supplementary.py
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
from cgem_ext.surrogate.features import extract_features  # noqa: E402
from cgem_ext.surrogate.targets import TARGETS  # noqa: E402
from cgem_ext.surrogate.xgb import (  # noqa: E402
    TwoStageXGBSurrogate,
    XGBSurrogate,
)

DATASET = REPO / "data" / "datasets" / "cgem_synthetic_v1.parquet"
OUT_DIR_DATA = REPO / "data" / "results" / "supplementary"
OUT_DIR_SUP = REPO / "manuscripts" / "ijnmbe" / "rendered" / "supplementary"


def compute_shap_for_target(spec, train_df, test_df) -> dict:
    import shap  # local import keeps the rest of the pipeline working if shap is missing

    if spec.censored:
        model = TwoStageXGBSurrogate(spec.name).fit(train_df)
        # Stage-2 regressor SHAP on event-positive test rows is the
        # informative slice; classifier SHAP is similar for tree models.
        event_col = spec.event_column
        assert event_col is not None
        mask = test_df[event_col].astype(int).to_numpy() == 1
        test_event = test_df[mask].reset_index(drop=True)
        feats = extract_features(test_event)
        explainer = shap.TreeExplainer(model._regressor)
        shap_values = explainer.shap_values(feats.to_numpy(dtype=float))
        mean_abs = np.abs(shap_values).mean(axis=0).astype(float).tolist()
        return {
            "target": spec.name,
            "censored": True,
            "stage": "regressor (event=1)",
            "n_test": int(len(test_event)),
            "feature_columns": list(feats.columns),
            "mean_abs_shap": mean_abs,
        }
    else:
        model = XGBSurrogate(spec.name).fit(train_df)
        feats = extract_features(test_df)
        explainer = shap.TreeExplainer(model._regressor)
        shap_values = explainer.shap_values(feats.to_numpy(dtype=float))
        mean_abs = np.abs(shap_values).mean(axis=0).astype(float).tolist()
        return {
            "target": spec.name,
            "censored": False,
            "stage": "regressor",
            "n_test": int(len(test_df)),
            "feature_columns": list(feats.columns),
            "mean_abs_shap": mean_abs,
        }


def main() -> int:
    OUT_DIR_DATA.mkdir(parents=True, exist_ok=True)
    OUT_DIR_SUP.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATASET)
    df_ok = df[df["status"] == "ok"].reset_index(drop=True)
    split = stratified_split(df_ok, seed=42, drop_status_error=False)
    train_df, _val_df, test_df = split.apply(df_ok)

    rows = []
    for spec in TARGETS:
        print(f"  SHAP TreeExplainer on {spec.name} …", flush=True)
        try:
            rows.append(compute_shap_for_target(spec, train_df, test_df))
        except ModuleNotFoundError as exc:
            print(f"  WARNING: {exc}; skipping SHAP for {spec.name}")
            return 1

    payload = {
        "_meta": {
            "produced_by": "scripts/build_shap_supplementary.py",
            "dataset": str(DATASET.relative_to(REPO)),
            "split": "stratified_split(seed=42, drop_status_error=True)",
            "tool": "shap.TreeExplainer (exact for tree ensembles)",
            "feature_space": "17-dim (extract_features)",
        },
        "rows": rows,
    }
    text = json.dumps(payload, indent=2)
    for path in (OUT_DIR_DATA / "shap_importance.json", OUT_DIR_SUP / "shap_importance.json"):
        path.write_text(text)
        print(f"  written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
