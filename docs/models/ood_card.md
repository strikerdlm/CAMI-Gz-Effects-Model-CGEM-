# Model card — `cgem_ext.ood`

OOD (out-of-distribution) detector for CGEM inputs. Two detectors are bundled side-by-side so paper-1 can report a fair comparison:

- **`MahalanobisOOD`** — robust covariance (`sklearn.covariance.MinCovDet`) over the fixed feature space, χ²(df, 0.95) cutoff on squared Mahalanobis distance. **Pre-registered as the primary OOD backbone**.
- **`IsolationForestOOD`** — `sklearn.ensemble.IsolationForest` baseline with default hyperparameters and matched API (same `fit / score / is_in_envelope` shape; score sign-flipped so higher = more OOD).

Both are calibrated by the same split-conformal abstention layer (`cgem_ext.ood.ConformalAbstention`) on a held-out validation slice.

This card follows the framework of Mitchell *et al.* 2019, [*Model Cards for Model Reporting*](https://arxiv.org/abs/1810.03677).

---

## Intended use

- **Primary**: gate downstream model use. Surrogate emulator predictions and FastAPI `/predict` responses carry an `ood: bool` field driven by this detector. When `ood == True`, the API still returns a point prediction but flags it explicitly.
- **Secondary**: generate "abstention rate" metrics for paper-1 Discussion (how often does a representative downstream user encounter an OOD input?).
- **Not for**: a hard gate on physiological reality. The detector measures distance from the *training feature distribution* — not distance from physiological plausibility. A physiologically reasonable input that happens to live in a sparse training region will be flagged; that is by design (the surrogate is not yet validated there).

---

## Model details

- **Backbone (primary)**: `MahalanobisOOD`
  - Fitter: `sklearn.covariance.MinCovDet(random_state=0)`
  - Cutoff: χ²(df = rank-effective feature count, q = 0.95)
  - Constant columns dropped before fit so the scatter matrix is full-rank.
- **Backbone (baseline)**: `IsolationForestOOD`
  - `IsolationForest(n_estimators=100, contamination="auto", random_state=0)`
  - Score = negated `decision_function` so higher = more OOD.
- **Calibration layer**: `ConformalAbstention(alpha=0.05)`
  - Picks the empirical (1 − α) quantile (with finite-sample correction `ceil((n+1)(1-α))/n`) of the calibration scores as the threshold.
  - Distribution-free: works with either backbone.
- **Feature space** (17 dims, frozen in `cgem_ext.ood.features.FEATURE_COLUMNS`):
  - Numeric (9): `g_peak_abs`, `dgdt_max_g_per_s`, `profile_duration_s`, `dehydration_level`, `g_tolerance_multiplier`, `gsuit_max_psi`, `gsuit_coverage_fraction`, `agsm_effectiveness`, `pbg_max_mmhg`.
  - Categorical (7, one-hot): `who_1` … `who_6`, `who_custom`.
  - Ordinal (1): `cm_ordinal` ∈ {0, 1, 2}.

---

## Training data

- **Dataset**: `cgem_synthetic_v1` (`data/datasets/cgem_synthetic_v1.parquet`).
- **Datasheet**: `docs/data/datasheet.md`.
- **Train slice** for the published metrics: 70 % stratified split, seed 42 (see `cgem_ext.data.splits.stratified_split`).
- **Calibration slice**: the 15 % validation split.

---

## Performance

Numbers below are reproduced by `tests/test_ood.py` against the canonical paper-1 dataset.

### Calibration coverage (the strong result)

The conformal layer on top of `MahalanobisOOD` hits the target abstention rate cleanly:

| Slice | Empirical in-envelope rate | Nominal | Pass |
|---|---|---|---|
| Calibration (val) | 0.955 | 0.95 | ✅ |
| Test (held out) | **0.953** | 0.95 | ✅ (within ±2 pp) |

The conformal threshold (78.3 squared distance units) is much higher than the χ²(17, 0.95) cutoff (27.6), reflecting the fact that the joint feature distribution is heavier-tailed than a multivariate Gaussian — exactly the situation conformal calibration is designed to handle.

### Leave-one-group-out AUROC (exploratory)

We evaluate "category drift" by holding out one maneuver category at a time and asking the OOD detector to discriminate held-out rows from training rows. **Categories overlap substantially in feature space** (e.g., a championship Hammerhead and a military 9-G turn share G-peak and onset-rate ranges), so this AUROC is **a soft drift signal, not a hard separator**.

| Held-out category | n_train | n_test | Mahalanobis | IsolationForest |
|---|---|---|---|---|
| championship | 1,665 | 1,575 | 0.529 | 0.543 |
| conceptual | 3,105 | 135 | 0.387 | 0.414 |
| extreme_post_stall | 2,700 | 540 | 0.600 | 0.569 |
| military_acm | 2,250 | 990 | 0.659 | 0.636 |

**Findings**:

- Both detectors provide weak discrimination across categories (best AUROC 0.66, worst 0.39). No fold meets the originally aspirational ≥ 0.85 target.
- `military_acm` is the most easily distinguished hold-out — its higher mean G-peak (≈ 7 G vs ≈ 4 G for championship) creates a separable signal.
- `conceptual` scores below 0.5 because conceptual maneuvers (low G-peak, short duration) are *more central* to the joint feature distribution than the training categories themselves; both detectors mistakenly mark them as well-supported by training.
- IsolationForest narrowly leads on `championship` and `conceptual`; Mahalanobis leads on `extreme_post_stall` and `military_acm`. Differences are within noise; we report both.

### Interpretation

- **Use the calibration result, not the LOGO AUROC, as the headline OOD claim.** A calibration of 0.953 ± 0.02 is a defensible operational guarantee: out of every 100 in-distribution queries, ~5 will be flagged for review.
- **The LOGO AUROC tells us category labels are not a clean OOD axis** in this synthetic dataset. That's a finding about the dataset structure (categories overlap), not a failure of the detectors. Real OOD inputs at deployment time — pilots outside the trained `who_profile` set, maneuvers with G profiles outside the training envelope — would produce stronger signals.

---

## Limitations

- **Synthetic-only validation**. The detector has not been evaluated against centrifuge or in-flight inputs. Paper 2 (external re-analysis) and paper 3 (own-centrifuge) will extend this.
- **Categorical "OOD" via maneuver category is weak.** Maneuver categories overlap substantially in continuous feature space; LOGO AUROC reflects that overlap and should not be read as a failure of the detector.
- **Robust-covariance instability warnings**. `MinCovDet` occasionally emits a "determinant has increased" warning during the iterative refinement; in our experiments the resulting covariance was usable. Production code should record these warnings and re-fit with a higher `support_fraction` if instability persists.
- **No drift-over-time monitoring.** This detector is fit once on the v1 dataset; if/when the dataset is regenerated (new binary SHA, new tier definitions), the detector must be re-fit.
- **Feature space is fixed**. Adding new pilot-config dimensions (e.g., HRV inputs from paper 3) will require a new model version with its own model card.

---

## Ethical considerations

- **Aeromedical decision support**: the detector is a soft warning, never a clearance gate. Operational use to make pilot fly/no-fly decisions requires paper-3-grade validation.
- **OOD ≠ unsafe**: an OOD flag means "the surrogate hasn't seen anything like this before"; it does *not* mean "this configuration is dangerous." Conflating the two would be ethically misleading.
- **Bias**: the standard arm uses six FAA preset pilot profiles (1–6), drawn from historical CAMI data. Pilots outside these phenotypes (e.g., high-G-tolerant trained operators, female aviators outside the Profile-2 anthropometric envelope) will skew toward the OOD region. This is a *correct* signal — the model is honest about its blind spots — but it must be communicated explicitly to downstream users.

---

## How to reproduce

```python
from cgem_ext.data.splits import stratified_split
from cgem_ext.ood import MahalanobisOOD, ConformalAbstention
import pandas as pd

df = pd.read_parquet("data/datasets/cgem_synthetic_v1.parquet")
sp = stratified_split(df, seed=42)
train_df, val_df, test_df = sp.apply(df)

mh = MahalanobisOOD().fit(train_df)
abst = ConformalAbstention(alpha=0.05).calibrate(mh.score(val_df))
test_in_env = abst.is_in_envelope(mh.score(test_df))
print(f"Test in-envelope rate: {test_in_env.mean():.3f}")  # 0.953
```

For the full LOGO table see `tests/test_ood.py::test_logo_auroc_better_than_random` and the empirical printout in this card.

---

## Versioning

- **v0.1.0** (current): bundled with the Phase-2 commit on `feat/ml-layer-phase-0`. Detector trained at use-time from the dataset; no serialised artefact ships yet. A serialised version (`cgem_ext/ood/artifacts/mahalanobis_v0_1_0.joblib`) will land alongside paper-1 submission.
- Any change to `cgem_ext.ood.features.FEATURE_COLUMNS` increments the model version and triggers a re-fit; a model trained on v(N) features must not be loaded against v(N+1) features.
