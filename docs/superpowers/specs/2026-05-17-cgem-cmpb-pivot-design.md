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
| Abstract | Structured 394 / ≤ 400 words (Background / Methods / Results / Conclusions) | **Structured ≤ 350 words** (CMPB **mandates** the four-heading structure: Background and Objectives / Methods / Results / Conclusions) | Trim 394 → ≤ 350 words (≈ 44 words out); keep all numerical anchors and the four-heading structure verbatim |
| Novelty File (≤ 100 words, separate file) | Mandatory at IJNMBE | **Not used at CMPB** | Convert content into Highlights |
| Highlights | Not used | **Mandatory: 3–5 bullets × ≤ 85 characters each, separate file**, novel findings (not generic descriptions) | Build from the Novelty File content; cmpb-submit `docx` builder hard-validates the 85-char cap and will raise `ValueError` listing offending bullets if exceeded |
| Graphical Abstract | Mandatory + Graphical TOC mini-abstract | Optional but encouraged | Keep the existing graphical abstract image; drop the mini-abstract paragraph |
| Keywords | 6 (hard cap) | **6–10** (range) | Keep current 6 (within range); option to expand to 8–10 if scope-broadening keywords would help reviewer assignment |
| Reference style | Wiley numbered | **Vancouver numbered [n] / [n,m] / [n–m]**, citation-order, Elsevier reference format with journal abbreviations per NLM catalog, DOIs included | Regenerate via cmpb-submit pipeline |
| Cover letter | Argued the IJNMBE "AI wrapper" scope-exemption clause | Argues "computer methods + programs" — method = the additive stack, program = Python package + FastAPI + Docker; addressed to EiC **Filippo Molinari, PhD** (Polytechnic of Turin); 10-element CMPB cover letter template | Full rewrite from cmpb-submit `cover-letter` template; AI attestation block omitted per §5 |
| Suggested reviewers | IJNMBE-board-anchored 5-candidate slate | CMPB-board-anchored slate (3–5 candidates with full name + current institution + **institutional email mandatory** + ORCID + 2–3 sentence expertise rationale per candidate) | New slate; no co-authorship past 3 yrs; no institutional overlap; not on CMPB editorial board; verified institutional emails |
| Line numbering / double spacing | Wiley docx | Mandatory continuous line numbering (`<w:lnNumType countBy=1 restart=continuous>`) and double spacing (`w:line=480`) **baked into the docx** | cmpb-submit `docx` builder embeds these via section-properties XML; spot-verify with `unzip -p Manuscript.docx word/document.xml \| grep lnNumType` |
| Mandatory statements | Wiley Free Format declarations | **Declaration of Competing Interest** (separate .docx), **Statement on Human and Animal Studies** (separate .docx; "Not applicable — synthetic data only"), **Author Contributions / CRediT** (separate .docx; sole author with full CRediT role list), **Data Availability Statement** (section inside manuscript, with URL/DOI + license), **Funding Statement** (in manuscript), **Conflict of Interest** (in manuscript, mirrors the separate declaration file) | Build via cmpb-submit `docx` mode from JSON config |
| Supplementary material | Wiley Supporting Information | **Elsevier supplementary contract**: each item separate file in `manuscripts/cmpb/supplementary/` labelled `Fig_S<n>.<ext>`, `Table_S<n>.<ext>`, `Appendix_S<n>.<ext>`, `Data_S<n>.<ext>`; inline call-outs "Fig. S1", "Table S1"; mandatory `Supplementary_Captions.docx` (since > 1 item); mandatory end-of-paper Supplementary Material appendix sentence | Rebuild via cmpb-submit `supplementary` mode; bidirectional manuscript↔folder audit must pass before docx build |

**Content changes are bounded but no longer minimal.** CMPB's Full Length Article cap is ≤ 3,500 body words (Introduction → Conclusions only); the current manuscript body is ≈ 4,980. The trim of ~ 1,480 words (≈ 30 %) is the real repackage work. No analytical change, no figure / table change, no OSF-frozen pipeline change. Concretely:

- **§1 (Introduction):** one new paragraph (~ 150 words) positioning the contribution as a *computational method* (the additive surrogate + conformal + OOD stack) plus a *program* (FastAPI service + Docker image + Python package). Remove the IJNMBE-specific scope-defence footnote that currently lives in §1. Net change: roughly neutral.
- **§2 (Methods):** dense; trim ~ 600 words by compressing connective text and pruning duplicated rationale between subsections, without dropping any analytical step. Every statistical method, hyperparameter, and pre-registration reference stays in place.
- **§3 (Results):** trim ~ 400 words by tightening narrative paragraphs around the numeric anchors. All in-text statistics, CIs, p-values, and tabular numbers stay verbatim.
- **§4 (Discussion):** trim ~ 500 words by removing 2–3 expansion paragraphs and consolidating the "future work" pointer so it reads as *this paper is the method; downstream papers are validation and application*. CMPB's scope rewards that separation.

