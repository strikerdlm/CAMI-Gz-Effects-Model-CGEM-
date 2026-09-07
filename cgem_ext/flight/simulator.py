"""Deterministic guided maneuvers integrated from forces, not G-trace animation."""

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from scipy.spatial.transform import Rotation

from . import physics as p
from .schemas import (
    AircraftInfo,
    Controls,
    FlightEvent,
    FlightForces,
    FlightFrame,
    FlightRequest,
    FlightResponse,
    Phase,
    Physiology,
    Provenance,
)

DEFAULT_IAS = dict(
    coordinated_turn=140.0,
    loop=180.0,
    aileron_roll=120.0,
    immelmann=180.0,
    split_s=120.0,
    cuban_eight=180.0,
)
SOURCES = [
    "https://www.easa.europa.eu/en/downloads/7174/en",
    "https://www.manualslib.com/manual/1848391/Extra-300l.html",
    "https://data.ntsb.gov/Docket/Document/docBLOB?ID=16480049&FileExtension=pdf&FileName=Airplane+Information+Manual+Excerpts+Final+1-Rel.pdf",
]
ASSUMPTIONS = [
    "EASA A.362 Issue 09 (2026-08-05), Section C; source document SHA256 8c192c746413f4595f46339859a2243368b40c2b9810cf1b689b351126a66e18.",
    "NTSB-hosted manufacturer Information Manual excerpt; SHA256 7305f42a99460f29f452abb6e3bf5d549b12b7e6e79d7cdf4a59a752c5e8fad5. This manual is not kept current and is not an aircraft-specific approved POH.",
    "Above VA=158 KIAS the manual cautions against large or abrupt control inputs; the guided model uses bounded partial controls. VA is distinct from VNE=220 KIAS.",
    "Educational guided point mass; no flight-test calibration, post-stall dynamics or aircraft certification.",
    "NED world; forward/right/down body; xyzw quaternion maps body to NED; still-air ISA troposphere.",
    "IAS approximated by equivalent airspeed; instrument/position-error correction and compressibility are omitted.",
    "Mass is fixed at solo 820 kg or dual 870 kg; no fuel burn, CG shift, inertia or gyroscopic propeller model.",
    "Estimated: CL_alpha=5.2/rad, CD0=0.028, induced k=0.065, propeller efficiency=0.80; power density lapse exponent=0.85.",
    "CLmax derived separately from reported 55/57 KIAS idle, forward-CG stall anchors; symmetric negative lift assumed.",
    "Estimated guidance/control response: G lag 0.30 s / 2.5 G/s; roll lag 0.20 s / 160 deg/s²; roll cap 100 deg/s; throttle lag 0.4 s.",
    "Control deflections and RPM are bounded guidance proxies, not a measured linkage or engine governor model.",
    "Powered vertical maneuvers use full power climbing and reduce power descending; trajectories are not forced to close.",
    "CGEM uses signed body-normal Gz only; longitudinal/lateral specific force and vestibular effects are not modelled.",
    "CGEM native periodic rows are at integer seconds minus 0.001 s (written before integration); event rows are milliseconds after integration. No synthetic physiology at t=0.",
    "Physiology flags: 0 normal, 1 loss, 2 recovery. No surrogate confidence intervals apply to these generated trajectories.",
    "Standard WHO profiles ignore dehydration and tolerance-multiplier subject overrides; custom WHO=None uses wrapper conventions.",
    "CGEM axial onset validation ceiling is approximately 10 G/s; this aircraft model is a separate estimated envelope.",
]


@dataclass
class Segment:
    name: str
    mode: str
    target: float
    description: str


def segments(scenario: str) -> list[Segment]:
    def pull(name: str, deg: float) -> Segment:
        return Segment(
            name,
            "pull",
            math.radians(deg),
            "Positive normal lift curves the flight path; gravity and power exchange speed and altitude.",
        )

    def roll(name: str, deg: float) -> Segment:
        return Segment(
            name,
            "roll",
            math.radians(deg),
            "Bounded aileron guidance rolls about the velocity axis while the flight path responds to gravity and lift.",
        )

    entry = Segment(
        "Entry", "level", 2.0, "Establish the initial trimmed condition and observe IAS versus TAS."
    )
    recovery = Segment(
        "Recovery",
        "recover",
        5.0,
        "Roll wings level and recover the flight path with bounded normal load.",
    )
    plans = {
        "coordinated_turn": [
            Segment(
                "Coordinated turn",
                "turn",
                math.pi,
                "Bank tilts lift sideways; normal load must increase to support weight. Complete a half-circle.",
            )
        ],
        "loop": [pull("Loop", 360)],
        "aileron_roll": [
            Segment(
                "Pitch up",
                "pitch_up",
                math.radians(15),
                "A modest climb entry provides room for the altitude lost during the roll.",
            ),
            roll("Full roll", 360),
        ],
        "immelmann": [pull("Half loop", 180), roll("Half roll", 180)],
        "split_s": [roll("Inverting roll", 180), pull("Descending half loop", 180)],
        "cuban_eight": [
            pull("First five-eighths loop", 225),
            roll("First downline half roll", 180),
            pull("Second three-quarter loop", 270),
            roll("Second downline half roll", 180),
            pull("Final pullout", 45),
        ],
    }
    return [entry, *plans[scenario], recovery]


