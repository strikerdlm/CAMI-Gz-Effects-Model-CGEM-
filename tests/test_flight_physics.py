"""Independent physical identities for the guided point-mass model."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation


def test_specific_force_is_body_normal_not_world_vertical():
    from cgem_ext.flight.physics import specific_gz

    q = [0.0, 0.0, 0.0, 1.0]
    assert specific_gz(np.zeros(3), q) == pytest.approx(1.0)
    inverted = Rotation.from_euler("x", 180, degrees=True).as_quat()
    assert specific_gz(np.zeros(3), inverted) == pytest.approx(-1.0)
    assert specific_gz(np.array([0.0, 0.0, 9.80665]), q) == pytest.approx(0.0)


def test_density_and_stall_calibration():
    from cgem_ext.flight.physics import Aircraft, density, stall_ias

    a = Aircraft("solo")
    assert density(0) == pytest.approx(1.225, rel=0.001)
    assert density(1828.8) == pytest.approx(1.024, rel=0.003)
    assert stall_ias(a, 1) == pytest.approx(55, abs=0.01)
    assert stall_ias(a, 2**0.5) == pytest.approx(65.4, abs=0.5)
    assert stall_ias(Aircraft("dual"), 1) == pytest.approx(57, abs=0.1)


def test_force_energy_and_orientation():
    from cgem_ext.flight.physics import Aircraft, evaluate, initial_state

    a = Aircraft("solo")
    state = initial_state(a, 140, 6000)
    sample = evaluate(state, a)
    # Flight path is horizontal while fuselage has positive incidence.
    assert sample.gz == pytest.approx(1.0, abs=1e-9)
    assert sample.alpha_rad > 0
    assert np.linalg.det(sample.body) == pytest.approx(1.0)
    assert np.dot(sample.acceleration, state[3:6]) == pytest.approx(
        (sample.thrust * np.cos(sample.alpha_rad) - sample.drag)
        * np.linalg.norm(state[3:6])
        / a.mass_kg,
        abs=1e-8,
    )
