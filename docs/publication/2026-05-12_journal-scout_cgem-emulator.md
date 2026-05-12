# Journal Scout — CGEM Emulator Manuscript
**Date:** 2026-05-12  
**Paper:** "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"  
**Manuscript path:** `docs/publication/manuscript.md`  
**APC constraint:** $0 strict — subscription / non-OA track only  
**AI disclosure:** YES (generative AI used for code scaffolding, formatting, editorial review → ICMJE/COPE disclosure required)  
**Author context:** Diego Malpica, MD — Colombia (Research4Life Group B = 50 % discount on OA APCs where relevant, but irrelevant here given strict $0 constraint)  
**AI-Use Policy Filter:** ON (default; hard denylist active)

---

## Phase 1 — Field inference

| Dimension | Assessment |
|---|---|
| Primary field | Biomedical engineering / Computational physiology |
| Subfield | Surrogate modelling, conformal prediction, uncertainty quantification, OOD detection |
| Article type | Original research — computational/methodological |
| Methodology keywords | XGBoost surrogate, Mondrian conformal, CQR, Mahalanobis OOD, Sobol/Morris SA, OSF pre-registration |
| Reporting guideline | TRIPOD-AI (prediction model); OSF pre-registration |
| Body word count | ≈ 5,430 (≈ 4,980 after §3.8 drop) |
| AI-disclosure active? | YES — generative AI used in preparation; filter ON |
| Closest published precedent | Portela, Banga & Matabuena (2025) *PLOS Comput Biol* 21(5):e1013098 — conformal prediction on biological ODE systems |

---

## Phase 3.5 — AI-Use Policy compatibility

**Filter ON.** All candidate journals checked.

### Hard denylist hits (excluded before scoring)
| Journal | Reason | Evidence |
|---|---|---|
| Aerospace Medicine and Human Performance (AMHP, ASMA) | Desk-rejection of declared AI use — verbatim Newman letter on file | `AI_POLICY_FILTER.md` §4; 2026-05-08 |

### Eliminated on disqualifying flags (non-AI reasons)
| Journal | Reason |
|---|---|
| Computers in Biology and Medicine (Elsevier, CbioM) | WoS Core Collection (SCIE) removed 2024-11-17 — peer-review manipulation investigation by Clarivate; indexing not expected to be restored within 2026 cycle. Do not submit. |
| Mathematical Biosciences and Engineering (AIMS Press) | Not in WoS Core Collection (SCIE). Scopus-only. Eliminated on WoS absence. |
| Results in Engineering (Elsevier) | Q1 Gold OA only — no $0 subscription track. Scope fit also poor (general engineering). |
| PLOS Computational Biology | Gold OA USD 3,165 — excluded on strict $0 APC constraint. (Note: highest scope match of any eliminated journal; revisit if APC budget becomes available.) |

---

## Phase 4 — Scoring

Scoring per `SCORING_RUBRIC.md`: Scope (30) / Quartile (25) / APC (25) / Acceptance (10) / Speed (5) / Indexing bonus (up to +5).  
APC dimension: subscription $0 confirmed = 22 pts. Uncertainty bands apply throughout.

### Ranked table (all eligible journals, subscription-only lane)

| Rank | Journal | Publisher | SJR Quartile | APC | Scope | Q | APC pts | Accept | Speed | Bonus | **Total** |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Computer Methods and Programs in Biomedicine (CMPB) | Elsevier | **Q1** | $0 non-OA | 28 | 25 | 22 | 6 | 3 | +5 | **89** |
| 2 | Int J Numer Methods Biomed Eng (IJNMBE) | Wiley | Q2 | $0 non-OA | 27 | 20 | 22 | 5 | 3 | +4 | **81** |
| 3 | Biomedical Signal Processing and Control (BSPC) | Elsevier | Q2 | $0 non-OA | 22 | 20 | 22 | 8 | 3 | +5 | **80** |
| 4 | Medical Engineering & Physics | Elsevier | Q2 | $0 non-OA | 23 | 20 | 22 | 5 | 3 | +5 | **78** |
| 5 | Physiological Measurement | IOP Publishing | Q2 | $0 non-OA | 20 | 20 | 22 | 6 | 3 | +5 | **76** |
| 6 | IRBM (Innovation and Research in BioMedical Eng) | Elsevier Masson | Q2 | $0 non-OA | 22 | 20 | 22 | 5 | 3 | +2 | **74** |
| 7 | Mathematical Biosciences | Elsevier | Q2 | $0 non-OA | 18 | 20 | 22 | 5 | 3 | +4 | **72** |

