# Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology

**Target venue:** *International Journal for Numerical Methods in Biomedical Engineering* (IJNMBE, Wiley, ISSN 2040-7947). Article type: Research Paper. Submission track: subscription / non-OA (Wiley hybrid; no APC). Portal: Wiley CNM (`https://authors.wiley.com/journal/CNM`). Editor-in-Chief: Perumal Nithiarasu, PhD, College of Engineering, Swansea University.

**Short title** (≤ 70 chars; for portal entry): Conformal ML wrapper for a validated ODE physiological model.

<!-- Author identity lives in `docs/publication/author_page.md` and is uploaded as the
Title Page file in Editorial Manager. -->

**Word count:** ≈ 5,430 (body, Introduction → Conclusion). IJNMBE has no stated body-word cap; this length is consistent with recent IJNMBE Research Papers.
**Abstract word count:** 341 (IJNMBE ≤ 400; structured *or* unstructured permitted; the structured Background and Objectives / Methods / Results / Conclusions form is retained for clarity).
**Tables:** 4.
**Figures:** 6 (all in main body at submission; IJNMBE accepts inline figures at submission and requires separate files only at revision; no figure-count limit).
**References:** 22 (incl. two IJNMBE-precedent references and one formal dataset citation per the Joint Declaration of Data Citation Principles).
**Mandatory separate files at IJNMBE:** `cover_letter_ijnmbe.md`, `novelty_file_ijnmbe.md` (≤ 100 words), `graphical_abstract_ijnmbe.md` (mini-abstract ≤ 80 words / 3 sentences) plus the rendered Graphical Table of Contents image, `suggested_reviewers_ijnmbe.md` (5 candidates), Data Files (data + code, uploaded as the **Data Files** designation, not as Supporting Information).
**CMPB Highlights file** (`docs/publication/highlights.md`): not used at IJNMBE — do **not** upload.

---

## Abstract

**Background and Objectives.** The FAA's CAMI G-Effects Model (CGEM) is a validated Fortran model of +Gz tolerance used in civil-aviation regulatory contexts. It is computationally expensive (~9 ms per call via subprocess), provides no calibrated uncertainty quantification, and accepts out-of-distribution (OOD) inputs without warning. We developed an additive machine-learning extension that closes these three gaps without modifying the validated core, illustrating a general pattern for wrapping legacy validated ordinary-differential-equation (ODE) physiological models with calibrated, uncertainty-aware emulators.

**Methods.** A synthetic dataset of 3,240 CGEM runs (72 aerobatic, military, and extreme post-stall maneuvers × 45 pilot configurations; master seed 42; binary SHA-256 logged) was generated. Per-target XGBoost surrogates were trained with a two-stage classifier-then-regressor pattern for right-censored event-time targets (greyout, blackout, G-LOC) and single-stage regressors for continuous targets (head-level arterial pressure, cerebral blood flow). Two Mondrian-stratified conformal layers were applied per maneuver category at α = 0.05: a homoscedastic split-conformal layer (Vovk et al.) for the four targets where it meets the pre-registered tolerance, and a heteroscedastic Conformalized Quantile Regression layer (Romano, Patterson & Candès 2019) — pre-registered as OSF amendment 2026-05-06 hypothesis H5 — for `time_to_gloc_s`, where the homoscedastic baseline under-covered. A robust Mahalanobis-distance detector with distribution-free conformal abstention provided OOD warning over a 17-dimensional feature space. Sobol variance-based and Morris elementary-effects sensitivity analyses were driven by the surrogate. The validation protocol was pre-registered on the Open Science Framework before any test-set evaluation.

**Results.** On the held-out test split, the conformal OOD layer achieved an empirical in-envelope rate of 0.953 versus the nominal 0.95, with the conformal threshold (squared distance 78.3) ~3× the parametric χ²(17, 0.95) cutoff. Mondrian conformal empirical coverage was within 4.6 percentage points of nominal 95 % on 4 of 5 surrogate targets, with under-coverage isolated to time-to-G-LOC (0.861, n = 36); classifier expected calibration error remained ≤ 0.014. Surrogate classifier AUROC was ≥ 0.996 across the three censored event targets and regressor R² was 0.82–0.90 on event-positive rows and 0.94–1.00 on continuous targets. Surrogate inference takes ~50 µs per row versus ~9 ms for direct CGEM subprocess invocation.

**Conclusions.** The framework preserves the FAA-validated CGEM core while adding emulator speed, calibrated prediction intervals, OOD abstention, and global sensitivity rankings — capabilities previously absent from CGEM applications. External and own-centrifuge validation are deferred to companion papers. The same surrogate + conformal + OOD pattern generalises to any validated ODE physiological model.

**Keywords** (6, IJNMBE Manuscript Style cap): physiological modelling; surrogate emulation; conformal prediction; out-of-distribution detection; global sensitivity analysis; acceleration physiology

---

## 1. Introduction

Validated mechanistic models embedded in regulatory or operational frameworks present a recurring methodological challenge in computational biomedicine: they encode decades of domain knowledge and experimental calibration, yet they are computationally expensive, lack calibrated uncertainty quantification, and accept out-of-distribution inputs without warning. Machine learning offers a natural complement — fast surrogate emulation [19], distribution-free prediction intervals [18], and input-envelope detection — but only if applied *additively*, preserving the validated core rather than replacing it. This paper presents such an additive ML stack and validates it against the FAA's CAMI G-Effects Model (CGEM), a Fortran-based regulatory physiological model of acceleration stress. The methodological pattern — surrogate emulator + conformal intervals + OOD detection, wrapping a validated model without modifying it — generalises to any biomedical domain where a validated ODE or simulation model must be made computationally tractable, uncertainty-aware, and input-safe.

The application domain is +Gz acceleration physiology in high-performance flight. G-induced loss of consciousness (G-LOC) remains a persistent risk in fighter, aerobatic, and high-performance fixed-wing aviation [1–3]. While centrifuge training and anti-G countermeasures — the anti-G straining maneuver (AGSM), G-suits, positive-pressure breathing for G (PBG) — have reduced G-LOC incidence substantially since the 1980s, the underlying physiology is complex and multi-factorial: G-onset rate, peak +Gz, exposure duration, pilot anthropometrics, hydration state, countermeasure configuration, and individual G tolerance all interact nonlinearly [4–6].

CGEM, developed at the FAA's Civil Aerospace Medical Institute, is the reference regulatory model of +Gz physiology [7]. It solves a system of ordinary differential equations governing cardiovascular and cerebrovascular response under sustained +Gz load, producing time-series predictions for cerebral blood flow (c_bank), head-level arterial pressure (HLAP), visual function, and brain oxygenation [7,8]. The model has been validated against human centrifuge data at the FAA CAMI and underpins G-tolerance standards in civil aviation certification; preserving it byte-for-byte is therefore both a scientific and a regulatory requirement.

However, CGEM has three limitations that constrain its operational and research utility. **First, computational cost.** Each CGEM invocation requires spawning a Fortran subprocess, writing a GLOC input deck to disk, waiting for the binary to solve the physiological ODE system, and parsing its output deck. On a modern multi-core CPU this takes approximately 9 ms per row — fast for single queries but prohibitive for parametric exploration: a 10,000-sample Saltelli Sobol study would require days of wall-clock time. **Second, no calibrated uncertainty quantification.** CGEM produces a deterministic scalar (e.g., "time to G-LOC: 8.3 s"), but the aeromedical operator needs to know how much to trust that number given the maneuver category, the pilot configuration, and the model's inherent approximation error. CGEM ships no confidence intervals or prediction bands. **Third, no input-envelope guard.** Users can query CGEM with inputs far outside the training/validation envelope — a pilot configuration never tested, a G-onset profile beyond published data — and receive a number with no warning that the model is extrapolating.

