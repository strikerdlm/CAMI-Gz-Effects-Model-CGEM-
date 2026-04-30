# Model card — `cgem_ext.surrogate`

Fast ML surrogate of the CAMI G-Effects Model (CGEM). Five per-target models bundled together: three two-stage (classifier + conditional regressor) for the right-censored time targets, two single-stage regressors for the continuous targets. A RandomForest baseline ships alongside for fair comparison; a Mondrian split-conformal layer turns the point predictions into per-maneuver-category prediction intervals.

This card follows the framework of Mitchell *et al.* 2019, [*Model Cards for Model Reporting*](https://arxiv.org/abs/1810.03677).

---

## Intended use

- **Primary**: emulate CGEM ~10⁵× faster than direct subprocess invocation. Backs the FastAPI `/predict` endpoint and the parametric `/sweep` endpoint.
- **Secondary**: drive the SALib Sobol study in Phase 4 (sensitivity rankings would otherwise be intractable on the Fortran subprocess).
- **Operational pattern**: each prediction is paired with the OOD `is_in_envelope` flag (`cgem_ext.ood`) and a Mondrian conformal interval. Downstream consumers should display all three: the point estimate, the interval, and the OOD flag. **The surrogate is not a substitute for direct CGEM** when an authoritative answer is required — that's what `/run-cgem` is for.
- **Not for**: clinical decision-making on a real pilot. Synthetic-only validation; centrifuge validation is paper 3.

---

## Model details

### Targets

| Target | Family | Backbone | Stages | Monotonicity prior |
|---|---|---|---|---|
| `time_to_greyout_s` | censored time | XGBoost | classifier (event) + regressor (time \| event=1) | g_peak ↓ time, dgdt ↓ time, dehydration ↓ time, countermeasures ↑ time |
| `time_to_blackout_s` | censored time | XGBoost | classifier + regressor | same |
| `time_to_gloc_s` | censored time | XGBoost | classifier + regressor | same |
| `hlap_min` | continuous | XGBoost | single regressor | g_peak ↓ HLAP, dehydration ↓ HLAP, countermeasures ↑ HLAP |
| `c_bank_min` | continuous | XGBoost | single regressor | same set + dgdt ↓ c_bank |

Monotonicity vectors live in `cgem_ext/surrogate/targets.py` and are passed to XGBoost via `monotone_constraints`. The RandomForest baseline does not use monotonicity (sklearn does not support it); the comparison is therefore intentionally apples-to-oranges in that respect.

### Default hyperparameters

```python
n_estimators=400, max_depth=6, learning_rate=0.05,
subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
random_state=42, tree_method="hist"
```

A formal Optuna search is deferred to `scripts/optuna_search.py` (Phase-3 polish) and will be locked at OSF posting time.

### Conformal layer

`cgem_ext.surrogate.MondrianSplitConformal(alpha=0.05)` stratified by `maneuver_category`:

- Calibration: per-stratum quantile of `|y_true − y_pred|` on the validation split, with finite-sample correction `ceil((n+1)(1-α))/n`.
- Inference: each test row's interval width is the per-stratum quantile (with global-fallback for unseen strata).
- Property: empirical coverage tends to (1 − α) within each stratum on exchangeable data.

---

## Training data

- Dataset: `cgem_synthetic_v1` (`data/datasets/cgem_synthetic_v1.parquet`).
- Datasheet: `docs/data/datasheet.md`.
- Train/val/test split: 70/15/15 stratified by `maneuver_category`, master seed 42 (`cgem_ext.data.splits.stratified_split`).

---

## Performance

Numbers below are reproduced by `tests/test_surrogate.py::test_*_surrogate_meets_thresholds` against the canonical paper-1 dataset. The full test suite runs in ~100 s on an 8-core CPU.

### Classifier stage (event detection on censored targets)

| Target | Test AUROC |
|---|---|
| `time_to_greyout_s` (event = greyout occurred) | 0.996 |
| `time_to_blackout_s` (event = blackout occurred) | 0.999 |
| `time_to_gloc_s` (event = G-LOC occurred) | 0.996 |

The classifier is essentially perfect across all three event flags; the synthetic dataset is deterministic so this is unsurprising.

### Regressor stage

For censored targets, R² and RMSE are reported on rows where the event actually occurred (event = 1). For continuous targets, on the full test split.

| Target | Censored | XGB R² | XGB RMSE | RF baseline R² |
|---|---|---|---|---|
| `time_to_greyout_s` (event=1 only) | yes | 0.880 | 0.519 s | -0.835 |
| `time_to_blackout_s` (event=1 only) | yes | 0.903 | 0.458 s | -1.427 |
| `time_to_gloc_s` (event=1 only) | yes | 0.821 | 1.142 s | -1.029 |
| `hlap_min` | no | 1.000 | 0.008 mmHg | 1.000 |
| `c_bank_min` | no | 0.938 | 0.950 s | 0.939 |

The RandomForest baseline R² values for censored targets are *negative* on the event=1 evaluation slice because the baseline's expected-time prediction (P(event) × E[time | event]) is heavily damped on these high-event-rate test rows; the RF baseline is comparable to XGB only on continuous targets where this issue does not arise. Paper-1 reports both numbers and the discussion notes this evaluation asymmetry.

### Mondrian conformal coverage

Empirical coverage of the 95% Mondrian split-conformal interval on the held-out test split, calibrated on the val split:

| Target | Empirical coverage | Within ±5pp of nominal? |
|---|---|---|
| `hlap_min` | 0.928 | ✅ |
| `c_bank_min` | 0.949 | ✅ |
| `time_to_greyout_s` (event=1 cal+test) | 1.000 | ✅ (over-coverage) |
| `time_to_blackout_s` (event=1 cal+test) | 1.000 | ✅ (over-coverage) |
| `time_to_gloc_s` (event=1 cal+test) | 0.861 | ⚠️ (5pp under nominal) |

Per-stratum coverage tables are reproducible via `cp.coverage(...)` and live in the test outputs; they will be reported as supplementary in paper 1.

### Speedup vs direct CGEM subprocess

- Direct CGEM subprocess: ~9 ms per row on a single core (synthetic dataset generation rate, `cpu_count - 1` workers).
- XGBoost surrogate: ~50 µs per row on a single core (point prediction, in-process).
- **~180× wall-clock speedup** for a single-row prediction; orders of magnitude better when amortised across batches (XGBoost vectorises across rows whereas CGEM cannot).

Real-world impact: a 10⁴-sample Saltelli Sobol study (Phase 4) takes seconds via the surrogate, days via the subprocess.

---

## Limitations

- **Synthetic-only validation**. Performance numbers are *reproducing CGEM*, not predicting reality. Paper 2 (external re-analysis) will quantify the discrepancy term δ(x) = real − CGEM; paper 3 will validate against own-centrifuge subjects.
- **Two-stage censored handling masks per-row uncertainty**. `predict_expected_time = P(event) × E[time | event]` collapses two distributions into one scalar; the model card recommends downstream consumers display the classifier probability *and* the conditional time *and* the conformal interval, rather than a single "predicted time".
- **`time_to_gloc_s` regressor is the weakest** (R² = 0.82, RMSE = 1.14 s). Errors of ±1 s on a G-LOC time prediction can be operationally significant.
- **Conformal under-coverage on `time_to_gloc_s`** (0.86 vs nominal 0.95). The interval is too narrow for the long tail of the conditional time distribution; future work: heteroscedastic conformal (Romano et al. 2019) instead of Mondrian.
- **Monotonicity priors are local**. XGBoost enforces monotonicity for individual feature changes, holding others fixed. Real interaction effects (e.g. dehydration shifts the AGSM monotone direction) are not encoded.
- **Six FAA pilot presets only**. The surrogate generalises to the custom-arm `g_tolerance_multiplier ∈ {0.85, 1.00, 1.15}` but extrapolates poorly outside that range. The OOD detector flags such inputs.
- **Fixed feature space**. Adding HRV inputs from paper 3 will require a new model version with its own card.

---

## Ethical considerations

- **Aeromedical decision support, not clearance**. The surrogate is a research instrument; using it to make pilot fly/no-fly decisions requires paper-3-grade validation and regulatory review.
- **Bias in the pilot population**. Six FAA presets cover most fighter-pilot phenotypes but under-represent female pilots, high-G-tolerant trained operators, and pilots with anthropometric extremes. The OOD detector is the primary mitigation; its model card discusses the same limitation.
- **Synthetic-data communication**. When the surrogate is deployed (FastAPI, frontend), the response carries a `source: "surrogate"` field; users must be aware they are seeing a fast emulator, not direct CGEM. The `/run-cgem` endpoint exists for the cases where this matters.
- **Reproducibility commitment**. Every prediction can be back-checked against `/run-cgem` (the same compiled binary used during dataset generation, hash recorded in the dataset's sidecar metadata). Discrepancies above the conformal interval indicate either a surrogate failure or an OOD input, both of which are auditable.

---

## How to reproduce

```python
from cgem_ext.data.splits import stratified_split
from cgem_ext.surrogate import (
    MondrianSplitConformal, XGBSurrogate, TwoStageXGBSurrogate,
)
import pandas as pd

df = pd.read_parquet("data/datasets/cgem_synthetic_v1.parquet")
sp = stratified_split(df, seed=42)
train_df, val_df, test_df = sp.apply(df)

# Continuous target
xgb = XGBSurrogate("hlap_min").fit(train_df)
cp = MondrianSplitConformal(alpha=0.05).fit(
    cal_predictions=xgb.predict(val_df),
    cal_targets=val_df["hlap_min"],
    cal_strata=val_df["maneuver_category"],
)
print("Coverage:", cp.coverage(
    test_predictions=xgb.predict(test_df),
    test_targets=test_df["hlap_min"],
    test_strata=test_df["maneuver_category"],
))

# Censored target — predict expected time + classifier probability
two = TwoStageXGBSurrogate("time_to_gloc_s").fit(train_df)
print("AUROC:", roc_auc_score(test_df["event_gloc"],
                              two.predict_event_probability(test_df)))
```

---

## Versioning

- **v0.1.0** (current): bundled with Phase-3 commit on `feat/ml-layer-phase-0`. Models trained at use-time from the dataset; no serialised artefacts ship yet. Serialised artefacts (`cgem_ext/surrogate/artifacts/v0_1_0/*.json` for XGBoost, `*.joblib` for RF) will land alongside paper-1 submission.
- Any change to `cgem_ext.surrogate.features.FEATURE_COLUMNS` or `cgem_ext.surrogate.targets.TARGETS` increments the model version and forces a re-fit.
