# Reviewer Report — Physiological Modelling
**Reviewer:** Anonymous Reviewer 2
**Date:** 2026-05-22
**Manuscript:** *An additive ML wrapper for validated ODE physiological models: conformal prediction, out-of-distribution detection, and global sensitivity, applied to the FAA CAMI G-Effects Model* (sole author Diego Malpica).
**Venue:** *Physiological Measurement* (IOP), Research Paper.
**Recommendation:** **Major Revisions.**

---

## Summary of the manuscript

The author wraps the FAA Civil Aerospace Medical Institute's CGEM Fortran ODE model (cerebrovascular and cerebral oxygenation physiology under sustained +Gz load) with an additive ML layer comprising (a) per-target XGBoost surrogate emulators (two-stage classifier + regressor for right-censored event-time targets, single-stage for continuous targets) trained on 3,240 synthetic CGEM runs, (b) a Mondrian split-conformal layer stratified by maneuver category for four targets and a heteroscedastic Conformalized Quantile Regression (CQR) layer for `time_to_gloc_s`, (c) a robust-Mahalanobis OOD detector with distribution-free conformal abstention over a 17-dimensional mixed numeric/categorical input space, and (d) Sobol + Morris global sensitivity decomposition driven through the surrogate. The validated Fortran core is not modified. The protocol was OSF-pre-registered (master seed 42, frozen split indices, success thresholds locked before any test-set evaluation; CQR and an archival external-validation arm added as pre-registered amendments before the corresponding analyses were run). The manuscript reports satisfactory regressor performance (R² = 0.82–1.00), near-perfect classifier AUROC (≥ 0.996), conformal OOD coverage 0.953 vs nominal 0.95, and a partial archival validation against n = 8 pooled mean ± SD records from Whinnery & Forster (2013) showing a slow-onset bias of δ̄ = +26.6 s [95 % CI +6.3, +52.1] concentrated at onset ≤ 0.5 G/s and in-bracket calibration at onset ≥ 1 G/s.

The methodological execution is competent, the pre-registration discipline is genuine (the H6 partial failure is declared, the `time_to_gloc_s` regressor R² 95 % bootstrap lower bound of −0.055 is left in Table 1 rather than hidden, and CQR is reported side-by-side with the homoscedastic Mondrian baseline it replaces), and the engineering deliverables (Python package, FastAPI service, Docker image, frontend, OSF lock, Zenodo dataset) are appropriate for a methods paper. The paper is in scope for PMEA's "physiological modelling, simulation, model identification, and control" clause and for the "physics- and model-based machine learning" clause. However, several headline claims outrun the evidence base, and the manuscript currently reads as more of an aerospace-physiology demonstration paper with a methodological frame than as a PMEA generalizable-methods paper. The required revisions are tractable but substantive.

---

## Major concerns

### M1. The generalization claim "the pattern generalises to any validated ODE physiological model" is unsupported by a single demonstration.

The Abstract ("the pattern generalises to any validated ODE physiological model"), §1 ("the wrapper extends [Portela et al. 2025] … into a specific regulatory aerospace-physiology setting"), §4.2 ("the same surrogate + conformal + OOD pattern applies to any validated ODE physiological model that must be made computationally tractable and uncertainty-aware"), and §4.6 ("the wrapping pattern reported here … is publisher-agnostic, and is intended as a reference implementation for any model in that class") all state or imply that the demonstrated wrapper generalizes beyond CGEM. The paper provides no worked argument for this. The closest published precedent — Portela, Banga & Matabuena (2025, *PLOS Comput Biol*) — is cited only as motivation; the present paper does not show, even argumentatively, that the same stack (XGBoost surrogate + Mondrian conformal + CQR + robust-Mahalanobis with conformal abstention) would behave comparably on a different validated ODE physiological model — e.g., the Guyton cardiovascular model, a baroreflex Markov model, the Pulse Physiology Engine, or HumMod. From a PMEA-readership perspective the generalization claim is the *paper-level* claim — without it, this is an aerospace-medicine paper.

