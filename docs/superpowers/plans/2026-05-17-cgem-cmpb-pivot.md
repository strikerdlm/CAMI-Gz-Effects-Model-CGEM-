# CGEM → CMPB Pivot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repackage the CGEM manuscript (currently in IJNMBE/Wiley format, desk-rejected on scope 2026-05-17) into a portal-ready CMPB submission package (Elsevier, Q1, $0 APC), with body trimmed to ≤ 3,500 words, structured ≤ 350-word abstract, Highlights, mandatory separate-file declarations, Vancouver references, line numbers and double spacing baked into the .docx, and Elsevier supplementary contract enforced.

**Architecture:** Three durable artifacts. (1) `manuscripts/_archive/ijnmbe/` preserves the rejected submission as a frozen historical record. (2) `manuscripts/cmpb/` is the new live working tree: `src/` for markdown sources, `supplementary/` for the Elsevier S-numbered package, `rendered/` for portal-ready .docx + figure PDFs produced by the cmpb-submit `docx` builder. (3) `docs/publication/osf_amendment_2026-05-17.md` records the venue change for OSF audit. The cmpb-submit skill provides the docx-build mechanics; the known non-use-attestation FAIL in `check` mode is explicitly waived per spec §5.

**Tech Stack:** Markdown (manuscript source), python-docx via the `cmpb-submit` skill's builder, pandoc as fallback for .docx generation if needed, JSON config consumed by `bin/build-cmpb-docx`. Word counts via `wc -w` after stripping the abstract, title page, references, tables, and figure captions.

**Reference documents:**
- Spec: `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`
- Scout report: `docs/publication/2026-05-17_journal-scout_cgem-emulator.md`
- cmpb-submit skill: `~/.claude/skills/cmpb-submit/SKILL.md` (skill bug — see Task 12)
- Source manuscript: `manuscripts/ijnmbe/src/manuscript.md` (will be moved to `manuscripts/_archive/ijnmbe/src/manuscript.md` in Task 1)

---

## File structure (post-plan)

```
manuscripts/
├── _archive/
│   └── ijnmbe/                               ← whole current manuscripts/ijnmbe/ tree
│       ├── REJECTION.md                       ← new
│       └── src/
│           └── manuscript.md                  ← unchanged historical record
├── cgem/                                      ← pre-existing stub from c8f3abb, not touched
└── cmpb/                                      ← new live working tree
    ├── src/
    │   ├── manuscript.md                      ← created from ijnmbe copy; §1 reposition + §2/§3/§4 trims; CRediT + Data Availability sections; end-of-paper Supplementary Material appendix
    │   ├── cover_letter_cmpb.md               ← built from cmpb-submit cover-letter template; NO AI block
    │   ├── highlights.md                      ← 3–5 bullets × ≤ 85 chars
    │   ├── declaration_of_competing_interest.md
    │   ├── statement_on_human_animal_studies.md ← "Not applicable — synthetic data only"
    │   ├── author_contributions.md            ← CRediT, sole author (mirror of manuscript section)
    │   └── suggested_reviewers_cmpb.md        ← 3–5 candidates with verified institutional emails
    ├── supplementary/                         ← Elsevier supplementary contract
    │   ├── Fig_S1.pdf                         ← renamed from existing fig_s1_shap_*
    │   ├── …
    │   ├── Table_S1.docx
    │   ├── Data_S1.csv
    │   └── Supplementary_Captions.docx
    └── rendered/                              ← cmpb-submit docx output
        ├── manuscript_cmpb.docx               ← line numbers + double spacing baked in
        ├── cover_letter_cmpb.docx
        ├── highlights_cmpb.docx
        ├── declaration_of_competing_interest_cmpb.docx
        ├── statement_on_human_animal_studies_cmpb.docx
        ├── author_contributions_cmpb.docx
        ├── suggested_reviewers_cmpb.docx
        └── fig1.pdf … fig6.pdf                ← one figure per file
docs/
├── publication/
│   ├── osf_amendment_2026-05-17.md            ← new (venue change record)
│   └── 2026-05-17_journal-scout_cgem-emulator.md ← already committed
└── superpowers/
    ├── specs/
    │   └── 2026-05-17-cgem-cmpb-pivot-design.md ← already committed
    ├── plans/
    │   └── 2026-05-17-cgem-cmpb-pivot.md      ← this file
    └── skills-issues/
        └── 2026-05-17-cmpb-submit-attestation-bug.md ← new
```

---

## Task 1: Archive the IJNMBE submission

**Files:**
- Move: `manuscripts/ijnmbe/` → `manuscripts/_archive/ijnmbe/`
- Create: `manuscripts/_archive/ijnmbe/REJECTION.md`

- [ ] **Step 1.1: Create the `_archive/` parent directory**

```bash
mkdir -p manuscripts/_archive
```

- [ ] **Step 1.2: Move the IJNMBE tree wholesale**

```bash
git mv manuscripts/ijnmbe manuscripts/_archive/ijnmbe
```

Using `git mv` preserves history.

- [ ] **Step 1.3: Write the REJECTION.md**

Create `manuscripts/_archive/ijnmbe/REJECTION.md` with this content:

````markdown
# IJNMBE Submission — Desk-Rejection Record

**Manuscript ID:** 5977782
**Title:** Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology
**Author:** Diego Malpica, MD (sole)
**Submitted:** 2026-05-12 (Wiley CNM portal)
**Decision:** Desk-rejection — out of scope
**Decision date:** 2026-05-17
**Editor-in-Chief signing:** Prof. Perumal Nithiarasu, Swansea University

## Verbatim rejection text

> Thank you for submitting your manuscript 5977782, titled "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology", to our journal. After careful assessment, we have made the decision not to consider your manuscript for publication in International Journal for Numerical Methods in Biomedical Engineering.
>
> We appreciate you considering International Journal for Numerical Methods in Biomedical Engineering for the publication of your research.
>
> Kind regards,
> Dr. P. Nithiarasu
>
> Thank you for submitting your manuscript to the International Journal for Numerical Methods in Biomedical Engineering. After careful consideration, we regret to inform you that the work falls outside the scope of the journal.
>
> We encourage you to review the journal's aims and scope before considering any future submissions to ensure a strong alignment with the topics covered by IJNMBE.

## Rationale (per IJNMBE updated Aims and Scope, as cited in the rejection email)

> International Journal for Numerical Methods in Biomedical Engineering is no longer accepting submissions based purely on machine and deep learning methods applied to biomedical problems.
>
> However, using these methods to solve differential equations or to accelerate numerical methods is within the scope.

The categorical scope change is final; appeal is not viable. CGEM moved to CMPB per `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`.

## Why this submission is preserved

This folder is the frozen IJNMBE submission as packaged 2026-05-12, retained for: (a) historical record, (b) future scope-defence reference if any IJNMBE-Lab variant relaxes the policy, (c) cross-reference for the CMPB cover letter (the IJNMBE rejection establishes precedent for the manuscript's reception at one sibling journal). Do not modify any file under this directory.
````

- [ ] **Step 1.4: Verify the archive structure**

```bash
ls -la manuscripts/_archive/ijnmbe/ | head -5
test -f manuscripts/_archive/ijnmbe/REJECTION.md && echo "REJECTION.md present"
test -d manuscripts/ijnmbe && echo "ERROR: original ijnmbe/ still exists" || echo "OK: original ijnmbe/ moved"
```

Expected output: REJECTION.md present, OK: original ijnmbe/ moved.

- [ ] **Step 1.5: Commit**

```bash
git add manuscripts/_archive/ijnmbe/REJECTION.md
git add manuscripts/_archive/ijnmbe/  # picks up the rename
git commit -m "$(cat <<'EOF'
archive(ijnmbe): freeze IJNMBE submission after 2026-05-17 desk-rejection

Move the entire manuscripts/ijnmbe/ tree to manuscripts/_archive/ijnmbe/.
Preserve git history via git mv. Add REJECTION.md with the verbatim
Nithiarasu desk-rejection text and rationale (IJNMBE updated Aims and
Scope no longer accepts purely-ML papers on biomedical problems).

The archive is a frozen historical record; do not modify. CGEM moves
to CMPB per docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md.
EOF
)"
```

---

## Task 2: Scaffold the CMPB working tree

**Files:**
- Create: `manuscripts/cmpb/src/`, `manuscripts/cmpb/supplementary/`, `manuscripts/cmpb/rendered/`
- Create: `manuscripts/cmpb/src/manuscript.md` (initial copy from archive)
- Create: `manuscripts/cmpb/.gitkeep` for empty dirs as needed

- [ ] **Step 2.1: Create the directory tree**

```bash
mkdir -p manuscripts/cmpb/src manuscripts/cmpb/supplementary manuscripts/cmpb/rendered
```

- [ ] **Step 2.2: Seed manuscript.md from the archived IJNMBE copy**

```bash
cp manuscripts/_archive/ijnmbe/src/manuscript.md manuscripts/cmpb/src/manuscript.md
```

This is the working copy; all subsequent body edits land here. The archive copy stays untouched.

- [ ] **Step 2.3: Verify**

```bash
test -f manuscripts/cmpb/src/manuscript.md && wc -w manuscripts/cmpb/src/manuscript.md
```

Expected: roughly 10,472 words total (includes title page, abstract, references — body alone is ~ 4,980).

- [ ] **Step 2.4: Commit**

```bash
git add manuscripts/cmpb/
git commit -m "scaffold(cmpb): seed manuscripts/cmpb/ from archived IJNMBE source"
```

---

## Task 3: Strip the IJNMBE-specific title-page block from the working manuscript

The current `manuscript.md` opens with an IJNMBE target-venue header, word-count notes referencing IJNMBE, and a "Mandatory separate files at IJNMBE" line. These do not belong in a CMPB submission.

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md` (lines 1–17)

- [ ] **Step 3.1: Read the current top of the manuscript**

```bash
sed -n '1,20p' manuscripts/cmpb/src/manuscript.md
```

- [ ] **Step 3.2: Replace lines 1–17 with the CMPB title block**

Use Edit to replace the entire IJNMBE-target header (from the title line through the "CMPB Highlights file" note) with the CMPB title block. The new top of the file:

```markdown
# Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology

**Author.** Diego Malpica, MD. Direction of Aerospace Medicine, Aerospace Scientific Department, Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC), Bogotá, Colombia. ORCID 0000-0002-2257-4940. Correspondence: dlmalpica@yahoo.com.

