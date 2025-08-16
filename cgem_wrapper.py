from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

from aerobatic_profiles import Sample, load_profile


BASE_GLOC_INP = Path(__file__).resolve().parent / "gloc_inp.dat"
def _resolve_cgem_executable() -> Path:
    """Resolve the correct CGEM executable path for the current OS.

    On Windows, prefer `cgem.exe`. On POSIX, prefer the `cgem` binary.
    Falls back between variants if one is missing. Ensures the resolved
    path is a regular file (not a directory).
    """
    root = Path(__file__).resolve().parent
    candidates = []

    if sys.platform.startswith("win"):
        candidates.extend([
            root / "cgem.exe",
            root / "cgem",
        ])
    else:
        candidates.extend([
            root / "cgem",
            root / "cgem.exe",
        ])

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    # Provide a helpful error with the checked locations
    checked = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"CGEM executable not found. Checked: {checked}")


@dataclass
class CGEMResult:
    time_to_greyout_s: Optional[float]
    time_to_blackout_s: Optional[float]
    time_to_gloc_s: Optional[float]

    # Snapshot of last known physiological values (optional, for display)
    last_time_s: Optional[float] = None
    last_g: Optional[float] = None
    last_geff: Optional[float] = None

    # Full time-series from CGEM output for plotting and analysis
    times_s: Optional[List[float]] = None
    g_values: Optional[List[float]] = None
    geff_values: Optional[List[float]] = None
    flags_n2: Optional[List[int]] = None  # consciousness flag
    flags_ne2: Optional[List[int]] = None  # vision flag (greyout)
    flags_non2: Optional[List[int]] = None  # blackout flag


@dataclass(frozen=True)
class PilotConfig:
    """Pilot/subject configuration for CGEM.

    If who_profile is provided (1..6), the Fortran model will override
    subject physiology (flows, BP, sex, height) to that standard profile.
    In that case, only countermeasures and other non-subject parameters
    (e.g., suit, AGSM, PBG, seat tilt, drug delay) will be applied.

    If who_profile is None, a custom subject is used (who=0) and all
    provided fields will be written into gloc_inp.dat.
    """
    # Standard subject selection (1..6) or None for custom
    who_profile: Optional[int] = 2

    # Subject physiology (used when who_profile is None)
    male: Optional[int] = 1  # 1 male, 0 female
    height_cm: Optional[float] = 179.0
    baseline_systolic_bp: Optional[float] = 120.0
    baseline_diastolic_bp: Optional[float] = 80.0
    max_systolic_bp: Optional[float] = 177.0
    max_diastolic_bp: Optional[float] = 80.0
    g_tolerance_multiplier: Optional[float] = 1.0  # gtm
    heart_response_tau_s: Optional[float] = 2.5  # beta
    # Consciousness and life reserves (seconds)
    conbank_s: Optional[float] = 7.1
    lifebank_s: Optional[float] = 180.0

    # Countermeasures and state
    gsuit_max_psi: float = 0.0
    gsuit_coverage_fraction: float = 0.0  # 0.0 - 0.7
    agsm_effectiveness: float = 0.0  # 0..1
    pbg_max_mmhg: float = 0.0  # 0..60
    pretest_other_strain_mmhg: float = 0.0  # 0..60
    non_agsm_tensing_limit_mmhg: float = 0.0  # 0..60
    seat_tilt_deg: float = 10.0  # from vertical
    drug_delay_s: float = 0.0

    # Dehydration level as fraction 0.0 (none) .. 1.0 (severe)
    dehydration_level: float = 0.0

    def to_cache_key(self) -> str:
        # Simple stable string for streamlit cache keys
        d: Dict[str, object] = asdict(self)
        # Convert None to a JSON-friendly null via repr
        return str(sorted(d.items()))

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


