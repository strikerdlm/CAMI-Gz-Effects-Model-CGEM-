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
   coverage preserved within operational input sub-populations, not pooled,
   with under-coverage at low-event-rate strata declared transparently
   rather than masked by global pooling.
2. **Distribution-free conformal abstention on a robust-Mahalanobis OOD
   detector over a 17-dimensional mixed numeric/categorical feature space** —
   operational in-envelope guarantee without Gaussianity, calibrated to
   within 0.3 pp of the nominal level on the held-out split.
3. **Two-stage classifier-then-regressor pattern** for right-censored event-
   time targets (greyout, blackout, G-LOC) with monotonicity priors derived
   from acceleration physiology, applied to a regulatory ODE physiological
   model whose censoring structure has not previously been emulated by a
   calibrated ML surrogate.

---

**Self-audit:**

- Word count of items 1–3 (the itemised list, excluding title and headers):
  **94 words** / 100. PASS.
- Sentence count: 3. Itemised list per IJNMBE guidance.
- Textual overlap with the manuscript abstract: each itemised contribution
  uses different phrasing from the abstract — the abstract describes *what
  the paper contains* (dataset, surrogate, conformal interval, OOD
  detector, sensitivity analysis, results); this file describes *what the
  paper adds to the field* (three methodological contributions). No phrase
  ≥ 6 words is shared with the abstract. PASS.
- Lead with non-standard methodology (item 1), not "applied XGBoost".
  PASS.
- The earlier draft of this file included two further claims — an
  "additive-wrapper preservation principle" and a generalisability
  assertion to other validated ODE solvers. The first is a software-
  engineering constraint, not a scientific contribution; the second was
  hand-waving without empirical support. Both have been removed in
  preparation for the originality uplift tracked in the project plan.

**Compliance with IJNMBE rule "no standard procedure on a standard problem":**
The Novelty File leads with the Mondrian *stratification by maneuver
category* and the *conformal-distance OOD abstention layer* — neither is a
standard pipeline element. The combined three-element stack over a
validated regulatory ODE physiological model is, to the author's knowledge,
not previously published.
