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
operational sub-populations of inputs; (iii) a robust-Mahalanobis distance
detector calibrated by *distribution-free conformal abstention*, providing an
operationally meaningful in-envelope guarantee that does not assume Gaussianity
of the score; and (iv) the *additive-wrapper* preservation principle — the
ML stack does not replace the FAA-validated Fortran core, it surrounds it,
preserving the regulatory validation chain. To my knowledge no prior work
combines all four elements over a validated regulatory ODE physiological
model. The pattern generalises immediately to other validated biomedical ODE
solvers — cardiovascular haemodynamics, pharmacokinetic compartment models,
thermoregulatory and respiratory simulators — that must be made
computationally tractable, uncertainty-aware, and input-safe for operational
research use.

**Key empirical anchors** on the pre-registered held-out test split: classifier
AUROC ≥ 0.996 on all three right-censored event targets; XGBoost regressor
R² = 0.82–0.90 on event-positive rows of censored targets and 0.94–1.00 on
continuous targets; Mondrian conformal empirical coverage within 4.6 percentage
points of nominal 95 % on 4 of 5 targets, with the under-coverage on time-to-
G-LOC declared transparently and motivating a heteroscedastic conformal
extension flagged in §4.4; conformal OOD calibration within 0.3 pp of nominal
95 %; ~180× emulator speedup over direct Fortran subprocess invocation,
enabling a 20,480-evaluation Saltelli Sobol study in ~38 s rather than the
days that would be required of direct CGEM. The validation protocol was
pre-registered on the Open Science Framework before any test-set evaluation.

**Generalisability.** Although the worked example is aerospace physiology,
the methodological pattern (additive surrogate + Mondrian conformal +
distribution-free OOD + global sensitivity) applies to any validated ODE
physiological model. Companion papers 2 and 3 (in preparation, also
pre-registered on OSF) will quantify the discrepancy term δ(x) = real(x) −
CGEM(x) against published centrifuge data and validate the full pipeline
against own-centrifuge subjects (CACOM-1 protocol, Bogotá, 2,600 m altitude).

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