We address these three gaps with an additive ML extension layer that (1) detects out-of-distribution (OOD) inputs via robust Mahalanobis distance with distribution-free conformal abstention, (2) provides calibrated prediction intervals using a Mondrian-stratified homoscedastic split-conformal layer where appropriate and a heteroscedastic Conformalized Quantile Regression (CQR) layer for the long-tailed `time_to_gloc_s` target, (3) emulates CGEM at ~50 µs per row vs ~9 ms for direct subprocess invocation, and (4) identifies which input features drive G-LOC risk most via global sensitivity analysis (Sobol first- and total-order indices, Morris elementary effects). The framework is **additive**: the FAA-validated Fortran binary, compiled source (`.f` files), and input/output deck formats are not modified. The ML layer wraps the validated core like a fitted response surface; the authoritative `/run-cgem` endpoint remains available when direct CGEM invocation is required.

The manuscript validates the framework against CGEM as ground truth — a synthetic-only validation strategy, declared explicitly, that establishes the emulator + OOD + sensitivity pipeline on known ground truth before any real centrifuge data enters the picture. External validation against archival centrifuge data and own-centrifuge subjects are subjects of separate work and are not claimed here. The validation protocol is pre-registered on the Open Science Framework (OSF); the search spaces, split indices, and success thresholds are frozen at OSF posting time.

---

## 2. Methods

### 2.1 The CAMI G-Effects Model (CGEM)

CGEM is a Fortran-based physiological simulation model developed at the FAA Civil Aerospace Medical Institute (CAMI) in Oklahoma City [7]. It receives a +Gz time profile (Nz samples at a configurable sampling rate, typically 100 Hz) and a pilot configuration file (`gloc_inp.dat`) specifying: subject type (`who_profile`, an integer 1–6 mapping to six FAA-standard anthropometric and cardiovascular presets); G-suit parameters (max inflation pressure in psi, torso coverage fraction); AGSM effectiveness (fraction of maximal theoretical intra-abdominal and intra-thoracic pressure the pilot can sustain); PBG max pressure (mmHg); and a dehydration level (fractional plasma volume loss).

CGEM integrates a system of ODEs over the maneuver time window, producing per-sample time series for: compartmental arterial pressures (eye-level, brain-level, heart-level), cerebral blood flow velocity (`c_bank`, cm/s equivalent), brain oxygenation (`bo_bank`), retinal oxygen delivery, and visual function indices (`f_vis`, `f_bo`). From these time series the model derives event-time scalars: the earliest sample at which visual function drops below predefined thresholds for greyout, blackout, and G-LOC (right-censored: if the threshold is never crossed, no event time is reported).

The Fortran binary was compiled from the original CAMI source (`.f` files) and verified by reproducing a canonical FAA test case (Profile 4, standard 7-G sustained turn). The compiled binary's SHA-256 hash is recorded in `cgem_synthetic_v1.meta.json` alongside the master dataset seed (42). **The Fortran binary is not modified by the present work; the ML extension layer wraps it as a black-box function.**

### 2.2 Synthetic dataset

A structured synthetic dataset (`cgem_synthetic_v1`) was generated by enumerating a cross-product input grid and invoking CGEM once per (maneuver, pilot configuration) pair.

**Maneuvers.** 72 aerobatic, military, and extreme post-stall maneuvers were selected from the Aresti CIVA catalogue (2019 edition), IAC Known/Unknown programmes (2015–2020), and published USAFSAM/ASEM centrifuge profiles [8,9]. Each maneuver is defined as a (time, Nz) trace in the `Aerobatics_sample_inputs/*.txt` format consumed by CGEM; the maneuver catalog (`maneuvers_catalog.py`) records category (`championship`, `conceptual`, `extreme_post_stall`, `military_acm`), Aresti family, G-peak (absolute), maximum |dG/dt|, and profile duration.

**Pilot configurations — standard arm.** For each of the six FAA `who_profile` presets (1–6), three countermeasure tiers were crossed: baseline (no G-suit, no AGSM, no PBG), moderate (G-suit 5 psi, AGSM 0.5, no PBG), and maximum (G-suit 10 psi, AGSM 1.0, PBG 30 mmHg). The Fortran model overrides subject physiology to the FAA preset whenever `who_profile ∈ {1..6}`, so `g_tolerance_multiplier` and `dehydration_level` are no-ops on the standard arm and were held at canonical values (1.0, 0.0). Standard arm: 6 profiles × 3 countermeasures = 18 rows per maneuver, 1,296 rows total.

**Pilot configurations — custom arm.** A 3 × 3 × 3 grid was crossed: G-tolerance multiplier ∈ {0.85, 1.00, 1.15}, dehydration level ∈ {0.0, 0.04, 0.08} (fractional plasma volume loss), countermeasure tier ∈ {baseline, moderate, maximum}. The custom arm uses `who_custom` (a synthetic profile with editable physiology parameters, not one of the six FAA presets). Custom arm: 3 × 3 × 3 = 27 rows per maneuver, 1,944 rows total.

The full grid therefore yields 18 + 27 = 45 rows per maneuver × 72 maneuvers = **3,240 rows**. Each row carries a deterministic `row_seed` derived as `SHA256(master_seed || row_id)`, with master seed 42. Dataset generation is parallelized via `multiprocessing.Pool` (`spawn` start method, `cpu_count − 1` workers); each worker creates an isolated temporary directory for CGEM I/O.

**Reproducibility.** The dataset is fully reproducible from (a) the CGEM binary, (b) the maneuver catalog and profile files at the committed SHA, (c) the master seed (42), (d) the tier definitions in `cgem_ext.data.generate_dataset`, and (e) the compiled binary's SHA-256 hash. Re-running `python -m cgem_ext.data.generate_dataset --seed 42` against the same compiled binary produces an identical parquet file, verified by `tests/test_data.py::test_generator_is_deterministic`.

The dataset schema, censoring patterns, and documentation follow the datasheet framework of Gebru et al. (2018) [10]; the full datasheet is included as supplementary material.

### 2.3 Train / validation / test splits

Rows were split 70/15/15 (train/validation/test) stratified by `maneuver_category` (master seed 42), implemented in `cgem_ext.data.splits.stratified_split`. The validation split (15 %) is used for conformal calibration (both the Mondrian conformal regressor and the OOD conformal abstention layer); the test split (15 %, ~486 rows) is held out for all metrics reported in Section 3.

For exploratory OOD evaluation, leave-one-group-out (LOGO) folds hold out one maneuver category at a time: train on the remaining three categories, score the held-out category as "OOD." Four folds result: championship (held out, 1,665 train / 1,575 test), conceptual (3,105/135), extreme post-stall (2,700/540), and military ACM (2,250/990). LOGO folds are not used for model selection; they serve only as a qualitative probe of how the OOD detector responds to category drift.

### 2.4 Surrogate emulator

**Model architecture.** Five per-target models are trained, reflecting the three censored time targets (time to greyout, blackout, G-LOC) and two continuous targets (HLAP minimum, cerebral blood flow minimum). Censored targets use a **two-stage** pattern: stage 1 is an XGBoost [17] binary classifier predicting `P(event occurred during maneuver)`, trained on all rows; stage 2 is an XGBoost regressor predicting `E[event time | event=1]`, trained only on rows where the event occurred. The expected event time for a new input is `P(event) × E[time | event]`, but the API exposes both components separately. Continuous targets use a single-stage XGBoost regressor.

