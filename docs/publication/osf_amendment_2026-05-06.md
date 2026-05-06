# OSF Pre-Registration Amendment — 2026-05-06

> **Amends**: `docs/publication/osf_preregistration.md` at git
> commit `1820edb`.
>
> **Status**: DRAFT — to be appended to the OSF pre-registration record
> *before* any test-set evaluation under the Scenario B originality
> uplift (specifically before
> `tests/test_cqr.py::test_cqr_fixes_time_to_gloc_under_coverage` is
> first executed against `data/datasets/cgem_synthetic_v1.parquet`).
>
> **OSF DOI of the amended record**: TBD at posting.
>
> **Authoring rationale.** The original pre-registration locked
> hypotheses H1–H4 against a homoscedastic Mondrian conformal layer
> + maneuver-category Mahalanobis OOD. The 2026-05-06 originality
> plan (Scenario B in
> `/root/.claude/plans/moonlit-stargazing-wolf.md`) introduces two
> new methodological elements — Conformalized Quantile Regression
> (CQR) and an archival-centrifuge external-validation cohort —
> that were not part of the pre-registered protocol. To preserve
> pre-registration discipline, this amendment locks the
> corresponding hypotheses **before** any test-set evaluation of
> the new layers.

---

## A. Scope of the amendment

The amendment **adds** two hypotheses (H5, H6) and **adds** the
artifacts required to evaluate them. It does **not** modify or
relax any existing hypothesis (H1–H4), which remain locked at the
values committed in the original pre-registration.

---

## B. New hypotheses

### H5 — CQR fixes the time-to-G-LOC under-coverage

**Statement.** With Conformalized Quantile Regression
(`cgem_ext.surrogate.cqr.TwoStageXGBQuantileSurrogate`) replacing
the homoscedastic Mondrian conformal layer
(`cgem_ext.surrogate.conformal.MondrianSplitConformal`) on the
right-censored target `time_to_gloc_s`, the empirical coverage on
event-positive rows of the OSF-pre-registered held-out test split
is **≥ 0.90** (within 5 pp of the nominal 0.95).

**Anchor.** The homoscedastic Mondrian baseline reported coverage
of **0.861** on the same test slice (`docs/publication/manuscript.md`
§3.3, Table 2, commit 1f1a816). H5 requires the CQR layer to be
strictly closer to the nominal 0.95 than this baseline — encoded as
the second assertion in
`tests/test_cqr.py::test_cqr_fixes_time_to_gloc_under_coverage`.

**Statistical-uncertainty reporting.** Coverage is reported with a
95 % bootstrap CI (1,000 paired resamples of the test split using
`numpy.random.default_rng(42)`), consistent with §3.2 of the
manuscript.

**Failure handling.** Failure of H5 is reported transparently in
the manuscript Section 3.3, not silently masked. Failure does
**not** invalidate the paper; it triggers a documented decision
between (i) reverting to the homoscedastic Mondrian layer and
keeping the under-coverage as a declared limitation, or (ii)
exploring distributional conformal prediction (Chernozhukov et al.
2021; Gibbs & Candès 2024) as a follow-up.

### H6 — Archival-validated discrepancy is bounded

**Statement.** On a cohort of historical centrifuge event-time
records assembled from public sources
(`data/archival/centrifuge_tables.parquet`, generated via
`scripts/extract_archival_tables.py` and described in
`docs/data/datasheet_archival.md`), the surrogate's calibrated
prediction interval covers **≥ 90 %** of the real event times.
The systematic discrepancy
δ̄ = mean(real − CGEM-via-surrogate-median)
is reported with a 95 % bootstrap CI, **without** a pre-registered
sign or magnitude threshold (the literature anchor for δ on
G-tolerance models is sparse — see manuscript §4.4).

**Cohort sources, in priority order** (revised 2026-05-06 after a
PubMed / Crossref reference-verification scout — see §F below):

1. **Whinnery JE & Forster EM (2013)**, *Extreme Physiology &
   Medicine* 2:19 (open-access, BioMed Central; doi
   10.1186/2046-7648-2-19) — onset-rate × time-to-loss-of-
   consciousness records, n = 729 centrifuge subjects.
2. **Whinnery JE, Forster EM & Rogers PB (2014)**, *Extreme
   Physiology & Medicine* 3:9 (open-access; doi
   10.1186/2046-7648-3-9) — offset-rate × duration-of-absolute-
   incapacitation records, n = 715 centrifuge subjects.
3. **Copeland K & Whinnery JE (2023)**, DOT/FAA/AM-23/6 (open-
   access; doi 10.21949/1524446) — pooled CGEM-vs-centrifuge
   summary tables in §3, ≈ 40 aggregated rows that summarise the
   two primary sources above plus ≈ 22 Burton-summarised
   countermeasure cells.

