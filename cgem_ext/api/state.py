"""Shared application state for the FastAPI service.

All trained models, the OOD detector + conformal abstainer, the
Mondrian conformal layers per target, and the precomputed Sobol
indices are loaded once at app startup so each ``/predict`` call has
deterministic latency (and so we don't pay 30 s of training on every
request).

The ``AppState`` dataclass is the single global handle; the FastAPI
``lifespan`` context (in ``main.py``) instantiates it on startup and
attaches it to the application so handlers can do
``request.app.state.cgem``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import cgem_ext  # noqa: F401  triggers sys.path injection
from cgem_ext.data.splits import stratified_split
from cgem_ext.ood import ConformalAbstention, MahalanobisOOD
from cgem_ext.surrogate import (
    MondrianSplitConformal,
    TARGETS,
    TargetSpec,
    TwoStageXGBSurrogate,
    XGBSurrogate,
    build_surrogate,
)


# ── Resolved paths ───────────────────────────────────────────────────


def _repo_root() -> Path:
    return Path(cgem_ext.__file__).resolve().parent.parent


def _resolve_dataset(repo_root: Path) -> Path:
    path = repo_root / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    if not path.is_file():
        raise FileNotFoundError(
            f"Canonical dataset not found at {path}. Run "
            f"`python -m cgem_ext.data.generate_dataset` first."
        )
    return path


def _resolve_sensitivity_csv(repo_root: Path) -> Optional[Path]:
    path = repo_root / "data" / "results" / "sensitivity" / "sobol_first_total.csv"
    return path if path.is_file() else None


# ── App-state container ──────────────────────────────────────────────


@dataclass
class AppState:
    package_version: str
    dataset_path: Path
    cgem_binary_sha256: str
    master_seed: int
    surrogates: dict[str, XGBSurrogate | TwoStageXGBSurrogate] = field(default_factory=dict)
    conformals: dict[str, MondrianSplitConformal] = field(default_factory=dict)
    ood_detector: Optional[MahalanobisOOD] = None
    ood_abstainer: Optional[ConformalAbstention] = None
    sensitivity_df: Optional[pd.DataFrame] = None
    sensitivity_manifest: Optional[dict] = None

    # ── Building ────────────────────────────────────────────────────

    @classmethod
    def build(cls) -> "AppState":
        """Train all models from the canonical dataset.

        Wall-clock at startup: ~30 s for the full 5-target surrogate
        suite + OOD + conformal layers on `cgem_synthetic_v1`. This is
        a one-time cost paid at server boot; each request afterwards is
        sub-millisecond per row.
        """
        repo_root = _repo_root()
        dataset_path = _resolve_dataset(repo_root)
        df = pd.read_parquet(dataset_path)

        # Sidecar metadata gives us the binary SHA + master seed for
        # the /version endpoint.
        meta_path = dataset_path.with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}

        sp = stratified_split(df, seed=meta.get("master_seed", 42))
        train_df, val_df, _test_df = sp.apply(df)

        state = cls(
            package_version=getattr(cgem_ext, "__version__", "unknown"),
            dataset_path=dataset_path,
            cgem_binary_sha256=str(meta.get("binary_sha256", "")),
            master_seed=int(meta.get("master_seed", 42)),
        )

        # 1. OOD detector + conformal abstainer
        ood = MahalanobisOOD().fit(train_df)
        abstainer = ConformalAbstention(alpha=0.05).calibrate(ood.score(val_df))
        state.ood_detector = ood
        state.ood_abstainer = abstainer

        # 2. Surrogates + Mondrian conformal layers, per target
        for spec in TARGETS:
            model = build_surrogate(spec.name).fit(train_df)
            state.surrogates[spec.name] = model
            cp = state._fit_conformal(model, spec, val_df)
            if cp is not None:
                state.conformals[spec.name] = cp

        # 3. Sensitivity CSV (loaded if present)
        sens_path = _resolve_sensitivity_csv(repo_root)
        if sens_path is not None:
            state.sensitivity_df = pd.read_csv(sens_path)
            manifest_path = sens_path.parent / "manifest.json"
            if manifest_path.is_file():
                state.sensitivity_manifest = json.loads(manifest_path.read_text())

        return state

    # ── Per-target conformal calibration ────────────────────────────

    @staticmethod
    def _fit_conformal(
        model: XGBSurrogate | TwoStageXGBSurrogate,
        spec: TargetSpec,
        val_df: pd.DataFrame,
    ) -> Optional[MondrianSplitConformal]:
        if spec.censored:
            event_col = spec.event_column
            assert event_col is not None  # spec.censored implies event_column
            mask = val_df[event_col].astype(int).to_numpy() == 1
            if mask.sum() < 30:
                return None
            cal = val_df.loc[mask]
            preds = model.predict(cal)  # E[time | event=1]
            targets = cal[spec.name]
        else:
            cal = val_df
            preds = model.predict(cal)
            targets = cal[spec.name]
        return MondrianSplitConformal(alpha=0.05).fit(
            cal_predictions=preds,
            cal_targets=targets,
            cal_strata=cal["maneuver_category"],
            min_per_stratum=10,
        )


__all__ = ["AppState"]
