# OSF Pre-registration — Amendment 2026-05-17 (venue change)

**Project:** Conformal ML emulator + OOD detector for the FAA CAMI G-Effects mechanistic model
**Sole author:** Diego Malpica, MD (ORCID 0000-0002-2257-4940)
**Date:** 2026-05-17

## Trigger

Manuscript 5977782 was desk-rejected by the *International Journal for Numerical Methods in Biomedical Engineering* (IJNMBE, Wiley) on 2026-05-17 on scope grounds. The verbatim rejection text and the citation of IJNMBE's updated Aims and Scope ("no longer accepting submissions based purely on machine and deep learning methods applied to biomedical problems") are recorded at `manuscripts/_archive/ijnmbe/REJECTION.md`.

## Venue trajectory

The submission target moved through three venues on 2026-05-17:

1. **IJNMBE (Wiley, Q2, $0) — rejected.** Desk-rejected on scope at 2026-05-17.
2. **CMPB (Elsevier, Q1, $0) — considered, abandoned.** Top-ranked in both the 2026-05-12 and the post-rejection 2026-05-17 journal-scout outputs (`docs/publication/2026-05-{12,17}_journal-scout_cgem-emulator.md`). The cmpb-submit skill's claim that CMPB requires a verbatim non-use AI attestation was verified as a skill bug (in-place fixed; see `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`). After AI policy was resolved, the body word count was rebuilt against CMPB's hard 3,500-word cap (Full Length Article). The IJNMBE manuscript header claimed body ≈ 4,980 words; direct measurement after Tasks 6/7/8 trims (cumulative −1,666 words from §2/§3/§4) showed the actual prose body was ~5,800 words — still ~2,300 words over the CMPB cap. Aggressive further trim would have removed substantive content rather than connective tissue. Abandoned.
3. **BSPC (Elsevier, Q1, $0) — chosen.** Rank 1 in the 2026-05-17 re-scout (score 85, Q1 in Biomedical Engineering / Health Informatics / Signal Processing per Scimago 2024, JIF 4.9, ~40-50% acceptance). BSPC's "Full Paper" soft target is ~5,000 words (no hard cap); the manuscript at ~5,800 sits comfortably within BSPC convention. Abstract reformatted from the four-heading structured form (CMPB style) to BSPC's unstructured ≤250-word form. §1 reframed toward BSPC's biosignal-processing scope: the CGEM outputs are physiological biosignals (cerebrovascular, oxygenation, visual function), and the wrapper is presented as a biosignal-fidelity-preserving emulator with conformal coverage and OOD abstention.

The corresponding-author submission package will be uploaded to Editorial Manager at `https://submit.elsevier.com/BSPC`. The cover letter is addressed to Prof. Panicos A. Kyriacou (Editor-in-Chief, City University of London).

## What does NOT change

- All OSF-pre-registered hypotheses (H1–H6) remain unchanged.
- The OSF-frozen split indices (`docs/publication/osf_split_indices.parquet`) remain authoritative.
- The OSF-frozen hyperparameter search spaces (`docs/publication/osf_search_spaces.json`) remain authoritative.
- The frozen synthetic dataset (`cgem_synthetic_v1.parquet`, master seed 42, binary SHA-256 recorded in the `.meta.json` sidecar) is unchanged.
- All conformal calibration, all numerical results, all figures, all tables, all hyperparameters remain unchanged.
- The 2026-05-06 amendment (H5 heteroscedastic CQR + H6 archival external validation against Whinnery and Forster 2013) remains in force.

## What did change (procedural, non-scientific)

- Manuscript body trims of ~1,666 words across §2/§3/§4, removing connective prose and redundant rationale without removing any analytical step, hyperparameter, statistic, or pre-registration reference. These trims are calibrated for CMPB's hard cap but persist into the BSPC submission (the paper is leaner and tighter for them).
- Abstract reformatted from 394-word four-heading structured form (IJNMBE / CMPB style) to 247-word unstructured form (BSPC style). Every numerical anchor preserved verbatim.
- §1 opening paragraph rewritten twice: once toward CMPB's "computer-methods-and-programs" framing, then re-reframed toward BSPC's biosignal-processing scope. The body of the introduction (§1 paragraphs 2–6 describing the application domain, the CGEM model, the three limits, the four solution components, and the synthetic-only declaration) is unchanged.
- §4.6 rewritten to a "method-vs-application" separation: the present paper is the method against CGEM as ground truth; paper-2 will replace the two-stage classifier+regressor with conformalized survival analysis on archival data; paper-3 will validate against own-centrifuge subjects.

This is a procedural amendment recording the venue change; it has no scientific content and is filed for OSF audit completeness.

## Cross-references

- IJNMBE rejection record: `manuscripts/_archive/ijnmbe/REJECTION.md`
- CMPB pivot spec (then re-pivoted): `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`
- Implementation plan: `docs/superpowers/plans/2026-05-17-cgem-cmpb-pivot.md`
- 2026-05-12 scout (pre-rejection): `docs/publication/2026-05-12_journal-scout_cgem-emulator.md`
- 2026-05-17 scout (post-rejection, AI-policy-filtered): `docs/publication/2026-05-17_journal-scout_cgem-emulator.md`
- cmpb-submit skill bug record: `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`

Diego Malpica, MD
[Signed at OSF posting]