**Article type.** Full Length Article.

**Running title** (≤ 70 chars). Conformal ML wrapper for a validated ODE physiological model.

---
```

The old IJNMBE-target paragraph, the "Word count / Abstract word count / Tables / Figures / References" pre-amble lines, and the "Mandatory separate files at IJNMBE" / "CMPB Highlights file" lines are deleted. The body starts at the Abstract heading immediately after the horizontal rule.

- [ ] **Step 3.3: Verify the top is clean**

```bash
sed -n '1,12p' manuscripts/cmpb/src/manuscript.md
```

Expected: title line, author line, article-type line, running-title line, then `---`.

- [ ] **Step 3.4: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "fix(cmpb): replace IJNMBE title-page block with CMPB header"
```

---

## Task 4: Trim and re-stamp the abstract (394 → ≤ 350, four CMPB headings)

CMPB requires the structured form: **Background and Objectives / Methods / Results / Conclusions** — these exact headings, ≤ 350 words total. The current abstract uses "Background and Objectives / Methods / Results / Conclusions" already (matching), but is at 394 words. Trim ~ 44 words by tightening connective text without dropping any numerical anchor.

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md` (the Abstract section)

- [ ] **Step 4.1: Read the current abstract**

```bash
awk '/^## Abstract/,/^---$/' manuscripts/cmpb/src/manuscript.md
```

- [ ] **Step 4.2: Trim each abstract section**

Edit each of the four heading-paragraphs in the Abstract:

- **Background and Objectives.** Compress "underpins civil-aviation regulatory practice" + "computationally expensive, provides no calibrated uncertainty quantification, and accepts out-of-distribution (OOD) inputs without warning" into a tighter formulation that names the three gaps. Remove the "a general pattern for wrapping any validated ODE physiological model" trailing sentence — same content appears in the Conclusions paragraph.
- **Methods.** Drop the "(pre-registered as OSF amendment H5)" parenthetical from the Mondrian-CQR sentence (the pre-registration is mentioned at the end of the paragraph instead). Compress "Per-target XGBoost surrogates used a two-stage classifier-then-regressor pattern for right-censored event-time targets and single-stage regressors for two continuous targets" → "Per-target XGBoost surrogates: two-stage classifier+regressor for right-censored event-time targets, single-stage regressors for continuous targets." Compress "A robust Mahalanobis detector with distribution-free conformal abstention guarded a 17-dimensional feature space" → "A robust Mahalanobis detector with distribution-free conformal abstention guarded the 17-feature input space." Keep "The surrogate drove Sobol and Morris sensitivity decompositions" and the pre-registration sentence verbatim.
- **Results.** Keep every number verbatim. Compress "Mondrian conformal coverage landed within 4.6 percentage points of nominal on 4 of 5 surrogate targets; on the fifth, time_to_gloc_s, the heteroscedastic CQR layer raised coverage from 0.861 to 0.972 on n = 36 event-positive test rows" by removing the explanatory "the heteroscedastic CQR layer raised coverage" — let "Mondrian-baseline coverage landed within 4.6 pp on 4/5 targets; CQR raised time_to_gloc_s coverage 0.861 → 0.972 on n = 36 event-positive test rows" do the same work in fewer words. Drop "with the 95 % bootstrap CI on time_to_gloc_s spanning [−0.055, 0.951], the regime in which the heteroscedastic CQR layer was activated" — this returns in §3.
- **External validation** (free-standing paragraph): keep verbatim. The numerical anchors (δ̄ = +26.6 s, CI, onset thresholds) are load-bearing.
- **Conclusions.** Compress "This framework preserves the FAA-validated core and adds emulator speed, calibrated prediction intervals, OOD abstention, and global sensitivity rankings" → "The framework preserves the FAA-validated core and adds emulator speed, calibrated prediction intervals, OOD abstention, and global sensitivity rankings." (drop the redundant "This" demonstrative).

- [ ] **Step 4.3: Verify abstract ≤ 350 words**

```bash
awk '/^\*\*Background and Objectives\.\*\*/,/^\*\*Keywords\*\*/{if(!/^\*\*Keywords\*\*/) print}' manuscripts/cmpb/src/manuscript.md | wc -w
```

Expected: ≤ 350. If over, second-pass trim on the Methods paragraph.

- [ ] **Step 4.4: Verify the four CMPB headings are present in the right order**

```bash
grep -nE '^\*\*Background and Objectives\.\*\*|^\*\*Methods\.\*\*|^\*\*Results\.\*\*|^\*\*Conclusions\.\*\*' manuscripts/cmpb/src/manuscript.md | head -5
```

Expected: four lines, in order.

- [ ] **Step 4.5: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "fix(cmpb): trim abstract 394 -> <=350 words, keep four CMPB headings"
```

---

## Task 5: Reposition §1 Introduction toward the CMPB "computer methods + programs" framing

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md` (the §1 Introduction section)

- [ ] **Step 5.1: Read §1 (Introduction)**

```bash
awk '/^## 1\. Introduction/,/^## 2\. Methods/' manuscripts/cmpb/src/manuscript.md
```

- [ ] **Step 5.2: Edit the §1 opening paragraph**

Replace the current §1 opening paragraph (the "Validated mechanistic models embedded in regulatory or operational frameworks pose a recurring problem in computational biomedicine…" paragraph) with a CMPB-anchored reposition.

The replacement opening paragraph:

```markdown
Validated mechanistic models embedded in regulatory or operational frameworks pose a recurring problem in computational biomedicine: they encode decades of domain knowledge and experimental calibration, yet they are computationally expensive, lack calibrated uncertainty quantification, and accept out-of-distribution inputs without warning. The aim of this paper is to propose a **computer-methods-and-programs** solution to that recurring problem: a method — the additive surrogate + conformal + OOD stack — and a program — an open Python package, FastAPI service, and Docker image — that together close the three gaps without modifying the validated core. The method generalises across any validated ODE physiological model; the program is a concrete reference implementation against the FAA Civil Aerospace Medical Institute's CGEM. Portela, Banga and Matabuena [23] recently demonstrated the wrapping pattern on canonical biological dynamical systems; the present work extends it from generic biological dynamics into a specific regulatory aerospace-physiology setting and adds three operational refinements: (i) per-stratum (Mondrian) conformal calibration over operationally meaningful maneuver categories, (ii) heteroscedastic conformal layers for long-tailed event-time targets, and (iii) an explicit input-envelope abstention layer.
```

The paragraph that previously closed §1 (the "This manuscript validates the framework against CGEM itself as ground truth…" paragraph) stays unchanged.

- [ ] **Step 5.3: Remove the IJNMBE-specific scope-defence footnote**

If `manuscript.md` contains any sentence of the form "falls within … IJNMBE scope clauses" or "verified scope clauses simultaneously", delete it. (Scan with `grep -n 'IJNMBE' manuscripts/cmpb/src/manuscript.md` first.)

- [ ] **Step 5.4: Verify**

```bash
grep -n 'computer-methods-and-programs' manuscripts/cmpb/src/manuscript.md  # expect 1+ hit
grep -n 'IJNMBE' manuscripts/cmpb/src/manuscript.md  # expect 0 hits
```

- [ ] **Step 5.5: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "fix(cmpb): reframe section 1 toward computer methods + programs"
```

---

## Task 6: Trim §2 Methods (~ 600 words out, no analytical change)

