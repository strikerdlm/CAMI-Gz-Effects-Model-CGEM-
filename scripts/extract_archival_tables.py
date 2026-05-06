"""Build the archival-validation cohort parquet from open-source centrifuge
references.

Phase A cohort (this script):
- Whinnery & Forster (2013), "The +Gz-induced loss of consciousness curve",
  *Extreme Physiology and Medicine* 2:19, doi:10.1186/2046-7648-2-19
  (open access, CC-BY). Pooled time-to-LOC by acceleration onset rate,
  n = 729 USN + USAF participants. Source: FAA technical report
  DOT/FAA/AM-23/6 §"Validation" Figure 1, which reproduces Whinnery &
  Forster's Figure 2 numerically.
- Whinnery, Forster & Rogers (2014), "The +Gz recovery of consciousness
  curve", *Extreme Physiology and Medicine* 3:9, doi:10.1186/2046-7648-3-9
  (open access, CC-BY). Pooled duration-of-absolute-incapacitation by
  acceleration offset rate, n = 715 USN + USAF participants. Source:
  FAA technical report DOT/FAA/AM-23/6 §"Validation" Figure 2.

Phase B cohort (deferred, see ``data/archival/PROVENANCE.md``):
- Per-subject records extracted directly from the upstream open-access
  papers (BMC Extreme Physiology and Medicine), once subject-level data
  are confirmed accessible. Phase A consists of the aggregated /
  summary-statistic rows that *FAA AM-23/6* reproduces from the upstream
  tables; this gives 13 aggregated records that anchor the H6 archival
  validation cohort while Phase B per-subject extraction is in progress.

The script is deterministic (no network calls, no randomness). Re-running
``python -m scripts.extract_archival_tables`` against the same source
markdown produces an identical parquet. The provenance audit is in
``data/archival/PROVENANCE.md``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

# ── Phase A: Whinnery & Forster (2013) Figure-2 data, reproduced as
# ── FAA AM-23/6 Figure 1.

WF2013_ONSET_RATE_TABLE: list[dict] = [
    # record_id schema: WF2013-{onset_rate_in_centi_g_per_s}.
    # Mean ± SD time-to-loss-of-consciousness for relaxed participants
    # without anti-G countermeasures.
    {
        "record_id": "WF2013-005",
        "onset_rate_g_per_s": 0.05,
        "time_to_loc_s_mean": 95.0,
        "time_to_loc_s_sd": 5.0,
    },
    {
        "record_id": "WF2013-010",
        "onset_rate_g_per_s": 0.1,
        "time_to_loc_s_mean": 85.0,
        "time_to_loc_s_sd": 10.0,
    },
    {
        "record_id": "WF2013-020",
        "onset_rate_g_per_s": 0.2,
        "time_to_loc_s_mean": 70.0,
        "time_to_loc_s_sd": 15.0,
    },
    {
        "record_id": "WF2013-050",
        "onset_rate_g_per_s": 0.5,
        "time_to_loc_s_mean": 20.0,
        "time_to_loc_s_sd": 5.0,
    },
    {
        "record_id": "WF2013-100",
        "onset_rate_g_per_s": 1.0,
        "time_to_loc_s_mean": 12.0,
        "time_to_loc_s_sd": 3.0,
    },
    {
        "record_id": "WF2013-200",
        "onset_rate_g_per_s": 2.0,
        "time_to_loc_s_mean": 9.0,
        "time_to_loc_s_sd": 2.0,
    },
    {
        "record_id": "WF2013-500",
        "onset_rate_g_per_s": 5.0,
        "time_to_loc_s_mean": 8.0,
        "time_to_loc_s_sd": 3.0,
    },
    {
        "record_id": "WF2013-1000",
        "onset_rate_g_per_s": 10.0,
        "time_to_loc_s_mean": 9.0,
        "time_to_loc_s_sd": 4.0,
    },
]

# ── Phase A: Whinnery, Forster & Rogers (2014) Table-2 data, reproduced
# ── as FAA AM-23/6 Figure 2.

WFR2014_OFFSET_RATE_TABLE: list[dict] = [
    {
        "record_id": "WFR2014-020",
        "offset_rate_g_per_s": 0.2,
        "duration_incap_s_mean": 13.6,
        "duration_incap_s_sd": None,
    },
    {
        "record_id": "WFR2014-040",
        "offset_rate_g_per_s": 0.4,
        "duration_incap_s_mean": 12.5,
        "duration_incap_s_sd": None,
    },
    {
        "record_id": "WFR2014-060",
        "offset_rate_g_per_s": 0.6,
        "duration_incap_s_mean": 10.3,
        "duration_incap_s_sd": None,
    },
    {
        "record_id": "WFR2014-080",
        "offset_rate_g_per_s": 0.8,
        "duration_incap_s_mean": 8.6,
        "duration_incap_s_sd": None,
    },
    {
        "record_id": "WFR2014-100",
        "offset_rate_g_per_s": 1.0,
        "duration_incap_s_mean": 7.7,
        "duration_incap_s_sd": None,
    },
]

# ── Phase B: WFR2014 Table 2 narrow-range bands recovered from scite
# ── full-text excerpts (DOI 10.1186/2046-7648-3-9, "Methods" /
# ── "Results" sections). These are *additional stratifications* of the
# ── same upstream cohort that FAA AM-23/6 summarised in 5 rows; the
# ── narrow ranges report mean ± SD that the FAA Figure 2 reproduced
# ── with SDs omitted.

WFR2014_NARROW_OFFSET_RATE_TABLE: list[dict] = [
    {
        "record_id": "WFR2014B-NARROW-0p1-0p499",
        "offset_rate_g_per_s_low": 0.1,
        "offset_rate_g_per_s_high": 0.499,
        "duration_incap_s_mean": 13.61,
        "duration_incap_s_sd": 5.26,
        "narrow_range_label": "0.1 to 0.499 G/s",
    },
    {
        "record_id": "WFR2014B-NARROW-0p5-0p599",
        "offset_rate_g_per_s_low": 0.5,
        "offset_rate_g_per_s_high": 0.599,
        "duration_incap_s_mean": 14.13,
        "duration_incap_s_sd": 6.00,
        "narrow_range_label": "0.5 to 0.599 G/s",
    },
    {
        "record_id": "WFR2014B-NARROW-2p0-2p99",
        "offset_rate_g_per_s_low": 2.0,
        "offset_rate_g_per_s_high": 2.99,
        "duration_incap_s_mean": 7.96,
        "duration_incap_s_sd": 3.38,
        "narrow_range_label": "2.0 to 2.99 G/s",
    },
    {
        "record_id": "WFR2014B-NARROW-3p0-8p0",
        "offset_rate_g_per_s_low": 3.0,
        "offset_rate_g_per_s_high": 8.0,
        "duration_incap_s_mean": 7.91,
        "duration_incap_s_sd": 2.43,
        "narrow_range_label": "3.0 to 8.0 G/s",
    },
    {
        "record_id": "WFR2014B-COMBINED-ge0p6",
        "offset_rate_g_per_s_low": 0.6,
        "offset_rate_g_per_s_high": 8.0,
        "duration_incap_s_mean": 8.53,
        "duration_incap_s_sd": 0.82,
        "narrow_range_label": "≥ 0.6 G/s combined",
    },
]

# ── Phase B: Whinnery & Forster (2013) abstract-derived summary anchors.
# ── These come from the published Abstract Results paragraph of DOI
# ── 10.1186/2046-7648-2-19. They report stratification thresholds that
# ── the FAA report's 8-row Figure 1 does not encode at the same
# ── granularity.

WF2013_THRESHOLD_TABLE: list[dict] = [
    {
        "record_id": "WF2013B-RAPID-ONSET-GE-1",
        "onset_rate_g_per_s_low": 1.0,
        "onset_rate_g_per_s_high": 10.0,
        "time_to_loc_s_mean": 9.10,
        "time_to_loc_s_sd": None,
        "stratification_label": "onset ≥ 1.0 G/s (rapid)",
        "summary_kind": "stratification_mean",
    },
    {
        "record_id": "WF2013B-GRADUAL-ONSET-LE-0p2",
        "onset_rate_g_per_s_low": 0.05,
        "onset_rate_g_per_s_high": 0.2,
        "time_to_loc_s_mean": 74.41,
        "time_to_loc_s_sd": None,
        "stratification_label": "onset ≤ 0.2 G/s (gradual)",
        "summary_kind": "stratification_mean",
    },
    {
        "record_id": "WF2013B-RAPID-GZ-GE-7",
        "g_peak_abs_low": 7.0,
        "g_peak_abs_high": 11.0,
        "time_to_loc_s_mean": 9.65,
        "time_to_loc_s_sd": None,
        "stratification_label": "Gz ≥ +7 Gz (rapid onset)",
        "summary_kind": "stratification_mean",
    },
    {
        "record_id": "WF2013B-MIN-GZ-THRESHOLD",
        "g_peak_abs_threshold": 4.7,
        "stratification_label": "minimum +Gz threshold for G-LOC",
        "summary_kind": "threshold_value",
        "time_to_loc_s_mean": None,
        "time_to_loc_s_sd": None,
    },
    {
        "record_id": "WF2013B-MIN-LOCINDTI",
        "time_to_loc_s_mean": 5.0,
        "time_to_loc_s_sd": None,
        "stratification_label": "minimum observed LOCINDTI across all exposures",
        "summary_kind": "threshold_value",
    },
]

# ── Common metadata applied row-wise during build.

WF2013_METADATA = {
    "source_id": "WF2013",
    "source_citation": (
        "Whinnery JE, Forster EM. The +Gz-induced loss of consciousness "
        "curve. Extreme Physiol Med. 2013;2(1):19."
    ),
    "source_doi": "10.1186/2046-7648-2-19",
    "source_table": "Figure 2 (reproduced as Figure 1 of FAA AM-23/6)",
    "n_subjects_total": 729,
    "subject_population": (
        "USN + USAF participants, predominantly male, predominantly "
        "USN/USAF aircrew and aircrew candidates."
    ),
    "countermeasure_state": "none (relaxed, no AGSM, no G-suit, no PBG)",
    "endpoint": "time_to_loss_of_consciousness",
    "g_plateau_assumption": "9.4 G experimental ceiling",
    "seat_tilt_deg": 10.0,
    "record_type": "aggregated_summary",
}

WFR2014_METADATA = {
    "source_id": "WFR2014",
    "source_citation": (
        "Whinnery JE, Forster EM, Rogers PB. The +Gz recovery of "
        "consciousness curve. Extreme Physiol Med. 2014;3:9."
    ),
    "source_doi": "10.1186/2046-7648-3-9",
    "source_table": "Table 2 (reproduced as Figure 2 of FAA AM-23/6)",
    "n_subjects_total": 715,
    "subject_population": (
        "USN + USAF participants, predominantly male; superset of the "
        "Whinnery & Forster (2013) cohort."
    ),
    "countermeasure_state": "none (relaxed, no AGSM, no G-suit, no PBG)",
    "endpoint": "duration_of_absolute_incapacitation",
    "g_plateau_assumption": "9.4 G experimental ceiling, held 1 s at +Gz of LOC",
    "seat_tilt_deg": 10.0,
    "record_type": "aggregated_summary",
}

PROVENANCE_TIMESTAMP = date(2026, 5, 6).isoformat()
TRANSCRIBER = "Diego Malpica (via Claude Code, OSF amendment 2026-05-06)"


def build() -> pd.DataFrame:
    """Build the archival cohort DataFrame.

    Returns a DataFrame with one row per archival record. Phase A rows
    are the aggregated WF2013 + WFR2014 tables; Phase B (per-subject
    extraction) is deferred and not returned here.
    """
    rows: list[dict] = []

    for entry in WF2013_ONSET_RATE_TABLE:
        rows.append(
            {
                **WF2013_METADATA,
                **entry,
                "phase": "A",
                "transcribed_on": PROVENANCE_TIMESTAMP,
                "transcribed_by": TRANSCRIBER,
                # Map to CGEM input-space columns where unambiguous.
                "dgdt_max_g_per_s": entry["onset_rate_g_per_s"],
                # G-peak is bounded by the experimental ceiling; the
                # study reports time-to-LOC as a pooled outcome at the
                # specified onset rate, plateau is at LOC induction.
                "g_peak_abs": None,
                "profile_duration_s": None,
                # Outcome columns aligned to CGEM target naming.
                "time_to_gloc_s_mean": entry["time_to_loc_s_mean"],
                "time_to_gloc_s_sd": entry["time_to_loc_s_sd"],
                "duration_incap_s_mean": None,
                "duration_incap_s_sd": None,
            }
        )

    for entry in WFR2014_OFFSET_RATE_TABLE:
        rows.append(
            {
                **WFR2014_METADATA,
                **entry,
                "phase": "A",
                "transcribed_on": PROVENANCE_TIMESTAMP,
                "transcribed_by": TRANSCRIBER,
                "dgdt_max_g_per_s": None,
                "g_peak_abs": None,
                "profile_duration_s": None,
                "time_to_gloc_s_mean": None,
                "time_to_gloc_s_sd": None,
                "duration_incap_s_mean": entry["duration_incap_s_mean"],
                "duration_incap_s_sd": entry.get("duration_incap_s_sd"),
            }
        )

    # Phase B: WFR2014 narrow-range Table 2 rows (5 additional rows).
    # These rows have an offset-rate *band* rather than a point value;
    # we keep offset_rate_g_per_s as the band mid-point for downstream
    # consumers and add the explicit low/high columns.
    for entry in WFR2014_NARROW_OFFSET_RATE_TABLE:
        midpoint = (
            entry["offset_rate_g_per_s_low"] + entry["offset_rate_g_per_s_high"]
        ) / 2.0
        rows.append(
            {
                **WFR2014_METADATA,
                "record_id": entry["record_id"],
                "phase": "B",
                "transcribed_on": PROVENANCE_TIMESTAMP,
                "transcribed_by": TRANSCRIBER,
                "offset_rate_g_per_s": midpoint,
                "offset_rate_g_per_s_low": entry["offset_rate_g_per_s_low"],
                "offset_rate_g_per_s_high": entry["offset_rate_g_per_s_high"],
                "narrow_range_label": entry["narrow_range_label"],
                "dgdt_max_g_per_s": None,
                "g_peak_abs": None,
                "profile_duration_s": None,
                "time_to_gloc_s_mean": None,
                "time_to_gloc_s_sd": None,
                "duration_incap_s_mean": entry["duration_incap_s_mean"],
                "duration_incap_s_sd": entry["duration_incap_s_sd"],
            }
        )

    # Phase B: WF2013 abstract-derived summary anchors (5 additional
    # threshold / stratification rows). Both abstract anchors and
    # threshold values are recorded so downstream consumers can audit
    # the H6 mapping rules against the upstream paper directly.
    for entry in WF2013_THRESHOLD_TABLE:
        rows.append(
            {
                **WF2013_METADATA,
                "record_id": entry["record_id"],
                "phase": "B",
                "transcribed_on": PROVENANCE_TIMESTAMP,
                "transcribed_by": TRANSCRIBER,
                "onset_rate_g_per_s": (
                    (
                        entry.get("onset_rate_g_per_s_low", 0.0)
                        + entry.get("onset_rate_g_per_s_high", 0.0)
                    )
                    / 2.0
                    if "onset_rate_g_per_s_low" in entry
                    else None
                ),
                "onset_rate_g_per_s_low": entry.get("onset_rate_g_per_s_low"),
                "onset_rate_g_per_s_high": entry.get("onset_rate_g_per_s_high"),
                "g_peak_abs_low": entry.get("g_peak_abs_low"),
                "g_peak_abs_high": entry.get("g_peak_abs_high"),
                "g_peak_abs_threshold": entry.get("g_peak_abs_threshold"),
                "stratification_label": entry["stratification_label"],
                "summary_kind": entry["summary_kind"],
                "dgdt_max_g_per_s": None,
                "g_peak_abs": None,
                "profile_duration_s": None,
                "time_to_loc_s_mean": entry["time_to_loc_s_mean"],
                "time_to_loc_s_sd": entry["time_to_loc_s_sd"],
                "time_to_gloc_s_mean": entry["time_to_loc_s_mean"],
                "time_to_gloc_s_sd": entry["time_to_loc_s_sd"],
                "duration_incap_s_mean": None,
                "duration_incap_s_sd": None,
            }
        )

    df = pd.DataFrame(rows)
    # Stable column order for downstream readers.
    column_order = [
        "record_id",
        "source_id",
        "source_citation",
        "source_doi",
        "source_table",
        "phase",
        "record_type",
        "n_subjects_total",
        "subject_population",
        "countermeasure_state",
        "endpoint",
        "g_plateau_assumption",
        "seat_tilt_deg",
        "onset_rate_g_per_s",
        "onset_rate_g_per_s_low",
        "onset_rate_g_per_s_high",
        "offset_rate_g_per_s",
        "offset_rate_g_per_s_low",
        "offset_rate_g_per_s_high",
        "narrow_range_label",
        "g_peak_abs_low",
        "g_peak_abs_high",
        "g_peak_abs_threshold",
        "stratification_label",
        "summary_kind",
        "dgdt_max_g_per_s",
        "g_peak_abs",
        "profile_duration_s",
        "time_to_loc_s_mean",
        "time_to_loc_s_sd",
        "time_to_gloc_s_mean",
        "time_to_gloc_s_sd",
        "duration_incap_s_mean",
        "duration_incap_s_sd",
        "transcribed_on",
        "transcribed_by",
    ]
    # Add any missing columns as None for stability.
    for col in column_order:
        if col not in df.columns:
            df[col] = None
    return df.loc[:, column_order]


def main() -> None:
    out = Path("data") / "archival" / "centrifuge_tables.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_parquet(out, index=False)
    print(
        f"Wrote {len(df)} archival records to {out} "
        f"({df['source_id'].value_counts().to_dict()})"
    )


if __name__ == "__main__":
    main()
