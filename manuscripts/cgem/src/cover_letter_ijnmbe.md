# Cover letter — *International Journal for Numerical Methods in Biomedical Engineering* (IJNMBE)

[Date: TBD at submission]

Professor Perumal Nithiarasu
Editor-in-Chief, *International Journal for Numerical Methods in Biomedical Engineering*
College of Engineering, Swansea University
Swansea, Wales, United Kingdom

*Submitted via the Wiley Authors portal (CNM)*

---

Dear Professor Nithiarasu,

I am pleased to submit for your consideration a Research Paper entitled
**"Conformal machine-learning emulation and out-of-distribution detection for
the FAA CAMI G-Effects mechanistic model of acceleration physiology"** by
Diego Malpica, MD (sole author).

**Why IJNMBE.** The manuscript falls within three of IJNMBE's verified scope
clauses simultaneously. (1) The validated core is a *differential-equation-
based biomedical model* — the FAA Civil Aerospace Medical Institute's CGEM, a
Fortran-implemented system of ordinary differential equations governing
cardiovascular and cerebrovascular response under sustained +Gz load. (2) The
extension layer is an *artificial-intelligence wrapper* — explicitly within
scope per the journal's "special cases that may not involve differential
equations such as image processing, meshing and artificial intelligence are
within the scope" clause. (3) The application is *broadly linked to the
wellbeing of the human body* — G-induced loss of consciousness remains an
established occupational risk in fighter, aerobatic, and high-performance
fixed-wing aviation, and the framework is delivered as an open Python
package, FastAPI service, and Docker image suitable for downstream operational
research. The methodological neighbourhood — surrogate emulation of validated
biomedical ODE solvers with calibrated uncertainty — is well-represented in
recent IJNMBE issues (e.g., inverse uncertainty quantification of mechanical
arterial-tissue models with ML surrogates; benchmark studies of one-dimensional
arterial blood-flow numerical schemes).

**Non-standard contribution — explicit pre-emption of the scope filter.**
The journal's guidance reminds authors that "application of a standard
numerical procedure to a standard problem is not within the scope". The
contribution of this paper is *not* "we applied XGBoost to a Fortran model".
It is the **combined methodological stack**: (i) a two-stage classifier-then-
regressor pattern for right-censored event-time targets, wrapped by a
*heteroscedastic* maneuver-category-stratified Conformalized Quantile
Regression layer (Romano, Patterson & Candès 2019) that restores empirical
coverage on the long-tailed `time_to_gloc_s` target from 0.861 to 0.972 on
the OSF-pre-registered held-out test split (pre-registered as OSF amendment
2026-05-06 hypothesis H5); (ii) Mondrian split-conformal prediction intervals
stratified *by maneuver category* (rather than the more common pooled
calibration), so that conformal coverage is preserved within operational
sub-populations of inputs, with under-coverage at low-event-rate strata
declared transparently rather than masked by global pooling; and
(iii) a robust-Mahalanobis distance detector calibrated by *distribution-free
conformal abstention* over a 17-dimensional mixed numeric/categorical input
space, providing an operationally meaningful in-envelope guarantee that does
not assume Gaussianity of the score. To my knowledge no prior work combines
these three elements over a validated regulatory ODE physiological model;
the CQR application to a two-stage right-censored aerospace-medicine target
is, specifically, novel.