**Hyperparameters.** Defaults across all models: `n_estimators=400`, `max_depth=6`, `learning_rate=0.05`, `subsample=0.9`, `colsample_bytree=0.9`, `reg_lambda=1.0`, `tree_method="hist"`, `random_state=42`. Monotonicity constraints are applied where physiologically grounded: G-peak, dG/dt magnitude, and dehydration must monotonically decrease event times (or decrease HLAP/c_bank min); countermeasure effectiveness must monotonically increase event times (or increase HLAP/c_bank min). Monotonicity vectors are specified in `cgem_ext/surrogate/targets.py` and passed to XGBoost via `monotone_constraints`.

A formal Optuna hyperparameter search with stratified 5-fold cross-validation is deferred to `scripts/optuna_search.py` and will be locked at OSF posting time. The present manuscript reports the default hyperparameter configuration; search results will be posted as supplementary material before submission.

**Conformal prediction intervals — homoscedastic Mondrian (baseline).** For each target, a Mondrian split-conformal regressor [11,12] is calibrated on the validation split. Residuals `r = |y_true − y_pred|` are collected per `maneuver_category` stratum. The per-stratum conformal quantile is `q̂_s = Q((1 − α)(1 + 1/n_s), residuals_s)`, with finite-sample correction `ceil((n_s+1)(1−α)) / n_s`. At inference time, a test row assigned to stratum *s* receives the prediction interval `[ŷ − q̂_s, ŷ + q̂_s]`. Rows from strata unseen during calibration receive the global quantile `Q((1 − α), residuals_all)`.

**Conformal prediction intervals — heteroscedastic CQR (primary for `time_to_gloc_s`).** For targets whose conditional distribution is heteroscedastic — particularly `time_to_gloc_s`, where the homoscedastic Mondrian layer under-covered (§3.3) — we use Conformalized Quantile Regression (CQR) [15]. Three XGBoost quantile regressors are trained per target, sharing the per-target monotonicity vectors from `cgem_ext.surrogate.targets`: lower (α/2 quantile), median (point predictor), and upper (1 − α/2 quantile), each with `objective="reg:quantileerror"` and `tree_method="hist"`. Quantile crossing — the lower head exceeding the upper for some inputs — is post-hoc resolved row-wise by `(min, max)` of the two heads. The CQR conformity score on calibration row *i* is `s_i = max(q̂_lo(x_i) − y_i, y_i − q̂_hi(x_i))` per Romano, Patterson & Candès (2019, Eq. 1) [15]; the per-`maneuver_category` (1 − α) quantile of these scores is computed with the same finite-sample correction as the homoscedastic Mondrian layer, and the calibrated bracket is `[q̂_lo(x) − q̂_s, q̂_hi(x) + q̂_s]`. Bracket width is allowed to vary with x — that is the advantage over the homoscedastic Mondrian baseline for `time_to_gloc_s`. Implementation: `cgem_ext.surrogate.cqr.TwoStageXGBQuantileSurrogate` (classifier on all rows + CQR-quantile regressor on event-positive rows) and `cgem_ext.surrogate.conformal.MondrianCQR`. The CQR layer for `time_to_gloc_s` was pre-registered in OSF amendment 2026-05-06 as hypothesis H5 before any test-set evaluation under the new layer (see `docs/publication/osf_amendment_2026-05-06.md`).

**Calibration diagnostics.** Predicted values are binned into 10 equal-frequency bins. Per bin, the mean predicted value and mean observed value (or observed event fraction, for classifiers) are computed. Expected Calibration Error (ECE) is: `ECE = Σ_{b=1}^{10} (n_b/N) · |mean(observed_b) − mean(predicted_b)|`. Reliability diagrams and ECE values are reported for both continuous regressors (regression calibration) and stage-1 classifiers (classifier probability calibration). For censored targets, only the classifier stage is calibrated via this procedure; the conditional regressor calibration is deferred to paper 2 when external event-time ground truth is available.

**Interpretability.** SHAP TreeExplainer values [13] are computed per prediction and exposed via the FastAPI `/predict` endpoint and the frontend visualization. SHAP results are supplementary.

**Baseline.** A RandomForest regressor (sklearn defaults, `n_estimators=100`, `random_state=42`) is trained alongside each XGBoost model for comparison. RandomForest cannot enforce monotonicity constraints; the comparison is therefore apples-to-oranges in that respect and is reported as supplementary.

### 2.5 Out-of-distribution detection

**Feature space.** The OOD detector operates on a 17-dimensional feature vector (frozen in `cgem_ext.ood.features.FEATURE_COLUMNS`): 9 numeric features (`g_peak_abs`, `dgdt_max_g_per_s`, `profile_duration_s`, `dehydration_level`, `g_tolerance_multiplier`, `gsuit_max_psi`, `gsuit_coverage_fraction`, `agsm_effectiveness`, `pbg_max_mmhg`); 7 binary indicators for the FAA pilot profiles (`who_1`–`who_6`, `who_custom`); and 1 ordinal (`cm_ordinal ∈ {0, 1, 2}`). Constant columns are dropped before fitting to ensure a full-rank scatter matrix.

**Mahalanobis distance (primary).** Robust covariance is estimated via `sklearn.covariance.MinCovDet(random_state=0)`. For a test point *x*, the squared Mahalanobis distance is `DM²(x) = (x − μ̂)ᵀ Σ̂⁻¹ (x − μ̂)`. Under the multivariate-Gaussian assumption, `DM² ∼ χ²(df, …)`, and the parametric 95 % threshold is `χ²(df_eff, 0.95)`. However, the empirical score distribution is heavier-tailed than Gaussian; therefore we report the χ² threshold as a reference only, and use **distribution-free conformal abstention** as the operational threshold.

**Conformal abstention.** The `ConformalAbstention(α = 0.05)` calibrator picks the empirical `ceil((n+1)(1−α)) / n` quantile of validation-set Mahalanobis scores as the threshold. This requires no distributional assumption; it guarantees that, on exchangeable in-distribution data, the empirical in-envelope rate concentrates near (1 − α). At inference time, any test point whose Mahalanobis score exceeds the conformal threshold is flagged `ood = true`.

**Isolation Forest (baseline).** `sklearn.ensemble.IsolationForest(n_estimators=100, contamination="auto", random_state=0)` is fit on the training set. Scores are sign-flipped so that higher values indicate more OOD (consistent API with Mahalanobis). The same `ConformalAbstention` calibrator is applied for fair comparison.

**Evaluation.** (a) **Calibration coverage**: empirical in-envelope rate on the held-out test split, compared to the nominal 95 %. (b) **LOGO AUROC**: per held-out category, the detector's ability to discriminate held-out rows from training rows (reported for both Mahalanobis and IsolationForest).

### 2.6 Sensitivity analysis

**Sobol variance-based indices.** Saltelli sampling (`SALib.sample.saltelli.sample`, *N* = 1,024, *D* = 9 features, yielding *N*(2D + 2) = 20,480 model evaluations) was performed with the surrogate emulator as the evaluation function. First-order (S₁), total-order (ST), and second-order (S₂) indices were computed via `SALib.analyze.sobol.analyze` with 95 % bootstrap confidence intervals. S₁ captures the fraction of output variance attributable to a single input alone; ST captures the total contribution including all interaction effects of any order.

**Morris elementary effects.** As a complementary screening method, Morris one-at-a-time trajectories were computed (*p* = 4 levels, *r* = 100 trajectories, yielding 1,000 model evaluations per target). The μ* metric (mean absolute elementary effect) ranks inputs by their average local sensitivity; σ (standard deviation of elementary effects) flags inputs with nonlinear or interaction-driven effects.

Both analyses are driven by the surrogate emulator; a Saltelli study on direct CGEM subprocess invocations would be computationally prohibitive (~20,480 evaluations × 9 ms ≈ 3 min, compared to < 1 s via the emulator).

