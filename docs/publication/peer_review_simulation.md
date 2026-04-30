# Simulated AMHP peer review — Reviewer 2

> **Disclaimer.** This is a self-administered, simulated peer review
> performed *before submission* to surface issues a real AMHP
> reviewer is likely to raise. It is intentionally critical and is
> not part of the editorial record. Use it as a stress-test; address
> the items below before clicking *Submit* in Editorial Manager.
>
> **Reviewer persona.** Aerospace medicine physician with centrifuge
> research experience and graduate-level (but not specialist)
> ML/statistics literacy — a representative AMHP reviewer. The
> editorial board includes both clinical aviation-medicine
> practitioners and human-performance researchers; this review is
> written from the clinical end of that spectrum, which is the
> harder audience for a methods paper.

---

## Manuscript

**Title:** Conformal ML emulation and OOD detection for the FAA CGEM
G-LOC model.

**Article type:** Research Article (claimed).

**Word count (body):** ≈ 3,146 / 6,000.

**References:** 16. **Tables:** 4. **Figures:** 6 (over the limit).

**Document under review:** `docs/publication/manuscript.md` at HEAD
of `main` (commit `d298570`); supplementary materials in
`docs/publication/{author_page,cover_letter,tripod_ai_checklist,
suggested_reviewers,references_verification,render_checklist}.md`;
figure source files at `data/results/figures/`.

---

## Recommendation

**Major revision.**

The manuscript is technically competent and the engineering work is
substantial, but in its current form it is a poor fit for AMHP's
reader profile and has three serious scientific and presentation
concerns that must be addressed before re-review:

1. **Audience mismatch.** This is an applied-ML methods paper dressed
   as an aerospace-medicine paper. The technical jargon density
   (Mondrian split-conformal, Mahalanobis χ², SALib Saltelli,
   monotonicity-constrained XGBoost, ECE) will lose most clinical
   AMHP readers in §2.4 and §2.5. The work itself may be a better
   match for *Computers in Biology and Medicine*, *Frontiers in
   Physiology*, or *npj Digital Medicine*. If the author insists on
   AMHP, the methods sections must be rewritten for an aeromedical
   reader who has heard of "machine learning" but has never trained
   a model. A 2–3 paragraph "ML primer" box would help.

2. **No real-world validation.** The headline claim — "emulator R²
   of 0.82–1.00, near-perfect AUROC, well-calibrated conformal
   intervals, ~180× speedup" — measures only how faithfully the
   surrogate reproduces *another model* (CGEM). No centrifuge
   subject, no actual flight, no real G-LOC event. The author is
   transparent about this, but AMHP's audience cares about pilot
   outcomes. A reviewer with centrifuge experience will ask, point-
   blank: *what does an R² of 0.82 against CGEM tell me about a
   pilot in my squadron?* The honest answer — "nothing directly" —
   is awkward for a Research Article. Either (a) defer the AMHP
   submission until paper 2 (external re-analysis) or paper 3
   (own-centrifuge) has empirical results, or (b) demote this to a
   *Brief Communication* (1,500-word limit) and reframe as a
   methodological note rather than a Research Article.