For acceptance the author should either (a) add at least a conceptual worked example on one additional ODE physiological model class (a Pulse benchmark scenario, a 1D arterial-flow Boileau-style benchmark, or even a Guyton-reduced-form demonstration in supplementary would suffice — the comparison need not match the depth of the CGEM analysis, only show that the wrapper components map cleanly), or (b) tone the claim throughout to "the wrapper components — XGBoost surrogate, Mondrian / CQR conformal layers, conformal-abstention OOD — are demonstrated on CGEM here and are in principle applicable to similar validated ODE physiological models; cross-model validation is left for future work." The current language sits between (a) and (b) and reads as an unearned promise.

### M2. "The framework is well-calibrated in the rapid-onset regime" rests on n = 4 records.

The §3.7 / §4.1 operational interpretation is that the framework is well-calibrated at onset ≥ 1 G/s — the fighter and aerobatic regime — and biased at onset ≤ 0.5 G/s. The four "rapid-onset" archival points in Table 5 are onset = 1.00, 2.00, 5.00, and 10.00 G/s, all from a single archival cohort (Whinnery & Forster 2013, parent n = 729 for the relaxed-subject subset). Four point estimates, all from one center's reproduction, are not a calibration claim that supports the manuscript's confidence in the operational envelope. The corresponding 95 % bootstrap CI for the rapid-onset δ̄ is presumably tight only because of the small range of |δ| values, not because of cohort breadth. A PMEA reader will read "well-calibrated in the rapid-onset regime" as an operational guarantee; it is, at present, a four-data-point pattern.

Recommended fix: explicitly mark the rapid-onset calibration as **exploratory** wherever it appears (§3.7 "Operational interpretation", §4.1 "Principal findings", and the Abstract "Significance" sentence). Either pre-commit to expanding the archival cohort in a revision (additional FAA AM-23/6 or independent centrifuge re-analyses such as the Burton or Stoll cohorts, which exist in the historical centrifuge literature) or commit explicitly in §4.4 / §4.6 that the n = 4 rapid-onset evaluation is descriptive of the present archival cohort and not yet an operational guarantee for fighter or aerobatic flight. The corresponding sentence in the Abstract should be reworded.

### M3. CGEM's own external-validation provenance is asserted as "validated mechanistic core" without explicit accounting.

The phrasing "validated mechanistic core" recurs in the Abstract, §1, and §4.6 — but CGEM's published external validation chain is single-center FAA CAMI work (Copeland 2021 *CGEM User's Guide*; Copeland & Whinnery 2023; Copeland, Knarr & Whinnery 2000). The slow-onset bias surfaced by H6 is itself evidence that CGEM's validation envelope is bounded — and the author already quotes Copeland & Whinnery (2023) on the slow-onset relaxed-subject limitation. The present manuscript should make this provenance explicit rather than letting "validated mechanistic core" do undefined work. A PMEA reviewer with no aerospace-medicine background will read "validated" as multi-center, multi-cohort, multi-investigator validation; that is not what the CGEM literature supports.

Recommended fix: add one short paragraph either at the end of §2.1 or near the top of §4.4 acknowledging that CGEM's published external validation derives from FAA CAMI centrifuge work and that the H6 archival result is itself one such external-validation datapoint — i.e., treat the slow-onset finding as a refinement of, not an external addition to, the CGEM validation chain. This is a one-paragraph rewrite, not a structural change.

### M4. Sobol-vs-H6 onset-rate tension: model-structure gap or parameter-sensitivity gap?

The most physiologically interesting tension in the paper is unaddressed. The Sobol analysis (§3.6, Figure 5) ranks `g_peak_abs` overwhelmingly dominant on all three event-time targets (ST = 0.876–0.942) with `profile_duration_s` second (ST = 0.20–0.28) and `dgdt_max_g_per_s` (G-onset rate) a distant third (ST = 0.067–0.089). Yet the H6 archival result (§3.7) identifies *G-onset rate* as the single discriminating variable of CGEM-vs-reality discrepancy: δ̄ = +26.6 s at onset ≤ 0.5 G/s collapses to |δ̄| ≤ 1.3 s at onset ≥ 1 G/s. The two findings are not contradictory within the CGEM input space — the Sobol decomposition ranks input *parameters* of CGEM, and the H6 discrepancy is a CGEM-vs-reality discrepancy — but the manuscript should engage with the implication: the operationally relevant variable (gradual-onset muscle-tension / postural-reflex augmentation of arterial pressure) is not parameterized in the 17-dimensional input vector at all. That is a model-structure gap, not a parameter-sensitivity gap.