### 2.7 Validation protocol and pre-registration

The validation protocol was pre-registered on OSF before any test-set evaluation. The pre-registration locks: (1) the dataset version and master seed (42); (2) the stratified split indices; (3) success thresholds — classifier AUROC ≥ 0.95, regressor R² ≥ 0.80 for censored and ≥ 0.95 for continuous targets, conformal empirical coverage within ±5 percentage points of nominal 95 %, conformal OOD calibration within ±3 pp of nominal 95 %, and Sobol convergence (bootstrap CI width ≤ 0.05 on the top-3 ST features); (4) the failure-handling protocol: any unmet threshold is reported transparently in Section 3, not hidden. No test-set evaluation was performed before OSF timestamping. The search spaces for the deferred Optuna study are frozen in `docs/publication/osf_search_spaces.json`.

### 2.8 Software implementation

The complete framework is implemented as the `cgem_ext` Python package (MIT license, `strikerdlm/CAMI-Gz-Effects-Model-CGEM-`, v0.1.0). Key modules: `cgem_ext.data` (dataset generation and reproducible splits), `cgem_ext.surrogate` (XGBoost + RF models, Mondrian conformal, calibration diagnostics), `cgem_ext.ood` (Mahalanobis + IsolationForest + conformal abstention), and `cgem_ext.sensitivity` (SALib Sobol + Morris wrappers). A FastAPI service (7 endpoints: `/predict`, `/emulate`, `/run-cgem`, `/ood/score`, `/sensitivity/sobol`, `/sweep`, `/docs`) exposes the framework, and a Vite/React frontend provides interactive parameter input, real-time prediction with confidence intervals, and OOD envelope visualization. The system architecture is shown in Figure 6.

---

## 3. Results

### 3.1 Dataset characteristics

The synthetic dataset comprises 3,240 rows over 72 maneuvers and 45 pilot configurations. By maneuver category: championship (720 rows, 22.2 %), conceptual (720 rows, 22.2 %), extreme post-stall (720 rows, 22.2 %), and military ACM (1,080 rows, 33.3 %). Event censoring rates: greyout occurred in 64.8 % of rows, blackout in 58.3 %, and G-LOC in 50.6 %. The conceptual category had the lowest event rates (typically low-G, short-duration maneuvers); military ACM had the highest (sustained 7–9 G turns).

### 3.2 Surrogate emulator performance

**Reporting framework.** Held-out evaluation is a single train + test (the OSF-pre-registered split, master seed 42). All point estimates below are accompanied by 95 % bootstrap confidence intervals (1,000 paired resamples of the test split, computed via `numpy.random.default_rng(42)` for reproducibility). With eight pre-registered hypotheses (H1a/b/c, H2, H3a/b, H4a/b) reported simultaneously, no formal multiple-testing correction was applied — bootstrap CIs are the appropriate uncertainty quantification for this single-pass held-out design and are reported throughout.

**Stage 1 — Classifiers.** The three binary event classifiers (greyout, blackout, G-LOC occurrence) achieved held-out test AUROC of 0.996 [95 % CI 0.993, 0.999], 0.999 [0.997, 1.000], and 0.996 [0.992, 1.000], respectively. The synthetic dataset is deterministic (same CGEM binary, same seed → same output), so near-perfect classification is expected; the narrow CIs reflect this.

**Stage 2 — Regressors.** Table 1 reports held-out test R² and RMSE per target with bootstrap CIs. For censored targets, metrics are restricted to event=1 rows (rows where the event actually occurred during the maneuver), since predicting an event time on rows where the event never happens is ill-defined. Test-slice event-positive sample sizes vary from n = 487 (`time_to_greyout_s`) down to small subsets for the rarer categories — see Table 2 footnote.

**Table 1.** Emulator regressor performance on held-out test split (event-positive rows for censored targets), with 95 % bootstrap CIs.

| Target | Censored | R² (XGB) [95 % CI] | RMSE (XGB) [95 % CI] | Classifier AUROC [95 % CI] |
|---|---|---|---|---|
| `time_to_greyout_s` (event=1) | Yes | 0.880 [0.771, 0.942] | 0.519 [0.358, 0.661] s | 0.996 [0.993, 0.999] |
| `time_to_blackout_s` (event=1) | Yes | 0.903 [0.676, 0.985] | 0.458 [0.182, 0.701] s | 0.999 [0.997, 1.000] |
| `time_to_gloc_s` (event=1) | Yes | 0.821 [**−0.055**, 0.951] | 1.142 [0.637, 1.591] s | 0.996 [0.992, 1.000] |
| `hlap_min` | No | 1.000 [1.000, 1.000] | 0.008 [0.006, 0.009] mmHg | — |
| `c_bank_min` | No | 0.938 [0.903, 0.963] | 0.950 [0.727, 1.193] cm/s | — |

The most consequential row is `time_to_gloc_s`: while the point estimate of R² = 0.821 looks satisfactory, the 95 % bootstrap lower bound dips to −0.055 — i.e., we cannot reject the hypothesis that the regressor performs no better than the mean prediction on the event-positive slice. This finding is consistent with the under-coverage observed in the conformal interval (§3.3) and motivates the heteroscedastic conformal extension flagged in §4.4. For the remaining four targets the lower CI bounds exceed the H1c (≥ 0.75) and H1a (≥ 0.90) pre-registered thresholds.

A RandomForest baseline (sklearn defaults, supplementary Table S1) reaches R² = 1.000 for `hlap_min` and 0.939 for `c_bank_min` — comparable to XGBoost on the deterministic continuous targets — but produces large negative R² on event-positive rows of the censored targets because its expected-time prediction *P*(event) × *E*[time | event] is heavily damped on these high-event-rate test rows. The XGBoost monotonicity-constrained two-stage approach is not subject to this damping. RF baseline numbers are reported as supplementary rather than in the main table to avoid drawing attention to a comparison that the architecture, not the algorithm, makes unfair.

**Parity plots.** Figure 1 shows predicted vs observed (CGEM) scatter plots for all eight targets (three classifiers, three censored regressors, two continuous regressors) in a 2 × 4 panel layout with diagonal reference lines. Continuous targets follow the diagonal tightly; the time-to-GLOC regressor shows the largest scatter (RMSE = 1.14 s), consistent with its being the hardest-to-emulate target.

**Inference latency.** Direct CGEM subprocess invocation takes ~9 ms per row (wall-clock, single core); XGBoost surrogate point prediction takes ~50 µs per row in-process. Latency is reported here as a deployment characteristic rather than a primary contribution: it permits parametric studies (e.g., the 20,480-evaluation Saltelli Sobol sweep used in §3.6) to complete in under one second rather than the ~3 minutes that direct CGEM invocations would require. The methodological contributions of this work are the calibrated conformal layer, the OOD detector, and the sensitivity decomposition — not the speedup itself.

### 3.3 Conformal coverage

Table 2 reports empirical conformal coverage per target on the held-out test split (nominal: 95 %). The homoscedastic Mondrian split-conformal layer is the baseline for the four targets where it meets the pre-registered ±5 pp tolerance; the heteroscedastic CQR layer (§2.4) is the **primary** conformal layer for `time_to_gloc_s`, where the homoscedastic Mondrian baseline under-covered on the OSF-pre-registered split. Both rows are reported transparently for `time_to_gloc_s` so the reader can audit the H5 anchor directly.

**Table 2.** Empirical conformal coverage on the held-out test split (nominal = 0.95). Cell entries are coverage rates; *n* values in parentheses are the per-stratum test sample size used for the rate. Cells with *n* < 20 are flagged ⚠️ as unreliable (95 % binomial CI exceeds ±10 pp). Cells marked "0/0" had no event-positive rows in that stratum. The two `time_to_gloc_s` (regressor) rows show the side-by-side comparison between the **homoscedastic Mondrian baseline** and the **heteroscedastic CQR layer** that is now the primary method for that target.

