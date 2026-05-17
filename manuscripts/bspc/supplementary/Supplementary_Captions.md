# Supplementary Material for "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"

This document lists every supplementary item delivered with the BSPC submission. Each item is uploaded as a separate file under the "Supplementary Material" category in Editorial Manager, named per the Elsevier convention (`Fig_S<n>.<ext>`, `Table_S<n>.<ext>`, `Appendix_S<n>.<ext>`, `Data_S<n>.<ext>`). This captions file is uploaded first.

## Tables

**Table S1.** RandomForest baseline regressor performance on the held-out test split, alongside the XGBoost surrogate hyperparameter table for the five surrogate targets.

**Table S2.** Per-stratum Mondrian conformal coverage on the held-out test split, with finite-sample-corrected Clopper–Pearson 95 % exact binomial confidence intervals per cell. The `time_to_gloc_s` regressor is reported both under the homoscedastic Mondrian baseline (rejected by H5 pre-registration) and under the heteroscedastic CQR layer (primary, OSF-amendment H5).

**Table S3.** Second-order Sobol interaction indices (S₂) for all feature pairs across the five surrogate targets, with 95 % bootstrap confidence intervals.

## Figures

**Fig. S1.** SHAP TreeExplainer feature-importance ranking across the five surrogate targets, computed on the held-out test split. Bars are sorted by mean absolute SHAP value per feature; targets are colour-coded per the legend.

**Fig. S2.** Morris Elementary Effects μ\*–σ scatter for the nine continuous input features across the five surrogate targets, computed on the surrogate emulator. High μ\* indicates strong global influence; high σ indicates non-linear or interactive influence.

## Appendices

**Appendix S1.** Dataset datasheet for `cgem_synthetic_v1.parquet`, following the framework of Gebru et al. (2018). Documents provenance, motivation, composition, collection process, preprocessing, uses, distribution, and maintenance.

**Appendix S2.** TRIPOD-AI reporting-guideline compliance checklist for the present manuscript (Collins et al., 2024).

**Appendix S3.** Model card for the XGBoost surrogate emulator (per Mitchell et al., 2019). Includes intended use, training data summary, evaluation, ethical considerations, and caveats.

**Appendix S4.** Model card for the Mahalanobis + conformal-abstention OOD detector. Same template as Appendix S3.

**Appendix S5.** Frozen OSF pre-registration document. Hypotheses H1–H4, search spaces, split indices, success thresholds — all locked at OSF posting time before any test-set evaluation.

**Appendix S6.** OSF amendment dated 2026-05-06, adding hypotheses H5 (heteroscedastic CQR on `time_to_gloc_s`) and H6 (archival external validation against Whinnery and Forster 2013), filed before any test-set evaluation under the new hypotheses.

## Data

**Data S1.** OSF-frozen hyperparameter search spaces for the Optuna stratified 5-fold cross-validation tuning runs (JSON). Locked at OSF posting time.

**Data S2.** OSF-frozen train/validation/test split indices (Parquet). Master seed 42; stratified by `maneuver_category`.

**Data S3.** Sobol first-order (S₁) and total-order (ST) indices for the nine input features across the five surrogate targets, with 95 % bootstrap confidence intervals (CSV).

**Data S4.** Sobol second-order (S₂) interaction indices for all feature pairs across the five surrogate targets (CSV).

**Data S5.** Morris Elementary Effects μ, μ\*, σ for the nine input features across the five surrogate targets (CSV).

**Data S6.** Side-by-side CQR-vs-Mondrian conformal coverage comparison on `time_to_gloc_s` (JSON). Per-stratum coverage rates and Clopper–Pearson 95 % exact CIs for both the homoscedastic Mondrian baseline and the heteroscedastic CQR layer.

**Data S7.** H6 archival-validation discrepancy diagnostics against the Whinnery & Forster (2013) Phase A cohort (JSON). Per-record predicted vs observed `time_to_gloc_s`, conformal bracket bounds, in-bracket flags, and the bootstrap distribution of the mean discrepancy δ̄.
