"""Synthetic CGEM dataset generation.

Cross-product CGEM runner that materialises a reproducible parquet of
``(input features, CGEM outputs)`` rows for downstream surrogate
training, OOD detector fitting, and global sensitivity analysis.

Two arms compose the standard grid:

* **Standard** — ``who_profile in {1..6}`` × ``countermeasures in {none,
  agsm, suit_agsm}``. The Fortran model overrides subject physiology
  (BPs, flows, reserves) to the FAA preset when ``who_profile`` is set,
  so the dehydration knob and the G-tolerance multiplier are no-ops on
  this arm and are therefore not varied. Per maneuver: ``6 × 3 = 18``
  rows.
* **Custom** — ``who_profile=None`` × ``g_tolerance_multiplier in
  {low, nominal, high}`` × ``dehydration in {none, mild, severe}`` ×
  ``countermeasures in {none, agsm, suit_agsm}``. Exercises the
  custom-subject path so the surrogate learns the full input space the
  Fortran model accepts. Per maneuver: ``3 × 3 × 3 = 27`` rows.

Per maneuver: ``18 + 27 = 45`` rows. Across 72 maneuvers: **3,240 rows**.

Reproducibility:

- The compiled CGEM binary is hashed (SHA-256) at run start and written
  to the sidecar metadata; CI verifies the same SHA before re-using the
  dataset.
- A master seed produces deterministic per-row seeds via SHA-derived
  hashing; multiprocessing workers receive their seed alongside the
  RowSpec rather than sharing a Python RNG.
- Every run emits a JSON sidecar with the binary SHA, package version,
  master seed, tier definitions, host, wall-clock, row counts by status,
  and ISO timestamp.

Usage:

    python -m cgem_ext.data.generate_dataset --smoke
    python -m cgem_ext.data.generate_dataset --output data/datasets/cgem_synthetic_v1.parquet
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import platform
import shutil
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import numpy as np
import pandas as pd

import cgem_ext  # noqa: F401  side-effect: injects repo root onto sys.path
from aerobatic_profiles import PROFILES, load_profile
from cgem_wrapper import PilotConfig, run_cgem_for_profile

try:
    from maneuvers_catalog import get as _get_maneuver_meta
except ImportError:  # pragma: no cover  (catalog is shipped, but be defensive)
    _get_maneuver_meta = None  # type: ignore[assignment]


# ──────────────────────────────────────────────────────────────────────
# Tier definitions
# ──────────────────────────────────────────────────────────────────────

DEHYDRATION_LEVELS: dict[str, float] = {
    "none": 0.0,
    "mild": 0.3,
    "severe": 0.7,
}

# Countermeasures tiers — physiologically representative, not exhaustive.
# "none"      — bare-pilot baseline.
# "agsm"      — straining manoeuvre alone (no suit).
# "suit_agsm" — modern fighter package: anti-G suit + AGSM + pressure breathing.
COUNTERMEASURES_LEVELS: dict[str, dict[str, float]] = {
    "none": {
        "gsuit_max_psi": 0.0,
        "gsuit_coverage_fraction": 0.0,
        "agsm_effectiveness": 0.0,
        "pbg_max_mmhg": 0.0,
    },
    "agsm": {
        "gsuit_max_psi": 0.0,
        "gsuit_coverage_fraction": 0.0,
        "agsm_effectiveness": 0.6,
        "pbg_max_mmhg": 0.0,
    },
    "suit_agsm": {
        "gsuit_max_psi": 10.0,
        "gsuit_coverage_fraction": 0.7,
        "agsm_effectiveness": 0.8,
        "pbg_max_mmhg": 15.0,
    },
}

# Only applied in the custom-subject arm (who_profile=None). The Fortran
# model overrides g_tolerance_multiplier when who_profile is set.
G_TOLERANCE_TIERS: dict[str, float] = {"low": 0.85, "nominal": 1.00, "high": 1.15}

WHO_PROFILES: list[int] = [1, 2, 3, 4, 5, 6]


# ──────────────────────────────────────────────────────────────────────
# Reproducibility helpers
# ──────────────────────────────────────────────────────────────────────


def _row_seed(master_seed: int, row_id: str) -> int:
    """Derive a 32-bit per-row seed from ``master_seed`` and a stable row id."""
    digest = hashlib.sha256(f"{master_seed}|{row_id}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def _binary_sha256(binary_path: Path) -> str:
    h = hashlib.sha256()
    with binary_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_binary_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    for name in ("cgem", "cgem.exe"):
        candidate = repo_root / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"CGEM binary not found in {repo_root}. Expected `cgem` or `cgem.exe`."
    )


# ──────────────────────────────────────────────────────────────────────
# Maneuver-summary features (precomputed once per maneuver)
# ──────────────────────────────────────────────────────────────────────


def _maneuver_summary(maneuver: str) -> dict:
    """Compute summary features from a maneuver's G(t) profile.

    The CGEM Fortran model consumes the profile but does not expose its
    descriptors directly; we materialise them here so the surrogate has
    feature-space information about what it is regressing on.
    """
    samples = load_profile(maneuver)
    if not samples:
        return {
            "maneuver_category": "unregistered",
            "aresti_family": None,
            "catalog_onset_rate_g_per_s": None,
            "g_peak_abs": float("nan"),
            "g_min": float("nan"),
            "g_max": float("nan"),
            "dgdt_max_g_per_s": float("nan"),
            "profile_duration_s": float("nan"),
            "num_profile_samples": 0,
        }

    g_values = np.asarray([s.nz for s in samples], dtype=float)
    durations_ms = np.asarray([s.duration_ms for s in samples], dtype=float)
    times_s = np.cumsum(durations_ms) / 1000.0

    g_max = float(g_values.max())
    g_min = float(g_values.min())
    g_peak_abs = float(max(abs(g_max), abs(g_min)))

    if len(g_values) > 1:
        dt = np.diff(times_s)
        dt = np.where(dt <= 0, 1e-6, dt)
        dgdt = np.diff(g_values) / dt
        dgdt_max = float(np.max(np.abs(dgdt)))
    else:
        dgdt_max = 0.0

    profile_duration = float(times_s[-1]) if len(times_s) else 0.0

    if _get_maneuver_meta is not None:
        try:
            meta = _get_maneuver_meta(maneuver)
            category = meta.category.value
            aresti_family = meta.aresti_family
            catalog_onset_rate = meta.onset_rate_g_per_s
        except KeyError:
            category = "unregistered"
            aresti_family = None
            catalog_onset_rate = None
    else:
        category = "unregistered"
        aresti_family = None
        catalog_onset_rate = None

    return {
        "maneuver_category": category,
        "aresti_family": aresti_family,
        "catalog_onset_rate_g_per_s": catalog_onset_rate,
        "g_peak_abs": g_peak_abs,
        "g_min": g_min,
        "g_max": g_max,
        "dgdt_max_g_per_s": dgdt_max,
        "profile_duration_s": profile_duration,
        "num_profile_samples": int(len(samples)),
    }


# ──────────────────────────────────────────────────────────────────────
# Per-row spec + execution
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RowSpec:
    row_id: str
    maneuver: str
    arm: str  # "standard" | "custom"
    who_profile: Optional[int]
    g_tolerance_multiplier: float
    dehydration_label: str
    dehydration_level: float
    countermeasures_label: str
    gsuit_max_psi: float
    gsuit_coverage_fraction: float
    agsm_effectiveness: float
    pbg_max_mmhg: float
    seed: int


def _ts_stats(values: list[float] | None, prefix: str) -> dict:
    """Summary statistics for an optional CGEM time-series."""
    if not values:
        return {
            f"{prefix}_min": float("nan"),
            f"{prefix}_max": float("nan"),
            f"{prefix}_mean": float("nan"),
            f"{prefix}_final": float("nan"),
        }
    arr = np.asarray(values, dtype=float)
    return {
        f"{prefix}_min": float(arr.min()),
        f"{prefix}_max": float(arr.max()),
        f"{prefix}_mean": float(arr.mean()),
        f"{prefix}_final": float(arr[-1]),
    }


def _run_single(spec: RowSpec) -> dict:
    """Execute one CGEM run and return a flat row dict."""
    base_row = {
        "row_id": spec.row_id,
        "maneuver": spec.maneuver,
        "arm": spec.arm,
        "who_profile": spec.who_profile,
        "g_tolerance_multiplier": spec.g_tolerance_multiplier,
        "dehydration_label": spec.dehydration_label,
        "dehydration_level": spec.dehydration_level,
        "countermeasures_label": spec.countermeasures_label,
        "gsuit_max_psi": spec.gsuit_max_psi,
        "gsuit_coverage_fraction": spec.gsuit_coverage_fraction,
        "agsm_effectiveness": spec.agsm_effectiveness,
        "pbg_max_mmhg": spec.pbg_max_mmhg,
        "row_seed": spec.seed,
    }

    cfg_kwargs = {
        "who_profile": spec.who_profile,
        "dehydration_level": spec.dehydration_level,
        "gsuit_max_psi": spec.gsuit_max_psi,
        "gsuit_coverage_fraction": spec.gsuit_coverage_fraction,
        "agsm_effectiveness": spec.agsm_effectiveness,
        "pbg_max_mmhg": spec.pbg_max_mmhg,
    }
    if spec.who_profile is None:
        cfg_kwargs["g_tolerance_multiplier"] = spec.g_tolerance_multiplier

    try:
        cfg = PilotConfig(**cfg_kwargs)
        result, run_dir = run_cgem_for_profile(spec.maneuver, cfg)
    except Exception as exc:  # noqa: BLE001  surface as row status, never crash the pool
        return {**base_row, "status": "error", "error_msg": f"{type(exc).__name__}: {exc}"}
    finally:
        # run_cgem_for_profile creates its own tempdir; clean it eagerly.
        try:
            run_dir  # noqa: B018  (only set on success path)
            shutil.rmtree(run_dir, ignore_errors=True)
        except NameError:
            pass

    row = {
        **base_row,
        "status": "ok",
        "error_msg": None,
        "time_to_greyout_s": result.time_to_greyout_s,
        "time_to_blackout_s": result.time_to_blackout_s,
        "time_to_gloc_s": result.time_to_gloc_s,
        "event_greyout": int(result.time_to_greyout_s is not None),
        "event_blackout": int(result.time_to_blackout_s is not None),
        "event_gloc": int(result.time_to_gloc_s is not None),
        "num_samples": len(result.times_s) if result.times_s else 0,
    }
    row.update(_ts_stats(result.hlap_values, "hlap"))
    row.update(_ts_stats(result.c_bank_values, "c_bank"))
    row.update(_ts_stats(result.bo_bank_values, "bo_bank"))
    row.update(_ts_stats(result.f_con_values, "f_con"))
    row.update(_ts_stats(result.f_vis_values, "f_vis"))
    row.update(_ts_stats(result.f_bo_values, "f_bo"))
    row.update(_ts_stats(result.geff_values, "g_eff"))
    return row


# ──────────────────────────────────────────────────────────────────────
# Grid enumeration
# ──────────────────────────────────────────────────────────────────────


def _spec_from_levels(
    *,
    maneuver: str,
    arm: str,
    who_profile: Optional[int],
    gtm: float,
    deh_label: str,
    deh_value: float,
    cm_label: str,
    cm: dict[str, float],
    master_seed: int,
) -> RowSpec:
    if arm == "standard":
        row_id = f"std|{maneuver}|who{who_profile}|cm{cm_label}|deh{deh_label}"
    else:
        row_id = f"cust|{maneuver}|gtm{deh_label}|cm{cm_label}|deh{deh_label}|gtm{gtm:.2f}"
    return RowSpec(
        row_id=row_id,
        maneuver=maneuver,
        arm=arm,
        who_profile=who_profile,
        g_tolerance_multiplier=gtm,
        dehydration_label=deh_label,
        dehydration_level=deh_value,
        countermeasures_label=cm_label,
        gsuit_max_psi=cm["gsuit_max_psi"],
        gsuit_coverage_fraction=cm["gsuit_coverage_fraction"],
        agsm_effectiveness=cm["agsm_effectiveness"],
        pbg_max_mmhg=cm["pbg_max_mmhg"],
        seed=_row_seed(master_seed, row_id),
    )


def _enumerate_grid(
    maneuvers: list[str],
    *,
    arms: tuple[str, ...],
    master_seed: int,
) -> Iterator[RowSpec]:
    """Enumerate the cross-product grid.

    The standard arm fixes dehydration_level=0 and g_tolerance_multiplier=1
    because the Fortran model ignores both when who_profile is set (subject
    physiology is overridden to a FAA preset). Varying them in the standard
    arm would produce redundant rows; the custom arm covers their effects.
    """
    cm_items = list(COUNTERMEASURES_LEVELS.items())
    deh_items = list(DEHYDRATION_LEVELS.items())
    for maneuver in maneuvers:
        if "standard" in arms:
            for who in WHO_PROFILES:
                for cm_label, cm in cm_items:
                    row_id = f"std|{maneuver}|who{who}|cm{cm_label}"
                    yield RowSpec(
                        row_id=row_id,
                        maneuver=maneuver,
                        arm="standard",
                        who_profile=who,
                        g_tolerance_multiplier=1.0,
                        dehydration_label="none",
                        dehydration_level=0.0,
                        countermeasures_label=cm_label,
                        gsuit_max_psi=cm["gsuit_max_psi"],
                        gsuit_coverage_fraction=cm["gsuit_coverage_fraction"],
                        agsm_effectiveness=cm["agsm_effectiveness"],
                        pbg_max_mmhg=cm["pbg_max_mmhg"],
                        seed=_row_seed(master_seed, row_id),
                    )
        if "custom" in arms:
            for gtm_label, gtm_value in G_TOLERANCE_TIERS.items():
                for cm_label, cm in cm_items:
                    for deh_label, deh_value in deh_items:
                        row_id = (
                            f"cust|{maneuver}|gtm{gtm_label}|cm{cm_label}|deh{deh_label}"
                        )
                        yield RowSpec(
                            row_id=row_id,
                            maneuver=maneuver,
                            arm="custom",
                            who_profile=None,
                            g_tolerance_multiplier=gtm_value,
                            dehydration_label=deh_label,
                            dehydration_level=deh_value,
                            countermeasures_label=cm_label,
                            gsuit_max_psi=cm["gsuit_max_psi"],
                            gsuit_coverage_fraction=cm["gsuit_coverage_fraction"],
                            agsm_effectiveness=cm["agsm_effectiveness"],
                            pbg_max_mmhg=cm["pbg_max_mmhg"],
                            seed=_row_seed(master_seed, row_id),
                        )


# ──────────────────────────────────────────────────────────────────────
# Top-level entry
# ──────────────────────────────────────────────────────────────────────


def generate(
    *,
    output_path: Path,
    maneuvers: list[str] | None = None,
    arms: tuple[str, ...] = ("standard", "custom"),
    master_seed: int = 42,
    workers: int = 0,
    smoke: bool = False,
) -> dict:
    """Generate the dataset and write parquet + sidecar metadata.

    Returns the metadata dict so callers (CI, smoke tests) can assert
    on row counts, status counts, and wall-clock without re-reading
    the parquet.
    """
    if maneuvers is None:
        maneuvers = sorted(PROFILES.keys())
    if smoke:
        maneuvers = maneuvers[:5]
        arms = ("standard", "custom")

    if workers <= 0:
        workers = max(1, mp.cpu_count() - 1)

    specs = list(_enumerate_grid(maneuvers, arms=arms, master_seed=master_seed))
    if smoke:
        # Smoke: 5 maneuvers, who in {1,2} on standard, gtm in {nominal} on
        # custom, all cm tiers, all dehydration tiers. ~ 30+45 = 75 rows.
        specs = [
            s
            for s in specs
            if (s.arm == "standard" and s.who_profile in (1, 2))
            or (s.arm == "custom" and s.g_tolerance_multiplier == 1.0)
        ]

    print(f"Total rows: {len(specs)}", flush=True)
    print(f"Workers:    {workers}", flush=True)

    binary_sha = _binary_sha256(_resolve_binary_path())
    run_id = uuid.uuid4().hex
    start = time.time()

    rows: list[dict] = []
    if workers == 1:
        for i, spec in enumerate(specs):
            if i % 25 == 0 and i:
                print(f"  [{i}/{len(specs)}] {spec.maneuver}/{spec.arm}/who{spec.who_profile}", flush=True)
            rows.append(_run_single(spec))
    else:
        with mp.get_context("spawn").Pool(workers) as pool:
            for i, row in enumerate(pool.imap_unordered(_run_single, specs, chunksize=4)):
                rows.append(row)
                if i % 25 == 0 and i:
                    print(f"  [{i}/{len(specs)}]", flush=True)

    elapsed = time.time() - start

    df = pd.DataFrame(rows)

    # Merge maneuver-summary features
    summaries = {m: _maneuver_summary(m) for m in maneuvers}
    summary_df = (
        pd.DataFrame.from_dict(summaries, orient="index")
        .reset_index()
        .rename(columns={"index": "maneuver"})
    )
    df = df.merge(summary_df, on="maneuver", how="left")

    # Stable column ordering: ids → inputs → maneuver summary → outputs → status
    leading = [
        "row_id", "maneuver", "maneuver_category", "arm",
        "who_profile", "g_tolerance_multiplier",
        "dehydration_label", "dehydration_level",
        "countermeasures_label",
        "gsuit_max_psi", "gsuit_coverage_fraction",
        "agsm_effectiveness", "pbg_max_mmhg",
        "row_seed",
    ]
    rest = [c for c in df.columns if c not in leading]
    df = df[[c for c in leading if c in df.columns] + rest]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    metadata = {
        "run_id": run_id,
        "master_seed": master_seed,
        "binary_sha256": binary_sha,
        "package_version": getattr(cgem_ext, "__version__", "unknown"),
        "rows_total": int(len(df)),
        "rows_ok": int((df["status"] == "ok").sum()),
        "rows_error": int((df["status"] == "error").sum()),
        "wall_clock_s": round(elapsed, 2),
        "host": platform.node(),
        "python": sys.version.split()[0],
        "smoke": bool(smoke),
        "maneuvers_count": len(maneuvers),
        "arms": list(arms),
        "tier_definitions": {
            "DEHYDRATION_LEVELS": DEHYDRATION_LEVELS,
            "COUNTERMEASURES_LEVELS": COUNTERMEASURES_LEVELS,
            "G_TOLERANCE_TIERS": G_TOLERANCE_TIERS,
            "WHO_PROFILES": WHO_PROFILES,
        },
        "generation_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    metadata_path = output_path.with_suffix(".meta.json")
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str))

    rate = elapsed / max(1, len(df))
    print(
        f"\nWrote {len(df)} rows -> {output_path}\n"
        f"Metadata -> {metadata_path}\n"
        f"Wall clock: {elapsed:.1f}s ({rate:.2f}s/row)\n"
        f"Status: ok={metadata['rows_ok']}, error={metadata['rows_error']}",
        flush=True,
    )
    return metadata


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a synthetic CGEM dataset for the cgem_ext ML layer.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/datasets/cgem_synthetic_v1.parquet"),
        help="Output parquet path (sidecar .meta.json written alongside).",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Small smoke run (5 maneuvers x 2 pilots x cm in {none, agsm} x all dehydration).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Master seed for per-row seeding.")
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Worker count; 0 (default) auto-selects max(1, cpu_count - 1).",
    )
    parser.add_argument(
        "--arms",
        nargs="+",
        default=["standard", "custom"],
        choices=["standard", "custom"],
    )
    parser.add_argument(
        "--maneuvers",
        nargs="*",
        default=None,
        help="Subset of maneuver identifiers (default: all 72).",
    )
    args = parser.parse_args()

    generate(
        output_path=args.output,
        maneuvers=args.maneuvers,
        arms=tuple(args.arms),
        master_seed=args.seed,
        workers=args.workers,
        smoke=args.smoke,
    )


if __name__ == "__main__":
    _cli()