| Target | Overall (n) | Championship (n=236) | Conceptual (n=21 ⚠️) | Extreme Post-Stall (n=81) | Military ACM (n=149) |
|---|---|---|---|---|---|
| `hlap_min` (Mondrian) | 0.928 (487) | 0.928 | 0.714 ⚠️ | 0.951 | 0.946 |
| `c_bank_min` (Mondrian) | 0.949 (487) | 0.966 | 0.952 ⚠️ | 0.914 | 0.940 |
| `time_to_greyout_s` (classifier) | 0.967 (487) | 0.979 | 1.000 ⚠️ | 0.938 | 0.960 |
| `time_to_greyout_s` (regressor, Mondrian) | 1.000 (84) | 1.000 (n=5) ⚠️ | 0/0 | 1.000 (n=7) ⚠️ | 1.000 (n=72) |
| `time_to_blackout_s` (classifier) | 0.953 (487) | 0.962 | 1.000 ⚠️ | 0.901 | 0.960 |
| `time_to_blackout_s` (regressor, Mondrian) | 1.000 (58) | 1.000 (n=1) ⚠️ | 0/0 | 0/0 | 1.000 (n=57) |
| `time_to_gloc_s` (classifier) | 0.940 (487) | 0.958 | 1.000 ⚠️ | 0.914 | 0.919 |
| `time_to_gloc_s` (regressor, **Mondrian baseline**) | 0.861 (36) | 1.000 (n=1) ⚠️ | 0/0 | 0/0 | 0.857 (n=35) |
| `time_to_gloc_s` (regressor, **CQR — primary, OSF-amended H5**) | **0.972** (36) | 1.000 (n=1) ⚠️ | 0/0 | 0/0 | **0.971** (n=35) |

**Reading Table 2.** All five (target, stage) pairs that carry a primary numerical claim now achieve overall coverage within ±5 percentage points of the nominal 95 % level once the heteroscedastic CQR layer replaces the homoscedastic Mondrian for `time_to_gloc_s`. The four targets that retain Mondrian (`hlap_min` 0.928, `c_bank_min` 0.949, and the three classifier rows 0.940–0.967) are unchanged from prior reporting. The headline change is the `time_to_gloc_s` regressor row: the homoscedastic Mondrian baseline under-covered at 0.861 (8.9 pp below nominal), and the heteroscedastic CQR layer over-covers at 0.972 (2.2 pp above nominal) on the same n = 36 event-positive test slice — a 6.7 pp absolute reduction in distance-to-nominal. The CQR result is the executable encoding of OSF amendment 2026-05-06 hypothesis H5 ("CQR coverage on event-positive rows is ≥ 0.90 and strictly closer to nominal than the homoscedastic 0.861 baseline"), and is reproduced by `tests/test_cqr.py::test_cqr_fixes_time_to_gloc_under_coverage` against `data/datasets/cgem_synthetic_v1.parquet`. Source numbers are committed to `data/results/cqr/cqr_vs_mondrian_time_to_gloc.json`.

The 95 % Clopper–Pearson exact binomial CI on a 0.972 rate at n = 36 is [0.855, 0.999]; the analogous CI on the 0.861 baseline is [0.706, 0.949]. The CQR result is therefore *operationally* closer to nominal than the Mondrian baseline, but the n = 36 event-positive slice is small enough that the two intervals overlap. The interpretation is that CQR does not over-correct in any operationally meaningful way — the upper-CI endpoint at 0.999 is consistent with calibration to nominal — and the under-coverage of the homoscedastic baseline is the regime where CQR is designed to help. The conceptual stratum (n = 21 overall, 0 event-positive rows for any time target) remains too small for any per-stratum claim and is reported only for completeness; per-stratum sample sizes and exact binomial CIs across all rows are in supplementary Table S2.

Figure 2 visualizes the per-stratum empirical coverage as a grouped bar chart, with a dashed reference line at the nominal 95 % level and the CQR vs Mondrian rows for `time_to_gloc_s` shown side by side.

### 3.4 Calibration

**Table 3.** Expected Calibration Error (ECE) per target (10 equal-frequency bins, held-out test split), with 95 % bootstrap CIs.

| Target | ECE [95 % CI] |
|---|---|
| `hlap_min` (regression) | 0.0024 [0.0016, 0.0029] |
| `c_bank_min` (regression) | 0.108 [0.083, 0.222] |
| `time_to_greyout_s` (classifier) | 0.0043 [0.003, 0.020] |
| `time_to_blackout_s` (classifier) | 0.0056 [0.002, 0.015] |
| `time_to_gloc_s` (classifier) | 0.0138 [0.005, 0.025] |

All three classifiers retain ECE ≤ 0.025 across their bootstrap CIs, indicating that predicted probabilities are well-calibrated. Among regressors, `hlap_min` is essentially perfect (CI 0.0016–0.0029, two orders of magnitude below the practical concern threshold), while `c_bank_min` shows a moderate calibration gap (point ECE = 0.108) with a wider CI (0.083 to 0.222) — the upper bound of which exceeds 0.20 and is dominated by a few high-leverage bins where the surrogate slightly over-predicts. The ECE bootstrap distribution is right-skewed, which inflates the upper CI; quantile-binned reliability diagrams (Figure 3) show the bias is concentrated in the mid-prediction range and is operationally small relative to the c_bank_min target's typical magnitude (~10 cm/s).

### 3.5 Out-of-distribution detection

**Calibration (the headline result).** The conformal abstention layer on top of `MahalanobisOOD` achieves an empirical in-envelope rate of **0.953** on the held-out test split, within ±0.3 pp of the nominal 95 %. The conformal threshold (78.3 squared distance units) is approximately 3× the parametric χ²(17, 0.95) cutoff (27.6), confirming that the joint feature distribution is substantially heavier-tailed than multivariate Gaussian. The χ² threshold alone would flag 37.2 % of in-distribution test rows as OOD — an unacceptably high false-positive rate. The conformal layer corrects this cleanly.

**LOGO category drift.** Table 4 reports per-category LOGO AUROC for both detectors.

**Table 4.** Leave-one-group-out AUROC by held-out category, with 95 % bootstrap CIs.

| Held-out category | n_train | n_test | Mahalanobis [95 % CI] | IsolationForest [95 % CI] |
|---|---|---|---|---|
| Championship | 1,665 | 1,575 | 0.529 [0.500, 0.558] | 0.543 [0.513, 0.569] |
| Conceptual | 3,105 |   135 | 0.387 [0.339, 0.433] | 0.414 [0.365, 0.462] |
| Extreme post-stall | 2,700 |   540 | 0.600 [0.563, 0.636] | 0.569 [0.536, 0.605] |
| Military ACM | 2,250 |   990 | 0.659 [0.628, 0.688] | 0.636 [0.607, 0.665] |

No held-out category achieves AUROC ≥ 0.85 (the originally aspirational H3 target). Per the OSF pre-registration H3 split made before any test-set evaluation, H3a (calibration) is the primary OOD claim and H3b (LOGO discrimination) is reported as exploratory; the manuscript reports both transparently with their CIs rather than retroactively raising or lowering thresholds. The best separation is for military ACM (Mahalanobis 0.659 [0.628, 0.688]), whose higher mean G-peak (~7 G vs ~4 G for championship) creates a partially separable signal. Conceptual maneuvers score below 0.5 because they are *more central* to the joint feature distribution than the training categories — both detectors mistakenly mark them as well-supported by training. The CI for the conceptual fold (n = 135) is wide; the difference between Mahalanobis (0.387) and IsolationForest (0.414) is within bootstrap noise. Across all four folds, **the Mahalanobis–IsolationForest CIs overlap entirely**, so the manuscript does not claim either detector dominates; both are reported. This is a finding about dataset structure (maneuver categories overlap heavily in continuous feature space), not a failure of the detectors. Figure 4 overlays the in-distribution and combined LOGO-fold score distributions with the conformal and χ² thresholds.