def _prepare_gloc_inp(
    temp_dir: Path,
    egp_name: str = "input.egp",
    out_name: str = "output.out",
    config: Optional[PilotConfig] = None,
) -> None:
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
    def _set_line(idx0: int, value_str: str) -> None:
        # idx0 is 0-based line index
        if idx0 < 0 or idx0 >= len(lines):
            return
        # Preserve any comment after the first comma
        if "," in lines[idx0]:
            _, comment = lines[idx0].split(",", 1)
            lines[idx0] = f"{value_str},{comment}"
        else:
            lines[idx0] = value_str

    # Set gfile to 1 (use custom experimental profile), then set names
    _set_line(29, "1")
    _set_line(30, egp_name)
    _set_line(31, out_name)

    # Apply subject and countermeasure overrides
    if config is not None:
        # who_profile: if provided (1..6), use standard subject. else custom.
        who = config.who_profile if config.who_profile in (1, 2, 3, 4, 5, 6) else 0
        _set_line(28, str(who))  # who at 1-based line 29 -> 0-based index 28

        # Countermeasures and other non-subject parameters (always applicable)
        _set_line(19, f"{float(config.gsuit_max_psi):.1f}")  # line 20 smpsi
        _set_line(20, f"{float(config.gsuit_coverage_fraction):.2f}")  # 21 sbc
        _set_line(21, f"{float(config.agsm_effectiveness):.2f}")  # 22 agsm
        _set_line(22, f"{float(config.pbg_max_mmhg):.1f}")  # 23 pbg
        _set_line(23, f"{float(config.pretest_other_strain_mmhg):.1f}")  # 24 otherstrain
        _set_line(24, f"{float(config.non_agsm_tensing_limit_mmhg):.1f}")  # 25 tenlim
        _set_line(25, f"{float(config.seat_tilt_deg):.1f}")  # 26 seattilt
        _set_line(26, f"{float(config.drug_delay_s):.1f}")  # 27 Drugdelay

        if who == 0:
            # Custom subject: write all subject physiology fields
            male_val = 1 if (config.male is None or int(config.male) == 1) else 0
            _set_line(17, str(int(male_val)))  # 18 male
            _set_line(18, f"{float(config.height_cm if config.height_cm is not None else 179.0):.1f}")  # 19 height

            # Baseline and max BPs
            bsp = float(config.baseline_systolic_bp or 120.0)
            bdp = float(config.baseline_diastolic_bp or 80.0)
            msp = float(config.max_systolic_bp or 177.0)
            mdp = float(config.max_diastolic_bp or 80.0)

            # Adjust for dehydration fractionally: reduce BPs modestly and normal flow
            dehydr = max(0.0, min(1.0, float(config.dehydration_level)))
            if dehydr > 0:
                # empirical simple adjustments
                bsp -= 10.0 * dehydr
                bdp -= 5.0 * dehydr
                msp -= 10.0 * dehydr
                mdp -= 5.0 * dehydr

            _set_line(8, f"{bsp:.1f}")  # 9 BSP
            _set_line(9, f"{bdp:.1f}")  # 10 BDP
            _set_line(10, f"{msp:.1f}")  # 11 MSP
            _set_line(11, f"{mdp:.1f}")  # 12 MDP

            # Flow parameters and reserves
            fnorm = float(_extract_numeric(lines[2], default=49.5))
            fmax = float(_extract_numeric(lines[3], default=110.0))
            fcon = float(_extract_numeric(lines[4], default=19.0))
            flife = float(_extract_numeric(lines[5], default=9.0))
            # Apply dehydration to flows (reduce normal and max flows)
            if dehydr > 0:
                fnorm *= (1.0 - 0.10 * dehydr)  # up to 10% reduction
                fmax *= (1.0 - 0.10 * dehydr)

            _set_line(2, f"{fnorm:.1f}")  # 3 fnorm
            _set_line(3, f"{fmax:.1f}")  # 4 fmax
            _set_line(4, f"{fcon:.1f}")  # 5 fcon
            _set_line(5, f"{flife:.1f}")  # 6 flife

            gtm = float(config.g_tolerance_multiplier or 1.0)
            beta = float(config.heart_response_tau_s or 2.5)
            _set_line(6, f"{gtm:.2f}")  # 7 gtm
            _set_line(7, f"{beta:.2f}")  # 8 beta

            conbank = float(config.conbank_s or 7.1)
            lifebank = float(config.lifebank_s or 180.0)
            _set_line(12, f"{conbank:.1f}")  # 13 conbank
            _set_line(13, f"{lifebank:.1f}")  # 14 lifebank


    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _extract_numeric(line: str, default: float = 0.0) -> float:
    try:
        token = line.split(",", 1)[0].strip()
        return float(token)
    except Exception:
        return default


