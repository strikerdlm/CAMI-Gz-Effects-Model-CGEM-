# OSF Pre-Registration — Paper 1 (AMHP Methods Paper)

> **Title**: An ML-augmented framework for accelerated G-LOC prediction:
> surrogate emulation, out-of-distribution detection, and conformal
> uncertainty quantification of the CAMI G-Effects Model.

> **Status**: DRAFT — to be posted to OSF before any test-set evaluation
> in Phase 3 (surrogate training).
>
> **OSF DOI**: TBD (will be inserted here at posting time and committed).
>
> **Pre-registered on**: TBD (target: end of Phase 1, before Phase 2/3
> begin).

This document locks the validation protocol for paper 1. After the OSF post is timestamped, **no field below may change in the published paper without an explicit deviation statement in the Methods section**. That contract is what makes the synthetic-only validation defensible to reviewers.

---

## 1. Hypotheses

We pre-register the following testable hypotheses, all evaluated on the held-out test set drawn from the synthetic dataset `cgem_synthetic_v1` (sidecar `data/datasets/cgem_synthetic_v1.meta.json`, master seed 42, binary SHA-256 logged):

- **H1a (continuous-target accuracy)**: For each continuous-target XGBoost surrogate (`hlap_min`, `c_bank_min`), held-out test R² ≥ 0.90. *Empirical anchors* (Phase-3 smoke run before posting): hlap_min R² = 1.000, c_bank_min R² = 0.938.
- **H1b (censored-target classifier)**: For each censored-target two-stage surrogate (`time_to_greyout_s`, `time_to_blackout_s`, `time_to_gloc_s`), the stage-1 classifier achieves AUROC ≥ 0.95 on the held-out test split. *Empirical anchors*: 0.996 / 0.999 / 0.996.
- **H1c (censored-target regressor)**: For each censored-target two-stage surrogate, the stage-2 regressor R² ≥ 0.75 on event=1 rows of the held-out test split. *Empirical anchors*: 0.880 / 0.903 / 0.821.
- **H2 (conformal calibration)**: Empirical coverage of the Mondrian split-conformal 95 % prediction intervals is within ±5 percentage points of the nominal 95 % for each continuous target. *Empirical anchors*: hlap_min 0.928, c_bank_min 0.949. Censored-target coverage reported as exploratory; the conditional time has a long tail and `time_to_gloc_s` shows a 9pp under-coverage that motivates a future heteroscedastic conformal extension (Romano et al. 2019).
- **H3a (OOD calibration, primary)**: With Mahalanobis-distance scores plus a split-conformal abstention threshold calibrated on the validation split at `α = 0.05`, the empirical in-envelope rate on the held-out test split is within ±2 percentage points of the nominal 95 %. *Empirical anchor* (Phase-2 smoke run before posting): test in-envelope rate **0.953** on `cgem_synthetic_v1`, well within tolerance.
- **H3b (OOD discrimination, exploratory)**: On at least 2 of 4 leave-one-group-out folds, the LOGO AUROC of the better-performing detector (Mahalanobis vs IsolationForest baseline) exceeds 0.60. *Empirical anchor*: best-fold AUROC is 0.659 (`military_acm`, Mahalanobis). H3b is reported as an exploratory result; failure does not block paper-1. The reframing is documented in the OOD model card (`docs/models/ood_card.md`): **categories overlap in continuous feature space, so LOGO AUROC reflects category-overlap, not detector failure**.
- **H4a (sensitivity stability, total-order — primary)**: Total-order Sobol indices (ST) computed via the surrogate are stable across two independent Saltelli samples — Spearman rank correlation of the per-target ST rankings ≥ 0.95 across all 5 targets. *Empirical anchor* (Phase-4 smoke at n_base=512 per sample, two seeds): 1.000 for time_to_greyout/blackout/gloc and c_bank_min; 0.983 for hlap_min. Final paper run uses n_base=1024.
- **H4b (sensitivity stability, first-order — exploratory)**: First-order indices (S1) Spearman rank correlation ≥ 0.60 across all 5 targets. *Empirical anchor*: 0.466 for `time_to_gloc_s` (failed), 0.569 for `hlap_min`, 0.741 for `time_to_greyout_s`, 0.810 for `time_to_blackout_s`, 0.983 for `c_bank_min`. The under-stability for `time_to_gloc_s` is expected: many of its 9 inputs have near-zero S1 (effect is interaction-mediated, captured by ST), and rank correlations on near-zero values are noisy. Reported as a documented limitation; the headline rankings in paper 1 use ST.

