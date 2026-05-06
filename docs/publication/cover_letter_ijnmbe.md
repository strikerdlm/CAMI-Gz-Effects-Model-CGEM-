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
regressor pattern for right-censored event-time targets that handles the
intrinsic censoring structure of G-LOC outcomes; (ii) Mondrian split-conformal
prediction intervals stratified *by maneuver category* (rather than the more
common pooled calibration), so that conformal coverage is preserved within
operational sub-populations of inputs, with under-coverage at low-event-rate
strata declared transparently rather than masked by global pooling; and
(iii) a robust-Mahalanobis distance detector calibrated by *distribution-free
conformal abstention* over a 17-dimensional mixed numeric/categorical input
space, providing an operationally meaningful in-envelope guarantee that does
not assume Gaussianity of the score. To my knowledge no prior work combines
these three elements over a validated regulatory ODE physiological model.

**Key empirical anchors** on the pre-registered held-out test split: conformal
OOD calibration of 0.953 versus the nominal 0.95 (within 0.3 pp), with the
conformal threshold ~3× the parametric χ²(17, 0.95) cutoff; Mondrian
conformal empirical coverage within 4.6 percentage points of nominal 95 % on
4 of 5 surrogate targets, with the under-coverage on time-to-G-LOC declared
transparently and motivating a heteroscedastic / quantile-regression conformal
extension flagged in §4.4; XGBoost regressor R² = 0.82–0.90 on event-positive
rows of censored targets and 0.94–1.00 on continuous targets; classifier
AUROC ≥ 0.996 across the three event targets, presented as a sanity check
on a deterministic data-generating process rather than a primary claim. The
surrogate evaluates in ~50 µs per row versus ~9 ms for direct CGEM
subprocess invocation, which makes the 20,480-evaluation Saltelli Sobol
sweep in §3.6 tractable inside a manuscript-preparation cycle. The
validation protocol was pre-registered on the Open Science Framework before
any test-set evaluation.

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
- **AI disclosure.** Generative AI tools (Anthropic Claude and OpenAI
  GPT-class models) were used only for code scaffolding, draft
  formatting, reference cross-checking, and editorial review of drafts.
  No AI tool was used to design the study, generate scientific claims,
  perform analyses, interpret results, or compose original scientific
  arguments. All scientific content was authored, reviewed, and approved
  by the human author. AI use is also disclosed in §"Declaration of
  generative AI use" of the manuscript.
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
