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

1. **Heteroscedastic Conformalized Quantile Regression for a two-stage,
   right-censored event-time target on a regulatory ODE model.** The
   two-stage classifier-then-regressor pattern (greyout, blackout,
   G-LOC) is wrapped by a maneuver-category-stratified CQR layer that
   restores empirical coverage on the long-tailed `time_to_gloc_s` target
   from 0.861 (homoscedastic baseline) to 0.972 (within 2.2 pp of nominal
   0.95) on the OSF-pre-registered held-out test split (H5).
2. **Distribution-free conformal abstention on a robust-Mahalanobis OOD
   detector over a 17-dimensional mixed numeric/categorical feature space**
   — operational in-envelope guarantee without Gaussianity, calibrated to
   within 0.3 pp of nominal on the held-out split.
3. **Maneuver-category-stratified conformal coverage** with under-coverage
   at low-event-rate strata declared transparently rather than masked by
   global pooling — applied to a regulatory ODE physiological model whose
   censoring structure has not previously been emulated by a calibrated ML
   surrogate.

---

**Self-audit:**

- Word count of items 1–3 (itemised list only, excluding title and headers):
  **148 words.** **WARN** — exceeds the IJNMBE 100-word cap. Trim before
  portal entry; current draft prioritises precision of the H5 anchor
  numbers over brevity, which is appropriate for an internal review
  draft but must be tightened pre-submission. Suggested trim path:
  drop the parenthetical (0.861 → 0.972) figures from item 1 and the
  "0.3 pp" annotation in item 2; both numbers appear in the abstract and
  do not need duplication here.
- Sentence count: 3 across three items.
- Textual overlap with the manuscript abstract: each itemised contribution
  uses different phrasing from the abstract — the abstract describes
  *what the paper contains*; this file describes *what the paper adds
  to the field*. No phrase ≥ 6 words is shared with the abstract.
- Lead with the non-standard methodological contribution (CQR for a
  two-stage censored aerospace-medicine target on a regulatory ODE) —
  PASS the "no standard procedure" filter.
- Earlier drafts included an "additive-wrapper preservation principle"
  (a software-engineering constraint, not a scientific contribution) and
  a generalisability assertion to other validated ODE solvers (hand-waving
  without empirical support). Both removed; not reinstated.

**Compliance with IJNMBE rule "no standard procedure on a standard problem":**
The Novelty File leads with **CQR applied to a two-stage right-censored
event-time target on a regulatory ODE physiological model** — to our
knowledge not previously published. The combined three-element stack over
the FAA-validated CGEM is the first ML-surrogate / conformal-UQ wrapper
of any FAA CAMI regulatory model.
