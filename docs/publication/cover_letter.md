# Cover letter — *Computer Methods and Programs in Biomedicine*

[Date: TBD at submission]

Filippo Molinari, PhD
Editor-in-Chief, *Computer Methods and Programs in Biomedicine*
Polytechnic of Turin, Department of Electronics and Telecommunications
Turin, Italy

*Submitted via Editorial Manager*

---

Dear Prof. Molinari,

I am pleased to submit the manuscript **"Conformal ML emulation and OOD detection
for the FAA CGEM G-LOC model"** for consideration as a Full Length Article in
*Computer Methods and Programs in Biomedicine*.

**Why CMPB.** The manuscript addresses a class of problem that sits squarely in
CMPB's scope: a validated mechanistic model embedded in a regulatory framework
is wrapped with a formal computing layer — without modifying the validated core —
to gain emulation speed, calibrated uncertainty, and input-envelope safety. The
specific model is the FAA's Civil Aerospace Medical Institute G-Effects Model
(CGEM), a Fortran-based ODE simulator of cardiovascular and cerebrovascular
response under +Gz acceleration stress. The ML extension layer comprises:
(1) per-target XGBoost surrogate emulators (~180× faster than the Fortran
subprocess), (2) Mondrian split-conformal prediction intervals (α = 0.05)
stratified by maneuver category, (3) a robust Mahalanobis out-of-distribution
detector with distribution-free conformal abstention, and (4) global Sobol
and Morris sensitivity analysis driven by the emulator. The framework is
delivered as an open Python package (`cgem_ext`, MIT licence), a FastAPI service
with a React/TypeScript frontend, and a Docker image — assets that align with
CMPB's stated aim to stimulate research into application software design.

**Key empirical anchors** on the pre-registered held-out test split: classifier
AUROC ≥ 0.996 on all three right-censored event targets; regressor R² 0.82–0.90
on event-positive rows and 0.94–1.00 on continuous targets; Mondrian conformal
empirical coverage within 4.6 pp of nominal 95 % on 4 of 5 targets; OOD
conformal calibration within 0.3 pp of nominal 95 %. The surrogate enables a
full 20,480-evaluation Sobol sensitivity analysis in ~38 s (vs. days via direct
subprocess). The validation protocol was pre-registered on OSF before any
test-set evaluation.

**Generalizability.** Although the application is aerospace physiology, the
surrogate + conformal + OOD pattern generalises immediately to any validated
ODE physiological model — cardiovascular haemodynamics simulators, pharmacokinetic
compartment models, thermoregulatory or respiratory system models — that must be
made computationally tractable and uncertainty-aware for operational research use.
Paper 2 (in preparation) will quantify the discrepancy between the CGEM-emulator
stack and published centrifuge datasets; paper 3 will validate against own-centrifuge
subjects. All three papers are pre-registered on OSF.

**Declarations:**

- **Originality.** The manuscript reports original work not published or accepted
  elsewhere and not under concurrent consideration by another journal.
- **AI disclosure.** Generative AI tools were used solely for code scaffolding,
  reference formatting, and editorial review of drafts. No AI tool generated
  scientific claims, study design, analyses, or interpretation. All scientific
  content was authored, reviewed, and approved by the human author. This is
  disclosed in §2.8.
- **Conflicts of interest.** None declared.
- **Funding.** No external funding. Self-funded research.
- **Data and code availability.** Full code (MIT licence) at
  `github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`; dataset at Zenodo
  (DOI: TBD at submission); Docker image at GHCR.
- **Suggested reviewers.** Five candidates are listed in the accompanying file
  `suggested_reviewers.md`. None has co-authored work with the corresponding
  author in the past three years; none shares an institution with the author.

I look forward to the editorial decision.

Sincerely,

Diego Malpica, MD
Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force, Bogotá, Colombia.
ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)
[dlmalpica@yahoo.com](mailto:dlmalpica@yahoo.com)
