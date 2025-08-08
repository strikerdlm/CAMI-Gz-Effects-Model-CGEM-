from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from aerobatic_profiles import Sample, load_profile


CGEM_EXE = Path(__file__).resolve().parent / "cgem"
BASE_GLOC_INP = Path(__file__).resolve().parent / "gloc_inp.dat"


@dataclass
class CGEMResult:
    time_to_greyout_s: Optional[float]
    time_to_blackout_s: Optional[float]
    time_to_gloc_s: Optional[float]

    # Snapshot of last known physiological values (optional, for display)
    last_time_s: Optional[float] = None
    last_g: Optional[float] = None
    last_geff: Optional[float] = None


def _profile_to_egp_lines(samples: List[Sample], g0: float = 1.0) -> List[Tuple[float, int]]:
    """Convert Nz/duration_ms samples to CGEM EGP entries (dgdt[G/s], ms).

    Strategy: step instantly (1 ms) to requested Nz from current G using a high
    dgdt, then hold with dgdt=0 for the duration. CGEM integrates per-ms:
    G = G + dgdt * 0.001.
    """
    egp: List[Tuple[float, int]] = []
    current_g = g0

    for s in samples:
        target_g = float(s.nz)
        duration_ms = int(s.duration_ms)
        if duration_ms <= 0:
            continue
        # Ramp to target in 1 ms if needed
        delta = target_g - current_g
        if abs(delta) > 1e-9:
            egp.append((delta * 1000.0, 1))  # 1 ms step
            current_g = target_g
        # Hold
        egp.append((0.0, duration_ms))

    return egp


def _write_egp_file(egp_lines: List[Tuple[float, int]], path: Path) -> None:
    # First line: number of subsequent lines
    with path.open("w", encoding="utf-8") as f:
        f.write(f"{len(egp_lines)}\n")
        for dgdt, ms in egp_lines:
            # Fortran free-form read tolerant to spaces/commas
            f.write(f"{dgdt:.6g}, {int(ms)}\n")


def _prepare_gloc_inp(temp_dir: Path, egp_name: str = "input.egp", out_name: str = "output.out") -> None:
    """Copy base gloc_inp.dat into temp_dir and set custom profile I/O names.

    We assume base file has the standard structure (lines 30-32 control gfile and names).
    """
    assert len(egp_name) <= 12 and len(out_name) <= 12, "EGP and OUT names must be <= 12 chars per CGEM"

    src = BASE_GLOC_INP
    dst = temp_dir / "gloc_inp.dat"
    lines = src.read_text(encoding="utf-8").splitlines()

    # Defensive: ensure there are enough lines
    if len(lines) < 33:
        raise RuntimeError("gloc_inp.dat has unexpected format (too few lines)")

    # Indices based on provided template (1-based in file):
    # 30: gfile (0 or 1)
    # 31: egpname (12 char max)
    # 32: egpoutname (12 char max)
    # Set gfile to 1 (use custom experimental profile), then set names
    lines[29] = "1, \"0 or 1, use a internal/custom experimental profile\""
    lines[30] = egp_name
    lines[31] = out_name

    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_cgem(temp_dir: Path) -> None:
    if not CGEM_EXE.exists():
        raise FileNotFoundError(f"CGEM executable not found at {CGEM_EXE}")
    subprocess.run([str(CGEM_EXE)], cwd=str(temp_dir), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _parse_cgem_output(out_path: Path) -> CGEMResult:
    """Parse CGEM custom() output file to find event times and last snapshot.

    Output rows (format 700):
    time_ms, G, Geff, boc, F, FOG, FON, bonoc, HLAP, n2, ne2, non2
    """
    t_grey: Optional[float] = None
    t_black: Optional[float] = None
    t_gloc: Optional[float] = None

    last_time_s: Optional[float] = None
    last_g: Optional[float] = None
    last_geff: Optional[float] = None

    prev_flags: Optional[Tuple[int, int, int]] = None

    with out_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            # Heuristic: data lines are mostly numeric and fairly long
            if len(parts) >= 12:
                try:
                    # First field could be seconds (ttot) or ms (totalt) depending on context
                    t = float(parts[0])
                    g = float(parts[1])
                    geff = float(parts[2])
                    # Last 3 integers are flags
                    n2 = int(parts[-3])  # conscious state
                    ne2 = int(parts[-2])  # vision
                    non2 = int(parts[-1])  # blackout
                except Exception:
                    continue

                # Keep last snapshot (prefer larger time)
                last_time_s = t if t > (last_time_s or -1.0) else last_time_s
                if last_time_s == t:
                    last_g = g
                    last_geff = geff

                if prev_flags is None:
                    prev_flags = (n2, ne2, non2)
                else:
                    pn2, pne2, pnon2 = prev_flags
                    if t_gloc is None and pn2 == 0 and n2 == 1:
                        t_gloc = t / 1000.0 if t > 100.0 else t  # ms vs s heuristic
                    if t_grey is None and pne2 == 0 and ne2 == 1:
                        t_grey = t / 1000.0 if t > 100.0 else t
                    if t_black is None and pnon2 == 0 and non2 == 1:
                        t_black = t / 1000.0 if t > 100.0 else t
                    prev_flags = (n2, ne2, non2)

    return CGEMResult(
        time_to_greyout_s=t_grey,
        time_to_blackout_s=t_black,
        time_to_gloc_s=t_gloc,
        last_time_s=last_time_s,
        last_g=last_g,
        last_geff=last_geff,
    )


def run_cgem_for_profile(profile_id: str) -> Tuple[CGEMResult, Path]:
    """Run CGEM on a given aerobatic profile identifier.

    Returns: (CGEMResult, temp_dir_path) for inspection. Caller may clean up.
    """
    samples = load_profile(profile_id)
    egp_lines = _profile_to_egp_lines(samples)

    temp_dir_obj = tempfile.TemporaryDirectory(prefix="cgem_run_")
    temp_dir = Path(temp_dir_obj.name)

    try:
        # Prepare files
        egp_path = temp_dir / "input.egp"
        _write_egp_file(egp_lines, egp_path)
        _prepare_gloc_inp(temp_dir, egp_name="input.egp", out_name="output.out")

        # Run CGEM
        _run_cgem(temp_dir)

        # Parse output
        out_path = temp_dir / "output.out"
        result = _parse_cgem_output(out_path)
        return result, temp_dir
    except Exception:
        # On failure, clean temp dir and re-raise
        temp_dir_obj.cleanup()
        raise


if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="Run CGEM on an aerobatic profile and print event times")
    parser.add_argument("profile_id", help="Profile identifier (see aerobatic_profiles.PROFILES)")
    args = parser.parse_args()

    res, tmp = run_cgem_for_profile(args.profile_id)
    print(json.dumps({
        "time_to_greyout_s": res.time_to_greyout_s,
        "time_to_blackout_s": res.time_to_blackout_s,
        "time_to_gloc_s": res.time_to_gloc_s,
        "last_g": res.last_g,
        "last_geff": res.last_geff,
    }, indent=2))
    print(f"Temporary files in: {tmp}")