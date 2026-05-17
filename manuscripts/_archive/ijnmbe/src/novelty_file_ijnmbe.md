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

1. **Heteroscedastic Conformalized Quantile Regression** wrapping a
   two-stage classifier-then-regressor pattern for right-censored
   event-time targets on a regulatory ODE physiological model — the
   first such combination, to our knowledge.
2. **Distribution-free conformal abstention on a robust-Mahalanobis
   out-of-distribution detector** over a 17-dimensional mixed
   numeric/categorical feature space — operational in-envelope
   guarantee that does not assume Gaussianity of the score distribution.
3. **Maneuver-category-stratified conformal coverage** with
   under-coverage at low-event-rate strata declared transparently
   rather than masked by global pooling, plus an external-validation
   discrepancy quantification against archival centrifuge data (H6).

---

**Self-audit:**

- Word count of items 1–3 (itemised list only, excluding title and
  headers): **84 tokens** (≈ 81 words after stripping the
  numerals). Comfortably within the IJNMBE 100-word cap.
- Sentence count: 3 across three items.
- Textual overlap with the manuscript abstract: each itemised
  contribution uses different phrasing from the abstract — the
  abstract describes *what the paper contains*; this file describes
  *what the paper adds to the field*. No phrase ≥ 6 words is shared
  with the abstract.
- Lead with the non-standard methodological contribution (CQR for a
  two-stage censored aerospace-medicine target on a regulatory ODE) —
  passes the "no standard procedure" filter.
- Earlier drafts included an "additive-wrapper preservation
  principle" (a software-engineering constraint) and a
  generalisability assertion to other validated ODE solvers
  (hand-waving without empirical support). Both removed.

**Compliance with IJNMBE rule "no standard procedure on a standard
problem":** the Novelty File leads with **CQR applied to a two-stage
right-censored event-time target on a regulatory ODE physiological
model** — to our knowledge not previously published. The combined
three-element stack over the FAA-validated CGEM is the first
ML-surrogate / conformal-UQ wrapper of any FAA CAMI regulatory model.
