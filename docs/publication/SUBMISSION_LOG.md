# CGEM Emulator Manuscript — Submission Log

**Manuscript:** Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology.
**Author:** Diego Malpica, MD (sole). ORCID 0000-0002-2257-4940.
**Manuscript scope:** XGBoost two-stage surrogate emulator + Mondrian-stratified split-conformal + heteroscedastic Conformalized Quantile Regression + Mahalanobis OOD with distribution-free conformal abstention + Sobol/Morris sensitivity, all wrapping the FAA CAMI Fortran CGEM ODE model. ~ 6,000 body words, 247-word unstructured abstract, 6 figures, 5 tables, 27 references, 18 supplementary items.

This log tracks every venue attempt, decision, and the next planned move. **Update each time a decision lands.**

---

## Current status (last updated 2026-05-17)

- **Active target:** *Biomedical Signal Processing and Control* (BSPC, Elsevier, Q1, $0 APC subscription track).
- **Portal:** https://submit.elsevier.com/BSPC (Editorial Manager).
- **EiC:** Prof. Panicos A. Kyriacou, City University of London.
- **Submission package:** Built and committed to `manuscripts/bspc/rendered/` (7 .docx + 6 figure PDFs) and `manuscripts/bspc/supplementary/` (18 Elsevier S-numbered items + captions).
- **Next action (Diego):** Manual portal upload at the link above. Date-stamp the cover letter + declarations first; add the Zenodo and OSF DOIs once minted.

---

## Submission history

### Attempt 1 — IJNMBE (Wiley, Q2, $0 APC)

- **Submitted:** 2026-05-12 (Wiley CNM portal).
- **Manuscript ID:** 5977782.
- **Decision:** **Desk-rejected on scope.**
- **Decision date:** 2026-05-17.
- **EiC:** Prof. Perumal Nithiarasu, Swansea University.
- **Rejection text:** Categorical — *"International Journal for Numerical Methods in Biomedical Engineering is no longer accepting submissions based purely on machine and deep learning methods applied to biomedical problems."* The "ML to solve / accelerate numerical methods" carve-out exists but the EiC ruled the manuscript outside it.
- **Appealability:** None. Categorical policy change.
- **Archive:** `manuscripts/_archive/ijnmbe/` (full submission tree + `REJECTION.md` with verbatim text).

### Attempt 2 (considered, abandoned) — CMPB (Elsevier, Q1, $0 APC)

- **Decision date:** 2026-05-17.
- **EiC:** Prof. Filippo Molinari, Polytechnic of Turin.
- **Reason for abandonment:** Body word-count mismatch.
  - The IJNMBE manuscript header claimed ≈ 4,980 body words. CMPB's hard Full-Length-Article cap is ≤ 3,500.
  - Cumulative trims (−540 §2 / −469 §3 / −657 §4) reduced the manuscript by 1,666 words, but direct `wc -w` measurement showed the actual prose body was ~ 5,800 words — still ~ 2,300 words over the CMPB cap.
  - The header's word count was off by ~ 50%.
  - Further trim would have removed substantive content (analytical detail, methodology) rather than connective tissue. Decided not to compromise the paper for CMPB.
- **Side issue resolved:** The `cmpb-submit` skill historically claimed CMPB required a verbatim non-use AI attestation in the cover letter; verified this was a skill bug (Elsevier publisher-wide policy is disclosure-if-used). Skill fixed in-place 2026-05-17 (8 sections). Record at `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`.

### Attempt 3 — BSPC (Elsevier, Q1, $0 APC) — IN PROGRESS

- **Pivot date:** 2026-05-17.
- **Portal:** https://submit.elsevier.com/BSPC.
- **EiC:** Prof. Panicos A. Kyriacou, City University of London. Co-EiC: Prof. Anna Maria Bianchi, Polytechnic of Milan.
- **Why BSPC:** Rank 1 in the 2026-05-17 re-scout (score 85, Q1 in Biomedical Engineering / Health Informatics / Signal Processing per Scimago 2024, JIF 4.9, acceptance rate ~ 40–50 %). Soft target ~ 5,000 body words with no hard cap accommodates the 6,020-word manuscript without further trim. Scope fit (22/30 in the scout) required §1 reframing toward biosignal processing: CGEM outputs are physiological biosignals (cerebrovascular, oxygenation, visual function), wrapper presented as biosignal-fidelity-preserving emulator with conformal coverage and OOD abstention.
- **Submission package built 2026-05-17.** Files in `manuscripts/bspc/rendered/` (manuscript with continuous line numbers + double spacing baked into XML; cover letter; highlights; 4 standalone declaration files; 6 figures) and `manuscripts/bspc/supplementary/` (Fig_S1–S2, Table_S1–S3, Appendix_S1–S6, Data_S1–S7, plus the Supplementary_Captions inventory).
- **Compliance:** Body 6,020 / ~5,000 soft target (over by ~20% but no hard cap); abstract 247 / 250 unstructured (PASS); 6 keywords / 1–7 range (PASS); 5 highlight bullets all ≤ 81 chars / 85 cap (PASS); references Elsevier numbered with DOIs (PASS); CRediT + Data Availability present (PASS); bidirectional supplementary audit (PASS, 18 items perfect match); AI declaration omitted (nothing to disclose per Elsevier disclosure-if-used + local policy).
- **Awaiting:** Diego's manual portal upload.
- **Expected decision timeline:** BSPC advertises ~ 10 days to first decision. Realistic range: 2–6 weeks for first editorial response.