This matters for PMEA's readership. A physiological-measurement reviewer will read the present paper as a calibration story; the more interesting and generalizable lesson is that **a global sensitivity analysis on a surrogate of a validated ODE model can only rank features the underlying ODE actually parameterizes** — and a low Sobol ST for `dgdt_max_g_per_s` should not be misread as evidence that G-onset rate is unimportant operationally. The author should add a short paragraph (either in §3.6, §3.7 "Operational interpretation", or §4.2 "Aeromedical implications") connecting the two findings explicitly. This is genuinely the kind of methodological caution PMEA's audience will value.

### M5. Synthetic-only training validation — what does calibrated uncertainty mean before paper 3?

§3.2–3.6 measures the surrogate's ability to reproduce CGEM outputs. §3.7 is the first time the paper measures CGEM-vs-reality. The manuscript declares synthetic-only training as a limitation (§4.4) and defers external validation to papers 2 and 3, which is fair. But the §3 framing should be more transparent that *the conformal coverage figures in Tables 2 and 3, and the OOD calibration in §3.5, are statements about how well the ML layer reproduces CGEM's deterministic outputs* — they are not statements about the framework's physiological calibration. A PMEA reader who skims §3.3 ("conformal coverage within 5 pp of nominal on all five targets") will reasonably take that as a physiological-uncertainty claim; the author should foreground at the top of §3 that all §3.2–3.6 metrics are emulator-to-CGEM, and that §3.7 is the only emulator-vs-real evaluation. The current Section 3 introduction does not say this. One additional sentence at the start of §3 (or a one-sentence preamble to Table 1) would close the gap.

### M6. The §1 framing remains aerospace-centric for a PMEA audience.

§1 is a single paragraph that pivots from the methodological motivation (validated ODE models with no UQ, no OOD guard, high compute cost) to CGEM specifically by paragraph 2. For a PMEA reviewer this is acceptable but suboptimal. The PMEA readership includes researchers on patient-monitoring, ICU physiology, anesthesia, perioperative cardiovascular modeling — i.e., on validated ODE physiological models that are not aerospace. The introduction does not name any such model as a candidate downstream beneficiary of the wrapper, and consequently reads as aerospace-physiology demonstration. The author should add one paragraph in §1 (≤ 150 words) identifying 2–3 other validated ODE physiological model classes — e.g., Guyton-style cardiovascular models, 1D arterial-blood-flow benchmarks à la Boileau et al. (2015) (already cited), Pulse Physiology Engine, HumMod, or compartmental respiratory mechanics — for which the same gaps (compute cost, no UQ, no OOD guard) hold, so that the methodological contribution is visibly transferable. This goes hand-in-hand with M1.

---

## Minor concerns

### m1. Feature-space omissions worth flagging in §4.4.

The 17-dimensional input vector (9 continuous + 7 FAA-profile binaries + 1 ordinal countermeasure) abstracts pilot physiology via the `who_profile` presets. For a PMEA audience the manuscript should briefly acknowledge that this abstraction omits, at minimum: actual age, biological sex (beyond the implicit FAA preset), baseline mean arterial pressure, ventricular preload state, cerebrovascular autoregulation phenotype, fatigue / recent sleep state, and recent altitude exposure. These are not required for a methodological paper, and the FAA-profile abstraction is defensible. But a single sentence in §4.4 acknowledging that these are operationally-relevant inputs absorbed into the FAA-profile abstraction — and that paper-3 Bayesian per-pilot calibration will address them — would close a gap the physiology-trained reader will notice.

### m2. `c_bank_min` ECE upper CI bound 0.222 is genuinely high and the §3.4 hand-wave is thin.

Table 3 reports `c_bank_min` ECE = 0.108 [0.083, 0.222]. The accompanying narrative ("the ECE bootstrap distribution is right-skewed, which inflates the upper CI") is plausible but unaccompanied by evidence. The author should provide the per-bin residual table for `c_bank_min` in supplementary (or extend Supplementary Table S2 to include a per-bin breakdown), so that the reader can audit whether the right-skew is driven by a small number of high-leverage bins as claimed. As written, the §3.4 explanation feels like post-hoc reasoning; a per-bin table would make it diagnostic.

