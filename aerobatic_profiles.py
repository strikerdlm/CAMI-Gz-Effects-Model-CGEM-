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