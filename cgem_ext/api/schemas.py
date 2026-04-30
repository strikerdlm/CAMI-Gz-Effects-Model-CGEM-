"""Pydantic v2 models for the FastAPI service.

These schemas are the wire contract between the React/TS frontend
and the Python service. Two design constraints carry across every
schema:

1. ``CGEMRunResponse`` must reproduce the v2.2.0 ``CGEMRun`` JSON
   shape used by ``pulse-sim/integrations/cgem_bridge.load_cgem_json``
   verbatim. The bridge reads keys ``maneuver``, ``pilot_profile``,
   ``duration_s``, ``time_to_*_s``, and ``data`` (with the per-time-
   series columns). ``tests/test_api.py`` enforces this in CI.

2. Every prediction response carries the OOD flag *and* a conformal
   prediction interval *and* a model-version stamp so the frontend
   can render the trio (point estimate, calibrated interval, OOD
   warning) consistently — matching the operational pattern documented
   in the OOD and emulator model cards.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ──────────────────────────────────────────────────────────────────────
# Liveness / version
# ──────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    detail: Optional[str] = None


class VersionResponse(BaseModel):
    package_version: str
    cgem_binary_sha256: str
    dataset_name: str
    dataset_master_seed: int
    targets: list[str]


# ──────────────────────────────────────────────────────────────────────
# Pilot config (input shared by /predict and /run-cgem)
# ──────────────────────────────────────────────────────────────────────


class PilotConfigRequest(BaseModel):
    """Pilot-side inputs. Mirrors `cgem_wrapper.PilotConfig`'s
    operational subset (i.e. the fields the surrogate consumes plus
    the few extras the Fortran model honours when ``who_profile`` is
    set)."""

    who_profile: Optional[int] = Field(
        default=2,
        ge=1,
        le=6,
        description="FAA standard subject 1..6, or None for a custom subject "
                    "(custom-arm path that exercises g_tolerance_multiplier "
                    "and dehydration_level).",
    )
    g_tolerance_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)
    dehydration_level: float = Field(default=0.0, ge=0.0, le=1.0)
    countermeasures_label: str = Field(
        default="none",
        description='one of "none", "agsm", "suit_agsm"',
    )
    gsuit_max_psi: float = Field(default=0.0, ge=0.0, le=20.0)
    gsuit_coverage_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    agsm_effectiveness: float = Field(default=0.0, ge=0.0, le=1.0)
    pbg_max_mmhg: float = Field(default=0.0, ge=0.0, le=60.0)


class ManeuverDescriptors(BaseModel):
    """Maneuver-summary features the surrogate consumes directly.

    Provided either by the caller (already known) or implicitly by
    naming an existing maneuver and letting the service compute them
    from the registered profile.
    """

    maneuver: Optional[str] = Field(
        default=None,
        description="Identifier from `aerobatic_profiles.PROFILES`. If "
                    "present, the service computes g_peak_abs / "
                    "dgdt_max_g_per_s / profile_duration_s itself.",
    )
    g_peak_abs: Optional[float] = Field(default=None, ge=0.0, le=15.0)
    dgdt_max_g_per_s: Optional[float] = Field(default=None, ge=0.0, le=60.0)
    profile_duration_s: Optional[float] = Field(default=None, ge=0.0, le=120.0)


# ──────────────────────────────────────────────────────────────────────
# /predict
# ──────────────────────────────────────────────────────────────────────


class PredictionRequest(BaseModel):
    """Single-row prediction request — surrogate path (fast)."""

    maneuver: ManeuverDescriptors
    pilot: PilotConfigRequest = PilotConfigRequest()


class TargetPrediction(BaseModel):
    """Per-target output.

    For continuous targets:
        point         — direct surrogate prediction
        lo, hi        — Mondrian conformal interval (95%) on `point`
    For censored time targets:
        point         — E[time | event=1] (regressor stage)
        lo, hi        — conformal interval on E[time | event=1]
        event_probability — P(event=1) from the classifier stage
        expected_time_s   — P(event) × E[time | event=1] (convenience)

    The point + lo/hi pair is therefore *always* on the same scale,
    which simplifies the frontend rendering. Frontends that want the
    expected-time scalar use `expected_time_s`; frontends that want
    to display a probability badge alongside the conditional time use
    `event_probability`.
    """

    target: str
    censored: bool
    point: float = Field(
        description=(
            "Point estimate. Continuous: direct surrogate output. "
            "Censored: E[time | event=1]."
        )
    )
    lo: Optional[float] = Field(default=None, description="Conformal lower bound on `point`.")
    hi: Optional[float] = Field(default=None, description="Conformal upper bound on `point`.")
    event_probability: Optional[float] = Field(
        default=None,
        description="P(event=1) for censored time targets.",
        ge=0.0,
        le=1.0,
    )
    expected_time_s: Optional[float] = Field(
        default=None,
        description="Convenience: P(event) * point for censored time targets.",
    )


class PredictionResponse(BaseModel):
    """Complete `/predict` response."""

    model_config = ConfigDict(extra="forbid")

    targets: list[TargetPrediction]
    ood: bool
    ood_score: float
    in_envelope: bool
    model_version: str
    cgem_binary_sha256: str
    source: str = Field(default="surrogate", description='"surrogate" or "fortran".')


# ──────────────────────────────────────────────────────────────────────
# /sweep
# ──────────────────────────────────────────────────────────────────────


class SweepRequest(BaseModel):
    """Batched sweep — same surrogate path applied to N inputs."""

    inputs: list[PredictionRequest] = Field(min_length=1, max_length=10_000)


class SweepResponse(BaseModel):
    results: list[PredictionResponse]


# ──────────────────────────────────────────────────────────────────────
# /run-cgem — must mirror pulse-sim CGEMRun JSON
# ──────────────────────────────────────────────────────────────────────


class RunCGEMRequest(BaseModel):
    """Authoritative path: invoke the Fortran subprocess directly."""

    maneuver: str = Field(description="Identifier from aerobatic_profiles.PROFILES.")
    pilot: PilotConfigRequest = PilotConfigRequest()


class CGEMRunData(BaseModel):
    """Time-series payload — the per-column lists pulse-sim's bridge
    consumes verbatim. Field aliases preserve the original column
    names with units in parentheses (e.g. ``Time(s)``)."""

    model_config = ConfigDict(populate_by_name=True)

    Time_s: list[float] = Field(alias="Time(s)")
    G: list[float]
    G_eff: list[float]
    HLAP_mmHg: list[float] = Field(alias="HLAP(mmHg)")
    F_con_dl_per_min: list[float] = Field(alias="F_con(dl/min)")
    F_vis_dl_per_min: list[float] = Field(alias="F_vis(dl/min)")
    F_bo_dl_per_min: list[float] = Field(alias="F_bo(dl/min)")
    c_bank_s: list[float] = Field(alias="c_bank(s)")
    bo_bank_s: list[float] = Field(alias="bo_bank(s)")
    Conscious: list[int]
    Greyout: list[int]
    Blackout: list[int]


class CGEMRunResponse(BaseModel):
    """Mirrors the v2.2.0 `CGEMRun.to_json()` shape used by pulse-sim's
    `cgem_bridge.load_cgem_json`. Any change here breaks the contract;
    `tests/test_api.py::test_run_cgem_matches_pulse_sim_schema`
    enforces this."""

    model_config = ConfigDict(populate_by_name=True)

    maneuver: str
    pilot_profile: str
    duration_s: float
    time_to_greyout_s: Optional[float]
    time_to_blackout_s: Optional[float]
    time_to_gloc_s: Optional[float]
    data: CGEMRunData


# ──────────────────────────────────────────────────────────────────────
# /sensitivity/{target}
# ──────────────────────────────────────────────────────────────────────


class SobolFeatureIndex(BaseModel):
    feature: str
    S1: float
    S1_conf: float
    ST: float
    ST_conf: float


class SensitivityResponse(BaseModel):
    """Sobol indices for one target, loaded from the committed CSV."""

    target: str
    censored: bool
    fixed_who_profile: str
    sobol_n_base: int
    indices: list[SobolFeatureIndex]


__all__ = [
    "CGEMRunData",
    "CGEMRunResponse",
    "HealthResponse",
    "ManeuverDescriptors",
    "PilotConfigRequest",
    "PredictionRequest",
    "PredictionResponse",
    "RunCGEMRequest",
    "SensitivityResponse",
    "SobolFeatureIndex",
    "SweepRequest",
    "SweepResponse",
    "TargetPrediction",
    "VersionResponse",
]