3. **The OSF pre-registration claim is not yet substantiated.**
   §2.7 asserts the pre-registration was timestamped before any
   test-set evaluation. The Reproducibility section §4.5 says the
   OSF DOI is "TBD at submission." This is a credibility risk: if
   the OSF posting is performed *after* the test-set numbers are
   already in the manuscript, the pre-registration is post-hoc and
   does not protect against p-hacking / threshold-shifting. The
   manuscript itself documents one such retrospective adjustment
   (the LOGO AUROC threshold was lowered from "≥ 0.85 originally
   aspirational" to a softer report). Reviewers will catch this.
   The OSF DOI must be live and timestamped *before* the AMHP
   submission, and the cover letter / Methods §2.7 must point to a
   resolvable DOI, not "TBD."

Beyond these three, several methodological and presentational
concerns are listed below. None individually is a knock-out, but
together they make the paper feel rushed.

---

## Strengths (acknowledged up front)

- **Reproducibility infrastructure is exemplary.** Open code, MIT
  license, datasheet (Gebru), model cards (Mitchell), Docker image,
  pre-registration intent, deterministic seeds — far above the AMHP
  median. This deserves explicit praise in the Discussion and may
  be the strongest single contribution.
- **Engineering of the conformal layer.** Mondrian split-conformal
  per-stratum is principled; the per-stratum coverage table (Table 2)
  is the right way to report it; the finite-sample correction
  `ceil((n+1)(1−α))/n` is the academically correct quantile.
- **The OOD calibration result (0.953 vs nominal 0.95).** This is
  the single most defensible empirical claim in the paper. Lead with
  it more.
- **Sensitivity-analysis section (§3.6).** Sobol + Morris pair, with
  S₂ interaction reporting on g_peak × profile_duration_s, is
  publishable on its own merits. The dehydration-dominates-HLAP
  result is a clean, physically interpretable finding.
- **Pulse-sim contract preservation.** The "additive ML wraparound,
  not rewrite" framing is a real contribution to the maintainability
  of legacy regulatory models. AMHP's reviewer pool may
  underappreciate this — emphasize it.

---

## Major comments

### M1 — Scope/audience fit (§1, §2 globally)

The Introduction makes a strong case for *what* CGEM lacks
(speed, UQ, OOD), but a weak case for *why an AMHP reader should
care*. Re-write §1 ¶3 ("We address these three gaps...") to lead
with operational consequences: *"a flight surgeon evaluating G-LOC
risk for a new pilot today must rely on point estimates with no
uncertainty bracket and no warning when the input is out-of-envelope.
This paper closes those gaps."* The technical machinery in §2.4,
§2.5, §2.6 should be supported by a short box or callout
re-explaining each ML term in aeromedical idiom (e.g., "conformal
prediction interval" = "calibrated 95 % bracket around the
prediction"; "Sobol total-order index" = "fraction of risk variance
attributable to a given input").

### M2 — Synthetic-only validation (§4.4 ¶1)

The current limitations paragraph names the gap but does not
quantify the cost. Add a paragraph estimating *bounds on real-world
performance* even in the absence of real data:
- Cite the historical CGEM validation literature ([4], [6]) with
  effect sizes — what is the typical CGEM-vs-centrifuge residual?
- State explicitly that the surrogate's R² of 0.82 against CGEM is
  an *upper bound* on its R² against centrifuge subjects, not a
  prediction of clinical performance.
- Drop the speculative "real-time advisory" language in §4.2 ¶2.
  Without centrifuge validation, claiming cockpit-integration
  feasibility is a stretch a reviewer will push back on. Replace
  with: "Future work (paper 3) will validate whether the surrogate's
  prediction latency is operationally adequate for cockpit
  integration."

### M3 — Pre-registration discipline (§2.7)

(See major concern #3 above.) Specific edits:
- Replace "TBD at submission" with the real OSF DOI before the
  cover letter is finalized.
- In §3.5, the LOGO AUROC threshold reframing ("originally aspirational
  ≥ 0.85, observed best 0.66") is a *change* between the
  pre-registered protocol and the reported result. This must be
  flagged explicitly in §3 as a deviation, with the date and
  rationale, in line with TRIPOD-AI item 14 and standard
  pre-registration practice. Currently it reads as if the lower
  threshold were always intended.
- The "search spaces frozen in `osf_search_spaces.json`" is not
  visible in the supplementary list (§Supplementary materials). If
  the file does not exist or is not posted, remove the claim.

### M4 — Statistical reporting

**Effect sizes and confidence intervals.** AMHP §12 expects effect
sizes where applicable. Tables 1, 3, 4 report point estimates with
no CI bands.
- Table 1 (R², RMSE): add bootstrap 95 % CIs.
- Table 3 (ECE): add bootstrap CIs (10 bins is small enough that
  ECE itself is noisy).
- Table 4 (LOGO AUROC): add bootstrap CIs. With n = 135 in the
  conceptual fold, the AUROC point estimate of 0.387 has a CI of
  roughly ±0.10 — meaning it could plausibly be 0.30 or 0.50.
  Without the CI, readers cannot judge whether Mahalanobis vs
  IsolationForest differences are real.

**Per-stratum coverage with sparse strata (Table 2).** The
"conceptual" stratum has 21 test rows; the empirical coverage
estimates have ±20 pp 95 % CIs (the manuscript notes this in §3.3
but the table itself does not). Either move the conceptual column
to a supplementary table, or annotate the cells with their CIs and
explicitly mark the unreliable ones.

**Multiple-testing.** The author reports H1 (a/b/c), H2, H3 (a/b),
H4 (a/b) — eight pre-registered hypotheses. There is no Bonferroni
or FDR adjustment discussion. For a methodological paper this is
acceptable but should be stated.

### M5 — Comparison to prior CGEM applications (§4.3)

Reference [5] (Burns & Kruger, *AvSEM* 1997, "Mathematical model of
G-LOC onset time: validation and sensitivity analysis") is directly
adjacent — it is a sensitivity analysis of a G-LOC mathematical
model, exactly what §3.6 reports. The current §4.3 dismisses prior
work in two sentences. Devote a full paragraph to:
- What did Burns & Kruger find? Which inputs did they identify as
  dominant?
- Are this paper's Sobol rankings (g_peak >> profile_duration >>
  others) consistent with or contradictory to Burns & Kruger's
  earlier finding?
- The same applies to ref [6] (Copeland, Knarr & Whinnery 2000) —
  what did they identify as dominant inputs, and how does the new
  Sobol decomposition compare?

This is the single biggest scientific gap in the paper. The reviewer
will not let it stand without engagement.

### M6 — The "180× speedup" claim

Two issues:
- **Single-row vs batch comparison.** The 9 ms / 50 µs comparison is
  for a single inference call. CGEM subprocess overhead (startup,
  file I/O, parse) is amortized in batch mode if you write a
  multi-row input deck (which the wrapper does support). Quote both
  numbers.
- **The Sobol claim of "~3 min via direct CGEM (acceptable but
  wasteful)."** Three minutes is *not* prohibitive for a Sobol study
  done once. The paper's case for the surrogate's necessity would be
  stronger if it were framed around use cases the surrogate
  *enables* (Monte Carlo over millions of pilot configurations,
  real-time advisory, in-cockpit prediction) rather than the Sobol
  case where direct CGEM is fine.

### M7 — Generative-AI disclosure granularity

The cover letter says AI was used for "code scaffolding, reference
formatting, editorial review of drafts." AMHP §5 prohibits AI in
*manuscript writing*; this disclosure must be more granular. State
explicitly:
- AI was *not* used to generate the abstract, results
  interpretation, discussion, or conclusions.
- AI was *not* used to invent citations. (The reference-verification
  log records two unverifiable references that *were* dropped during
  cleanup; this is a credit to the author, but the reviewer will ask
  whether AI generated the placeholder.)
- AI assistance was confined to: code scaffolding (per §2.8 with
  specific module names), Pandoc/Word formatting, and copy-editing.

This level of detail is not pedantic for AMHP — it is the standard
the journal explicitly requires. The current cover-letter phrasing
will be flagged.

### M8 — Single-author paper

The submission is by a single corresponding author. AMHP accepts
single-author papers but reviewers may probe the contribution
statement. The Title Page's ICMJE statement says the author
"designed the architecture, generated the dataset, trained the
models, ran the sensitivity analysis, interpreted all results,
drafted the manuscript." For a 3,146-word body covering ML
emulation, conformal prediction, OOD detection, sensitivity
analysis, FastAPI service, React frontend, and three planned
papers — the reviewer will want to see, in §4.5 Reproducibility,
explicit pointers to *which* code modules and *which* lines the
author personally wrote vs. AI-assisted. The git history is the
source of truth; cite specific commit ranges.

### M9 — Figure count

Six figures vs. the AMHP limit of four. The plan stated in the
Title Page — "move calibration (Fig 3) and OOD-score distribution
(Fig 4) to supplementary" — is fine but must be executed *before*
submission, not promised. The 4 main-body figures should be:
1. Parity plots (current Fig 1) — keep.
2. Conformal coverage (current Fig 2) — keep.
3. Sobol heatmap (current Fig 5) — keep.
4. System architecture (current Fig 6) — keep.

Demote Figs 3 (calibration) and 4 (OOD distribution) to
Supplementary Figs S1 and S2. Update all Results-section figure
callouts to match.

### M10 — Reference quality

The reference list shows clear evidence of late-stage cleanup (two
placeholder DOT/FAA technical reports replaced with correct
DOIs; two unverifiable references dropped). The internal log
`references_verification.md` documents this. **The reviewer will
not see that log.** What they will see is a 16-reference list with
9 DOI-bearing canonical entries and 7 entries flagged in the log
as `[verify]`. Before submission, the author must:
- Cross-check refs [1], [4], [5], [6], [16] against PubMed (PMIDs).
- Add ISBNs to refs [2] (Newman 2015) and [3] (Green 2016).
- Confirm that ref [12] (Boström COPA 2018) is `PMLR 91:24-38`,
  not a hallucinated volume number.

A reviewer who finds *one* fabricated or seriously mis-cited
reference will recommend rejection.

---

## Specific section comments

### Abstract

- "≥ 0.996 on the three censored targets" — the AUROC values were
  0.996, 0.999, 0.996, so "≥ 0.996" is a fair summary. Good.
- "under-coverage isolated to time-to-G-LOC (0.86)" — say *0.861*
  (consistent with Table 2) or *0.86 ± [bootstrap CI]*.
- "the framework preserves the validated model while adding..." —
  good closing. Could be stronger: name the operational gap closed,
  not the technical capability added.
- The abstract is 250/250 words — at the absolute limit. Trim 10
  more words to leave breathing room for typesetters.

### §1 Introduction

- ¶1 sets up G-LOC well but cites only [1-6]. Add a recent FAA or
  USAFSAM annual G-LOC incidence statistic if available.
- ¶3 ("However, CGEM has three limitations...") is the most
  important paragraph in the manuscript and needs to be rewritten
  for the aeromedical reader. Currently it leads with "computational
  cost" which is a software-engineering concern, not a clinical
  one. Lead with the clinical concern instead: *"a flight surgeon
  using CGEM today receives a single number with no uncertainty
  bracket and no warning if the input is out-of-envelope."*
- The "first of three planned" framing is unusual in AMHP. Either
  commit to publishing all three in AMHP (and say so in the cover
  letter as a series proposal to the EIC), or reframe so the three
  papers stand independently. Pre-announcing two unwritten papers
  is a credibility risk if either fails to materialize.

### §2.1 The CAMI G-Effects Model

- Description of CGEM is technically accurate but reads like a
  software-architecture description, not a physiological model
  description. An aeromedical reader needs to see: which ODE
  variables drive G-LOC, what the validation envelope of the
  underlying empirical data was (Burns/Whinnery centrifuge runs,
  USAFSAM data), what the published validation residuals look like.
- "subject type (`who_profile`...)" — using monospace for code
  identifiers in the paper body is jarring; the AMHP house style
  uses italic for variable names. Convert.

### §2.2 Synthetic dataset

- "USAFSAM/ASEM centrifuge profiles [8,9]" — make sure ref [9] is
  the FAI Aresti catalogue and that this citation is appropriate
  for "USAFSAM/ASEM centrifuge profiles." If profiles are from
  Aresti and from centrifuge data, this is two distinct sources;
  cite each properly.
- "fractional plasma volume loss" — at 0.7? That is a mortal-shock
  level of dehydration. Verify the dehydration-level units and
  semantics; 0.7 likely means "70 % of the maximum modeled
  dehydration scaling factor," not 70 % plasma volume loss. If so,
  rewrite to make the units unambiguous.
- "Each row carries a deterministic `row_seed` derived as
  `SHA256(master_seed || row_id)`" — SHA256 is overkill for
  reproducibility-only seeding (CRC32 or numpy's built-in seed
  derivation would suffice and is more readable). Not a blocker,
  but a minor signal of over-engineering.

### §2.4 Surrogate emulator

- "Censored targets use a **two-stage** pattern: stage 1 is an
  XGBoost binary classifier..." — this is fine but glosses over a
  subtle issue: the regressor is trained only on event-positive
  rows, which means the regressor's training distribution is biased
  toward higher-G maneuvers. Discuss whether this biases predictions
  on borderline cases.
- "Monotonicity constraints are applied where physiologically
  grounded" — list them in a table. The reviewer wants to see the
  9-feature × 5-target monotonicity matrix.
- The deferred Optuna hyperparameter search is a flag. Either run
  it before submission (the OSF pre-registration locks the *search
  space* but the reported numbers must come from the locked search,
  not from defaults), or strip the Optuna mention and present the
  default-hyperparameter results as the registered analysis.

### §2.5 Out-of-distribution detection

- The 17-d feature space mixes 9 numeric, 7 binary one-hot, and 1
  ordinal. The Mahalanobis distance is not well-defined for binary
  + continuous mixtures (it implicitly treats binary indicators as
  Gaussian, which is wrong). Acknowledge this limitation explicitly.
  The conformal layer compensates empirically, which is precisely
  the point — but the methodological caveat must be stated.

### §3 Results

- §3.1: dataset characteristics is one paragraph; this should be a
  Table (n per category × per arm × per countermeasure tier) so the
  reviewer can verify the 3,240-row arithmetic.
- §3.2: the Stage 1 classifier AUROC (0.996, 0.999, 0.996) on a
  *deterministic* dataset is unsurprising, as the manuscript notes.
  This is *not* a result; it is a sanity check. Consider relegating
  Stage 1 numbers to a single sentence and not Table 1.
- §3.3: Table 2 with `—` cells is visually confusing. Either drop
  the `—` strata or annotate them with the n value (e.g., "n=4").
- §3.4: Table 3 has 5 rows; combining with Table 1 may improve
  scanability. Consider a single per-target results table with
  AUROC, R², RMSE, ECE, conformal coverage in one row per target.
- §3.5 (the strongest result): split this into "calibration"
  (headline) and "discrimination" (exploratory) more clearly. The
  calibration result (0.953) deserves its own bolded sub-paragraph
  separately from the LOGO discussion.
- §3.6: the dehydration ST = 1.005 with S₁ = 1.005 is a Sobol
  finite-sample artifact (the indices should be ≤ 1). Annotate
  this in a footnote and report the bootstrap CI.

### §4 Discussion

- §4.1 ¶3: "An error of ±1.14 s on a G-LOC time prediction can be
  operationally significant." This should be quantified. At what
  G-onset rate does 1.14 s of error span the difference between a
  recoverable greyout and a G-LOC?
- §4.2: the three "Aeromedical implications" subsections are too
  speculative for a methods paper without operational validation
  (see major concern #2). Trim to a single short paragraph.
- §4.4 limitations is comprehensive but the *order* of items
  matters. Lead with the synthetic-only-validation limitation
  (currently first — good); follow with the OSF pre-registration
  discipline (currently absent — must be added per major concern
  #3).
- §4.5 "tests (80 tests, all passing)" is a software-engineering
  artifact, not a scientific result. Move to a footnote or to the
  Methods §2.8.

### §5 Conclusion

- "It is ready for downstream aeromedical research applications"
  is too strong without centrifuge validation. Soften: "It is
  *suitable as a research tool* for parametric studies, with
  operational deployment gated on Paper 3."

---

## Compliance against AMHP Feb-2026 Instructions for Authors

| Rule | Required | This manuscript | Status |
|---|---|---|---|
| Title length | ≤ 100 chars including spaces | 67 | ✅ |
| Running head | ≤ 30 chars, ALL CAPS | 26 | ✅ |
| Abstract | ≤ 250 words, unstructured | 250 | ⚠️ at the limit; trim 10 words for safety |
| Keywords | 3–5; none verbatim in title | 5; "G-induced loss of consciousness" overlaps with title's "G-LOC" abbreviation | ⚠️ edge case |
| Body word count | ≤ 6,000 (Research) | ≈ 3,146 | ✅ |
| In-text citations | Superscript Arabic | bracketed `[N]` in markdown | ⚠️ render-time conversion required |
| Reference style | NLM | mostly NLM; some `[verify]` | ⚠️ verify before submission |
| Reference count | ~25 guideline | 16 | ✅ |
| Tables | ≤ 4 | 4 | ✅ |
| Figures | ≤ 4 | 6 (claimed plan to demote 2 to supplementary) | ❌ must execute the demotion before submission |
| Title page | Depersonalized | yes | ✅ |
| Author Page | Separate file | `author_page.md` | ✅ |
| Generative AI disclosure | Required (§5) | present in cover letter, but too coarse | ⚠️ see major concern M7 |
| Statistical expertise statement | Required (§12) | present | ✅ |
| Suggested reviewers | ≥ 2 | 6 + 3 backups | ✅ |
| OSF / preprint disclosure | Required (§3) | OSF DOI is `[TBD]` | ❌ must be a live DOI by submission |
| TRIPOD-AI checklist | Required for ML in medicine | supplementary present | ✅ |

---

## Specific minor / typographical comments

- "Fortran-based physiological simulation model" → "Fortran-based
  physiological model." "Simulation model" is redundant.
- "in Oklahoma City" — drop; institutional location is not a
  citation requirement.
- "intra-abdominal and intra-thoracic pressure" — for the
  AGSM mechanism description, cite Newman 2015 [2] inline.
- The em-dashes in the abstract are inconsistent with body em-dash
  spacing. Pick one convention.
- "≈ 0.05" and "α = 0.05" used interchangeably; standardize on
  "α = 0.05."
- "p-value" never appears, but "performance" results are reported
  without significance testing. State explicitly that the held-out
  evaluation is *deterministic* (single train + test) and that
  bootstrap CIs (rather than p-values) are the appropriate
  uncertainty quantification.
- §3.6 ¶2 "ST = 1.005, S₁ = 1.005" — finite-sample noise allowing
  Sobol indices > 1; annotate.
- §4.5: the reference to "`Docs/Manual.md`" is a project-internal
  filename that has no meaning to a reviewer; drop or rename.

---

## Summary of recommended actions

| Priority | Item | Section |
|---|---|---|
| 🔴 Block | Live OSF DOI in cover letter and §2.7; remove all `TBD` placeholders | M3 |
| 🔴 Block | Verify all 16 references against PubMed/Crossref/DOI; replace any unverifiable | M10 |
| 🔴 Block | Demote 2 figures to supplementary; update §3 callouts and the figure-captions section | M9 |
| 🔴 Block | Fix `[N]` → superscript Arabic citation format in the rendered .docx | render checklist §3 |
| 🟠 Major | Rewrite §1 ¶3 and §4.2 for the aeromedical reader; add ML-primer box | M1 |
| 🟠 Major | Engage with [5] Burns & Kruger 1997 and [6] Copeland, Knarr & Whinnery 2000 in §4.3 | M5 |
| 🟠 Major | Quantify operational cost of synthetic-only validation in §4.4 | M2 |
| 🟠 Major | Granular AI disclosure in cover letter; specify what was *not* AI-assisted | M7 |
| 🟠 Major | Add bootstrap 95 % CIs to Tables 1, 3, 4 | M4 |
| 🟡 Minor | Annotate Sobol indices > 1 as finite-sample noise (§3.6 ¶2) | — |
| 🟡 Minor | Combine Tables 1 + 3 into a single per-target results table | §3 |
| 🟡 Minor | Drop "tests (80 tests, all passing)" from §4.5; this is engineering not science | §4.5 |
| 🟡 Minor | Standardize α / 0.05 / em-dash conventions throughout | global |

---

## Verdict for the author

The work behind this manuscript is real and the open-source artifact
is genuinely useful. The paper as written, however, is uncomfortable
in its chosen venue: it is too technical for AMHP's clinical
audience and too applied for the methods journals where the ML
machinery would be appreciated. The strongest single result — the
0.953 OOD calibration — is also the most reviewer-friendly; lead
with it.

**My honest recommendation, as a hypothetical reviewer:** accept
after major revision *if* (a) the four blocker items above are
fixed, (b) the rewrite for AMHP audience lands successfully, and
(c) the OSF pre-registration is verifiably live before submission.
Otherwise, redirect to *Computers in Biology and Medicine*, where
the methodological depth will be properly appreciated and the
synthetic-only validation is more defensible.

— *Reviewer 2 (simulated, pre-submission)*