**Key empirical anchors** on the pre-registered held-out test split: conformal
OOD calibration of 0.953 versus the nominal 0.95 (within 0.3 pp), with the
conformal threshold ~3× the parametric χ²(17, 0.95) cutoff; conformal coverage
within 5 percentage points of nominal 95 % on **all** 5 surrogate targets
once the heteroscedastic CQR layer replaces the homoscedastic Mondrian
baseline on `time_to_gloc_s` (the CQR layer narrows distance-to-nominal from
8.9 pp to 2.2 pp on the n = 36 event-positive test slice; the per-stratum
Clopper–Pearson exact 95 % binomial CIs on the two layers overlap at this
sample size, so the manuscript reports the CQR result as operationally
closer to nominal rather than statistically dominant — the n = 36 anchor is
the primary practical, not statistical, claim of H5); XGBoost regressor
R² = 0.82–0.90 on event-positive rows of censored targets (with the 95 %
bootstrap CI on `time_to_gloc_s` spanning [−0.055, 0.951], the regime in
which the CQR layer was activated) and 0.94–1.00 on continuous targets;
classifier AUROC ≥ 0.996 across the three event targets, presented as a
sanity check on a deterministic data-generating process rather than a
primary claim. The surrogate evaluates in ~50 µs per row versus ~9 ms for
direct CGEM subprocess invocation, which makes the 20,480-evaluation
Saltelli Sobol sweep in §3.6 tractable inside a manuscript-preparation
cycle; this latency figure is reported as a deployment characteristic, not
as a methodological contribution. The validation protocol was pre-registered
on the Open Science Framework before any test-set evaluation; the CQR layer
and the archival-validation arm were added under a 2026-05-06 OSF amendment
(H5, H6) before any test-set evaluation under those new hypotheses. The H6
archival evaluation against the Phase A cohort of Whinnery & Forster (2013)
[5] does **not** meet its pre-registered ≥ 0.90 coverage criterion: the
mean discrepancy δ̄ = +26.6 s [95 % CI +6.3, +52.1] is statistically
distinguishable from zero. The discrepancy concentrates at onset ≤ 0.5 G/s
and the surrogate is in-bracket on every record at onset ≥ 1 G/s — the
operationally relevant fighter and aerobatic regime. We therefore present
H6 as a partial external-validation failure with a well-defined operational
scope, not as a clean pass.

**Boundary of the present paper.** The framework is validated against CGEM
itself as ground truth. External validation against archival centrifuge
data and against own-centrifuge subjects is the subject of separate work
and is not claimed in this manuscript.

---

**Declarations** (Wiley Free Format title-page mandatory list):

- **Originality.** This manuscript reports original work that has not been
  published or accepted elsewhere and is not under concurrent consideration
  by another journal.
- **Conflict of interest.** The author declares no conflicts of interest.
- **Funding.** This research received no external funding. All work was
  self-funded.
- **Ethics approval.** n/a — synthetic data only. No human or animal
  subjects were studied. Companion paper 3 (in preparation) reports own-
  centrifuge work under separate IRB approval at the relevant site.
- **Patient consent.** n/a — no human subjects.
- **Permission to reproduce third-party material.** n/a — all figures,
  tables, and code are original to this work; no third-party material is
  reproduced.
- **Clinical-trial registration.** n/a — methodological / synthetic-data
  study; no clinical trial.
- **Data and code availability.** Source code (MIT licence) is at
  `https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`; the synthetic
  dataset `cgem_synthetic_v1.parquet` is archived on Zenodo (DOI: TBD at
  submission); a reproducibility Docker image is on GitHub Container
  Registry (GHCR); the OSF pre-registration is at: TBD at submission. Data
  and code will be uploaded to the portal as **Data Files** (not as
  Supporting Information) and the dataset is cited formally in the
  reference list per the Joint Declaration of Data Citation Principles.
- **Preprint.** TBD at submission — if a preprint is posted on arXiv prior
  to portal entry, it will be done under a non-exclusive licence per
  IJNMBE's preprint policy, and this declaration will be updated to cite
  the arXiv URL.
- **Suggested reviewers.** Five candidates are listed in the accompanying
  file `suggested_reviewers_ijnmbe.md`. None has co-authored with the
  corresponding author in the past three years; none shares an institution
  with the author; and the slate is verified against the IJNMBE editorial
  board.

The mandatory **Novelty File** (`novelty_file_ijnmbe.md`, ≤ 100 words,
itemised) and the mandatory **Graphical Abstract / Graphical Table of
Contents** (`graphical_abstract_ijnmbe.md` plus the rendered TOC graphic) are
provided as separate uploads per the IJNMBE Author Guidelines.

I confirm that this manuscript has not been published previously and is not
under consideration at another journal. Thank you and the editorial board for
your consideration.

Sincerely,

Diego Malpica, MD
Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC),
Bogotá, Colombia.
ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)
[dlmalpica@yahoo.com](mailto:dlmalpica@yahoo.com)
