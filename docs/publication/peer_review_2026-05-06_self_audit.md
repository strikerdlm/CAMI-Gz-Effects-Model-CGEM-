# Single-reviewer self-audit — `manuscript.md` (HEAD `6edbaab`, 2026-05-06)

> **Status.** Pre-submission self-audit performed at HEAD of `main`. Builds on
> `peer_review_simulation.md` (2026-04 audit), `2026-05-01_ijnmbe-status.md`,
> and the OSF amendment of 2026-05-06. Surfaces what a real IJNMBE reviewer
> with command of the 2023–2025 conformal-prediction-for-dynamic-biology
> literature is likely to flag. Not part of the editorial record.

**Recommendation:** Major revision before IJNMBE submission. The work is
methodologically real and the engineering is exemplary, but it under-cites
the 2023–2025 conformal-prediction-for-dynamic-biology literature, mis-frames
its single most important real-world result (§3.7 H6), and bets the headline
calibration claim on a 36-row test slice. Fix those three and the paper is
publishable as-is in IJNMBE; if IJNMBE bounces on the *"standard procedure on
standard problem"* scope filter, the Q1 landing pad is **PLOS Computational
Biology** (Portela, Banga & Matabuena 2025 is the precedent), and the
cleanest pure-**Q2** landing pad is **Bioengineering (MDPI)**.

---

## 1 · What the manuscript gets right (acknowledged up front)

- **Additive-wrapper framing.** Preserving the FAA Fortran core byte-for-byte
  and pushing all ML into `cgem_ext/` is a real methodological contribution
  to the maintainability of legacy regulatory ODE models. The Pulse-sim
  downstream contract and `tests/test_contract.py` make the claim
  *executable*, which most "ML wrapper" papers don't.
- **Reproducibility infrastructure.** Datasheet (Gebru et al. 2018), model
  cards (Mitchell et al. 2019), TRIPOD-AI checklist, deterministic
  SHA-tagged binary, OSF pre-registration intent, MIT-licensed code with
  80 tests — well above the median for the venue.
- **OOD calibration.** The 0.953 in-envelope rate vs nominal 0.95 with a
  conformal threshold ~3× the χ² cutoff is the single most defensible
  empirical claim. Lead with it more visibly in the abstract.
- **Honest limitations.** §4.4 names every gap, and §3.7 admits H6 fails the
  ≥ 0.90 success criterion at slow onset. That kind of transparency is rare
  and should be preserved through revision.

## 2 · Major scientific concerns (in priority order)

### M1 · Two-stage classifier-then-regressor is the wrong baseline for right-censored event-time targets

The current pattern (`P(event)·E[time | event]` with a regressor trained
only on `event=1` rows) is the censoring-induced training shift that
**conformalized survival analysis** was specifically built to address. The
2023–2025 literature has moved past it:

| Reference | What it gives you |
|---|---|
| Candès, Lei & Ren 2023 (PMID 33758770) | Distribution-free finite-sample lower predictive bounds (LPBs) under Type-I censoring |
| Gui, Hannig & Hofmann 2024, *Biometrika* 111(2):459–477, doi:10.1093/biomet/asad073 | Adaptive cutoffs → more informative LPBs |
| Davidov, Feldman, Shamai, Kimmel & Romano 2025 (ICLR, OpenReview JQtuCumAFD) | **General** right-censored data, distribution-free finite-sample LPBs — directly applicable to `time_to_gloc_s` |
| arxiv:2412.09729 (ICML 2025) | Doubly-robust conformalized survival |

`time_to_gloc_s` is exactly the target where the under-coverage shows up
(0.861 → 0.972 with CQR), and §4.4 already concedes "the regressor is
trained only on event-positive rows" — that's the bias these methods
correct. **Action:** in the next revision, present **conformalized survival**
as the principled baseline and CQR as a complementary heteroscedastic layer;
do not present the two-stage pattern as the primary method. This single
change reframes the paper from "applied XGBoost wrapped in conformal" to
"principled UQ for censored event-time emulators of regulatory ODE models."
It also pre-empts the IJNMBE *"standard procedure on standard problem"*
scope filter directly.

### M2 · The Portela, Banga & Matabuena 2025 precedent is missing

- Portela A, Banga JR, Matabuena M. *Conformal Prediction for Uncertainty
  Quantification in Dynamic Biological Systems.* **PLOS Computational
  Biology** 21(5):e1013098 (2025). Software & supplement at Zenodo
  10.5281/zenodo.15396217.

