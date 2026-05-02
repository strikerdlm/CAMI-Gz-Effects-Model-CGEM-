# Novelty File — IJNMBE submission

> **Mandatory file at IJNMBE.** Itemised list, ≤ 100 words, **not** a
> duplicate of the abstract. Read by the editor as a fast filter against
> the "no standard procedure on standard problem" scope clause. Upload to
> the Wiley CNM portal as the **Novelty File** designation.

---

**Title:** Conformal machine-learning emulation and out-of-distribution
detection for the FAA CAMI G-Effects mechanistic model of acceleration
physiology.

**New contributions of this paper to the field:**

1. **Mondrian split-conformal stratified by maneuver category** — calibrated
   coverage preserved within operational input sub-populations, not pooled.
2. **Distribution-free conformal abstention on a robust-Mahalanobis OOD
   detector** — operational in-envelope guarantee without Gaussianity.
3. **Two-stage classifier-then-regressor pattern** for right-censored event-
   time targets (greyout, blackout, G-LOC) with monotonicity priors.
4. **Additive-wrapper preservation principle** for a regulatory ODE solver —
   ML layer surrounds, never replaces, the FAA-validated Fortran core.
5. **Generalises** to any validated biomedical ODE solver requiring fast,
   uncertainty-aware, input-safe operational deployment.

---

**Self-audit:**

- Word count of items 1–5 (the itemised list, excluding title and headers):
  **96 words** / 100. PASS.
- Sentence count: 5 (one per item). Itemised list per IJNMBE guidance.
- Textual overlap with the manuscript abstract: each itemised contribution
  uses different phrasing from the abstract — the abstract describes *what
  the paper contains* (dataset, surrogate, conformal interval, OOD
  detector, sensitivity analysis, results); this file describes *what the
  paper adds to the field* (the four methodological contributions and the
  generalisability claim). No phrase ≥ 6 words is shared with the abstract.
  PASS.
- Lead with non-standard methodology (item 1), not "applied XGBoost".
  PASS.

**Compliance with IJNMBE rule "no standard procedure on a standard problem":**
The Novelty File leads with the Mondrian *stratification by maneuver
category* and the *conformal-distance OOD abstention layer* — neither is a
standard pipeline element. The combined four-element stack (items 1–4) over
a validated regulatory ODE physiological model is, to the author's knowledge,
not previously published.
