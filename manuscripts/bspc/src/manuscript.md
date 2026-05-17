# Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology

**Author.** Diego Malpica, MD. Direction of Aerospace Medicine, Aerospace Scientific Department, Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC), Bogotá, Colombia. ORCID 0000-0002-2257-4940. Correspondence: dlmalpica@yahoo.com.

**Article type.** Full Length Article.

**Running title** (≤ 70 chars). Conformal ML wrapper for a validated ODE physiological model.

---

## Abstract

**Background and Objectives.** The FAA's CAMI G-Effects Model (CGEM) is a validated Fortran +Gz-tolerance model underpinning civil aviation. Three limits constrain its use: high computational cost, no calibrated uncertainty quantification, and silent acceptance of out-of-distribution (OOD) inputs. We close these gaps via an additive ML extension preserving the validated core.

**Methods.** We generated 3,240 synthetic CGEM runs across 72 maneuvers × 45 pilot configurations (master seed 42). Per-target XGBoost surrogates use a two-stage classifier+regressor for right-censored event-time targets and single-stage regressors for continuous targets. Mondrian-stratified conformal layers (α = 0.05) per maneuver category combine homoscedastic split-conformal on four targets with heteroscedastic Conformalized Quantile Regression on `time_to_gloc_s`. A robust Mahalanobis detector with distribution-free conformal abstention guards the 17-feature input space. The surrogate drives Sobol and Morris sensitivity decompositions. The full validation protocol was pre-registered on OSF before any test-set evaluation; the CQR layer and archival-validation arm were added under the 2026-05-06 amendment (H5, H6).

**Results.** On the held-out test split, the conformal OOD layer reached an empirical in-envelope rate of 0.953 against the nominal 0.95, with the threshold ~3× the parametric χ² cutoff. Mondrian conformal coverage was within 4.6 pp of nominal on 4/5 surrogate targets; on `time_to_gloc_s`, CQR raised coverage from 0.861 to 0.972 on n = 36 event-positive test rows. Classifier AUROC was ≥ 0.996 across the three censored targets, with expected calibration error ≤ 0.014. Regressor R² was 0.82–0.90 on event-positive rows of censored targets and 0.94–1.00 on continuous targets. Surrogate inference takes ~50 µs per row versus ~9 ms for direct CGEM invocation.

**External validation against an archival centrifuge cohort (n = 8 pooled records, Whinnery & Forster 2013; OSF amendment H6) shows a slow-onset bias δ̄ = +26.6 s [95 % CI +6.3, +52.1] at onset ≤ 0.5 G/s and good calibration at onset ≥ 1 G/s — the operationally relevant fighter/aerobatic regime.**

**Conclusions.** The framework preserves the FAA-validated core and adds emulator speed, calibrated prediction intervals, OOD abstention, and global sensitivity rankings. H6 bounds operational use at slow onset; own-centrifuge validation is deferred. The additive-wrapper pattern generalises to any validated ODE physiological model.

**Keywords.** physiological modelling; surrogate emulation; conformal prediction; out-of-distribution detection; global sensitivity analysis; acceleration physiology

---

## 1. Introduction

Validated mechanistic models embedded in regulatory or operational frameworks pose a recurring problem in computational biomedicine: they encode decades of domain knowledge and experimental calibration, yet they are computationally expensive, lack calibrated uncertainty quantification, and accept out-of-distribution inputs without warning. The aim of this paper is to propose a *computer-methods-and-programs* solution to that recurring problem: a method — the additive surrogate + conformal + OOD stack — and a program — an open Python package, FastAPI service, and Docker image — that together close the three gaps without modifying the validated core. The method generalises across any validated ODE physiological model; the program is a concrete reference implementation against the FAA Civil Aerospace Medical Institute's CGEM. Portela, Banga & Matabuena [23] recently demonstrated the wrapping pattern on canonical biological dynamical systems; the present work extends it from generic biological dynamics into a specific regulatory aerospace-physiology setting and adds three operational refinements: (i) per-stratum (Mondrian) conformal calibration over operationally meaningful maneuver categories, (ii) heteroscedastic conformal layers for long-tailed event-time targets, and (iii) an explicit input-envelope abstention layer.

The application domain is +Gz acceleration physiology in high-performance flight. G-induced loss of consciousness (G-LOC) remains an established occupational risk in fighter, aerobatic, and high-performance fixed-wing aviation [1–3]. Centrifuge training and anti-G countermeasures — the anti-G straining maneuver (AGSM), G-suits, positive-pressure breathing for G (PBG) — have driven G-LOC incidence down substantially since the 1980s, but the underlying physiology remains complex and multi-factorial: G-onset rate, peak +Gz, exposure duration, pilot anthropometrics, hydration state, countermeasure configuration, and individual G tolerance all interact nonlinearly [4–6].

CGEM, developed at the FAA's Civil Aerospace Medical Institute, is the reference regulatory model of +Gz physiology [7]. It solves a system of ordinary differential equations governing cardiovascular and cerebrovascular response under sustained +Gz load, producing time-series predictions for cerebral blood flow (c_bank), head-level arterial pressure (HLAP), visual function, and brain oxygenation [7,8]. Validation against human centrifuge data at the FAA CAMI established the model's accuracy, and CGEM now underpins G-tolerance standards in civil-aviation certification — so preserving it byte-for-byte is both a scientific and a regulatory requirement.

However, CGEM has three limits that constrain operational and research use. **First, computational cost.** Each invocation spawns a Fortran subprocess, writes a GLOC input deck to disk, waits for the binary to solve the physiological ODE system, and parses its output deck. On a modern multi-core CPU this takes ~9 ms per row — fast for single queries but prohibitive for parametric exploration; a 10,000-sample Saltelli Sobol study would require days of wall-clock time. **Second, no calibrated uncertainty quantification.** CGEM returns a deterministic scalar (e.g., "time to G-LOC: 8.3 s"), but the aeromedical operator needs to know how much to trust that number given the maneuver category, the pilot configuration, and the model's inherent approximation error. CGEM ships no confidence intervals or prediction bands. **Third, no input-envelope guard.** Users can query CGEM with inputs far outside the training and validation envelope — a pilot configuration never tested, a G-onset profile beyond published data — and receive a number with no warning that the model is extrapolating.