**Score notes:**
- CMPB acceptance rate: ~30 % (6 pts) based on published metrics; Scopus+WoS SCIE+PubMed (+5 bonus). Confirmed tolerant AI policy (Elsevier disclosure-and-not-author).
- IJNMBE acceptance rate: unknown (5 pts neutral). Scopus+WoS SCIE (+4). Submission package already built. Two papers from this manuscript's reference list (Kakhaia 2021, Boileau 2015) published here — strongest scope anchor.
- BSPC acceptance rate: estimated 40–50 % range (8 pts, medium confidence — Elsevier metrics 2024). Scopus+WoS SCIE+PubMed (+5). Scope slightly peripheral: signal processing framing required.
- Medical Engineering & Physics: Scopus+WoS SCIE+PubMed/MEDLINE (+5). Accepts physiological model validation papers.
- Physiological Measurement: published 28 % acceptance rate (6 pts, high confidence — IOP public disclosure). Scopus+WoS SCIE+PubMed (+5). Scope is applied physiological measurement — ML/conformal wrapper fits as a measurement-tool paper.
- IRBM: smaller European venue; unclear WoS SCIE status → only Scopus bonus claimed (+2).
- Mathematical Biosciences: requires reframing toward the ODE/mathematical aspects; scope deduction (18/30) reflects mismatch with primary ML contribution.

---

## Phase 5 — Top-3 and recommended submission ladder

### **Top 3 (bold = highest-ranked)**

| Rank | Journal | Publisher | Quartile | APC | Scope match | Word cap | Indexing | Score |
|---:|---|---|---|---|---|---|---|---:|
| **1** | **Computer Methods and Programs in Biomedicine** | Elsevier | **Q1** | $0 non-OA | Very strong (28/30) | None stated | Scopus, WoS SCIE, PubMed | **89** |
| **2** | **Int J Numer Methods Biomed Eng (IJNMBE)** | Wiley | **Q2** | $0 non-OA | Strong (27/30) | None stated | Scopus, WoS SCIE | **81** |
| **3** | **Biomedical Signal Processing and Control** | Elsevier | **Q2** | $0 non-OA | Adequate (22/30) — needs signal/control framing | 8,000 words | Scopus, WoS SCIE, PubMed | **80** |

---

### Narrative

**CMPB (Rank 1, Q1, score 89).** The strongest scope match in the entire candidate pool for a paper whose primary contribution is computing methodology applied to biomedical simulation. CMPB's stated aims explicitly include "computational methods and tools for medical or biological problems"; the paper's conformal-ML stack + OOD detector + surrogate fits cleanly. Elsevier's hybrid model means the non-OA track is $0. The tradeoff is Q1: acceptance rates are lower (est. ~30 %), review is typically slower, and the paper must defend its methodological novelty against a more demanding reviewer pool than IJNMBE. **Risk:** CMPB recently removed from consideration if CbioM confusion persists — CMPB (ISSN 0169-2607) is distinct from CbioM (ISSN 0010-4825, which was WoS-suspended). Confirm ISSN before submission. CMPB remains fully WoS-indexed as of 2026-05.

**IJNMBE (Rank 2, Q2, score 81).** The current target journal. Two papers from the manuscript's reference list were published here; the paper fits three of IJNMBE's explicit scope clauses simultaneously (ODE-based biomedical model; AI extension; human wellbeing application); the submission package is already built; and the cover letter pre-empts the "no standard procedure" scope filter. The Q2 quartile and unknown acceptance rate mean acceptance probability is plausibly higher than CMPB. **Recommendation: submit to IJNMBE first** given the ready package, then escalate to CMPB if rejected.