The §2 trim concentrates on connective rationale that duplicates between subsections (§2.4 Surrogate emulator, §2.5 OOD detection, §2.6 Sensitivity analysis) and on long quoted-list constructions that can be tabularized or compressed.

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md` (the §2 Methods section, ~ lines 50–250 of the post-Task-3 file)

- [ ] **Step 6.1: Read §2 sub-section by sub-section**

```bash
awk '/^### 2\.1/,/^### 2\.2/' manuscripts/cmpb/src/manuscript.md
awk '/^### 2\.2/,/^### 2\.3/' manuscripts/cmpb/src/manuscript.md
awk '/^### 2\.3/,/^### 2\.4/' manuscripts/cmpb/src/manuscript.md
awk '/^### 2\.4/,/^### 2\.5/' manuscripts/cmpb/src/manuscript.md
awk '/^### 2\.5/,/^### 2\.6/' manuscripts/cmpb/src/manuscript.md
awk '/^### 2\.6/,/^## 3\./' manuscripts/cmpb/src/manuscript.md
```

- [ ] **Step 6.2: Trim §2.1 (CGEM model description) by ~ 100 words**

The detailed enumeration of pilot configuration parameters (lines around "G-suit parameters (max inflation pressure in psi, torso coverage fraction); AGSM effectiveness (fraction of maximal theoretical intra-abdominal and intra-thoracic pressure the pilot can sustain); PBG max pressure (mmHg); and a dehydration level (fractional plasma volume loss)") can compress to a single sentence pointing to Table 1 (which already lists every parameter). New form:

```markdown
CGEM receives a +Gz time profile (Nz samples at 100 Hz typical) and a pilot configuration file (gloc_inp.dat) specifying subject type (FAA `who_profile` 1–6), G-suit parameters, AGSM effectiveness, PBG max pressure, and dehydration level (full parameter definitions in Table 1).
```

The compiled-binary SHA-256 sentence stays verbatim.

- [ ] **Step 6.3: Trim §2.2 (Synthetic dataset) by ~ 100 words**

Compress the standard-arm and custom-arm subsection introductions. The current "Pilot configurations — standard arm." and "Pilot configurations — custom arm." paragraphs each open with a one-sentence rationale that duplicates the high-level enumeration in the introduction; remove the rationale sentences, keep the grid specifications and row counts (1,296 + 1,944 = 3,240) verbatim. The Reproducibility paragraph keeps every artifact reference (binary, catalog, seed, tier definitions, SHA hash).

- [ ] **Step 6.4: Trim §2.4 (Surrogate emulator) by ~ 200 words**

This is the densest subsection. Specific targets:

1. **"Relation to conformalized survival analysis."** This three-sentence aside is interesting context but not load-bearing for the present result. Compress to one sentence: *Conformalized survival analysis (Candès, Lei & Ren [24]; Gui, Hannig & Hofmann [25]; Davidov et al. [26]) is the principled alternative to the two-stage pattern adopted here and is treated as paper-2 scope (§4.6).* The three citation refs are preserved.
2. **"Hyperparameters."** Remove the *"Defaults across all models: …"* enumeration of the seven XGBoost parameters and replace with: *Default XGBoost hyperparameters (full set in Supplementary Table S1) include `n_estimators=400, max_depth=6, learning_rate=0.05, tree_method="hist", random_state=42`; monotonicity constraints are applied per-feature per `cgem_ext/surrogate/targets.py`.* The Optuna-search description stays.
3. **"Conformal prediction intervals — heteroscedastic CQR."** Compress the implementation block (the *"Three XGBoost quantile regressors are trained per target…"* sentence and the *"Implementation: cgem_ext.surrogate.cqr.TwoStageXGBQuantileSurrogate…"* sentence) into the formal CQR definition only. Implementation paths stay in the Reproducibility paragraph (§2.2).

All numbered hyperparameters, the CQR conformity score formula (Romano et al. Eq. 1), and the OSF amendment 2026-05-06 H5 pre-registration reference stay verbatim.

- [ ] **Step 6.5: Trim §2.5 (Out-of-distribution detection) by ~ 100 words**

The *"Mahalanobis distance (primary)"* paragraph carries a paragraph-long justification of why the multivariate-Gaussian assumption is misspecified on the 17-feature space and why the conformal layer compensates. Compress to two sentences:

```markdown
Robust covariance is estimated via `sklearn.covariance.MinCovDet(random_state=0)`; the squared Mahalanobis distance is `DM²(x) = (x − μ̂)ᵀ Σ̂⁻¹ (x − μ̂)`. The 17-feature space mixes 9 continuous, 7 binary, and 1 ordinal dimension, so the multivariate-Gaussian assumption is misspecified; we therefore use distribution-free conformal abstention as the operational threshold (Section "Conformal abstention" below), with the parametric χ² value reported as a reference only.
```

The conformal-abstention paragraph and the IsolationForest baseline stay verbatim.

- [ ] **Step 6.6: Trim §2.6 (Sensitivity analysis) by ~ 100 words**

Remove the standalone enumerations of *N* = 1,024, *D* = 9, *N(2D+2) = 20,480* — these numbers are already in the §3 Results table caption. New form:

```markdown
**Sobol variance-based indices.** Saltelli sampling drove the surrogate (N = 1,024 base samples, D = 9 features, 20,480 evaluations) and yielded first-order (S₁), total-order (ST), and second-order (S₂) indices with 95 % bootstrap confidence intervals via `SALib.analyze.sobol.analyze`.
```

The Morris paragraph stays.

- [ ] **Step 6.7: Compute §2 word count after trim**

```bash
awk '/^## 2\. Methods/,/^## 3\./' manuscripts/cmpb/src/manuscript.md | wc -w
```

Expected: roughly 600 words less than the original §2. If short of target, second-pass trim is concentrated on §2.4 (the densest subsection).

- [ ] **Step 6.8: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "trim(cmpb): compress section 2 Methods by ~600 words; no analytical change"
```

---

## Task 7: Trim §3 Results (~ 400 words out, every number stays verbatim)

The §3 trim concentrates on narrative paragraphs framing each results subsection. Every in-text statistic, CI, p-value, and tabular number is preserved.

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md` (the §3 Results section)

- [ ] **Step 7.1: Read §3 sub-section by sub-section**

```bash
awk '/^## 3\. Results/,/^## 4\./' manuscripts/cmpb/src/manuscript.md
```

- [ ] **Step 7.2: Trim each §3 subsection's narrative connective tissue**

For each §3 sub-section (3.1 through 3.7 plus §3.6 sensitivity), find the opening framing sentence and the closing rationalization sentence. The opening framing typically says "We turn now to X" or "Having established Y in §2, we now report Z" — these can be dropped or compressed to a half-sentence. Closing rationalizations typically say "These results support the H_n pre-registered hypothesis" — keep only when the H-numbered link is non-obvious; otherwise drop. All in-text statistics and table/figure references stay.

Specific cuts:

1. **§3.1 (Dataset summary).** The descriptive paragraph that comes before Table 1 can compress to one sentence; Table 1 itself does the work.
2. **§3.3 (Mondrian conformal coverage).** The paragraph explaining why the homoscedastic Mondrian layer under-covers `time_to_gloc_s` can compress — the explanation now lives in §2.4 and the result in Table 2.
3. **§3.4 (CQR conformal coverage on `time_to_gloc_s`).** The narrative framing the H5 pre-registration can compress to a single sentence linking back to §2.4 — the amendment is documented there.
4. **§3.5 (OOD detector coverage).** Trim the LOGO discussion that explains LOGO again — definition already in §2.3.
5. **§3.7 (External validation against Whinnery & Forster).** Keep this entirely; H6 is load-bearing for the cover letter and Discussion.

- [ ] **Step 7.3: Compute §3 word count after trim**

```bash
awk '/^## 3\. Results/,/^## 4\./' manuscripts/cmpb/src/manuscript.md | wc -w
```

Expected: roughly 400 words less than original.

- [ ] **Step 7.4: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "trim(cmpb): compress section 3 Results by ~400 words; all numbers preserved"
```

---

## Task 8: Trim §4 Discussion (~ 500 words out, tighten future-work pointer)

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md` (the §4 Discussion section)

- [ ] **Step 8.1: Read §4**

```bash
awk '/^## 4\. Discussion/,/^## 5\./' manuscripts/cmpb/src/manuscript.md
```

- [ ] **Step 8.2: Identify the 2–3 most compressible paragraphs**

§4 typically has subsections like §4.1 Principal findings, §4.2 Comparison with prior work, §4.3 Strengths, §4.4 Limitations, §4.5 Implications, §4.6 Future work. The highest-yield trims:

1. §4.2 (Comparison with prior work) — if it spends > 100 words restating Portela et al. [23] before the comparison, compress.
2. §4.4 (Limitations) — keep the H6 onset-rate boundary and the synthetic-only caveat verbatim; trim the second-tier limitations that don't have a downstream paper attached.
3. §4.5 (Implications) — the regulatory / operational extrapolation paragraphs can drop.

- [ ] **Step 8.3: Rewrite the §4.6 Future-work pointer**

The CMPB cover letter and §1 emphasize *this paper is the method; downstream papers are validation and application*. Mirror that separation in §4.6. The §4.6 paragraph should:

- State that the present paper validates the method against CGEM as ground truth (synthetic-only).
- Reference paper-2 (archival re-analysis, replacing the two-stage classifier+CQR with conformalized survival per Candès, Gui, and Davidov refs).
- Reference paper-3 (own-centrifuge validation, blocked on subject data).
- Avoid scope-defence language ("this is not just X"); CMPB does not require it.

- [ ] **Step 8.4: Compute §4 word count after trim**

```bash
awk '/^## 4\. Discussion/,/^## 5\./' manuscripts/cmpb/src/manuscript.md | wc -w
```

Expected: roughly 500 words less than original.

- [ ] **Step 8.5: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "trim(cmpb): compress section 4 Discussion by ~500 words; tighten future-work pointer"
```

---

## Task 9: Add CMPB-mandatory sections to `manuscript.md`

CMPB requires CRediT Author Contributions and a Data Availability Statement as sections in the manuscript. The cmpb-submit skill also expects the figure-captions to be appended after References and the supplementary appendix sentence to precede References.

**Files:**
- Modify: `manuscripts/cmpb/src/manuscript.md`