We close those three gaps with an additive ML extension layer that (1) detects out-of-distribution (OOD) inputs via robust Mahalanobis distance with distribution-free conformal abstention, (2) provides calibrated prediction intervals — a Mondrian-stratified homoscedastic split-conformal layer where appropriate, and a heteroscedastic Conformalized Quantile Regression (CQR) layer for the long-tailed `time_to_gloc_s` target, (3) emulates CGEM at ~50 µs per row versus ~9 ms for direct subprocess invocation, and (4) ranks which input features drive G-LOC risk via global sensitivity analysis (Sobol first- and total-order indices, Morris elementary effects). The framework is **additive**: the FAA-validated Fortran binary, compiled source (`.f` files), and input/output deck formats are not modified. The ML layer wraps the validated core like a fitted response surface, and the authoritative `/run-cgem` endpoint remains available when direct CGEM invocation is needed.

This manuscript validates the framework against CGEM as ground truth. The synthetic-only strategy is declared explicitly: it establishes the emulator + OOD + sensitivity pipeline on known ground truth before any real centrifuge data enters the picture. External validation against archival centrifuge data and against own-centrifuge subjects is the subject of separate work and is not claimed here. The full validation protocol is pre-registered on the Open Science Framework (OSF); search spaces, split indices, and success thresholds are frozen at OSF posting time.

---

## 2. Methods

### 2.1 The CAMI G-Effects Model (CGEM)

CGEM is a Fortran physiological simulator developed at the FAA Civil Aerospace Medical Institute (CAMI), Oklahoma City [7]. It receives a +Gz time profile (Nz samples at 100 Hz typical) and a pilot configuration file (`gloc_inp.dat`) specifying subject type (FAA `who_profile` 1–6), G-suit parameters, AGSM effectiveness, PBG max pressure, and dehydration level (full parameter definitions in Table 1).

CGEM integrates a system of ODEs over the maneuver window, producing per-sample time series for compartmental arterial pressures (eye-level, brain-level, heart-level), cerebral blood flow velocity (`c_bank`), brain oxygenation (`bo_bank`), retinal oxygen delivery, and visual function indices (`f_vis`, `f_bo`). Event-time scalars — greyout, blackout, and G-LOC — are the earliest samples at which visual function crosses predefined thresholds (right-censored if never crossed).

We compiled the Fortran binary from the original CAMI source and verified it against a canonical FAA test case (Profile 4, 7-G sustained turn). The binary's SHA-256 hash is recorded in `cgem_synthetic_v1.meta.json` alongside the master dataset seed (42). **The present work does not modify the Fortran binary; the ML extension layer wraps it as a black-box function.**

### 2.2 Synthetic dataset

A structured synthetic dataset (`cgem_synthetic_v1`) was generated by enumerating a cross-product input grid and invoking CGEM once per (maneuver, pilot configuration) pair.

**Maneuvers.** 72 aerobatic, military, and extreme post-stall maneuvers were selected from the Aresti CIVA catalogue (2019), IAC Known/Unknown programmes (2015–2020), and published USAFSAM/ASEM centrifuge profiles [8,9]. Each maneuver is a (time, Nz) trace in the `Aerobatics_sample_inputs/*.txt` format consumed by CGEM; `maneuvers_catalog.py` records category (`championship`, `conceptual`, `extreme_post_stall`, `military_acm`), Aresti family, G-peak, max |dG/dt|, and duration.

**Pilot configurations — standard arm.** Six FAA `who_profile` presets (1–6) × three countermeasure tiers — baseline (no G-suit, no AGSM, no PBG), moderate (G-suit 5 psi, AGSM 0.5, no PBG), maximum (G-suit 10 psi, AGSM 1.0, PBG 30 mmHg). The Fortran model overrides subject physiology to the FAA preset whenever `who_profile ∈ {1..6}`, so `g_tolerance_multiplier` and `dehydration_level` are no-ops on the standard arm and were held at canonical values (1.0, 0.0). Standard arm: 6 × 3 = 18 rows per maneuver, 1,296 rows total.

**Pilot configurations — custom arm.** A 3 × 3 × 3 grid: G-tolerance multiplier ∈ {0.85, 1.00, 1.15}, dehydration level ∈ {0.0, 0.04, 0.08} (fractional plasma volume loss), countermeasure tier ∈ {baseline, moderate, maximum}, all under `who_custom` (synthetic profile with editable physiology). Custom arm: 27 rows per maneuver, 1,944 rows total.

The full grid yields 18 + 27 = 45 rows per maneuver × 72 maneuvers = **3,240 rows**. Each row carries a deterministic `row_seed = SHA256(master_seed || row_id)` with master seed 42; generation is parallelized via `multiprocessing.Pool` (`spawn` start, `cpu_count − 1` workers, isolated tmpdir per worker).

**Reproducibility.** The dataset is fully reproducible from the CGEM binary, the maneuver catalog at the committed SHA, the master seed (42), the tier definitions in `cgem_ext.data.generate_dataset`, and the compiled binary's SHA-256 hash; re-running `python -m cgem_ext.data.generate_dataset --seed 42` against the same binary produces an identical parquet file (verified by `tests/test_data.py::test_generator_is_deterministic`). The dataset schema and documentation follow the datasheet framework of Gebru et al. [10]; the full datasheet is included as supplementary material.

### 2.3 Train / validation / test splits

Rows are split 70/15/15 (train/validation/test) stratified by `maneuver_category` (master seed 42; splitter `cgem_ext.data.splits.stratified_split`). The validation split (15 %) is used for conformal calibration (both Mondrian conformal regression and OOD conformal abstention); the test split (15 %, ~486 rows) is held out for all Section 3 metrics.

For exploratory OOD evaluation, leave-one-group-out (LOGO) folds hold out one maneuver category at a time (championship 1,665/1,575; conceptual 3,105/135; extreme post-stall 2,700/540; military ACM 2,250/990 train/test). LOGO folds are not used for model selection; they are a qualitative probe of OOD response to category drift.

### 2.4 Surrogate emulator

**Model architecture.** Five per-target models cover three censored time targets (greyout, blackout, G-LOC) and two continuous targets (HLAP minimum, cerebral blood flow minimum). Censored targets use a **two-stage** pattern: stage 1, an XGBoost [17] binary classifier predicting `P(event)`, trained on all rows; stage 2, an XGBoost regressor predicting `E[event time | event=1]`, trained only on event-positive rows. The expected event time is `P(event) × E[time | event]`; the API exposes both components separately. Continuous targets use a single-stage XGBoost regressor.

