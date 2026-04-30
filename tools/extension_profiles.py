"""
Extension profile data — championship, military, and extreme/post-stall maneuvers.

This is the single source of truth for the 56 maneuvers added on top of the
original 16 in aerobatic_profiles.PROFILES. Run tools/generate_extension.py to
materialize the .txt files in Aerobatics_sample_inputs/ and emit the snippets
to splice into aerobatic_profiles.py and maneuvers_catalog.py.

Each entry in EXTENSION_PROFILES has:
  identifier   — snake_case key for PROFILES dict
  filename     — Aerobatics_sample_inputs/<filename>.txt
  description  — human-readable description (used in PROFILES dict and CATALOG)
  category     — "championship" | "military_acm" | "extreme_post_stall"
  aresti_family— int 1..9 or None
  aircraft     — typical airframe context
  peak_pos_gz  — peak +Gz
  peak_neg_gz  — peak -Gz
  onset_g_per_s— typical onset rate
  total_dur_s  — total maneuver duration (s)
  sustained_gz / sustained_dur_s — for sustained-G plateau (None if transient-only)
  hemodynamic_concern — short note
  source       — citation / basis
  rows         — list of (Nz, duration_ms) tuples (the profile data)

Citations: subagents flagged honestly that web tools were unavailable; profiles
are kinematic-phase reconstructions calibrated against the existing CGEM sample
inputs and standard aerobatic / fighter doctrine references (FAI/CIVA Aresti
catalogue, Shaw 1985 "Fighter Combat", FAA H-8083-9 Aerobatic Flying Handbook,
Newman & Callister 2009 DOI:10.3357/asem.2361.2009).
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Optional

ProfileRow = Tuple[float, int]


def _rows(*rows: ProfileRow) -> List[ProfileRow]:
    return list(rows)


# =============================================================================
# CHAMPIONSHIP — 23 maneuvers (Aresti / IAC catalogue)
# =============================================================================

CHAMPIONSHIP: Dict[str, dict] = {
    "avalanche": {
        "filename": "avalanche.txt",
        "description": "Inside loop with a horizontal positive snap roll at the apex; adds asymmetric high-G transient.",
        "aresti_family": 7,
        "aircraft": "Unlimited (Extra 330 / Su-26)",
        "peak_pos_gz": 6.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 3.0, "total_dur_s": 9.0,
        "hemodynamic_concern": "Loop sustained +G plus brief snap-roll spike (~250 ms).",
        "source": "FAI/CIVA Aresti family 7 + 9 (snap subfamily); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.0, 500),(3.5, 600),(5.0, 700),(5.5, 700),(4.0, 500),
            (2.0, 500),(0.5, 400),(-1.0, 400),(0.5, 300),(6.0, 250),(0.5, 300),
            (-0.8, 400),(1.5, 500),(3.0, 600),(4.5, 700),(3.0, 500),(1.0, 600),
        ),
    },
    "tailslide_positive": {
        "filename": "tailslide_positive.txt",
        "description": "Vertical climb to zero airspeed, brief rearward slide, canopy-back nose-over with positive-G recovery.",
        "aresti_family": 6,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 3.5, "peak_neg_gz": -0.5,
        "onset_g_per_s": 5.0, "total_dur_s": 10.0,
        "hemodynamic_concern": "Long zero-G phase before positive recovery pull (mild push-pull).",
        "source": "FAI/CIVA Aresti family 6; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(3.5, 600),(1.0, 800),(1.0, 1000),(0.6, 600),(0.2, 500),
            (0.0, 500),(-0.2, 600),(-0.5, 600),(0.0, 400),(1.5, 400),(3.5, 500),
            (2.5, 500),(1.5, 500),(0.8, 500),(0.2, 500),(0.0, 600),
        ),
    },
    "tailslide_negative": {
        "filename": "tailslide_negative.txt",
        "description": "Vertical climb, rearward slide, canopy-forward nose-over with negative-G recovery.",
        "aresti_family": 6,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 1.0, "peak_neg_gz": -2.5,
        "onset_g_per_s": 5.0, "total_dur_s": 10.0,
        "hemodynamic_concern": "Sustained negative-G recovery; cephalad blood pooling.",
        "source": "FAI/CIVA Aresti family 6; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(3.5, 600),(1.0, 800),(1.0, 1000),(0.5, 500),(0.0, 400),
            (-0.2, 500),(-0.5, 500),(-1.5, 500),(-2.5, 500),(-2.0, 500),(-1.2, 500),
            (-0.6, 500),(-0.2, 500),(0.2, 500),(0.0, 600),(0.0, 600),
        ),
    },
    "humpty_bump_positive": {
        "filename": "humpty_bump_positive.txt",
        "description": "Quarter-loop up, vertical line, half-loop forward (positive over the top), vertical line down, quarter-loop pull.",
        "aresti_family": 8,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 5.5, "peak_neg_gz": -0.5,
        "onset_g_per_s": 4.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "Two large +G corners bracketing brief negative apex.",
        "source": "FAI/CIVA Aresti family 8; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.0, 500),(4.0, 600),(5.0, 700),(5.5, 600),(3.0, 500),
            (1.5, 600),(1.0, 800),(1.5, 500),(3.5, 500),(4.5, 500),(2.0, 500),
            (-0.5, 500),(1.5, 500),(1.0, 800),(1.5, 500),(4.0, 600),(5.5, 700),
            (3.0, 500),(1.0, 600),
        ),
    },
    "humpty_bump_negative": {
        "filename": "humpty_bump_negative.txt",
        "description": "Quarter-loop up, pushed (outside) half-loop over the top loading the pilot negatively, vertical down.",
        "aresti_family": 8,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 5.5, "peak_neg_gz": -4.0,
        "onset_g_per_s": 3.5, "total_dur_s": 14.0,
        "hemodynamic_concern": "Sustained -3 to -4 G across pushed half-loop; severe push-pull risk.",
        "source": "FAI/CIVA Aresti family 8; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.0, 500),(4.5, 600),(5.5, 700),(4.0, 500),(1.5, 500),
            (1.0, 800),(0.5, 400),(-2.0, 500),(-4.0, 600),(-4.0, 600),(-2.5, 500),
            (0.0, 400),(1.0, 600),(1.5, 800),(2.5, 500),(4.5, 600),(5.5, 700),
            (3.0, 500),(1.0, 500),
        ),
    },
    "square_loop": {
        "filename": "square_loop.txt",
        "description": "Four 90° corner pulls (~5–6 G) linked by 1-G straight lines.",
        "aresti_family": 7,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 6.0, "peak_neg_gz": -0.2,
        "onset_g_per_s": 5.5, "total_dur_s": 15.0,
        "hemodynamic_concern": "Four high-onset +6 G corners in sequence; AGSM endurance test.",
        "source": "FAI/CIVA Aresti family 7 (square loop); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.5, 400),(5.0, 500),(6.0, 400),(1.0, 1500),(5.5, 500),
            (6.0, 400),(2.0, 500),(-0.2, 1500),(-0.2, 1000),(1.5, 500),(5.5, 400),
            (6.0, 500),(1.0, 1500),(5.0, 500),(6.0, 400),(2.5, 500),(1.0, 600),
            (0.5, 400),(0.0, 600),
        ),
    },
    "reverse_cuban_eight": {
        "filename": "reverse_cuban_eight.txt",
        "description": "Mirror of standard Cuban eight: 5/8-loop entry then 45° upline half-rolls and pulls.",
        "aresti_family": 7,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 5.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 3.5, "total_dur_s": 18.0,
        "hemodynamic_concern": "Two large +G pulls separated by brief negative half-roll segments.",
        "source": "FAI/CIVA Aresti family 7 (eights); kinematic synthesis.",
        "rows": _rows(
            (0.0, 400),(2.0, 500),(3.8, 600),(5.0, 700),(4.5, 600),(2.5, 500),
            (1.0, 500),(0.2, 400),(-1.0, 400),(0.5, 400),(1.5, 500),(0.0, 500),
            (2.2, 500),(4.0, 600),(5.0, 700),(4.0, 600),(2.5, 500),(1.0, 500),
            (0.2, 400),(-1.0, 400),(0.5, 400),(0.0, 600),
        ),
    },
    "snap_roll_level": {
        "filename": "snap_roll_level.txt",
        "description": "Autorotative aileron-rudder snap on level line; brief asymmetric high-G spike.",
        "aresti_family": 9,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 6.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 18.0, "total_dur_s": 5.0,
        "hemodynamic_concern": "Sub-300 ms +6 G spike; onset rate exceeds AGSM time constant.",
        "source": "FAI/CIVA Aresti family 9 (snap subfamily); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(1.0, 400),(1.2, 300),(2.0, 250),(6.0, 250),(4.0, 250),
            (1.5, 300),(-1.0, 300),(0.5, 400),(1.0, 500),(1.0, 600),(1.0, 800),
        ),
    },
    "vertical_snap_upline": {
        "filename": "vertical_snap_upline.txt",
        "description": "Quarter-loop pull to vertical, snap roll executed during the climb at decaying airspeed.",
        "aresti_family": 9,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 6.0, "peak_neg_gz": -1.5,
        "onset_g_per_s": 18.0, "total_dur_s": 9.0,
        "hemodynamic_concern": "Snap-G spike on top of 1-G vertical baseline.",
        "source": "FAI/CIVA Aresti family 9 (snap on family-1 line); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.5, 500),(4.5, 500),(3.0, 400),(1.0, 600),(1.0, 400),
            (6.0, 250),(4.0, 250),(-1.5, 300),(0.5, 400),(1.0, 600),(1.0, 800),
            (0.5, 600),(0.0, 500),
        ),
    },
    "outside_snap_level": {
        "filename": "outside_snap_level.txt",
        "description": "Snap roll initiated by forward stick (negative AOA stall); brief negative-G spike.",
        "aresti_family": 9,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 1.5, "peak_neg_gz": -4.5,
        "onset_g_per_s": 18.0, "total_dur_s": 5.0,
        "hemodynamic_concern": "Sub-300 ms -4.5 G spike; rare physiologic challenge.",
        "source": "FAI/CIVA Aresti family 9 (outside snap); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(1.0, 400),(0.8, 300),(0.5, 250),(-2.0, 250),(-4.5, 250),
            (-3.0, 250),(-0.5, 300),(1.5, 300),(1.0, 400),(1.0, 600),(1.0, 600),
        ),
    },
    "hesitation_roll_4pt": {
        "filename": "hesitation_roll_4pt.txt",
        "description": "Aileron roll executed in four 90° increments with brief stops.",
        "aresti_family": 9,
        "aircraft": "Aerobatic competition",
        "peak_pos_gz": 1.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 2.5, "total_dur_s": 6.0,
        "hemodynamic_concern": "Mild oscillating G; knife-edge unloads to ~0 G.",
        "source": "FAI/CIVA Aresti family 9; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(1.0, 500),(1.0, 500),(0.3, 400),(0.0, 500),(-0.3, 400),
            (-1.0, 500),(-1.0, 500),(-0.3, 400),(0.0, 500),(0.3, 400),(1.0, 500),
            (1.0, 600),
        ),
    },
    "hesitation_roll_8pt": {
        "filename": "hesitation_roll_8pt.txt",
        "description": "Eight-stop slow roll (45° increments).",
        "aresti_family": 9,
        "aircraft": "Aerobatic competition",
        "peak_pos_gz": 1.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 2.0, "total_dur_s": 8.0,
        "hemodynamic_concern": "Finer-granularity oscillation; mild stress.",
        "source": "FAI/CIVA Aresti family 9; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(1.0, 400),(0.7, 400),(0.3, 400),(0.0, 400),(-0.3, 400),
            (-0.7, 400),(-1.0, 400),(-1.0, 400),(-0.7, 400),(-0.3, 400),(0.0, 400),
            (0.3, 400),(0.7, 400),(1.0, 400),(1.0, 400),(1.0, 600),
        ),
    },
    "slow_roll_level": {
        "filename": "slow_roll_level.txt",
        "description": "Continuous full-360° aileron roll on level line; smooth Nz transition through ±1 G.",
        "aresti_family": 9,
        "aircraft": "Aerobatic competition",
        "peak_pos_gz": 1.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 1.5, "total_dur_s": 5.0,
        "hemodynamic_concern": "Smooth ±1 G sinusoid; mild physiologic load.",
        "source": "FAI/CIVA Aresti family 9; idealised slow-roll Nz profile.",
        "rows": _rows(
            (0.0, 500),(1.0, 400),(0.7, 300),(0.0, 300),(-0.7, 300),(-1.0, 400),
            (-1.0, 400),(-0.7, 300),(0.0, 300),(0.7, 300),(1.0, 400),(1.0, 500),
            (0.0, 600),
        ),
    },
    "inverted_spin": {
        "filename": "inverted_spin.txt",
        "description": "Sustained autorotation at negative AOA; -1.5 to -2.5 G sustained, +G recovery pull.",
        "aresti_family": 9,
        "aircraft": "Aerobatic / military trainer",
        "peak_pos_gz": 3.0, "peak_neg_gz": -2.5,
        "onset_g_per_s": 4.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "Sustained -G with Coriolis stress; recovery pull on deconditioned baroreflex.",
        "source": "FAI/CIVA Aresti family 9 (inverted spin subcode); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(0.5, 500),(0.0, 400),(-0.5, 500),(-1.5, 500),(-2.0, 800),
            (-2.5, 1000),(-2.0, 1000),(-2.5, 1000),(-2.0, 1000),(-2.5, 1000),(-2.0, 800),
            (-1.5, 600),(-0.5, 500),(1.0, 500),(3.0, 500),(2.0, 500),(0.5, 600),
        ),
    },
    "flat_spin_positive": {
        "filename": "flat_spin_positive.txt",
        "description": "High-AOA flat-attitude spin; modest +Gz dominated by centripetal yaw rate.",
        "aresti_family": 9,
        "aircraft": "Aerobatic / fighter",
        "peak_pos_gz": 2.5, "peak_neg_gz": -0.5,
        "onset_g_per_s": 3.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "Dominant rotational/Gy stress (not modeled); +Gz modest.",
        "source": "FAI/CIVA Aresti family 9 (flat spin subcode); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(0.8, 400),(1.5, 500),(2.0, 800),(2.5, 1000),(2.5, 1000),
            (2.5, 1000),(2.5, 1000),(2.5, 1000),(2.5, 1000),(2.5, 1000),(2.0, 800),
            (1.5, 600),(0.5, 500),(-0.5, 400),(1.0, 500),(2.5, 500),(1.0, 600),
        ),
    },
    "inverted_flat_spin": {
        "filename": "inverted_flat_spin.txt",
        "description": "Flat spin in inverted attitude; sustained -1.5 to -2.5 G.",
        "aresti_family": 9,
        "aircraft": "Aerobatic / fighter",
        "peak_pos_gz": 2.0, "peak_neg_gz": -2.5,
        "onset_g_per_s": 4.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "Most stressful Unlimited spin; sustained -G + rotational stress.",
        "source": "FAI/CIVA Aresti family 9; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(-0.5, 400),(-1.5, 500),(-2.0, 800),(-2.5, 1000),(-2.5, 1000),
            (-2.5, 1000),(-2.5, 1000),(-2.5, 1000),(-2.5, 1000),(-2.5, 1000),(-2.0, 800),
            (-1.5, 600),(-0.5, 500),(0.5, 400),(2.0, 500),(1.0, 500),(0.0, 600),
        ),
    },
    "english_bunt": {
        "filename": "english_bunt.txt",
        "description": "Full outside loop pushed from level upright; sustained negative G throughout.",
        "aresti_family": 7,
        "aircraft": "Unlimited aerobatic",
        "peak_pos_gz": 0.5, "peak_neg_gz": -4.5,
        "onset_g_per_s": 3.0, "total_dur_s": 16.0,
        "hemodynamic_concern": "Sustained -3 to -4.5 G for 12+ seconds; cerebral congestion / red-out risk.",
        "source": "FAI/CIVA Aresti family 7 (outside loop variant); kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(-1.0, 500),(-2.5, 600),(-3.5, 700),(-4.5, 700),(-4.0, 600),
            (-3.0, 600),(-2.5, 600),(-2.0, 800),(-2.5, 600),(-3.0, 600),(-3.5, 700),
            (-4.5, 700),(-4.0, 600),(-3.0, 600),(-2.5, 600),(-2.0, 600),(-1.5, 600),
            (-1.0, 600),(-0.5, 500),(0.0, 500),(0.5, 600),
        ),
    },
    "torque_roll": {
        "filename": "torque_roll.txt",
        "description": "Vertical zero-airspeed rotation under engine torque; ~0 G hang then recovery.",
        "aresti_family": 1,
        "aircraft": "Showpiece (Sean Tucker / Mike Goulian)",
        "peak_pos_gz": 2.5, "peak_neg_gz": -0.5,
        "onset_g_per_s": 3.0, "total_dur_s": 10.0,
        "hemodynamic_concern": "Long zero-G float; mild push-pull on recovery.",
        "source": "Airshow figure; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(3.0, 600),(1.5, 700),(1.0, 800),(0.5, 800),(0.0, 1000),
            (-0.2, 1000),(-0.5, 800),(0.0, 500),(0.5, 400),(1.5, 500),(2.5, 500),
            (1.5, 500),(0.5, 600),
        ),
    },
    "knife_edge_pass_highg": {
        "filename": "knife_edge_pass_highg.txt",
        "description": "High-G level turn into 90° bank knife-edge with rudder; sustained +G then sudden offload.",
        "aresti_family": 1,
        "aircraft": "Showpiece",
        "peak_pos_gz": 6.0, "peak_neg_gz": -0.3,
        "onset_g_per_s": 5.0, "total_dur_s": 10.0,
        "hemodynamic_concern": "Sudden +6 → 0 G offload (~10 G/s); abrupt baroreflex demand.",
        "source": "Airshow figure; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.0, 500),(4.0, 500),(5.5, 600),(6.0, 700),(6.0, 700),
            (3.0, 300),(0.5, 300),(0.0, 1500),(0.0, 1000),(1.0, 400),(3.0, 500),
            (1.5, 500),(0.5, 600),
        ),
    },
    "double_immelmann": {
        "filename": "double_immelmann.txt",
        "description": "Two consecutive Immelmann turns flown back-to-back without level segment between.",
        "aresti_family": 8,
        "aircraft": "Generic / fighter",
        "peak_pos_gz": 5.0, "peak_neg_gz": -0.5,
        "onset_g_per_s": 3.5, "total_dur_s": 16.0,
        "hemodynamic_concern": "Two sustained +5 G pulls within 16 s; AGSM endurance.",
        "source": "FAI/CIVA Aresti family 8; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.0, 500),(3.5, 700),(5.0, 700),(3.0, 600),(1.0, 500),
            (0.2, 400),(0.0, 400),(-0.5, 400),(0.5, 500),(1.5, 500),(2.0, 500),
            (3.5, 700),(5.0, 700),(3.0, 600),(1.0, 500),(0.2, 400),(0.0, 400),
            (0.0, 600),(0.0, 800),
        ),
    },
    "quarter_clover": {
        "filename": "quarter_clover.txt",
        "description": "Looping segment combined with 90° heading change; classical clover-leaf training figure.",
        "aresti_family": 7,
        "aircraft": "Generic / fighter",
        "peak_pos_gz": 5.0, "peak_neg_gz": -0.5,
        "onset_g_per_s": 3.5, "total_dur_s": 12.0,
        "hemodynamic_concern": "Single sustained +5 G pull with mild post-roll segment.",
        "source": "FAA-H-8083-9 Aerobatic Flying Handbook; kinematic synthesis.",
        "rows": _rows(
            (0.0, 500),(2.0, 500),(3.5, 600),(5.0, 700),(4.0, 600),(2.5, 500),
            (1.0, 500),(0.0, 400),(-0.5, 400),(0.5, 400),(1.5, 500),(1.0, 600),
            (2.0, 500),(3.0, 500),(1.5, 500),(0.5, 600),
        ),
    },
    "reverse_half_cuban": {
        "filename": "reverse_half_cuban.txt",
        "description": "Half-Cuban entered from the top: pull up to 45° upline, half-roll to inverted, then 5/8 loop.",
        "aresti_family": 7,
        "aircraft": "Aerobatic competition",
        "peak_pos_gz": 5.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 3.0, "total_dur_s": 10.0,
        "hemodynamic_concern": "Single +5 G pull preceded by brief inverted segment.",
        "source": "FAI/CIVA Aresti family 7; kinematic synthesis.",
        "rows": _rows(
            (0.0, 400),(2.0, 500),(3.5, 600),(4.0, 600),(2.0, 500),(0.5, 400),
            (-1.0, 400),(0.0, 400),(1.0, 500),(3.0, 600),(5.0, 700),(3.5, 600),
            (1.5, 500),(0.5, 600),
        ),
    },
    "lazy_eight": {
        "filename": "lazy_eight.txt",
        "description": "Gentle commercial-pilot/training maneuver: undulating coordinated turns in horizontal figure-eight.",
        "aresti_family": 7,
        "aircraft": "Trainer / GA",
        "peak_pos_gz": 2.5, "peak_neg_gz": 0.5,
        "onset_g_per_s": 0.5, "total_dur_s": 24.0,
        "hemodynamic_concern": "Mild; no negative phase. Reference low-stress profile.",
        "source": "FAA-H-8083-3 Airplane Flying Handbook; kinematic synthesis.",
        "rows": _rows(
            (1.0, 800),(1.5, 1000),(2.0, 1000),(2.5, 1000),(2.0, 1000),(1.5, 1000),
            (1.0, 1000),(0.7, 1200),(0.5, 1200),(0.7, 1200),(1.0, 1000),(1.5, 1000),
            (2.0, 1000),(2.5, 1000),(2.0, 1000),(1.5, 1000),(1.0, 1000),(0.7, 1200),
            (0.5, 1200),(1.0, 1000),
        ),
    },
}


# =============================================================================
# MILITARY ACM — 21 maneuvers
# =============================================================================

MILITARY: Dict[str, dict] = {
    "defensive_break_9g": {
        "filename": "military_defensive_break_9g.txt",
        "description": "Maximum-performance 9-G defensive break turn to spoil a bandit's tracking solution.",
        "aircraft": "F-16C",
        "peak_pos_gz": 9.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 7.0, "total_dur_s": 17.0,
        "sustained_gz": 9.0, "sustained_dur_s": 4.0,
        "hemodynamic_concern": "Maximum sustained +Gz with fast onset; AGSM critical.",
        "source": "Shaw, Fighter Combat Ch.4; Newman & Callister 2009 DOI:10.3357/asem.2361.2009.",
        "rows": _rows(
            (1.0, 500),(1.5, 300),(3.0, 200),(5.0, 200),(7.0, 200),(9.0, 200),
            (9.0, 4000),(8.5, 2000),(7.0, 4000),(5.0, 2000),(3.0, 1000),(1.5, 1000),
            (1.0, 1000),
        ),
    },
    "sustained_9g_turn": {
        "filename": "military_sustained_9g_turn.txt",
        "description": "9-G structural-limit turn held for 25–30 s (qualification SACM standard).",
        "aircraft": "F-16C / F-22A",
        "peak_pos_gz": 9.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 6.0, "total_dur_s": 38.0,
        "sustained_gz": 9.0, "sustained_dur_s": 25.0,
        "hemodynamic_concern": "G-tolerance endurance test; cumulative AGSM fatigue.",
        "source": "USAF AFMAN 11-2F-16; NATO HFM-251 lineage SACM 9G/30s standard.",
        "rows": _rows(
            (1.0, 1000),(2.0, 300),(4.0, 300),(6.0, 300),(8.0, 300),(9.0, 300),
            (9.0, 25000),(8.5, 3000),(7.0, 2000),(5.0, 1000),(3.0, 1000),(1.5, 1000),
            (1.0, 1000),
        ),
    },
    "corner_velocity_turn": {
        "filename": "military_corner_velocity_turn.txt",
        "description": "Brief instantaneous-rate turn at corner velocity (max G/min radius) with rapid energy bleed.",
        "aircraft": "F-16C @ ~430 KCAS SL",
        "peak_pos_gz": 9.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 9.0, "total_dur_s": 12.0,
        "sustained_gz": 9.0, "sustained_dur_s": 3.0,
        "hemodynamic_concern": "Aggressive 9 G/s onset; high G-LOC risk if AGSM late.",
        "source": "Shaw Ch.3; F-16 corner-velocity charts.",
        "rows": _rows(
            (1.0, 500),(2.5, 200),(4.5, 200),(6.5, 200),(8.0, 200),(9.0, 200),
            (9.0, 3000),(7.5, 1500),(6.0, 3000),(4.0, 1000),(2.0, 1000),(1.0, 1000),
        ),
    },
    "high_yoyo_offensive": {
        "filename": "military_high_yoyo.txt",
        "description": "Offensive 3-D maneuver: climb out of plane, trade airspeed, dive back into bandit's plane.",
        "aircraft": "F-15C / F-16C",
        "peak_pos_gz": 6.0, "peak_neg_gz": 0.5,
        "onset_g_per_s": 5.0, "total_dur_s": 13.0,
        "sustained_gz": 5.5, "sustained_dur_s": 2.0,
        "hemodynamic_concern": "Dual +5–6 G pulls separated by brief unload.",
        "source": "Shaw Ch.4 (offensive BFM); USAF AFMAN 11-2F-16.",
        "rows": _rows(
            (1.0, 500),(3.0, 400),(5.0, 400),(6.0, 500),(6.0, 2000),(3.0, 800),
            (1.0, 1500),(0.5, 1000),(2.0, 600),(4.0, 500),(5.0, 1500),(3.0, 1000),
            (1.0, 1000),
        ),
    },
    "low_yoyo_offensive": {
        "filename": "military_low_yoyo.txt",
        "description": "Offensive maneuver: roll-and-dive below bandit's plane to gain closure, then hard pull-up.",
        "aircraft": "F-16C / F/A-18",
        "peak_pos_gz": 7.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 6.0, "total_dur_s": 13.0,
        "sustained_gz": 7.0, "sustained_dur_s": 2.5,
        "hemodynamic_concern": "Hard +7 G pull-up after low-G dive; mild push-pull.",
        "source": "Shaw Ch.4; Newman & Callister 2009.",
        "rows": _rows(
            (1.0, 500),(4.0, 500),(5.0, 1500),(2.0, 700),(1.0, 1500),(3.0, 400),
            (5.0, 400),(7.0, 400),(7.0, 2500),(5.0, 1500),(2.0, 1000),(1.0, 1000),
        ),
    },
    "barrel_roll_attack": {
        "filename": "military_barrel_roll_attack.txt",
        "description": "Rolling, vertically-displaced helical maneuver to control closure on a slower bandit.",
        "aircraft": "F-15C / Su-27",
        "peak_pos_gz": 5.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 3.0, "total_dur_s": 14.0,
        "sustained_gz": 4.5, "sustained_dur_s": 6.0,
        "hemodynamic_concern": "Sustained +4–5 G with continuous body-axis rotation (Gy stress).",
        "source": "Shaw Ch.4 (rolling maneuvers).",
        "rows": _rows(
            (1.0, 500),(2.5, 400),(4.0, 400),(5.0, 400),(5.0, 3000),(4.5, 3000),
            (5.0, 2000),(4.5, 2000),(4.0, 1000),(3.0, 800),(1.5, 600),(1.0, 1000),
        ),
    },
    "lag_pursuit_roll": {
        "filename": "military_lag_pursuit_roll.txt",
        "description": "Rolling-displacement maneuver to convert excess closure into angles.",
        "aircraft": "F-16C",
        "peak_pos_gz": 4.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 3.0, "total_dur_s": 13.0,
        "sustained_gz": 3.5, "sustained_dur_s": 6.0,
        "hemodynamic_concern": "Sustained +3–4 G with rolling component.",
        "source": "Shaw Ch.4 (pursuit curves); USAF AFMAN 11-2F-16.",
        "rows": _rows(
            (1.0, 500),(2.0, 400),(3.0, 400),(4.0, 400),(4.0, 4000),(3.5, 2000),
            (3.0, 2000),(2.5, 1500),(2.0, 1000),(1.5, 500),(1.0, 500),
        ),
    },
    "flat_scissors_defensive": {
        "filename": "military_flat_scissors.txt",
        "description": "Defensive horizontal-plane rolling reversals to force bandit overshoot.",
        "aircraft": "F/A-18",
        "peak_pos_gz": 4.5, "peak_neg_gz": 0.5,
        "onset_g_per_s": 4.0, "total_dur_s": 16.0,
        "sustained_gz": 4.0, "sustained_dur_s": 1.5,
        "hemodynamic_concern": "Multiple +4–4.5 G reversal pulses; AGSM cycle stress.",
        "source": "Shaw Ch.4; Newman & Callister 2009 (F/A-18 reversal G profiles).",
        "rows": _rows(
            (1.0, 500),(3.0, 300),(4.5, 400),(4.0, 1500),(1.5, 600),(3.5, 400),
            (4.5, 1500),(4.0, 1500),(1.0, 600),(3.5, 400),(4.5, 1500),(3.5, 1500),
            (1.5, 1000),(1.0, 1000),
        ),
    },
    "rolling_scissors": {
        "filename": "military_rolling_scissors.txt",
        "description": "Vertical scissors with rolling component; sustained 3–5 G alternating.",
        "aircraft": "F-16C / F/A-18",
        "peak_pos_gz": 5.0, "peak_neg_gz": 0.5,
        "onset_g_per_s": 3.0, "total_dur_s": 18.0,
        "sustained_gz": 4.5, "sustained_dur_s": 5.0,
        "hemodynamic_concern": "Sustained +4–5 G with rolling/vertical component over 18 s.",
        "source": "Shaw Ch.4; Newman & Callister 2009.",
        "rows": _rows(
            (1.0, 500),(3.0, 400),(5.0, 500),(5.0, 2000),(3.0, 1500),(2.0, 1000),
            (4.5, 500),(5.0, 2000),(4.5, 1500),(2.0, 1000),(4.5, 500),(5.0, 2000),
            (3.0, 1500),(1.0, 1000),
        ),
    },
    "defensive_jink": {
        "filename": "military_defensive_jink.txt",
        "description": "Rapid out-of-plane G excursions to defeat tracking-gun / IR-missile lock-on.",
        "aircraft": "A-10 / F-16C",
        "peak_pos_gz": 6.5, "peak_neg_gz": -0.5,
        "onset_g_per_s": 10.0, "total_dur_s": 10.0,
        "hemodynamic_concern": "High-onset (~10 G/s) pulses with brief unloads; mild push-pull.",
        "source": "Shaw Ch.5 (gun defense); A-10 BFM doctrine.",
        "rows": _rows(
            (1.0, 400),(4.0, 200),(6.5, 200),(6.0, 800),(1.0, 300),(-0.5, 200),
            (3.0, 200),(6.0, 200),(6.0, 800),(0.5, 300),(4.0, 200),(6.0, 200),
            (5.5, 800),(1.0, 1000),
        ),
    },
    "last_ditch_break": {
        "filename": "military_last_ditch_break.txt",
        "description": "Final maximum-G out-of-plane break ~1.5–3 s before missile impact, often combined with chaff/flare.",
        "aircraft": "F-16C / F/A-18",
        "peak_pos_gz": 9.5, "peak_neg_gz": -1.0,
        "onset_g_per_s": 13.0, "total_dur_s": 6.0,
        "hemodynamic_concern": "Onset >12 G/s exceeds standard envelope; pilot accepts grey-out risk.",
        "source": "Shaw Ch.5; NATO HFM-251 rapid-onset tolerance discussions.",
        "rows": _rows(
            (1.0, 400),(-1.0, 500),(0.0, 200),(3.0, 100),(6.0, 100),(9.0, 100),
            (9.5, 1500),(8.0, 800),(5.0, 600),(3.0, 500),(1.5, 400),(1.0, 800),
        ),
    },
    "combat_immelmann": {
        "filename": "military_combat_immelmann.txt",
        "description": "Combat-power half-loop with half-roll on top; 6–7 G entry pull.",
        "aircraft": "F-16C / F-15C",
        "peak_pos_gz": 7.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 6.0, "total_dur_s": 14.0,
        "sustained_gz": 6.5, "sustained_dur_s": 2.5,
        "hemodynamic_concern": "Higher peak than aerobatic Immelmann (5G); 6 G/s onset.",
        "source": "Shaw Ch.4; USAF AFMAN BFM.",
        "rows": _rows(
            (1.0, 500),(3.0, 400),(5.0, 300),(7.0, 300),(7.0, 2500),(6.0, 1500),
            (4.0, 1500),(2.5, 1500),(1.5, 1500),(0.7, 1000),(0.5, 1000),(0.8, 1000),
            (1.0, 1000),
        ),
    },
    "combat_split_s": {
        "filename": "military_combat_split_s.txt",
        "description": "Inverted half-loop reversal at low altitude with 7–8 G pull-out.",
        "aircraft": "F-16C / F/A-18",
        "peak_pos_gz": 8.0, "peak_neg_gz": -0.5,
        "onset_g_per_s": 7.0, "total_dur_s": 14.0,
        "sustained_gz": 7.5, "sustained_dur_s": 2.5,
        "hemodynamic_concern": "High +G recovery from inverted at low altitude; minimal margin.",
        "source": "Shaw Ch.4; Newman & Callister 2009.",
        "rows": _rows(
            (1.0, 500),(0.5, 600),(-0.5, 600),(0.0, 500),(2.0, 500),(5.0, 400),
            (7.0, 300),(8.0, 300),(8.0, 2500),(6.0, 2000),(3.0, 2000),(1.5, 1500),
            (1.0, 1000),
        ),
    },
    "defensive_break_chaff_flare": {
        "filename": "military_defensive_break_chaff_flare.txt",
        "description": "Max-G break with brief unload at decoy release to favor seduction, then re-pull.",
        "aircraft": "F-16C / F-15E / Eurofighter",
        "peak_pos_gz": 9.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 8.0, "total_dur_s": 14.0,
        "sustained_gz": 8.5, "sustained_dur_s": 2.5,
        "hemodynamic_concern": "Two high-G pulses with abrupt unload; AGSM cycle disruption.",
        "source": "Shaw Ch.5; Bürkle et al. (Eurofighter G-LOC, by topic).",
        "rows": _rows(
            (1.0, 400),(3.0, 300),(6.0, 300),(9.0, 400),(9.0, 2500),(0.5, 300),
            (2.0, 200),(6.0, 200),(8.0, 200),(8.0, 2500),(6.0, 3000),(3.0, 1500),
            (1.5, 1000),(1.0, 1000),
        ),
    },
    "strike_turn_strafing_pullout": {
        "filename": "military_strike_pullout.txt",
        "description": "Ground-attack profile: shallow dive at -1 G push, strafing pass, 7 G pull-out.",
        "aircraft": "A-10C / F-16C strike",
        "peak_pos_gz": 7.0, "peak_neg_gz": -1.0,
        "onset_g_per_s": 7.0, "total_dur_s": 16.0,
        "sustained_gz": 6.5, "sustained_dur_s": 3.0,
        "hemodynamic_concern": "Push-pull: -1 G dive bunt for 2 s then +7 G pull-out.",
        "source": "USAF A-10 BFM/CAS doctrine; Shaw Ch.6.",
        "rows": _rows(
            (1.0, 1000),(0.0, 800),(-1.0, 2000),(-0.5, 800),(0.0, 600),(2.0, 400),
            (4.0, 300),(6.0, 300),(7.0, 300),(7.0, 3000),(4.0, 2000),(2.0, 2000),
            (1.0, 1500),
        ),
    },
    "push_pull_missile_evasion": {
        "filename": "military_push_pull_evasion.txt",
        "description": "Negative-G push to displace velocity vector, immediately followed by max +G inside pull.",
        "aircraft": "F-16C / F/A-18",
        "peak_pos_gz": 7.0, "peak_neg_gz": -1.5,
        "onset_g_per_s": 6.0, "total_dur_s": 13.0,
        "sustained_gz": 6.5, "sustained_dur_s": 3.5,
        "hemodynamic_concern": "Classical push-pull: 2.5 s -1.5 G push then 7 G pull. Tolerance ↓1–2 G.",
        "source": "Banks et al. push-pull effect literature; Shaw Ch.5.",
        "rows": _rows(
            (1.0, 600),(-0.5, 500),(-1.5, 2000),(-1.0, 500),(0.0, 400),(3.0, 300),
            (5.0, 300),(7.0, 300),(7.0, 3500),(5.0, 2000),(2.0, 1000),(1.0, 1000),
        ),
    },
    "defensive_spiral": {
        "filename": "military_defensive_spiral.txt",
        "description": "Descending high-G spiral (corkscrew) to bleed bandit's energy.",
        "aircraft": "F-16C / Su-27",
        "peak_pos_gz": 7.5, "peak_neg_gz": 0.0,
        "onset_g_per_s": 6.0, "total_dur_s": 22.0,
        "sustained_gz": 7.0, "sustained_dur_s": 12.0,
        "hemodynamic_concern": "Sustained +6.5–7.5 G across multiple spiral turns.",
        "source": "Shaw Ch.4 (vertical maneuvers); Zhang et al. Su-27 +Gz exposure.",
        "rows": _rows(
            (1.0, 500),(3.0, 400),(5.0, 400),(7.0, 400),(7.5, 300),(7.5, 5000),
            (7.0, 5000),(6.5, 5000),(5.0, 2000),(3.0, 1500),(1.5, 1000),(1.0, 1000),
        ),
    },
    "rate_fight_sustained": {
        "filename": "military_rate_fight.txt",
        "description": "Two-circle sustained turning engagement at corner velocity; 7–8 G plateau for 22 s.",
        "aircraft": "F-16C / Eurofighter",
        "peak_pos_gz": 8.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 6.0, "total_dur_s": 30.0,
        "sustained_gz": 7.5, "sustained_dur_s": 18.0,
        "hemodynamic_concern": "G-tolerance endurance test; major AGSM fatigue scenario.",
        "source": "Shaw Ch.4 (one-circle vs two-circle); Sauvet et al. F-16 ACM HRV.",
        "rows": _rows(
            (1.0, 1000),(3.0, 400),(5.0, 400),(7.0, 400),(8.0, 400),(8.0, 8000),
            (7.5, 6000),(7.0, 4000),(6.0, 4000),(4.0, 2000),(2.0, 1500),(1.5, 1000),
            (1.0, 1000),
        ),
    },
    "vertical_climb_missile_evasion": {
        "filename": "military_vertical_climb_evasion.txt",
        "description": "Zoom climb to drag missile into thin air; high-G pull-up then near-1 G climb.",
        "aircraft": "F-15C / F-22A",
        "peak_pos_gz": 7.0, "peak_neg_gz": 0.0,
        "onset_g_per_s": 6.0, "total_dur_s": 22.0,
        "sustained_gz": 6.5, "sustained_dur_s": 2.5,
        "hemodynamic_concern": "Initial high-G pull then prolonged low-G climb; mild post-G-pull recovery.",
        "source": "Shaw Ch.4; USAF AFMAN 11-2F-15.",
        "rows": _rows(
            (1.0, 500),(3.0, 400),(5.0, 300),(7.0, 300),(7.0, 2500),(4.0, 1500),
            (2.0, 1500),(1.2, 4000),(1.0, 4000),(0.5, 2000),(0.7, 2000),(1.0, 2000),
            (1.0, 1000),
        ),
    },
    "helicopter_bugout": {
        "filename": "military_helicopter_bugout.txt",
        "description": "Low-energy disengagement: nose-high, decelerate, pivot and pitch over into dive.",
        "aircraft": "F/A-18 / F-16C",
        "peak_pos_gz": 4.5, "peak_neg_gz": -0.7,
        "onset_g_per_s": 3.0, "total_dur_s": 17.0,
        "sustained_gz": 4.0, "sustained_dur_s": 2.5,
        "hemodynamic_concern": "Low-energy push-pull: -0.7 G pitchover then +4.5 G recovery.",
        "source": "Shaw Ch.4 (low-speed maneuvers); Newman & Callister 2009.",
        "rows": _rows(
            (1.0, 500),(1.5, 1500),(0.8, 2000),(0.3, 1500),(-0.3, 1000),(-0.7, 1000),
            (-0.3, 800),(0.5, 600),(2.0, 500),(3.5, 400),(4.5, 2500),(2.5, 2000),
            (1.0, 1500),
        ),
    },
    "slatted_high_aoa_turn": {
        "filename": "military_slatted_high_aoa_turn.txt",
        "description": "Sustained 7-G turn at high AOA with leading-edge slats deployed.",
        "aircraft": "F/A-18C/D",
        "peak_pos_gz": 7.5, "peak_neg_gz": 0.0,
        "onset_g_per_s": 5.0, "total_dur_s": 22.0,
        "sustained_gz": 7.2, "sustained_dur_s": 10.0,
        "hemodynamic_concern": "Long sustained 7 G plateau at high AOA.",
        "source": "Newman & Callister 2009 DOI:10.3357/asem.2361.2009.",
        "rows": _rows(
            (1.0, 1000),(3.0, 500),(5.0, 500),(7.0, 500),(7.5, 500),(7.5, 6000),
            (7.2, 3000),(7.0, 3000),(5.5, 2000),(3.5, 2000),(2.0, 1500),(1.5, 1000),
            (1.0, 1000),
        ),
    },
}


# =============================================================================
# EXTREME / POST-STALL — 12 maneuvers
# =============================================================================

EXTREME: Dict[str, dict] = {
    "pugachev_cobra": {
        "filename": "pugachev_cobra.txt",
        "description": "Dynamic post-stall pitch-up to ~110–120° AOA, decelerate, pitch forward and recover.",
        "aircraft": "Su-27 / Su-35",
        "peak_pos_gz": 6.5, "peak_neg_gz": -0.4,
        "onset_g_per_s": 30.0, "total_dur_s": 5.0,
        "hemodynamic_concern": "Pitch-up Gz spike (~150 ms) too short for AGSM; brief float.",
        "source": "Herbst W.B. (1980) Dynamics of Air Combat, J. Aircraft 17(8); kinematic estimate.",
        "rows": _rows(
            (1.0, 800),(1.5, 150),(3.0, 150),(5.5, 200),(6.5, 200),(4.0, 250),
            (1.5, 300),(0.2, 600),(-0.4, 400),(-0.2, 300),(0.5, 300),(1.8, 300),
            (1.2, 500),(1.0, 700),
        ),
    },
    "kulbit": {
        "filename": "kulbit.txt",
        "description": "Cobra continued through full 360° backflip about pitch axis at low translational velocity.",
        "aircraft": "Su-37 / Su-30MKI / Su-35",
        "peak_pos_gz": 8.0, "peak_neg_gz": -1.8,
        "onset_g_per_s": 35.0, "total_dur_s": 7.0,
        "hemodynamic_concern": "Textbook push-pull: +6–8 G then sustained -1.8 G then +6–7 G recovery.",
        "source": "Sukhoi flight-demo materials; cross-reference Banks et al. push-pull literature.",
        "rows": _rows(
            (1.0, 600),(2.0, 150),(5.0, 150),(7.5, 200),(8.0, 200),(5.0, 250),
            (2.0, 300),(0.0, 300),(-1.0, 400),(-1.8, 400),(-1.2, 300),(0.0, 300),
            (2.0, 200),(5.5, 200),(7.0, 250),(4.0, 300),(1.5, 500),(1.0, 800),
        ),
    },
    "lomcovak": {
        "filename": "lomcovak.txt",
        "description": "Czech autorotative tumbling maneuver; gyroscopically coupled rotation about all three body axes.",
        "aircraft": "Zlín Z-50 / Extra 300 / Su-26",
        "peak_pos_gz": 6.5, "peak_neg_gz": -5.5,
        "onset_g_per_s": 45.0, "total_dur_s": 6.0,
        "hemodynamic_concern": "Highest per-unit-time CV demand; alternating ±5+ G defeats AGSM.",
        "source": "FAI/CIVA Aresti family 9 tumble; Walter Extra airframe ±10G; kinematic estimate.",
        "rows": _rows(
            (1.0, 500),(3.5, 300),(6.0, 400),(2.0, 200),(-3.0, 300),(-5.5, 400),
            (-2.0, 200),(3.0, 300),(6.5, 400),(2.0, 200),(-3.5, 300),(-5.0, 400),
            (-1.5, 200),(4.0, 300),(6.0, 400),(1.0, 300),(-1.0, 400),(0.5, 400),
            (2.0, 500),(1.0, 800),
        ),
    },
    "herbst_jturn": {
        "filename": "herbst_jturn.txt",
        "description": "Post-stall yaw-reversal: pitch-up to ~70° AOA, 180° body-axis yaw, pitch-down recovery.",
        "aircraft": "X-31 / F-22A / F-18 HARV",
        "peak_pos_gz": 3.8, "peak_neg_gz": -0.5,
        "onset_g_per_s": 12.0, "total_dur_s": 12.0,
        "hemodynamic_concern": "Body-axis Nz modest; lateral Gy + longitudinal Gx unmodeled by CGEM.",
        "source": "NASA Dryden / Langley X-31 EFM publications (Smith, Foster).",
        "rows": _rows(
            (1.0, 1000),(1.8, 500),(3.0, 600),(3.8, 800),(3.2, 1000),(2.0, 1500),
            (1.0, 1500),(0.8, 1000),(0.2, 800),(-0.3, 600),(-0.5, 500),(0.5, 500),
            (1.5, 600),(1.2, 800),(1.0, 1000),
        ),
    },
    "helicopter_maneuver": {
        "filename": "helicopter_maneuver.txt",
        "description": "Near-vertical attitude at low airspeed (Russian 'Bell'); rearward drift, nose-over, recovery.",
        "aircraft": "Su-27 / Su-35 / MiG-29 OVT",
        "peak_pos_gz": 3.5, "peak_neg_gz": -1.2,
        "onset_g_per_s": 15.0, "total_dur_s": 12.0,
        "hemodynamic_concern": "Long zero-G phase causes cephalad shift; -G nose-over then mild +G pull.",
        "source": "Sukhoi public demo literature; F-18 HARV high-alpha analog.",
        "rows": _rows(
            (1.0, 1000),(2.0, 500),(1.5, 1000),(0.5, 1500),(0.2, 2000),(0.0, 2000),
            (-0.5, 500),(-1.2, 500),(-0.5, 400),(0.5, 500),(2.0, 400),(3.5, 500),
            (1.5, 700),(1.0, 1000),
        ),
    },
    "falling_leaf": {
        "filename": "falling_leaf.txt",
        "description": "Sustained high-AOA flight with alternating yaw/pitch oscillations resembling a falling leaf.",
        "aircraft": "F-18 HARV / X-31 / Su-35",
        "peak_pos_gz": 2.5, "peak_neg_gz": -1.2,
        "onset_g_per_s": 8.0, "total_dur_s": 16.0,
        "hemodynamic_concern": "10+ s vestibular-baroreflex coupling; mild but cumulative.",
        "source": "NASA Langley wing-rock and falling-leaf literature (Foster).",
        "rows": _rows(
            (1.0, 1000),(1.8, 500),(2.5, 400),(1.5, 500),(0.0, 500),(-1.0, 500),
            (-0.5, 400),(1.0, 500),(2.2, 500),(1.0, 500),(-0.5, 500),(-1.2, 500),
            (0.0, 500),(1.5, 500),(2.5, 500),(1.0, 500),(-0.8, 500),(0.5, 500),
            (1.5, 500),(1.0, 1000),
        ),
    },
    "tailslide_tumble": {
        "filename": "tailslide_tumble.txt",
        "description": "Tailslide entering autorotative tumble during recovery; compound sustained-G then alternating ±G.",
        "aircraft": "Unlimited (Extra 300 / Su-26 / Edge 540)",
        "peak_pos_gz": 6.0, "peak_neg_gz": -5.0,
        "onset_g_per_s": 50.0, "total_dur_s": 9.0,
        "hemodynamic_concern": "Longest combined push-pull pattern in catalog; highest aggregate risk.",
        "source": "Pilot incident reports (CIVA / IAC); kinematic estimate.",
        "rows": _rows(
            (1.0, 800),(4.5, 400),(2.0, 400),(0.5, 600),(-0.5, 600),(-1.2, 800),
            (-0.8, 600),(-0.2, 400),(3.0, 200),(6.0, 300),(-2.0, 300),(-5.0, 300),
            (2.0, 300),(5.5, 300),(-3.0, 300),(-4.0, 300),(2.0, 300),(6.0, 400),
            (3.0, 500),(1.0, 800),
        ),
    },
    "inverted_cobra": {
        "filename": "inverted_cobra.txt",
        "description": "Theoretical negative-G mirror of Pugachev's Cobra; sustained -Gz spike and recovery from inverted.",
        "aircraft": "Theoretical / Extra 300L kinematic equivalent",
        "peak_pos_gz": 1.0, "peak_neg_gz": -5.5,
        "onset_g_per_s": 30.0, "total_dur_s": 5.0,
        "hemodynamic_concern": "Peak -5 G ~ 1 s; conjunctival hemorrhage / red-out risk; airframe-limited.",
        "source": "Burton USAFSAM -Gz literature; theoretical envelope extension.",
        "rows": _rows(
            (1.0, 600),(0.0, 200),(-1.5, 200),(-3.0, 200),(-5.0, 200),(-5.5, 250),
            (-3.5, 250),(-1.5, 300),(-0.2, 500),(0.5, 400),(-0.3, 300),(0.2, 300),
            (1.0, 500),(1.0, 800),
        ),
    },
    "lomcovak_repeats": {
        "filename": "lomcovak_repeats.txt",
        "description": "Two to three Lomcováks back-to-back; cumulative axis-switching ±G.",
        "aircraft": "Extra 330SC / Su-26 / Edge 540 / MX-2",
        "peak_pos_gz": 6.5, "peak_neg_gz": -5.5,
        "onset_g_per_s": 50.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "Cumulative baroreflex exhaustion; CGEM lacks fatigue term — likely under-predicts.",
        "source": "Competition aerobatic flight literature; kinematic estimate.",
        "rows": _rows(
            (1.0, 400),(6.0, 300),(-5.0, 300),(5.5, 300),(-5.5, 300),(2.0, 300),
            (6.0, 300),(-5.5, 300),(6.0, 300),(-5.0, 300),(2.0, 300),(6.5, 300),
            (-5.5, 300),(5.5, 300),(-5.0, 300),(1.5, 400),(3.0, 500),(1.5, 500),
            (0.5, 500),(-0.5, 400),(0.5, 400),(1.0, 800),
        ),
    },
    "inverted_spin_recovery": {
        "filename": "inverted_spin_recovery.txt",
        "description": "Developed inverted spin → 2–3 s -G recovery dive → hard symmetric +G pull.",
        "aircraft": "T-6 / Pitts / Extra 300 / Su-26",
        "peak_pos_gz": 6.0, "peak_neg_gz": -2.5,
        "onset_g_per_s": 25.0, "total_dur_s": 16.0,
        "hemodynamic_concern": "Most clinically realistic push-pull; sustained -G unloads carotid baroreflex before +6 G pull.",
        "source": "NASA SP-2009-575 (Chambers); Bihrle Applied Research; Banks push-pull literature.",
        "rows": _rows(
            (1.0, 1000),(0.0, 500),(-1.5, 800),(-2.5, 1000),(-2.0, 1000),(-1.5, 1000),
            (-1.0, 1000),(-0.5, 800),(0.0, 500),(1.0, 400),(2.5, 300),(4.5, 300),
            (6.0, 400),(6.0, 300),(4.0, 400),(2.0, 500),(1.2, 700),(1.0, 1000),
        ),
    },
    "bell_tailslide": {
        "filename": "bell_tailslide.txt",
        "description": "Vertical climb, full backslide, negative-G nose-over at apex, forward dive recovery.",
        "aircraft": "Sukhoi Su-26/29 / Extra 300 / MX-2",
        "peak_pos_gz": 3.5, "peak_neg_gz": -2.0,
        "onset_g_per_s": 15.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "Sustained low-G then -2 G nose-over; classical push-pull setup.",
        "source": "Russian aerobatic literature ('Bell' / Колокол); CIVA Aresti.",
        "rows": _rows(
            (1.0, 800),(4.0, 400),(2.5, 800),(1.5, 1500),(0.5, 2000),(0.0, 1500),
            (-0.5, 800),(-1.5, 500),(-2.0, 500),(-1.0, 400),(0.0, 400),(1.5, 400),
            (3.5, 400),(2.0, 600),(1.2, 800),(1.0, 1000),
        ),
    },
    "snake_modulated": {
        "filename": "snake_modulated.txt",
        "description": "Falling leaf with intentional pitch-rate forcing producing phased ±G modulation.",
        "aircraft": "F-18 HARV / X-31",
        "peak_pos_gz": 3.8, "peak_neg_gz": -2.0,
        "onset_g_per_s": 20.0, "total_dur_s": 14.0,
        "hemodynamic_concern": "~2–3 s push-pull period close to baroreflex resonance frequency.",
        "source": "NASA F-18 HARV and X-31 high-AOA flight-test pilot reports.",
        "rows": _rows(
            (1.0, 800),(2.0, 400),(3.5, 400),(2.0, 400),(0.5, 400),(-1.5, 400),
            (-2.0, 400),(-0.5, 400),(1.5, 400),(3.5, 400),(2.5, 400),(0.0, 400),
            (-1.8, 400),(-2.0, 400),(-0.5, 400),(2.0, 400),(3.8, 400),(2.0, 400),
            (0.0, 400),(-1.5, 400),(0.5, 500),(1.0, 800),
        ),
    },
}


# =============================================================================
# Combined registry
# =============================================================================

ALL_EXTENSIONS: Dict[str, dict] = {}
for ident, meta in CHAMPIONSHIP.items():
    ALL_EXTENSIONS[ident] = {**meta, "category": "championship"}
for ident, meta in MILITARY.items():
    ALL_EXTENSIONS[ident] = {**meta, "category": "military_acm"}
for ident, meta in EXTREME.items():
    ALL_EXTENSIONS[ident] = {**meta, "category": "extreme_post_stall"}


if __name__ == "__main__":
    # Sanity check
    for ident, meta in ALL_EXTENSIONS.items():
        rows = meta["rows"]
        assert all(len(r) == 2 for r in rows), f"bad row in {ident}"
        assert all(isinstance(r[1], int) and r[1] > 0 for r in rows), f"bad ms in {ident}"
    print(f"OK — {len(ALL_EXTENSIONS)} maneuvers "
          f"({len(CHAMPIONSHIP)} championship, {len(MILITARY)} military, {len(EXTREME)} extreme)")