- [ ] **Step 9.1: Insert the Author Contributions (CRediT) section**

Append after §5 Conclusions and before the Supplementary Material appendix:

```markdown
## Author Contributions

**Diego Malpica:** Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Resources, Data curation, Writing — original draft, Writing — review and editing, Visualization, Supervision, Project administration, Funding acquisition.

As sole author, Diego Malpica contributed to every CRediT role listed above.
```

- [ ] **Step 9.2: Insert the Data Availability Statement section**

Append after Author Contributions:

```markdown
## Data Availability Statement

The compiled CGEM Fortran binary and source (`.f` files) are provided by the FAA Civil Aerospace Medical Institute under their public-domain release. The synthetic dataset `cgem_synthetic_v1.parquet` (master seed 42, binary SHA-256 in the accompanying `.meta.json` sidecar) and all derived analysis code are openly available under the MIT licence at `https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`. A reproducibility Docker image is published on GitHub Container Registry (GHCR) at `ghcr.io/strikerdlm/cami-gz-effects-model-cgem-:v0.1.0`. The OSF pre-registration (including search spaces, split indices, and the 2026-05-06 amendment for H5/H6) is at the project's OSF page (DOI assigned at submission acceptance). All five Supplementary Data files (`Data_S1` through `Data_S5`) accompany this submission per the Elsevier supplementary contract.
```

- [ ] **Step 9.3: Insert the Supplementary Material end-of-paper appendix**

Append after Data Availability Statement and before References:

```markdown
## Supplementary Material

Supplementary material associated with this article is provided in the online version of the journal. Each file is named per the Elsevier convention (`Fig_S<n>.<ext>`, `Table_S<n>.<ext>`, `Data_S<n>.<ext>`, `Appendix_S<n>.<ext>`); a full inventory with one-sentence captions is included as `Supplementary_Captions.docx` (uploaded first in the Supplementary Material category in Editorial Manager).
```

- [ ] **Step 9.4: Move figure captions to the file end**

If the figure captions currently live inline with the figures in §3, leave them in place — the cmpb-submit docx builder will handle the appended figure-captions page. If captions are scattered, consolidate them as `## Figure Captions` after the References block.

- [ ] **Step 9.5: Verify section presence**

```bash
grep -nE '^## (Author Contributions|Data Availability Statement|Supplementary Material|References)' manuscripts/cmpb/src/manuscript.md
```

Expected: four headings in order — Author Contributions / Data Availability Statement / Supplementary Material / References. Figure captions appear after References.

- [ ] **Step 9.6: Commit**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "feat(cmpb): add CRediT, Data Availability, Supplementary Material appendix"
```

---

## Task 10: Body word-count gate

Verify the §1–§5 body is ≤ 3,500 words. If over, run a second-pass trim on §4 Discussion before proceeding.

- [ ] **Step 10.1: Compute body word count**

```bash
awk '/^## 1\. Introduction/,/^## 6\./' manuscripts/cmpb/src/manuscript.md | \
  awk 'BEGIN{p=1} /^## (Author Contributions|Data Availability Statement|Supplementary Material|References|Figure Captions|Acknowledgments)/{p=0} p' | \
  wc -w
```

Expected: ≤ 3,500. Acceptable upper bound: 4,000 (CMPB tolerates 3,500–4,000 with a cover-letter justification — but aim ≤ 3,500).

- [ ] **Step 10.2: If over, second-pass trim**

If the count exceeds 3,500: concentrate the trim on §4 Discussion (highest compressibility ratio). Repeat Step 8.2's high-yield cuts more aggressively. Re-run the count.

- [ ] **Step 10.3: If still over after second pass**

Document the over-cap count in the cover letter with a one-sentence justification (per spec §11 risk mitigation). Do not block submission on a 200–500-word overshoot.

- [ ] **Step 10.4: Commit (only if Step 10.2 made changes)**

```bash
git add manuscripts/cmpb/src/manuscript.md
git commit -m "trim(cmpb): second-pass section 4 cut to fit 3500-word body cap"
```

---

## Task 11: Build the Highlights file (3–5 bullets × ≤ 85 chars)

**Files:**
- Create: `manuscripts/cmpb/src/highlights.md`

- [ ] **Step 11.1: Source content from the archived Novelty File**

```bash
cat manuscripts/_archive/ijnmbe/src/novelty_file_ijnmbe.md
```

The Novelty File contained the contribution claims at ≤ 100 words total. Each contribution claim becomes one Highlights bullet, compressed to ≤ 85 characters.

- [ ] **Step 11.2: Draft 4 bullets**

Create `manuscripts/cmpb/src/highlights.md`:

```markdown
# Highlights — CMPB submission

- Conformal+OOD wrapper preserves a validated Fortran ODE physiological model.
- Mondrian-stratified CQR restores time_to_gloc_s coverage from 0.861 to 0.972.
- Distribution-free Mahalanobis conformal abstention guards 17-feature inputs.
- Surrogate emulates CGEM at ~50 µs/row vs ~9 ms direct subprocess invocation.
```

- [ ] **Step 11.3: Validate each bullet ≤ 85 characters**

```bash
awk '/^- / {n=length($0); if (n > 85) print "FAIL: "n" chars: "$0; else print "OK: "n" chars"}' manuscripts/cmpb/src/highlights.md
```

Expected: 4 "OK" lines, no FAIL. (The 85-char cap counts the leading `- ` prefix.)

- [ ] **Step 11.4: Commit**

```bash
git add manuscripts/cmpb/src/highlights.md
git commit -m "feat(cmpb): build Highlights (4 bullets, validated <=85 chars)"
```

---

## Task 12: Build the cover letter (no AI block per spec §5)

**Files:**
- Create: `manuscripts/cmpb/src/cover_letter_cmpb.md`

- [ ] **Step 12.1: Read the cmpb-submit cover-letter template**

The `cmpb-submit cover-letter` mode prints the 10-element template. Use it as the structural backbone. The CMPB cover letter is addressed to **Filippo Molinari, PhD**, Editor-in-Chief, Polytechnic of Turin.

- [ ] **Step 12.2: Draft the cover letter**

Create `manuscripts/cmpb/src/cover_letter_cmpb.md`:

```markdown
# Cover letter — *Computer Methods and Programs in Biomedicine* (CMPB)

[Date at submission]

Filippo Molinari, PhD
Editor-in-Chief, Computer Methods and Programs in Biomedicine
Polytechnic of Turin, Department of Electronics and Telecommunications
Turin, Italy

*Submitted via Editorial Manager*

---

Dear Professor Molinari,

I am pleased to submit for your consideration a Full Length Article entitled
**"Conformal machine-learning emulation and out-of-distribution detection for
the FAA CAMI G-Effects mechanistic model of acceleration physiology"** by
Diego Malpica, MD (sole author).

**Why CMPB.** This manuscript is a *computer methods and programs* submission in the literal CMPB sense: the **method** is an additive surrogate-emulator + Mondrian-stratified Conformalized Quantile Regression + distribution-free Mahalanobis OOD-abstention stack wrapping a validated regulatory ODE physiological model; the **program** is an open Python package (`cgem_ext`), a FastAPI service, and a Docker image that ship the method as a production-runnable artifact. The validated core is the FAA Civil Aerospace Medical Institute's CGEM, a Fortran-implemented system of ordinary differential equations governing cardiovascular and cerebrovascular response under sustained +Gz load. The method generalises across any validated ODE physiological model; the program is a concrete reference implementation against CGEM.

**What is known.** Validated mechanistic ODE physiological models — CGEM, Pulse, and similar codes — are computationally expensive, lack calibrated uncertainty quantification, and accept out-of-distribution inputs without warning. Conformal prediction (Vovk et al. 2005; Romano, Patterson and Candès 2019) provides distribution-free finite-sample coverage guarantees, and Portela, Banga and Matabuena (2025, PLOS Comp Biol) recently demonstrated the surrogate+conformal+OOD wrapping pattern on canonical biological dynamical systems.

**What this study adds.** Three operationally novel refinements to the wrapping pattern: (i) per-stratum (Mondrian) conformal calibration over operationally meaningful maneuver categories rather than the more common pooled calibration, with under-coverage at low-event-rate strata declared transparently rather than masked by global pooling; (ii) heteroscedastic Conformalized Quantile Regression for long-tailed event-time targets, restoring `time_to_gloc_s` empirical coverage from 0.861 to 0.972 on n = 36 event-positive test rows (pre-registered as OSF amendment H5, 2026-05-06, before any test-set evaluation under the new layer); and (iii) a robust-Mahalanobis OOD detector calibrated by distribution-free conformal abstention over a 17-dimensional mixed numeric/categorical input space. The full validation protocol — search spaces, split indices, hypotheses H1–H6 — is OSF-pre-registered.

**Key empirical anchors** on the held-out test split: conformal OOD calibration of 0.953 versus the nominal 0.95; conformal coverage within 5 percentage points of nominal 95 % on all five surrogate targets once the heteroscedastic CQR layer replaces the homoscedastic Mondrian baseline on `time_to_gloc_s`; XGBoost regressor R² = 0.82–0.90 on event-positive rows of censored targets and 0.94–1.00 on continuous targets; classifier AUROC ≥ 0.996 across the three event targets; surrogate inference at ~ 50 µs per row versus ~ 9 ms for direct subprocess invocation. External validation against the archival centrifuge cohort of Whinnery and Forster (2013) — pre-registered as H6 — establishes a slow-onset bias *δ̄* = +26.6 s [95 % CI +6.3, +52.1] at onset ≤ 0.5 G/s, with the surrogate in-bracket on every record at onset ≥ 1 G/s (the operationally relevant fighter and aerobatic regime).