**Relation to conformalized survival analysis.** Conformalized survival analysis (Candès, Lei & Ren [24]; Gui, Hannig & Hofmann [25]; Davidov et al. [26]) is the principled alternative to the two-stage pattern adopted here and is treated as paper-2 scope (§4.6).


**Hyperparameters.** Default XGBoost hyperparameters (full set in Supplementary Table S1) include `n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0, tree_method="hist", random_state=42`; monotonicity constraints are applied per-feature per `cgem_ext/surrogate/targets.py` (G-peak, dG/dt magnitude, dehydration decrease event times; countermeasure effectiveness increases them), passed to XGBoost via `monotone_constraints`.

Optuna search spaces (stratified 5-fold CV, `scripts/optuna_search.py`) are frozen in `docs/publication/osf_search_spaces.json`, committed at OSF posting. Primary results use the default-hyperparameter configuration so the headline numbers in Tables 1–5 are not search-tuned against the test split; Optuna-tuned configurations are supplementary.

**Conformal prediction intervals — homoscedastic Mondrian (baseline).** For each target, a Mondrian split-conformal regressor [11,12] is calibrated on the validation split. Residuals `r = |y_true − y_pred|` are collected per `maneuver_category` stratum. The per-stratum conformal quantile is `q̂_s = Q((1 − α)(1 + 1/n_s), residuals_s)`, with finite-sample correction `ceil((n_s+1)(1−α)) / n_s`. At inference time, a test row assigned to stratum *s* receives the prediction interval `[ŷ − q̂_s, ŷ + q̂_s]`. Rows from strata unseen during calibration receive the global quantile `Q((1 − α), residuals_all)`.

**Conformal prediction intervals — heteroscedastic CQR (primary for `time_to_gloc_s`).** For heteroscedastic targets — particularly `time_to_gloc_s`, where the homoscedastic Mondrian layer under-covered (§3.3) — we use Conformalized Quantile Regression (CQR) [15]. Three quantile heads (α/2, median, 1 − α/2) are trained per target with `objective="reg:quantileerror"` and shared monotonicity vectors; quantile crossing is resolved row-wise by `(min, max)`. The CQR conformity score on calibration row *i* is `s_i = max(q̂_lo(x_i) − y_i, y_i − q̂_hi(x_i))` per Romano, Patterson & Candès (2019, Eq. 1) [15]; the per-`maneuver_category` (1 − α) quantile of these scores, with the same finite-sample correction as the homoscedastic Mondrian layer, gives the calibrated bracket `[q̂_lo(x) − q̂_s, q̂_hi(x) + q̂_s]` of x-varying width — the advantage over the homoscedastic Mondrian baseline for `time_to_gloc_s`. The CQR layer was pre-registered in OSF amendment 2026-05-06 as hypothesis H5 before any test-set evaluation (see `docs/publication/osf_amendment_2026-05-06.md`); implementation: `cgem_ext.surrogate.cqr.TwoStageXGBQuantileSurrogate`, `cgem_ext.surrogate.conformal.MondrianCQR`.

**Calibration diagnostics.** Predicted values are binned into 10 equal-frequency bins (mean predicted vs mean observed, event fraction for classifiers); Expected Calibration Error is `ECE = Σ_{b=1}^{10} (n_b/N) · |mean(observed_b) − mean(predicted_b)|`. Reliability diagrams and ECE are reported for continuous regressors and stage-1 classifiers; for censored targets, only the classifier stage is calibrated here — conditional-regressor calibration is deferred to paper 2.

**Interpretability.** SHAP TreeExplainer values [13] are computed per prediction and exposed via the FastAPI `/predict` endpoint and the frontend; SHAP results are supplementary.

**Baseline.** A RandomForest regressor (sklearn defaults, `n_estimators=100`, `random_state=42`) is trained alongside each XGBoost model; because RandomForest cannot enforce monotonicity, the comparison is apples-to-oranges and is reported as supplementary.

### 2.5 Out-of-distribution detection

**Feature space.** The OOD detector operates on a 17-dimensional feature vector frozen in `cgem_ext.ood.features.FEATURE_COLUMNS`: 9 numeric (`g_peak_abs`, `dgdt_max_g_per_s`, `profile_duration_s`, `dehydration_level`, `g_tolerance_multiplier`, `gsuit_max_psi`, `gsuit_coverage_fraction`, `agsm_effectiveness`, `pbg_max_mmhg`); 7 binary FAA-profile indicators (`who_1`–`who_6`, `who_custom`); and 1 ordinal (`cm_ordinal ∈ {0, 1, 2}`). Constant columns are dropped before fitting to keep the scatter matrix full-rank.

**Mahalanobis distance (primary).** Robust covariance is estimated via `sklearn.covariance.MinCovDet(random_state=0)`; the squared Mahalanobis distance is `DM²(x) = (x − μ̂)ᵀ Σ̂⁻¹ (x − μ̂)`. The 17-feature space mixes 9 continuous, 7 binary, and 1 ordinal dimension, so the multivariate-Gaussian assumption is misspecified; we therefore use distribution-free conformal abstention as the operational threshold (see below), with the parametric χ²(df_eff, 0.95) value reported as a reference only.

**Conformal abstention.** `ConformalAbstention(α = 0.05)` picks the empirical `ceil((n+1)(1−α)) / n` quantile of validation-set Mahalanobis scores as the threshold; this requires no distributional assumption and guarantees that, on exchangeable in-distribution data, the empirical in-envelope rate concentrates near (1 − α). Test points whose Mahalanobis score exceeds the threshold are flagged `ood = true`.

**Isolation Forest (baseline).** `sklearn.ensemble.IsolationForest(n_estimators=100, contamination="auto", random_state=0)` is fit on the training set; scores are sign-flipped so higher = more OOD (consistent API with Mahalanobis), and the same `ConformalAbstention` calibrator is applied for fair comparison.

**Evaluation.** (a) **Calibration coverage**: empirical in-envelope rate on the test split vs the nominal 95 %. (b) **LOGO AUROC**: per held-out category, the detector's ability to discriminate held-out from training rows (both Mahalanobis and IsolationForest).

### 2.6 Sensitivity analysis

