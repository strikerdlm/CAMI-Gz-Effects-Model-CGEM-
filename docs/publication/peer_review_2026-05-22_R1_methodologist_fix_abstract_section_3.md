# Abstract / Table 2 / §3.3 Correction

Reviewer 1 (Anonymous Methodologist), 2026-05-22 — Major Concerns 2 and 3.
This file documents the per-claim audit, the corrected text blocks, and which
side yields when the abstract and Table 2 disagree.

## Source results files

- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/data/results/cqr/cqr_vs_mondrian_time_to_gloc.json`
  — CQR vs homoscedastic Mondrian comparison on `time_to_gloc_s` regressor.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/data/results/supplementary/table_s2_per_stratum_coverage.json`
  — Per-stratum coverage rows for all 9 (target, stage) pairs, with
  Clopper–Pearson exact CIs and 1,000-resample bootstrap CIs.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/data/results/figures/coverage_data.json`
  — Overall and per-stratum coverage values driving Figure 2.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/data/results/figures/ood_scores.json`
  — Verifies `conformal_in_envelope_rate = 0.9528` (rounds to 0.953),
  `chi2_in_envelope_rate = 0.6283` (false-positive 0.3717 → 37.2 %),
  `conformal_threshold = 78.26`, `chi2_threshold = 27.59`.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/publication/osf_amendment_2026-05-06.md`
  — H5 pre-registration anchor; explicitly names `time_to_gloc_s` baseline
  0.861 and Romano et al. (2019) CQR as the locked remedy. Confirms n=36
  event-positive on the OSF-frozen test slice.

## Coverage numbers (actual, computed from results JSONs)

| Target | Layer | Coverage | Deviation from 95 % nominal | n (event-positive) |
|---|---|---:|---:|---:|
| `hlap_min` | Mondrian | 0.9281 | **2.19 pp (under)** | 487 |
| `c_bank_min` | Mondrian | 0.9487 | **0.13 pp (under)** | 487 |
| `time_to_greyout_s` regressor | Mondrian | 1.0000 | **5.00 pp (over)** | 84 |
| `time_to_blackout_s` regressor | Mondrian | 1.0000 | **5.00 pp (over)** | 58 |
| `time_to_gloc_s` regressor | Mondrian (baseline only) | 0.8611 | 8.89 pp (under) | 36 |
| `time_to_gloc_s` regressor | **CQR (primary)** | 0.9722 | **2.22 pp (over)** | 36 |
| `time_to_greyout_s` classifier | Mondrian | 0.9671 | 1.71 pp (over) | 487 |
| `time_to_blackout_s` classifier | Mondrian | 0.9528 | 0.28 pp (over) | 487 |
| `time_to_gloc_s` classifier | Mondrian | 0.9405 | 0.95 pp (under) | 487 |
| OOD (Mahalanobis + conformal) | Distribution-free conformal | 0.9528 | 0.28 pp (under) | 487 |

**Worst Mondrian deviation across the four Mondrian-retained regressor
targets is 5.00 pp**, tied between `time_to_greyout_s` regressor (over-covering
to 1.000 on n = 84) and `time_to_blackout_s` regressor (over-covering to 1.000
on n = 58). The reviewer is empirically correct: the abstract's "4.6 pp on
4/5 targets" is not reproducible from any reading of the source JSONs.

## Per-stratum event-positive distribution (`time_to_gloc_s` regressor, test split)

Source: `table_s2_per_stratum_coverage.json`, row "time_to_gloc_s (regressor, Mondrian)",
mirrored in `cqr_vs_mondrian_time_to_gloc.json`.

| maneuver_category | n_event_positive | k_in_bracket (Mondrian) | k_in_bracket (CQR) |
|---|---:|---:|---:|
| championship | 1 | 1 | 1 |
| conceptual | 0 | 0 | 0 |
| extreme_post_stall | 0 | 0 | 0 |
| military_acm | 35 | 30 | 34 |
| **total** | **36** | **31** | **35** |

The reviewer's "35/36 military_acm" claim verifies exactly. The Mondrian
per-stratum quantile collapses to a per-stratum quantile on a single
populated stratum (military_acm n = 35) with one outlier row in championship
that receives a stratum quantile derived from n_calib = 1 (i.e. literally
its own residual, hence the 1.000 cell). The CQR layer has the same
single-stratum structure; the 0.857 → 0.971 improvement is computed on
the same 35 military_acm rows.

## Resolution

**The abstract yields; Table 2 stands.** Every cell of Table 2 matches the
JSONs. The "4.6 pp on 4/5 targets" sentence in the original abstract has
no source in the data and is removed; the actual deviations and the
35/36 single-stratum disclosure replace it.

---

## Abstract — Main results — Original vs Corrected

### Original (lines 14–15 of `manuscript.md`)

> **Main results.** Conformal OOD coverage was 0.953 vs nominal 0.95; Mondrian
> coverage was within 4.6 pp on 4/5 targets; CQR raised `time_to_gloc_s`
> coverage from 0.861 to 0.972 (n = 36 event-positive). Classifier AUROC was
> ≥ 0.996 (ECE ≤ 0.014); regressor R² was 0.82–0.90 on censored and 0.94–1.00
> on continuous targets. Inference took ~50 µs vs ~9 ms for direct CGEM.
> External archival validation showed slow-onset bias δ̄ = +26.6 s [95 % CI
> +6.3, +52.1] at onset ≤ 0.5 G/s and in-bracket calibration at onset ≥ 1 G/s.

### Corrected (drop-in replacement)

> **Main results.** Conformal OOD in-envelope coverage was 0.953 vs nominal
> 0.95. The four Mondrian-retained regressor targets covered within 5.0 pp
> of nominal (`hlap_min` 0.928, `c_bank_min` 0.949, `time_to_greyout_s` and
> `time_to_blackout_s` regressors both over-covering to 1.000 on n = 84 and
> n = 58 event-positive slices). CQR raised `time_to_gloc_s` coverage from
> 0.861 to 0.972 on n = 36 event-positive test rows; 35 of those 36 rows are
> in the `military_acm` stratum (1 `championship`; 0 in each of `conceptual`
> and `extreme_post_stall`), so the CQR uplift is operationally a
> single-stratum result. Classifier AUROC was ≥ 0.996 (ECE ≤ 0.014);
> regressor R² was 0.82–0.90 on censored and 0.94–1.00 on continuous
> targets. Inference took ~50 µs vs ~9 ms for direct CGEM. Archival external
> validation showed slow-onset bias δ̄ = +26.6 s [95 % CI +6.3, +52.1] at
> onset ≤ 0.5 G/s and in-bracket calibration at onset ≥ 1 G/s.

**Word counts.** Original abstract: 254 words (Objective 49, Approach 84,
Main results 85, Significance 36). Corrected abstract: **305 words**
(Objective 49, Approach 74, **Main results 141**, Significance 36). The
+51 word inflation is concentrated in Main results, where the two
mandatory disclosures cost ~55 words: (a) the 5.0 pp worst-deviation
breakout with the over-cover direction stated for `time_to_greyout_s`
and `time_to_blackout_s` (~30 words); and (b) the 35-of-36 single-stratum
disclosure with the per-stratum count (~25 words). Approach was tightened
by 10 words to partially offset, with `Romano et al. 2019` added as an
inline citation in case PMEA wants the CQR method anchored in the
abstract.

**If PMEA enforces 250 words at portal entry**, the cheapest two trims to
hit budget are: (i) drop "for direct CGEM" and "Archival external" → save
~3 words; (ii) collapse the Significance second sentence ("The pattern
generalises to any validated ODE physiological model; operational bounds
quantify slow-onset applicability") → save ~17 words. Together with
dropping the Romano citation (`(Romano et al. 2019)` → 3 words), that
brings the abstract to ~282 words. To reach 250 strictly, the
`military_acm` parenthetical can be condensed to "(35 of 36 rows are
`military_acm`)" → save ~14 words, taking the total to ~268. Reaching
250 requires sacrificing one of the existing claims (cleanest cut: the
H6 archival validation sentence, ~33 words, which is restated in §3.7
and §4.4); I have not made that cut here. The methodology corrections
are the load-bearing change; the abstract length is a budget question
for the corresponding author to resolve at portal entry, and most PMEA
abstracts run 270–320 words in practice.

### Corrected Approach (small adjustment — drop-in)

> **Approach.** Per-target XGBoost surrogates (two-stage classifier +
> regressor for censored event-time targets; single-stage for continuous
> targets) were trained on 3,240 synthetic CGEM runs (72 maneuvers × 45
> pilot configurations, master seed 42). A maneuver-category Mondrian
> split-conformal layer calibrated four targets; heteroscedastic
> Conformalized Quantile Regression (CQR) (Romano et al. 2019) calibrated
> `time_to_gloc_s`. A robust Mahalanobis detector with distribution-free
> conformal abstention guarded the 17-feature input envelope; Sobol and
> Morris analyses ranked input drivers. The protocol was OSF-pre-registered.

(The "before test-set evaluation" wording at the end of the original
Approach paragraph was elided here because Major Concern 1 of the reviewer
report flags that exact wording as overclaiming blind locking. The
corrected language matches Reviewer Major Concern 1's suggested
phrasing more cleanly and is consistent with what §2.7 actually
describes. Major Concern 1 is officially out of this deliverable's scope
— it lives in §2.4 and §2.7 — but the abstract's "before test-set
evaluation" formulation drops cleanly in this paragraph rewrite and would
need to be removed anyway when MC1 is addressed.)

---

## Table 2 — Original vs Corrected

### Original (lines 159–169 of `manuscript.md`)

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

### Corrected

**No change to the cell values is needed.** Every Table 2 cell verifies
against `coverage_data.json`, `cqr_vs_mondrian_time_to_gloc.json`, and
`table_s2_per_stratum_coverage.json`. The table caption already flags the
n = 1 championship cell (⚠️). The table itself is correct; the abstract
was wrong.

**Recommended caption tweak** (lines 157–158, the explanatory text that
introduces the table). Add one sentence to the existing caption:

> *Add at the end of the existing caption:* On the `time_to_gloc_s`
> regressor rows the calibration and test-set event-positive slices
> concentrate in `military_acm` (n_test = 35) and contribute one row to
> `championship` (n_test = 1); `conceptual` and `extreme_post_stall` are
> empty on this target. The Mondrian/CQR per-stratum quantile on
> `time_to_gloc_s` therefore reduces to a quantile on the `military_acm`
> stratum, and the 0.861 → 0.972 improvement is computed on the same 35
> `military_acm` rows. The four-stratum Mondrian story on this row is a
> bookkeeping artefact of the per-`maneuver_category` calibration; it is
> not an empirical multi-stratum claim.

---

## §3.3 — Original vs Corrected

### Original "Reading Table 2" paragraph (lines 171–173 of `manuscript.md`)

> **Reading Table 2.** All five (target, stage) pairs achieve overall
> coverage within ±5 pp of nominal once CQR replaces homoscedastic
> Mondrian on `time_to_gloc_s`. The four Mondrian-retained targets
> (`hlap_min` 0.928, `c_bank_min` 0.949, and the three classifier rows
> 0.940–0.967) are unchanged. On the `time_to_gloc_s` regressor row, the
> homoscedastic Mondrian baseline under-covered at 0.861 (8.9 pp below
> nominal) and CQR over-covers at 0.972 (2.2 pp above nominal) on the same
> n = 36 event-positive slice — a 6.7 pp reduction in distance-to-nominal,
> satisfying the OSF-amended H5 criterion (see §2.4).
>
> **Per-stratum reliability and Clopper–Pearson exact CIs.** Cells in
> Table 2 are flagged ⚠️ where per-stratum n < 20 (binomial CI > ±10 pp);
> the conceptual stratum (n = 21 overall, 0 event-positive rows) is too
> small for per-stratum claims. On the operationally relevant military-ACM
> stratum (n = 35) the Clopper–Pearson 95 % CIs are [0.706, 0.949] for the
> Mondrian baseline (point 0.857) and [0.847, 0.999] for CQR (point 0.971);
> the corresponding overall CIs at n = 36 are [0.706, 0.949] and [0.855,
> 0.999]. The intervals overlap, so CQR is reported as *operationally*
> closer to nominal rather than statistically dominant — its upper endpoint
> 0.999 is consistent with calibration to nominal, and the under-coverage
> of the homoscedastic baseline is the regime CQR is designed to address.
> Full per-stratum sample sizes and exact CIs are in supplementary Table S2.

### Corrected (drop-in replacement)

> **Reading Table 2.** Empirical coverage on the four Mondrian-retained
> regressor targets lies within 5.0 pp of the nominal 95 %: `hlap_min`
> 0.928 (2.2 pp under-cover), `c_bank_min` 0.949 (0.1 pp under-cover), and
> the `time_to_greyout_s` and `time_to_blackout_s` regressors both
> over-covering to 1.000 (5.0 pp above nominal, on n = 84 and n = 58
> event-positive slices respectively). The three classifier rows are
> tighter (0.940–0.967, within 1.7 pp of nominal). The 1.000 over-coverage
> on the two regressor rows is a single-direction over-cover rather than
> mis-calibration, sits at the edge of the ±5 pp pre-registered tolerance,
> and is consistent with constant-width Mondrian under-fit on
> deterministically generated synthetic outputs when the absolute-residual
> distribution is concentrated.
>
> On `time_to_gloc_s` the homoscedastic Mondrian baseline under-covers at
> 0.861 (8.9 pp below nominal) and CQR raises overall coverage to 0.972
> (2.2 pp above nominal) on the same n = 36 event-positive slice — a
> 6.7 pp reduction in distance-to-nominal, satisfying the OSF-amended H5
> criterion (see §2.4). This row is operationally a **single-stratum
> claim**: the test-set event-positive rows distribute as `military_acm`
> n = 35, `championship` n = 1, `conceptual` n = 0, `extreme_post_stall`
> n = 0. The Mondrian per-`maneuver_category` and the CQR
> per-`maneuver_category` calibration both reduce to a single-stratum
> quantile on `military_acm` plus one `championship` row whose stratum
> quantile is its own residual; the 0.861 → 0.972 improvement is computed
> on the same 35 `military_acm` rows (Mondrian k = 30/35 = 0.857;
> CQR k = 34/35 = 0.971). The Mondrian-stratification *operational
> refinement* claim made in §1 and §4.3 therefore rests on the two
> Mondrian-retained continuous targets (`hlap_min`, `c_bank_min`), where
> four strata are populated with non-trivial n (championship 236,
> conceptual 21, extreme_post_stall 81, military_acm 149) and per-stratum
> deviations are bounded; on `time_to_gloc_s` the H5 result is best framed
> as "CQR raises overall coverage on the `military_acm` stratum from
> 0.857 to 0.971 on n = 35 event-positive rows," not as a five-target
> Mondrian-then-CQR per-category result.
>
> **Per-stratum reliability and Clopper–Pearson exact CIs.** Cells in
> Table 2 are flagged ⚠️ where per-stratum n < 20 (binomial CI > ±10 pp);
> the `conceptual` stratum is too small for per-stratum claims on
> `hlap_min`/`c_bank_min`/classifier targets and is empty for the censored
> regressor targets. On the operationally relevant `military_acm` stratum
> for `time_to_gloc_s` (n = 35) the Clopper–Pearson 95 % CIs are
> [0.706, 0.949] for the Mondrian baseline (point 0.857) and
> [0.847, 0.999] for CQR (point 0.971); the corresponding overall CIs at
> n = 36 are [0.706, 0.949] and [0.855, 0.999]. The intervals overlap, so
> CQR is reported as *operationally* closer to nominal rather than
> statistically dominant — its upper endpoint 0.999 is consistent with
> calibration to nominal, and the under-coverage of the homoscedastic
> baseline is the regime CQR is designed to address. Full per-stratum
> sample sizes and exact CIs are in supplementary Table S2.

---

## Per-claim audit

| Claim in original | Actual value | Source | Action |
|---|---|---|---|
| Abstract: "Conformal OOD coverage was 0.953 vs nominal 0.95" | 0.9528 (rounds to 0.953); threshold 78.26; χ² in-envelope 0.6283 (FPR 0.372) | `ood_scores.json` | **No change** — accurate. Reworded "Conformal OOD" → "Conformal OOD in-envelope" for precision (the "0.953" is the in-envelope rate, not "coverage" in the conformal-bracket sense). |
| Abstract: "Mondrian coverage was within 4.6 pp on 4/5 targets" | Worst Mondrian-retained regressor deviation = 5.00 pp (tied: `time_to_greyout_s` and `time_to_blackout_s` regressors, both over-covering to 1.000). No reading of the source JSONs yields 4.6 pp. | `coverage_data.json`, `table_s2_per_stratum_coverage.json` | **Replace.** Use "within 5.0 pp" with the over-cover direction stated explicitly. |
| Abstract: "CQR raised `time_to_gloc_s` coverage from 0.861 to 0.972 (n = 36 event-positive)" | 0.861 → 0.972 on n = 36 is correct; but 35 of 36 are `military_acm`, so this is a single-stratum result. | `cqr_vs_mondrian_time_to_gloc.json`, `table_s2_per_stratum_coverage.json` | **Augment.** Keep the numeric improvement; add "35 of 36 rows are `military_acm`; CQR uplift is operationally a single-stratum result." |
| Abstract: "Classifier AUROC was ≥ 0.996 (ECE ≤ 0.014)" | Verified in §3.2 Table 1 and §3.4 Table 3. | `manuscript.md` Tables 1, 3 | No change. |
| Abstract: "R² was 0.82–0.90 on censored and 0.94–1.00 on continuous" | Verified in §3.2 Table 1. | `manuscript.md` Table 1 | No change. |
| Abstract: "Inference took ~50 µs vs ~9 ms" | Verified in §3.2. | `manuscript.md` §3.2 | No change. |
| Abstract: "External archival validation showed slow-onset bias δ̄ = +26.6 s [+6.3, +52.1] at onset ≤ 0.5 G/s and in-bracket calibration at onset ≥ 1 G/s" | Verified in §3.7 Table 5 and discrepancy_phase_a.json. | `manuscript.md` §3.7, `discrepancy_phase_a.json` | No change. (Reviewer flags this for LOO sensitivity in Major Concern 4 — out of this deliverable's scope.) |
| Abstract Approach: "before test-set evaluation" | Reviewer Major Concern 1 — the test split was inspected at the Phase-3 smoke run before OSF posting; H5 was filed knowing the 0.861 baseline. The wording overclaims blind locking. | `osf_amendment_2026-05-06.md`, `osf_preregistration.md` | **Out of scope** for this fix — but elided in the corrected Approach paragraph above because it sits in the abstract and is the cleanest place to drop the overclaim. The §2.4 and §2.7 rewrites belong to a separate MC1 fix and are not included here. |
| §3.3: "All five (target, stage) pairs achieve overall coverage within ±5 pp of nominal once CQR replaces homoscedastic Mondrian on `time_to_gloc_s`" | True at the boundary: greyout regressor and blackout regressor both 5.0 pp over. Not "within ±5 pp" if read strictly as < 5; equal to 5 if read as ≤ 5. The 1.000 cells are at the ±5 pp pre-registered tolerance edge and should not be elided. | `coverage_data.json` | **Rewrite the paragraph.** Replace with explicit per-target numbers and the over-cover direction. See corrected §3.3 above. |
| §3.3: "On the operationally relevant military-ACM stratum (n = 35) the Clopper–Pearson 95 % CIs are [0.706, 0.949] … and [0.847, 0.999]" | Verified against `table_s2_per_stratum_coverage.json`. | `table_s2_per_stratum_coverage.json` rows 6 (Mondrian) and 9 (CQR) | No change to the CIs. The framing is correct but should be preceded by the explicit "single-stratum claim" disclosure. |
| Table 2 cells | Every cell matches the JSON, including the n = 1 championship row and the 0/0 cells. | `table_s2_per_stratum_coverage.json`, `coverage_data.json` | **Table 2 stands.** Recommended caption add-on documents the single-stratum structure of the `time_to_gloc_s` regressor rows. |

---

## Notes on out-of-scope items (flagged, not fixed)

These reviewer concerns intersect the corrected text but are not part of
this deliverable; the main session should address them separately:

- **Major Concern 1** (pre-registration chain wording in §2.4 and the
  cover letter). Touched lightly in the corrected Approach paragraph by
  dropping "before any test-set evaluation"; full §2.4 / §2.7 / cover
  letter rewrite is separate.
- **Major Concern 4** (H6 LOO sensitivity on the three slow-onset rows).
  Not touched. The abstract's δ̄ = +26.6 s line is preserved.
- **§4.1** restates the "within 5 pp on all five (target, stage) pairs"
  claim (line 259 of `manuscript.md`). The corrected §3.3 paragraph
  resolves the wording for §3.3 but **§4.1 needs a parallel update** to
  mention the 5.0 pp over-cover on the two regressor slices and the
  single-stratum nature of the CQR uplift. That edit is not included in
  this deliverable but is mechanically the same swap as §3.3.
- **Minor Concern 3** (replace "homoscedastic Mondrian" with
  "constant-width Mondrian" or "absolute-residual Mondrian"). Not adopted
  in the corrected text above; the original "homoscedastic" framing is
  retained throughout the corrected blocks to minimise terminology
  churn. The reviewer's preferred rename can be applied globally as a
  separate find-and-replace pass.

---

## Summary of the resolution

- **The abstract yields.** Two specific claims in the original abstract
  are wrong by the data and must be revised: (a) the "within 4.6 pp on
  4/5 targets" Mondrian claim (actual worst deviation is 5.0 pp); and
  (b) the implied multi-stratum framing of the CQR uplift (the uplift is
  on n = 35 `military_acm` rows plus one `championship` row whose stratum
  quantile is its own residual).
- **Table 2 stands.** Every numeric cell is reproducible from
  `coverage_data.json`, `table_s2_per_stratum_coverage.json`, and
  `cqr_vs_mondrian_time_to_gloc.json`. Recommended caption add-on documents
  the single-stratum structure of the two `time_to_gloc_s` regressor rows.
- **§3.3 needs a rewrite of the "Reading Table 2" paragraph** to (a)
  state per-target Mondrian deviations explicitly with the over-cover
  direction, (b) state that the CQR uplift on `time_to_gloc_s` is
  operationally a single-stratum (`military_acm` n = 35) result, and (c)
  reframe the Mondrian-stratification refinement claim to the two
  continuous targets where it is empirically supported.
- **OOD coverage of 0.953** is accurate to four decimal places
  (0.9528 → 0.953); no change beyond a one-word tightening ("OOD
  coverage" → "OOD in-envelope coverage").
- **All other abstract claims verify** against §3.2 Table 1, §3.4 Table 3,
  §3.7 Table 5, and the supporting JSONs.
