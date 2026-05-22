# OSF Pre-registration — Amendment 2026-05-22 (venue change, amendment 2)

**Project:** Additive ML wrapper for the FAA CAMI G-Effects mechanistic model — conformal prediction, OOD detection, and global sensitivity
**Sole author:** Diego Malpica, MD (ORCID 0000-0002-2257-4940)
**Date:** 2026-05-22
**Amendment number:** 2

## Trigger

Manuscript BSPC-D-26-08373 was desk-rejected by *Biomedical Signal Processing and Control* (BSPC, Elsevier) on 2026-05-22 on scope grounds. The rejection was an editorial pre-screen — generic boilerplate citing high acceptance threshold and pre-screening for scope fit; no reviewer comments, no specific scope objection beyond the generic notice. Executive Editor Prof. Lisheng Xu, PhD, signed the decision. The 2026-05-17 journal-scout had flagged BSPC scope match at 22/30 (versus PMEA 28/30 and ABE 26/30); BSPC won the overall ranking on Q1 quartile (+25 pts) and acceptance rate (~40–50 %), but the editorial pre-screen rejected on scope alignment alone, ignoring the ranking score. The 2026-05-22 desk rejection is the calibration event behind the journal-scout v2.4.0 rubric overhaul that tightens scope-match weighting to a hard ≥ 25/30 floor.

## Venue trajectory

The submission target now moves through its fourth venue:

1. **IJNMBE (Wiley, Q2, $0) — rejected.** Desk-rejected on scope at 2026-05-17.
2. **CMPB (Elsevier, Q1, $0) — considered, abandoned.** Body word count exceeded the hard 3,500-word cap.
3. **BSPC (Elsevier, Q1, $0) — rejected.** Desk-rejected on scope at 2026-05-22.
4. **PMEA (IOP Publishing, Q2, $0) — chosen.** PMEA's scope explicitly names "physiological modelling, simulation, model identification, and control" and "physics- and model-based machine learning" — the strongest single-clause scope match in the eligible Q2 pool (28/30). The corresponding-author submission package will be uploaded to ScholarOne at `http://mc04.manuscriptcentral.com/pmea-ipem`. The cover letter is addressed to Prof. Xiao Hu (Editor-in-Chief, Emory University).

## What does NOT change

- All OSF-pre-registered hypotheses (H1–H6) remain unchanged.
- The OSF-frozen split indices (`docs/publication/osf_split_indices.parquet`) remain authoritative.
- The OSF-frozen hyperparameter search spaces (`docs/publication/osf_search_spaces.json`) remain authoritative.
- The frozen synthetic dataset (`cgem_synthetic_v1.parquet`, master seed 42, binary SHA-256 recorded in the `.meta.json` sidecar) is unchanged.
- All conformal calibration, all numerical results, all figures, all tables, all hyperparameters remain unchanged.
- The 2026-05-06 amendment (H5 heteroscedastic CQR + H6 archival external validation against Whinnery and Forster 2013) remains in force.
- The 2026-05-17 amendment (venue change to BSPC) remains historical record; the science of that amendment is unaffected.

## What did change (procedural, non-scientific)

- **Title.** Updated to "An additive ML wrapper for validated ODE physiological models: conformal prediction, out-of-distribution detection, and global sensitivity, applied to the FAA CAMI G-Effects Model." The new title signals "methodology paper" to PMEA's scope screen and positions FAA-CGEM as the demonstration case, not the headline.
- **Abstract restructure.** Reformatted from BSPC's unstructured 247-word paragraph into PMEA's mandatory four-heading structure: Objective / Approach / Main results / Significance. Word count target ≤ 250. Every numerical anchor preserved verbatim.
- **References.** Converted from Vancouver numerical `[n]` to Harvard alphabetical with article titles, the IOP convention required by PMEA. Every reference includes the full article title (already present in the BSPC variant; the conversion was layout-only). All 27 DOIs preserved.
- **§1 paragraph 1 reorder.** Opening reframed to lead with the generalizable methodological pattern (additive ML wrapper for validated ODE physiological models), with CGEM positioned as the demonstration case. Paragraphs 2–6 of §1 unchanged. Methods, Results, and Discussion (§2–§5) unchanged.
- **Consolidated Acknowledgements section** placed immediately before References inside the manuscript PDF. Folds Funding, Conflict of Interest, Author Contributions, Ethics, and Data Availability into a single section per IOP convention. Drops Elsevier-convention separate declaration files (`author_contributions.docx`, `declaration_of_competing_interest.docx`, `statement_on_human_animal_studies.docx`). Drops the BSPC Highlights file (PMEA does not use Highlights).
- **Single-PDF submission with figures inline at first reference.** PMEA requires a single PDF with figures and tables embedded inline, 12 pt font, ≥ 1.5 line spacing. The six previously-standalone fig PDFs are now embedded inline in `manuscripts/pmea/rendered/manuscript.pdf` and the standalone `fig*.pdf` files are dropped from the PMEA submission tree.
- **Cover letter** rewritten for PMEA / Prof. Xiao Hu, EiC, quoting PMEA's scope clauses verbatim and disclosing the prior IJNMBE (2026-05-17) and BSPC (2026-05-22) desk rejections.
- **Suggested reviewers** carried forward from the BSPC list (four candidates: Matabuena, Gopakumar, Boström, Chakraborty), re-audited against the PMEA editorial board (none on the PMEA board — clean to suggest), and the rationale block rewritten to use PMEA scope vocabulary.

This is a procedural amendment recording the venue change; it has no scientific content and is filed for OSF audit completeness.

## Cross-references

- BSPC rejection record: `manuscripts/_archive/bspc/REJECTION.md`
- IJNMBE rejection record: `manuscripts/_archive/ijnmbe/REJECTION.md`
- PMEA guidelines audit: `docs/publication/2026-05-22_pmea_guidelines_audit.md`
- Q2/Q3 post-PMEA fallback ladder: `docs/publication/2026-05-22_journal-scout_cgem-q2-q3-fallback.md`
- 2026-05-17 venue-change amendment (IJNMBE → BSPC): `docs/publication/osf_amendment_2026-05-17.md`
- 2026-05-06 H5/H6 amendment: `docs/publication/osf_amendment_2026-05-06.md`

Diego Malpica, MD
[Signed at OSF posting]