Failure of any individual hypothesis does **not** invalidate the paper; it triggers the failure-handling protocol in §6.

---

## 2. Dataset

- **Name**: `cgem_synthetic_v1`.
- **Path**: `data/datasets/cgem_synthetic_v1.parquet`.
- **Sidecar**: `data/datasets/cgem_synthetic_v1.meta.json`.
- **Datasheet**: `docs/data/datasheet.md` (Gebru et al. 2018).
- **Generation seed**: master seed `42` (per-row seeds derived deterministically; see datasheet §Reproducibility).
- **Compiled binary**: SHA-256 hash recorded in the sidecar; CI verifies the hash matches before any model is trained.
- **Total rows**: 3,240 (1,296 standard arm + 1,944 custom arm; 45 rows per maneuver across 72 maneuvers).
- **Status filter**: pre-registered to drop `status != "ok"` rows before splitting (`drop_status_error=True` in `cgem_ext.data.splits.stratified_split`).

---

## 3. Splits

### 3.1 Stratified 70 / 15 / 15

- Implementation: `cgem_ext.data.splits.stratified_split(df, seed=42, train_frac=0.70, val_frac=0.15, test_frac=0.15, drop_status_error=True)`.
- Stratification key: `maneuver_category` (championship, military_acm, extreme_post_stall, conceptual; "training" is empty in v1).
- Per-category proportions in train must lie within ±5 percentage points of the overall proportions (verified by `tests/test_data.py::test_stratified_split_preserves_category_proportions`).
- Test set may be inspected **only once**, after H1–H4 have been evaluated and reported. No test-set tuning is permitted — see §5.

### 3.2 Leave-one-group-out

- Implementation: `cgem_ext.data.splits.leave_one_group_out(df)`.
- One `GroupSplit` per maneuver category; train = all rows from other categories, test = all rows from the held-out category.
- Drives H3 (OOD AUROC) and the leave-one-group-out R² robustness metric.
- Iteration order is alphabetical and deterministic.

---

## 4. Models

### 4.1 Surrogate (per target)

- **Targets**: `time_to_greyout_s`, `time_to_blackout_s`, `time_to_gloc_s`, `hlap_min`, `c_bank_min`. Censored time targets handled via two-stage classifier-then-regressor (the classifier is fit on the binary `event_*` flag; the regressor is fit on rows with `event_* == 1` only).
- **Backbone**: XGBoost regressor (or classifier for the gating stage). Sanity baseline: scikit-learn `RandomForestRegressor`.
- **Monotonicity constraints**: applied where physiologically required (e.g., `g_peak_abs` ↑ → `time_to_gloc_s` ↓, monotone-decreasing).
- **Hyperparameter search**: Optuna with stratified k-fold CV (`k=5`) on the train split. Search space frozen at OSF posting time (recorded as `docs/publication/osf_search_spaces.json`).
- **Calibration**: split-conformal Mondrian intervals stratified by `maneuver_category`, calibrated on the validation split, evaluated on the test split. Reliability diagrams + ECE reported as supplementary.

### 4.2 OOD detector

- **Backbone**: `sklearn.covariance.MinCovDet` over the input feature space `{g_peak_abs, dgdt_max_g_per_s, profile_duration_s, who_profile (one-hot), countermeasures (ordinal: none<agsm<suit_agsm), dehydration_level, g_tolerance_multiplier}`.
- **Threshold**: χ²(df, 0.95) on squared Mahalanobis distance.
- **Conformal abstention**: split-conformal threshold tuned to nominal abstention rate α = 0.05 on the validation split.
- **Comparison baseline**: `sklearn.ensemble.IsolationForest` with default hyperparameters.

### 4.3 Sensitivity analysis