**Generalisability.** The method generalises across any validated ODE physiological model; the program ships as a reusable Python package, FastAPI service, and Docker image. The wrapping pattern is publisher-agnostic and is intended as a reference implementation for the broader computational-biomedicine community.

---

**Declarations.**

- **Originality.** This manuscript reports original work that has not been published or accepted elsewhere and is not under concurrent consideration by another journal. It was previously submitted to the *International Journal for Numerical Methods in Biomedical Engineering* (manuscript 5977782), where it was desk-rejected on 2026-05-17 on scope grounds (IJNMBE updated Aims and Scope no longer accepts purely-ML papers on biomedical problems); the IJNMBE record is archived at `manuscripts/_archive/ijnmbe/REJECTION.md` in the project repository.
- **Conflict of interest.** The author declares no conflicts of interest.
- **Funding.** This research received no external funding. All work was self-funded.
- **Ethical approval.** Not applicable — the present study uses synthetic data only. No human or animal subjects were studied.
- **Data and code availability.** Source code (MIT licence) is at `https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`; the synthetic dataset `cgem_synthetic_v1.parquet` is archived under the project's Zenodo deposit (DOI assigned at acceptance); a reproducibility Docker image is on GHCR. The OSF pre-registration (including the 2026-05-06 amendment for H5/H6) is at the project's OSF page.
- **Software and program.** The CGEM-extension Python package (`cgem_ext`), FastAPI service, and Docker image are released as production-runnable artifacts under MIT licence. A reference deployment is exercisable via `docker run ghcr.io/strikerdlm/cami-gz-effects-model-cgem-:v0.1.0`.
- **Suggested reviewers.** Five candidates with verified institutional emails are listed in `suggested_reviewers_cmpb.md`. None has co-authored with the corresponding author in the past three years; none shares an institution with the author.
- **Preprint.** No preprint is currently posted. If posted on arXiv prior to portal entry, this declaration will be updated to cite the arXiv URL under a non-exclusive licence.

I confirm that this manuscript has not been published previously and is not under consideration at another journal. Thank you and the editorial board for your consideration.

Sincerely,

Diego Malpica, MD
Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC),
Bogotá, Colombia.
ORCID: 0000-0002-2257-4940
dlmalpica@yahoo.com
```

**Note:** The cmpb-submit skill's mandatory verbatim non-use attestation is intentionally omitted per spec §5 (verified Elsevier policy is disclosure-if-used; nothing to disclose ⇒ no statement; AI declarations do not belong in cover letters anyway per Elsevier guidance updated 2025-10-09).

- [ ] **Step 12.3: Verify no IJNMBE-residual language**

```bash
grep -nE 'IJNMBE|Wiley|Novelty File|Graphical Abstract|CNM' manuscripts/cmpb/src/cover_letter_cmpb.md
```

Expected: only the IJNMBE reference inside the Originality declaration (citing the prior submission record). No other hits.

- [ ] **Step 12.4: Commit**

```bash
git add manuscripts/cmpb/src/cover_letter_cmpb.md
git commit -m "feat(cmpb): build cover letter; no AI attestation block per spec section 5"
```

---

## Task 13: Build the Suggested Reviewers slate

**Files:**
- Create: `manuscripts/cmpb/src/suggested_reviewers_cmpb.md`

- [ ] **Step 13.1: Identify candidates via the cmpb-submit `reviewers` guide**

The eligibility criteria (per cmpb-submit skill `reviewers` mode):
1. Active researcher in computational methods, ML/AI in biomedicine, biomedical signal processing, physiological modelling, uncertainty quantification, or relevant domain
2. Published in CMPB or top-tier peer journals in the past 5 years
3. No co-authorship with Diego in the past 3 years
4. No current institutional affiliation shared with Diego (FAC, Bogotá)
5. Verifiable current institutional email
6. Not on CMPB editorial board

Candidate sourcing strategy: (a) authors of close-match papers cited by the manuscript (refs [23], [24], [25], [26]) — Portela, Banga, Matabuena (PLOS Comp Biol 2025); Candès, Lei, Ren; Gui, Hannig, Hofmann; Davidov, Feldman, Shamai, Kimmel, Romano; (b) authors of recent CMPB papers on conformal prediction / surrogate modelling in physiology; (c) the cmpb-submit reviewer-finding workflow (Semantic Scholar / OpenAlex / ORCID).

- [ ] **Step 13.2: Verify each candidate's affiliation, email, ORCID**

For each candidate, verify via their current institutional homepage (Tavily / firecrawl scrape):
- Current institution + department (must NOT be FAC or any Colombian aerospace institution)
- Current institutional email (must NOT be Gmail / Yahoo / personal; Editorial Manager will reject)
- ORCID
- One representative recent publication (DOI + journal name) showing scope alignment

- [ ] **Step 13.3: Draft the file**

Create `manuscripts/cmpb/src/suggested_reviewers_cmpb.md`. Use this template per reviewer (5 entries total):

```markdown
# Suggested Reviewers — CMPB submission

The five candidates below are selected per the CMPB Author Guidelines: active researchers in conformal prediction, surrogate modelling, biomedical-engineering ML, or computational physiology; institutional emails verified; no co-authorship with Diego Malpica in the past three years; no institutional overlap with the Colombian Aerospace Force; not on the current CMPB editorial board.

## 1. [Full name], [credentials]

- **Affiliation:** [Department], [Institution], [City], [Country]
- **Institutional email:** [verified email]
- **ORCID:** [0000-0000-0000-0000]
- **Expertise rationale:** [2–3 sentences citing one recent paper with DOI and journal name, linking the candidate's research focus to the manuscript's contribution]

[repeat for candidates 2 through 5]
```

For each entry, replace bracketed placeholders with verified information. If a candidate's institutional email cannot be verified from a public source (their institution's directory, their published-paper byline, their personal academic page), drop them and pick another candidate — Editorial Manager rejects unverified emails.

- [ ] **Step 13.4: Verify file integrity**

```bash
grep -c '^## ' manuscripts/cmpb/src/suggested_reviewers_cmpb.md
```

Expected: 5 (one per reviewer).

- [ ] **Step 13.5: Commit**

```bash
git add manuscripts/cmpb/src/suggested_reviewers_cmpb.md
git commit -m "feat(cmpb): build verified suggested-reviewer slate (5 candidates)"
```

---

## Task 14: Build the mandatory standalone declaration files

CMPB requires three declaration files uploaded separately to Editorial Manager: Declaration of Competing Interest, Statement on Human and Animal Studies, and Author Contributions (mirror of the manuscript-internal CRediT section, but as a separate .docx in the portal).

**Files:**
- Create: `manuscripts/cmpb/src/declaration_of_competing_interest.md`
- Create: `manuscripts/cmpb/src/statement_on_human_animal_studies.md`
- Create: `manuscripts/cmpb/src/author_contributions.md`

- [ ] **Step 14.1: Declaration of Competing Interest**

Create `manuscripts/cmpb/src/declaration_of_competing_interest.md`:

```markdown
# Declaration of Competing Interest

The author declares that he has no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

Diego Malpica, MD
Direction of Aerospace Medicine, Aerospace Scientific Department,
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC),
Bogotá, Colombia.
ORCID: 0000-0002-2257-4940
[Date at submission]
```

- [ ] **Step 14.2: Statement on Human and Animal Studies**

Create `manuscripts/cmpb/src/statement_on_human_animal_studies.md`:

```markdown
# Statement on Human and Animal Studies

**Human subjects.** Not applicable. The present study uses synthetic data generated by the FAA Civil Aerospace Medical Institute's CGEM Fortran model only. No human subjects were studied. The H6 external-validation arm against Whinnery and Forster (2013) uses previously-published archival summary statistics, not identifiable individual-level data.

**Animal subjects.** Not applicable. No animal subjects were studied.

**Informed consent.** Not applicable. No human subjects were studied.

**Ethics approval / IRB.** Not applicable. The present study does not involve human or animal subjects. The companion paper (in preparation) on own-centrifuge subjects will report under separate IRB approval at the relevant site.

Diego Malpica, MD
[Date at submission]
```

- [ ] **Step 14.3: Author Contributions (standalone)**

Create `manuscripts/cmpb/src/author_contributions.md`:

```markdown
# Author Contributions (CRediT)

**Diego Malpica:** Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Resources, Data curation, Writing — original draft, Writing — review and editing, Visualization, Supervision, Project administration, Funding acquisition.

As sole author, Diego Malpica contributed to every CRediT role listed above. There are no other contributors to acknowledge.

Diego Malpica, MD
ORCID: 0000-0002-2257-4940
[Date at submission]
```

- [ ] **Step 14.4: Verify**

```bash
ls -la manuscripts/cmpb/src/declaration_of_competing_interest.md \
       manuscripts/cmpb/src/statement_on_human_animal_studies.md \
       manuscripts/cmpb/src/author_contributions.md
```

Expected: three files, each non-empty.

- [ ] **Step 14.5: Commit**

```bash
git add manuscripts/cmpb/src/declaration_of_competing_interest.md \
        manuscripts/cmpb/src/statement_on_human_animal_studies.md \
        manuscripts/cmpb/src/author_contributions.md