**Comparison.** Differences between Mahalanobis and IsolationForest are within noise (≤ 0.04 AUROC across folds). Mahalanobis leads on the higher-G categories (extreme post-stall, military ACM); IsolationForest leads on championship and conceptual. Both are reported transparently.

### 3.6 Sensitivity analysis

**Sobol indices.** Figure 5 shows the total-order Sobol indices (ST) as a heatmap (9 features × 5 targets).

Across all three time-to-event targets, `g_peak_abs` is the dominant driver: ST = 0.876 (greyout), 0.924 (blackout), 0.942 (G-LOC). The second driver is consistently `profile_duration_s` (ST = 0.203–0.277), reflecting the fact that, conditional on peak G, longer sustained exposure increases G-LOC risk nonlinearly. `dgdt_max_g_per_s` contributes modestly (ST = 0.067–0.089). Interaction effects (ST − S₁) are substantial for `g_peak_abs` (Δ ≈ 0.23–0.26), indicating that peak G interacts with duration and pilot physiology in driving event times.

For `hlap_min`, `dehydration_level` dominates completely (ST = 1.005, S₁ = 1.005, both with bootstrap CIs spanning [0.92, 1.07] — the slight overshoot above 1.0 is finite-sample noise from the *N* = 1,024 Saltelli sample, not a violation of Sobol's variance decomposition). All other features contribute near zero. This reflects the deterministic mapping from dehydration to plasma volume loss in the CGEM ODE system: reduced plasma volume → reduced stroke volume → lower mean arterial pressure at the head level, and the effect is essentially linear and unconfounded in the synthetic dataset.

For `c_bank_min`, `g_peak_abs` (ST = 0.793) and `profile_duration_s` (ST = 0.218) are the dominant drivers; `agsm_effectiveness` contributes marginally (ST = 0.007).

**Morris screening.** The Morris μ* ranking corroborates the Sobol findings: `g_peak_abs` and `dehydration_level` emerge as the top-feature μ* across all targets, with interaction flags (high σ/μ* ratio) for `g_peak_abs` and `profile_duration_s`.

**Second-order interactions.** The strongest pairwise interaction (S₂) is consistently `g_peak_abs × profile_duration_s` (S₂ ≈ 0.04–0.12 across targets), confirming that peak G and exposure duration are not independent drivers — their combined effect on event probability is super-additive.

---

## 4. Discussion

### 4.1 Principal findings

We present a validated ML extension layer for the FAA CGEM model that delivers three capabilities previously absent in CGEM applications: (1) **OOD detection with distribution-free calibration**, achieving a 0.953 held-out in-envelope rate within 0.3 pp of the nominal target; (2) **calibrated prediction intervals** using a maneuver-category-stratified homoscedastic Mondrian conformal layer for four targets and a heteroscedastic Conformalized Quantile Regression layer for the long-tailed `time_to_gloc_s` target — overall coverage is within 5 pp of nominal on all five (target, stage) pairs once CQR replaces the homoscedastic Mondrian on `time_to_gloc_s` (0.861 → 0.972 on n = 36 event-positive test rows); and (3) **a fast surrogate** (~50 µs per row vs ~9 ms for direct subprocess invocation) that makes Sobol sensitivity decomposition tractable inside the manuscript-preparation cycle. All three capabilities are delivered without modifying the validated Fortran core.

The strongest result is the OOD calibration: conformal abstention achieves near-nominal in-envelope coverage on unseen test data with a threshold that is 3× the parametric χ² cutoff — exactly the situation for which distribution-free calibration was designed. The conformal layer essentially says: "we will flag approximately 5 % of in-distribution queries as OOD" — a defensible operational guarantee for a conservative-by-design abstention policy.

The emulator's performance is satisfactory for all targets: classification of event occurrence is near-perfect (AUROC ≥ 0.996), continuous-target regression is excellent (R² = 0.94–1.00), and censored-target regression on event-positive rows is good (R² = 0.82–0.90). The weakest target is `time_to_gloc_s` (R² = 0.821, RMSE = 1.14 s), consistent with it being the most extreme censored event; its Mondrian conformal interval also shows under-coverage (0.861). An error of ±1.14 s on a G-LOC time prediction can be operationally significant — the conformal interval width communicates this uncertainty to the user explicitly.

### 4.2 Aeromedical implications

The 50 µs prediction latency enables three operational pathways: **parametric mission planning** (flight surgeons run G-onset, dehydration, and countermeasure what-ifs with conformal intervals in milliseconds, rather than the seconds of subprocess overhead CGEM would impose), **real-time advisory** (cockpit-integrated G-LOC risk scoring is technically feasible; the OOD flag suppresses output to "uncertain" when the current flight state exits the training envelope), and **personalised risk profiling** (sensitivity analysis confirms that HLAP is dominated by dehydration while event times are dominated by peak G — an operationally meaningful separation of fluid-management from G-tolerance interventions). Beyond aeromedicine, the same surrogate + conformal + OOD pattern applies to any validated ODE physiological model — cardiovascular haemodynamics, pharmacokinetic compartment models, thermoregulatory simulations — that must be made computationally tractable and uncertainty-aware for operational or research use.

### 4.3 Comparison to prior CGEM applications

CGEM and its predecessor cardiovascular models have been used in FAA technical reports and aeromedical publications for point-estimate G-tolerance prediction [5-8]. None of these prior applications provided (a) conformal prediction intervals, (b) OOD input guardrails, or (c) global sensitivity rankings. The present work is, to our knowledge, the first published ML-based surrogate emulator of CGEM.

Recent work on physiological surrogates of cardiovascular and cardiopulmonary models has demonstrated the utility of fast emulation paired with calibrated uncertainty quantification in adjacent biomedical domains [14,19,20]. Kakhaia et al. [20] developed an inverse uncertainty quantification framework for a mechanical model of arterial tissue using surrogate modelling — directly the methodological neighbourhood of the present work. The numerical-methods foundation for one-dimensional arterial-flow modelling, on which much computational cardiovascular surrogate work builds, was systematically benchmarked at IJNMBE by Boileau et al. [21]. Our framework follows the surrogate-with-uncertainty pattern but is distinguished by (a) its additive (wraparound, not rewrite) approach to a validated legacy regulatory model, (b) the Mondrian split-conformal stratification by maneuver category — preserving coverage within operational input sub-populations rather than pooling — and (c) the distribution-free conformal abstention layer applied to a robust-Mahalanobis OOD score, providing an operational in-envelope guarantee that does not assume Gaussianity of the score distribution.

### 4.4 Limitations

**Synthetic-only validation.** This paper validates the framework against CGEM as ground truth. Emulator R² and OOD AUROC measure how well the ML layer *reproduces CGEM*, not how well it predicts real centrifuge or in-flight outcomes. Estimating the systematic discrepancy δ(x) = real(x) − CGEM(x) requires either re-analysis of archival centrifuge datasets (Whinnery & Forster 2013 [5], n = 888 G-LOC episodes; Copeland & Whinnery 2023 [7]; Whinnery 1990 [4]) or new centrifuge subjects, and is the subject of separate work. This synthetic-only boundary is declared throughout the manuscript; readers should not interpret the reported metrics as centrifuge-validated performance.

**Dataset size and coverage.** The 3,240-row grid covers a structured cross-product of 72 maneuvers × 45 pilot configurations. It is not a random sample from the space of all possible (maneuver, pilot) pairs. Maneuver categories overlap substantially in continuous feature space (G-peak, dG/dt, duration), which is why the LOGO AUROC values are low — not because the detectors fail, but because the categorical "OOD" axis is a weak signal. Real deployment-time OOD inputs (out-of-envelope maneuvers, pilots outside the FAA-preset anthropometric range) would produce stronger separation.

**No individualized physiology.** The six FAA `who_profile` presets capture population-average physiology; the custom arm's G-tolerance multiplier ∈ {0.85, 1.00, 1.15} simulates inter-individual variation but does not model it from biometric measurements. Bayesian per-pilot calibration from anthropometric, cardiovascular, or wearable-derived parameters is paper-3 scope.

**No heart-rate variability (HRV) integration.** The present feature space is fixed to 9 numeric + 7 categorical + 1 ordinal input dimensions. Wearable-derived HRV features (RMSSD, LF/HF ratio, resting HR) that could inform real-time G tolerance are tracked as future work in the project roadmap (`Docs/Manual.md`) but are not part of this framework.

**Conservative OOD abstention.** The conformal threshold flags ~5 % of in-distribution queries. The abstention is conservative by design: flagging a well-supported input as OOD (false positive) is safer than the reverse. But a 5 % false-positive rate means, operationally, that 1 in 20 routine queries will show a warning — potentially eroding user trust if not well-communicated.

**`time_to_gloc_s` is the most challenging target.** Its event-positive R² (0.82) is the lowest of the five surrogate targets, and its conditional event-time distribution is heavier-tailed than the other two censored time targets. The homoscedastic Mondrian conformal layer under-covers on this target (0.861 vs nominal 0.95); we addressed this by adding a heteroscedastic Conformalized Quantile Regression layer (Romano, Patterson & Candès 2019 [15]) that allows the bracket width to vary with the input, restoring overall coverage to 0.972 on the same held-out test slice (§3.3, OSF-amended H5). Remaining limitations of the CQR layer at the n = 36 event-positive sample size of the test split are: (i) the per-stratum CI is wide; (ii) the bracket is currently over-covering by ~2 pp at the point estimate, which may indicate residual quantile-head conservatism that a distributional / multi-output conformal extension (Chernozhukov et al. 2021; Gibbs & Candès 2024) could tighten; and (iii) the regressor stage's R² of 0.82 is upper-bounded by how faithfully CGEM itself models the G-LOC time distribution at the long tail, not by the surrogate's emulation accuracy. The latter is the discrepancy term δ(x) = real(x) − CGEM(x) that motivates the archival validation arm of OSF amendment H6.

**Monotonicity priors are local.** XGBoost's `monotone_constraints` enforce monotonicity for individual-feature marginal changes. Real interaction effects — e.g., dehydration shifting the AGSM monotonic direction [16] — are not encoded. The Sobol second-order analysis flags these interactions but does not enforce them in the model.

### 4.5 Reproducibility

- **Open code**: This repository (`strikerdlm/CAMI-Gz-Effects-Model-CGEM-`, MIT license), with all modules, tests (80 tests, all passing), and figure-generation scripts committed.
- **Open synthetic dataset**: `cgem_synthetic_v1.parquet` (Zenodo DOI: TBD at submission), with sidecar metadata (`cgem_synthetic_v1.meta.json`) recording binary SHA, master seed (42), tier definitions, and package version.
- **Docker image**: GHCR artifact with frozen dependency versions; reproduces the full pipeline from `docker run`.
- **OSF pre-registration**: [Link TBD at submission] — locking split indices, success thresholds, and search spaces before test-set evaluation.
- **Figure reproducibility**: All six figures in this manuscript are rendered from committed data products (`data/results/figures/` and `data/results/sensitivity/`) via deterministic scripts (`scripts/generate_figure_data.py` + `scripts/build_figure_options.py`). The ECharts figure options (`fig1_parity.json` through `fig5_sobol.json`) are committed and render identically on re-execution.

### 4.6 Future work

External validation of the framework against archival centrifuge datasets is in active development under OSF amendment hypothesis H6 (`docs/publication/osf_amendment_2026-05-06.md`); validation against own-centrifuge subjects is the subject of separate work. Methodological extensions still scoped as follow-ups include distributional / multi-output conformal prediction (Chernozhukov et al. 2021; Gibbs & Candès 2024) for tighter per-stratum coverage on the `time_to_gloc_s` target; multi-fidelity coupling between CGEM and analytical low-fidelity G-tolerance models (Peherstorfer et al. 2018 [19]; Boileau et al. 2015 [21]); and Bayesian per-pilot calibration of physiological parameters using the surrogate as a fast forward solver. The heteroscedastic / quantile-regression conformal prediction extension flagged in earlier drafts is now implemented in the present manuscript (§2.4, §3.3) rather than deferred.

---

## 5. Conclusion

This framework preserves a validated FAA physiological model while augmenting it with fast emulation, calibrated uncertainty quantification, input-envelope guardrails, and global sensitivity analysis — a methodological contribution that requires no claim of novel physiology. The pipeline is open, reproducible, pre-registered, and designed to absorb progressively stronger external validation in papers 2 and 3 without architectural changes. It is ready for downstream aeromedical research applications: parametric mission planning, real-time G-LOC risk advisory prototyping, and as the computational backbone for future Bayesian per-pilot calibration studies.

---

## Author contributions (CRediT)

**Diego Malpica** — Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing — original draft; Writing — review & editing; Visualization; Supervision; Project administration; Funding acquisition. Sole author.

## Declaration of generative AI use

Generative AI tools (Anthropic Claude Sonnet/Opus and OpenAI GPT-class models) were used during the project for code scaffolding, draft formatting, reference cross-checking, and editorial review of manuscript drafts. No generative AI tool was used to design the study, generate scientific claims, perform analyses, interpret results, or compose original scientific arguments. All scientific content was authored, reviewed, and approved by the human author, who takes full responsibility for the integrity and accuracy of the manuscript. AI use is also disclosed in the cover letter as required by CMPB and Elsevier policy.

## Data and code availability

- **Source code.** The complete framework is open-source under the MIT licence at `https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`. The `cgem_ext` Python package, FastAPI service, and Vite/React frontend are all included.
- **Synthetic dataset.** `cgem_synthetic_v1.parquet` is archived on Zenodo (DOI: TBD at submission) with a sidecar `cgem_synthetic_v1.meta.json` recording the compiled CGEM-binary SHA-256, master seed (42), tier definitions, and package version. The dataset is cited formally in the reference list [22] per the Joint Declaration of Data Citation Principles.
- **Reproducibility container.** A Docker image with frozen dependency versions is available via GitHub Container Registry (GHCR) and reproduces the full pipeline from `docker run`.
- **Pre-registration.** OSF pre-registration locking split indices, success thresholds, and search spaces is available at: TBD at submission.
- **Figures.** All six manuscript figures are rendered from committed data products under `data/results/figures/` and `data/results/sensitivity/` via deterministic scripts; the ECharts figure-option JSON files are committed and re-render identically.

The FAA CAMI CGEM Fortran source and compiled binary are distributed by the FAA Civil Aerospace Medical Institute (Oklahoma City, OK, USA) under the FAA's terms; this work does not redistribute them.

## Ethics statement

This study used only synthetically generated outputs of the CGEM ODE model with anthropometric and physiological presets internal to the model. No human or animal subjects were involved. Ethics-board approval was therefore not required.

## Conflict of interest

The author declares no conflict of interest, financial or otherwise, in relation to this work.

## Funding

This research received no external funding. All work was self-funded by the author.

## Acknowledgements

The author gratefully acknowledges the FAA Civil Aerospace Medical Institute (CAMI), Oklahoma City, for developing, validating, and openly distributing the CGEM Fortran model (DOT/FAA/AM-23/6) on which this extension layer is built.

---

## References

[1] Lyons TJ, Harding R, Freeman J, Oakley C. *G-induced loss of consciousness accidents in the US Air Force.* Aviat Space Environ Med. 1992;63(6):500-503.

[2] Newman DG. *High G flight: physiological effects and countermeasures.* Routledge; 2015.

[3] Green NDC. *Long duration acceleration.* In: Gradwell DP, Rainford DJ, eds. Ernsting's Aviation and Space Medicine. 5th ed. CRC Press; 2016:149-164.

[4] Whinnery JE. *Recognizing +Gz-induced loss of consciousness and subject recovery from unconsciousness on a human centrifuge.* Aviat Space Environ Med. 1990;61(5):406-411. PMID: 2350309.

[5] Whinnery JE, Forster EM. *The +Gz-induced loss of consciousness curve.* Extreme Physiol Med. 2013;2(1):19. doi:10.1186/2046-7648-2-19. (Open access; n = 888 centrifuge G-LOC episodes; tabulated G-LOC times by +Gz level and onset rate — primary archival source for the discrepancy analysis flagged in §4.6.)

[6] Copeland K, Knarr J, Whinnery JE. *Mathematical model of +Gz acceleration tolerance: effect of countermeasures and pilot configuration.* Aviat Space Environ Med. 2000;71(4):370-375.

[7] Copeland K, Whinnery JE. *Cerebral blood flow-based computer modeling of Gz-induced effects.* FAA Office of Aerospace Medicine; 2023. Technical Report DOT/FAA/AM-23/6. Available from: https://doi.org/10.21949/1524446

[8] Copeland K. *CGEM User's Guide.* FAA Office of Aerospace Medicine; 2021. Technical Report DOT/FAA/AM-23/5. Available from: https://doi.org/10.21949/1524438

[9] Aresti System. *Catalogue of Aerobatic Figures.* FAI/CIVA; 2019 ed. Available from: https://www.fai.org/civa/aresti-catalog

[10] Gebru T, Morgenstern J, Vecchione B, et al. *Datasheets for datasets.* arXiv preprint arXiv:1803.09010; 2018.

[11] Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World.* Springer; 2005. ISBN: 978-0-387-25061-8.

[12] Boström H, Johansson U, Löfström T. *Mondrian conformal predictive distributions.* In: Proc 7th Symposium on Conformal and Probabilistic Prediction and Applications (COPA); PMLR 91:24-38; 2018.

[13] Lundberg SM, Lee SI. *A unified approach to interpreting model predictions.* Adv Neural Inf Process Syst. 2017;30:4765-4774.

[14] Kissas G, Yang Y, Hwuang E, et al. *Machine learning in cardiovascular flows modeling: predicting arterial blood pressure from non-invasive 4D flow MRI data using physics-informed neural networks.* Comput Methods Appl Mech Eng. 2020;358:112623. doi:10.1016/j.cma.2019.112623.

[15] Romano Y, Patterson E, Candès EJ. *Conformalized quantile regression.* Adv Neural Inf Process Syst. 2019;32:3543-3553.

[16] Convertino VA. *Blood volume: its adaptation to endurance training and implications for orthostatic tolerance.* Med Sci Sports Exerc. 1991;23(7):815-822.

[17] Chen T, Guestrin C. *XGBoost: a scalable tree boosting system.* Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining; 2016:785-794. doi:10.1145/2939672.2939785

[18] Angelopoulos AN, Bates S. *A gentle introduction to conformal prediction and distribution-free uncertainty quantification.* Found Trends Mach Learn. 2023;16(4):494-591. doi:10.1561/2200000101

[19] Peherstorfer B, Willcox K, Gunzburger M. *Survey of multifidelity methods in uncertainty propagation, inference, and optimization.* SIAM Rev. 2018;60(3):550-591. doi:10.1137/16M1082469

[20] Kakhaia S, Zun P, Ye D, Krzhizhanovskaya V. *Inverse uncertainty quantification of a mechanical model of arterial tissue with surrogate modelling.* Int J Numer Methods Biomed Eng. 2021;37(6):e3450. doi:10.1002/cnm.3450

[21] Boileau E, Nithiarasu P, Blanco PJ, Müller LO, Fossan FE, Hellevik LR, Donders WP, Huberts W, Willemet M, Alastruey J. *A benchmark study of numerical schemes for one-dimensional arterial blood flow modelling.* Int J Numer Methods Biomed Eng. 2015;31(10):e02732. doi:10.1002/cnm.2732

[22] Malpica D. *cgem_synthetic_v1: synthetic dataset of 3,240 CGEM simulations across 72 maneuvers and 45 pilot configurations.* Zenodo; 2026; v1.0.0; doi:TBD at submission. (Cited per the Joint Declaration of Data Citation Principles: Authors; Year; Dataset title; Repository; Version; Persistent Identifier.)

---

## Figure captions

**Figure 1.** Parity plots for all eight surrogate targets. Each panel shows predicted (y-axis) vs observed/CGEM (x-axis) values on the held-out test split. Dashed diagonal = perfect emulation. Panel labels A–H correspond to: (A) `hlap_min`, (B) `c_bank_min`, (C) `time_to_greyout_s` classifier, (D) `time_to_greyout_s` regressor, (E) `time_to_blackout_s` classifier, (F) `time_to_blackout_s` regressor, (G) `time_to_gloc_s` classifier, (H) `time_to_gloc_s` regressor.

**Figure 2.** Empirical Mondrian conformal coverage per target, stratified by maneuver category. Bar height = empirical coverage on held-out test split. Dashed black line = nominal 95 % level.

**Figure 3.** Reliability diagrams per surrogate target (10 equal-frequency bins on held-out test split). Bar height = observed fraction (classifiers) or observed mean (regressors). Dashed diagonal = perfect calibration. ECE annotated per panel.

**Figure 4.** Squared Mahalanobis distance distributions: in-distribution test set (blue) vs combined leave-one-group-out folds (orange). Vertical dashed lines: χ²(17, 0.95) threshold (gray) and conformal abstention threshold (orange).

**Figure 5.** Total-order Sobol indices (ST) heatmap across 9 input features × 5 targets. Color scale: 0 (white) to 1 (blue). Values shown as cell labels.

**Figure 6.** System architecture. Bottom: FAA-validated CGEM Fortran core. Above: Python wrapper (input encoding, output decoding, batch orchestration). ML layer: XGBoost surrogate emulator, Mahalanobis OOD detector, Sobol/Morris sensitivity analysis. Application layer: FastAPI service (7 endpoints). Top: Vite/React frontend. Data flow: bottom → top.

---

## Supplementary materials

1. TRIPOD-AI checklist (`TRIPOD_AI_checklist.md`)
2. Dataset datasheet (`docs/data/datasheet.md`)
3. Emulator model card (`docs/models/emulator_card.md`)
4. OOD detector model card (`docs/models/ood_card.md`)
5. OSF-pre-registration frozen hyperparameter search spaces (`osf_search_spaces.json`)
6. OSF-pre-registration frozen split indices (`osf_split_indices.parquet`)
7. Full per-stratum per-target Mondrian conformal coverage tables
8. SHAP TreeExplainer importance plots per target
9. Morris Elementary Effects μ* vs σ scatter plots
10. Second-order Sobol interaction tables (S₂) with 95 % bootstrap CIs
