# Datasheet — `cgem_synthetic_v1`

A synthetic dataset of CAMI G-Effects Model (CGEM) outputs over a structured cross-product of aerobatic maneuvers and pilot configurations. Used to train and validate the surrogate emulator (`cgem_ext.surrogate`), the OOD detector (`cgem_ext.ood`), and the global sensitivity analysis (`cgem_ext.sensitivity`) shipped in the v0.1.0 ML extension layer.

This datasheet follows the framework of Gebru *et al.* (2018), [*Datasheets for Datasets*](https://arxiv.org/abs/1803.09010).

---

## Motivation

**For what purpose was the dataset created?** To enable rigorous benchmarking of an ML extension layer (surrogate, OOD detection, sensitivity analysis, conformal uncertainty quantification) on top of the FAA's validated CGEM Fortran model, *before* centrifuge validation against the lab's own subjects becomes available. The synthetic-only approach is a deliberate v1 boundary documented in `docs/publication/Q1_PAPER_PLAN.md`: paper 1 validates the framework against CGEM as ground truth; paper 2 extends to published external centrifuge data; paper 3 extends to own-centrifuge subjects.

**Who created the dataset?** Dr. Diego Malpica, MD (Direction of Aerospace Medicine, Colombian Aerospace Force, Aerospace Scientific Department). ORCID: 0000-0002-2257-4940.

**Who funded the creation?** Self-funded research; no external sponsorship.

---

## Composition

**What do the instances represent?** Each row represents one CGEM simulation run for a (maneuver, pilot configuration) pair. The maneuver is one of 72 registered aerobatic / military / extreme profiles; the pilot configuration combines a `who_profile` (FAA standard subject 1–6, or custom), a G-tolerance multiplier, a dehydration tier, and a countermeasures tier.

**How many instances?** 3,240 rows over the full grid:

| Arm | Cross-product | Rows / maneuver | Total |
|---|---|---|---|
| Standard | 6 `who_profile` × 3 countermeasures | 18 | 1,296 |
| Custom | 3 G-tolerance × 3 dehydration × 3 countermeasures | 27 | 1,944 |
| **Sum** | | **45** | **3,240** |

The two arms exist because the Fortran model overrides subject physiology to the FAA preset whenever `who_profile ∈ {1..6}`, making both `g_tolerance_multiplier` and `dehydration_level` no-ops on that path. The standard arm therefore fixes those at canonical values; the custom arm exercises them.

**What does each instance consist of?** A flat row with the following column families:

- *Identification*: `row_id`, `maneuver`, `arm`, `who_profile`, `g_tolerance_multiplier`, `dehydration_label`, `dehydration_level`, `countermeasures_label`, `gsuit_max_psi`, `gsuit_coverage_fraction`, `agsm_effectiveness`, `pbg_max_mmhg`, `row_seed`.
- *Maneuver-summary features* (precomputed once per maneuver): `maneuver_category`, `aresti_family`, `catalog_onset_rate_g_per_s`, `g_peak_abs`, `g_min`, `g_max`, `dgdt_max_g_per_s`, `profile_duration_s`, `num_profile_samples`.
- *CGEM event-time scalars* (the regression targets): `time_to_greyout_s`, `time_to_blackout_s`, `time_to_gloc_s` (all nullable), and the matching binary flags `event_greyout`, `event_blackout`, `event_gloc`.
- *Time-series-derived statistics*: `{hlap, c_bank, bo_bank, f_con, f_vis, f_bo, g_eff}_{min,max,mean,final}`.
- *Status*: `status` ∈ {`ok`, `error`}; `error_msg`; `num_samples`.

**Are there missing values?** Event-time scalars are `None` (parquet `null`) when the event did not occur during the maneuver. This is **not** missingness — it is right-censoring and is the rationale for the two-stage classifier-then-regressor pattern documented in `docs/architecture/ML_LAYER.md`.

**Is the dataset self-contained?** Yes. Maneuver definitions live in `Aerobatics_sample_inputs/*.txt`; the maneuver catalog (with category and Aresti metadata) lives in `maneuvers_catalog.py`. Both ship with this repo at the same commit as the dataset.

**Does the dataset contain confidential or sensitive content?** No. All maneuvers are publicly documented (Aresti CIVA catalogue, IAC programmes, ASEM/USAFSAM/NEDU literature). All pilot configurations are synthetic — no real subject's biometric data is included.

---

## Collection process

**How was the data acquired?** By executing the FAA-validated CGEM Fortran binary (`cgem` ELF / `cgem.exe`) once per row via the `cgem_wrapper.run_cgem_for_profile` Python wrapper. Each CGEM invocation receives the maneuver's `(Nz, duration_ms)` profile plus a `gloc_inp.dat` deck encoding the row's `PilotConfig`. The Fortran binary writes its output deck to a temporary directory; the wrapper parses it back into a `CGEMResult` dataclass; the dataset generator extracts the documented columns and writes them to parquet.

**What was the cross-product enumeration?** Implemented in `cgem_ext/data/generate_dataset.py:_enumerate_grid`. The generator yields a `RowSpec` per row; each `RowSpec` carries a deterministic per-row `seed` derived as `int.from_bytes(SHA256(f"{master_seed}|{row_id}").digest()[:4], "big")`. The master seed defaults to **42** and is recorded in the sidecar metadata.

**How was the data parallelised?** `multiprocessing.Pool` with `spawn` start method and `cpu_count - 1` workers. Each `run_cgem_for_profile` call creates its own `tempfile.mkdtemp` directory, so concurrent invocations are inherently isolated; no inter-worker locking is needed.

**Over what timeframe was the data collected?** The full grid generates in well under one minute on a modern multi-core CPU (~0.05 s/row × 3,240 rows ÷ N_workers). The dataset is regenerable at any time from the same seed with the same compiled binary.

**Was any preprocessing or filtering applied?** None at row generation time. Status-error rows (Fortran failures) are retained in the parquet and tagged via the `status` column; downstream ML code filters them at training time via `cgem_ext.data.splits.stratified_split(..., drop_status_error=True)`.

---

## Reproducibility

The dataset is fully reproducible from:

1. The compiled CGEM binary, hashed by SHA-256 at generation time and written to `*.meta.json` (`binary_sha256` field).
2. The `aerobatic_profiles` and `maneuvers_catalog` modules at the same commit as the generator.
3. The master seed (default 42).
4. The package version (recorded as `cgem_ext.__version__`).
5. The tier definitions (`DEHYDRATION_LEVELS`, `COUNTERMEASURES_LEVELS`, `G_TOLERANCE_TIERS`, `WHO_PROFILES` — all written to `*.meta.json`).

Re-running `python -m cgem_ext.data.generate_dataset --seed 42` against the same compiled binary produces an identical parquet (verified by `tests/test_data.py::test_generator_is_deterministic`).

---

## Recommended uses

- Training the surrogate emulator (`cgem_ext.surrogate`) — Phase 3.
- Fitting the OOD detector envelope (`cgem_ext.ood`) — Phase 2.
- Driving global sensitivity analysis (`cgem_ext.sensitivity`) — Phase 4.
- As the in-distribution reference for OOD evaluation against held-out maneuver categories (leave-one-group-out via `cgem_ext.data.splits.leave_one_group_out`).

**Recommended _not-uses_**:

- Do **not** treat synthetic CGEM outputs as ground-truth physiological response of any specific real pilot. The synthetic-only validation strategy is documented in paper 1's Methods and Discussion; downstream consumers should respect that boundary.
- Do **not** use the dataset to fit a model and then claim centrifuge-validated performance — that's the explicit subject of paper 3, blocked on subject data.
- Do **not** mix this dataset with real centrifuge data without re-fitting the surrogate; the discrepancy term `δ(x) = real(x) − CGEM(x)` is the explicit subject of paper 2.

---

## Distribution

- **Repository**: `strikerdlm/CAMI-Gz-Effects-Model-CGEM-`, branch `feat/ml-layer-phase-0`.
- **Path**: `data/datasets/cgem_synthetic_v1.parquet` (full file in DVC; hash committed). Sidecar metadata at `data/datasets/cgem_synthetic_v1.meta.json` (committed).
- **Zenodo DOI**: TBD at paper-1 submission time (Phase 7).
- **License**: MIT (matches the rest of the repo).

---

## Maintenance

- **Versioning**: Frozen by name (`cgem_synthetic_v1`). Any change to the input grid, master seed, tier definitions, or the underlying compiled binary's SHA increments the version — `cgem_synthetic_v2`, etc. — and is **not** an in-place update.
- **Updates**: Tracked in `CHANGELOG.md` `[Unreleased]` block per phase.
- **Successor versions** will land alongside paper 2 (external-data discrepancy work) and paper 3 (own-centrifuge validation), each carrying its own datasheet.

---

## Limitations

- **Synthetic only** — the dataset reproduces a validated FAA model. It does **not** validate against centrifuge or in-flight physiological data. This is the explicit subject of paper 2 and paper 3 follow-ups.
- **Standard arm undervaries** the dehydration and G-tolerance knobs because the Fortran model ignores them when `who_profile` is set. The surrogate naturally learns this constraint from the custom-arm rows.
- **Censored events** — many maneuver / pilot combinations do not trigger greyout/blackout/G-LOC. The censoring rate per target is reported in the sidecar metadata. Downstream models handle censoring via the two-stage pattern.
- **No instrumentation noise** — outputs are deterministic given inputs. Real centrifuge data carries noise that this dataset does not capture.
- **Six FAA presets only** — the custom arm exposes physiological variation but is bounded by the parameter ranges of `PilotConfig`. Out-of-range pilots (extreme age, unusual anthropometrics) are out of distribution and should be flagged by the OOD detector.

---

## Citation

> Malpica D. (2026). *cgem_synthetic_v1*: a synthetic CGEM dataset for ML-augmented G-LOC prediction. Repository `strikerdlm/CAMI-Gz-Effects-Model-CGEM-` v0.1.0. Zenodo DOI: *TBD at paper-1 submission*.

The underlying FAA CGEM model is cited separately:

> Copeland K. (2020). *Civil Aerospace Medicine Institute G-Effects Model (CGEM)*. Federal Aviation Administration Office of Aerospace Medicine, AAM-631.