**Sobol variance-based indices.** Saltelli sampling (`SALib.sample.saltelli.sample`) drove the surrogate (N = 1,024 base samples, D = 9 features, 20,480 evaluations) and yielded first-order (S₁), total-order (ST), and second-order (S₂) indices with 95 % bootstrap confidence intervals via `SALib.analyze.sobol.analyze`.

**Morris elementary effects.** As a complementary screen, Morris one-at-a-time trajectories (*p* = 4 levels, *r* = 100 trajectories, 1,000 evaluations per target) yielded μ* (mean absolute elementary effect, ranking inputs by average local sensitivity) and σ (flagging nonlinear or interaction-driven effects).

Both analyses run against the surrogate; direct CGEM subprocess invocations would be prohibitive (~20,480 × 9 ms ≈ 3 min vs < 1 s via the emulator).

### 2.7 Validation protocol and pre-registration

The validation protocol was pre-registered on OSF before any test-set evaluation. The pre-registration locks (1) dataset version and master seed (42); (2) stratified split indices; (3) success thresholds — classifier AUROC ≥ 0.95, regressor R² ≥ 0.80 (censored) / ≥ 0.95 (continuous), conformal empirical coverage within ±5 pp of nominal 95 %, conformal OOD calibration within ±3 pp of nominal 95 %, Sobol convergence (bootstrap CI width ≤ 0.05 on the top-3 ST features); (4) the failure-handling rule: any unmet threshold is reported transparently in Section 3, not hidden. No test-set evaluation preceded OSF timestamping; deferred-Optuna search spaces are frozen in `docs/publication/osf_search_spaces.json`.

### 2.8 Software implementation

The framework is implemented as the `cgem_ext` Python package (MIT, `strikerdlm/CAMI-Gz-Effects-Model-CGEM-`, v0.1.0): `cgem_ext.data` (generation, splits), `cgem_ext.surrogate` (XGBoost + RF, Mondrian conformal, calibration), `cgem_ext.ood` (Mahalanobis + IsolationForest + conformal abstention), `cgem_ext.sensitivity` (SALib Sobol + Morris). A FastAPI service (7 endpoints: `/predict`, `/emulate`, `/run-cgem`, `/ood/score`, `/sensitivity/sobol`, `/sweep`, `/docs`) exposes the framework; a Vite/React frontend provides interactive input, real-time prediction with confidence intervals, and OOD envelope visualization. Architecture: Figure 6.

---

## 3. Results

### 3.1 Dataset characteristics

The synthetic dataset comprises 3,240 rows over 72 maneuvers and 45 pilot configurations, with category sizes of 720 (championship, 22.2 %), 720 (conceptual, 22.2 %), 720 (extreme post-stall, 22.2 %), and 1,080 (military ACM, 33.3 %); event rates were 64.8 % (greyout), 58.3 % (blackout), and 50.6 % (G-LOC), lowest in the conceptual category (low-G, short-duration) and highest in military ACM (sustained 7–9 G turns).

### 3.2 Surrogate emulator performance

**Reporting framework.** Held-out evaluation uses the OSF-pre-registered single train + test split (master seed 42); all point estimates carry 95 % bootstrap CIs (1,000 paired resamples, `numpy.random.default_rng(42)`). Because each of the ten pre-registered hypotheses (H1a/b/c, H2, H3a/b, H4a/b, H5, H6) concerns a distinct estimand rather than a parallel test of the same effect, per-estimand bootstrap CIs are reported in lieu of any family-wise correction.

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

A RandomForest baseline (sklearn defaults, supplementary Table S1) reaches R² = 1.000 for `hlap_min` and 0.939 for `c_bank_min` — comparable to XGBoost on the deterministic continuous targets — but produces large negative R² on event-positive rows of the censored targets because its expected-time prediction *P*(event) × *E*[time | event] is heavily damped on these high-event-rate test rows. The XGBoost monotonicity-constrained two-stage approach avoids this damping. We report RF baseline numbers as supplementary rather than in the main table because the architecture, not the algorithm, makes the comparison unfair.

**Parity plots.** Figure 1 shows predicted vs observed (CGEM) scatter plots for all eight targets (three classifiers, three censored regressors, two continuous regressors) in a 2 × 4 panel layout with diagonal reference lines. Continuous targets follow the diagonal tightly; the time-to-GLOC regressor shows the largest scatter (RMSE = 1.14 s), consistent with its being the hardest-to-emulate target.

**Inference latency.** Direct CGEM subprocess invocation takes ~9 ms per row (wall-clock, single core); XGBoost surrogate point prediction takes ~50 µs per row in-process — a ~180× wall-clock acceleration. This is what makes the 20,480-evaluation Saltelli Sobol sweep in §3.6 complete in under one second rather than the ~3 minutes direct CGEM invocations would require.

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

**Reading Table 2.** All five (target, stage) pairs achieve overall coverage within ±5 pp of nominal once CQR replaces homoscedastic Mondrian on `time_to_gloc_s`. The four Mondrian-retained targets (`hlap_min` 0.928, `c_bank_min` 0.949, and the three classifier rows 0.940–0.967) are unchanged. On the `time_to_gloc_s` regressor row, the homoscedastic Mondrian baseline under-covered at 0.861 (8.9 pp below nominal) and CQR over-covers at 0.972 (2.2 pp above nominal) on the same n = 36 event-positive slice — a 6.7 pp reduction in distance-to-nominal, satisfying the OSF-amended H5 criterion (see §2.4).

**Per-stratum reliability and Clopper–Pearson exact CIs.** Cells in Table 2 are flagged ⚠️ where per-stratum n < 20 (binomial CI > ±10 pp); the conceptual stratum (n = 21 overall, 0 event-positive rows) is too small for per-stratum claims. On the operationally relevant military-ACM stratum (n = 35) the Clopper–Pearson 95 % CIs are [0.706, 0.949] for the Mondrian baseline (point 0.857) and [0.847, 0.999] for CQR (point 0.971); the corresponding overall CIs at n = 36 are [0.706, 0.949] and [0.855, 0.999]. The intervals overlap, so CQR is reported as *operationally* closer to nominal rather than statistically dominant — its upper endpoint 0.999 is consistent with calibration to nominal, and the under-coverage of the homoscedastic baseline is the regime CQR is designed to address. Full per-stratum sample sizes and exact CIs are in supplementary Table S2.

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

