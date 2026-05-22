"""Export `maneuvers_catalog.CATALOG` + Aerobatics_sample_inputs/*.txt
to a single JSON manifest consumed by the frontend at build time.

Output: frontend/src/data/maneuvers.json
Run:    python3 scripts/export_maneuvers_json.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from maneuvers_catalog import CATALOG  # noqa: E402
from attitude_synthesis import attach_attitude_to_samples  # noqa: E402

INPUTS_DIR = REPO_ROOT / "Aerobatics_sample_inputs"
OUTPUT = REPO_ROOT / "frontend" / "src" / "data" / "maneuvers.json"


def parse_txt(path: Path) -> list[dict[str, float]]:
    """Parse a `(g_value, duration_ms)` profile file. First line = row count."""
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    if not lines:
        return []
    samples: list[dict[str, float]] = []
    for ln in lines[1:]:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) != 2:
            continue
        try:
            nz = float(parts[0])
            dur_ms = float(parts[1])
        except ValueError:
            continue
        samples.append({"nz": nz, "duration_ms": dur_ms})
    return samples


def candidate_filenames(identifier: str, category: str) -> list[Path]:
    """Some catalog identifiers don't perfectly match filenames (military ACM
    entries drop the `military_` prefix in the catalog id but keep it in the
    .txt name; extreme post-stall and conceptual likewise vary)."""
    stems = {
        identifier,
        identifier.replace("_", ""),
        identifier.replace("_", "").lower(),
    }
    if category == "military_acm":
        stems.add(f"military_{identifier}")
        # Reverse-mapping for naming quirks in the txt corpus
        rev = {
            "corner_velocity_turn": "military_corner_velocity_turn",
            "defensive_break_9g": "military_defensive_break_9g",
            "defensive_break_chaff_flare": "military_defensive_break_chaff_flare",
            "defensive_jink": "military_defensive_jink",
            "defensive_spiral": "military_defensive_spiral",
            "flat_scissors_defensive": "military_flat_scissors",
            "helicopter_bugout": "military_helicopter_bugout",
            "high_yoyo_offensive": "military_high_yoyo",
            "lag_pursuit_roll": "military_lag_pursuit_roll",
            "last_ditch_break": "military_last_ditch_break",
            "low_yoyo_offensive": "military_low_yoyo",
            "push_pull_missile_evasion": "military_push_pull_evasion",
            "rate_fight_sustained": "military_rate_fight",
            "rolling_scissors": "military_rolling_scissors",
            "slatted_high_aoa_turn": "military_slatted_high_aoa_turn",
            "strike_turn_strafing_pullout": "military_strike_pullout",
            "sustained_9g_turn": "military_sustained_9g_turn",
            "vertical_climb_missile_evasion": "military_vertical_climb_evasion",
        }
        if identifier in rev:
            stems.add(rev[identifier])
        stems.add(f"military_combat_{identifier}")
    if identifier == "half_vert_roll_neg_pull":
        stems.add("halfverticalrollwnegpullout")
    if identifier == "outside_inside_vert8":
        stems.add("outsideinsidevertical8")
    return [INPUTS_DIR / f"{s}.txt" for s in stems]


def main() -> None:
    records: list[dict] = []
    missing: list[str] = []
    for identifier, meta in sorted(CATALOG.items()):
        samples: list[dict[str, float]] = []
        filename = ""
        for c in candidate_filenames(identifier, meta.category.value):
            if c.exists():
                samples = parse_txt(c)
                filename = c.name
                break
        if not samples:
            missing.append(identifier)
        enriched_samples = attach_attitude_to_samples(
            meta.identifier,
            meta.category.value,
            meta.aresti_family,
            meta.description,
            samples,
        )
        records.append({
            "id": meta.identifier,
            "filename": filename,
            "category": meta.category.value,
            "description": meta.description,
            "aircraft": meta.aircraft,
            "peak_pos_gz": meta.peak_pos_gz,
            "peak_neg_gz": meta.peak_neg_gz,
            "onset_rate_g_per_s": meta.onset_rate_g_per_s,
            "total_duration_s": meta.total_duration_s,
            "aresti_family": meta.aresti_family,
            "aresti_code": meta.aresti_code,
            "sustained_gz": meta.sustained_gz,
            "sustained_duration_s": meta.sustained_duration_s,
            "hemodynamic_concern": meta.hemodynamic_concern,
            "source": meta.source,
            "tags": list(meta.tags),
            "samples": enriched_samples,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"wrote {len(records)} maneuvers to {OUTPUT}")
    if missing:
        print(f"warning: {len(missing)} catalog entries had no .txt profile:")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    main()
