"""Kinematic attitude (pitch/roll) synthesis for aerobatic G-trace playback.

Each maneuver profile is mapped to a flight-path template. Attitude keyframes
are emitted at the end of every G segment so the tactical simulator ADI can
interpolate pitch and roll during playback.

This is a visualization model aligned with Aresti families and maneuver names —
not a 6-DOF integrator. CGEM still receives only the Nz profile.
"""
from __future__ import annotations

import math
from typing import Callable, Literal

Sample = dict[str, float]
AttitudePair = tuple[float, float]

TemplateName = Literal[
    "inside_loop",
    "inside_loop_snap_apex",
    "outside_loop",
    "square_loop",
    "vertical_maneuver",
    "tailslide",
    "immelmann",
    "split_s",
    "cuban_eight",
    "aileron_roll",
    "snap_roll",
    "hesitation_roll",
    "barrel_roll",
    "acm_turn",
    "spin",
    "cobra",
    "knife_edge",
    "lazy_eight",
    "push_pull",
    "hammerhead",
    "post_stall_tumble",
    "level_flight",
]

# Explicit overrides for figures whose G trace alone is ambiguous.
TEMPLATE_BY_ID: dict[str, TemplateName] = {
    "avalanche": "inside_loop_snap_apex",
    "loop_standard": "inside_loop",
    "square_loop": "square_loop",
    "outside_360": "outside_loop",
    "english_bunt": "outside_loop",
    "vertical_eight": "outside_loop",
    "outside_inside_vert8": "outside_loop",
    "triple_push_pull_loop": "push_pull",
    "triple_push_pull_immelmann": "push_pull",
    "triple_push_pull_split_s": "push_pull",
    "hammerhead": "hammerhead",
    "tailslide_positive": "tailslide",
    "tailslide_negative": "tailslide",
    "bell_tailslide": "tailslide",
    "tailslide_tumble": "post_stall_tumble",
    "immelmann_turn": "immelmann",
    "double_immelmann": "immelmann",
    "combat_immelmann": "immelmann",
    "split_s": "split_s",
    "combat_split_s": "split_s",
    "cuban_eight": "cuban_eight",
    "reverse_cuban_eight": "cuban_eight",
    "quarter_clover": "cuban_eight",
    "reverse_half_cuban": "cuban_eight",
    "lazy_eight": "lazy_eight",
    "horizontal_rolling_360": "aileron_roll",
    "slow_roll_level": "aileron_roll",
    "torque_roll": "aileron_roll",
    "snap_roll_level": "snap_roll",
    "vertical_snap_upline": "snap_roll",
    "outside_snap_level": "snap_roll",
    "quarter_down_roll": "snap_roll",
    "snap_45deg_down_roll": "snap_roll",
    "hesitation_roll_4pt": "hesitation_roll",
    "hesitation_roll_8pt": "hesitation_roll",
    "half_vert_roll_neg_pull": "snap_roll",
    "barrel_roll_attack": "barrel_roll",
    "lag_pursuit_roll": "barrel_roll",
    "rolling_scissors": "barrel_roll",
    "knife_edge_pass_highg": "knife_edge",
    "inverted_spin": "spin",
    "flat_spin_positive": "spin",
    "inverted_flat_spin": "spin",
    "inverted_spin_recovery": "spin",
    "pugachev_cobra": "cobra",
    "inverted_cobra": "cobra",
    "kulbit": "post_stall_tumble",
    "lomcovak": "post_stall_tumble",
    "lomcovak_repeats": "post_stall_tumble",
    "herbst_jturn": "post_stall_tumble",
    "helicopter_maneuver": "vertical_maneuver",
    "helicopter_bugout": "vertical_maneuver",
    "falling_leaf": "post_stall_tumble",
    "snake_modulated": "post_stall_tumble",
    "humpty_bump_positive": "vertical_maneuver",
    "humpty_bump_negative": "vertical_maneuver",
    "high_g_turn": "acm_turn",
}


def to_export_attitude(pitch: float, roll: float) -> AttitudePair:
    """Map body attitude to ADI pitch (±90°) while preserving roll for rotation."""
    p = pitch
    r = roll
    while p > 90.0:
        p = 180.0 - p
        r += 180.0
    while p < -90.0:
        p = -180.0 - p
        r += 180.0
    return (p, r)