git commit -m "feat(cmpb): build standalone declaration files (COI, ethics, CRediT)"
```

---

## Task 15: Rename and re-stamp the supplementary package per Elsevier contract

The IJNMBE supplementary tree at `manuscripts/_archive/ijnmbe/rendered/supplementary/` uses descriptive lowercase names (`fig_s1_shap_*.pdf`, `table_s1_rf_baseline.json`, etc.). The Elsevier contract requires `Fig_S<n>.<ext>`, `Table_S<n>.<ext>`, `Data_S<n>.<ext>`, `Appendix_S<n>.<ext>`. Inline call-outs in the manuscript must use `Fig. S1`, `Table S1` (Elsevier style — period after `Fig`, none after `Table`).

**Files:**
- Create: `manuscripts/cmpb/supplementary/Fig_S1.pdf` … `Fig_S<n>.pdf`
- Create: `manuscripts/cmpb/supplementary/Table_S1.docx` … `Table_S<m>.docx`
- Create: `manuscripts/cmpb/supplementary/Data_S1.csv` … `Data_S<k>.csv`
- Create: `manuscripts/cmpb/supplementary/Appendix_S1.pdf` (if any narrative appendix exists)
- Create: `manuscripts/cmpb/supplementary/Supplementary_Captions.docx`
- Modify: `manuscripts/cmpb/src/manuscript.md` (inline call-outs)

- [ ] **Step 15.1: Inventory the archived supplementary tree**

```bash
ls manuscripts/_archive/ijnmbe/rendered/supplementary/data_files/ 2>/dev/null
ls manuscripts/_archive/ijnmbe/rendered/supplementary/supporting_info/ 2>/dev/null
```

Map each file to its Elsevier-form target name. Example mapping (verify against the actual archive contents):

| Source path (archive) | Target name (cmpb/supplementary/) |
|---|---|
| `data_files/plots/fig_s1_shap_importance.pdf` | `Fig_S1.pdf` |
| `data_files/plots/fig_s1_shap_c_bank_min.pdf` | `Fig_S2.pdf` |
| `data_files/plots/fig_s1_shap_hlap_min.pdf` | `Fig_S3.pdf` |
| `data_files/plots/fig_s2_morris_mu_star_sigma.pdf` | `Fig_S4.pdf` |
| (… continue per actual inventory) | (…) |
| `supporting_info/table_s1_rf_baseline.docx` | `Table_S1.docx` |
| `supporting_info/table_s2_per_stratum_coverage.docx` | `Table_S2.docx` |
| `supporting_info/table_s3_second_order_sobol.docx` | `Table_S3.docx` |
| `data_files/sobol_first_total.csv` | `Data_S1.csv` |
| `data_files/sobol_second_order.csv` | `Data_S2.csv` |
| `data_files/morris.csv` | `Data_S3.csv` |
| `data_files/cqr_vs_mondrian_time_to_gloc.json` | `Data_S4.json` |
| `data_files/h6_discrepancy_phase_a.json` | `Data_S5.json` |
| `supporting_info/datasheet.docx` | `Appendix_S1.pdf` (convert) |
| `supporting_info/tripod_ai_checklist.docx` | `Appendix_S2.pdf` (convert) |
| `supporting_info/osf_preregistration.docx` | `Appendix_S3.pdf` (convert) |
| `supporting_info/osf_amendment_2026-05-06.docx` | `Appendix_S4.pdf` (convert) |

(The exact mapping depends on the archive's actual contents; verify before renaming.)

- [ ] **Step 15.2: Copy and rename files**

For each source-target pair from Step 15.1's inventory:

```bash
cp manuscripts/_archive/ijnmbe/rendered/supplementary/data_files/plots/fig_s1_shap_importance.pdf \
   manuscripts/cmpb/supplementary/Fig_S1.pdf
# [repeat for every mapped pair]
```

For `.docx` appendix files that need to become `.pdf`, use pandoc or LibreOffice:

```bash
soffice --headless --convert-to pdf \
        --outdir manuscripts/cmpb/supplementary/ \
        manuscripts/_archive/ijnmbe/rendered/supplementary/supporting_info/datasheet.docx
mv manuscripts/cmpb/supplementary/datasheet.pdf manuscripts/cmpb/supplementary/Appendix_S1.pdf
```

- [ ] **Step 15.3: Build `Supplementary_Captions.docx` source**

Create `manuscripts/cmpb/src/supplementary_captions.md` (the cmpb-submit `docx` builder will render it to `Supplementary_Captions.docx`):

```markdown
# Supplementary Material for "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"

**Fig. S1.** [≤ 25-word caption — SHAP importance ranking across all five surrogate targets.]
**Fig. S2.** [SHAP local-attribution heatmap for `c_bank_min`.]
**Fig. S3.** [SHAP local-attribution heatmap for `hlap_min`.]
**Fig. S4.** [Morris elementary-effects μ★–σ scatter across input dimensions.]
[continue for every Fig_S<n> in the supplementary folder]

**Table S1.** [Random-Forest vs XGBoost baseline comparison on the five surrogate targets.]
**Table S2.** [Per-stratum (maneuver-category) Mondrian conformal coverage with finite-sample corrections.]
**Table S3.** [Second-order Sobol indices (S₂) for all 9-feature input pairs, with 95 % bootstrap CIs.]

**Data S1.** [Sobol first-order and total-order indices in CSV form; columns: feature, S1, ST, S1_ci_lo, S1_ci_hi, ST_ci_lo, ST_ci_hi.]
**Data S2.** [Sobol second-order indices in CSV form; columns: feature_i, feature_j, S2, ci_lo, ci_hi.]
**Data S3.** [Morris elementary-effects results in CSV form; columns: feature, mu, mu_star, sigma.]
**Data S4.** [CQR-vs-Mondrian coverage comparison on `time_to_gloc_s` in JSON form.]
**Data S5.** [H6 discrepancy diagnostics against the Whinnery and Forster (2013) Phase-A cohort in JSON form.]

**Appendix S1.** [Datasheet for `cgem_synthetic_v1.parquet` per Gebru et al. (2018).]
**Appendix S2.** [TRIPOD-AI compliance checklist for the present manuscript.]
**Appendix S3.** [Frozen OSF pre-registration document.]
**Appendix S4.** [OSF amendment dated 2026-05-06 (hypotheses H5 and H6).]
```

Replace bracketed captions with single-sentence (≤ 25 word) accurate descriptions, derived from the existing archive captions.

- [ ] **Step 15.4: Update inline call-outs in `manuscript.md`**

Replace any descriptive supplementary references with Elsevier form. Examples:

- `Figure S1` → `Fig. S1`
- `Table S1` → `Table S1` (already correct in many places — verify)
- `Supplementary Information` → `Supplementary Material` (only used as bibliographic appendix label, not inline)
- "as detailed in the supplementary material" → "as shown in Fig. S<n>" / "as listed in Table S<n>" / "as released in Data S<n>"

```bash
grep -nE 'Fig\.? S[0-9]+|Table S[0-9]+|Appendix S[0-9]+|Data S[0-9]+' manuscripts/cmpb/src/manuscript.md
```

Verify each result uses the Elsevier form. Also check there are no orphaned "Supplementary Figure X" / "Supplementary Table X" references.

- [ ] **Step 15.5: Verify the bidirectional supplementary audit will pass**

```bash
# Every inline call-out → must have a matching file
grep -oE 'Fig\. S[0-9]+|Table S[0-9]+|Appendix S[0-9]+|Data S[0-9]+' manuscripts/cmpb/src/manuscript.md | sort -u > /tmp/cmpb-callouts.txt
# Every file → must be cited inline
ls manuscripts/cmpb/supplementary/ | grep -oE 'Fig_S[0-9]+|Table_S[0-9]+|Appendix_S[0-9]+|Data_S[0-9]+' | sed 's/_/. /;s/^Fig\. /Fig. /;s/^/Item: /' > /tmp/cmpb-files.txt
diff /tmp/cmpb-callouts.txt /tmp/cmpb-files.txt
```

Expected: empty diff (or only ordering differences). Any unmatched item in either direction is a blocker — fix before committing.

- [ ] **Step 15.6: Commit**

```bash
git add manuscripts/cmpb/supplementary/ manuscripts/cmpb/src/supplementary_captions.md manuscripts/cmpb/src/manuscript.md
git commit -m "feat(cmpb): build Elsevier supplementary package (Fig_Sn, Table_Sn, Data_Sn, Appendix_Sn)"
```

---

## Task 16: File the OSF venue-change amendment

**Files:**
- Create: `docs/publication/osf_amendment_2026-05-17.md`

- [ ] **Step 16.1: Draft the amendment**

Create `docs/publication/osf_amendment_2026-05-17.md`:

```markdown
# OSF Pre-registration — Amendment 2026-05-17 (venue change)

**Project:** Conformal ML emulator + OOD detector for the FAA CAMI G-Effects mechanistic model
**Sole author:** Diego Malpica, MD (ORCID 0000-0002-2257-4940)
**Date:** 2026-05-17

## Trigger