def frame(y: p.Vector, a: p.Aircraft, time: float, phase: str) -> FlightFrame:
    s = p.evaluate(y, a)
    quat = Rotation.from_matrix(s.body).as_quat()
    # Euler readouts only; never used for integration (including vertical flight).
    pitch = math.asin(float(np.clip(-s.body[2, 0], -1, 1)))
    heading = math.atan2(float(s.body[1, 0]), float(s.body[0, 0]))
    roll = math.atan2(float(s.body[2, 1]), float(s.body[2, 2]))
    tas = float(np.linalg.norm(y[3:6]))
    alpha_deg = math.degrees(s.alpha_rad)
    return FlightFrame(
        t_s=round(time, 6),
        position_m=y[:3].tolist(),
        velocity_mps=y[3:6].tolist(),
        quaternion=quat.tolist(),
        ias_kts=tas * math.sqrt(s.rho / p.RHO0) / p.KNOT,
        tas_kts=tas / p.KNOT,
        altitude_ft=-float(y[2]) / p.FT,
        vertical_speed_fpm=-float(y[5]) / p.FT * 60,
        heading_deg=math.degrees(heading) % 360,
        pitch_deg=math.degrees(pitch),
        roll_deg=math.degrees(roll),
        alpha_deg=alpha_deg,
        gz=s.gz,
        phase=phase,
        controls=Controls(
            aileron_deg=math.degrees(float(y[10])) / 100 * 30,
            elevator_deg=-s.cl / a.cl_max * 25,
            rudder_deg=0.0,
            throttle=float(y[11]),
            rpm=1000 + 1700 * float(y[11]),
        ),
        forces_n=FlightForces(lift=s.lift, drag=s.drag, thrust=s.thrust, weight=a.mass_kg * p.G),
    )


def validate(req: FlightRequest) -> tuple[p.Aircraft, float]:
    a = p.Aircraft(req.loading)
    ias = req.entry_ias_kts or DEFAULT_IAS[req.scenario]
    if req.intensity_g > a.g_limit:
        raise ValueError(f"{req.loading} loading has a ±{a.g_limit:g} G structural limit.")
    lo, hi = (80.0, 158.0) if req.scenario in ("aileron_roll", "split_s") else (100.0, 190.0)
    if req.scenario == "coordinated_turn":
        lo, hi = 80.0, 158.0
    if not lo <= ias <= hi:
        raise ValueError(
            f"Entry IAS for {req.scenario} must be {lo:g}–{hi:g} KIAS; this is an educational entry envelope."
        )
    return a, ias