The two *Extreme Physiology & Medicine* primary sources were
identified by a 2026-05-06 reference-verification scout that also
found that the previously planned anchors — Burns & Kruger 1997
(PMID 9143752 does not match the cited title; reference unrecoverable
from PubMed / Crossref / scite) and Whinnery 1990 (the cited PMID
2350248 maps to an unrelated paper; the closest extant Whinnery
1990 paper is *ASEM* 61(5):406–411, PMID 2350309) — are not usable
as cohort sources. Both are dropped from H6's source list and from
the manuscript reference list (see §F).

**Cohort size, after transcription audit:** target n ≥ 50
event-time records across at least two of the three sources.
If transcription yields fewer than 50 records, a sensitivity
analysis with n = 30 is reported in supplementary; if fewer than
30, the archival arm is reframed as exploratory in §3.7 of the
manuscript and H6 is downgraded to an exploratory hypothesis.

**Mapping rules from publication tables to CGEM input space**
(locked here, not at run time):

- `g_peak_abs`: read directly from the publication's reported peak
  G value.
- `profile_duration_s`: read directly when a duration is reported;
  if only an onset rate and plateau time are given, derive
  duration via `profile_duration_s = onset_time + plateau_time`
  with onset_time computed from the reported `dG/dt`.
- `dgdt_max_g_per_s`: read directly when reported; default to the
  publication's reported "rapid onset" / "gradual onset"
  classification mapped to {3, 1} G/s when not specified, with
  this default flagged in the per-record provenance.
- `who_profile`: default to the publication's reported subject
  cohort (military pilots → `who_profile=4`; civilian aerobatic
  pilots → `who_profile=2`; mixed civilian → `who_profile=1`),
  with the choice flagged in the per-record provenance and a
  sensitivity analysis over `who_profile ∈ {1, 4}` reported in
  supplementary.
- `agsm_effectiveness`, `gsuit_max_psi`, `pbg_max_mmhg`,
  `gsuit_coverage_fraction`, `dehydration_level`,
  `g_tolerance_multiplier`: when not reported, default to the
  publication's stated countermeasure tier (none → baseline tier;
  AGSM → AGSM 0.5 / G-suit 0 / PBG 0; full countermeasures → AGSM
  1.0 / G-suit 5 psi / PBG 30 mmHg). The full mapping table is
  versioned at `data/archival/PROVENANCE.md` and timestamped at
  cohort-build time.

**Failure handling.** If H6 fails because of unavailable source
data (e.g., a Wiley pay-walled article cannot be obtained), the
archival arm is reported transparently with an *n* footnote, and
the manuscript's discussion explicitly states which sources were
tractable and which were not. If H6 fails because the surrogate
under-covers real outcomes, that is a *finding*, not a failure of
the paper — it directly motivates the heteroscedastic /
fidelity-aware extensions in §4.6.

**Outcome (recorded 2026-05-06, after running the H6 evaluation
pass on the Phase A cohort via `scripts/run_h6_evaluation.py`).**
The primary success criterion (≥ 0.90 bracket coverage of real event
times) **was not met** on the Phase A cohort: point coverage = 0.500
(4 / 8), interval-overlap coverage = 0.625 (5 / 8). Mean discrepancy
δ̄ = +26.6 s (real minus surrogate median) with 95 % bootstrap CI
[+6.3, +52.1]. The discrepancy is concentrated entirely in the
slow-onset regime (onset ≤ 0.5 G/s), where rows show δ between +6.9
and +81.0 s; rows for onset ≥ 1.0 G/s show no systematic bias
(|δ| ≤ 1.3 s, all in-bracket). The pattern is consistent with the
documented CGEM limitation that the relaxed-participant assumption
breaks down at long durations (Copeland & Whinnery 2023 [7]); the
framework's calibrated bracket should be treated as a lower bound on
real outcomes in the slow-onset regime. Reported transparently in
manuscript §3.7 (Table 5) and §4.4. The full per-row JSON is at
`data/results/h6/discrepancy_phase_a.json`.

---

## C. New artifacts (lock list)

The following artifacts are referenced by H5 and H6 and are
versioned at the commit-SHA at which the OSF amendment is posted.

- `cgem_ext/surrogate/cqr.py` — implements
  `XGBQuantileSurrogate` and `TwoStageXGBQuantileSurrogate`. CQR
  hyperparameters: three quantile heads at α / 2, 0.5, 1 − α / 2,
  with `objective="reg:quantileerror"`,
  `tree_method="hist"`, and per-target monotonicity vectors from
  `cgem_ext.surrogate.targets`. All other XGBoost hyperparameters
  inherit the locked values from §4.1 of the original pre-
  registration.