Manuscript 5977782 was desk-rejected by the *International Journal for Numerical Methods in Biomedical Engineering* (IJNMBE, Wiley) on 2026-05-17 on scope grounds. The verbatim rejection text and the citation of IJNMBE's updated Aims and Scope ("no longer accepting submissions based purely on machine and deep learning methods applied to biomedical problems") is recorded at `manuscripts/_archive/ijnmbe/REJECTION.md`.

## Amendment

The submission target is changed from IJNMBE (Wiley) to **Computer Methods and Programs in Biomedicine** (CMPB, Elsevier, Q1, $0 APC subscription track). The rationale is documented at `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`. The 2026-05-12 journal-scout output had already ranked CMPB at score 89 against IJNMBE at 81; the 2026-05-17 re-scout (`docs/publication/2026-05-17_journal-scout_cgem-emulator.md`) confirmed CMPB at the top once a separately-verified AI-policy bug in the `cmpb-submit` skill was set aside.

## What does NOT change

- All OSF-pre-registered hypotheses (H1–H6) remain unchanged.
- The OSF-frozen split indices (`docs/publication/osf_split_indices.parquet`) remain authoritative.
- The OSF-frozen hyperparameter search spaces (`docs/publication/osf_search_spaces.json`) remain authoritative.
- The frozen synthetic dataset (`cgem_synthetic_v1.parquet`, master seed 42, binary SHA-256 in `.meta.json`) is unchanged.
- All conformal calibration, all numerical results, all figures, all tables remain unchanged.
- The 2026-05-06 amendment (H5 CQR + H6 archival external validation) remains in force.

This is a procedural amendment recording the venue change; it has no scientific content and is filed for OSF audit completeness.

Diego Malpica, MD
[Signed at OSF posting]
```

- [ ] **Step 16.2: Commit**

```bash
git add docs/publication/osf_amendment_2026-05-17.md
git commit -m "docs(osf): file venue-change amendment 2026-05-17 (IJNMBE -> CMPB)"
```

---

## Task 17: File the cmpb-submit-skill bug report (workspace-internal housekeeping)

The `cmpb-submit` skill claims a mandatory verbatim non-use attestation in the cover letter; this is not reproducible from any current CMPB, Elsevier, or third-party source (verified 2026-05-17, two independent agents). The actual fix to the skill is being made in parallel by a separate background process; this task creates the workspace-internal record so future submissions (and the next person to invoke the skill) understand the divergence.

**Files:**
- Create: `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`

- [ ] **Step 17.1: Create the issues directory**

```bash
mkdir -p docs/superpowers/skills-issues
```

- [ ] **Step 17.2: Draft the bug report**

Create `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`:

```markdown
# `cmpb-submit` skill — AI non-use attestation bug

**Skill:** `~/.claude/skills/cmpb-submit/SKILL.md`
**Reported:** 2026-05-17
**Reporter:** Diego Malpica (during CGEM CMPB pivot)
**Status:** Skill fix pushed upstream 2026-05-17 (separate commit; this report is the workspace-local record).

## Bug

The skill's Cover Letter Requirements section, cover-letter template, pre-submission checklist (`status` mode), formatting rules table, compliance audit (`check` mode), quick reference (`rules` mode), and peer-review mode (`review` mode) all claim that the CMPB cover letter must contain a verbatim NON-USE attestation of generative AI:

> "The authors specifically state that they have not used generative AI in the preparation of this manuscript. ChatGPT, Large Language Models, and any other generative AI programs have not been used as a replacement for original thought or to perform activities that would normally be the responsibility of the authors (e.g., developing hypotheses, selecting and interpreting statistical tests, writing the abstract, formatting the article). Generative AI has not been used to create images, multimedia, or graphic elements. Standard referencing software tools used in the normal course of manuscript preparation are not considered generative AI."

## Why it's wrong

Independent verification (2026-05-17, two agent runs):

1. **Live CMPB Guide for Authors** scraped 2026-05-17: carries only Elsevier's standard *disclosure-if-used* clause — "Authors must declare the use of generative AI in the manuscript preparation process upon submission of the paper. […] If you have nothing to disclose, you do not need to add a statement."
2. **Elsevier publisher-wide policy** (updated September 2025): identical disclosure-if-used language; AI declaration goes in the **manuscript** (before References), not the cover letter.
3. **Elsevier cover-letter guidance** (updated 2025-10-09): the cover letter "should not include funding information, author declarations, or suggested or opposed reviewers" — author declarations are precisely what an AI attestation is.
4. **Exact-phrase search** for the skill's verbatim block ("replacement for original thought", "developing hypotheses … formatting the article", "Standard referencing software tools used in the normal course"): zero hits across Tavily and Brave. The block does not appear in any indexed Elsevier, CMPB, special-issue, Editorial Manager, or third-party source.

The skill's self-described provenance is "verified via secondary sources 2026-05-01" — i.e., never directly verified against the live Guide.

## Workspace impact

The CGEM CMPB pivot (spec `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`) waives the skill's `check`-mode FAIL on this clause explicitly. The CMPB cover letter at `manuscripts/cmpb/src/cover_letter_cmpb.md` does **not** contain the verbatim block. This is policy-compliant per spec §5 and per Elsevier's actual disclosure-if-used policy under Diego's local "nothing to disclose, no statement" stance.

## Upstream fix

The skill itself is being fixed in parallel (separate commit, pushed to the `~/.claude/skills/cmpb-submit/` repo). The fix replaces the mandatory non-use attestation with the standard disclosure-if-used language and downgrades the `check`-mode rule. Once the fix is merged, this workspace-local report becomes a historical record of the divergence.

## How to use this report

- Future CMPB submissions in this workspace: read this report before invoking `cmpb-submit`. If the upstream fix has merged, this report is informational only. If the upstream fix has not yet propagated to the local copy, this report explains why the skill's mandatory attestation block is ignored.
```

- [ ] **Step 17.3: Commit**

```bash
git add docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md
git commit -m "docs(skills): file cmpb-submit attestation-bug report (workspace record)"
```

---

## Task 18: Run cmpb-submit `supplementary` (bidirectional audit)

**Files:**
- (No file writes; audit-only step. May surface issues that require fixes upstream.)

- [ ] **Step 18.1: Invoke the skill**

In the chat session, invoke:

```
Skill: cmpb-submit
Args: supplementary
```

The skill will:
1. Grep `manuscripts/cmpb/src/manuscript.md` for every `Fig. S<n> / Table S<n> / Data S<n> / Appendix S<n>` call-out.
2. Compare against the file inventory in `manuscripts/cmpb/supplementary/`.
3. Report orphans on either side as FAIL.

- [ ] **Step 18.2: Resolve any orphans**

If the skill reports an unmatched call-out, either add the missing file (renamed from the archive) or remove the call-out from the manuscript. If the skill reports an unmatched file, either add a call-out in the manuscript or remove the file from the supplementary tree.

- [ ] **Step 18.3: Re-run if changes were made**

Repeat Step 18.1 until the audit reports zero orphans.

- [ ] **Step 18.4: Commit (only if Step 18.2 made changes)**

```bash
git add manuscripts/cmpb/supplementary/ manuscripts/cmpb/src/manuscript.md
git commit -m "fix(cmpb): resolve supplementary bidirectional-audit orphans"
```

---

## Task 19: Run cmpb-submit `check` (full compliance audit; waive the known FAIL)

**Files:**
- (No file writes from the audit itself; fixes for any non-AI FAILs land in subsequent commits.)

- [ ] **Step 19.1: Invoke the skill**

In the chat session, invoke:

```
Skill: cmpb-submit
Args: check
```

The skill will run the full audit (manuscript + cover letter + supplementary).

- [ ] **Step 19.2: Resolve non-AI FAILs**

Address every PASS/FAIL/WARN line **except** the verbatim non-use attestation FAIL — that one is explicitly waived per spec §5 and recorded in the skill bug report at `docs/superpowers/skills-issues/2026-05-17-cmpb-submit-attestation-bug.md`. For each non-waived FAIL, fix the manuscript or supporting file and re-run the audit.

Typical FAILs to expect and how to address them:

- Body word count over 3,500 → return to Task 10's second-pass trim.
- Abstract over 350 words → return to Task 4.
- Highlights bullet over 85 chars → return to Task 11.
- Missing structured-abstract heading → return to Task 4.
- Vancouver reference format error → re-check the References block; the cmpb-submit `docx` builder may catch this in Task 20.
- Missing CRediT / Data Availability section → return to Task 9.

- [ ] **Step 19.3: Re-run until clean (with the one known waiver)**

Repeat Step 19.1. Audit must pass on every check except the non-use attestation.

- [ ] **Step 19.4: Commit (only if Step 19.2 made changes)**

```bash
git add manuscripts/cmpb/
git commit -m "fix(cmpb): resolve cmpb-submit check FAILs (non-AI)"
```

---

## Task 20: Run cmpb-submit `docx` (build the portal-ready package)

**Files:**
- Create: `manuscripts/cmpb/cmpb_config.json` (JSON config consumed by the docx builder)
- Create: `manuscripts/cmpb/rendered/manuscript_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/cover_letter_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/highlights_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/declaration_of_competing_interest_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/statement_on_human_animal_studies_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/author_contributions_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/suggested_reviewers_cmpb.docx`
- Create: `manuscripts/cmpb/rendered/fig1.pdf` … `fig6.pdf` (copies from archive)
- Create: `manuscripts/cmpb/supplementary/Supplementary_Captions.docx`

- [ ] **Step 20.1: Copy the cmpb-submit JSON config template**

```bash
cp ~/.claude/skills/cmpb-submit/assets/cmpb_manuscript_config.example.json \
   manuscripts/cmpb/cmpb_config.json
