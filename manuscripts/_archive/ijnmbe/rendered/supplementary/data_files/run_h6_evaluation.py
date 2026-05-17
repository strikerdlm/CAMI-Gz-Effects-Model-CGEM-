"""H6 evaluation pass — score the trained CQR surrogate against the
Phase A archival cohort and write the results JSON.

H6 (OSF amendment 2026-05-06 §B-H6): "On a cohort of historical
centrifuge event-time records, the surrogate's calibrated prediction
interval covers ≥ 90 % of the real event times."

This script:

1. Loads ``data/datasets/cgem_synthetic_v1.parquet`` and the OSF-locked
   stratified split (master seed 42).
2. Trains :class:`TwoStageXGBQuantileSurrogate` on ``time_to_gloc_s``
   (the same model evaluated under H5 in
   ``tests/test_cqr.py::test_cqr_fixes_time_to_gloc_under_coverage``).
3. Loads the archival cohort from
   ``data/archival/centrifuge_tables.parquet``.
4. Maps each WF2013 row (event = G-LOC) to a CGEM-input row using the
   mapping rules locked in OSF amendment §B-H6:

   - ``dgdt_max_g_per_s`` ← ``onset_rate_g_per_s`` (verbatim).
   - ``g_peak_abs`` ← ``min(9.0, 1.0 + onset_rate * time_to_loc_s_mean)``.
     The 9.0 ceiling reflects the CGEM training envelope; the 9.4 G
     experimental ceiling reported in WF2013 is clipped to 9.0 for
     the surrogate query.
   - ``profile_duration_s`` ← ``time_to_loc_s_mean + 5.0`` (a five-
     second buffer past the reported mean ensures the maneuver
     definitely contains the event).
   - ``who_profile = 4`` (military average resistance, US cohort —
     locked rule in OSF amendment §B-H6).
   - All countermeasures off (``gsuit_*``, ``agsm_effectiveness``,
     ``pbg_max_mmhg`` = 0; ``countermeasures_label = "none"``;
     ``cm_ordinal = 0``).
   - ``dehydration_level = 0.0``; ``g_tolerance_multiplier = 1.0``.
   - ``maneuver_category = "military_acm"`` so the CQR Mondrian
     stratum aligns with the manuscript §3.3 Military ACM stratum.

5. Runs :meth:`TwoStageXGBQuantileSurrogate.predict_event_probability`
   and :meth:`predict_interval` per row, computes the surrogate
   bracket, and compares to the real ``time_to_loc_s_mean`` and the
   1-SD reference interval ``[mean - sd, mean + sd]``.
6. Reports two coverage criteria:

   - **Point coverage**: fraction of cohort rows where
     ``surrogate_lo ≤ real_mean ≤ surrogate_hi``.
   - **Interval-overlap coverage**: fraction of cohort rows where the
     surrogate bracket overlaps the real ``[mean − sd, mean + sd]``
     reference interval.

7. Computes the discrepancy δ̄ = mean(real − surrogate_median) with a
   95 % bootstrap CI (1,000 paired resamples,
   ``numpy.random.default_rng(42)``).
8. Writes ``data/results/h6/discrepancy_phase_a.json`` with the full
   per-row table and the headline aggregates.

The script is deterministic; re-running against the same parquet and
binary produces an identical JSON. It does not invoke the Fortran
binary directly — the surrogate is queried as the H5/H6 fast forward
solver. A future extension may run the Fortran binary on the same
mapped rows for a higher-fidelity discrepancy estimate; that is
deferred to Week 5–6 (multi-fidelity).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from cgem_ext.data.splits import stratified_split
from cgem_ext.surrogate import TwoStageXGBQuantileSurrogate

# ── Mapping constants (OSF amendment §B-H6) ───────────────────────────

CGEM_GPEAK_CEILING = 9.0  # CGEM training envelope max
EXPERIMENTAL_GCEILING = 9.4  # WF2013 / WFR2014 experimental ceiling
PROFILE_DURATION_BUFFER_S = 5.0  # ensure the maneuver fully contains LOC
DEFAULT_WHO_PROFILE = 4  # military average-resistance US cohort
DEFAULT_MANEUVER_CATEGORY = "military_acm"
ALPHA = 0.05


def _build_input_row(record: pd.Series) -> dict:
    """Build a single CGEM-input row from a WF2013 archival record."""
    onset = float(record["onset_rate_g_per_s"])
    real_t = float(record["time_to_loc_s_mean"])

    # G-peak at LOC under the experimental protocol, clipped to CGEM
    # training envelope.
    g_peak = min(CGEM_GPEAK_CEILING, 1.0 + onset * real_t)
    duration = real_t + PROFILE_DURATION_BUFFER_S

    return {
        "row_id": str(record["record_id"]),
        "maneuver": str(record["record_id"]),
        "maneuver_category": DEFAULT_MANEUVER_CATEGORY,
        "arm": "archival",
        "who_profile": DEFAULT_WHO_PROFILE,
        "g_tolerance_multiplier": 1.0,
        "dehydration_label": "none",
        "dehydration_level": 0.0,
        "countermeasures_label": "none",
        "gsuit_max_psi": 0.0,
        "gsuit_coverage_fraction": 0.0,
        "agsm_effectiveness": 0.0,
        "pbg_max_mmhg": 0.0,
        "g_peak_abs": float(g_peak),
        "dgdt_max_g_per_s": onset,
        "profile_duration_s": duration,
        "status": "ok",
        # The censored event is by construction: every WF2013 row is an
        # observed G-LOC. We set event_gloc=1 so the surrogate's
        # event-positive coverage path applies.
        "event_gloc": 1,
        "time_to_gloc_s": real_t,
    }


def _bootstrap_ci(values: np.ndarray, *, alpha: float, seed: int = 42) -> tuple[float, float]:
    """Paired-resample bootstrap (1,000 draws); return (lo, hi)."""
    rng = np.random.default_rng(seed)
    n = len(values)
    if n == 0:
        return (float("nan"), float("nan"))
    means = np.empty(1000)
    for i in range(1000):
        idx = rng.integers(0, n, n)
        means[i] = float(values[idx].mean())
    lo = float(np.quantile(means, alpha / 2.0))
    hi = float(np.quantile(means, 1.0 - alpha / 2.0))
    return (lo, hi)


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    syn_path = repo / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    arc_path = repo / "data" / "archival" / "centrifuge_tables.parquet"
    out_dir = repo / "data" / "results" / "h6"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "discrepancy_phase_a.json"

    if not syn_path.exists():
        raise SystemExit(f"missing synthetic parquet at {syn_path}")
    if not arc_path.exists():
        raise SystemExit(f"missing archival parquet at {arc_path}")

    syn = pd.read_parquet(syn_path)
    if "status" in syn.columns:
        syn = syn[syn["status"] == "ok"].reset_index(drop=True)
    split = stratified_split(syn, seed=42)
    train_df = syn.iloc[split.train_idx].copy()
    val_df = syn.iloc[split.val_idx].copy()

    print(f"[H6] training surrogate on n_train={len(train_df)} rows")
    surrogate = TwoStageXGBQuantileSurrogate(
        "time_to_gloc_s", alpha=ALPHA
    ).fit(train_df, calibration_df=val_df)

    arc = pd.read_parquet(arc_path)
    # H6 evaluation runs against the 8 Phase A onset-rate point rows
    # (each carries a real time_to_loc_s mean and SD at a single onset
    # rate). Phase B WF2013 rows are stratification-band anchors and
    # threshold values — they do not have a single onset rate to map
    # into CGEM input space and are reported separately in the
    # provenance audit, not consumed by the surrogate query path.
    wf2013 = arc[
        (arc["source_id"] == "WF2013") & (arc["phase"] == "A")
    ].copy()
    if wf2013.empty:
        raise SystemExit("no Phase A WF2013 rows in archival cohort")

    rows = [_build_input_row(rec) for _, rec in wf2013.iterrows()]
    eval_df = pd.DataFrame(rows)

    p_event = surrogate.predict_event_probability(eval_df)
    median = surrogate.predict(eval_df)
    lo, hi = surrogate.predict_interval(eval_df)

    real_mean = wf2013["time_to_loc_s_mean"].astype(float).to_numpy()
    real_sd = wf2013["time_to_loc_s_sd"].astype(float).to_numpy()
    onset = wf2013["onset_rate_g_per_s"].astype(float).to_numpy()

    point_in_bracket = (real_mean >= lo) & (real_mean <= hi)
    real_lo = real_mean - real_sd
    real_hi = real_mean + real_sd
    overlap = (lo <= real_hi) & (hi >= real_lo)
    discrepancy = real_mean - np.asarray(median, dtype=float)

    rows_out: list[dict] = []
    for i, (_, rec) in enumerate(wf2013.iterrows()):
        rows_out.append(
            {
                "record_id": str(rec["record_id"]),
                "onset_rate_g_per_s": float(onset[i]),
                "real_time_to_loc_s_mean": float(real_mean[i]),
                "real_time_to_loc_s_sd": float(real_sd[i]),
                "g_peak_at_eval": float(eval_df.loc[i, "g_peak_abs"]),
                "profile_duration_s_at_eval": float(
                    eval_df.loc[i, "profile_duration_s"]
                ),
                "surrogate_p_event": float(p_event[i]),
                "surrogate_median_s": float(median[i]),
                "surrogate_lo_s": float(lo[i]),
                "surrogate_hi_s": float(hi[i]),
                "real_mean_in_bracket": bool(point_in_bracket[i]),
                "interval_overlap_with_real_pm_sd": bool(overlap[i]),
                "discrepancy_real_minus_surrogate_s": float(discrepancy[i]),
            }
        )

    delta_mean = float(discrepancy.mean())
    delta_ci = _bootstrap_ci(discrepancy, alpha=ALPHA)

    summary = {
        "_meta": {
            "produced_by": "scripts/run_h6_evaluation.py",
            "synthetic_dataset": str(
                syn_path.relative_to(repo)
            ),
            "archival_cohort": str(arc_path.relative_to(repo)),
            "split_seed": 42,
            "alpha": ALPHA,
            "n_train": int(len(train_df)),
            "n_val": int(len(val_df)),
            "n_archival_rows_evaluated": int(len(wf2013)),
            "mapping_rules": {
                "g_peak_ceiling": CGEM_GPEAK_CEILING,
                "experimental_g_ceiling": EXPERIMENTAL_GCEILING,
                "profile_duration_buffer_s": PROFILE_DURATION_BUFFER_S,
                "who_profile": DEFAULT_WHO_PROFILE,
                "maneuver_category": DEFAULT_MANEUVER_CATEGORY,
                "countermeasure_state": "none (relaxed)",
            },
            "osf_amendment": "docs/publication/osf_amendment_2026-05-06.md (H6)",
        },
        "headline": {
            "n_evaluated": int(len(wf2013)),
            "point_coverage_real_mean_in_bracket": float(
                point_in_bracket.mean()
            ),
            "interval_overlap_coverage": float(overlap.mean()),
            "delta_bar_real_minus_surrogate_s_mean": delta_mean,
            "delta_bar_95pct_bootstrap_ci": list(delta_ci),
            "h6_threshold": 0.90,
            "h6_threshold_met_overlap": bool(overlap.mean() >= 0.90),
            "h6_threshold_met_point": bool(point_in_bracket.mean() >= 0.90),
        },
        "rows": rows_out,
    }

    out_path.write_text(json.dumps(summary, indent=2))
    print(f"[H6] wrote {out_path}")
    print(
        f"[H6] point coverage = {summary['headline']['point_coverage_real_mean_in_bracket']:.3f}; "
        f"interval-overlap coverage = {summary['headline']['interval_overlap_coverage']:.3f}; "
        f"δ̄ = {delta_mean:+.2f} s [95% CI {delta_ci[0]:+.2f}, {delta_ci[1]:+.2f}]"
    )


if __name__ == "__main__":
    main()