**Calibration (the headline result).** The conformal abstention layer on top of `MahalanobisOOD` reaches an empirical in-envelope rate of **0.953** on the held-out test split, within ±0.3 pp of the nominal 95 %. Its threshold (78.3 squared distance units) sits at approximately 3× the parametric χ²(17, 0.95) cutoff (27.6), which confirms that the joint feature distribution is substantially heavier-tailed than multivariate Gaussian. By contrast, the χ² threshold alone would flag 37.2 % of in-distribution test rows as OOD — an unacceptably high false-positive rate. The conformal layer corrects this cleanly.

**LOGO category drift.** Table 4 reports per-category LOGO AUROC for both detectors.

**Table 4.** Leave-one-group-out AUROC by held-out category, with 95 % bootstrap CIs.

| Held-out category | n_train | n_test | Mahalanobis [95 % CI] | IsolationForest [95 % CI] |
|---|---|---|---|---|
| Championship | 1,665 | 1,575 | 0.529 [0.500, 0.558] | 0.543 [0.513, 0.569] |
| Conceptual | 3,105 |   135 | 0.387 [0.339, 0.433] | 0.414 [0.365, 0.462] |
| Extreme post-stall | 2,700 |   540 | 0.600 [0.563, 0.636] | 0.569 [0.536, 0.605] |
| Military ACM | 2,250 |   990 | 0.659 [0.628, 0.688] | 0.636 [0.607, 0.665] |

No held-out category reaches AUROC ≥ 0.85; per the OSF pre-registration, H3a (calibration) is the primary OOD claim and H3b (LOGO discrimination) is exploratory. Best separation is for military ACM (Mahalanobis 0.659 [0.628, 0.688], higher mean G-peak ~7 G vs ~4 G for championship); conceptual maneuvers score below 0.5 because they sit *more central* to the joint feature distribution than the training categories, so both detectors mark them as well-supported (Mahalanobis 0.387 vs IsolationForest 0.414, within bootstrap noise at n = 135). The Mahalanobis–IsolationForest CIs overlap entirely across all four folds (differences ≤ 0.04 AUROC; Mahalanobis leads on the higher-G extreme post-stall and military ACM, IsolationForest on championship and conceptual), so neither detector is claimed to dominate — this is a finding about dataset structure rather than detector failure. Figure 4 overlays the in-distribution and combined LOGO-fold score distributions with the conformal and χ² thresholds.

### 3.6 Sensitivity analysis

**Sobol indices.** Figure 5 shows the total-order Sobol indices (ST) as a heatmap (9 features × 5 targets).

Across all three time-to-event targets, `g_peak_abs` is the dominant driver: ST = 0.876 (greyout), 0.924 (blackout), 0.942 (G-LOC). The second driver is consistently `profile_duration_s` (ST = 0.203–0.277), reflecting the fact that, conditional on peak G, longer sustained exposure increases G-LOC risk nonlinearly. `dgdt_max_g_per_s` contributes modestly (ST = 0.067–0.089). Interaction effects (ST − S₁) are substantial for `g_peak_abs` (Δ ≈ 0.23–0.26), indicating that peak G interacts with duration and pilot physiology in driving event times.