### m3. The "conceptual" stratum (n = 21, 0 event-positive rows) is operationally uninformative.

Table 2 carries multiple "0/0" cells for the conceptual stratum and several other small-n strata flagged ⚠️. The current ⚠️ flag is appropriate. Consider, in revision, either dropping the conceptual stratum from the headline Table 2 (moving it to supplementary) or merging conceptual with the lowest-event-rate stratum for headline reporting and presenting the full per-stratum breakdown in Table S2. The current Table 2 reads as more impressive than it is because the conceptual cells visually "pass" at 1.000 coverage but on n = 1 or n = 5.

### m4. The CQR rescue from 0.861 to 0.972 on n = 36 is the headline H5 result — present its uncertainty more carefully.

The CQR-vs-Mondrian comparison on `time_to_gloc_s` (Table 2, last two rows) is operationally important but rests on n = 36 event-positive test rows on the military-ACM stratum (the only stratum where the comparison is non-degenerate). The Clopper–Pearson 95 % CIs reported in §3.3 ([0.706, 0.949] for Mondrian, [0.847, 0.999] for CQR) overlap, and the author already states that CQR is reported as "operationally closer to nominal rather than statistically dominant." Good. But the CQR layer is one of the three operational refinements listed in the cover letter and is highlighted in the Abstract. The Abstract sentence "CQR raised `time_to_gloc_s` coverage from 0.861 to 0.972 (n = 36 event-positive)" should add the parenthetical "(95 % CIs overlapping)" or a comparable qualifier — the n = 36 is in the sentence but the CI overlap is not. As written, the Abstract over-claims a clean win where the CI overlap is genuine.

### m5. Reference list — Whinnery & Forster 2013 and the H6 anchor.

The H6 archival anchor cites Whinnery & Forster (2013) and the related FAA AM-23/6 reproduction; §3.7 explicitly distinguishes the n = 729 relaxed-subject subset from the larger n = 888 cohort. The reference list cites Whinnery & Forster (2013) as the primary external-validation source. Consider whether the FAA AM-23/6 reproduction referenced in §3.7 ("a related FAA AM-23/6 reproduction" — 5 Phase-A point rows) should be cited explicitly with its DOI in the reference list, given that it contributes 5 of the 13 point rows in the expanded archival registry. Right now AM-23/6 is referenced once via Copeland & Whinnery 2023; the AM-23/6 attribution is not transparent.

### m6. "Aerobatic catalogue" — the Aresti citation needs a year.

The reference "Aresti System 2019" is unconventional. The Aresti Aerocryptographic Catalog is maintained continuously by FAI/CIVA; citing "2019" is fine if that is the version retrieved, but the URL https://www.fai.org/civa/aresti-catalog will not consistently resolve to a 2019 snapshot. Add a retrieval date (per Harvard convention for evolving online resources).

### m7. Figure 1 panel order is confusing.

The Figure 1 caption labels panels (a)–(h) and pairs continuous targets in (a)–(b), then alternates classifier/regressor for the three censored targets in (c)–(h). A reader expecting the standard "classifiers first, then regressors" or "continuous first, then censored regressors only" layout has to re-orient. Either re-order panels so that (a)–(c) are the three classifiers, (d)–(e) the two continuous regressors, and (f)–(h) the three censored event-time regressors, or annotate each panel with its target name in the figure itself rather than relying solely on the caption.

---

## Specific line/section comments

