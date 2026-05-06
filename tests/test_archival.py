"""Schema and provenance tests for the archival validation cohort.

Every row of ``data/archival/centrifuge_tables.parquet`` must carry a
verifiable source citation, DOI, table-of-record reference, transcriber,
and transcription date. Tests below enforce those invariants so a
reviewer can audit any row back to its primary source.

Tests are gated by the presence of the parquet (regenerable via
``python -m scripts.extract_archival_tables``); all other tests are
pure-Python and run in CI under ``not needs_cgem_binary``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REQUIRED_COLUMNS = {
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
    "transcribed_on",
    "transcribed_by",
}

ALLOWED_RECORD_TYPES = {"aggregated_summary", "per_subject"}
ALLOWED_PHASES = {"A", "B"}
ALLOWED_COUNTERMEASURE_STATES = {
    "none (relaxed, no AGSM, no G-suit, no PBG)",
    "AGSM only",
    "G-suit only",
    "AGSM + G-suit",
    "AGSM + G-suit + PBG",
    "AGSM + G-suit + PBG + posterior tilt",
}


@pytest.fixture(scope="module")
def archival_df() -> pd.DataFrame:
    parquet_path = (
        Path(__file__).parent.parent / "data" / "archival" / "centrifuge_tables.parquet"
    )
    if not parquet_path.exists():
        pytest.skip(
            "archival cohort parquet not found; run "
            "`python -m scripts.extract_archival_tables`"
        )
    return pd.read_parquet(parquet_path)


def test_archival_required_columns_present(archival_df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(archival_df.columns)
    assert not missing, f"Required columns missing: {missing}"


def test_archival_record_id_unique(archival_df: pd.DataFrame) -> None:
    assert archival_df["record_id"].is_unique, "record_id must be unique"


def test_archival_record_type_valid(archival_df: pd.DataFrame) -> None:
    bad = set(archival_df["record_type"].unique()) - ALLOWED_RECORD_TYPES
    assert not bad, f"Invalid record_type values: {bad}"


def test_archival_phase_valid(archival_df: pd.DataFrame) -> None:
    bad = set(archival_df["phase"].unique()) - ALLOWED_PHASES
    assert not bad, f"Invalid phase values: {bad}"


def test_archival_countermeasure_state_valid(archival_df: pd.DataFrame) -> None:
    bad = set(archival_df["countermeasure_state"].unique()) - ALLOWED_COUNTERMEASURE_STATES
    assert not bad, (
        f"Unexpected countermeasure_state values: {bad}. Update "
        f"ALLOWED_COUNTERMEASURE_STATES if a new tier is added."
    )


def test_archival_doi_format(archival_df: pd.DataFrame) -> None:
    """Every row must carry a non-empty DOI matching the standard
    10.<registrant>/<suffix> format."""
    import re

    pattern = re.compile(r"^10\.\d{4,9}/[^\s]+$")
    bad = []
    for record_id, doi in zip(
        archival_df["record_id"], archival_df["source_doi"], strict=True
    ):
        if not isinstance(doi, str) or not pattern.match(doi):
            bad.append((record_id, doi))
    assert not bad, f"Invalid or missing DOIs: {bad[:3]}..."


def test_archival_n_subjects_positive(archival_df: pd.DataFrame) -> None:
    assert (archival_df["n_subjects_total"] > 0).all()


def test_archival_endpoint_known(archival_df: pd.DataFrame) -> None:
    """Every row's endpoint must be one of the canonical CGEM-mappable
    quantities. New endpoints require explicit allowlist updates so the
    cite chain stays auditable."""
    allowed_endpoints = {
        "time_to_loss_of_consciousness",
        "duration_of_absolute_incapacitation",
        "time_to_blackout",
        "time_to_greyout",
    }
    bad = set(archival_df["endpoint"].unique()) - allowed_endpoints
    assert not bad, f"Unrecognised endpoints: {bad}"


def test_archival_transcribed_on_iso_date(archival_df: pd.DataFrame) -> None:
    """transcribed_on must be an ISO-format date string (YYYY-MM-DD)."""
    import re

    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    bad = [
        (rid, t)
        for rid, t in zip(
            archival_df["record_id"], archival_df["transcribed_on"], strict=True
        )
        if not (isinstance(t, str) and pattern.match(t))
    ]
    assert not bad, f"Invalid transcribed_on values: {bad[:3]}..."


def test_archival_phase_a_minimum_records(archival_df: pd.DataFrame) -> None:
    """Phase A is the FAA AM-23/6 reproduction of Whinnery et al.
    aggregated tables. The minimum is 13 records (8 WF2013 + 5 WFR2014).
    Lower counts indicate a transcription failure."""
    phase_a = archival_df[archival_df["phase"] == "A"]
    assert len(phase_a) >= 13, (
        f"Phase A cohort under-populated: {len(phase_a)} < 13 records. "
        f"See data/archival/PROVENANCE.md."
    )


def test_archival_phase_b_minimum_records(archival_df: pd.DataFrame) -> None:
    """Phase B is the scite-full-text-derived narrow-range and threshold
    rows from the upstream BMC papers. Minimum 10 records (5 WFR2014
    narrow-range bands + 5 WF2013 abstract anchors). Lower counts
    indicate that the Phase B extraction has regressed."""
    phase_b = archival_df[archival_df["phase"] == "B"]
    assert len(phase_b) >= 10, (
        f"Phase B cohort under-populated: {len(phase_b)} < 10 records. "
        f"See data/archival/PROVENANCE.md."
    )


def test_archival_endpoints_match_cgem_outcomes(archival_df: pd.DataFrame) -> None:
    """The two endpoint families currently in the cohort must populate
    their respective outcome columns mutually exclusively (a row should
    not carry both a time_to_gloc and a duration_incap mean)."""
    has_gloc = archival_df["time_to_gloc_s_mean"].notna()
    has_incap = archival_df["duration_incap_s_mean"].notna()
    overlap = (has_gloc & has_incap).sum()
    assert overlap == 0, (
        f"{overlap} rows carry both time_to_gloc_s_mean and "
        "duration_incap_s_mean; the cohort is supposed to keep the two "
        "endpoints in separate rows."
    )