def simulate(req: FlightRequest, dt: float = 0.01) -> FlightResponse:
    if dt not in (0.01, 0.005):
        raise ValueError(
            "Integration step must be 0.01 s (or 0.005 s for convergence verification)."
        )
    a, ias = validate(req)
    y = p.initial_state(a, ias, req.altitude_ft)
    plan = segments(req.scenario)
    frames: list[FlightFrame] = []
    phases: list[Phase] = []
    events: list[FlightEvent] = []
    index = 0
    started = 0.0
    progress = 0.0
    status: Literal["complete", "stopped"] = "stopped"
    heading_prev = 0.0
    previous_q = None
    for tick in range(round(120 / dt) + 1):
        t = tick * dt
        seg = plan[index]
        s = p.evaluate(y, a)
        f = frame(y, a, t, seg.name)
        # Choose a continuous quaternion hemisphere for smooth interpolation.
        if previous_q is not None and np.dot(previous_q, f.quaternion) < 0:
            f.quaternion = [-v for v in f.quaternion]
        previous_q = f.quaternion
        frames.append(f)
        event = None
        if not np.isfinite(y).all() or abs(s.alpha_rad) > math.radians(25):
            event = (
                "model_envelope",
                "Attitude/angle-of-attack exceeded the supported attached-flow model.",
            )
        elif abs(s.cl) > a.cl_max * 1.001:
            event = ("stall", "Required lift exceeded the POH-anchored attached-flow lift limit.")
        elif abs(s.gz) > a.g_limit + 0.001:
            event = ("structural_g", "Aircraft structural normal-load limit exceeded.")
        elif f.ias_kts >= 220:
            event = ("overspeed", "IAS reached the 220 KIAS never-exceed limit.")
        elif f.altitude_ft <= 0:
            event = ("terrain", "Flight reached the zero-elevation terrain plane.")
        elif f.altitude_ft > 16000:
            event = ("altitude", "Altitude exceeded the 16000 ft aircraft/model limit.")
        if event:
            events.append(FlightEvent(time_s=t, kind=event[0], message=event[1]))
            break
        elapsed = t - started
        done = elapsed >= seg.target if seg.mode in ("level", "recover") else progress >= seg.target
        # Recovery is only complete when wings and flight path actually settle.
        if seg.mode == "recover":
            done = elapsed >= seg.target and abs(float(s.forward[2])) < 0.07 and abs(f.roll_deg) < 4
        if done:
            phases.append(
                Phase(name=seg.name, start_s=started, end_s=t, description=seg.description)
            )
            index += 1
            if index == len(plan):
                status = "complete"
                break
            seg = plan[index]
            started = t
            progress = 0.0
        speed = float(np.linalg.norm(y[3:6]))
        # Relative bank computed without Euler pitch singularities.
        bank = math.atan2(float(s.right[2]), float(s.down[2]))
        gamma = math.asin(float(np.clip(-s.forward[2], -1, 1)))
        max_n = 0.86 * (f.ias_kts / p.stall_ias(a, 1)) ** 2
        throttle = 0.95 if s.forward[2] < 0.05 else 0.12
        roll_rate = 0.0
        if seg.mode in ("pull", "pitch_up"):
            n = 1 + (req.intensity_g - 1) * (0.5 + 0.5 * float(s.down[2]))
            if req.scenario == "split_s":
                n = req.intensity_g
            if seg.mode == "pitch_up":
                n = 2.0
            n = min(n, max_n)
        elif seg.mode == "roll":
            remaining = seg.target - progress
            roll_rate = min(math.radians(100), max(0.0, remaining) * 5)
            n = 0.15
            throttle = 0.5
            # The asymptotic controller needs a physical settling tolerance.
            if remaining < math.radians(0.3) and abs(y[10]) < math.radians(2):
                progress = seg.target
        else:
            desired_bank = math.acos(1 / req.intensity_g) if seg.mode == "turn" else 0.0
            roll_rate = float(
                np.clip((desired_bank - bank) * 3, -math.radians(70), math.radians(70))
            )
            n = (math.cos(gamma) - speed * gamma / (p.G * 1.5)) / max(0.25, math.cos(bank))
            n = float(np.clip(n, -min(1.5, max_n), min(req.intensity_g, max_n)))
            throttle = float(np.clip(0.55 + (ias - f.ias_kts) * 0.045, 0.1, 1.0))
        command = np.array([n, roll_rate, throttle])
        z = p.step(y, a, command, dt)
        if seg.mode in ("pull", "pitch_up"):
            # Signed path curvature about transported right; gravity is included.
            sn = p.evaluate(z, a)
            angle = math.atan2(
                float(np.dot(np.cross(s.forward, sn.forward), s.right)),
                float(np.dot(s.forward, sn.forward)),
            )
            progress += angle
        elif seg.mode == "roll":
            progress += float((y[10] + z[10]) * 0.5 * dt)
        elif seg.mode == "turn":
            heading_now = math.atan2(float(z[4]), float(z[3]))
            progress += (heading_now - heading_prev + math.pi) % (2 * math.pi) - math.pi
        heading_prev = math.atan2(float(z[4]), float(z[3]))
        y = z
    duration = frames[-1].t_s
    if status != "complete":
        phases.append(
            Phase(
                name=plan[index].name,
                start_s=started,
                end_s=duration,
                description=plan[index].description,
            )
        )
        if not events:
            events.append(
                FlightEvent(
                    time_s=duration,
                    kind="incomplete",
                    message="Guidance could not complete within the 120 s model duration limit.",
                )
            )
    implementation_sha = hashlib.sha256(
        Path(__file__).read_bytes() + Path(p.__file__).read_bytes()
    ).hexdigest()
    params = dict(
        implementation_sha256=implementation_sha,
        model="extra300l-point-mass-1.0",
        dt=dt,
        loading=req.loading,
        cl_max=a.cl_max,
        cl_alpha=p.CL_ALPHA,
        cd0=p.CD0,
        induced_k=p.INDUCED_K,
        prop_efficiency=p.PROP_EFFICIENCY,
        mass_kg=a.mass_kg,
        area_m2=a.area_m2,
        power_w=a.power_w,
        request=req.model_dump(),
    )
    parameter_sha = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
    trace = [[round(f.t_s * 1000), f.gz] for f in frames]
    trace_sha = hashlib.sha256(json.dumps(trace, separators=(",", ":")).encode()).hexdigest()
    return FlightResponse(
        scenario=req.scenario,
        duration_s=duration,
        status=status,
        frames=frames,
        phases=phases,
        events=events,
        aircraft=AircraftInfo(mass_kg=a.mass_kg, g_limit=a.g_limit),
        provenance=Provenance(
            model_version="extra300l-point-mass-1.0",
            flight_model="Guided force-integrated 3D point mass (estimated educational model)",
            source_urls=SOURCES,
            assumptions=ASSUMPTIONS,
            parameter_sha256=parameter_sha,
            trace_sha256=trace_sha,
        ),
        physiology=Physiology(status="unavailable", reason="CGEM has not been invoked."),
    )
