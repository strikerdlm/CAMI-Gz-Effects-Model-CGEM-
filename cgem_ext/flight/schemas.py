"""Additive flight API. Existing CGEM schemas remain untouched."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from cgem_ext.api.schemas import CGEMRunResponse, PilotConfigRequest

Scenario = Literal[
    "coordinated_turn", "loop", "aileron_roll", "immelmann", "split_s", "cuban_eight"
]


class FlightRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")
    scenario: Scenario
    entry_ias_kts: float | None = Field(default=None, gt=0, le=220)
    altitude_ft: float = Field(default=6000, gt=0, le=16000)
    loading: Literal["solo", "dual"] = "solo"
    intensity_g: float = Field(default=4, ge=2, le=10)
    pilot: PilotConfigRequest = Field(default_factory=PilotConfigRequest)


class Controls(BaseModel):
    aileron_deg: float
    elevator_deg: float
    rudder_deg: float
    throttle: float
    rpm: float


class FlightForces(BaseModel):
    lift: float
    drag: float
    thrust: float
    weight: float


class FlightFrame(BaseModel):
    t_s: float
    position_m: list[float]
    velocity_mps: list[float]
    quaternion: list[float]
    ias_kts: float
    tas_kts: float
    altitude_ft: float
    vertical_speed_fpm: float
    heading_deg: float
    pitch_deg: float
    roll_deg: float
    alpha_deg: float
    gz: float
    phase: str
    controls: Controls
    forces_n: FlightForces


class Phase(BaseModel):
    name: str
    start_s: float
    end_s: float
    description: str


class FlightEvent(BaseModel):
    time_s: float
    kind: str
    message: str


class AircraftInfo(BaseModel):
    name: str = "Extra 300L"
    mass_kg: float
    g_limit: float
    vne_kias: float = 220
    va_kias: float = 158


class Provenance(BaseModel):
    model_version: str
    flight_model: str
    source_urls: list[str]
    assumptions: list[str]
    parameter_sha256: str
    trace_sha256: str


class Physiology(BaseModel):
    status: Literal["available", "unavailable"]
    reason: str | None = None
    binary_sha256: str | None = None
    result: CGEMRunResponse | None = None


class FlightResponse(BaseModel):
    scenario: Scenario
    duration_s: float
    status: Literal["complete", "stopped"]
    frames: list[FlightFrame]
    phases: list[Phase]
    events: list[FlightEvent]
    aircraft: AircraftInfo
    provenance: Provenance
    physiology: Physiology
