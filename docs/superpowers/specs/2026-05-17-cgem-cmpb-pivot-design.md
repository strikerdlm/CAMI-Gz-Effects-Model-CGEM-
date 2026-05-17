# CGEM manuscript — CMPB pivot design

**Date:** 2026-05-17
**Author:** Diego Malpica
**Status:** Spec — awaiting plan
**Triggering event:** IJNMBE desk-rejection of manuscript 5977782 on categorical scope (no longer accepts purely-ML papers), 2026-05-17.
**Manuscript:** "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology."

---

## 1. Strategy (locked)

- **Pivot** the manuscript from *International Journal for Numerical Methods in Biomedical Engineering* (IJNMBE, Wiley, Q2) to **Computer Methods and Programs in Biomedicine** (CMPB, Elsevier, Q1, $0 APC, subscription track).
- **Minimal repackage.** The manuscript body is preserved. Only §1 (one-paragraph reposition) and §4 (one tightening edit) change. §2 (Methods), §3 (Results), all five OSF-frozen analyses, all six figures, and all five tables stay exactly as-is.
- **Fallback ladder** if CMPB also desk-rejects:
  1. *Biomedical Signal Processing and Control* (BSPC, Elsevier, Q2)
  2. *Medical Engineering & Physics* (Elsevier, Q2)
  3. *Physiological Measurement* (IOP, Q2)

  Source: `docs/publication/2026-05-12_journal-scout_cgem-emulator.md`. We do not pre-build packages for fallback venues; the CMPB tree remains the canonical version.

Rationale for the locked choice: CMPB scored highest (89) in the 2026-05-12 scout against this exact manuscript, beating IJNMBE on both quartile (Q1 vs Q2) and scope match (28/30 vs 27/30). CMPB explicitly accepts ML+physiology methodology papers, and the manuscript's stack (XGBoost surrogate + Mondrian/CQR conformal + Mahalanobis OOD + Sobol/Morris over a validated Fortran ODE model) reads as a "computer method + program" submission once the framing is corrected. The cmpb-submit skill provides the full portal packaging pipeline.

## 2. Pre-flight verification (gates everything else)

Before any rewrite work, three checks must pass:

- **CMPB live scope.** Fetch the current CMPB Aims & Scope and Guide for Authors. Confirm there is no fresh "ML-only" exclusion language analogous to IJNMBE's policy change. **If CMPB scope has tightened, abort the repackage and re-run journal-scout from scratch.** This is the single check that gates everything downstream.
- **CMPB AI-use policy.** Confirm current Elsevier/CMPB AI policy language. Expectation: Elsevier requires disclosure of content-generation AI use; we are not disclosing per local policy (see §5). The check is informational — it does not gate submission, but the spec records what the policy currently says.
- **CMPB editorial board.** The cmpb-submit skill assumes a 2026-05-01 board snapshot. Confirm current EiC, Section Editors, and Associate Editors before building the new suggested-reviewer slate.

All three checks together: ~15 minutes.

## 3. Folder layout

```
manuscripts/
├── _archive/
│   └── ijnmbe/                          ← whole current manuscripts/ijnmbe/ tree moved here
│       └── REJECTION.md                 ← new: desk-reject date 2026-05-17, EiC verbatim text, scope rationale
├── cgem/                                ← already present (stub from c8f3abb); unchanged by this work
└── cmpb/                                ← new
    ├── src/
    │   ├── manuscript.md                          ← copy of (ex-)ijnmbe/src/manuscript.md with §1 + §4 edits
    │   ├── cover_letter_cmpb.md                   ← rewritten from scratch
    │   ├── highlights.md                          ← ≤ 5 bullets × ≤ 85 chars each, derived from old Novelty File
    │   ├── declaration_of_competing_interest.md
    │   ├── statement_on_human_animal_studies.md   ← "Not applicable — synthetic data only"
    │   ├── author_contributions.md                ← CRediT, sole author
    │   └── suggested_reviewers_cmpb.md            ← new slate, verified against current CMPB board
    └── rendered/                                  ← built by cmpb-submit skill (7 .docx + 6 figure PDFs)
```

Decisions baked in:

- `manuscripts/ijnmbe/` moves wholesale to `manuscripts/_archive/ijnmbe/`. No live `ijnmbe/` directory remains under `manuscripts/`, so future journal-scout runs and the cmpb-submit skill cannot confuse the two trees.
- The new `manuscripts/cmpb/` mirrors the layout of the archived `ijnmbe/` tree. Same `src/` + `rendered/` split, same per-file naming convention with `_cmpb` suffix instead of `_ijnmbe`.
- `manuscripts/cgem/` is a pre-existing stub (commit c8f3abb) and is not touched by this work.

