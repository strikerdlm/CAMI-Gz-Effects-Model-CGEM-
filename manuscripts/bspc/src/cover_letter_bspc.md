# Cover letter — *Biomedical Signal Processing and Control* (BSPC)

[Date at submission]

Professor Panicos A. Kyriacou
Editor-in-Chief, *Biomedical Signal Processing and Control*
School of Science and Technology, City University of London
Northampton Square, London EC1V 0HB, United Kingdom

*Submitted via Editorial Manager (https://submit.elsevier.com/BSPC)*

---

Dear Professor Kyriacou,

I am pleased to submit for your consideration a Full Paper entitled **"Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"** by Diego Malpica, MD (sole author).

**Why BSPC.** This manuscript fits BSPC's stated scope along the *biomedical signal processing* axis. The system under study, the FAA Civil Aerospace Medical Institute's CGEM, is a validated Fortran ODE model that emits cerebrovascular and visual biosignals — cerebral blood flow (`c_bank`), head-level arterial pressure (HLAP), retinal oxygen delivery, and visual-function indices (`f_vis`, `f_bo`) — under sustained +Gz load. The contribution of the paper is an additive machine-learning layer wrapped around that mechanistic biosignal generator: a fast emulator with distribution-free conformal coverage on every biosignal channel and event-time scalar, plus an out-of-distribution (OOD) abstention guard on the operational input envelope. Both the methodology and the working program (open Python package, FastAPI signal-prediction service, Docker image) are intended for direct deployment in biomedical-signal monitoring and advisory contexts. The methodological neighbourhood — surrogate emulation of validated biomedical models with calibrated uncertainty — is well-represented in recent BSPC issues.

**What is known and what this study adds.** Validated mechanistic biosignal generators are computationally expensive, supply no calibrated uncertainty on the signals they emit, and accept out-of-distribution operational inputs without warning. Portela, Banga and Matabuena (2025, *PLOS Computational Biology*) recently demonstrated the surrogate + conformal + OOD wrapping pattern on canonical biological dynamical systems. The present work extends that pattern into a specific regulatory aerospace-physiology setting and adds three operational refinements: (i) per-stratum (Mondrian) conformal calibration over operationally meaningful maneuver categories — rather than the more common pooled calibration — with under-coverage at low-event-rate strata declared transparently; (ii) heteroscedastic Conformalized Quantile Regression (Romano, Patterson and Candès 2019) for the long-tailed event-time target, restoring `time_to_gloc_s` empirical coverage from 0.861 to 0.972 on n = 36 event-positive test rows (pre-registered as OSF amendment H5, 2026-05-06, before any test-set evaluation under the new layer); and (iii) a robust-Mahalanobis OOD detector calibrated by distribution-free conformal abstention over a 17-dimensional mixed numeric/categorical input space, providing a finite-sample operational in-envelope guarantee that does not assume Gaussianity of the score.

**Key empirical anchors** on the OSF-pre-registered held-out test split: conformal OOD calibration of 0.953 versus the nominal 0.95; conformal coverage within 5 percentage points of nominal 95 % on all five surrogate targets once the heteroscedastic CQR layer replaces the homoscedastic Mondrian baseline on `time_to_gloc_s`; classifier AUROC ≥ 0.996 (expected calibration error ≤ 0.014) across the three censored event targets; regressor R² = 0.82–0.90 on event-positive rows of censored targets and 0.94–1.00 on continuous targets; surrogate inference at ~50 µs per row versus ~9 ms for direct Fortran subprocess invocation. External validation against the archival centrifuge cohort of Whinnery and Forster (2013) — pre-registered as H6 — establishes a slow-onset bias δ̄ = +26.6 s [95 % CI +6.3, +52.1] at onset ≤ 0.5 G/s, with the surrogate in-bracket on every record at onset ≥ 1 G/s (the operationally relevant fighter and aerobatic regime).

**Generalisability and biosignal-control relevance.** The wrapping pattern (surrogate + conformal + OOD) is publisher-agnostic and is intended as a reference implementation for any validated ODE biomedical-signal generator. The accompanying FastAPI service exposes the wrapped signal-generation pipeline as an HTTP endpoint suitable for closed-loop monitoring and advisory prototypes; the Docker image reproduces the full validation protocol from `docker run`.

---

**Declarations.**

- **Originality.** This manuscript reports original work that has not been published or accepted elsewhere and is not under concurrent consideration by another journal. It was previously submitted to the *International Journal for Numerical Methods in Biomedical Engineering* (manuscript 5977782), where it was desk-rejected on 2026-05-17 on scope grounds (IJNMBE updated Aims and Scope no longer accepts purely-ML papers on biomedical problems); the IJNMBE record is archived at `manuscripts/_archive/ijnmbe/REJECTION.md` in the project repository.
- **Conflict of interest.** The author declares no conflicts of interest.
- **Funding.** This research received no external funding. All work was self-funded.
- **Ethical approval.** Not applicable — the present study uses synthetic data only. No human or animal subjects were studied.
- **Data and code availability.** Source code (MIT licence) is at `https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`; the synthetic dataset `cgem_synthetic_v1.parquet` is archived under the project's Zenodo deposit (DOI assigned at acceptance); a reproducibility Docker image is on GitHub Container Registry (GHCR). The OSF pre-registration (including the 2026-05-06 amendment for H5/H6) is at the project's OSF page.
- **Software and program.** The CGEM-extension Python package (`cgem_ext`), FastAPI service, and Docker image are released as production-runnable artifacts under MIT licence. A reference deployment is exercisable via `docker run ghcr.io/strikerdlm/cami-gz-effects-model-cgem-:v0.1.0`.
- **Suggested reviewers.** Five candidates with verified institutional emails are listed in `suggested_reviewers_bspc.md` (uploaded as portal entries, per BSPC submission convention). None has co-authored with the corresponding author in the past three years; none shares an institution with the author; none is on the current BSPC editorial board.
- **Preprint.** No preprint is currently posted. If posted on arXiv prior to portal entry, this declaration will be updated to cite the arXiv URL under a non-exclusive licence.

I confirm that this manuscript has not been published previously and is not under consideration at another journal. Thank you and the editorial board for your consideration.

Sincerely,

Diego Malpica, MD
Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC),
Bogotá, Colombia.
ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)
[dlmalpica@yahoo.com](mailto:dlmalpica@yahoo.com)