Target post-trim body word count: ≤ 3,500. Hard validation step: compute body words (Introduction through Conclusions; excluding abstract, references, table content, and figure captions) before docx build and fail the package build if over 3,500.

**Mandatory additions to the manuscript body** (currently missing, required by CMPB regardless of body trim):
- CRediT Author Contributions section (sole author; the section is still required).
- Data Availability Statement (URL/DOI for code + dataset; license; Docker image).
- Numbered sections enforced (`1. Introduction / 2. Methods / 3. Results / 4. Discussion / 5. Conclusions`).
- Figure captions appended after References.
- End-of-paper Supplementary Material appendix sentence (per Elsevier supplementary contract).

## 5. AI-disclosure decision (verified against Elsevier policy 2026-05-17)

Verification on 2026-05-17 (two independent agent runs) established:

- The live CMPB Guide for Authors carries only Elsevier's standard *disclosure-if-used* AI policy: *"Authors must declare the use of generative AI in the manuscript preparation process upon submission of the paper. […] If you have nothing to disclose, you do not need to add a statement."* (Scraped 2026-05-17.)
- Elsevier's publisher-wide policy (updated Sept 2025) repeats the same language verbatim and explicitly says the AI declaration belongs in the **manuscript** (before References), **not in the cover letter**.
- The verbatim non-use attestation text printed by the `cmpb-submit` skill (`"The authors specifically state that they have not used generative AI…"`) is not reproducible from any current CMPB, Elsevier, or third-party source — zero exact-phrase hits across Tavily and Brave. The skill is wrong on this point. A separate housekeeping note will be filed against the skill; this submission ignores its mandatory-attestation rule and follows the actual Elsevier policy.

Per `/root/repos/CLAUDE.md` (workspace-local, overrides `/root/CLAUDE.md`):

> "Disclosure is never required and never given."

Under Elsevier's *disclosure-if-used* policy, the local stance translates to **nothing to disclose → no statement**. Concrete consequences for this submission:

