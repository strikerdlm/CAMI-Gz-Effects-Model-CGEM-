"""Reproduce numerical calibration evidence: python -m docs.extra300l.validate_model."""

import json
from pathlib import Path

import numpy as np

from cgem_ext.flight.adapter import run_trace
from cgem_ext.flight.physics import G
from cgem_ext.flight.schemas import FlightRequest
from cgem_ext.flight.simulator import DEFAULT_IAS, simulate


def main():
    evidence = []
    for scenario in DEFAULT_IAS:
        req = FlightRequest(scenario=scenario)
        result = simulate(req)
        frames = result.frames
        times = np.array([f.t_s for f in frames])
        speed = np.array([np.linalg.norm(f.velocity_mps) for f in frames])
        height = np.array([-f.position_m[2] for f in frames])
        mass = result.aircraft.mass_kg
        energy = 0.5 * mass * speed**2 + mass * G * height
        power = np.array(
            [
                (f.forces_n.thrust * np.cos(np.deg2rad(f.alpha_deg)) - f.forces_n.drag) * v
                for f, v in zip(frames, speed, strict=True)
            ]
        )
        work = np.sum(0.5 * (power[1:] + power[:-1]) * np.diff(times))
        residual = float(energy[-1] - energy[0] - work)
        phys = run_trace(times.tolist(), [f.gz for f in frames], req.pilot, scenario)
        evidence.append(
            dict(
                scenario=scenario,
                status=result.status,
                duration_s=result.duration_s,
                altitude_min_ft=min(f.altitude_ft for f in frames),
                altitude_max_ft=max(f.altitude_ft for f in frames),
                altitude_change_ft=frames[-1].altitude_ft - frames[0].altitude_ft,
                ias_min_kts=min(f.ias_kts for f in frames),
                ias_max_kts=max(f.ias_kts for f in frames),
                gz_min=min(f.gz for f in frames),
                gz_max=max(f.gz for f in frames),
                energy_balance_residual_j=residual,
                residual_relative_initial_kinetic=abs(residual) / (0.5 * mass * speed[0] ** 2),
                final_position_m=frames[-1].position_m,
                final_heading_deg=frames[-1].heading_deg,
                final_pitch_deg=frames[-1].pitch_deg,
                final_roll_deg=frames[-1].roll_deg,
                physiology_status=phys.status,
                physiology_reason=phys.reason,
                physiology_samples=len(phys.result.data.Time_s) if phys.result else 0,
                binary_sha256=phys.binary_sha256,
                parameter_sha256=result.provenance.parameter_sha256,
                trace_sha256=result.provenance.trace_sha256,
            )
        )
        print(
            scenario,
            result.status,
            round(result.duration_s, 2),
            phys.status,
            "energy error J",
            residual,
            flush=True,
        )
    Path("docs/extra300l/validation.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
