"""Unit tests for the synthetic CGEM dataset generator and splitters.

These tests do **not** invoke the Fortran binary in the splitter checks
(they synthesise small fixture DataFrames). The smoke run that exercises
the full generator is gated by ``needs_cgem_binary`` so CI without the
binary still passes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ──────────────────────────────────────────────────────────────────────
# Splitter tests — synthetic fixture, no CGEM binary needed
# ──────────────────────────────────────────────────────────────────────


def _fixture_df(rows_per_category: dict[str, int]) -> pd.DataFrame:
    """Build a small DataFrame with deterministic per-row metadata."""
    rows = []
    rid = 0
    for category, n in rows_per_category.items():
        for i in range(n):
            rows.append(
                {
                    "row_id": f"{category}_{i}",
                    "maneuver": f"{category}_maneuver_{i % 3}",
                    "maneuver_category": category,
                    "status": "ok",
                    "time_to_gloc_s": 5.0 + i * 0.1,
                }
            )
            rid += 1
    return pd.DataFrame(rows)


def test_stratified_split_shapes():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 30, "military_acm": 20, "extreme_post_stall": 10})
    sp = stratified_split(df, seed=0, train_frac=0.7, val_frac=0.15, test_frac=0.15)

    assert len(sp.train_idx) + len(sp.val_idx) + len(sp.test_idx) == len(df)
    # Roughly 70/15/15
    assert 0.65 < len(sp.train_idx) / len(df) < 0.75
    assert 0.10 < len(sp.val_idx) / len(df) < 0.20
    assert 0.10 < len(sp.test_idx) / len(df) < 0.20


def test_stratified_split_no_leakage():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 30, "military_acm": 20, "extreme_post_stall": 10})
    sp = stratified_split(df, seed=0)

    train_set = set(sp.train_idx.tolist())
    val_set = set(sp.val_idx.tolist())
    test_set = set(sp.test_idx.tolist())
    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(test_set)
    assert val_set.isdisjoint(test_set)


def test_stratified_split_preserves_category_proportions():
    from cgem_ext.data.splits import stratified_split

    counts = {"championship": 100, "military_acm": 50, "extreme_post_stall": 30}
    df = _fixture_df(counts)
    sp = stratified_split(df, seed=0)

    train_df, _, _test_df = sp.apply(df)
    overall = df["maneuver_category"].value_counts(normalize=True)
    train_props = train_df["maneuver_category"].value_counts(normalize=True)

    # Category proportions in train should be within 5pp of the overall proportions.
    for cat in counts:
        assert abs(train_props.get(cat, 0) - overall.get(cat, 0)) < 0.05


def test_stratified_split_is_deterministic():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 50, "military_acm": 50})
    sp1 = stratified_split(df, seed=123)
    sp2 = stratified_split(df, seed=123)

    np.testing.assert_array_equal(sp1.train_idx, sp2.train_idx)
    np.testing.assert_array_equal(sp1.val_idx, sp2.val_idx)
    np.testing.assert_array_equal(sp1.test_idx, sp2.test_idx)


def test_stratified_split_seeds_differ():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 50, "military_acm": 50})
    sp1 = stratified_split(df, seed=1)
    sp2 = stratified_split(df, seed=2)

    # Different seeds should produce different partitions.
    assert not np.array_equal(sp1.train_idx, sp2.train_idx)


def test_stratified_split_drops_error_rows():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 30})
    df.loc[:5, "status"] = "error"
    sp = stratified_split(df, seed=0, drop_status_error=True)

    n_total = len(sp.train_idx) + len(sp.val_idx) + len(sp.test_idx)
    assert n_total == 24  # 30 - 6 errored


def test_stratified_split_invalid_fractions():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 10})
    with pytest.raises(ValueError):
        stratified_split(df, train_frac=0.5, val_frac=0.5, test_frac=0.5)


def test_leave_one_group_out_yields_each_category():
    from cgem_ext.data.splits import leave_one_group_out

    counts = {"championship": 20, "military_acm": 15, "extreme_post_stall": 10}
    df = _fixture_df(counts)
    splits = list(leave_one_group_out(df))

    assert len(splits) == len(counts)
    held_out = {gs.held_out for gs in splits}
    assert held_out == set(counts.keys())


def test_leave_one_group_out_shapes():
    from cgem_ext.data.splits import leave_one_group_out

    counts = {"championship": 20, "military_acm": 15, "extreme_post_stall": 10}
    df = _fixture_df(counts)

    for gs in leave_one_group_out(df):
        n_train = len(gs.train_idx)
        n_test = len(gs.test_idx)
        # Held-out test should equal that category's row count.
        assert n_test == counts[gs.held_out]
        # Train should contain all *other* rows.
        assert n_train == len(df) - counts[gs.held_out]


def test_leave_one_group_out_no_leakage():
    from cgem_ext.data.splits import leave_one_group_out

    df = _fixture_df({"championship": 20, "military_acm": 15, "extreme_post_stall": 10})
    for gs in leave_one_group_out(df):
        train_categories = df.iloc[gs.train_idx]["maneuver_category"].unique()
        test_categories = df.iloc[gs.test_idx]["maneuver_category"].unique()
        assert gs.held_out not in set(train_categories)
        assert set(test_categories) == {gs.held_out}


def test_apply_returns_disjoint_frames():
    from cgem_ext.data.splits import stratified_split

    df = _fixture_df({"championship": 100, "military_acm": 50})
    sp = stratified_split(df, seed=0)
    train_df, val_df, test_df = sp.apply(df)

    train_ids = set(train_df["row_id"])
    val_ids = set(val_df["row_id"])
    test_ids = set(test_df["row_id"])
    assert train_ids.isdisjoint(val_ids)
    assert train_ids.isdisjoint(test_ids)
    assert val_ids.isdisjoint(test_ids)
    assert len(train_ids) + len(val_ids) + len(test_ids) == len(df)


# ──────────────────────────────────────────────────────────────────────
# Generator tests — require the cgem binary
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.needs_cgem_binary
def test_generate_smoke_run(tmp_path: Path, cgem_binary_available: bool):
    """End-to-end smoke run produces a non-empty parquet with the
    documented schema and a sidecar metadata file."""
    if not cgem_binary_available:
        pytest.skip("cgem binary not present")

    from cgem_ext.data import generate_dataset

    output = tmp_path / "smoke.parquet"
    metadata = generate_dataset.generate(
        output_path=output,
        smoke=True,
        master_seed=7,
        workers=1,
    )

    assert output.is_file()
    assert metadata["rows_total"] > 0
    assert metadata["rows_error"] == 0
    assert metadata["smoke"] is True

    df = pd.read_parquet(output)

    # Required columns from the schema contract
    required = {
        "row_id", "maneuver", "maneuver_category", "arm",
        "who_profile", "g_tolerance_multiplier",
        "dehydration_label", "dehydration_level",
        "countermeasures_label",
        "gsuit_max_psi", "gsuit_coverage_fraction",
        "agsm_effectiveness", "pbg_max_mmhg",
        "row_seed", "status",
        "time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s",
        "event_greyout", "event_blackout", "event_gloc",
        "hlap_min", "c_bank_min", "f_con_min",
        "g_peak_abs", "dgdt_max_g_per_s", "profile_duration_s",
    }
    missing = required - set(df.columns)
    assert not missing, f"Smoke parquet missing required columns: {missing}"

    # Sidecar metadata
    sidecar = output.with_suffix(".meta.json")
    assert sidecar.is_file()


@pytest.mark.needs_cgem_binary
def test_generator_is_deterministic(tmp_path: Path, cgem_binary_available: bool):
    """Two smoke runs with the same seed must produce identical row_seeds
    (CGEM itself is deterministic; we verify our seeding is too)."""
    if not cgem_binary_available:
        pytest.skip("cgem binary not present")

    from cgem_ext.data import generate_dataset

    out1 = tmp_path / "a.parquet"
    out2 = tmp_path / "b.parquet"
    generate_dataset.generate(output_path=out1, smoke=True, master_seed=99, workers=1)
    generate_dataset.generate(output_path=out2, smoke=True, master_seed=99, workers=1)

    df1 = pd.read_parquet(out1).sort_values("row_id").reset_index(drop=True)
    df2 = pd.read_parquet(out2).sort_values("row_id").reset_index(drop=True)

    # Per-row seed determinism
    pd.testing.assert_series_equal(df1["row_seed"], df2["row_seed"], check_names=False)
    # Per-row CGEM event scalars must also match exactly
    for col in ("time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s",
                "hlap_min", "c_bank_min"):
        pd.testing.assert_series_equal(
            df1[col].astype(float, errors="ignore"),
            df2[col].astype(float, errors="ignore"),
            check_names=False,
        )
