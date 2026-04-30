"""
CGEM Batch Runner
=================

Runs every registered maneuver in ``aerobatic_profiles.PROFILES`` against
multiple ``PilotConfig`` setups (no countermeasures, G-suit only, AGSM only,
full countermeasures, dehydrated) across all six standard ``who_profile``
subjects, and stores the resulting time-series + event times for downstream
hemodynamic analysis.

Output
------

Results are written to ``data/batch_results/`` as one JSON file per
(maneuver × config × who_profile) and one Parquet rollup ``summary.parquet``.

Run
---

    python run_cgem_batch.py --maneuvers all --who all --configs all
    python run_cgem_batch.py --maneuvers high_g_turn,loop_standard --who 2
"""
from __future__ import annotations

import argparse
import json
import shutil
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from aerobatic_profiles import PROFILES
from cgem_wrapper import CGEMResult, PilotConfig, run_cgem_for_profile

OUT_DIR = Path(__file__).resolve().parent / "data" / "batch_results"


# ---------------------------------------------------------------------------
# Pilot config presets — these are the operationally meaningful states we want
# to compare hemodynamics against, per maneuver.
# ---------------------------------------------------------------------------

CONFIG_PRESETS: Dict[str, PilotConfig] = {
    "no_countermeasures": PilotConfig(
        who_profile=2,
        gsuit_max_psi=0.0, gsuit_coverage_fraction=0.0,
        agsm_effectiveness=0.0, pbg_max_mmhg=0.0,
        seat_tilt_deg=10.0, dehydration_level=0.0,
    ),
    "gsuit_only": PilotConfig(
        who_profile=2,
        gsuit_max_psi=5.5, gsuit_coverage_fraction=0.40,
        agsm_effectiveness=0.0, pbg_max_mmhg=0.0,
        seat_tilt_deg=10.0, dehydration_level=0.0,
    ),
    "agsm_only": PilotConfig(
        who_profile=2,
        gsuit_max_psi=0.0, gsuit_coverage_fraction=0.0,
        agsm_effectiveness=0.7, pbg_max_mmhg=0.0,
        seat_tilt_deg=10.0, dehydration_level=0.0,
    ),
    "full_countermeasures": PilotConfig(
        who_profile=2,
        gsuit_max_psi=5.5, gsuit_coverage_fraction=0.40,
        agsm_effectiveness=0.7, pbg_max_mmhg=30.0,
        seat_tilt_deg=15.0, dehydration_level=0.0,
    ),
    "dehydrated": PilotConfig(
        who_profile=2,
        gsuit_max_psi=5.5, gsuit_coverage_fraction=0.40,
        agsm_effectiveness=0.5, pbg_max_mmhg=20.0,
        seat_tilt_deg=10.0, dehydration_level=0.5,
    ),
}


def _serialize_result(res: CGEMResult) -> Dict:
    """Convert CGEMResult to JSON-friendly dict."""
    return {
        "time_to_greyout_s": res.time_to_greyout_s,
        "time_to_blackout_s": res.time_to_blackout_s,
        "time_to_gloc_s": res.time_to_gloc_s,
        "last_time_s": res.last_time_s,
        "last_g": res.last_g,
        "last_geff": res.last_geff,
        "times_s": res.times_s,
        "g_values": res.g_values,
        "geff_values": res.geff_values,
        "flags_n2": res.flags_n2,
        "flags_ne2": res.flags_ne2,
        "flags_non2": res.flags_non2,
        "c_bank_values": res.c_bank_values,
        "f_con_values": res.f_con_values,
        "f_vis_values": res.f_vis_values,
        "f_bo_values": res.f_bo_values,
        "bo_bank_values": res.bo_bank_values,
        "hlap_values": res.hlap_values,
    }