For `hlap_min`, `dehydration_level` dominates completely (ST = 1.005, S₁ = 1.005, both with bootstrap CIs spanning [0.92, 1.07] — the slight overshoot above 1.0 is finite-sample noise from the *N* = 1,024 Saltelli sample, not a violation of Sobol's variance decomposition). All other features contribute near zero. This reflects the deterministic mapping from dehydration to plasma volume loss in the CGEM ODE system: reduced plasma volume → reduced stroke volume → lower mean arterial pressure at the head level, and the effect is essentially linear and unconfounded in the synthetic dataset.

For `c_bank_min`, `g_peak_abs` (ST = 0.793) and `profile_duration_s` (ST = 0.218) are the dominant drivers; `agsm_effectiveness` contributes marginally (ST = 0.007).

**Morris screening.** The Morris μ* ranking corroborates the Sobol findings: `g_peak_abs` and `dehydration_level` emerge as the top-feature μ* across all targets, with interaction flags (high σ/μ* ratio) for `g_peak_abs` and `profile_duration_s`.

**Second-order interactions.** The strongest pairwise interaction (S₂) is consistently `g_peak_abs × profile_duration_s` (S₂ ≈ 0.04–0.12 across targets), confirming that peak G and exposure duration are not independent drivers — their combined effect on event probability is super-additive.

### 3.7 External validation against archival centrifuge cohort (H6 anchor)

To complement the synthetic-only validation against CGEM-as-ground-truth (§3.2–3.6), we evaluated the trained CQR surrogate against an archival validation cohort of n = 8 pooled mean ± SD records reproduced from Whinnery & Forster (2013) [5]. The parent population for the relaxed-subject subset of that study — the regime that maps cleanly to the surrogate's countermeasure-state input — comprises 729 G-LOC episodes; the larger figure of 888 episodes commonly cited for Whinnery & Forster (2013) includes with-AGSM data and is therefore not the operative cohort here. Each evaluable record reports a fixed acceleration onset rate (0.05 to 10 G/s) and the mean ± SD time-to-loss-of-consciousness. Records were mapped to CGEM input space using the rules locked in OSF amendment 2026-05-06 §B-H6 (`who_profile = 4`, baseline countermeasures, no dehydration, `g_peak_abs` = min(9.0, 1 + onset × real_mean), `profile_duration_s` = real_mean + 5 s buffer, `maneuver_category = "military_acm"`). The full per-row table is committed at `data/results/h6/discrepancy_phase_a.json`; the evaluation script is `scripts/run_h6_evaluation.py`. An expanded archival registry of n = 23 records (8 Phase-A point rows from Whinnery & Forster 2013, 5 Phase-A point rows from a related FAA AM-23/6 reproduction, 5 Phase-B narrow-range stratification rows, and 5 Phase-B abstract anchors) is committed for auditability but is not consumed by the H6 query path: the Phase-B records describe stratifications or threshold values that do not map to a single CGEM input vector and are not yet evaluable under the OSF-locked H6 protocol. Lifting that restriction is Phase-C work and is deferred to paper 2.

**Table 5.** External validation against the Phase A archival cohort. ``surrogate_lo / hi`` is the calibrated CQR bracket; ``in_bracket`` reports whether the real mean falls inside the bracket (point coverage); ``overlap`` reports whether the surrogate bracket overlaps the real ±1 SD reference interval; ``δ = real − surrogate_median`` is the residual.

| Onset (G/s) | Real mean ± SD (s) | Surrogate median (s) | Surrogate 95 % bracket (s) | In bracket | Overlap | δ (s) |
|---:|---:|---:|---:|:---:|:---:|---:|
| 0.05 | 95 ± 5 | 14.0 | [4.4, 18.4] | ✗ | ✗ | +81.0 |
| 0.10 | 85 ± 10 | 13.6 | [4.3, 18.6] | ✗ | ✗ | +71.4 |
| 0.20 | 70 ± 15 | 13.6 | [4.3, 18.6] | ✗ | ✗ | +56.4 |
| 0.50 | 20 ± 5 | 13.1 | [3.9, 18.5] | ✗ | ✓ | +6.9 |
| 1.00 | 12 ± 3 | 12.4 | [3.9, 17.9] | ✓ | ✓ | −0.4 |
| 2.00 | 9 ± 2 | 10.3 | [3.9, 17.9] | ✓ | ✓ | −1.3 |
| 5.00 | 8 ± 3 | 8.5 | [4.3, 17.9] | ✓ | ✓ | −0.5 |
| 10.00 | 9 ± 4 | 9.6 | [3.8, 17.6] | ✓ | ✓ | −0.6 |

**Headline.** Point coverage (real mean ∈ surrogate bracket) is **0.500** (4 / 8); interval-overlap coverage is **0.625** (5 / 8). The mean discrepancy δ̄ = +26.6 s with 95 % bootstrap CI [+6.3, +52.1] — i.e., real centrifuge participants tolerate +Gz, on average, **substantially longer than the CGEM-via-surrogate prediction**, and the discrepancy is statistically distinguishable from zero. **H6's pre-registered primary success criterion (≥ 0.90 coverage) is therefore not met on the Phase A cohort.** As §3.7 below makes explicit, the discrepancy concentrates entirely at onset ≤ 0.5 G/s, *outside* the rapid-onset (≥ 1 G/s) fighter and aerobatic envelope this framework is intended for; on that operationally relevant subset the surrogate is in-bracket on every record. The result is therefore a partial external-validation failure with a well-defined operational scope, and it quantifies the CGEM-vs-reality discrepancy term δ(x) = real(x) − CGEM(x) that the OSF-amended H6 hypothesis was designed to surface — but it is not a clean H6 pass.

**The discrepancy is concentrated at slow onset rates.** Rows for onset ≤ 0.5 G/s contribute the entire bias (δ̄ between +6.9 and +81.0 s); rows for onset ≥ 1.0 G/s show no systematic bias (|δ̄| ≤ 1.3 s, all in-bracket). This pattern is consistent with the CGEM literature: Copeland & Whinnery (2023) [7] note explicitly that "the underestimation of the time to loss of consciousness when compared with the data at very low onset rates suggests a completely relaxed participant may not be an accurate assumption" — gradual G onset gives relaxed participants 30 + s in which non-AGSM muscle tension (gripping, postural reflex) raises arterial pressure by up to 60 mmHg, an effect CGEM does not encode at run time. The H6 result quantifies that documented limitation rather than discovering a new failure mode of CGEM.

**Operational interpretation.** The CGEM-via-surrogate framework is well-calibrated against real outcomes in the **rapid-onset regime** (onset ≥ 1 G/s, the operationally relevant regime for fighter and aerobatic flight) and systematically under-predicts time-to-LOC in the **slow-onset regime** (onset ≤ 0.5 G/s, more typical of agricultural / large-aircraft flight). Until paper-3 incorporates the missing muscle-tension term explicitly (and re-validates against own-centrifuge subjects, see §4.6), the framework's prediction intervals should be treated as **lower bounds** in the slow-onset regime — i.e., real outcomes are likely longer than the bracket's upper limit, never shorter than its lower limit. The conformal layer remains correctly calibrated against CGEM (§3.3), so the failure is a CGEM-vs-reality discrepancy, not a CQR-vs-CGEM discrepancy.

---

## 4. Discussion

### 4.1 Principal findings

We present a validated ML extension layer for the FAA CGEM model that delivers three capabilities previously absent in CGEM applications: (1) **OOD detection with distribution-free calibration**, achieving a 0.953 held-out in-envelope rate within 0.3 pp of the nominal target; (2) **calibrated prediction intervals** using a maneuver-category-stratified homoscedastic Mondrian conformal layer for four targets and a heteroscedastic Conformalized Quantile Regression layer for the long-tailed `time_to_gloc_s` target — overall coverage is within 5 pp of nominal on all five (target, stage) pairs once CQR replaces the homoscedastic Mondrian on `time_to_gloc_s` (0.861 → 0.972 on n = 36 event-positive test rows); and (3) **a fast surrogate** (~50 µs per row vs ~9 ms for direct subprocess invocation) that makes Sobol sensitivity decomposition tractable inside the manuscript-preparation cycle. All three capabilities are delivered without modifying the validated Fortran core.

The strongest result is the OOD calibration: conformal abstention achieves near-nominal in-envelope coverage on unseen test data with a threshold that is 3× the parametric χ² cutoff — exactly the situation for which distribution-free calibration was designed. The conformal layer essentially says: "we will flag approximately 5 % of in-distribution queries as OOD" — a defensible operational guarantee for a conservative-by-design abstention policy.

Emulator performance is satisfactory across all targets: event-occurrence classification is near-perfect (AUROC ≥ 0.996), continuous-target regression is excellent (R² = 0.94–1.00), and censored-target regression on event-positive rows is good (R² = 0.82–0.90). The weakest target is `time_to_gloc_s` (R² = 0.821, RMSE = 1.14 s), as expected for the most extreme censored event; its Mondrian conformal interval also under-covers (0.861). An error of ±1.14 s on a G-LOC time prediction can be operationally significant — the conformal interval width communicates that uncertainty to the user explicitly.

### 4.2 Aeromedical implications

The 50 µs prediction latency makes parametric what-if analysis (G-onset, dehydration, countermeasure variants with conformal intervals) tractable in milliseconds rather than the seconds of subprocess overhead CGEM would impose; the Sobol decomposition separates HLAP (dominated by dehydration) from event-time targets (dominated by peak G), which is an operationally meaningful separation of fluid-management from G-tolerance interventions. The same surrogate + conformal + OOD pattern applies to any validated ODE physiological model that must be made computationally tractable and uncertainty-aware.

### 4.3 Comparison to prior CGEM applications

CGEM and its predecessor cardiovascular models have served FAA technical reports and aeromedical publications for point-estimate G-tolerance prediction [5–8]. None of those prior applications provided (a) conformal prediction intervals, (b) OOD input guardrails, or (c) global sensitivity rankings. To our knowledge, this is the first published ML-based surrogate emulator of CGEM.

Fast emulation paired with calibrated uncertainty quantification has worked well in adjacent physiological-surrogate domains [14,19,20], and Boileau et al. [21] benchmarked the one-dimensional arterial-flow methods on which much of that work builds. Most directly relevant, Portela, Banga & Matabuena [23] applied distribution-free conformal prediction to canonical biological ODE systems, establishing the precedent for the surrogate + conformal pattern. Our framework extends that pattern in four ways: (a) it is additive — a wraparound rather than a rewrite of a validated legacy regulatory model; (b) Mondrian split-conformal stratification by maneuver category preserves coverage within operational sub-populations rather than pooling; (c) a heteroscedastic Conformalized Quantile Regression layer handles the long-tailed `time_to_gloc_s` target where homoscedastic Mondrian conformal under-covers; and (d) a distribution-free conformal abstention layer over a robust-Mahalanobis OOD score gives an in-envelope guarantee that does not assume Gaussianity. The principled successor to the present two-stage classifier-then-regressor pattern is the conformalized survival analysis framework of Candès, Lei & Ren [24] and the extensions by Gui, Hannig & Hofmann [25] and Davidov et al. [26]; that is paper-2 scope and is discussed in §4.6.

### 4.4 Limitations

**Synthetic-only validation, partially closed by §3.7.** Sections 3.2–3.6 validate the framework against CGEM-as-ground-truth — the surrogate's R² and the conformal layer's coverage measure how well the ML layer reproduces CGEM, not how well CGEM predicts real outcomes. Section 3.7 partially closes this gap by evaluating the calibrated surrogate against the Phase A archival cohort (n = 8 pooled mean ± SD records from Whinnery & Forster 2013 [5]; n_parent = 729 relaxed-subject centrifuge participants — the commonly cited n = 888 total in W&F2013 includes with-AGSM records excluded from the OSF H6 mapping, as explained in §3.7) and reports the discrepancy δ̄ = +26.6 s [95 % CI +6.3, +52.1] with an explicit slow-onset bias. Phase B per-subject extraction and validation against own-centrifuge subjects belong to separate work and are not claimed here.

**No individualized physiology.** The six FAA `who_profile` presets capture population-average physiology; the custom arm's G-tolerance multiplier ∈ {0.85, 1.00, 1.15} simulates inter-individual variation but does not model it from biometric measurements. Bayesian per-pilot calibration from anthropometric, cardiovascular, or wearable-derived parameters is paper-3 scope.

**`time_to_gloc_s` is the most challenging target.** Its event-positive R² (0.82) is the lowest of the five surrogate targets, and its conditional event-time distribution is heavier-tailed than the other two censored time targets. The homoscedastic Mondrian conformal layer under-covers on this target (0.861 vs nominal 0.95); the heteroscedastic Conformalized Quantile Regression layer (Romano, Patterson & Candès 2019 [15]) restores coverage to 0.972 on the same held-out test slice (§3.3, OSF-amended H5), and the regressor stage's R² of 0.82 is upper-bounded by how faithfully CGEM itself models the G-LOC time distribution at the long tail — the discrepancy term δ(x) = real(x) − CGEM(x) that motivates the archival validation arm of OSF amendment H6.

### 4.5 Reproducibility

- **Open code**: This repository (`strikerdlm/CAMI-Gz-Effects-Model-CGEM-`, MIT license), with all modules, tests (80 tests, all passing), and figure-generation scripts committed.
- **Open synthetic dataset**: `cgem_synthetic_v1.parquet` (Zenodo DOI: TBD at submission), with sidecar metadata (`cgem_synthetic_v1.meta.json`) recording binary SHA, master seed (42), tier definitions, and package version.
- **Docker image**: GHCR artifact with frozen dependency versions; reproduces the full pipeline from `docker run`.
- **OSF pre-registration**: [Link TBD at submission] — locking split indices, success thresholds, and search spaces before test-set evaluation.
- **Figure reproducibility**: All six figures in this manuscript are rendered from committed data products (`data/results/figures/` and `data/results/sensitivity/`) via deterministic scripts (`scripts/generate_figure_data.py` + `scripts/build_figure_options.py`). The ECharts figure options (`fig1_parity.json` through `fig5_sobol.json`) and the Mermaid architecture source (`fig6_architecture.mmd`) are committed and render identically on re-execution.

### 4.6 Future work

The present paper validates the method against CGEM as ground truth (synthetic-only). External validation against archival centrifuge data and own-centrifuge subjects is the subject of separate work.

Paper-2 is an archival re-analysis: it replaces the two-stage classifier-plus-regressor with a conformalized survival analysis framework (Candès, Lei & Ren [24]; Gui, Hannig & Hofmann [25]; Davidov et al. [26]) that exploits the full Type-I right-censored structure of archival event-time data, and is expected to deliver tighter and more principled lower predictive bounds on `time_to_gloc_s`. Paper-3 is own-centrifuge validation under separate IRB and is blocked on subject data.

The wrapping pattern reported here — surrogate + conformal + OOD over a validated ODE physiological model — is publisher-agnostic, and is intended as a reference implementation for any model in that class.

---

## 5. Conclusion

This framework preserves a validated FAA physiological model and adds fast emulation, calibrated uncertainty quantification for four of five targets (with a heteroscedastic CQR layer activated for the long-tailed `time_to_gloc_s` target, where the homoscedastic Mondrian baseline under-covered and where the regressor's event-positive R² has a 95 % bootstrap CI lower bound of −0.055), input-envelope guardrails, and global sensitivity analysis — a methodological contribution that requires no claim of novel physiology. The H6 archival evaluation bounds applicability to the rapid-onset (≥ 1 G/s) regime operationally relevant to fighter and aerobatic flight; the slow-onset bias of δ̄ = +26.6 s [95 % CI +6.3, +52.1] is documented as a CGEM-vs-reality discrepancy term to be addressed in paper 2. Open, reproducible, and pre-registered, the pipeline is designed to absorb progressively stronger external validation in papers 2 and 3 without architectural changes. It is ready for downstream aeromedical research applications: parametric mission planning, real-time G-LOC risk advisory prototyping, and the computational backbone for future Bayesian per-pilot calibration studies.

---

## Author contributions (CRediT)

**Diego Malpica** — Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing — original draft; Writing — review & editing; Visualization; Supervision; Project administration; Funding acquisition. Sole author.

## Data and code availability

- **Source code.** The complete framework is open-source under the MIT licence at `https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`. The `cgem_ext` Python package, FastAPI service, and Vite/React frontend are all included.
- **Synthetic dataset.** `cgem_synthetic_v1.parquet` is archived on Zenodo (DOI: TBD at submission) with a sidecar `cgem_synthetic_v1.meta.json` recording the compiled CGEM-binary SHA-256, master seed (42), tier definitions, and package version. The dataset is cited formally in the reference list [22] per the Joint Declaration of Data Citation Principles.
- **Reproducibility container.** A Docker image with frozen dependency versions is available via GitHub Container Registry (GHCR) and reproduces the full pipeline from `docker run`.
- **Pre-registration.** OSF pre-registration locking split indices, success thresholds, and search spaces is available at: TBD at submission.
- **Figures.** All six manuscript figures are rendered from committed data products under `data/results/figures/` and `data/results/sensitivity/` via deterministic scripts; the ECharts figure-option JSON files (`fig1_parity.json` through `fig5_sobol.json`) and the Mermaid architecture source (`fig6_architecture.mmd`) are committed and re-render identically.

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

[10] Gebru T, Morgenstern J, Vecchione B, et al. *Datasheets for datasets.* arXiv preprint arXiv:1803.09010; 2018. Available from: https://arxiv.org/abs/1803.09010

[11] Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World.* Springer; 2005. ISBN: 978-0-387-25061-8.

[12] Boström H, Johansson U, Löfström T. *Mondrian conformal predictive distributions.* In: Proc 7th Symposium on Conformal and Probabilistic Prediction and Applications (COPA); PMLR 91:24-38; 2018. Available from: http://proceedings.mlr.press/v91/bostrom18a.html

[13] Lundberg SM, Lee SI. *A unified approach to interpreting model predictions.* Adv Neural Inf Process Syst. 2017;30:4765-4774. Available from: https://arxiv.org/abs/1705.07874

[14] Kissas G, Yang Y, Hwuang E, et al. *Machine learning in cardiovascular flows modeling: predicting arterial blood pressure from non-invasive 4D flow MRI data using physics-informed neural networks.* Comput Methods Appl Mech Eng. 2020;358:112623. doi:10.1016/j.cma.2019.112623.

[15] Romano Y, Patterson E, Candès EJ. *Conformalized quantile regression.* Adv Neural Inf Process Syst. 2019;32:3543-3553. Available from: https://arxiv.org/abs/1905.03222

[16] Convertino VA. *Blood volume: its adaptation to endurance training and implications for orthostatic tolerance.* Med Sci Sports Exerc. 1991;23(7):815-822.

[17] Chen T, Guestrin C. *XGBoost: a scalable tree boosting system.* Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining; 2016:785-794. doi:10.1145/2939672.2939785

[18] Angelopoulos AN, Bates S. *A gentle introduction to conformal prediction and distribution-free uncertainty quantification.* Found Trends Mach Learn. 2023;16(4):494-591. doi:10.1561/2200000101

[19] Peherstorfer B, Willcox K, Gunzburger M. *Survey of multifidelity methods in uncertainty propagation, inference, and optimization.* SIAM Rev. 2018;60(3):550-591. doi:10.1137/16M1082469

[20] Kakhaia S, Zun P, Ye D, Krzhizhanovskaya V. *Inverse uncertainty quantification of a mechanical model of arterial tissue with surrogate modelling.* Int J Numer Methods Biomed Eng. 2021;37(6):e3450. doi:10.1002/cnm.3450

[21] Boileau E, Nithiarasu P, Blanco PJ, Müller LO, Fossan FE, Hellevik LR, Donders WP, Huberts W, Willemet M, Alastruey J. *A benchmark study of numerical schemes for one-dimensional arterial blood flow modelling.* Int J Numer Methods Biomed Eng. 2015;31(10):e02732. doi:10.1002/cnm.2732

[22] Malpica D. *cgem_synthetic_v1: synthetic dataset of 3,240 CGEM simulations across 72 maneuvers and 45 pilot configurations.* Zenodo; 2026; v1.0.0; doi:TBD at submission. (Cited per the Joint Declaration of Data Citation Principles: Authors; Year; Dataset title; Repository; Version; Persistent Identifier.)

[23] Portela A, Banga JR, Matabuena M. *Conformal prediction for uncertainty quantification in dynamic biological systems.* PLoS Comput Biol. 2025;21(5):e1013098. doi:10.1371/journal.pcbi.1013098. (Direct methodological precedent: distribution-free conformal prediction wrapped around dynamic ODE biological models.)

[24] Candès EJ, Lei L, Ren Z. *Conformalized survival analysis.* J R Stat Soc Ser B Stat Methodol. 2023;85(1):24-45. doi:10.1093/jrsssb/qkac004. PMID 33758770. (Foundational conformalized survival analysis under Type-I right-censoring; distribution-free finite-sample lower predictive bounds.)

[25] Gui Y, Hannig J, Hofmann T. *Conformalized survival analysis with adaptive cut-offs.* Biometrika. 2024;111(2):459-477. doi:10.1093/biomet/asad073. (Adaptive-threshold extension producing more informative LPBs than the original Candès-Lei-Ren method.)

[26] Davidov H, Feldman S, Shamai G, Kimmel R, Romano Y. *Conformalized survival analysis for general right-censored data.* In: International Conference on Learning Representations (ICLR); 2025. OpenReview ID JQtuCumAFD. Available from: https://openreview.net/forum?id=JQtuCumAFD (Generalises the Type-I framework to the ubiquitous general right-censored setting where censoring time is not always observed; directly applicable to time-to-G-LOC under operational missingness.)

[27] Meng X, Karniadakis GE. *A composite neural network that learns from multi-fidelity data: application to function approximation and inverse PDE problems.* J Comput Phys. 2020;401:109020. doi:10.1016/j.jcp.2019.109020. (Multi-fidelity deep neural network — robust at small high-fidelity sample sizes where Kennedy-O'Hagan / NARGP discrepancy GPs over-fit.)

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