---

## Fallback ladder (if BSPC desk-rejects or major-revisions in a way that doesn't suit)

Pre-vetted by the 2026-05-17 re-scout (`docs/publication/2026-05-17_journal-scout_cgem-emulator.md`). Listed in recommended order:

| Rank | Journal | Publisher | Q | APC | Soft cap | Scope match | Why next |
|---:|---|---|---|---|---|---:|---|
| 1 | **Annals of Biomedical Engineering** (ABE) | Springer / BMES | Q2 | $0 hybrid sub | 10,000 words | 26/30 | Strong scope on "theory and mathematical models", BMES society, lots of headroom. Manuscript fits without further trim. |
| 2 | **Physiological Measurement** | IOP Publishing | Q2 | $0 non-OA | ~ 8,000 | 28/30 | **Strongest scope match in the eligible pool.** Scope page explicitly names "physiological modelling, simulation, model identification, and control" and "physics- and model-based machine learning." 28 % published acceptance rate. |
| 3 | **Journal of the Royal Society Interface** | Royal Society | Q1 | $0 hybrid | (verify at venue) | 23/30 | Q1 fallback if BSPC plus ABE plus PhysMeas all reject; multidisciplinary; UQ-friendly. ~ 15-20 % acceptance — long shot. |

**Hard exclusions (do NOT re-shop):**
- IJNMBE (Wiley) — desk-rejected on categorical scope policy.
- AMHP (ASMA) — denylisted in `~/.hermes/skills/journal-scout/AI_POLICY_FILTER.md` § 4 after the 2026-05-08 Newman desk-rejection on declared AI use.
- Computers in Biology and Medicine (Elsevier) — WoS Core (SCIE) removed 2024-11-17.
- PLOS Computational Biology — Gold OA $3,165, fails $0 APC constraint.
- CMPB (Elsevier) — abandoned 2026-05-17 on word-cap mismatch; would require a major-revision rebuild before retry.
- Medical Engineering & Physics (Elsevier → IPEM/IOP) — transition-year editorial pipeline disrupted; re-evaluate post-2026.

---

## Updating this log

When BSPC delivers a decision:
- **Acceptance / Minor revisions:** add a new "Attempt 3 — outcome" subsection under Submission history. Update Current status. Optionally close this log.
- **Major revisions:** record the decision under Attempt 3 with reviewer-comment summary; add an "Attempt 3 revision" subsection when the revision is submitted.
- **Desk rejection or hard rejection:** move "BSPC — chosen" to the Submission history; start "Attempt 4 — ABE" under Current status (or whichever venue is next per the fallback ladder); rebuild the submission package in `manuscripts/abe/` mirroring the `manuscripts/bspc/` pattern; file a new OSF venue-change amendment in `docs/publication/`.

The auto-memory entries at `~/.claude/projects/-root-repos-CAMI-Gz-Effects-Model-CGEM-/memory/` mirror this log at the per-Claude-session level — they should be updated in parallel with this file.

---

## Cross-references

- IJNMBE archive: `manuscripts/_archive/ijnmbe/`
- BSPC working tree: `manuscripts/bspc/`
- CMPB pivot spec (records IJNMBE→CMPB→BSPC reasoning): `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`
- CMPB pivot implementation plan: `docs/superpowers/plans/2026-05-17-cgem-cmpb-pivot.md`
- Journal-scout reports: `docs/publication/2026-05-{12,17}_journal-scout_cgem-emulator.md`
- OSF venue-change amendment: `docs/publication/osf_amendment_2026-05-17.md`
- Skill bug record: `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`