- **Abstract, "Significance" sentence:** "The pattern generalises to any validated ODE physiological model" — see M1. Suggest "The same wrapper components — surrogate emulator, Mondrian / CQR conformal layers, and conformal-abstention OOD detector — are demonstrated on CGEM; cross-model validation on additional ODE physiological models is left for future work."
- **§1, paragraph 1:** Add one paragraph (≤ 150 words) identifying validated ODE physiological models outside aerospace (Guyton-style cardiovascular, 1D arterial flow per Boileau 2015, Pulse Physiology Engine, HumMod, compartmental respiratory mechanics) for which the same gaps hold — see M6.
- **§2.1:** Add one paragraph clarifying CGEM's published external-validation provenance — single-center FAA CAMI, the Copeland/Whinnery chain, and the relaxed-subject limitation already noted in Copeland & Whinnery (2023) — see M3.
- **§3 introduction (one line before §3.1):** Add a sentence clarifying that all §3.2–3.6 metrics are emulator-to-CGEM reproductions, and §3.7 is the only emulator-vs-real evaluation in the paper. See M5.
- **§3.6, end:** Add 2–3 sentences connecting the low Sobol ST for `dgdt_max_g_per_s` (G-onset rate) to the H6 finding that G-onset rate is the single discriminator of CGEM-vs-reality discrepancy. The lesson — that surrogate-driven sensitivity analyses can rank only inputs that are parameterized in the underlying ODE — is the most generalizable methodological lesson in the paper for PMEA's audience. See M4.
- **§3.7 "Operational interpretation" paragraph:** Mark the rapid-onset calibration as exploratory; n = 4 archival points from one cohort do not support an operational guarantee. See M2.
- **§4.1, last sentence:** "An error of ±1.14 s on a G-LOC time prediction can be operationally significant" — yes, and the conformal interval communicates that. The sentence could be tightened to reflect that the conformal layer is the operational deliverable here, not the point prediction.
- **§4.4, second paragraph:** Add a sentence acknowledging feature-space omissions absorbed into the `who_profile` abstraction (age, sex, baseline MAP, autoregulation phenotype, fatigue, recent altitude exposure). See m1.
- **§4.6:** Either provide a worked example of the wrapper on a second ODE physiological model class or tone the "publisher-agnostic … reference implementation for any model in that class" claim. See M1.
- **Table 1, `time_to_gloc_s` row:** The bolded **−0.055** lower CI bound is appropriate and honest. Consider adding a single footnote sentence: "Bootstrap CI lower bound below zero indicates that on this n = 36 event-positive slice, the regressor's R² is not statistically distinguishable from the mean predictor; the CQR-based conformal interval reported in Table 2 (n = 36, coverage 0.972 [0.847, 0.999]) is the operational deliverable on this target."
- **Table 2:** Consider relocating the conceptual stratum to supplementary or merging strata; the small-n cells dominate the visual impression. See m3.
- **Figure 1 caption:** Re-order panels for readability. See m7.
- **Reference list:** Add Aresti retrieval date (see m6); confirm AM-23/6 attribution (see m5).

---

## Strengths to preserve