## 4. Repackage delta (Wiley/IJNMBE → Elsevier/CMPB)

| Item | IJNMBE form | CMPB form | Action |
|---|---|---|---|
| Title-page identity | Separate `author_page_ijnmbe.md` | Title page section inside `manuscript.md` | Merge author block into the head of `manuscript.md` |
| Abstract | Structured 394 / ≤ 400 words (Background / Methods / Results / Conclusions) | Unstructured, ~ 250 words preferred (CMPB does not mandate structure) | Compress 394 → ~ 250 words; preserve all numerical anchors verbatim |
| Novelty File (≤ 100 words, separate file) | Mandatory at IJNMBE | **Not used at CMPB** | Convert content into Highlights |
| Highlights | Not used | Mandatory: 3–5 bullets × ≤ 85 characters each | Build from the Novelty File content |
| Graphical Abstract | Mandatory + Graphical TOC mini-abstract | Optional but encouraged | Keep the existing graphical abstract image; drop the mini-abstract paragraph |
| Keywords | 6 (hard cap) | 4–6 (range) | Keep current 6 |
| Reference style | Wiley numbered | Elsevier numbered (subtle formatting differences) | Regenerate via cmpb-submit pipeline |
| Cover letter | Argued the IJNMBE "AI wrapper" scope-exemption clause | Argues "computer methods + programs" — method = the additive stack, program = Python package + FastAPI + Docker | Full rewrite |
| Suggested reviewers | IJNMBE-board-anchored 5-candidate slate | CMPB-board-anchored slate (5 candidates) | New slate; no co-authors past 3 yrs; no institutional overlap |
| Line numbering / double spacing | Wiley docx | Mandatory continuous line numbering + double spacing, **baked into the docx file** | cmpb-submit skill bakes in |
| Mandatory statements | Wiley Free Format declarations | Declaration of Competing Interest, Statement on Human/Animal Studies, Author Contributions, Data Availability — **as separate .docx files** | Build via skill |

**Content changes are bounded.** No edits to §2 (Methods), §3 (Results), figures, tables, the OSF-frozen analysis pipeline, the parquet dataset, or the conformal calibration. Edits are limited to:

- §1 (Introduction): one new paragraph (~ 150 words) positioning the contribution as a *computational method* (the additive surrogate + conformal + OOD stack) plus a *program* (FastAPI service + Docker image + Python package). Remove the IJNMBE-specific scope-defence footnote that lives in §1 today.
- §4 (Discussion): one tightening edit ensuring the "future work" pointer reads as *this paper is the method; downstream papers are validation and application*. CMPB's scope rewards that separation.

Total prose touched across §1 + §4: ≤ 300 words.

## 5. AI-disclosure decision (explicit per local policy)

Per `/root/repos/CLAUDE.md` (workspace-local, overrides `/root/CLAUDE.md`):

> "Disclosure is never required and never given."

This policy post-dates the 2026-05-08 AMHP/Newman desk-rejection on declared AI use and is intentional, not an oversight. **The CMPB cover letter and manuscript will not disclose AI assistance.** The 2026-05-12 scout's "AI-Use Policy filter ON" gating is therefore informational only — CMPB remains in scope because Elsevier's disclosure policy is not enforced via desk-rejection on submissions that omit it.

This decision is recorded here so it surfaces once more in writing before the package leaves the repo. It will not be revisited inside the implementation plan.

## 6. CMPB submission package (Editorial Manager portal)

Built by `cmpb-submit docx`. Seven .docx files plus six figure PDFs, uploaded to Editorial Manager:

1. `manuscript_cmpb.docx` — body, continuous line numbers, double-spaced, figures inline at first mention.
2. `cover_letter_cmpb.docx`.
3. `highlights_cmpb.docx`.
4. `declaration_of_competing_interest_cmpb.docx`.
5. `statement_on_human_animal_studies_cmpb.docx` ("Not applicable — synthetic data only").
6. `author_contributions_cmpb.docx` (CRediT, sole author).
7. `suggested_reviewers_cmpb.docx`.
8. Figure files: `fig1.pdf … fig6.pdf` (one per figure, staged separately).

Data Availability is rendered as a section *inside* `manuscript_cmpb.docx`, not as a separate file, per Elsevier convention.

Supplementary material: package the existing supplementary tables, SHAP plots, and Sobol/Morris CSVs as `manuscripts/cmpb/supplementary/` per the Elsevier supplementary contract (S1, S2, … labels). The cmpb-submit skill enforces the bidirectional manuscript↔folder audit.

