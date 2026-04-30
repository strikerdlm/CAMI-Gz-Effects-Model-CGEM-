# TRIPOD-AI checklist

> **Citation:** Collins GS, Moons KGM, Dhiman P, *et al.* TRIPOD+AI
> statement: updated guidance for reporting clinical prediction models
> that use regression or machine learning methods. *BMJ* 2024;385:e078378.
> doi:10.1136/bmj-2023-078378.
>
> The checklist is supplementary to the AMHP submission. Each item
> below maps to a manuscript section / page / line range and a brief
> note. Where TRIPOD-AI uses sub-items, the reporting location is
> repeated for each sub-item that applies.
>
> Manuscript file: `docs/publication/manuscript.md` (this PDF is
> rendered from that source).

## Title and abstract

| # | Item | Reported in | Note |
|---|---|---|---|
| 1 | Title — identifies the study as developing/validating an ML prediction model | Manuscript title | "Conformal ML emulation and OOD detection for the FAA CGEM G-LOC model" |
| 2 | Abstract — structured (background, methods, results, conclusions) | §Abstract | Unstructured per AMHP §3 (250 words) — content covers all four elements |

## Introduction

| # | Item | Reported in | Note |
|---|---|---|---|
| 3a | Explain the medical context | §1 ¶1 | G-LOC risk in fighter / aerobatic / high-performance flight |
| 3b | Explain the rationale for developing the model | §1 ¶2–4 | Three CGEM gaps motivate the additive ML extension |
| 4 | Specify objectives | §1 ¶4 | "Emulate CGEM 180× faster + calibrated intervals + OOD detection + sensitivity" |

## Methods

| # | Item | Reported in | Note |
|---|---|---|---|
| 5a | Source of data — describe key elements of study setting | §2.2 | Synthetic CGEM dataset; cross-product input grid |
| 5b | Source of data — eligibility criteria | §2.2 | All 72 registered maneuvers × 45 pilot configurations |
| 5c | Source of data — relevant dates | §2.2 | Dataset generated 2026-04, master seed 42 |
| 6a | Outcome — definition | §2.4 | Five targets: time_to_greyout/blackout/gloc_s, hlap_min, c_bank_min |
| 6b | Outcome — methods of measurement | §2.4 | CGEM Fortran integration; right-censored event times |
| 7a | Predictors — definition | §2.4 | 17-d feature space (9 numeric + 7 one-hot WHO + 1 ordinal cm) |
| 7b | Predictors — methods of measurement | §2.4 | Encoded from PilotConfig + maneuver descriptors |
| 8 | Sample size | §2.2 | 3,240 rows; n=2,267 train / 486 val / 487 test |
| 9 | Missing data | §2.2 | Right-censored event times handled via two-stage classifier-then-regressor |
| 10 | Model development — model type | §2.4 | XGBoost (per-target); RF baseline |
| 10a | Model development — algorithm parameters | §2.4 ¶2 | n_est=400, max_depth=6, eta=0.05, monotonicity constraints |
| 10b | Model development — feature engineering | §2.4 / `cgem_ext.ood.features` | 17-d feature space; ordinal encoding for cm; one-hot for WHO |
| 11 | Model performance — calibration | §2.4 ¶4 | Mondrian split-conformal + ECE on classifier stages |
| 12 | Model evaluation — held-out method | §2.3, §3.2 | 70/15/15 stratified; LOGO for OOD |
| 13 | Risk groups | N/A | Not a clinical risk-group study |
| 14 | Hyperparameter tuning | §2.4 ¶3 | Defaults; formal Optuna search deferred to OSF-pre-registered Phase-3 polish |

## Results

| # | Item | Reported in | Note |
|---|---|---|---|
| 15 | Participants — flow diagram | §3.1, Figure 6 (architecture) | Dataset composition by category |
| 16 | Model development — characteristics | §3.2, Table 1 | Per-target R², RMSE, RF baseline |
| 17 | Model performance — discrimination | §3.2 | Classifier AUROC ≥ 0.996 |
| 18 | Model performance — calibration | §3.3, Table 2; §3.4, Table 3 | Conformal coverage; ECE per target |
| 19 | Subgroup analysis | §3.3, Table 2 (per-stratum) | By maneuver category |
| 20 | OOD performance | §3.5, Table 4 | Mahalanobis vs IsolationForest LOGO AUROC |

## Discussion

| # | Item | Reported in | Note |
|---|---|---|---|
| 21 | Interpretation | §4.1 | Three principal findings + caveats |
| 22 | Limitations | §4.4 | Synthetic-only validation; dataset coverage; six FAA presets; weak time-to-G-LOC; conservative OOD threshold |
| 23 | Implications | §4.2 | Parametric planning; real-time advisory; personalized risk |
| 24 | Future research | §4.6 | Papers 2 & 3; heteroscedastic conformal; Bayesian per-pilot calibration |

## Other information

| # | Item | Reported in | Note |
|---|---|---|---|
| 25 | Pre-registration | §2.7 | OSF pre-registration before any test-set evaluation |
| 26 | Code availability | §4.5 | `strikerdlm/CAMI-Gz-Effects-Model-CGEM-` (MIT, GitHub) |
| 27 | Data availability | §4.5 | `cgem_synthetic_v1.parquet` + sidecar; Zenodo DOI at submission |
| 28 | Reporting standard | This file | TRIPOD-AI; supplementary |
| 29 | Funding | Title Page | None (self-funded) |
| 30 | Conflicts of interest | Title Page | None |
| 31 | Acknowledgments | Title Page | FAA CAMI for CGEM source/binaries; AI tool disclosure |

---

## Mapping to AMHP-specific concerns

- **Clinical decision-making boundary.** The TRIPOD-AI framework is
  designed for clinical prediction models. This work is explicitly
  *not* a centrifuge-validated clinical model — see the manuscript
  Limitations (§4.4) and the OOD/emulator model cards
  (`docs/models/`). The framework is presented as a methodological
  contribution; clinical use is gated on Paper 3 (own-centrifuge
  validation against subjects).
- **Generative AI disclosure.** Per AMHP §5 and TRIPOD-AI §10b, AI use
  is disclosed in the cover letter, in the manuscript Methods (§2.8),
  and on the Title Page acknowledgments.
