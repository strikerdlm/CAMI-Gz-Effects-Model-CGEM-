# Cover letter — *Aerospace Medicine and Human Performance*

[Date: TBD at submission]

David G. Newman, AM, MBBS, DAvMed, MBA, PhD
Editor-in-Chief, *Aerospace Medicine and Human Performance*
Aerospace Medical Association
[AMHPJournal@asma.org](mailto:AMHPJournal@asma.org)

---

Dear Dr. Newman,

I am pleased to submit the enclosed manuscript, **"Conformal ML
emulation and OOD detection for the FAA CGEM G-LOC model,"** for
consideration as a Research Article in *Aerospace Medicine and Human
Performance*.

The work presents an additive machine-learning extension to the FAA
Civil Aerospace Medical Institute G-Effects Model (CGEM). The Fortran
core that operationally defines CGEM is preserved byte-for-byte; the
extension wraps it with (1) a fast XGBoost surrogate emulator that
runs ~180× faster than the subprocess, (2) Mondrian split-conformal
prediction intervals stratified by maneuver category, (3) a robust
Mahalanobis out-of-distribution detector with distribution-free
conformal abstention, and (4) global sensitivity analysis (Sobol +
Morris) driven by the surrogate. Together these capabilities address
three operational gaps in CGEM: computational cost, lack of calibrated
uncertainty, and acceptance of out-of-envelope inputs without warning.

Empirical anchors on the held-out test split: classifier AUROC ≥ 0.996
on all three censored time targets; regressor R² 0.82–0.90 on
event-positive rows and 0.94–1.00 on continuous targets; conformal
coverage within 4.6 percentage points of nominal 95 % on 4 of 5
targets; OOD calibration within 0.3 percentage points of nominal 95 %.
The framework is suitable for parametric mission planning, real-time
G-LOC risk advisory prototyping, and as the computational backbone for
future Bayesian per-pilot calibration studies.

I attest to the following points required by the AMHP Instructions for
Authors (February 2026 revision):

1. **Originality.** The manuscript reports original work that has not
   been published or accepted for publication elsewhere, in whole or
   in part, and is not under consideration by another journal.

2. **Thesis or dissertation disclosure.** The work is not derived
   from a thesis or dissertation. (AMHP §3.)

3. **Preprint disclosure.** The manuscript will be posted to OSF as a
   pre-print at the time of AMHP submission (the OSF pre-registration,
   covering split indices and success thresholds, was timestamped
   before any test-set evaluation). The OSF DOI will be supplied as
   soon as it is minted. The manuscript has not been posted to bioRxiv,
   arXiv, or any other preprint server.

4. **Author approval.** The single author has read and approved the
   final manuscript as submitted.

5. **ICMJE authorship.** The single author meets all four ICMJE
   authorship criteria: substantial contributions to design, data
   acquisition, analysis, and interpretation; drafting the manuscript;
   final approval; and accountability for all aspects of the work.
   The detailed contribution statement is on the Title Page file.

6. **Generative AI policy (AMHP §5).** Generative AI tools were used
   solely for code scaffolding, reference formatting, and editorial
   review of drafts. The AI tools did not generate scientific claims,
   study design, analyses, or interpretation. All scientific content
   was authored, reviewed, and approved by the human author. The AI
   contribution is disclosed in the Methods section and acknowledged
   on the Title Page.

7. **Statistical expertise.** All statistical analyses (XGBoost
   training, Mondrian split-conformal calibration, ECE, AUROC,
   bootstrap intervals, Sobol decomposition) were performed by the
   author, who holds a medical degree and has formal training in
   statistical methods, machine learning, and aerospace medicine
   research design. Detailed methods, including software versions and
   random seeds, are documented in §2 of the manuscript and in the
   accompanying code repository.

8. **Suggested reviewers.** Six suggested reviewers, each with
   verified institutional affiliation and email, are provided in the
   accompanying file `suggested_reviewers.md`. None has co-authored
   work with the author in the past three years; none shares a
   current institution with the author; and none has previously
   reviewed any version of this manuscript.

9. **Figure color.** All figures are intended for grayscale print and
   color online. No color print is requested; the Color Surcharge
   Form is therefore not submitted.

10. **Conflicts of interest.** The author declares no conflicts of
    interest. A signed COI form is enclosed.

11. **Funding.** No external funding was received for this work.
    The research is self-funded.

The package includes a depersonalized manuscript file, the title page
file with author identity, six figure files, the
TRIPOD-AI reporting checklist (supplementary), a datasheet for the
synthetic dataset (Gebru et al. 2018, supplementary), model cards for
the surrogate and OOD detector (Mitchell et al. 2019, supplementary),
the OSF pre-registration (timestamp linked), and signed Author
Checklist, Copyright Release, and Conflict of Interest forms.

I look forward to the editorial decision.

Sincerely,

Diego Malpica, MD
Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force, Bogotá, Colombia.
ORCID: 0000-0002-2257-4940
[dlmalpica@yahoo.com](mailto:dlmalpica@yahoo.com)