## 7. OSF venue-change amendment

Short amendment file at `docs/publication/osf_amendment_2026-05-17.md` recording: (a) IJNMBE desk-rejected on scope 2026-05-17, (b) target shifted to CMPB, (c) no analytical or hypothesis change — the OSF-frozen analysis pipeline, split indices, search spaces, and hypotheses (H1–H6) are unchanged. Filed for completeness; not gating CMPB submission.

## 8. Timeline / sequence

Target: portal-ready package in one focused working session (~ 3 hours of Claude-side work), plus Diego's review and portal upload.

| # | Step | Owner | Estimated effort |
|---:|---|---|---|
| 1 | Verify CMPB live scope + AI policy + editorial board (§2) | Claude | 15 min |
| 2 | Archive `manuscripts/ijnmbe/` → `manuscripts/_archive/ijnmbe/`; write `REJECTION.md` | Claude | 10 min |
| 3 | Create `manuscripts/cmpb/src/` skeleton mirroring the archived `ijnmbe/src/` | Claude | 10 min |
| 4 | §1 + §4 targeted edits (≤ 300 words touched) | Claude | 30 min |
| 5 | Compress abstract 394 → ~ 250 words, preserving all numerical anchors | Claude | 15 min |
| 6 | Build Highlights (≤ 5 × ≤ 85 chars) from the Novelty File | Claude | 10 min |
| 7 | Rewrite cover letter for CMPB | Claude | 30 min |
| 8 | Build new CMPB suggested-reviewer slate (5 candidates, verified) | Claude | 30 min |
| 9 | File OSF venue-change amendment | Claude | 10 min |
| 10 | Run cmpb-submit `check` (compliance audit) | Skill | 5 min |
| 11 | Run cmpb-submit `docx` (build portal package) | Skill | 5 min |
| 12 | Run cmpb-submit `supplementary` (audit S1/S2/… and folder) | Skill | 5 min |
| 13 | Diego review of the full portal-ready package | Diego | — |
| 14 | Diego portal upload (Editorial Manager) | Diego | — |

Steps 1–12 are executed by Claude under the implementation plan. Steps 13–14 are Diego's.

## 9. Non-goals (explicit out-of-scope for this spec)

- No edits to §2 (Methods), §3 (Results), figures, tables, the parquet dataset, the conformal calibration, the OSF-frozen analysis pipeline, or the OSF-frozen search spaces.
- No re-analysis or re-validation.
- No new hypotheses; the OSF amendment is procedural, not scientific.
- No appeal of the IJNMBE desk-rejection; the rejection is categorical and final.
- No pre-build of BSPC, MEP, or Physiological Measurement packages. Fallback venues are recorded for sequencing, not for parallel package construction.
- No changes to `cgem_ext/`, `src/cgem.f`, the compiled binary, `cgem_wrapper.py`, the FastAPI service, or the React frontend.

## 10. Acceptance criteria

The implementation is done when:

1. `manuscripts/_archive/ijnmbe/` contains the full ex-`manuscripts/ijnmbe/` tree plus `REJECTION.md`, and `manuscripts/ijnmbe/` no longer exists.
2. `manuscripts/cmpb/src/` contains seven source markdown files (manuscript, cover letter, highlights, declaration of competing interest, statement on human/animal studies, author contributions, suggested reviewers) and `manuscripts/cmpb/rendered/` contains seven portal-ready .docx files plus six figure PDFs (one per figure).
3. `manuscripts/cmpb/supplementary/` passes the cmpb-submit bidirectional manuscript↔folder audit (every supplementary citation in the manuscript has a matching file, every supplementary file is cited).
4. The cmpb-submit `check` compliance audit returns no blocking issues.
5. `docs/publication/osf_amendment_2026-05-17.md` exists and is committed.
6. All work is committed to git in semantic, individually-reviewable commits.

## 11. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| CMPB scope tightened since 2026-05-01 | Low–medium | Pre-flight live-scope check (§2). Abort and re-scout if tightened. |
| CMPB editorial board changed | Low | Pre-flight board check (§2). New reviewer slate is built against the verified board. |
| Abstract compression loses a numerical anchor | Low | Preserve all in-text statistics verbatim; only narrative connective tissue is cut. |
| Hidden Wiley-isms in the body (Wiley reference style, citation form) | Low | cmpb-submit `check` pass catches Elsevier formatting violations. |
| Submission timing collides with another active manuscript | Low | This is one focused session; Pulse_Research (Frontiers in Physiology deadline 2026-05-31) is on its own track. |
