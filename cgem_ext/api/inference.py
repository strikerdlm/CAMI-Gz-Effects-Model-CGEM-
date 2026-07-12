"""Canonical maneuver resolution for surrogate inference."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import HTTPException

from cgem_ext.api.schemas import ManeuverDescriptors, PredictionRequest
from cgem_ext.data.generate_dataset import _maneuver_summary


@dataclass(frozen=True)
class ResolvedManeuver:
    maneuver_id: str
    category: str
    g_peak_abs: float
    dgdt_max_g_per_s: float
    profile_duration_s: float
    calibration_scope: Literal["category", "global"]


def _checked(resolved: ResolvedManeuver) -> ResolvedManeuver:
    values = (
        resolved.g_peak_abs,
        resolved.dgdt_max_g_per_s,
        resolved.profile_duration_s,
    )
    if not np.isfinite(values).all():
        raise HTTPException(status_code=422, detail="maneuver descriptors must be finite")
    return resolved


def resolve_maneuver(md: ManeuverDescriptors) -> ResolvedManeuver:
    if md.maneuver is not None:
        try:
            summary = _maneuver_summary(md.maneuver)
        except (KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=404, detail=f"unknown maneuver {md.maneuver!r}"
            ) from exc
        return _checked(
            ResolvedManeuver(
                maneuver_id=md.maneuver,
                category=str(summary["maneuver_category"]),
                g_peak_abs=float(summary["g_peak_abs"]),
                dgdt_max_g_per_s=float(summary["dgdt_max_g_per_s"]),
                profile_duration_s=float(summary["profile_duration_s"]),
                calibration_scope="category",
            )
        )

    # ManeuverDescriptors validates completeness before this function is called.
    return _checked(
        ResolvedManeuver(
            maneuver_id="<inline>",
            category="unregistered",
            g_peak_abs=float(md.g_peak_abs),  # type: ignore[arg-type]
            dgdt_max_g_per_s=float(md.dgdt_max_g_per_s),  # type: ignore[arg-type]
            profile_duration_s=float(md.profile_duration_s),  # type: ignore[arg-type]
            calibration_scope="global",
        )
    )


def build_inference_row(
    req: PredictionRequest,
) -> tuple[pd.DataFrame, ResolvedManeuver]:
    resolved = resolve_maneuver(req.maneuver)
    pilot = req.pilot
    row = {
        "maneuver": resolved.maneuver_id,
        "maneuver_category": resolved.category,
        "arm": "custom" if pilot.who_profile is None else "standard",
        "who_profile": pilot.who_profile,
        "g_tolerance_multiplier": pilot.g_tolerance_multiplier,
        "dehydration_label": "none" if pilot.dehydration_level == 0 else "varied",
        "dehydration_level": pilot.dehydration_level,
        "countermeasures_label": pilot.countermeasures_label,
        "gsuit_max_psi": pilot.gsuit_max_psi,
        "gsuit_coverage_fraction": pilot.gsuit_coverage_fraction,
        "agsm_effectiveness": pilot.agsm_effectiveness,
        "pbg_max_mmhg": pilot.pbg_max_mmhg,
        "g_peak_abs": resolved.g_peak_abs,
        "dgdt_max_g_per_s": resolved.dgdt_max_g_per_s,
        "profile_duration_s": resolved.profile_duration_s,
    }
    return pd.DataFrame([row]), resolved


__all__ = ["ResolvedManeuver", "build_inference_row", "resolve_maneuver"]
