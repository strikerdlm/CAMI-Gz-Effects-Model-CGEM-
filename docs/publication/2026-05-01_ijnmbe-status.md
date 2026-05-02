# `/ijnmbe-submit status` — pre-submission checklist

> **Manuscript:** `docs/publication/manuscript.md` (Conformal ML emulation
> and OOD detection for the FAA CGEM G-LOC model)
> **Target journal:** *International Journal for Numerical Methods in
> Biomedical Engineering* (IJNMBE), Wiley, ISSN 2040-7947
> **Editor-in-Chief:** Perumal Nithiarasu (Swansea)
> **Submission portal:** https://authors.wiley.com/journal/CNM
> **Article type:** Research Paper
> **Peer-review model:** single-anonymous (Wiley default; double-anonymous not
> offered on this title)
> **Audit run:** 2026-05-01 against the verified IJNMBE Author Guidelines

This is the output of `/ijnmbe-submit status`. It compares the current
submission package — built originally for AMHP, then re-tailored for CMPB —
against IJNMBE's verified Author Guidelines item by item. The report uses:

- **PASS** — IJNMBE rule met
- **FAIL** — IJNMBE rule not met; concrete fix listed
- **WARN** — borderline / cannot fully verify without author confirmation
- **N/A** — not applicable to a synthetic-only Research Paper

A prioritised action list closes the report.

---

## 1 · Manuscript-body checks