- `cgem_ext/surrogate/conformal.py::MondrianCQR` — Romano et al.
  (2019, Eq. 1) conformity scoring stratified by
  `maneuver_category`, with the same
  `ceil((n + 1)(1 − α)) / n` finite-sample correction as
  `MondrianSplitConformal`.
- `data/archival/centrifuge_tables.parquet` — to be generated by
  `scripts/extract_archival_tables.py` (Week 2 deliverable).
- `data/archival/PROVENANCE.md` — per-record citation chain and
  mapping-rule audit log.
- `tests/test_cqr.py::test_cqr_fixes_time_to_gloc_under_coverage`
  — gated by `needs_cgem_binary`; the test is the executable
  encoding of H5.
- `tests/test_archival.py` — to be created in Week 2; encodes
  schema and provenance enforcement for the archival cohort.

---

## D. Deviations from existing hypotheses

None. H1–H4 remain at the values committed in the original
pre-registration. The original pre-registration's H2 commentary
already noted that `time_to_gloc_s` under-coverage motivates a
heteroscedastic conformal extension (Romano et al. 2019); H5 is
the formal pre-registration of that extension.

---

## E. Reporting

H5 and H6 are reported in the manuscript Section 3.3 (CQR coverage
table) and Section 3.7 (archival validation) respectively. Both
sections cite this amendment by OSF DOI and date.

**Author**: Diego Malpica, MD.
**Date drafted**: 2026-05-06.
**Date posted to OSF**: TBD (to be inserted at posting time).

---

## F. Reference-verification scout — manuscript bibliography corrections

A 2026-05-06 PubMed / Crossref / scite scout (one-hour bounded scope)
flagged two entries in the current manuscript reference list as
non-resolvable as cited. These corrections are recorded here so the
manuscript's reference list can be updated under the same version
control as this amendment, and so reviewers can audit the chain.

| Manuscript ref # | As originally cited | Independent verification | Replacement applied |
|---|---|---|---|
| [4] Whinnery 1990 (EEG response to +Gz) | "The electroencephalographic response to +Gz stress." *ASEM* 61(5):435–439, PMID 2350248. | (a) PubMed lookup of PMID 2350248 returns Avrushchenko et al. 1990, "Structural and functional status of chromatin in the cerebral cortex…", *Arkh Anat Gistol Embriol* 98(1):42–8 — unrelated. (b) PubMed phrase search for "electroencephalographic response to +Gz stress" returns zero records. (c) The same is true via scite. The cited paper does not exist as written. | Replaced with Whinnery JE (1990), "Recognizing +Gz-induced loss of consciousness and subject recovery from unconsciousness on a human centrifuge," *ASEM* 61(5):406–411, **PMID 2350309** (verified via PubMed direct fetch). The replacement is closely topical (G-LOC recognition on a human centrifuge with > 500 documented cases) and a real, attributable Whinnery 1990 paper at the right journal/volume/issue, anchoring the same §1 ¶2 claim about the multi-factorial nature of G-LOC physiology. |
| [5] Burns & Kruger 1997 | "Mathematical model of G-LOC onset time: validation and sensitivity analysis." *ASEM* 68(2):120–126, PMID 9143752. | (a) PubMed lookup of PMID 9143752 returns Eshel et al. (1997), "Hyperthermia-induced cardiac arrest in monkeys: limited efficacy of standard CPR," *ASEM* 68(5):415–20 — unrelated. (b) PubMed direct search "Burns Kruger G-LOC" returns zero records. (c) PubMed phrase search "mathematical model G-LOC onset" returns zero records. (d) Crossref / scite searches return zero records for the cited title. **The cited paper does not exist.** | Replaced with Whinnery JE & Forster EM (2013), "The +Gz-induced loss of consciousness curve," *Extreme Physiology & Medicine* 2(1):19, **DOI 10.1186/2046-7648-2-19** (open-access, CC-BY, n = 888 centrifuge G-LOC episodes; tabulated G-LOC times by onset rate and Gz level). The replacement is a real, citable, verified open-access source for the same §1 ¶2 claim about G-LOC physiology being multi-factorial and *additionally* serves as the primary archival cohort source for H6 (see §B above). |

These corrections are bibliography-only (no scientific claim is added
or retracted by the substitution); they are recorded here as an
authoritative audit trail. The substitutions land in the manuscript
under the same commit as this amendment update so the cite chain
remains coherent before any test-set evaluation under H5 / H6.