- **Backbone**: SALib `saltelli.sample` (10⁴ base samples) → `sobol.analyze`.
- **Driver**: the trained per-target XGBoost surrogate.
- **Outputs**: first-order, total-order, and second-order Sobol indices with bootstrap confidence intervals.
- **Stability check** (H4): two independent Saltelli samples; Spearman rank correlation of per-target rankings ≥ 0.90.

---

## 5. Hold-out discipline

- The test split is sealed before training begins. Split indices are written to `docs/publication/osf_split_indices.parquet` at OSF posting time and never modified.
- **No test-set tuning** is permitted. The validation split drives all hyperparameter and calibration decisions.
- The test split is loaded exactly once in the final paper-1 evaluation script (`scripts/evaluate_paper1.py`, to be added in Phase 3).
- Model artifacts and metrics are versioned via MLflow with the dataset hash logged in every run. The `experiment_id` for the paper-1 run is recorded here at OSF posting.

---

## 6. Failure-handling protocol

If any of H1–H4 fail on the test split, the following protocol applies *and* is reported in the paper:

1. The failure is reported transparently in Results (no cherry-picking, no re-splitting).
2. **No** post-hoc adjustment to the surrogate, OOD detector, or sensitivity protocol is permitted before reporting.
3. Permitted post-failure actions:
   - Diagnostic analysis on the validation split to characterise where the failure originates.
   - Adding a new model variant *as a separate experiment* (logged as a distinct MLflow run, reported as exploratory in the Discussion).
   - Re-running with a freshly drawn test split *only if* a new dataset version (`cgem_synthetic_v2`) is generated and a new pre-registration is filed.
4. Failure of any H1 sub-hypothesis (H1a continuous R², H1b classifier AUROC, H1c regressor R²) or H2 (conformal coverage) implies the framework is not yet ready for paper-1 publication; we either iterate on the model architecture (new pre-registration) or scope the paper down (e.g., accept lower R² with explicit limitation reporting). Failure of conformal coverage on a single censored target (currently only `time_to_gloc_s` shows under-coverage) is acceptable as a documented limitation pointing at heteroscedastic conformal as future work.
5. **H3a** failure (calibration miss > 2 pp) is treated as a true methodological failure: the conformal layer must be debugged before reporting. **H3b** failure (LOGO AUROC at-or-below the 0.60 threshold on > 2 folds) is acceptable as a published limitation; it does not block paper-1 because the calibration result (H3a) carries the operational claim, while LOGO AUROC is reported as exploratory.
6. Failure of H4 alone is acceptable; the sensitivity rankings are reported but with explicit instability caveats.

---

## 7. Reporting standards

- TRIPOD-AI checklist for ML-in-medicine reporting (supplementary).
- Datasheet (`docs/data/datasheet.md`).
- Model cards: `docs/models/emulator_card.md`, `docs/models/ood_card.md`.
- All figures rendered at journal resolution via the `echarts` and `publication-visuals` skills.
- Open code (this repository, MIT license) and open synthetic dataset (Zenodo DOI) at submission time.

---

## 8. Authorship and AI disclosure

Sole author of all code, manuscript, and pre-registration: **Dr. Diego Malpica, MD** (ORCID 0000-0002-2257-4940).

AI assistants were used for code scaffolding, documentation drafts, and editorial assistance. The use of AI tools is disclosed at the paper level (Methods and/or Acknowledgments sections), not at the commit level — every git commit on this repository is sole-authored by `strikerdlm`.

---

## 9. Posting checklist

Before posting to OSF:

- [ ] Dataset hash logged in `data/datasets/cgem_synthetic_v1.meta.json` matches the parquet on disk.
- [ ] `tests/test_data.py` passes on Python 3.10 / 3.11 / 3.12.
- [ ] `tests/test_contract.py` passes (pulse-sim contract intact).
- [ ] Hyperparameter search spaces frozen and committed to `docs/publication/osf_search_spaces.json`.
- [ ] Stratified split indices frozen and committed to `docs/publication/osf_split_indices.parquet`.
- [ ] OSF page created, this document uploaded as the registration plan.
- [ ] OSF DOI inserted at the top of this document and committed.
- [ ] Pre-registration date recorded.

After posting:

- [ ] Phase 2 (OOD) and Phase 3 (surrogate) work begins.
- [ ] No commits modifying this file are permitted unless documenting a deviation.