| # | Item | Status | Evidence / fix |
|---|---|---|---|
| 1.1 | Title is short, informative, contains major keywords, **no abbreviations** | **WARN** | Current title contains the abbreviations *ML*, *OOD*, *CGEM*, *G-LOC*. IJNMBE wants no abbreviations in titles. Suggested rewrite: *"Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"* (16 words, no abbreviations except FAA which is a proper noun). |
| 1.2 | Short title ≤ 70 characters available | **WARN** | The CMPB/AMHP package has a running head ("CONFORMAL CGEM EMULATION", 26 chars) but no IJNMBE short-title slot. Use *"Conformal ML wrapper for a validated ODE physiological model"* (61 chars) at the portal short-title field. |
| 1.3 | Authors with affiliations + emails on title page | **PASS** | `author_page.md` carries Diego Malpica + ORCID 0000-0002-2257-4940 + FAC affiliation + email. |
| 1.4 | Abstract ≤ 400 words; structured *or* unstructured; no citations / fig / table / eq references | **PASS (with note)** | Current abstract is **341 words** (well under IJNMBE's 400-word cap), structured (Background and Objectives / Methods / Results / Conclusions), no in-text citations, no figure or table references. Note: PMEA needed it trimmed to 300; IJNMBE does not. |
| 1.5 | Keywords: **6** chosen (Manuscript Style cap) | **WARN** | Current manuscript lists **8 keywords**. Trim to 6, e.g.: physiological modelling; surrogate emulation; conformal prediction; out-of-distribution detection; uncertainty quantification; global sensitivity analysis. |
| 1.6 | Practitioner Points (optional): ≤ 3 bullets, practitioner-focused | **N/A** | Optional. Could be added — see action list. |
| 1.7 | Body: IMRaD (Introduction / Materials & Methods / Results / Discussion / Conclusion) | **PASS** | §1 Introduction → §2 Methods → §3 Results → §4 Discussion → §5 Conclusion. Well-formed. |
| 1.8 | Body word count fits journal expectations | **PASS** | ≈ 5,430 body words (Intro → Conclusion). IJNMBE has no hard cap; this length is well within the range of recently-published IJNMBE Research Papers. |
| 1.9 | Acknowledgments includes funding + grant numbers | **PASS** | "This research received no external funding. All work was self-funded by the author." |
| 1.10 | References complete and accurate; **DOI at end of each reference** | **PASS** | 19 references; `references_verification.md` documents DOI verification for each entry. Vancouver numerical style is acceptable under IJNMBE Free Format. **No conversion required.** |
| 1.11 | Tables: each with title and footnotes | **PASS** | 4 tables (T1 emulator regressor; T2 conformal coverage; T3 OOD; T4 Sobol) each captioned. T2 already has a footnote on event-positive sample sizes. |
| 1.12 | Figures: legends beneath each image AND complete legend list in text; **no tints**; lettering legible upon reduction; compound figures combined into single files | **WARN** | Manuscript carries a Figure-captions block at the end of the body (lines 365–377), which provides the "complete legend list in the text" requirement. Each ECharts panel has its caption in the manuscript flow. **Tints status [VERIFY]:** ECharts uses colour-blind-safe palettes (verified) but I cannot confirm without rendering each PNG that no panel uses a greyscale gradient to encode categorical data — that is the IJNMBE-specific "no tints" rule. Action: re-render Figs 3 and 4 with explicit colour or pattern coding rather than greyscale shading. |
| 1.13 | Continuous reading order: figures and tables embedded inline at submission (or separate, author choice) | **PASS** | The manuscript has figures and tables embedded inline in the markdown source. At revision stage they will need to be separated — but at *initial* submission this is fine. |

---

## 2 · Title-page declarations (Wiley Free Format mandatory list)

The IJNMBE title page must include all of the following. Currently they
are split between `author_page.md` and the Acknowledgements section at the
end of the manuscript body. **For an IJNMBE submission, consolidate them
all on the title page** (`author_page.md`).

| # | Declaration | Status | Evidence / fix |
|---|---|---|---|
| 2.1 | **Data availability statement** (URL / DOI) | **PASS (location fix)** | Currently in §"Data and code availability" of the manuscript body (lines 295–303). Move a copy to the title page. Statement reads: GitHub repo URL + Zenodo DOI (TBD) + GHCR Docker image + OSF pre-registration (TBD). |
| 2.2 | **Funding statement** (sources + grant numbers, or "self-funded") | **PASS (location fix)** | Currently at line 315 of manuscript body and on `author_page.md` line 53. State: "This research received no external funding. All work was self-funded by the author." |
| 2.3 | **Conflict of interest disclosure** | **PASS (location fix)** | "The author declares no conflicts of interest." Present in both files. |
| 2.4 | **Ethics approval statement** | **PASS** | "This study used only synthetically generated outputs of the CGEM ODE model… No human or animal subjects were involved. Ethics-board approval was therefore not required." (manuscript line 307). For IJNMBE state: **"n/a — synthetic data only"** in the title page declaration. |
| 2.5 | **Patient consent statement** | **PASS — n/a** | No human subjects; declare "n/a" on the title page. |
| 2.6 | **Permission to reproduce material from other sources** | **PASS — n/a** | No third-party figures or extended quotes reused; declare "n/a — all figures original; no third-party material reproduced". |
| 2.7 | **Clinical-trial registration** | **PASS — n/a** | No clinical trial; declare "n/a — methodological / synthetic-data study, no trial". |

---

## 3 · Mandatory separate files (in addition to the manuscript)

| # | File | Status | Evidence / fix |
|---|---|---|---|
| 3.1 | **Cover Letter** addressed to **Prof. Perumal Nithiarasu**, EiC | **FAIL** | `cover_letter.md` is currently addressed to Filippo Molinari (CMPB EiC). Re-target: change addressee block, link the scope justification to IJNMBE's verified clauses ("DE-based biomedical models" + "AI within scope"), add an explicit paragraph pre-empting the "no standard procedure on standard problem" filter. Run `/ijnmbe-submit cover-letter` to generate the corrected draft. |
| 3.2 | **Novelty File** — itemised list, ≤ 100 words, **NOT a duplicate of the abstract** | **FAIL — file does not exist** | This is mandatory at IJNMBE and is one of the two most common reasons submissions are returned without review at this journal. Run `/ijnmbe-submit novelty` to draft. Lead with: (a) Mondrian split-conformal stratified by maneuver category, (b) conformal-Mahalanobis OOD abstention, (c) two-stage classifier-then-regressor pattern for right-censored event-time targets, (d) additive-wrapper preservation of the FAA-validated core, (e) generalisability claim. |
| 3.3 | **Graphical Table of Contents** — single graphic, 300 dpi+, colour-blind-safe, no tints | **FAIL — file does not exist** | Mandatory at IJNMBE. Run `/ijnmbe-submit graphical` to draft. Suggested content: a 2-panel composite — left panel showing the "validated ODE core ⇄ ML wrapper layer with conformal + OOD" architecture diagram (essentially Fig 6 simplified); right panel showing speed-up (~180×) + Mondrian conformal coverage table summary. |
| 3.4 | **Graphical Abstract** mini-abstract (text) — title + authors + ≤ 80 words / 3 sentences | **FAIL — file does not exist** | Mandatory. Run `/ijnmbe-submit graphical` to draft alongside the TOC graphic. |
| 3.5 | **Data Files** — data + code uploaded as **Data Files** (NOT Supporting Information); README documents reproduction | **WARN** | The repository (`github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`) and Docker image are public, and reproduction scripts are committed. The Zenodo DOI for `cgem_synthetic_v1.parquet` and the OSF pre-registration URL are still listed as "TBD at submission" in the manuscript. **Action:** mint the Zenodo DOI and the OSF pre-registration timestamp before clicking submit. Cite the dataset formally in the reference list per the Joint Declaration of Data Citation Principles (Authors; Year; Dataset title; Zenodo; Version; DOI). |
| 3.6 | (optional) Supporting Information | **PASS** | TRIPOD-AI checklist + dataset datasheet + emulator/OOD model cards + OSF search-spaces JSON + SHAP plots + Morris EE plots + S₂ tables — all listed in the manuscript Supplementary materials block (lines 381–393). |

---

## 4 · Suggested reviewers

IJNMBE requires 3–5 with strong methodological balance.

| Item | Status | Evidence / fix |
|---|---|---|
| Number of candidates | **PASS** | `suggested_reviewers.md` lists 5. |
| Coverage axes (methodology + application + numerical methods + regulatory + generalist) | **WARN** | The current list (Copeland, Aliverti, … — only first 2 reviewed in this audit) was assembled for **CMPB**. For IJNMBE the slate should explicitly cover: (a) **conformal prediction / surrogate ML methodology**, (b) **biomedical-physiology application domain** (cerebrovascular / cardiovascular ODE), (c) **numerical methods** with an IJNMBE publication record in the past 3 years, (d) **regulatory / aerospace-medicine application**, (e) **generalist** with senior IJNMBE familiarity. **Action:** retain Kyle Copeland (FAA / regulatory). Replace at least one reviewer with a published IJNMBE author from the past 3 years (e.g., authors of cardiovascular-ODE-surrogate papers; Kakhaia et al. 2021 on arterial-tissue ML surrogates would be apt). Run `/ijnmbe-submit reviewers` to draft a fresh slate. |
| No co-authorship in past 3 years; no shared institution; no IJNMBE editorial-board members | **WARN — re-verify** | Current list passes for CMPB; re-verify against IJNMBE editorial board (`onlinelibrary.wiley.com/page/journal/20407947/homepage/EditorialBoard.html`) before portal entry. |

---

## 5 · Scope-filter pre-emption

IJNMBE explicitly states:
> "Authors are reminded that application of a standard numerical procedure
> to a standard problem is not within the scope of this journal."

This is the single highest-risk filter for the manuscript, because a
fast-reading editor could classify "XGBoost on a Fortran simulator" as
exactly that pattern.

| Item | Status | Evidence / fix |
|---|---|---|
| 5.1 | The cover letter explicitly addresses the "no standard procedure on standard problem" clause | **FAIL** | The CMPB cover letter does not address this clause. **Action:** in the IJNMBE cover letter, dedicate one paragraph to identifying which of (a) the method, (b) the problem, or (c) the combination is non-standard. The defensible answer is **(c) the combination**: Mondrian conformal stratification by maneuver category + conformal-Mahalanobis OOD abstention + two-stage censored-event-time pattern + additive wrapper of a validated regulatory ODE model is not, taken together, a standard pipeline. |
| 5.2 | The Novelty File leads with a non-standard methodological contribution | **FAIL** | Novelty File does not yet exist (item 3.2). When drafted, lead with the Mondrian + conformal-OOD combination, NOT with "applied XGBoost". |
| 5.3 | The abstract does not present the contribution as a single off-the-shelf tool applied to a standard problem | **WARN** | The current abstract is structured around three capability gaps (computational cost / no calibrated UQ / no input-envelope guard) and the methods used to close them. This is a defensible methodological framing. **Optional reinforcement:** after the Background sentence, insert one sentence explicitly framing the contribution as "a generalisable methodological pattern for any validated ODE physiological model", to pre-empt the scope filter at the abstract level. |

---

## 6 · IJNMBE-specific extra audits

| # | Item | Status | Evidence / fix |
|---|---|---|---|
| 6.1 | Compound-figure consolidation (1a, 1b, 1c → one file at revision) | **WARN — at revision only** | Figure 1 is described as a 2 × 4 panel layout (panels A–H). At revision stage these need to be one file, not eight. The current rendering pipeline produces a single composite — verify before revision upload. |
| 6.2 | "No tints" rule in figures (greyscale shading forbidden) | **WARN** | Manuscript-side cannot verify without rendering. **Action:** open `data/results/figures/echarts_options/fig*.json` and confirm that no axis or panel encodes data via a greyscale gradient (acceptable: solid colour fills, line styles, hatching). The OOD KDE (Fig 4) and Sobol heatmap (Fig 5) are the two highest-risk panels here. |
| 6.3 | eLocators awareness — no "page numbers" in cross-references | **PASS** | The manuscript already uses section/equation/figure references throughout, not page numbers. Reference entries also use volume:pages, which is acceptable; production will swap the page range for an eLocator. |
| 6.4 | AI disclosure | **PASS** | Manuscript §"Declaration of generative AI use" (line 293) is a clean, properly framed disclosure. Also referenced in the cover letter. The IJNMBE/Wiley reviewer ethics says no AI-generated reviews; nothing in the policy I have verified prohibits authors from using AI for the kinds of editorial / formatting / scaffolding tasks disclosed here. |
| 6.5 | Highlights file | **N/A — drop the CMPB Highlights** | `highlights.md` is a CMPB-specific 3–5-bullet ≤ 85-char file. IJNMBE does not require Highlights — do not upload. The optional **Practitioner Points** (≤ 3 bullets) is a different artefact and would replace it if used. |
| 6.6 | Continuous Publication awareness | **PASS** | No issue/page references in the body, so the manuscript will land cleanly under IJNMBE's Continuous Publication / eLocator workflow. |
| 6.7 | Preprint policy | **PASS — discretionary** | IJNMBE permits arXiv/bioRxiv/engrXiv preprints under non-exclusive licence. Optional: post a preprint at submission. If posted, update the cover letter "Preprint" declaration accordingly. |

---

## 7 · Prioritised action list

### FAIL (must fix before clicking submit)

| # | Action | Tool | Est. time |
|---|---|---|---|
| F1 | Re-write the cover letter, addressed to Prof. Nithiarasu, with the IJNMBE scope-filter pre-emption paragraph | `/ijnmbe-submit cover-letter` | 30 min |
| F2 | Draft the **Novelty File** (≤ 100 words, itemised, ≠ abstract) | `/ijnmbe-submit novelty` | 20 min |
| F3 | Draft the **Graphical Abstract** mini-abstract (≤ 80 words / 3 sentences) | `/ijnmbe-submit graphical` | 15 min |
| F4 | Render the **Graphical Table of Contents** image (300 dpi, colour-blind-safe, thumbnail-readable, no tints) | publication-visuals + ECharts pipeline | 60 min |
| F5 | Mint Zenodo DOI for `cgem_synthetic_v1.parquet`; mint OSF pre-registration; replace the "TBD at submission" placeholders in the manuscript and title page | manual (Zenodo + OSF web UIs) | 45 min |

### WARN (should fix; or document why not)

| # | Action | Tool | Est. time |
|---|---|---|---|
| W1 | Rewrite the title to remove abbreviations (or accept that "FAA", "CAMI", and similar proper nouns are tolerated) | manual | 10 min |
| W2 | Trim keywords from 8 → 6 | manual | 5 min |
| W3 | Audit Figs 3 (calibration) and 4 (OOD KDE) for greyscale tints; re-render if any panel encodes data via greyscale gradient | publication-visuals | 30 min |
| W4 | Move all seven Wiley title-page declarations from the body of the manuscript onto the title page (`author_page.md`) | manual | 20 min |
| W5 | Re-target the suggested-reviewer slate for IJNMBE: keep Copeland (regulatory), replace at least one slot with a recent IJNMBE author on cardiovascular-ODE surrogates | `/ijnmbe-submit reviewers` | 30 min |
| W6 | Add 2–3 IJNMBE-precedent references (Kakhaia et al. 2021 on arterial-tissue ML surrogates with inverse UQ; the IJNMBE 1-D arterial blood-flow benchmark study; Liang et al. on aortic ML surrogates) | manual + DOI verify | 30 min |
| W7 | Cite `cgem_synthetic_v1` formally in the reference list per the Joint Declaration of Data Citation Principles | manual | 10 min |
| W8 | Reinforce the abstract with one sentence framing the contribution as a generalisable methodological pattern (optional) | manual | 5 min |

### Optional polish

| # | Action | Tool | Est. time |
|---|---|---|---|
| O1 | Add 2–3 Practitioner Points (≤ 3 bullets, written for the practitioner; published with the article) | manual | 20 min |
| O2 | Post an arXiv preprint at submission and update the cover-letter "Preprint" declaration | manual | 30 min |

### Drop (not used at IJNMBE)

| # | Action |
|---|---|
| D1 | Do **not** upload `highlights.md` — IJNMBE does not require Highlights |
| D2 | Do **not** upload AMHP-era forms (Copyright, COI, Pub-Cost) — Wiley uses WALS post-acceptance |
| D3 | Do **not** strip author identity from the manuscript — IJNMBE is single-anonymous, double-anonymous is not offered |

---

## 8 · One-screen summary

```
✓ /ijnmbe-submit status — pre-submission audit
  Manuscript:           docs/publication/manuscript.md
  Body words:           ≈ 5,430 (no IJNMBE cap)
  Abstract words:       341 / 400 PASS
  Keywords:             8 → trim to 6 WARN
  References:           19 (Vancouver — accepted under Free Format) PASS
  Tables:               4 PASS
  Figures:              6 (audit greyscale tints WARN)

  PASS:    13
  WARN:     9
  FAIL:     5 (cover letter addressee + Novelty File + Graphical Abstract +
              Graphical TOC graphic + DOI placeholders)
  N/A:      3

  Estimated time to "ready to submit": ~ 4–5 hours of focused work.
  Critical-path items (FAILs): cover-letter rewrite, Novelty File, Graphical
  Abstract pair, and Zenodo/OSF DOI minting. Run the next four /ijnmbe-submit
  modes in order:
    1. /ijnmbe-submit cover-letter
    2. /ijnmbe-submit novelty
    3. /ijnmbe-submit graphical
    4. /ijnmbe-submit reviewers   (optional but recommended)
```

---

## 9 · What this audit did NOT verify

- The exact JIF / CiteScore figures at submission time — taken from earlier
  Tavily lookup, may have moved.
- The portal label for the Novelty File — derived from the verified
  guidelines text; the portal UI may show it under "Other" or "Mandatory
  File" rather than literally "Novelty File".
- That every figure renders without greyscale tints — requires opening each
  rendered PNG/SVG.
- The current IJNMBE editorial-board roster — re-fetch before suggesting
  reviewers, to avoid recommending a board member.

Re-verify these against the live journal homepage
(`onlinelibrary.wiley.com/page/journal/20407947/homepage/forauthors.html`)
before clicking submit.
