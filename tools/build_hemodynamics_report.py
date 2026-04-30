"""
Build per-maneuver hemodynamic analysis report.

Reads data/batch_results/summary.json (rollup from run_cgem_batch.py) and
produces docs/MANEUVER_HEMODYNAMICS.md with:

* Master table: every maneuver, peak G envelope, sustained-G plateau, time
  to greyout/blackout/G-LOC across the 5 pilot configurations.
* Push-pull index: ms_below_0g for maneuvers that include negative-G phases.
* Countermeasure efficacy: G-LOC time delta between no_countermeasures and
  full_countermeasures.
* Per-category sub-sections (championship / military_acm / extreme / conceptual).
* Top-10 G-LOC-prone maneuvers under no countermeasures.

Run:
    python tools/build_hemodynamics_report.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from maneuvers_catalog import CATALOG, ManeuverCategory  # noqa: E402

SUMMARY = ROOT / "data" / "batch_results" / "summary.json"
OUT = ROOT / "docs" / "MANEUVER_HEMODYNAMICS.md"

CONFIG_ORDER = [
    "no_countermeasures",
    "gsuit_only",
    "agsm_only",
    "full_countermeasures",
    "dehydrated",
]


def _fmt_t(t):
    return f"{t:.2f}" if isinstance(t, (int, float)) else "—"


def _fmt_g(g):
    return f"{g:.2f}" if isinstance(g, (int, float)) else "—"


def main() -> None:
    rows = json.loads(SUMMARY.read_text())
    # Index: maneuver -> config -> row
    idx = defaultdict(dict)
    for r in rows:
        idx[r["maneuver"]][r["config"]] = r

    lines: list[str] = []
    lines.append("# Maneuver Hemodynamics — CGEM Cross-Sectional Analysis")
    lines.append("")
    lines.append(
        "This report compares cerebral-perfusion outcomes predicted by CGEM "
        "across every maneuver in `aerobatic_profiles.PROFILES`, evaluated "
        "for the standard midrange male pilot (`who_profile=2`) under five "
        "countermeasure configurations: **no_countermeasures**, **gsuit_only** "
        "(G-suit 5.5 PSI / 40% coverage), **agsm_only** (AGSM effectiveness 0.7), "
        "**full_countermeasures** (G-suit + AGSM + 30 mmHg PBG + 15° seat tilt), "
        "and **dehydrated** (full countermeasures with dehydration_level 0.5 and "
        "reduced AGSM/PBG)."
    )
    lines.append("")
    lines.append(
        "All values are produced by the FAA CGEM Fortran model via "
        "`cgem_wrapper.run_cgem_for_profile()`. Times are in seconds from "
        "maneuver start. Cerebral-flow and HLAP minima reflect the deepest "
        "physiologic excursion observed during the run."
    )
    lines.append("")

    # ---- Top-10 G-LOC prone (no_countermeasures) ----
    lines.append("## Top G-LOC-prone maneuvers (no countermeasures)")
    lines.append("")
    lines.append("| Maneuver | Category | Peak +Gz | t-greyout (s) | t-blackout (s) | t-G-LOC (s) |")
    lines.append("|---|---|---:|---:|---:|---:|")
    no_cm_with_gloc = [
        idx[m]["no_countermeasures"]
        for m in idx
        if "no_countermeasures" in idx[m]
        and idx[m]["no_countermeasures"]["time_to_gloc_s"] is not None
    ]
    no_cm_with_gloc.sort(key=lambda r: r["time_to_gloc_s"])
    for r in no_cm_with_gloc:
        meta = CATALOG.get(r["maneuver"])
        cat = meta.category.value if meta else ""
        lines.append(
            f"| `{r['maneuver']}` | {cat} | "
            f"{_fmt_g(r['peak_g'])} | {_fmt_t(r['time_to_greyout_s'])} | "
            f"{_fmt_t(r['time_to_blackout_s'])} | **{_fmt_t(r['time_to_gloc_s'])}** |"
        )
    lines.append("")

    # ---- Countermeasure efficacy ----
    lines.append("## Countermeasure efficacy")
    lines.append("")
    lines.append(
        "For each maneuver that triggers G-LOC without countermeasures, "
        "this table shows whether full countermeasures prevent G-LOC entirely "
        "or merely delay it."
    )
    lines.append("")
    lines.append("| Maneuver | t-G-LOC no-CM (s) | t-G-LOC full-CM (s) | t-G-LOC dehydrated (s) | Δ no-CM → full-CM |")
    lines.append("|---|---:|---:|---:|---:|")
    for r in no_cm_with_gloc:
        m = r["maneuver"]
        full_cm = idx[m].get("full_countermeasures", {}).get("time_to_gloc_s")
        dehyd = idx[m].get("dehydrated", {}).get("time_to_gloc_s")
        if full_cm is None and r["time_to_gloc_s"] is not None:
            delta = "**prevented**"
        elif full_cm is not None and r["time_to_gloc_s"] is not None:
            delta = f"+{full_cm - r['time_to_gloc_s']:+.2f}"
        else:
            delta = "—"
        lines.append(
            f"| `{m}` | {_fmt_t(r['time_to_gloc_s'])} | {_fmt_t(full_cm)} | "
            f"{_fmt_t(dehyd)} | {delta} |"
        )
    lines.append("")

    # ---- Push-pull index ----
    lines.append("## Push-pull stress (ms below 0 G)")
    lines.append("")
    lines.append(
        "Maneuvers with the largest negative-G exposure (cumulative ms with "
        "Nz < -0.1) are the operational worst case for push-pull cerebral "
        "perfusion deficit when followed by a positive pull."
    )
    lines.append("")
    lines.append("| Maneuver | Category | ms below 0 G | Min HLAP (mmHg) | Min F_con | Min c_bank (s) |")
    lines.append("|---|---|---:|---:|---:|---:|")
    pushpull = [
        idx[m]["no_countermeasures"] for m in idx
        if idx[m].get("no_countermeasures", {}).get("ms_below_0g", 0) > 0
    ]
    pushpull.sort(key=lambda r: -r["ms_below_0g"])
    for r in pushpull[:20]:
        meta = CATALOG.get(r["maneuver"])
        cat = meta.category.value if meta else ""
        lines.append(
            f"| `{r['maneuver']}` | {cat} | {r['ms_below_0g']} | "
            f"{_fmt_g(r['min_hlap_mmhg'])} | {_fmt_g(r['min_f_con'])} | "
            f"{_fmt_g(r['min_c_bank_s'])} |"
        )
    lines.append("")

    # ---- Per-category breakdowns ----
    cat_to_maneuvers: dict[str, list[str]] = defaultdict(list)
    for ident, meta in CATALOG.items():
        cat_to_maneuvers[meta.category.value].append(ident)

    lines.append("## Per-category cross-config table")
    lines.append("")
    lines.append(
        "Each row gives the time-to-G-LOC (in seconds) across the five "
        "configurations. `—` means no G-LOC was triggered. **Bold** entries "
        "indicate G-LOC events under that configuration."
    )
    lines.append("")
    for cat in ["championship", "military_acm", "extreme_post_stall", "conceptual", "training"]:
        items = cat_to_maneuvers.get(cat, [])
        if not items:
            continue
        lines.append(f"### {cat.replace('_', ' ').title()}")
        lines.append("")
        header = "| Maneuver | Peak ±Gz | "
        header += " | ".join(c.replace("_", " ") for c in CONFIG_ORDER)
        header += " |"
        sep = "|---|---:|" + "---:|" * len(CONFIG_ORDER)
        lines.append(header)
        lines.append(sep)
        for ident in sorted(items):
            meta = CATALOG[ident]
            row_parts = [f"`{ident}`",
                         f"+{meta.peak_pos_gz:.1f} / {meta.peak_neg_gz:+.1f}"]
            for cfg in CONFIG_ORDER:
                r = idx.get(ident, {}).get(cfg)
                if r is None:
                    row_parts.append("—")
                else:
                    t = r["time_to_gloc_s"]
                    if t is None:
                        row_parts.append("—")
                    else:
                        row_parts.append(f"**{t:.2f}**")
            lines.append("| " + " | ".join(row_parts) + " |")
        lines.append("")

    # ---- Sustained-G endurance ----
    lines.append("## Sustained-G endurance maneuvers")
    lines.append("")
    lines.append(
        "Maneuvers with explicit sustained-G plateaus (`sustained_gz` set in "
        "the catalog). These are the principal AGSM-endurance and "
        "G-tolerance-test profiles."
    )
    lines.append("")
    lines.append("| Maneuver | Plateau +Gz | Plateau (s) | t-G-LOC no-CM | t-G-LOC full-CM | Min c_bank (no-CM) |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    sustained = [m for m in CATALOG.values() if m.sustained_gz is not None]
    sustained.sort(key=lambda m: -m.sustained_gz)
    for m in sustained:
        no_cm_r = idx.get(m.identifier, {}).get("no_countermeasures", {})
        full_r = idx.get(m.identifier, {}).get("full_countermeasures", {})
        lines.append(
            f"| `{m.identifier}` | {m.sustained_gz:.1f} | "
            f"{m.sustained_duration_s:.1f} | "
            f"{_fmt_t(no_cm_r.get('time_to_gloc_s'))} | "
            f"{_fmt_t(full_r.get('time_to_gloc_s'))} | "
            f"{_fmt_g(no_cm_r.get('min_c_bank_s'))} |"
        )
    lines.append("")

    # ---- Methodology / caveats ----
    lines.append("## Methodology and caveats")
    lines.append("")
    lines.append(
        "- **Pilot model.** All runs use `who_profile=2` (standard midrange "
        "male). Use `--who all` in `run_cgem_batch.py` to expand across "
        "subjects 1–6. The CGEM Fortran subject database (set via `who`) "
        "overrides custom physiology when a standard profile is selected."
    )
    lines.append(
        "- **Onset-rate fidelity.** Snap rolls and Cobra-class spikes are "
        "represented as 100–250 ms cells, which translates to onset rates "
        "30–60 G/s in CGEM. The model is validated through ~10 G/s onset "
        "(Copeland & Whinnery 2023, DOI:10.21949/1524446); behaviour above "
        "that ceiling is extrapolated."
    )
    lines.append(
        "- **Scalar Nz only.** CGEM models +Gz / −Gz only. Lateral (Gy) and "
        "longitudinal (Gx) loads from snap rolls, flat spins, and "
        "Lomcovák-class tumbling are not represented; the +Gz time series "
        "underestimates true physiologic stress for those maneuvers."
    )
    lines.append(
        "- **Push-pull effect.** CGEM does include a push-pull delay model "
        "(transient HR-response delay after −Gz). Rankings here capture the "
        "model's prediction; field measurements from Banks et al. and the "
        "FAA OAM tech reports should be used to calibrate operational "
        "thresholds."
    )
    lines.append(
        "- **Profile provenance.** New profiles added in this extension were "
        "constructed from kinematic-phase reconstruction calibrated against "
        "the canonical CGEM samples and standard aerobatic / fighter-doctrine "
        "references (FAI/CIVA Aresti catalogue, Shaw 1985, Newman & Callister "
        "2009 DOI:10.3357/asem.2361.2009). They are not flight-test telemetry. "
        "See `tools/extension_profiles.py` for per-maneuver source notes."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_Generated by `tools/build_hemodynamics_report.py` from `{SUMMARY.relative_to(ROOT)}`._")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote {OUT.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