- **Pre-registration discipline is genuine.** The OSF freeze before any test-set evaluation, the H5 / H6 amendments filed before the corresponding analyses, and the transparent reporting of the H6 partial failure (the framework's pre-registered ≥ 0.90 coverage criterion is declared not met on the Phase-A cohort) are textbook reporting practice and should be preserved through revision.
- **The CQR layer is well-justified** — the homoscedastic Mondrian baseline under-covers on `time_to_gloc_s` (0.861), the CQR layer recovers near-nominal coverage (0.972) and is reported side-by-side with the baseline it replaces, and the comparison is committed to with appropriate uncertainty (overlapping Clopper–Pearson CIs are reported).
- **The conformal-abstention OOD layer with χ² vs conformal threshold comparison (§3.5)** is methodologically clean. The 3× ratio of the conformal threshold to the parametric χ² cutoff is exactly the kind of distribution-free finding that justifies the abstention layer's design — preserve this passage.
- **Reproducibility deliverables** are appropriate for a methods paper: OSF lock, Zenodo dataset DOI placeholder, Docker image, full test suite (80 tests, all passing per §4.5), datasheet (Appendix S1), TRIPOD-AI checklist (Appendix S2), model cards (S3, S4). The author has done the engineering work that PMEA expects.
- **Honest declaration of negative findings.** The −0.055 lower CI bound on `time_to_gloc_s` R², the conceptual-stratum 0/0 cells, the LOGO AUROC values below 0.5 on the conceptual fold, and the H6 partial failure are all reported transparently. This is a strength.
- **The Whinnery & Forster (2013) attribution and the explicit distinction between the n = 729 relaxed-subject parent and the n = 888 total cohort** (§3.7, §4.4) shows careful primary-source handling — preserve.

---

## Recommendation rationale

The methodological work is well-executed and well-reported; the pre-registration is genuine; the engineering deliverables are appropriate; the H6 partial-failure transparency is admirable. The paper sits within PMEA's scope clause on "physiological modelling, simulation, model identification, and control" and "physics- and model-based machine learning." If this were submitted as an aerospace-medicine methods demonstration to *Aerospace Medicine and Human Performance* I would recommend Minor Revisions on the technical issues only.

For PMEA, however, the generalization claim (M1) is the *paper-level* claim — that the wrapper is a reference implementation for any validated ODE physiological model — and it is not earned by a single demonstration. Coupled with the n = 4 rapid-onset operational-calibration claim (M2), the implicit treatment of CGEM as a multi-center validated core (M3), the unaddressed Sobol-vs-H6 onset-rate tension (M4), the §3 framing that conflates emulator-to-CGEM calibration with physiological calibration (M5), and the aerospace-centric §1 (M6), the manuscript currently requires substantive (though tractable) revisions to meet PMEA's bar.

None of the major issues require new experiments; M1 can be satisfied with a worked conceptual argument and tempered language, M2 with explicit "exploratory" labeling, M3 / M4 / M5 / M6 with targeted paragraph additions and reframing. A round of major revisions is the right call.

**Recommendation: Major Revisions.**

---

## Suggested response-letter preparation for the authors

When responding, the author should structure the response letter so that each of the six major concerns receives a clearly labeled section with three components: (i) the concern restated, (ii) the change made (with manuscript line numbers in the revised version), and (iii) the reasoning. The minor concerns can be grouped under a single "Minor revisions" heading with brief responses.

Specific suggestions for high-impact responses:

- **M1 generalization claim.** The author should commit to one of two paths: either (a) add a one-page conceptual worked example in §4.6 sketching how the wrapper components map to a non-aerospace ODE physiological model (Pulse Physiology Engine and 1D arterial flow per Boileau 2015 are the two most natural candidates because the author already cites Boileau), or (b) tone the claim throughout. Option (a) is the stronger response and would substantially elevate the paper for PMEA's audience.
- **M2 rapid-onset operational claim.** Mark exploratory in §3.7, §4.1, and the Abstract; commit in §4.6 to expanding the archival registry in a future paper.
- **M3 CGEM provenance.** One paragraph in §2.1 (preferred) or §4.4 acknowledging the single-center FAA CAMI lineage. Cite Copeland 2021 (DOT/FAA/AM-23/5), Copeland & Whinnery 2023 (DOT/FAA/AM-23/6), and Copeland, Knarr & Whinnery 2000 explicitly.
- **M4 Sobol-vs-H6 tension.** This is the response with the highest payoff for PMEA's audience. A short paragraph (~150 words) explaining that a surrogate-driven sensitivity analysis ranks only inputs parameterized in the underlying ODE, and that the H6 slow-onset bias is evidence of a model-structure gap (missing muscle-tension / postural-reflex term) rather than a parameter-sensitivity gap, is a substantive methodological contribution that the present paper essentially leaves on the table.
- **M5 §3 framing.** Two sentences at the top of §3 distinguishing emulator-to-CGEM (§3.2–3.6) from emulator-vs-real (§3.7). Cheap to add and changes the reader's interpretation of all the §3 numbers.
- **M6 §1 broadening.** One paragraph in §1 identifying 2–3 non-aerospace validated ODE physiological model classes as candidate downstream beneficiaries of the wrapper. This pairs with M1.

If the author also wishes to address an *open physiological question for the response letter* that this reviewer will follow up on: **is the slow-onset muscle-tension / postural-reflex term — the variable that H6 identifies as the dominant discriminator of CGEM-vs-reality discrepancy — parameterizable within the CGEM ODE structure at all, or is it fundamentally a model-structure extension (a new state variable for skeletal-muscle pump augmentation of arterial pressure during gradual G onset)?** The author already gestures at this in §3.7 (citing Copeland & Whinnery 2023 on the relaxed-subject assumption); the response letter and revised §4.4 should engage explicitly with whether paper 3 plans to add the term as a CGEM modification or as a separate δ(x) correction layer. This is the methodological question that determines whether the present wrapper architecture remains additive in the next paper.

---

*End of report.*
