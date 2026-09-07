"""Force-integrated educational point mass; no measured handling qualities implied.

State: NED position, NED velocity, transported wind-right unit vector,
body-normal G command after response lag, roll rate, throttle. Gravity acts
in NED down. Lift is perpendicular to velocity; thrust follows body forward.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

Vector = NDArray[np.float64]
G = 9.80665
KNOT = 1852 / 3600
FT = 0.3048
RHO0 = 1.225
GRAVITY = np.array([0.0, 0.0, G])
# Estimated, not measured: symmetric linear lift and parabolic drag polar.
CL_ALPHA = 5.2
CD0 = 0.028
INDUCED_K = 0.065
PROP_EFFICIENCY = 0.80


@dataclass(frozen=True)
class Aircraft:
    loading: str = "solo"
    area_m2: float = 10.84
    power_w: float = 224000.0

    @property
    def mass_kg(self) -> float:
        return 820.0 if self.loading == "solo" else 870.0

    @property
    def g_limit(self) -> float:
        return 10.0 if self.loading == "solo" else 8.0

    @property
    def cl_max(self) -> float:
        # Each loading uses its reported idle forward-CG stall IAS anchor.
        vs = (55.0 if self.loading == "solo" else 57.0) * KNOT
        return 2 * self.mass_kg * G / (RHO0 * vs**2 * self.area_m2)


def density(altitude_m: float) -> float:
    """ISA troposphere density; applicable here below 16000 ft."""
    return float(RHO0 * (1 - 0.0065 * altitude_m / 288.15) ** 4.25588)


def stall_ias(aircraft: Aircraft, load: float) -> float:
    return float(
        np.sqrt(2 * aircraft.mass_kg * G * abs(load) / (RHO0 * aircraft.area_m2 * aircraft.cl_max))
        / KNOT
    )


def specific_gz(acceleration_ned: Vector, quaternion: Vector | list[float]) -> float:
    """Accelerometer sign: support upright +1, inverted -1, free fall zero."""
    down = Rotation.from_quat(quaternion).as_matrix()[:, 2]
    return float(-np.dot(acceleration_ned - GRAVITY, down) / G)


def initial_state(aircraft: Aircraft, ias_kts: float, altitude_ft: float) -> Vector:
    tas = ias_kts * KNOT * np.sqrt(RHO0 / density(altitude_ft * FT))
    y = np.array([0.0, 0.0, -altitude_ft * FT, tas, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.5])
    s = evaluate(y, aircraft)
    # Trim axial acceleration at entry. Normal G is exactly one.
    available = PROP_EFFICIENCY * aircraft.power_w * (s.rho / RHO0) ** 0.85 / tas
    y[11] = min(1.0, s.drag / (available * np.cos(s.alpha_rad)))
    return y


@dataclass
class Forces:
    acceleration: Vector
    body: Vector
    forward: Vector
    right: Vector
    down: Vector
    alpha_rad: float
    cl: float
    lift: float
    drag: float
    thrust: float
    gz: float
    rho: float


def evaluate(y: Vector, a: Aircraft) -> Forces:
    v = float(np.linalg.norm(y[3:6]))
    forward = y[3:6] / v
    right = y[6:9] - forward * np.dot(forward, y[6:9])
    right /= np.linalg.norm(right)
    down = np.cross(forward, right)
    rho = density(-float(y[2]))
    qs = 0.5 * rho * v * v * a.area_m2
    # Solve Gz = qS(CL cos(alpha) + CD sin(alpha))/(mg).
    alpha = float(y[9] * a.mass_kg * G / qs / CL_ALPHA)
    for _ in range(5):
        cl = CL_ALPHA * alpha
        cd = CD0 + INDUCED_K * cl * cl
        value = cl * np.cos(alpha) + cd * np.sin(alpha)
        deriv = (
            CL_ALPHA * np.cos(alpha)
            - cl * np.sin(alpha)
            + 2 * INDUCED_K * cl * CL_ALPHA * np.sin(alpha)
            + cd * np.cos(alpha)
        )
        alpha -= float((value - y[9] * a.mass_kg * G / qs) / deriv)
    cl = CL_ALPHA * alpha
    lift = qs * cl
    drag = qs * (CD0 + INDUCED_K * cl * cl)
    thrust = PROP_EFFICIENCY * a.power_w * (rho / RHO0) ** 0.85 * float(y[11]) / max(v, 25.0)
    body_x = np.cos(alpha) * forward - np.sin(alpha) * down
    body_z = np.sin(alpha) * forward + np.cos(alpha) * down
    body = np.column_stack((body_x, right, body_z))
    acceleration = GRAVITY + (thrust * body_x - drag * forward - lift * down) / a.mass_kg
    gz = float(-np.dot(acceleration - GRAVITY, body_z) / G)
    return Forces(acceleration, body, forward, right, down, alpha, cl, lift, drag, thrust, gz, rho)


def derivative(y: Vector, aircraft: Aircraft, command: Vector) -> Vector:
    s = evaluate(y, aircraft)
    v = float(np.linalg.norm(y[3:6]))
    fdot = (s.acceleration - s.forward * np.dot(s.forward, s.acceleration)) / v
    rdot = -s.forward * np.dot(fdot, s.right) + y[10] * s.down
    response = np.array(
        [
            np.clip((command[0] - y[9]) / 0.30, -2.5, 2.5),
            np.clip((command[1] - y[10]) / 0.20, -np.deg2rad(160), np.deg2rad(160)),
            np.clip((command[2] - y[11]) / 0.4, -1.0, 1.0),
        ]
    )
    return np.concatenate((y[3:6], s.acceleration, rdot, response))


def step(y: Vector, a: Aircraft, command: Vector, dt: float) -> Vector:
    """Classical RK4 with a transported, re-orthonormalized wind basis."""
    k1 = derivative(y, a, command)
    k2 = derivative(y + dt * k1 / 2, a, command)
    k3 = derivative(y + dt * k2 / 2, a, command)
    k4 = derivative(y + dt * k3, a, command)
    z = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    f = z[3:6] / np.linalg.norm(z[3:6])
    r = z[6:9] - f * np.dot(f, z[6:9])
    z[6:9] = r / np.linalg.norm(r)
    return z