This is the closest published methodological neighbour: conformal
prediction wrapped around a dynamic ODE biological model. Not citing it
will read as either ignorance of the field or evasion; both are bad.
**Action:** add to §1, §4.3, and the cover letter. Frame the present work
as the +Gz-physiology + Mondrian-by-maneuver-category + OOD-abstention
extension of the Portela framework. This also opens **PLOS Computational
Biology** as a Q1 fallback target — see §6 below.

### M3 · §3.7 (H6, archival cohort) is buried where it should be the headline

§3.7 contains the only **real-world** validation in the entire manuscript:
a calibrated discrepancy `δ̄ = +26.6 s [+6.3, +52.1]` between
CGEM-via-surrogate and an archival centrifuge cohort. Two issues:

- **The result is mis-located.** It belongs in the abstract (one sentence:
  "External validation against an archival centrifuge cohort revealed a
  slow-onset bias of +26.6 s [+6.3, +52.1] consistent with the documented
  muscle-tension limitation of CGEM") and in §3.2 as the prior to the
  synthetic-only validation table — not as §3.7 of an 8-section results
  block.
- **The cohort size is stale.** Recent commits (`5858b63`, "Phase B
  narrow-range + abstract anchor extraction (n=10 → cohort=23)") grew the
  cohort from 8 to 23. `manuscript.md` lines 235–244 still say `n = 8`.
  Update Table 5 with the Phase B rows or explicitly mark Phase A as the
  locked OSF anchor and Phase B as supplementary.

Also: the parent population is cited as "n_parent = 729 USN + USAF
participants." The Whinnery & Forster 2013 abstract reports
**888 G-LOC episodes**; 729 appears in a different figure (acceleration
onset rate). Reconcile the number against the original PMC source
(PMC3710154) before submission.

### M4 · The n=36 CQR claim is operationally true but statistically thin

The headline 0.861 → 0.972 CQR vs Mondrian comparison rides on a single
36-row event-positive test slice. Clopper–Pearson exact CIs of
[0.706, 0.949] and [0.855, 0.999] **overlap entirely**. Two missing
diagnostics:

- **Mean bracket width** (CQR vs Mondrian): if CQR widened the bracket to
  fix coverage, that is not heteroscedastic adaptation, it is inflation.
  The advantage of CQR is allowing width to **vary with x**; the per-row
  distribution of widths (median, IQR, max) belongs in Table 2 or a
  supplementary panel.
- **Conditional coverage diagnostics.** Per-stratum coverage is in Table 2
  already, but a calibration-error proxy (Worst-Slab Coverage Gap, e.g.
  Romano et al. 2020 group-balanced conformal) on the held-out test split
  would let the reader see whether the 0.972 overall coverage hides
  systematic per-stratum failures.

**Action:** add a "bracket width and conditional coverage" sub-table; do
not claim CQR "fixes" the under-coverage on n = 36 alone. This is also
where the OSF amendment language ("≥ 0.90 *and* strictly closer to
nominal") needs to be matched line-for-line in the test code.

### M5 · §3.8 multi-fidelity NARGP is a null result framed as a positive

`Table 6` reports MF-NARGP RMSE of **53.18 s and 56.38 s at
n_high ∈ {20, 50}** against an XGB baseline RMSE of 3.07–2.85 s. That is
not "MF-NARGP does not improve point estimates in this regime"; that is
**catastrophic GP discrepancy over-fit**. The "calibrated UQ at
n_high = 100" framing rescues only one row of one table.

Two principled options:

1. **Drop §3.8** and move to a "Future work — multi-fidelity coupling"
   mention in §4.6. The H6 slow-onset discrepancy (the regime where MF
   would help) is a more honest motivator than a benchmark that fails at
   n_high ≤ 50.
2. **Pivot to MF-DNN** (Meng & Karniadakis 2020, *J. Comp. Phys.*
   401:109020, doi:10.1016/j.jcp.2019.109020), with the residual-MFNN
   extension (Lv et al. 2024, *J. Phys. Conf. Ser.* 2913:012003,
   10.1088/1742-6596/2913/1/012003) or the C2³ combination model
   (Tang et al. 2024, *Mach. Learn. Sci. Technol.* 5:035071,
   10.1088/2632-2153/ad718f). MF-DNN's two-network linear/non-linear
   decomposition is robust at small n_high in a way Kennedy-O'Hagan /
   NARGP is not.

Option 1 is the lower-risk path for the IJNMBE submission timeline;
Option 2 is the better path for paper 2 or 3.

### M6 · OSF pre-registration is still `TBD at submission`

§2.7, §4.5, and the cover letter all reference an OSF DOI that is not yet
timestamped. With the Scenario B / H5+H6 amendment dated 2026-05-06
(`docs/publication/osf_amendment_2026-05-06.md`), **the amendment must be
live on OSF *before* the next CQR / H6 test-set run**, otherwise the
pre-registration discipline argument collapses and a reviewer who looks
at the OSF record will catch it. This is the single most fixable blocker
on the path to submission. Mint the DOI; replace every "TBD" placeholder;
cite resolvable URLs in §2.7 and the cover letter.

## 3 · Methodological tightening (not blockers, but worth doing)

- **Mahalanobis on a mixed feature space.** The 17-d frozen feature space
  is 9 numeric + 7 binary one-hot + 1 ordinal. Mahalanobis distance
  implicitly treats binaries as Gaussian. The conformal abstention layer
  compensates empirically (it's the entire point), but state the caveat
  explicitly and consider, as a robustness check, **Gower distance +
  conformal abstention** or an embedding-based OOD score for sensitivity
  analysis. Locally Adaptive Conformal Inference for Operator Models
  (Harris & Liu 2025, arXiv:2507.20975) is conceptually adjacent for a
  future iteration.
- **Multiple-testing on H1–H6.** With six pre-registered hypotheses (now
  eight after the H5/H6 amendment), bootstrap CIs are the right
  uncertainty quantification but the manuscript should state explicitly
  that no Bonferroni / FDR adjustment was applied because the hypotheses
  concern distinct estimands, not parallel statistical tests of the same
  effect.
- **Adaptive conformal SOTA is *not* a current gap.** Gibbs & Candès 2022
  (FACI), Bhatnagar et al. 2023 (SF-OGD, SAOCP), Zaffran et al. 2022
  (AgACI), and Susmann/Chambaz/Josse 2023 (`AdaptiveConformal` R package,
  arxiv:2312.00448) are designed for streaming / online distribution
  shift. The CGEM paper is a held-out batch evaluation; cite as "future
  work for cockpit-deployment streaming inference," do **not** add as a
  method gap.

## 4 · Reporting and presentation

- **Figure 1 (parity, 8 panels).** With CQR added in §2.4/§3.3, panels (G)
  and (H) (G-LOC classifier + regressor) need a parallel CQR-bracket
  overlay so the reader can visually confirm the heteroscedastic-vs-
  homoscedastic difference Table 2 reports.
- **Table 2.** Add a "method" column (Mondrian / CQR / classifier-only) to
  make the comparison rows machine-readable. Move the 0.972 bolded value
  to a per-row clarifier that the value is achieved **at the cost of
  marginal over-coverage** (point 2.2 pp above nominal) — let the reader
  see the trade-off in one cell.
- **Sobol indices > 1 (§3.6 ¶2).** ST = 1.005, S₁ = 1.005 for
  `dehydration_level` is finite-sample noise. The footnote "the slight
  overshoot above 1.0 is finite-sample noise from N = 1,024" is correct
  but reads as ad-hoc; the bootstrap CI [0.92, 1.07] should be in the
  table itself, not narrative-only.

## 5 · Improvement plan (ranked by leverage on the IJNMBE submission)

| Priority | Action | Expected impact | Effort |
|:-:|---|---|:-:|
| 🔴 1 | Replace two-stage classifier+regressor framing with **conformalized survival** (Candès/Lei/Ren 2023; Gui et al. 2024; Davidov et al. 2025) as the principled baseline; CQR becomes the heteroscedastic complement, not the primary tool | Reframes the methodological contribution from "applied XGBoost" to "principled UQ for censored emulators of regulatory ODE models" — directly defuses the IJNMBE scope filter | 2–3 days |
| 🔴 2 | Cite **Portela, Banga & Matabuena 2025** in §1, §4.3, and the cover letter; reframe the Discussion contribution against this precedent | Closes the single biggest prior-art gap; opens PLOS Comp Biol as Q1 fallback | 30 min |
| 🔴 3 | Move §3.7 H6 result to the abstract + §3.2 prelude; update cohort size from n = 8 to n = 23 (Phase B); reconcile the 729-vs-888 W&F2013 parent count | Promotes the only real-world validation result; corrects a stale number | 2 hrs |
| 🔴 4 | Mint Zenodo DOI; mint OSF pre-registration with H5/H6 amendment; replace all "TBD at submission" placeholders | Submission blocker | 45 min (manual) |
| 🟠 5 | Either drop §3.8 and reduce to a §4.6 future-work paragraph, **or** pivot to MF-DNN (Meng & Karniadakis 2020) with residual-MFNN benchmark | Removes a null result from the body; or strengthens it with a SOTA architecture | 1 hr (drop) / 5 days (pivot) |
| 🟠 6 | Add bracket-width and per-stratum conditional coverage diagnostics for CQR vs Mondrian on `time_to_gloc_s` | Closes the M4 statistical-thinness gap; differentiates "calibration via heteroscedasticity" from "calibration via inflation" | 1 day |
| 🟠 7 | Trim the conceptual-stratum row from Table 2 to a supplementary table; add Clopper–Pearson CIs on every empirical-coverage cell | Removes a row a reviewer will catch on for n < 20 | 2 hrs |
| 🟡 8 | Re-render Fig 1 with CQR bracket overlays on panels (G)+(H); audit Figs 3, 4 for greyscale tints (IJNMBE rule 6.2) | Pre-empts IJNMBE figure-style rejection at first decision | 4 hrs |
| 🟡 9 | Add an explicit "no Bonferroni/FDR" sentence to §3.2 and a Mahalanobis-on-mixed-features caveat sentence to §2.5 | Closes minor reviewer-trap items | 30 min |
| 🟡 10 | State explicitly in §4.6 that adaptive conformal (FACI, AgACI, SAOCP) is the natural extension for streaming cockpit deployment, not the current setting | Demonstrates command of the conformal SOTA without over-promising | 30 min |

## 6 · Q2 venue recommendation

The user's ask was explicitly Q2. The strongest **pure Q2** target is
*Bioengineering (MDPI)*; the strongest **scope-matched fallback if IJNMBE
rejects** is the Q1-but-precedented *PLOS Computational Biology*. Three
options ranked by methodological precedent and review profile:

| Rank | Journal | Quartile | APC | Scope fit | Precedent / why |
|:-:|---|:-:|---|---|---|
| 1 | **Bioengineering** (MDPI), ISSN 2306-5354 | **Q2** (SJR 0.735, IF 4.34, Q2 in Bioengineering) | CHF 2,600 (≈ USD 2,800), CC BY | Scope explicitly covers "modeling, simulation, computational methods in biomedical engineering applications" — the additive ML wrapper of a validated ODE model fits cleanly | Open access, fast review (median ~ 30 days to first decision), no Highlights/Novelty mandatory files. Methodological-content review profile. |
| 2 | **Aerospace** (MDPI), ISSN 2226-4310 | **Q2** (IF 2.2, Q2 Aerospace Engineering) | CHF 2,400 (≈ USD 2,600), CC BY | Domain match for the +Gz / G-LOC framing; scope covers human-factors and pilot performance | Open access. The aerospace-medicine framing of the abstract is more visible here than at Bioengineering; trade-off is methodological depth gets less reviewer attention. |
| 3 | **Machine Learning: Science and Technology** (IOP), ISSN 2632-2153 | **Q1 borderline** (Q2 in some sub-categories) | ~ USD 2,000 (waivers available) | Methodological core (conformal + OOD + MF + Sobol on a physics emulator) is exactly the venue's wheelhouse | **Direct precedent:** Gopakumar et al. 2024–2026, *Uncertainty Quantification of Surrogate Models using Conformal Prediction*, accepted at ML:S&T (arXiv:2408.09881). If IJNMBE bounces and Bioengineering feels too generalist, this is the methodologically-best home. |
| Stretch (Q1 fallback if IJNMBE rejects) | **PLOS Computational Biology**, ISSN 1553-7358 | Q1 (Modeling and Simulation, Computational Theory and Mathematics); Q2 in Genetics / Molecular Biology sub-categories | USD 3,165 (waiver policy) | Closest scope precedent in the entire field | **Portela, Banga & Matabuena 2025** (e1013098) is the published precedent for "conformal prediction for ODE biological systems" — same methodological neighbourhood, accepted by this venue last year. |

**Recommendation:** stay the IJNMBE course (the audit lists ~ 4 hrs of
fixes; do them). If IJNMBE returns the manuscript without review under
the scope filter, **redirect to PLOS Computational Biology** with the
Portela 2025 framing in the cover letter — the manuscript's methodological
depth is wasted at a pure-aerospace Q2 venue. **Bioengineering** is the
right Q2 backup if PLOS Comp Biol also passes, not the primary target.

## 7 · Final note

The author's own pre-submission discipline (the H5 OSF amendment dated
*before* any test-set run; the explicit transparency on §3.7's failure
to meet H6's primary criterion; the honest framing of §3.8 as
"calibrated UQ, not point-estimate gain") is the strongest signal in this
package. Most submissions of this scope hide their negative results;
this one foregrounds them. Preserve that through revision — it is what
makes the manuscript publishable.

— *End of single-reviewer report*