def _run_cgem(temp_dir: Path) -> None:
    exe_path = _resolve_cgem_executable()
    subprocess.run([str(exe_path)], cwd=str(temp_dir), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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

    # Full series
    times_s: List[float] = []
    g_values: List[float] = []
    geff_values: List[float] = []
    flags_n2: List[int] = []
    flags_ne2: List[int] = []
    flags_non2: List[int] = []

    with out_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            # Heuristic: data lines are mostly numeric and fairly long
            if len(parts) >= 12:
                try:
                    # First field could be seconds (ttot) or ms (totalt) depending on context
                    t_raw = float(parts[0])
                    g = float(parts[1])
                    geff = float(parts[2])
                    # Last 3 integers are flags
                    n2 = int(parts[-3])  # conscious state
                    ne2 = int(parts[-2])  # vision
                    non2 = int(parts[-1])  # blackout
                except Exception:
                    continue

                # Normalize time to seconds (heuristic)
                t_sec = t_raw / 1000.0 if t_raw > 100.0 else t_raw

                # Append series
                times_s.append(t_sec)
                g_values.append(g)
                geff_values.append(geff)
                flags_n2.append(n2)
                flags_ne2.append(ne2)
                flags_non2.append(non2)

                # Keep last snapshot (prefer larger time)
                last_time_s = t_sec if t_sec > (last_time_s or -1.0) else last_time_s
                if last_time_s == t_sec:
                    last_g = g
                    last_geff = geff

                if prev_flags is None:
                    prev_flags = (n2, ne2, non2)
                else:
                    pn2, pne2, pnon2 = prev_flags
                    if t_gloc is None and pn2 == 0 and n2 == 1:
                        t_gloc = t_sec
                    if t_grey is None and pne2 == 0 and ne2 == 1:
                        t_grey = t_sec
                    if t_black is None and pnon2 == 0 and non2 == 1:
                        t_black = t_sec
                    prev_flags = (n2, ne2, non2)

    return CGEMResult(
        time_to_greyout_s=t_grey,
        time_to_blackout_s=t_black,
        time_to_gloc_s=t_gloc,
        last_time_s=last_time_s,
        last_g=last_g,
        last_geff=last_geff,
        times_s=times_s,
        g_values=g_values,
        geff_values=geff_values,
        flags_n2=flags_n2,
        flags_ne2=flags_ne2,
        flags_non2=flags_non2,
    )


def run_cgem_for_profile(profile_id: str, config: Optional[PilotConfig] = None) -> Tuple[CGEMResult, Path]:
    """Run CGEM on a given aerobatic profile identifier.

    Returns: (CGEMResult, temp_dir_path) for inspection. Caller may clean up.
    """
    samples = load_profile(profile_id)
    egp_lines = _profile_to_egp_lines(samples)

    # Use a persistent temp directory so that callers can inspect outputs
    temp_dir_path = tempfile.mkdtemp(prefix="cgem_run_")
    temp_dir = Path(temp_dir_path)

    try:
        # Prepare files
        egp_path = temp_dir / "input.egp"
        _write_egp_file(egp_lines, egp_path)
        _prepare_gloc_inp(temp_dir, egp_name="input.egp", out_name="output.out", config=config)

        # Run CGEM
        _run_cgem(temp_dir)

        # Parse output
        out_path = temp_dir / "output.out"
        result = _parse_cgem_output(out_path)
        return result, temp_dir
    except Exception:
        # On failure, clean the temp dir and re-raise
        shutil.rmtree(temp_dir, ignore_errors=True)
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
        "num_points": len(res.times_s or []),
    }, indent=2))
    print(f"Temporary files in: {tmp}")