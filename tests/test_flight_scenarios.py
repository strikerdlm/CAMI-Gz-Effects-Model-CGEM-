"""Geometry, determinism, safety and numerical convergence of real trajectories."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

SCENARIOS = ["coordinated_turn", "loop", "aileron_roll", "immelmann", "split_s", "cuban_eight"]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_default_maneuver_completes_with_consistent_frames(scenario):
    from cgem_ext.flight.schemas import FlightRequest
    from cgem_ext.flight.simulator import simulate

    result = simulate(FlightRequest(scenario=scenario))
    assert result.status == "complete", result.events
    assert result.frames[0].t_s == 0
    assert result.frames[0].gz == pytest.approx(1.0)
    assert result.frames[-1].t_s == result.duration_s
    assert 5 < result.duration_s <= 120
    t = np.array([f.t_s for f in result.frames])
    np.testing.assert_allclose(np.diff(t), 0.01, atol=1e-10)
    for f in result.frames:
        assert np.linalg.norm(f.quaternion) == pytest.approx(1.0, abs=1e-9)
        assert f.ias_kts < 220
        assert abs(f.gz) <= 10
        assert 0 < f.altitude_ft <= 16000
        assert abs(f.controls.aileron_deg) <= 30.00001
        assert abs(f.controls.elevator_deg) <= 25.00001
    first, last = result.frames[0], result.frames[-1]
    if scenario in ("immelmann", "split_s"):
        assert 160 < last.heading_deg < 200
        assert (last.altitude_ft > first.altitude_ft) == (scenario == "immelmann")
    if scenario == "loop":
        assert max(f.altitude_ft for f in result.frames) > first.altitude_ft + 300
        assert abs(last.pitch_deg) < 15
    if scenario == "aileron_roll":
        inverted = [
            f for f in result.frames if Rotation.from_quat(f.quaternion).as_matrix()[2, 2] < -0.8
        ]
        assert inverted
        assert abs(last.roll_deg) < 5
    if scenario == "coordinated_turn":
        assert max(abs(f.roll_deg) for f in result.frames) > 50
        assert 200 < max(f.position_m[1] for f in result.frames) < 500
        assert 170 < last.heading_deg < 230
        assert abs(last.roll_deg) < 5


def test_deterministic_and_convergent_loop():
    from cgem_ext.flight.schemas import FlightRequest
    from cgem_ext.flight.simulator import simulate

    req = FlightRequest(scenario="loop")
    a, b, fine = simulate(req), simulate(req), simulate(req, dt=0.005)
    assert a.model_dump() == b.model_dump()
    assert fine.status == "complete"
    assert abs(a.duration_s - fine.duration_s) < 0.1
    np.testing.assert_allclose(a.frames[-1].position_m, fine.frames[-1].position_m, atol=8)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(entry_ias_kts=250),
        dict(altitude_ft=17000),
        dict(entry_ias_kts=60),
        dict(intensity_g=11),
    ],
)
def test_invalid_initial_conditions_rejected(kwargs):
    from cgem_ext.flight.schemas import FlightRequest
    from cgem_ext.flight.simulator import simulate

    with pytest.raises(ValueError):
        simulate(FlightRequest(scenario="loop", **kwargs))


def test_split_s_stops_at_ground_instead_of_closing_trajectory():
    from cgem_ext.flight.schemas import FlightRequest
    from cgem_ext.flight.simulator import simulate

    result = simulate(FlightRequest(scenario="split_s", altitude_ft=100))
    assert result.status == "stopped"
    assert result.events[-1].kind == "terrain"


def test_turn_intensity_controls_sustained_normal_load():
    from cgem_ext.flight.schemas import FlightRequest
    from cgem_ext.flight.simulator import simulate

    result = simulate(FlightRequest(scenario="coordinated_turn", intensity_g=4))
    banked = [f for f in result.frames if f.phase == "Coordinated turn" and f.t_s > 7]
    assert max(f.gz for f in banked) > 3.85
