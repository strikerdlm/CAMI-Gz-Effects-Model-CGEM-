# Suggested reviewers — CMPB submission

> Five candidates covering: the CGEM domain (computational physiological
> modelling), surrogate ML for physiological systems, conformal prediction
> methodology, variance-based sensitivity analysis, and ML in biomedicine.
> None has co-authored work with the corresponding author in the past three
> years; none shares an institution with the author; none has previously
> reviewed any version of this manuscript.
>
> **Verification required before portal entry:** Confirm current affiliation,
> re-verify institutional email (never personal Gmail/Yahoo), confirm no
> co-authorship on Scopus/OpenAlex, confirm no shared institution with
> Bogotá/Colombian Aerospace Force.

---

## 1. Kyle Copeland — FAA Civil Aerospace Medical Institute (CAMI), Oklahoma City, OK, USA

- **Email:** Verify via FAA AAM-631 directory (Kyle.Copeland@faa.gov or similar).
- **ORCID:** [0000-0001-7893-6716](https://orcid.org/0000-0001-7893-6716)
- **Rationale:** Lead author of the CGEM Fortran model (DOT/FAA/AM-23/6)
  that this manuscript wraps. Uniquely positioned to evaluate whether the
  ML extension layer preserves CGEM's validation chain, correctly reproduces
  the ODE outputs, and respects the model's documented limitations and
  calibration envelope.
- **No conflict:** No co-authorship; institutions are Oklahoma City vs Bogotá;
  no prior peer-review history with this author.

---

## 2. Andrea Aliverti, PhD — Politecnico di Milano, Italy

- **Email:** [andrea.aliverti@polimi.it](mailto:andrea.aliverti@polimi.it)
  *(verify via faculty page).*
- **ORCID:** [0000-0002-3892-3622](https://orcid.org/0000-0002-3892-3622)
- **Rationale:** Bioengineering professor working on physiological surrogate
  modelling, cardiopulmonary system identification, and ML-augmented
  physiological prediction. The methodological framing — XGBoost surrogate +
  Mondrian conformal + OOD detection over a validated mechanistic ODE model —
  falls squarely in his published wheelhouse. Has a record of CMPB-adjacent
  publications on computational respiratory and cardiovascular physiology.
- **No conflict:** No co-authorship; institution distinct from author.

---

## 3. Harris Papadopoulos, PhD — Frederick University, Nicosia, Cyprus

- **Email:** Verify via Frederick University computer science faculty page
  (h.papadopoulos@frederick.ac.cy or similar).
- **Rationale:** A principal developer of inductive (split) conformal prediction
  algorithms in the tradition of Vovk, Gammerman, and Shafer. His work on
  regression conformal predictors and conditional conformal prediction is
  directly relevant to §2.4 (Mondrian split-conformal calibration) and to
  the under-coverage finding on `time_to_gloc_s`. A CMPB reviewer with deep
  conformal-prediction expertise will engage seriously with the calibration
  claims and the proposed heteroscedastic extension (§4.4).
- **No conflict:** No co-authorship; Cyprus vs Bogotá; no prior review history.

---

## 4. Andrea Saltelli, PhD — University of Bergen, Bergen, Norway

- **Email:** Verify via University of Bergen CEES/SDG pages
  (andrea.saltelli@uib.no or similar).
- **Rationale:** A founding contributor to variance-based sensitivity analysis
  (Sobol indices) and a co-developer of the SALib sampling methodology used
  in §2.6. His perspective on the Saltelli quasi-random sampling design, the
  bootstrap CI computation, and the interpretation of ST > S₁ interaction
  patterns (§3.6) is authoritative. He has published extensively on the proper
  application of Sobol analysis and its limitations — precisely the territory
  the manuscript navigates.
- **No conflict:** No co-authorship; Norway vs Bogotá; no prior review history.

---

## 5. Alfredo Vellido, PhD — Universitat Politècnica de Catalunya (UPC), Barcelona, Spain

- **Email:** Verify via UPC/IDEAI faculty page (avellido@cs.upc.edu or similar).
- **Rationale:** Established researcher in machine learning applied to
  biomedical data with a sustained publication record in CMPB. His work spans
  interpretable ML, clinical prediction models, and uncertainty quantification
  in biomedical contexts — all directly relevant to the manuscript's
  methodological claims. Brings the CMPB-typical ML-in-medicine reviewer
  perspective that will probe the XGBoost architecture choices, the
  monotonicity constraints, and the clinical/operational framing.
- **No conflict:** No co-authorship; Spain vs Bogotá; no prior review history.

---

## Verification checklist before portal entry

For each candidate:
- [ ] Confirm affiliation is current (institutional faculty page or ORCID)
- [ ] Re-verify institutional email address (not personal)
- [ ] Confirm no co-authorship in past 3 years (Scopus / OpenAlex author search)
- [ ] Confirm no shared institution with Colombian Aerospace Force, Bogotá
- [ ] Confirm no prior review of any version of this manuscript

## Backup candidates

If any of the five are unavailable:

- **Massimo Mischi, PhD** — TU Eindhoven (biomedical signal processing;
  CMPB editorial board — flag to editor if suggested as reviewer)
- **Erin J. Ott, MD, PhD** — USAFSAM, Wright-Patterson AFB
  (aerospace medicine, operational G-tolerance perspective)
- **James E. Whinnery, MD, PhD** — Independent / formerly NASA & FAA
  (G-LOC physiology, centrifuge validation, CGEM historical context)
