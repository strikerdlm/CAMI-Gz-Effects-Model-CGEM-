"""
Aerobatic Profiles Loader
=========================

This module provides a convenient way to load **aerobatic manoeuvre G-profiles**
that can be fed into the Combined-G-Effects-Model (CGEM) or any other
physiological model.  A *profile* is represented as a time-series of *(Nz,
duration_ms)* tuples where

* **Nz** – instantaneous normal acceleration (positive values are +Gz, negative
  values are −Gz).
* **duration_ms** – how long that Nz value is maintained, in **milliseconds**.

The raw data is stored in plain-text files inside the directory
`Aerobatics_sample_inputs/`.  Each file corresponds to a real aerobatic
manoeuvre that was measured in-flight and later discretised for simulation.
The first line of every file contains the **number of subsequent samples**.  All
remaining lines contain the comma-separated pair `Nz, duration_ms`.

Example file structure (excerpt from *hammerhead.txt*):

```
22            ← number of rows that follow
0.0, 1000     ← Nz, duration_ms
2.0, 1000
0.3, 1000
...
```

Quick-start
-----------

```python
from aerobatic_profiles import load_profile, load_all_profiles

data = load_profile("hammerhead")  # → List[Sample]
all_manoeuvres = load_all_profiles()  # → Dict[str, List[Sample]]
```

Available manoeuvres
--------------------

identifier              | file name                         | description
----------------------- | --------------------------------- | ------------------------------------------------------------
`hammerhead`            | hammerhead.txt                    | Vertical climb to zero-airspeed, yaw 180°, vertical descent
`horizontal_rolling_360`| horizontalrolling360.txt          | 360° aileron roll while maintaining level flight
`outside_360`           | outside360.txt                    | 360° outside loop (−G throughout the manoeuvre)
`outside_inside_vert8`  | outsideinsidevertical8.txt        | Vertical figure-of-eight: outside loop on the bottom, inside on the top
`quarter_down_roll`     | quarterdownroll.txt               | Quarter outside loop followed by 90° downline snap roll
`snap_45deg_down_roll`  | snap45degdownroll.txt             | 45° downline with a snap roll
`half_vert_roll_neg_pull`| halfverticalrollwnegpullout.txt  | ½ vertical roll with negative pull-out

Feel free to extend the table by adding new files to
`Aerobatics_sample_inputs/` and updating the mapping below.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

__all__ = [
    "Sample",
    "PROFILE_DIR",
    "PROFILES",
    "load_profile",
    "load_all_profiles",
]

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Sample:
    """A single entry of an aerobatic G-profile.

    Attributes
    ----------
    nz : float
        Instantaneous normal acceleration (+Gz / −Gz)
    duration_ms : int
        Time span for which *nz* is held, in milliseconds.
    """

    nz: float
    duration_ms: int


# ---------------------------------------------------------------------------
# File mapping & metadata
# ---------------------------------------------------------------------------

PROFILE_DIR: Path = Path(__file__).resolve().parent / "Aerobatics_sample_inputs"

# Mapping: internal identifier → (filename, human-readable description)
PROFILES: Dict[str, Tuple[str, str]] = {
    "hammerhead": ("hammerhead.txt", "Hammerhead (stall-turn): vertical climb, 180° yaw, vertical descent"),
    "horizontal_rolling_360": ("horizontalrolling360.txt", "360° aileron roll while maintaining level flight"),
    "outside_360": ("outside360.txt", "360° outside loop sustaining −G"),
    "outside_inside_vert8": ("outsideinsidevertical8.txt", "Vertical figure-of-eight – outside loop bottom, inside loop top"),
    "quarter_down_roll": ("quarterdownroll.txt", "Quarter outside loop followed by a downline snap roll"),
    "snap_45deg_down_roll": ("snap45degdownroll.txt", "45° downline with a snap roll"),
    "half_vert_roll_neg_pull": (
        "halfverticalrollwnegpullout.txt",
        "½ vertical roll ending with a negative G pull-out",
    ),
    # Custom push–pull sequences (conceptual/demo)
    "triple_push_pull_loop": (
        "triple_push_pull_loop.txt",
        "Triple push–pull loop: repeated push (−G) then pull (+G) x3",
    ),
    "triple_push_pull_immelmann": (
        "triple_push_pull_immelmann.txt",
        "Triple push–pull Immelmann: push–pull + half-roll repeated x3",
    ),
    "triple_push_pull_split_s": (
        "triple_push_pull_split_s.txt",
        "Triple push–pull Split S: three consecutive push–pull Split S entries",
    ),
    # High-risk maneuver set for G-LOC/greyout/blackout studies (conceptual)
    "high_g_turn": ("high_g_turn.txt", "Sustained high-G level turn with 6–7 G plateau and on/off modulation"),
    "loop_standard": ("loop_standard.txt", "Standard loop with 3–5 G pull-up and pull-out phases"),
    "immelmann_turn": ("immelmann_turn.txt", "Half-loop to half-roll Immelmann with high +G pull-up"),
    "split_s": ("split_s.txt", "Split-S: roll inverted then descending half-loop with high +G pull-out"),
    "cuban_eight": ("cuban_eight.txt", "Cuban Eight: two looping segments joined by half-rolls"),
    "vertical_eight": ("vertical_eight.txt", "Vertical figure eight with repeated +G exposures and brief −G transitions"),

    # ------------------------------------------------------------------------
    # Championship extension (Aresti / IAC families 1, 6, 7, 8, 9)
    # See maneuvers_catalog.py for category, peak G, onset, and source metadata.
    # ------------------------------------------------------------------------
    "avalanche": ("avalanche.txt", "Inside loop with a horizontal positive snap roll at the apex; adds asymmetric high-G transient."),
    "tailslide_positive": ("tailslide_positive.txt", "Vertical climb to zero airspeed, brief rearward slide, canopy-back nose-over with positive-G recovery."),
    "tailslide_negative": ("tailslide_negative.txt", "Vertical climb, rearward slide, canopy-forward nose-over with negative-G recovery."),
    "humpty_bump_positive": ("humpty_bump_positive.txt", "Quarter-loop up, vertical line, half-loop forward (positive over the top), vertical line down, quarter-loop pull."),
    "humpty_bump_negative": ("humpty_bump_negative.txt", "Quarter-loop up, pushed (outside) half-loop over the top loading the pilot negatively, vertical down."),
    "square_loop": ("square_loop.txt", "Four 90° corner pulls (~5–6 G) linked by 1-G straight lines."),
    "reverse_cuban_eight": ("reverse_cuban_eight.txt", "Mirror of standard Cuban eight: 5/8-loop entry then 45° upline half-rolls and pulls."),
    "snap_roll_level": ("snap_roll_level.txt", "Autorotative aileron-rudder snap on level line; brief asymmetric high-G spike."),
    "vertical_snap_upline": ("vertical_snap_upline.txt", "Quarter-loop pull to vertical, snap roll executed during the climb at decaying airspeed."),
    "outside_snap_level": ("outside_snap_level.txt", "Snap roll initiated by forward stick (negative AOA stall); brief negative-G spike."),
    "hesitation_roll_4pt": ("hesitation_roll_4pt.txt", "Aileron roll executed in four 90° increments with brief stops."),
    "hesitation_roll_8pt": ("hesitation_roll_8pt.txt", "Eight-stop slow roll (45° increments)."),
    "slow_roll_level": ("slow_roll_level.txt", "Continuous full-360° aileron roll on level line; smooth Nz transition through ±1 G."),
    "inverted_spin": ("inverted_spin.txt", "Sustained autorotation at negative AOA; -1.5 to -2.5 G sustained, +G recovery pull."),
    "flat_spin_positive": ("flat_spin_positive.txt", "High-AOA flat-attitude spin; modest +Gz dominated by centripetal yaw rate."),
    "inverted_flat_spin": ("inverted_flat_spin.txt", "Flat spin in inverted attitude; sustained -1.5 to -2.5 G."),
    "english_bunt": ("english_bunt.txt", "Full outside loop pushed from level upright; sustained negative G throughout."),
    "torque_roll": ("torque_roll.txt", "Vertical zero-airspeed rotation under engine torque; ~0 G hang then recovery."),
    "knife_edge_pass_highg": ("knife_edge_pass_highg.txt", "High-G level turn into 90° bank knife-edge with rudder; sustained +G then sudden offload."),
    "double_immelmann": ("double_immelmann.txt", "Two consecutive Immelmann turns flown back-to-back without level segment between."),
    "quarter_clover": ("quarter_clover.txt", "Looping segment combined with 90° heading change; classical clover-leaf training figure."),
    "reverse_half_cuban": ("reverse_half_cuban.txt", "Half-Cuban entered from the top: pull up to 45° upline, half-roll to inverted, then 5/8 loop."),
    "lazy_eight": ("lazy_eight.txt", "Gentle commercial-pilot/training maneuver: undulating coordinated turns in horizontal figure-eight."),

    # ------------------------------------------------------------------------
    # Military ACM / BFM extension
    # ------------------------------------------------------------------------
    "defensive_break_9g": ("military_defensive_break_9g.txt", "Maximum-performance 9-G defensive break turn to spoil a bandit's tracking solution."),
    "sustained_9g_turn": ("military_sustained_9g_turn.txt", "9-G structural-limit turn held for 25–30 s (qualification SACM standard)."),
    "corner_velocity_turn": ("military_corner_velocity_turn.txt", "Brief instantaneous-rate turn at corner velocity (max G/min radius) with rapid energy bleed."),
    "high_yoyo_offensive": ("military_high_yoyo.txt", "Offensive 3-D maneuver: climb out of plane, trade airspeed, dive back into bandit's plane."),
    "low_yoyo_offensive": ("military_low_yoyo.txt", "Offensive maneuver: roll-and-dive below bandit's plane to gain closure, then hard pull-up."),
    "barrel_roll_attack": ("military_barrel_roll_attack.txt", "Rolling, vertically-displaced helical maneuver to control closure on a slower bandit."),
    "lag_pursuit_roll": ("military_lag_pursuit_roll.txt", "Rolling-displacement maneuver to convert excess closure into angles."),
    "flat_scissors_defensive": ("military_flat_scissors.txt", "Defensive horizontal-plane rolling reversals to force bandit overshoot."),
    "rolling_scissors": ("military_rolling_scissors.txt", "Vertical scissors with rolling component; sustained 3–5 G alternating."),
    "defensive_jink": ("military_defensive_jink.txt", "Rapid out-of-plane G excursions to defeat tracking-gun / IR-missile lock-on."),
    "last_ditch_break": ("military_last_ditch_break.txt", "Final maximum-G out-of-plane break ~1.5–3 s before missile impact, often combined with chaff/flare."),
    "combat_immelmann": ("military_combat_immelmann.txt", "Combat-power half-loop with half-roll on top; 6–7 G entry pull."),
    "combat_split_s": ("military_combat_split_s.txt", "Inverted half-loop reversal at low altitude with 7–8 G pull-out."),
    "defensive_break_chaff_flare": ("military_defensive_break_chaff_flare.txt", "Max-G break with brief unload at decoy release to favor seduction, then re-pull."),
    "strike_turn_strafing_pullout": ("military_strike_pullout.txt", "Ground-attack profile: shallow dive at -1 G push, strafing pass, 7 G pull-out."),
    "push_pull_missile_evasion": ("military_push_pull_evasion.txt", "Negative-G push to displace velocity vector, immediately followed by max +G inside pull."),
    "defensive_spiral": ("military_defensive_spiral.txt", "Descending high-G spiral (corkscrew) to bleed bandit's energy."),
    "rate_fight_sustained": ("military_rate_fight.txt", "Two-circle sustained turning engagement at corner velocity; 7–8 G plateau for 22 s."),
    "vertical_climb_missile_evasion": ("military_vertical_climb_evasion.txt", "Zoom climb to drag missile into thin air; high-G pull-up then near-1 G climb."),
    "helicopter_bugout": ("military_helicopter_bugout.txt", "Low-energy disengagement: nose-high, decelerate, pivot and pitch over into dive."),
    "slatted_high_aoa_turn": ("military_slatted_high_aoa_turn.txt", "Sustained 7-G turn at high AOA with leading-edge slats deployed."),

    # ------------------------------------------------------------------------
    # Extreme / post-stall extension (Cobra, Kulbit, Lomcovak, Herbst, etc.)
    # ------------------------------------------------------------------------
    "pugachev_cobra": ("pugachev_cobra.txt", "Dynamic post-stall pitch-up to ~110–120° AOA, decelerate, pitch forward and recover."),
    "kulbit": ("kulbit.txt", "Cobra continued through full 360° backflip about pitch axis at low translational velocity."),
    "lomcovak": ("lomcovak.txt", "Czech autorotative tumbling maneuver; gyroscopically coupled rotation about all three body axes."),
    "herbst_jturn": ("herbst_jturn.txt", "Post-stall yaw-reversal: pitch-up to ~70° AOA, 180° body-axis yaw, pitch-down recovery."),
    "helicopter_maneuver": ("helicopter_maneuver.txt", "Near-vertical attitude at low airspeed (Russian 'Bell'); rearward drift, nose-over, recovery."),
    "falling_leaf": ("falling_leaf.txt", "Sustained high-AOA flight with alternating yaw/pitch oscillations resembling a falling leaf."),
    "tailslide_tumble": ("tailslide_tumble.txt", "Tailslide entering autorotative tumble during recovery; compound sustained-G then alternating ±G."),
    "inverted_cobra": ("inverted_cobra.txt", "Theoretical negative-G mirror of Pugachev's Cobra; sustained -Gz spike and recovery from inverted."),
    "lomcovak_repeats": ("lomcovak_repeats.txt", "Two to three Lomcováks back-to-back; cumulative axis-switching ±G."),
    "inverted_spin_recovery": ("inverted_spin_recovery.txt", "Developed inverted spin → 2–3 s -G recovery dive → hard symmetric +G pull."),
    "bell_tailslide": ("bell_tailslide.txt", "Vertical climb, full backslide, negative-G nose-over at apex, forward dive recovery."),
    "snake_modulated": ("snake_modulated.txt", "Falling leaf with intentional pitch-rate forcing producing phased ±G modulation."),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_profile(identifier: str, profile_dir: Path | None = None) -> List[Sample]:
    """Load a single aerobatic G-profile by its *identifier*.

    Parameters
    ----------
    identifier : str
        Key defined in the :data:`~aerobatic_profiles.PROFILES` mapping.
    profile_dir : pathlib.Path | None, optional
        Directory that contains the raw profile files.  Defaults to
        :data:`~aerobatic_profiles.PROFILE_DIR`.

    Returns
    -------
    List[Sample]
        Parsed list maintaining the original order of the manoeuvre samples.

    Raises
    ------
    KeyError
        If *identifier* is not present in :data:`~aerobatic_profiles.PROFILES`.
    FileNotFoundError
        If the profile file cannot be located.
    ValueError
        If the file contents are malformed.
    """

    if profile_dir is None:
        profile_dir = PROFILE_DIR

    try:
        filename, _ = PROFILES[identifier]
    except KeyError as exc:
        raise KeyError(
            f"Unknown profile '{identifier}'. Available profiles: {list(PROFILES)}"
        ) from exc

    filepath = profile_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Profile file not found: {filepath}")

    lines = filepath.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        raise ValueError(f"Profile file is empty: {filepath}")

    try:
        expected_rows = int(lines[0].strip())
    except ValueError as exc:
        raise ValueError(
            f"First line of profile must specify an integer row count: {filepath}"
        ) from exc

    samples: List[Sample] = []
    for idx, raw in enumerate(lines[1:], start=1):
        if not raw.strip():
            # Allow blank lines for readability
            continue
        try:
            nz_str, dur_str = raw.split(",")
            nz = float(nz_str.strip())
            duration_ms = int(dur_str.strip())
        except Exception as exc:
            raise ValueError(
                f"Malformed line {idx+1} in {filepath}: '{raw}'. Expected 'float, int'"
            ) from exc
        samples.append(Sample(nz=nz, duration_ms=duration_ms))

    if len(samples) != expected_rows:
        raise ValueError(
            f"Row count mismatch in {filepath}: expected {expected_rows}, got {len(samples)}"
        )

    return samples


def load_all_profiles(profile_dir: Path | None = None) -> Dict[str, List[Sample]]:
    """Load **all** available profiles into a dictionary.

    Parameters
    ----------
    profile_dir : pathlib.Path | None, optional
        Directory containing the raw profile files.  Defaults to
        :data:`~aerobatic_profiles.PROFILE_DIR`.

    Returns
    -------
    Dict[str, List[Sample]]
        Mapping of *identifier* → list of :class:`Sample` objects.
    """

    if profile_dir is None:
        profile_dir = PROFILE_DIR

    return {key: load_profile(key, profile_dir) for key in PROFILES}


# ---------------------------------------------------------------------------
# CLI helper (optional)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, json, sys

    parser = argparse.ArgumentParser(
        description="Print aerobatic G-profiles as JSON for quick inspection",
    )
    parser.add_argument(
        "identifier",
        nargs="?",
        default=None,
        help="Profile identifier (omit to dump all profiles)",
    )
    args = parser.parse_args()

    try:
        if args.identifier:
            data = {args.identifier: load_profile(args.identifier)}
        else:
            data = load_all_profiles()
    except Exception as exc:  # pragma: no cover – simple helper
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    json.dump(
        {k: [sample.__dict__ for sample in v] for k, v in data.items()},
        sys.stdout,
        indent=2,
    )
    print()  # newline