```

- [ ] **Step 20.2: Populate the config from the manuscript source files**

Edit `manuscripts/cmpb/cmpb_config.json` to point to:
- `manuscripts/cmpb/src/manuscript.md` as the body source (after parsing the four-heading abstract block, the numbered sections, the References block, and the appended Figure Captions block).
- `manuscripts/cmpb/src/cover_letter_cmpb.md`
- `manuscripts/cmpb/src/highlights.md`
- `manuscripts/cmpb/src/declaration_of_competing_interest.md`
- `manuscripts/cmpb/src/statement_on_human_animal_studies.md`
- `manuscripts/cmpb/src/author_contributions.md`
- `manuscripts/cmpb/src/suggested_reviewers_cmpb.md`
- `manuscripts/cmpb/src/supplementary_captions.md`
- `figure_map`: dict mapping `manuscripts/_archive/ijnmbe/rendered/figures/fig1.pdf` → `manuscripts/cmpb/rendered/fig1.pdf`, fig2 through fig6.

- [ ] **Step 20.3: Run the docx builder**

```bash
~/.claude/skills/cmpb-submit/bin/build-cmpb-docx \
    --config manuscripts/cmpb/cmpb_config.json \
    --out    manuscripts/cmpb/rendered/
```

Expected output: seven `.docx` files in `manuscripts/cmpb/rendered/`, plus six `figN.pdf` figure files copied from the archive.

- [ ] **Step 20.4: Verify line-number XML embedding**

```bash
unzip -p manuscripts/cmpb/rendered/manuscript_cmpb.docx word/document.xml | grep -o '<w:lnNumType[^/]*/>'
```

Expected output: `<w:lnNumType w:countBy="1" w:start="1" w:distance="360" w:restart="continuous"/>`.

- [ ] **Step 20.5: Verify double-spacing XML embedding**

```bash
unzip -p manuscripts/cmpb/rendered/manuscript_cmpb.docx word/styles.xml | grep -o '<w:spacing[^/]*w:line="480"[^/]*/>' | head -1
```

Expected: a hit on `w:line="480"` (double spacing).

- [ ] **Step 20.6: Verify Supplementary_Captions.docx was built**

```bash
test -f manuscripts/cmpb/supplementary/Supplementary_Captions.docx && echo "OK"
```

Expected: OK. If the builder didn't write it automatically, run pandoc against `manuscripts/cmpb/src/supplementary_captions.md`:

```bash
pandoc manuscripts/cmpb/src/supplementary_captions.md \
       -o manuscripts/cmpb/supplementary/Supplementary_Captions.docx
```

- [ ] **Step 20.7: Visual spot-check (open in Word / LibreOffice Writer)**

Open `manuscripts/cmpb/rendered/manuscript_cmpb.docx`. Confirm:
- Continuous line numbers visible in left margin.
- Body double-spaced.
- Structured abstract uses the four headings (Background and Objectives / Methods / Results / Conclusions) in order.
- Numbered sections (1. Introduction / 2. Methods / etc.).
- References in Vancouver `[n]` style.
- Figure captions appended after References.

- [ ] **Step 20.8: Commit**

```bash
git add manuscripts/cmpb/cmpb_config.json manuscripts/cmpb/rendered/ manuscripts/cmpb/supplementary/Supplementary_Captions.docx
git commit -m "build(cmpb): generate portal-ready docx package via cmpb-submit"
```

---

## Task 21: Final hand-off package (no commit; chat-only summary)

- [ ] **Step 21.1: Confirm all rendered files exist**

```bash
ls -la manuscripts/cmpb/rendered/
ls -la manuscripts/cmpb/supplementary/
```

Expected (rendered/): 7 `.docx` files + 6 figure PDFs.
Expected (supplementary/): all `Fig_S<n>.pdf`, `Table_S<n>.docx`, `Data_S<n>.<ext>`, `Appendix_S<n>.pdf`, plus `Supplementary_Captions.docx`.

- [ ] **Step 21.2: Print a chat-level summary for Diego**

Summary block to print to Diego in the final message:

```
Portal-ready CMPB submission package built. Files for Editorial Manager upload:

  manuscripts/cmpb/rendered/manuscript_cmpb.docx              ← Manuscript (line numbers + double spacing baked in)
  manuscripts/cmpb/rendered/cover_letter_cmpb.docx            ← Cover Letter
  manuscripts/cmpb/rendered/highlights_cmpb.docx              ← Highlights
  manuscripts/cmpb/rendered/declaration_of_competing_interest_cmpb.docx  ← Declaration of Competing Interest
  manuscripts/cmpb/rendered/statement_on_human_animal_studies_cmpb.docx  ← Statement on Human and Animal Studies
  manuscripts/cmpb/rendered/author_contributions_cmpb.docx    ← Author Contributions
  manuscripts/cmpb/rendered/suggested_reviewers_cmpb.docx     ← Suggested Reviewers
  manuscripts/cmpb/rendered/fig1.pdf ... fig6.pdf             ← Figures (one per file)
  manuscripts/cmpb/supplementary/Supplementary_Captions.docx  ← Supplementary captions (upload FIRST in SI category)
  manuscripts/cmpb/supplementary/Fig_S<n>.pdf, Table_S<n>.docx, Data_S<n>.<ext>, Appendix_S<n>.pdf  ← Supplementary items

Portal: https://www.editorialmanager.com/cmpb/
EiC: Filippo Molinari, PhD (Polytechnic of Turin)

Submission readiness checklist:
  Body word count: [computed value] / 3,500 cap
  Abstract: [count] / 350 cap
  References: [count] / 50 cap
  Highlights: [bullet count] / max 5 — all ≤ 85 chars
  Supplementary bidirectional audit: PASS
  cmpb-submit check: PASS (with the documented attestation-FAIL waiver, see skills-issues report)

When ready: log in to Editorial Manager, follow the cmpb-submit `upload` walkthrough.
```

- [ ] **Step 21.3: Diego review**

Pause here for Diego's review of the full package before any portal upload.

- [ ] **Step 21.4: Diego portal upload**

Diego performs the Editorial Manager upload manually. The cmpb-submit `upload` mode is available as a walkthrough.

---

## Self-Review

### Spec coverage

- ✅ §1 Strategy (CMPB pivot, minimal repackage) → Tasks 1–20 implement; word-count work is concentrated in Tasks 4–10.
- ✅ §2 Pre-flight verification → already executed during brainstorming (CMPB live scope and AI policy verified 2026-05-17, two independent agents). EIC and editorial board verification is folded into Task 13 (suggested reviewers) which requires checking the board anyway.
- ✅ §3 Folder layout → Tasks 1, 2, 15, 20 build exactly the spec's tree.
- ✅ §4 Repackage delta → every row of the spec's §4 table maps to one or more steps in Tasks 3–9, 11–15.
- ✅ §5 AI-disclosure decision → Task 12 omits the verbatim block, Task 17 files the skill bug report, Task 19 waives the known FAIL.
- ✅ §6 Submission package → Task 20 produces all seven .docx files + six figure PDFs, supplementary built in Task 15.
- ✅ §7 OSF amendment → Task 16.
- ✅ §8 Timeline (22 steps) → Tasks 1–20 implement steps 1–19; step 20 (skill bug report) is Task 17; steps 21–22 (Diego review + upload) are Task 21.
- ✅ §9 Non-goals → respected throughout (no analytical edits, no figure changes, no `cgem_ext/` changes).
- ✅ §10 Acceptance criteria → all 9 criteria are checkable from Task 21's summary block.
- ✅ §11 Risks → mitigations are embedded in Tasks 10, 15, 19, 20.

### Placeholder scan

- "[Date at submission]" appears in three declaration files (Tasks 12, 14) — this is intentional. Diego stamps the date at portal upload time.
- "[Full name], [credentials]", "[Department], [Institution], …" in Task 13 — intentional template placeholders; Diego or the executing engineer fills these from verified candidate research. Cannot be hardcoded without first running the candidate-verification step.
- The Task 15 file-mapping table uses "(… continue per actual inventory)" — this is correct because the mapping depends on the runtime inventory of the archived supplementary tree; the table provides the pattern and the engineer expands it from `ls` output.
- "(if any narrative appendix exists)" in Task 15 — conditional, correct.
- Bracketed captions in `supplementary_captions.md` (Task 15) — intentional template; engineer replaces with derived captions from the archive originals.

No "TBD" / "TODO" / "implement later" / "fill in details" patterns found.

### Type consistency

- File paths use `manuscripts/cmpb/...` consistently (not `manuscripts/CMPB/...` or `cmpb_manuscripts/...`).
- File names match between spec and plan: `manuscript_cmpb.docx`, `cover_letter_cmpb.docx`, etc.
- The supplementary naming pattern (`Fig_S<n>` / `Table_S<n>` / `Data_S<n>` / `Appendix_S<n>`) is used identically in Tasks 9, 15, and 20.
- The cmpb-submit skill is invoked in modes `supplementary` (Task 18), `check` (Task 19), `docx` (Task 20) — consistent with the skill's published mode list.
- EiC name "Filippo Molinari, PhD" appears in Tasks 12 and 21 with identical spelling.

Plan is internally consistent. Ready for execution.
