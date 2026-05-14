# Title page — IJNMBE submission

> Upload this file at the Wiley CNM portal as the **Title Page** during
> submission. The IJNMBE peer-review model is **single-anonymous** (Wiley
> default; double-anonymous not offered on this title), so author identity
> is visible to reviewers and the title page is **not** depersonalised.
>
> All seven Wiley Free-Format mandatory title-page declarations are
> consolidated below in the order specified by the IJNMBE Author
> Guidelines (verified 2026-05-01).

---

## Title

Conformal machine-learning emulation and out-of-distribution detection
for the FAA CAMI G-Effects mechanistic model of acceleration physiology.

## Short title (≤ 70 characters; for portal entry)

Conformal ML wrapper for a validated ODE physiological model.
*(60 characters including spaces.)*

## Author

**Diego Malpica, MD** (sole author).

ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940).

Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC),
Bogotá, Colombia.

## Corresponding author

Diego Malpica, MD
Direction of Aerospace Medicine, FAC
Bogotá, Colombia.
Email: <dlmalpica@yahoo.com>
ORCID: 0000-0002-2257-4940.

## Author contributions (CRediT)

The single author meets all four ICMJE criteria for authorship and
covers the full CRediT taxonomy:

- **Conceptualization** — defined the additive ML-extension architecture
  over the FAA-validated CGEM core.
- **Methodology** — designed the surrogate, Mondrian split-conformal,
  conformal-distance OOD, and Sobol/Morris pipeline.
- **Software** — implemented `cgem_ext` (Python), the FastAPI service,
  and the Vite/React frontend; wrote the test suite.
- **Validation** — pre-registered the protocol on OSF; ran the held-out
  evaluation with frozen splits.
- **Formal analysis** — computed all reported point estimates, bootstrap
  CIs, conformal coverage, OOD calibration, and Sobol/Morris indices.
- **Investigation, Data curation** — generated and verified
  `cgem_synthetic_v1`; logged binary SHA-256 and master seed.
- **Writing — original draft, review and editing** — drafted the entire
  manuscript and revised it iteratively.
- **Visualization** — designed and rendered all six figures via the
  ECharts pipeline.
- **Supervision, Project administration, Funding acquisition** — sole
  responsibility (self-funded).

## Title-page declarations (Wiley Free Format mandatory list)

The following seven declarations are mandatory on the IJNMBE title page;
the same content is mirrored in the cover letter.

### 1. Data availability statement

The complete framework is open under the MIT licence at
`https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`. The
synthetic dataset `cgem_synthetic_v1.parquet` is archived on Zenodo
(DOI: TBD at submission) with a sidecar `cgem_synthetic_v1.meta.json`
recording the CGEM-binary SHA-256, master seed (42), tier definitions,
and package version. A reproducibility Docker image is on GitHub
Container Registry (GHCR). The Open Science Framework (OSF)
pre-registration locks split indices, success thresholds, and search
spaces — URL TBD at submission. The dataset is cited formally in the
reference list per the Joint Declaration of Data Citation Principles
(reference [22] in the manuscript).

Data and code will be uploaded to the Wiley CNM portal under the
**Data Files** designation (not as Supporting Information). On
acceptance, Wiley deposits Data Files to figshare under CC-Zero by
default and assigns a permanent DOI bound to the HTML article.

### 2. Funding statement

This research received no external funding. All work was self-funded by
the author.

### 3. Conflict of interest disclosure

The author declares no conflicts of interest, financial or otherwise, in
relation to this work.

### 4. Ethics approval statement

n/a — synthetic data only. The study used exclusively synthetic outputs
of the FAA CAMI CGEM Fortran ODE model with anthropometric and
physiological presets internal to the model. No human or animal subjects
were involved; ethics-board approval was therefore not required.
Empirical validation against centrifuge subjects is the subject of
separate work, reported elsewhere under the appropriate IRB approval.

### 5. Patient consent statement

n/a — no human subjects.

### 6. Permission to reproduce material from other sources

n/a — all figures, tables, equations, and code are original to this
work; no third-party material is reproduced. The FAA CAMI CGEM Fortran
source and compiled binary are distributed by the FAA under the FAA's
own terms; this work does not redistribute them.

### 7. Clinical-trial registration

n/a — methodological / synthetic-data study; no clinical trial.

## Acknowledgments

The author gratefully acknowledges the FAA Civil Aerospace Medical
Institute (CAMI), Oklahoma City, for developing, validating, and openly
distributing the CGEM Fortran model (Technical Report DOT/FAA/AM-23/6)
on which this extension layer is built.

## Word counts

- Title: 21 words; 145 characters including spaces. No abbreviations
  except proper nouns (FAA, CAMI).
- Short title: 60 characters including spaces. (Wiley short-title
  cap ≤ 70.)
- Abstract: 368 words. (IJNMBE cap ≤ 400.)
- Body (Introduction → Conclusion): ≈ 4,980 words (§3.8 multi-fidelity
  section removed 2026-05-12). IJNMBE has no stated body-word cap; the
  length is consistent with recent IJNMBE Research Papers.
- References: 27.
- Tables: 5.
- Figures: 6 (all in main body at submission). At revision stage they
  will be uploaded as separate files; compound figures (e.g., Fig 1's
  panels A–H) will be uploaded as a single file per the IJNMBE rule.
- Mandatory separate files: cover letter, Novelty File (≤ 100 words),
  Graphical Abstract mini-abstract (≤ 80 words / 3 sentences),
  Graphical Table of Contents image, suggested-reviewer list, Data
  Files (data + code).