**BSPC (Rank 3, Q2, score 80).** Solid Elsevier Q2 journal with a broad biomedical signal-processing scope. The paper would need minor reframing: the physiological ODE outputs as "biosignals" and the ML layer as a signal-processing / control tool. AUROC ≥ 0.996 on event classification and Sobol sensitivity decomposition translate well to BSPC's audience. The estimated 40–50 % acceptance rate makes this a high-probability fallback if IJNMBE rejects.

---

### Best Q2/Q3 Alternative (explicitly called out)

**Biomedical Signal Processing and Control (BSPC, Elsevier, Q2, score 80)** is the best Q2 option outside the current IJNMBE target, with an estimated 40–50 % acceptance rate — substantially higher than either CMPB or IJNMBE. If speed and acceptance probability are the primary drivers and the author is willing to invest ~1 hour reframing the abstract toward biosignal/control language, BSPC is the lowest-risk Q2 venue. It is fully indexed (Scopus, WoS SCIE, PubMed/MEDLINE) and carries $0 on the non-OA submission track.

---

### Recommended submission ladder (no APC constraint, subscription track)

| Step | Journal | Rationale |
|---:|---|---|
| 1 | **IJNMBE (Q2, Wiley)** | Submission package built; strongest direct scope evidence (own references published here); cover letter pre-emptively addresses scope filter. |
| 2 | **CMPB (Q1, Elsevier)** | Highest aggregate score; if IJNMBE rejects on scope or novelty grounds, CMPB rewards the computing-methodology framing directly. |
| 3 | **BSPC (Q2, Elsevier)** | Highest estimated acceptance probability in the candidate pool; biosignal framing accessible with minor abstract revision. |
| 4 | **Medical Engineering & Physics (Q2, Elsevier)** | Accepts physiological-model validation + ML papers; fully indexed; clean fallback. |
| 5 | **Physiological Measurement (Q2, IOP)** | 28 % published acceptance rate; published active AI disclosure policy (tolerant). Pre-submission inquiry recommended to confirm $0 non-OA track is available. |

---

## Excluded — AI-policy incompatible

| Journal | Publisher | Evidence | Date |
|---|---|---|---|
| Aerospace Medicine and Human Performance (AMHP) | ASMA / Editor-in-Chief David G. Newman | Desk-rejection of "Lifetime prevalence and event rates of SD in Colombian Aerospace Force pilots" citing declared AI use; verbatim letter on file in `AI_POLICY_FILTER.md` §4 | 2026-05-08 |

AMHP remains on the hard denylist until Newman or a successor publishes a revised policy aligning with ICMJE/COPE/WAME. Re-verify annually (1 May) or on next rejected-manuscript event.

---

## Notes on submission readiness (as of 2026-05-12)

Before submitting to IJNMBE (Step 1):

1. **OSF DOI** — mint the pre-registration on OSF and replace all "TBD at submission" placeholders in `manuscript.md` (§2.7, §4.5), `cover_letter_ijnmbe.md`, and `novelty_file_ijnmbe.md`. This is a process blocker, not a scientific blocker.
2. **Zenodo DOI** — archive `cgem_synthetic_v1.parquet` and replace reference [22] DOI placeholder.
3. **Figures 1–5** — render to TIFF (1200 dpi line art / 600 dpi combination) and collect in `docs/publication/rendered/`.
4. **Table count header** — update manuscript header to "Tables: 5" (Tables 1–5 remain after §3.8 drop; header currently reads "Tables: 4" — also incorrect before the drop).
5. **§3.8 NARGP section** — dropped in this revision cycle (result is negative and statistically thin); key finding compressed into §4.6 item 3 as future-work framing.

These are tracked separately in the project ROADMAP.md Phase 7 checklist.
