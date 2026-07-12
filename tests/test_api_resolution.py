"""Tests for canonical maneuver resolution used by surrogate inference."""

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from cgem_ext.api.inference import build_inference_row, resolve_maneuver
from cgem_ext.api.schemas import (
    ManeuverDescriptors,
    PilotConfigRequest,
    PredictionRequest,
)
from cgem_ext.data.generate_dataset import _maneuver_summary


def test_named_maneuver_resolves_dataset_descriptors() -> None:
    resolved = resolve_maneuver(ManeuverDescriptors(maneuver="high_g_turn"))
    summary = _maneuver_summary("high_g_turn")

    assert resolved.category == summary["maneuver_category"]
    assert resolved.g_peak_abs == summary["g_peak_abs"]
    assert resolved.dgdt_max_g_per_s == summary["dgdt_max_g_per_s"]
    assert resolved.profile_duration_s == summary["profile_duration_s"]
    assert resolved.calibration_scope == "category"


def test_named_maneuver_rejects_descriptor_override() -> None:
    with pytest.raises(ValidationError):
        ManeuverDescriptors(
            maneuver="high_g_turn",
            g_peak_abs=7.0,
            dgdt_max_g_per_s=6.0,
            profile_duration_s=9.5,
        )


def test_inline_requires_all_descriptors() -> None:
    with pytest.raises(ValidationError):
        ManeuverDescriptors(g_peak_abs=7.0, dgdt_max_g_per_s=6.0)


def test_inline_uses_global_scope() -> None:
    resolved = resolve_maneuver(
        ManeuverDescriptors(
            g_peak_abs=7.0,
            dgdt_max_g_per_s=6.0,
            profile_duration_s=9.5,
        )
    )

    assert resolved.maneuver_id == "<inline>"
    assert resolved.category == "unregistered"
    assert resolved.calibration_scope == "global"


def test_invalid_countermeasure_label_is_rejected_at_schema_boundary() -> None:
    with pytest.raises(ValidationError):
        PilotConfigRequest.model_validate({"countermeasures_label": "unknown"})


def test_unknown_named_maneuver_returns_404() -> None:
    with pytest.raises(HTTPException) as exc_info:
        resolve_maneuver(ManeuverDescriptors(maneuver="not_registered"))
    assert exc_info.value.status_code == 404


def test_inference_row_uses_resolved_named_category() -> None:
    row, resolved = build_inference_row(
        PredictionRequest(maneuver=ManeuverDescriptors(maneuver="high_g_turn"))
    )
    assert row.loc[0, "maneuver"] == resolved.maneuver_id
    assert row.loc[0, "maneuver_category"] == resolved.category