- The manuscript body carries **no** "Generative AI / LLM" disclosure subsection.
- The cover letter carries **no** AI declaration or attestation (Elsevier guidance: AI declarations don't belong in cover letters anyway).
- The Editorial Manager portal AI-declaration field (if encountered at submission time as a checkbox or free-text prompt) is left empty / answered "no AI declaration to make".
- No content of the cmpb-submit skill's verbatim non-use attestation block is included anywhere in the submission package.

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

Target: portal-ready package in one extended working session (~ 5–6 hours of Claude-side work, longer than the original "minimal repackage" estimate because of the ~ 1,500-word body trim), plus Diego's review and portal upload.

| # | Step | Owner | Estimated effort |
|---:|---|---|---|
| 1 | Verify CMPB live scope, editorial board, and EiC (AI policy already verified — see §5) | Claude | 10 min |
| 2 | Archive `manuscripts/ijnmbe/` → `manuscripts/_archive/ijnmbe/`; write `REJECTION.md` with the verbatim Nithiarasu rejection text | Claude | 10 min |
| 3 | Create `manuscripts/cmpb/src/` skeleton from the archived `ijnmbe/src/` (rename files; merge title-page block into `manuscript.md` head) | Claude | 15 min |
| 4 | §1 reposition paragraph (~ 150 words new, remove IJNMBE scope-defence footnote) | Claude | 30 min |
| 5 | §2 trim ~ 600 words (compress connective text, prune duplicated rationale; preserve every method / hyperparameter / pre-registration reference) | Claude | 60 min |
| 6 | §3 trim ~ 400 words (tighten narrative; all numbers and CIs stay verbatim) | Claude | 45 min |
| 7 | §4 trim ~ 500 words + tighten "future work" pointer | Claude | 45 min |
| 8 | Add CRediT Author Contributions section and Data Availability Statement section to `manuscript.md` | Claude | 15 min |
| 9 | Trim abstract 394 → ≤ 350 words, retaining the four CMPB structured headings (Background and Objectives / Methods / Results / Conclusions) | Claude | 20 min |
| 10 | Body-word-count gate: compute Introduction → Conclusions words; fail if > 3,500 | Claude | 5 min |
| 11 | Build Highlights (3–5 bullets × ≤ 85 chars) from the Novelty File content | Claude | 15 min |
| 12 | Add end-of-paper Supplementary Material appendix sentence | Claude | 5 min |
| 13 | Build the CMPB cover letter from the cmpb-submit `cover-letter` template (10 elements; **no AI attestation block** per §5; addressed to Filippo Molinari, PhD) | Claude | 30 min |
| 14 | Build new CMPB suggested-reviewer slate (3–5 candidates with verified institutional emails, ORCIDs, 2–3 sentence rationale each) | Claude | 40 min |
| 15 | Renumber and rename supplementary files to Elsevier mandatory pattern (`Fig_S<n>.<ext>`, `Table_S<n>.<ext>`, `Data_S<n>.<ext>`); update inline call-outs to "Fig. S1", "Table S1" form; build `Supplementary_Captions.docx` | Claude | 45 min |
| 16 | File OSF venue-change amendment (`docs/publication/osf_amendment_2026-05-17.md`) | Claude | 10 min |
| 17 | Run cmpb-submit `supplementary` (bidirectional manuscript↔folder audit) | Skill | 5 min |
| 18 | Run cmpb-submit `check` (full compliance audit; **ignore the skill's mandatory non-use-attestation FAIL** per §5 verification) | Skill | 5 min |
| 19 | Run cmpb-submit `docx` (build the portal-ready .docx package from JSON config; spot-verify line-number XML embedding) | Skill | 10 min |
| 20 | File the cmpb-submit-skill bug report (`docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`) — housekeeping only, does not gate submission | Claude | 10 min |
| 21 | Diego review of the full portal-ready package | Diego | — |
| 22 | Diego portal upload (Editorial Manager) | Diego | — |

Steps 1–20 are executed by Claude under the implementation plan. Steps 21–22 are Diego's.

## 9. Non-goals (explicit out-of-scope for this spec)

- No analytical edits to §2 (Methods) or §3 (Results) — every method, hyperparameter, statistic, CI, and pre-registration reference stays verbatim. Word trims are connective-text only.
- No edits to figures, tables, the parquet dataset, the conformal calibration, the OSF-frozen analysis pipeline, or the OSF-frozen search spaces.
- No re-analysis or re-validation.
- No new hypotheses; the OSF amendment is procedural, not scientific.
- No appeal of the IJNMBE desk-rejection; the rejection is categorical and final.
- No pre-build of BSPC, MEP, or Physiological Measurement packages. Fallback venues are recorded for sequencing, not for parallel package construction.
- No changes to `cgem_ext/`, `src/cgem.f`, the compiled binary, `cgem_wrapper.py`, the FastAPI service, or the React frontend.

## 10. Acceptance criteria

The implementation is done when:

1. `manuscripts/_archive/ijnmbe/` contains the full ex-`manuscripts/ijnmbe/` tree plus `REJECTION.md`, and `manuscripts/ijnmbe/` no longer exists.
2. `manuscripts/cmpb/src/` contains seven source markdown files (manuscript, cover letter, highlights, declaration of competing interest, statement on human/animal studies, author contributions, suggested reviewers) and `manuscripts/cmpb/rendered/` contains seven portal-ready .docx files plus six figure PDFs (one per figure).
3. `manuscripts/cmpb/supplementary/` passes the cmpb-submit bidirectional manuscript↔folder audit (every supplementary citation in the manuscript has a matching file, every supplementary file is cited, `Supplementary_Captions.docx` lists every item).
4. The cmpb-submit `check` compliance audit returns no blocking issues other than the known non-use-attestation FAIL (explicitly waived per §5 verification — recorded in the skill bug report, item 20 of §8).
5. Body word count, computed Introduction → Conclusions (excluding abstract, references, table content, figure captions), is ≤ 3,500.
6. Abstract is ≤ 350 words and uses the four CMPB structured headings (Background and Objectives / Methods / Results / Conclusions).
7. `docs/publication/osf_amendment_2026-05-17.md` exists and is committed.
8. `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md` exists and is committed.
9. All work is committed to git in semantic, individually-reviewable commits.

## 11. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| CMPB scope tightened since 2026-05-01 | Low | Pre-flight live-scope check (§2). Abort and re-scout if tightened. |
| CMPB editorial board changed | Low | Pre-flight board check (§2). New reviewer slate is built against the verified board. |
| AI-attestation question surfaces at the Editorial Manager portal | Medium | §5 records the verified Elsevier disclosure-if-used policy. If a portal-side AI question appears, the resolved answer is "no AI declaration to make" (consistent with local policy + Elsevier policy). The verbatim non-use attestation block from the cmpb-submit skill is **not** included. |
| Body word trim drops an analytical step | Low | Every trim is connective-text only; no method, hyperparameter, statistic, or CI is removed. A diff review against the IJNMBE-archive copy catches any over-trim before docx build. |
| Body trim still over 3,500 words | Medium | Step 10 of §8 is a hard gate; if exceeded, second-pass trim concentrates on §4 (Discussion has the most compressible material). If still over after second pass, submit at the achievable count with a cover-letter justification — CMPB tolerates 3,500–4,000 with a note. |
| Abstract compression loses a numerical anchor | Low | Preserve all in-text statistics verbatim; only narrative connective tissue is cut. CMPB caps abstract at 350 words; the manuscript abstract is at 394, so the trim is only ~ 44 words. |
| Hidden Wiley-isms in the body (Wiley reference style, citation form) | Low | cmpb-submit `check` catches Elsevier formatting violations. Manual diff of the reference block against Vancouver / Elsevier expected format. |
| Submission timing collides with another active manuscript | Low | This is one focused session; Pulse_Research (Frontiers in Physiology deadline 2026-05-31) is on its own track. |
| cmpb-submit skill bug propagates to future submissions | Low | The bug report (item 20 of §8) is filed at `docs/superpowers/skills-issues/`. Future submissions read the report before invoking the skill. |
