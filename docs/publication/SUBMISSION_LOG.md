# CGEM Emulator Manuscript — Submission Log

**Manuscript:** An additive ML wrapper for validated ODE physiological models: conformal prediction, out-of-distribution detection, and global sensitivity, applied to the FAA CAMI G-Effects Model.
**Author:** Diego Malpica, MD (sole). ORCID 0000-0002-2257-4940.
**Manuscript scope:** Additive ML wrapper around a validated ODE physiological model. XGBoost two-stage surrogate emulator + Mondrian-stratified split-conformal + heteroscedastic Conformalized Quantile Regression + Mahalanobis OOD with distribution-free conformal abstention + Sobol/Morris global sensitivity. FAA CAMI Fortran CGEM is the demonstration substrate. ~ 6,200 body words, 248-word structured abstract (Objective / Approach / Main results / Significance), 6 figures inline, 5 tables, 27 references (Harvard alphabetical with article titles), 18 supplementary items.

This log tracks every venue attempt, decision, and the next planned move. **Update each time a decision lands.**

---

## Current status (last updated 2026-05-22)

- **Active target:** *Physiological Measurement* (PMEA, IOP Publishing, Q2 biomed eng, $0 APC subscription track).
- **Portal:** http://mc04.manuscriptcentral.com/pmea-ipem (ScholarOne).
- **EiC:** Prof. Xiao Hu, Emory University.
- **Submission package:** Built in `manuscripts/pmea/rendered/` and `manuscripts/pmea/supplementary/` per 2026-05-22 PMEA guidelines audit.
- **Next action (Diego):** Mint Zenodo dataset DOI + OSF preregistration DOI; paste into placeholders; portal upload at link above; date-stamp cover letter.

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

### Attempt 3 — BSPC (Elsevier, Q1, $0 APC) — DESK-REJECTED

- **Submitted:** 2026-05-17 (Editorial Manager).
- **Manuscript ID:** BSPC-D-26-08373.
- **Decision:** **Desk-rejected (editorial pre-screen).**
- **Decision date:** 2026-05-22.
- **Executive Editor:** Prof. Lisheng Xu, PhD.
- **Rejection text:** Generic Elsevier pre-screening boilerplate ("threshold for acceptance is high...we have to pre-screen all submissions to determine its fitting to BSPC"). No reviewer comments, no specific scope objection.
- **Diagnosis:** Scope mismatch. 2026-05-17 scout had flagged scope match 22/30 (vs PMEA 28/30, ABE 26/30). BSPC won the overall ranking on Q1 quartile (+25 pts) and ~40-50% acceptance rate. Editorial pre-screen rejected on scope alignment alone, ignoring the ranking score. Calibration event for the journal-scout v2.4.0 rubric overhaul (2026-05-22).
- **Archive:** `manuscripts/_archive/bspc/` (full submission tree + `REJECTION.md` with verbatim Xu email text). Move from `manuscripts/bspc/` to `manuscripts/_archive/bspc/`.

---

## Fallback ladder (if PMEA desk-rejects or major-revisions in a way that doesn't suit)

Pre-vetted by the 2026-05-22 Q2/Q3 scope-strict fallback ladder (`docs/publication/2026-05-22_journal-scout_cgem-q2-q3-fallback.md`). Q2/Q3 only, $0 APC subscription only, scope ≥ 25/30 hard floor — no more Q1 chasing. Listed in recommended order:

| Rank | Journal | Publisher | Q | APC | Soft cap | Scope match | Why next |
|---:|---|---|---|---|---|---:|---|
| 1 | **Annals of Biomedical Engineering** (ABE) | Springer / BMES | Q2 biomed eng | $0 hybrid sub | 10,000 words | 26/30 | Scope clause explicitly endorses "the development of theory and of mathematical models." ~3-week median first decision. 10,000-word headroom. Triple WoS SCIE / Scopus / PubMed indexing. Use `manuscripts/abe/` packaging mirroring `manuscripts/pmea/` pattern; file OSF amendment for venue change. |
| 2 | **Medical & Biological Engineering & Computing** (MBEC) | Springer / IFMBE | Q2 biomed eng | $0 hybrid sub | ~ 6,000 words | 26/30 | **6-day median submission-to-first-decision** — fastest in the entire CGEM scout history. Four-category WoS SCIE coverage (incl. Mathematical & Computational Biology). IFMBE society backing. Springer Editorial Manager portal. |
| 3 | **Bulletin of Mathematical Biology** (BMB) | Springer | Q2 (Comp Theo & Math) / Q1 (Math-misc) | $0 hybrid sub | (verify at venue) | 24/30 | Tier-2 (scope 1 pt below the ≥ 25/30 floor). Use only if both ABE and MBEC reject. `bmb-submit` skill exists in workspace → packaging cost ~ hours. Mitigation: rewrite intro to lead with biological-insight framing. |

**Hard exclusions (do NOT re-shop):**
- IJNMBE (Wiley) — desk-rejected on categorical scope policy.
- BSPC (Elsevier) — desk-rejected on scope; calibration event for the ≥ 25/30 floor.
- CMPB (Elsevier) — abandoned 2026-05-17 on word-cap mismatch; would require a major-revision rebuild before retry.
- AMHP (ASMA) — denylisted in `~/.hermes/skills/journal-scout/AI_POLICY_FILTER.md` § 4 after the 2026-05-08 Newman desk-rejection on declared AI use.
- Computers in Biology and Medicine (Elsevier) — WoS Core (SCIE) removed 2024-11-17.
- PLOS Computational Biology — Gold OA $3,165, fails $0 APC constraint.
- Medical Engineering & Physics (Elsevier → IPEM/IOP) — transition-year editorial pipeline disrupted; re-evaluate post-2026.
- IEEE TBME / IEEE JBHI / J. Royal Soc. Interface — all Q1, fail Q2/Q3 cut per 2026-05-22 user directive.

---

## Updating this log

When PMEA delivers a decision:
- **Acceptance / Minor revisions:** add a new "Attempt 4 — outcome" subsection under Submission history. Update Current status. Optionally close this log.
- **Major revisions:** record the decision under Attempt 4 with reviewer-comment summary; add an "Attempt 4 revision" subsection when the revision is submitted.
- **Desk rejection or hard rejection:** move "PMEA" to the Submission history; start "Attempt 5 — ABE" under Current status (or whichever venue is next per the fallback ladder); rebuild the submission package in `manuscripts/abe/` mirroring the `manuscripts/pmea/` pattern; file a new OSF venue-change amendment in `docs/publication/`.

The auto-memory entries at `~/.claude/projects/-root-repos-CAMI-Gz-Effects-Model-CGEM-/memory/` mirror this log at the per-Claude-session level — they should be updated in parallel with this file.

---

## Cross-references

- IJNMBE archive: `manuscripts/_archive/ijnmbe/`
- BSPC archive: `manuscripts/_archive/bspc/`
- PMEA working tree: `manuscripts/pmea/`
- PMEA guidelines audit (source of truth for PMEA formatting): `docs/publication/2026-05-22_pmea_guidelines_audit.md`
- Q2/Q3 post-PMEA fallback ladder: `docs/publication/2026-05-22_journal-scout_cgem-q2-q3-fallback.md`
- OSF venue-change amendment 1 (IJNMBE → BSPC): `docs/publication/osf_amendment_2026-05-17.md`
- OSF venue-change amendment 2 (BSPC → PMEA): `docs/publication/osf_amendment_2026-05-22.md`
- CMPB pivot spec: `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`
- Journal-scout reports: `docs/publication/2026-05-{12,17,22}_journal-scout_cgem-*.md`
- Skill bug record: `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`