def _hemodynamic_summary(res: CGEMResult) -> Dict:
    """Extract concise per-run hemodynamic metrics for the rollup table."""
    g = res.g_values or []
    hlap = [v for v in (res.hlap_values or []) if v == v]  # NaN-safe
    fc = [v for v in (res.f_con_values or []) if v == v]
    cb = [v for v in (res.c_bank_values or []) if v == v]
    bo = [v for v in (res.bo_bank_values or []) if v == v]

    n_neg = sum(1 for x in g if x < -0.1)
    n_pos5 = sum(1 for x in g if x >= 5.0)
    n_pos7 = sum(1 for x in g if x >= 7.0)
    return {
        "peak_g": max(g) if g else None,
        "min_g": min(g) if g else None,
        "ms_above_5g": n_pos5,  # one row ≈ 1 ms
        "ms_above_7g": n_pos7,
        "ms_below_0g": n_neg,
        "min_hlap_mmhg": min(hlap) if hlap else None,
        "min_f_con": min(fc) if fc else None,
        "min_c_bank_s": min(cb) if cb else None,
        "min_bo_bank_s": min(bo) if bo else None,
        "time_to_greyout_s": res.time_to_greyout_s,
        "time_to_blackout_s": res.time_to_blackout_s,
        "time_to_gloc_s": res.time_to_gloc_s,
    }


def run_batch(
    maneuver_ids: Iterable[str],
    who_profiles: Iterable[int],
    config_keys: Iterable[str],
    persist_full_series: bool = True,
) -> List[Dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: List[Dict] = []

    for mid in maneuver_ids:
        if mid not in PROFILES:
            print(f"[skip] unknown maneuver: {mid}")
            continue
        for who in who_profiles:
            for cfg_key in config_keys:
                base = CONFIG_PRESETS[cfg_key]
                # Override who_profile but keep the preset's countermeasures
                cfg = PilotConfig(**{**asdict(base), "who_profile": who})

                t0 = time.time()
                try:
                    res, tmp = run_cgem_for_profile(mid, config=cfg)
                except Exception as exc:  # noqa: BLE001
                    print(f"[error] {mid} who={who} cfg={cfg_key}: {exc}")
                    continue
                wall_s = time.time() - t0

                summary = {
                    "maneuver": mid,
                    "who_profile": who,
                    "config": cfg_key,
                    "wall_s": round(wall_s, 3),
                    **_hemodynamic_summary(res),
                }
                rows.append(summary)

                if persist_full_series:
                    out_path = OUT_DIR / f"{mid}__who{who}__{cfg_key}.json"
                    out_path.write_text(
                        json.dumps(
                            {"meta": summary, "series": _serialize_result(res)},
                            default=str,
                        ),
                        encoding="utf-8",
                    )

                # Clean per-run temp dir to avoid /tmp bloat
                shutil.rmtree(tmp, ignore_errors=True)

                print(
                    f"[ok] {mid:32s} who={who} cfg={cfg_key:22s} "
                    f"peak={summary['peak_g']} GLOC={summary['time_to_gloc_s']}"
                )

    return rows


def write_rollup(rows: List[Dict]) -> Path:
    """Write rollup as JSON (always) and Parquet (if pandas+pyarrow available)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "summary.json"
    json_path.write_text(json.dumps(rows, default=str, indent=2), encoding="utf-8")

    try:
        import pandas as pd  # noqa: WPS433
        df = pd.DataFrame(rows)
        parquet_path = OUT_DIR / "summary.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"[rollup] wrote {parquet_path} and {json_path}")
        return parquet_path
    except Exception as exc:  # noqa: BLE001
        print(f"[rollup] pandas/parquet unavailable ({exc}); JSON only at {json_path}")
        return json_path


def _parse_csv(s: str) -> List[str]:
    return [tok.strip() for tok in s.split(",") if tok.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maneuvers", default="all",
                    help='"all" or comma-separated maneuver identifiers')
    ap.add_argument("--who", default="2",
                    help='"all" or comma-separated who_profile values 1..6')
    ap.add_argument("--configs", default="no_countermeasures,full_countermeasures",
                    help='"all" or comma-separated config preset names')
    ap.add_argument("--no-series", action="store_true",
                    help="Skip writing per-run JSON time-series (rollup only)")
    args = ap.parse_args()

    maneuvers: Iterable[str] = (
        list(PROFILES.keys()) if args.maneuvers == "all" else _parse_csv(args.maneuvers)
    )
    who: Iterable[int] = (
        [1, 2, 3, 4, 5, 6] if args.who == "all" else [int(x) for x in _parse_csv(args.who)]
    )
    configs: Iterable[str] = (
        list(CONFIG_PRESETS.keys()) if args.configs == "all" else _parse_csv(args.configs)
    )

    rows = run_batch(maneuvers, who, configs, persist_full_series=not args.no_series)
    write_rollup(rows)


if __name__ == "__main__":
    main()