def normalize_adi(pitch: float, roll: float) -> AttitudePair:
    """Map body attitude to ADI-friendly pitch (±90°) and roll (±180°)."""
    p, r = to_export_attitude(pitch, roll)
    if r > 180.0:
        r -= 360.0
    if r < -180.0:
        r += 360.0
    return (p, r)


def _segment_end_times(samples: list[Sample]) -> tuple[list[float], float]:
    t = 0.0
    times: list[float] = []
    for sample in samples:
        t += sample["duration_ms"] / 1000.0
        times.append(t)
    return times, t


def _find_snap_segment(samples: list[Sample]) -> int | None:
    """Index of brief high-G spike (snap roll), if any."""
    best: int | None = None
    best_score = 0.0
    for i, sample in enumerate(samples):
        nz = sample["nz"]
        dur = sample["duration_ms"]
        if nz >= 4.5 and dur <= 450.0:
            score = nz / max(dur, 1.0)
            if score > best_score:
                best_score = score
                best = i
    return best


def _lerp(a: float, b: float, f: float) -> float:
    return a + (b - a) * max(0.0, min(1.0, f))


def _synth_inside_loop(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.42:
            pitch = 90.0 * (frac / 0.42)
            roll = 0.0
        elif frac < 0.58:
            pitch = 8.0
            roll = 180.0
        else:
            pitch = 90.0 * (1.0 - (frac - 0.58) / 0.42)
            roll = 0.0
        out.append((pitch, roll))
    return out


def _synth_inside_loop_snap_apex(
    times: list[float],
    samples: list[Sample],
    total: float,
) -> list[AttitudePair]:
    snap_i = _find_snap_segment(samples)
    if snap_i is None:
        return _synth_inside_loop(times, total)

    snap_t = times[snap_i]
    out: list[AttitudePair] = []
    for i, t in enumerate(times):
        pitch = 0.0
        roll = 0.0
        if i < snap_i:
            approach_frac = t / snap_t if snap_t > 0 else 0.0
            if approach_frac < 0.58:
                pitch = 90.0 * (approach_frac / 0.58)
            elif approach_frac < 0.78:
                pitch = 8.0
                roll = 180.0
            else:
                pitch = 90.0
                roll = 0.0
        elif i == snap_i:
            pitch = 90.0
            roll = 360.0
        else:
            rem = total - snap_t if total > snap_t else 1.0
            local = (t - snap_t) / rem
            pitch = 90.0 * (1.0 - local)
            roll = 0.0
        out.append((pitch, roll))
    return out


def _synth_outside_loop(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = -180.0 + 360.0 * frac
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_square_loop(times: list[float], total: float) -> list[AttitudePair]:
    corners = [(0.0, 0.0), (0.25, 90.0), (0.5, 180.0), (0.75, 90.0), (1.0, 0.0)]
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = 0.0
        for j in range(len(corners) - 1):
            f0, p0 = corners[j]
            f1, p1 = corners[j + 1]
            if f0 <= frac <= f1:
                local = (frac - f0) / (f1 - f0) if f1 > f0 else 0.0
                pitch = _lerp(p0, p1, local)
                break
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_vertical(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.35:
            pitch = _lerp(0.0, 90.0, frac / 0.35)
        elif frac < 0.65:
            pitch = 90.0
        else:
            pitch = _lerp(90.0, 0.0, (frac - 0.65) / 0.35)
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_tailslide(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.4:
            pitch = _lerp(0.0, 90.0, frac / 0.4)
        elif frac < 0.55:
            pitch = 90.0
        elif frac < 0.75:
            pitch = _lerp(90.0, 180.0, (frac - 0.55) / 0.2)
        else:
            pitch = _lerp(180.0, 0.0, (frac - 0.75) / 0.25)
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_immelmann(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.45:
            pitch = _lerp(0.0, 180.0, frac / 0.45)
            roll = 0.0
        elif frac < 0.55:
            pitch = to_export_attitude(180.0, 0.0)[0]
            roll = _lerp(0.0, 180.0, (frac - 0.45) / 0.1)
        else:
            pitch = 0.0
            roll = 180.0
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_split_s(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.15:
            pitch = 0.0
            roll = _lerp(0.0, 180.0, frac / 0.15)
        elif frac < 0.55:
            pitch = _lerp(180.0, 0.0, (frac - 0.15) / 0.4)
            roll = 180.0
        else:
            pitch = 0.0
            roll = 180.0
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_cuban_eight(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.45:
            local = frac / 0.45
            pitch = 360.0 * local * 0.55
            roll = 180.0 if 0.38 < local < 0.42 else 0.0
        else:
            local = (frac - 0.45) / 0.55
            pitch = 360.0 * (0.55 + local * 0.45)
            roll = 180.0 if 0.35 < local < 0.4 else 0.0
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_aileron_roll(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        roll = 360.0 * frac
        out.append(to_export_attitude(0.0, roll))
    return out


def _synth_snap_roll(
    times: list[float],
    samples: list[Sample],
    total: float,
    *,
    vertical: bool = False,
) -> list[AttitudePair]:
    snap_i = _find_snap_segment(samples)
    out: list[AttitudePair] = []
    for i, t in enumerate(times):
        if snap_i is not None and i >= snap_i:
            snap_t = times[snap_i]
            rem = total - snap_t if total > snap_t else 1.0
            local = (t - snap_t) / rem
            roll = 360.0 * local
        else:
            frac = t / total if total > 0 else 0.0
            roll = 0.0 if frac < 0.85 else 360.0 * ((frac - 0.85) / 0.15)
        pitch = 90.0 if vertical else 0.0
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_hesitation_roll(times: list[float], total: float, stops: int) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        step = int(frac * stops)
        roll = (360.0 / stops) * step
        out.append(to_export_attitude(0.0, roll))
    return out


def _synth_barrel_roll(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = 25.0 * math.sin(frac * 2.0 * math.pi)
        roll = 360.0 * frac
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_acm_turn(times: list[float], samples: list[Sample], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for i, t in enumerate(times):
        nz = max(samples[i]["nz"], 1.0)
        bank = math.degrees(math.acos(min(1.0, 1.0 / nz))) if nz > 1.05 else 0.0
        pitch = 5.0 if samples[i]["nz"] > 3.0 else 0.0
        out.append(to_export_attitude(pitch, bank))
    return out


def _synth_spin(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = _lerp(45.0, 70.0, abs(math.sin(frac * 4.0 * math.pi)))
        roll = 30.0 * math.sin(frac * 6.0 * math.pi)
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_cobra(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.35:
            pitch = _lerp(0.0, 110.0, frac / 0.35)
        elif frac < 0.55:
            pitch = _lerp(110.0, 40.0, (frac - 0.35) / 0.2)
        else:
            pitch = _lerp(40.0, 0.0, (frac - 0.55) / 0.45)
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_knife_edge(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if 0.2 < frac < 0.8:
            out.append(to_export_attitude(0.0, 90.0))
        else:
            out.append(to_export_attitude(0.0, _lerp(0.0, 90.0, min(1.0, frac / 0.2))))
    return out


def _synth_lazy_eight(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = 20.0 * math.sin(frac * 2.0 * math.pi)
        roll = 25.0 * math.sin(frac * 4.0 * math.pi)
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_push_pull(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = 35.0 * math.sin(frac * 3.0 * math.pi)
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_hammerhead(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        if frac < 0.45:
            pitch = _lerp(0.0, 90.0, frac / 0.45)
        elif frac < 0.55:
            pitch = 90.0
        else:
            pitch = _lerp(90.0, -90.0, (frac - 0.55) / 0.45)
        out.append(to_export_attitude(pitch, 0.0))
    return out


def _synth_post_stall_tumble(times: list[float], total: float) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for t in times:
        frac = t / total if total > 0 else 0.0
        pitch = 360.0 * frac
        roll = 180.0 * math.sin(frac * 3.0 * math.pi)
        out.append(to_export_attitude(pitch, roll))
    return out


def _synth_level_flight(times: list[float], samples: list[Sample]) -> list[AttitudePair]:
    out: list[AttitudePair] = []
    for sample in samples:
        nz = sample["nz"]
        pitch = 8.0 if nz > 2.5 else 0.0
        bank = math.degrees(math.acos(min(1.0, 1.0 / max(nz, 1.0)))) if nz > 1.05 else 0.0
        out.append(to_export_attitude(pitch, bank))
    return out


_SYNTH: dict[TemplateName, Callable[..., list[AttitudePair]]] = {
    "inside_loop": lambda times, samples, total: _synth_inside_loop(times, total),
    "inside_loop_snap_apex": _synth_inside_loop_snap_apex,
    "outside_loop": lambda times, samples, total: _synth_outside_loop(times, total),
    "square_loop": lambda times, samples, total: _synth_square_loop(times, total),
    "vertical_maneuver": lambda times, samples, total: _synth_vertical(times, total),
    "tailslide": lambda times, samples, total: _synth_tailslide(times, total),
    "immelmann": lambda times, samples, total: _synth_immelmann(times, total),
    "split_s": lambda times, samples, total: _synth_split_s(times, total),
    "cuban_eight": lambda times, samples, total: _synth_cuban_eight(times, total),
    "aileron_roll": lambda times, samples, total: _synth_aileron_roll(times, total),
    "hesitation_roll": lambda times, samples, total: _synth_hesitation_roll(times, total, 4),
    "barrel_roll": lambda times, samples, total: _synth_barrel_roll(times, total),
    "acm_turn": _synth_acm_turn,
    "spin": lambda times, samples, total: _synth_spin(times, total),
    "cobra": lambda times, samples, total: _synth_cobra(times, total),
    "knife_edge": lambda times, samples, total: _synth_knife_edge(times, total),
    "lazy_eight": lambda times, samples, total: _synth_lazy_eight(times, total),
    "push_pull": lambda times, samples, total: _synth_push_pull(times, total),
    "hammerhead": lambda times, samples, total: _synth_hammerhead(times, total),
    "post_stall_tumble": lambda times, samples, total: _synth_post_stall_tumble(times, total),
    "level_flight": lambda times, samples, total: _synth_level_flight(times, samples),
}


def resolve_template(
    identifier: str,
    category: str,
    aresti_family: int | None,
    description: str,
) -> TemplateName:
    if identifier in TEMPLATE_BY_ID:
        return TEMPLATE_BY_ID[identifier]

    ident = identifier.lower()
    desc = description.lower()

    if "hesitation" in ident:
        return "hesitation_roll"
    if "snap" in ident or "snap" in desc:
        return "snap_roll"
    if "roll" in ident and "barrel" not in ident and "lag" not in ident:
        return "aileron_roll"
    if "barrel" in ident or "scissors" in ident:
        return "barrel_roll"
    if "spin" in ident:
        return "spin"
    if "cobra" in ident or "kulbit" in ident:
        return "cobra"
    if "tailslide" in ident or "bell" in ident:
        return "tailslide"
    if "loop" in ident:
        if "outside" in ident or "english" in ident:
            return "outside_loop"
        if "square" in ident:
            return "square_loop"
        return "inside_loop"
    if "immelmann" in ident:
        return "immelmann"
    if "split_s" in ident or "split s" in desc:
        return "split_s"
    if "cuban" in ident or "clover" in ident:
        return "cuban_eight"
    if "lazy" in ident:
        return "lazy_eight"
    if "push_pull" in ident or "push–pull" in desc or "push-pull" in desc:
        return "push_pull"
    if "knife" in ident:
        return "knife_edge"
    if "hammerhead" in ident:
        return "hammerhead"
    if category == "military_acm":
        return "acm_turn"
    if category == "extreme_post_stall":
        return "post_stall_tumble"
    if aresti_family == 7:
        return "inside_loop"
    if aresti_family == 8:
        return "cuban_eight"
    if aresti_family == 9:
        return "aileron_roll"
    if aresti_family == 6:
        return "vertical_maneuver"
    return "level_flight"


def synthesize_attitude(
    identifier: str,
    category: str,
    aresti_family: int | None,
    description: str,
    samples: list[Sample],
) -> list[AttitudePair]:
    """Return (pitch_deg, roll_deg) at the end of each G segment."""
    if not samples:
        return []

    template = resolve_template(identifier, category, aresti_family, description)
    times, total = _segment_end_times(samples)

    if template == "hesitation_roll":
        stops = 8 if "8pt" in identifier else 4
        return _synth_hesitation_roll(times, total, stops)
    if template == "snap_roll":
        vertical = "vertical" in identifier
        return _synth_snap_roll(times, samples, total, vertical=vertical)

    synth_fn = _SYNTH[template]
    return synth_fn(times, samples, total)


def attach_attitude_to_samples(
    identifier: str,
    category: str,
    aresti_family: int | None,
    description: str,
    samples: list[Sample],
) -> list[dict[str, float]]:
    pairs = synthesize_attitude(identifier, category, aresti_family, description, samples)
    enriched: list[dict[str, float]] = []
    for sample, (pitch, roll) in zip(samples, pairs, strict=True):
        enriched.append(
            {
                **sample,
                "pitch_deg": round(pitch, 2),
                "roll_deg": round(roll, 2),
            }
        )
    return enriched
