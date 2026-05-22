# Physiological Measurement (PMEA / IOP / IPEM) — Submission Guidelines Audit

**Date:** 2026-05-22
**Audit author:** Claude Code (background research agent), under Dr. Diego Malpica's direction
**Manuscript under audit:** "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology" — sole author Diego Malpica, MD, ORCID `0000-0002-2257-4940`.
**Manuscript source path:** `/root/repos/manuscripts/cgem/bspc/src/manuscript.md` (BSPC variant, last edited 2026-05-17; current word count ≈ 6,020 main body / 8,697 total including refs and figure captions)
**Rendered Docx of BSPC variant:** `/root/repos/manuscripts/cgem/bspc/rendered/manuscript.docx`
**Working "canonical" manuscript in CGEM repo:** `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/publication/manuscript.md` (10,425 words, longer; the BSPC variant is the leaner, journal-shaped one)
**Prior PMEA scout (carry-forward):** `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/publication/2026-05-01_journal-scout_physiol-meas_guide.md` — Diego asked then for "PMEA route" rules; this audit replaces that with live-verified facts as of 2026-05-22.
**Why we are auditing now:** Paper desk-rejected from BSPC (Elsevier) on 2026-05-22 for scope mismatch. PMEA is the strongest single-clause scope match in the 2026-05-17 scout (28/30). This audit verifies, against the live IOP pages, every rule that gates a PMEA portal upload, and reports the deltas required to convert the BSPC package.

---

## 1. Cover summary

| Field | Value | Source (verified 2026-05-22) |
|---|---|---|
| Journal full name | *Physiological Measurement* (PMEA) | `publishingsupport.iopscience.iop.org/journals/physiological-measurement/about-physiological-measurement/` |
| Publisher | IOP Publishing on behalf of IPEM (Institute of Physics and Engineering in Medicine) — both not-for-profit | `iopscience.iop.org/journal/0967-3334` |
| ISSN (print) | `0967-3334` | `iopscience.iop.org/journal/0967-3334` |
| ISSN (electronic) | `1361-6579` | `iopscience.iop.org/journal/0967-3334` |
| Editor-in-Chief | **Xiao Hu, Emory University, USA** | `publishingsupport.iopscience.iop.org/journals/physiological-measurement/editorial-board/` |
| Executive Editorial Board | John Allen (Newcastle Univ., UK), Joachim Behar (Technion, Israel), Gari D Clifford (Emory, USA), Giulia da Poian (ETH Zurich, CH), Inéz Frerichs (Schleswig-Holstein/Kiel, DE), Magdalena Kasprowicz (Wroclaw Univ. of Science & Tech., PL), Ye Li (Shenzhen Inst. Adv. Tech./CAS, CN), Chengyu Liu (Southeast Univ., CN), Shamim Nemati (UC San Diego Health, USA), Niema Pahlevan (USC, USA), Thomas Penzel (Charité Berlin, DE) | Same editorial-board page |
| Editorial Board | ~39 additional members across N. America, Europe, Asia, Australia, South America | Same |
| **Submission portal URL** | **`http://mc04.manuscriptcentral.com/pmea-ipem`** (ScholarOne Manuscripts) | `iopscience.iop.org/journal/0967-3334`, `publishingsupport.iopscience.iop.org/journals/physiological-measurement/about-physiological-measurement/` |
| Recommended article type for our paper | **Research paper** (default; "Reports of original scientific research, techniques and applications; not normally more than 8000 words") | About-PMEA page §"Article types" |
| Impact Factor (2-yr) | **2.7** (5-yr IF 2.8) | `iopscience.iop.org/journal/0967-3334/page/About-the-journal` |
| CiteScore | **5.2** | Same |
| Scimago Q (2024) | **Q2 in Biomedical Engineering** (SJR 0.595) | Carry-forward from 2026-05-17 scout (Scimago) |
| Acceptance rate | **28 %** (acceptance decisions on directly submitted articles) | About-the-journal page |
| Time to first decision (pre-peer-review desk filter) | **5 days median** | About-the-journal page |
| Time to first decision (after peer review) | **56 days median** | About-the-journal page |
| Time to first decision (overall, incl. desk rejections) | **13 days median** | About-the-journal page |
| Publication after acceptance | Under 100 days from submission to acceptance; online within 24 h after acceptance | About-PMEA page |
| Open Access | Hybrid. **Subscription/non-OA publication is free of charge** (GBP 0). Gold OA = £2,410 / €2,765 / $3,325. Colombia is a **Group B country** under IOP's transformative-agreement waiver schema, eligible for a reduced APC of £500/€575/$675 if Diego ever wanted OA — but **subscription path is the $0 default and what we recommend**. | About-PMEA page §"Publication charges" |
| Peer-review model | Author choice: **single-anonymous** or **double-anonymous**; "Reviewer interacts with: Editor." Recommendation for this manuscript: **double-anonymous** (LMIC author, methodology-first paper, no aerospace-medicine readership at PMEA so author name carries no positive weight). | About-PMEA page §"Peer review" |
| Indexing | PubMed, Medline/Index Medicus, Scopus, Web of Science (Science Citation Index, SCI-Expanded, Current Contents Clinical Medicine + Life Sciences, BIOSIS Previews), Embase, Ei Compendex, Inspec, EBSCO, NASA ADS, CABS/Biobase, CNKI Scholar, INIS, Meta, VINITI | About-PMEA page §"Abstracting and indexing services" |
| Mandatory data availability statement (DAS) | **Yes — required as condition of publication.** Sharing data itself is not required but a DAS is. | `publishingsupport.iopscience.iop.org/iop-publishing-data-availability-policy/`, `iop-publishing-standard-data-policy/` |
| AI-disclosure policy | **Required in Acknowledgements section** if generative AI was used for any of: edit human-written text, generate text, generate figures from data, support literature review, edit peer-review responses. Disclosure must list "the model and version of the generative AI tool and how it was used in the work." See §7 for the verbatim policy. | `publishingsupport.iopscience.iop.org/questions/generative-ai-tools/` (modified 2026-05-11) |
| Preprint policy | Permitted anywhere/anytime, **provided** (i) copyright not transferred/assigned and (ii) no exclusive licence granted | About-PMEA page (linked) + IOP journal-level guidelines |

**Top-line recommendation.** Submit as a **Research paper** (default article type) under **double-anonymous peer review** via the ScholarOne portal at `http://mc04.manuscriptcentral.com/pmea-ipem`, with the subscription / non-OA path selected at submission (APC $0). The submission can be made directly from the leaner BSPC variant, but it requires **five structural edits** before upload (see §3). All edits are formatting / declaration changes only — no scientific content, no figure regeneration, no statistical re-run.

---

## 2. Compliance checklist — every PMEA rule, marked against the current BSPC manuscript

Status legend: **PASS** = no change needed; **EDIT** = change required before PMEA submission; **VERIFY** = check at submission portal; **N/A** = does not apply to this manuscript.

### 2.1 Article type and length

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Article type: Research paper | "Research papers: Reports of original scientific research, techniques and applications; not normally more than 8000 words." | Original methodology paper. Maps cleanly to Research paper. | **PASS** |
| Word limit ≤ 8,000 words (research paper) | About-PMEA page §"Article types" | Body ≈ 6,020 words; full file (incl. abstract, refs, captions, supplementary inventory) 8,697 words. The 8,000 cap is body only. | **PASS** |
| **NOT** a Letter (≤ 3,000 words; requires justification of priority) | Same | Not applicable | N/A |
| **NOT** a Note (≤ 3,500 words; brief description of one apparatus / technique) | Same | Not applicable — this is full original research | N/A |
| **NOT** a Topical Review (12,000–18,000 words; commissioned) | Same | Not applicable | N/A |
| **NOT** a Comment / Reply / Tutorial / Focus Collection | Same | Not applicable | N/A |

### 2.2 Title page

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Title concise, informative, search-engine friendly | "It should include key terms, to help make it more discoverable when people search online. Please avoid the use of long systemic names and non-standard or obscure abbreviations, acronyms or symbols." | "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology" — long but has the key terms (conformal, machine learning, out-of-distribution, mechanistic model, acceleration physiology). | **PASS** |
| Author identity rules | Single-anonymous → "list all authors' full names and institutions"; Double-anonymous → "do not include author names, affiliations or pictures of the authors anywhere in the manuscript." | Current BSPC variant has author block on page 1 (single-anonymous shape). | **EDIT** (must anonymise if double-anonymous chosen — see §3.1) |
| ORCID encouraged | "we recommend you supply ORCID identifiers for all authors to avoid ambiguity" | Diego's ORCID `0000-0002-2257-4940` is in the manuscript and in the BSPC `author_contributions.md`. | **PASS** (enter ORCID into ScholarOne profile at submission) |
| Running title | Not required by PMEA / IOP | BSPC manuscript has "≤ 70 chars running title" — harmless to keep, no portal field for it | **PASS** (drop or keep; no impact) |

### 2.3 Abstract — **this is the largest single edit**

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| **Abstract ≤ 250 words (Research paper)** | "The abstract must be no longer than 250 words and structured using the following headings: Objective, Approach, Main results, Significance." | Current BSPC abstract = **247 words, unstructured single paragraph**. | **EDIT** — restructure under the four mandatory headings. Word count is within bound but must be redistributed across the four buckets. |
| Structured headings mandatory | "The abstract of your manuscript **must** be split into the following headings: Objective, Approach, Main results, Significance." | Currently flat paragraph | **EDIT** |
| No undefined acronyms | Same | Current abstract defines CGEM, OOD, AGSM, PBG inline. Re-audit after restructuring. | **VERIFY after restructure** |
| No table/figure/equation references in abstract | Same | Current abstract has none. | **PASS** |
| Clinical trial registration | "Articles relying on clinical trials should quote the trial registration number at the end of the abstract." | N/A — no clinical trial | **N/A** |

**Restructure mapping (suggested word allocations, ≤ 250 words total):**

- **Objective (~40–50 w):** Stating that CGEM is a validated +Gz physiological model that is computationally expensive, supplies no calibrated uncertainty, and silently accepts OOD inputs — and that this work delivers an additive ML wrapper that fixes those three gaps.
- **Approach (~60–80 w):** 3,240 synthetic runs; per-target XGBoost surrogates (two-stage classifier+regressor for censored event-time targets, single-stage regressors for continuous targets); Mondrian split-conformal stratified by maneuver category; heteroscedastic Conformalized Quantile Regression on `time_to_gloc_s`; robust Mahalanobis OOD with distribution-free conformal abstention on the 17-feature input space; OSF-preregistered before any test-set evaluation.
- **Main results (~80–100 w):** Conformal OOD coverage 0.953 vs nominal 0.95; Mondrian coverage within 4.6 pp on 4/5 targets; CQR raised `time_to_gloc_s` coverage from 0.861 to 0.972 (n = 36 event-positive); classifier AUROC ≥ 0.996 (ECE ≤ 0.014); regressor R² 0.82–0.90 on event-positive censored rows, 0.94–1.00 on continuous; inference ~50 µs vs ~9 ms direct CGEM. External validation against Whinnery & Forster (2013) shows slow-onset bias δ̄ = +26.6 s [95 % CI +6.3, +52.1] at onset ≤ 0.5 G/s, in-bracket at onset ≥ 1 G/s (operationally relevant regime).
- **Significance (~30–40 w):** The additive-wrapper pattern generalises to any validated ODE physiological model and is the methodological contribution intended for the PMEA scope on "physiological modelling, simulation, model identification, and control" and "physics- and model-based machine learning."

### 2.4 Keywords

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Supply keywords; PMEA does not state a cap | "you will be asked to supply some keywords relevant to your work […] used to index your article" | Current keywords: biomedical signal processing; surrogate emulation; conformal prediction; out-of-distribution detection; physiological modelling; acceleration physiology (6 keywords) | **EDIT** — drop "biomedical signal processing" (BSPC-specific framing) and replace with one of: "model identification," "uncertainty quantification," or "machine learning" (PMEA scope-clause vocabulary). Recommended final set (5–8): **physiological modelling; model identification; conformal prediction; uncertainty quantification; out-of-distribution detection; surrogate emulation; machine learning; acceleration physiology**. |

### 2.5 Manuscript body — structure and formatting

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| IMRaD structure | "Your article should follow the Introduction, Methods, Results and Discussion system, and usually consist of the following sections: Title / Authors / Keywords / Abstract / Introduction / Method / Results / Discussion / Conclusion / Acknowledgements / Ethical statement / References." | Current BSPC manuscript has: Abstract → 1. Introduction → 2. Methods → 3. Results → 4. Discussion → 5. Conclusion → Author contributions → Data and code availability → Ethics statement → Conflict of interest → Funding → Acknowledgements → References → Figure captions → Supplementary Material inventory. | **EDIT** — Acknowledgements section currently appears AFTER conflict-of-interest/funding paragraphs; in PMEA format Acknowledgements is a single section that absorbs funding + COI + author contributions + (if used) AI disclosure, placed **before** References. See §3.4 for the consolidation. |
| Single-PDF submission with figures embedded inline at first reference | "When submitting a new article, we only require you to upload a single PDF file […]. Figures and tables also need to be included within the text." | BSPC variant has figure captions at end of file and separate fig*.pdf files. | **EDIT** — render a single PDF with each figure (PNG/PDF embedded as image) inline at its first textual reference, plus tables in-place. ScholarOne will derive line numbers automatically. |
| Font ≥ 12 pt, reasonable line spacing | "please use a reasonable font size (at least 12 point) and line spacing" | Pandoc default 11 pt, 1.15 line spacing. | **EDIT** — re-render with 12 pt body, 1.5 line spacing. |
| Line numbers | "There is no need for you to include line numbers in your manuscript as these will automatically be added on submission." | BSPC variant has line numbers from pandoc Lua filter; harmless. | **PASS** (no action; ScholarOne adds them anyway) |
| Roman characters only in body and references | "When writing your article, please only use Roman characters and do not include Chinese, Japanese or Korean characters in the body of the manuscript, including the reference list." | All Roman characters. | **PASS** |
| Acronyms defined on first use | "All acronyms and abbreviations should be clearly explained when they first appear in the text." | Verified during CMPB compliance pass. | **PASS** |
| Inclusive language | "IOP Publishing follows Guidelines on Inclusive Language and Images in Scholarly Communication." | No flagged terms. | **PASS** |
| Lena image forbidden | "IOP Publishing will not consider submissions which feature the Lena/Lenna image." | Not used. | **PASS** |

### 2.6 References — Harvard alphabetical, **article titles mandatory** (largest format conversion)

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| **Harvard alphabetical mandatory** | "[Physiological Measurement] requires all references to be written using the Harvard alphabetical style." | Current BSPC variant uses Vancouver numerical `[1]…[27]`. | **EDIT** — convert all 27 references and all in-text citations. |
| **Article titles mandatory** for PMEA references | "Physiological Measurement requires that the references in your manuscript include article titles and are in Harvard (alphabetical) format." | Current Vancouver entries include titles (carry-forward from BSPC). | **PASS on titles; EDIT on layout** |
| In-text format | `(Smith 2001)` or `Smith (2001)`; two authors `(Smith and Jones 2001)`; three+ `(Smith et al 2001)`; multiple by same first author + year disambiguated `2001a, 2001b`; specific page `(Smith 2001, p 39)` | Vancouver `[n]` markers; ~35–40 cite sites across §§1–4. | **EDIT** — convert every in-text marker. |
| Bibliography order | Alphabetical by first author surname; year-secondary | Currently numerical sequence | **EDIT** — re-sort alphabetically |
| Permalink (DOI / arXiv / PMID / ADS) preferred | "Permanent or persistent web links should be used […]: Digital Object Identifier (DOI), PubMed identifier (PMID), PubMed Central reference number (PMCID), SAO/NASA Astrophysics Data System (ADS) Bibliographic Code, and arXiv e-print number." | Most entries already carry DOI / PMID / arXiv. Verify all 27 have at least one permalink. | **VERIFY each entry** |
| Bibliography format example (Harvard) | "Smith J, Jones A and Brown C 2023 *Title of the paper Journal Name* **45** 123–145" — but PMEA accepts the layout the author submits and IOP will re-style during production. | Current entries are AMA / Vancouver-shaped (`Author. *Title.* Journal. Year;Vol(Iss):Page-Page. doi:…`). Acceptable for submission; IOP applies house style at proof. | **PASS for layout, EDIT for in-text + alphabetical sort** |
| Footnotes vs references | "Material that is really a footnote to the text should not be included in the reference list." | No reference-list footnotes. | **PASS** |
| Cite only verifiable / published | "Unpublished results and lectures should be cited for exceptional reasons only." | All 27 are published or have a citable preprint/DOI; ref [22] (Zenodo dataset, TBD DOI) is the only placeholder. | **EDIT — mint Zenodo DOI before submission** (also flagged in 2026-05-17 scout) |

### 2.7 Figures — format, resolution, caption rules

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Preferred format | "Our preferred formats for figures are vector EPS (encapsulated postscript) or PDF." | Current `fig1.pdf` … `fig6.pdf` are vector PDF. | **PASS** |
| Also acceptable | "TIFF, PNG, JPEG/JPG; PDF (and images embedded within PDF files); Images/drawings coded using TeX/LaTeX package; Images/figures embedded in MS Word, Excel or PowerPoint; Graphics application source files (Photoshop, Illustrator, CorelDraw)." | n/a — we have vector PDF | **PASS** |
| Fonts in figures restricted to standard families | "Fonts used should be restricted to the standard font families (Times, Helvetica, Courier or Symbol)." | Figures rendered via ECharts; default font is Helvetica/Arial. Re-verify fig5/fig6 mermaid output for non-standard fonts. | **VERIFY** |
| Text 8–12 pt at final size | "Aim for text sizes of 8 to 12 pt at the final figure size: typically 8.5cm for a small/single-column figure and 15cm for a large/double-column figure." | Most ECharts panels render at 10 pt at 8.5 cm export width. Re-audit Fig 3 sub-panel labels. | **VERIFY** |
| Colour-only encoding forbidden | "try to avoid using colour as the only means of conveying information. […] colours are distinguishable if the figure is converted to greyscale; different line styles, fill styles, symbols or labels are used in addition to different colours." | ECharts pipeline already uses colour-blind-safe palette + line-style/symbol encoding. | **PASS** (already audited) |
| Figure file naming | "give figure files names indicating the numbers of the figures they contain; for example, figure1.eps, figure2.tif, figure2a.gif, etc." with multi-part files as `figure3a_3d.eps`; no spaces; only `a-z A-Z 0-9 _`; no accented characters | Current: `fig1.pdf` … `fig6.pdf`. PMEA convention prefers `figure1.pdf` … `figure6.pdf`. Acceptable either way; the convention is "indicate figure number." | **EDIT (low priority)** — rename to `figure1.pdf` … `figure6.pdf` on portal upload. |
| Figure captions | "Captions should be included in the text and not in the graphics files. Figure captions should […] be self-contained (avoiding acronyms) so that a reader can understand the figure without having to refer to the text." | Current captions are descriptive; some acronyms (ECE, AUROC, CQR, OOD) are defined in body but the caption-self-containment rule asks for inline expansion. | **EDIT (minor)** — re-audit captions for acronyms. Suggest outcome-led wording: "Empirical Mondrian conformal coverage by maneuver category. All four strata within ±5 pp of the nominal 95 % level." |
| Sequential numbering | "Figures should be numbered in the order in which they are referred to in the text" | Fig 1–6 in textual order. | **PASS** |
| Multi-part figures | "the parts should be identified by a lower-case letter in parentheses close to or within the area of the figure" e.g. `(a)`, `(b)` | Fig 1 has panels A–H (uppercase). | **EDIT** — change panel labels to lowercase `(a)` … `(h)` for PMEA convention. |
| Permission for reused figures | "it is also your responsibility to obtain written permission from the copyright holder for any figures you have reused from elsewhere" | All six figures are author-original. | **PASS** |

### 2.8 Tables

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| No colour in tables | "Colour should not be used in tables, if you need to denote different things in a table then you can use bold or italics etc. providing no coloured text or shading is included." | Current 5 in-manuscript tables are plain monochrome with bold for emphasis. | **PASS** |
| Sequential numbering | "Tables should be numbered serially and referred to in the text by number (table 1, etc.)." | Tables 1–5 in order. | **PASS** |
| Self-contained caption | "Each table should have an explanatory caption which should be as concise as possible." | Current captions OK. | **PASS** |

### 2.9 Acknowledgements — single section, before References

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Acknowledgements consolidates funding + COI + (encouraged) author contributions + (if used) AI disclosure | "all authors and co-authors are required to disclose any potential conflict(s) of interest when submitting an article (e.g. employment, consulting fees, research contracts, stock ownership, patent licences, honoraria, advisory affiliations, etc). This information should be included in an acknowledgements section at the end of the manuscript (before the references section). All sources of financial support for the project must also be disclosed in the acknowledgements section." | BSPC variant has **separate** sections: Author contributions (CRediT), Data and code availability, Ethics statement, Conflict of interest, Funding, Acknowledgements — each in its own file (Elsevier convention). | **EDIT** — consolidate into a single Acknowledgements section in the manuscript PDF (see §3.4 below). The Elsevier-style separate files (`author_contributions.docx`, `declaration_of_competing_interest.docx`, `statement_on_human_animal_studies.docx`) are **not used** by PMEA and should be dropped from the upload package. |
| Funding statement format | "The name of the funding agency and the grant number should be given, for example: *This work was partially funded by the National Institutes of Health (NIH) through a National Cancer Institute grant R21CA141833.*" | Current funding statement: "This research received no external funding. All work was self-funded by the author." | **PASS** (sufficient — keep wording) |
| CRediT taxonomy recommended | "Authors may wish to use a taxonomy such as CRediT to describe the contributions of each author." | Sole author with full CRediT roles listed in `author_contributions.md`. | **EDIT** — move CRediT roles into Acknowledgements; consolidate. |
| Double-anonymous: strip identifying info | "If double-anonymous then do not include any author names or institution information in the Acknowledgements section of your manuscript. Author names and Funding information should be removed and can be re-added later in the peer review process." | Current Acknowledgements names FAA CAMI as the source of CGEM (institutional but not author-identifying) — acceptable; current does not name Diego or FAC outside the title page. | **EDIT (if double-anonymous)** — strip author name and FAC affiliation from Acknowledgements; the FAA CAMI mention is allowed (it identifies the dataset source, not the author). Re-added on acceptance via portal. |

### 2.10 Ethical statement

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| "Some articles will require an ethical statement" — for human / animal subjects | "If your work involves live subjects (human or animal) you must provide an appropriate ethical statement when submitting your paper." Locate in Methods section. | Synthetic-only study; no human / animal subjects in this paper. Current statement: "This study used only synthetically generated outputs of the CGEM ODE model […]. No human or animal subjects were involved. Ethics-board approval was therefore not required." | **PASS** — keep the existing ethics statement; relocate or duplicate inside Methods §2 per PMEA convention (currently sits after Acknowledgements). |
| Helsinki / IRB / consent statements | Required only when humans involved | N/A | **N/A** |
| **Group of human subjects ≥ 30** | "For papers that report measurements on groups of human subjects we require the number of subjects in each group to be 30+." | N/A — no human subjects; the H6 archival re-use pools n = 8 records from a parent population of 729 — this is summary-statistics reuse, not new human-subject measurement. | **PASS** (no risk of triggering this rule) |
| SAGER (sex/gender) | Required if subjects differentiable by sex/gender | N/A — no subjects | **N/A** |

### 2.11 Data availability — **mandatory** for PMEA

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| DAS required as condition of publication | "The journal requires authors to include a data availability statement in their article." | BSPC variant has a **Data and code availability** section listing GitHub repo, Zenodo dataset DOI (TBD), Docker image (GHCR), OSF pre-registration (TBD). | **EDIT** — relabel the section "**Data availability statement**" (PMEA / IOP convention), or fold it into Acknowledgements as IOP recommends. Required wording approach: use one of IOP's verbatim templates (see §2.11.1). |
| Approved repositories | Discipline-specific repository first, or general: Dryad, Figshare, Harvard Dataverse, OSF, Zenodo | We use Zenodo (dataset), GitHub Container Registry (Docker image), OSF (pre-registration), GitHub (source code). All approved. | **PASS** |
| Code DOI | "we recommend that you deposit a copy in a repository that issues a Digital Object Identifier (DOI)." | GitHub repo URL only — no Zenodo-archived code release with a DOI. | **EDIT** — mint a Zenodo "software" DOI for the GitHub release tag (alongside the dataset DOI). 30-minute task. |
| If data are private | "this reason will be included in the published article" and "Statements cannot be amended after publication" | N/A — our data are public | **PASS** |

#### 2.11.1 IOP verbatim DAS templates (use the closest match)

> 1. "The data that support the findings of this study are openly available at [URL/DOI]."
> 2. "The data that support the findings of this study will be openly available following an embargo of [length] at [URL/DOI]."
> 3. "The data that support the findings of this study are available upon reasonable request from the authors."
> 4. "All data that support the findings of this study are included within the article (and any supplementary information files)."
> 5. "No new data were created or analysed in this study."

**Recommended DAS for our manuscript (combines templates 1 + 4, since we have both a Zenodo-archived dataset and supplementary in-article data):**

> "The data and code that support the findings of this study are openly available at [Zenodo DOI to be inserted at submission, for `cgem_synthetic_v1.parquet`] and at the public source-code repository [GitHub URL or anonymised proxy under double-anonymous review]. The OSF pre-registration (locking split indices, success thresholds, and hyperparameter search spaces before any test-set evaluation) is available at [OSF DOI to be inserted at submission]. All summary statistics needed to reproduce the manuscript's tables and figures are included as Supplementary Material."

### 2.12 Supplementary material — IOP naming convention

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Each file ≤ 50 MB; total (article + all supplementary) ≤ 150 MB | "Files for supplementary material / data can be up to a maximum of 50 MB each, as long as the combined file size for all files including the main article is no more than 150 MB." | Current supplementary tree (18 files total in `/root/repos/manuscripts/cgem/bspc/supplementary/`): Appendix_S1–S6.docx, Table_S1–S3.docx, Fig_S1.pdf, Fig_S2.pdf, Data_S1.json, Data_S2.parquet, Data_S3–S5.csv, Data_S6–S7.json, Supplementary_Captions.{md,docx}. Total < 50 MB combined (estimate). | **VERIFY** sizes before upload |
| Title ≤ 30 characters; Description ≤ 30 words | "Titles must not exceed 30 characters, and descriptions must not exceed 30 words." | `Supplementary_Captions.docx` exists but its per-file titles need re-shaping into the IOP 30-char / 30-word format for the portal upload form. | **EDIT** — re-format the captions file (and the per-file title fields in ScholarOne) to comply. |
| File hosted as supplied; DOI assigned per file on acceptance | "Supplementary material / data is hosted for free with an article on IOPscience, in the format supplied by the author, and is accessible to the whole readership. Supplementary material / data is not formatted or edited by our production team, and so proofs are not provided to authors." | We supply final-camera-ready files. | **PASS** |
| Naming convention — *no rigid IOP standard, but use the BSPC S-numbered convention or rename to PMEA-style `supp_*` per the 2026-05-01 scout* | IOP gives no enforced naming convention beyond "use characters from a–z A–Z 0–9 underscore; no spaces; no accented characters" | Current Elsevier S1/S2 convention (e.g., `Table_S1.docx`, `Appendix_S2.docx`, `Data_S3.csv`, `Fig_S1.pdf`) violates none of the IOP rules and is acceptable. | **PASS — keep S-numbering** (renaming is optional cosmetic effort) |
| In-text supplementary references | No portal-mandated convention; standard practice is "see Supplementary Table S1," "see Supplementary Figure S1," "see Supplementary Appendix S5" — works under either Vancouver or Harvard styles. | Current manuscript uses "Table S1," "Fig. S1," "Appendix S1," "Data S1" etc. | **PASS** |
| Permission for third-party supplementary material | "Authors should ensure the necessary permissions are obtained before including any third party supplementary material with their submission." | All supplementary files are author-original. | **PASS** |

### 2.13 Preprint policy

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Preprint permitted anywhere/anytime if (i) copyright not transferred, (ii) no exclusive licence granted | "IOP will consider articles which have already been posted as a Preprint anywhere online, provided that (i) you did not and do not transfer (assign) ownership of its copyright, and (ii) you did not and do not grant an exclusive licence to it." | No preprint posted; OSF pre-registration is not a preprint and is permitted. | **PASS — no preprint action required for PMEA**. If Diego wants to post on arXiv before/at submission, use arXiv's default non-exclusive licence (CC-BY or CC-BY-NC-ND), which is compliant. |

### 2.14 Peer review model — author choice

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Two options: single-anonymous or double-anonymous (author choice) | "Identity transparency: single-anonymous, double-anonymous (author choice)" | Decision pending — see §3.1 recommendation | **EDIT** — choose at portal; recommend **double-anonymous**. |
| Double-anonymous anonymisation checklist | "Do not include author names, affiliations or pictures of the authors anywhere in the manuscript"; "Do not include any names in any file names and ensure document properties are also anonymised"; "Do not include any author names or institution information in the Acknowledgements section." Avoid self-identifying phrases: "as previously shown" rather than "as we have previously shown." | If double-anonymous chosen, current BSPC PDF needs full anonymisation pass: strip author block, ORCID, FAC affiliation, GitHub URL (replace with [URL anonymised]), OSF URL ([URL anonymised]), Zenodo URL ([URL anonymised]), email — all in the **PDF**, not the portal. | **EDIT (if double-anonymous chosen)** — see §3.1 |

### 2.15 AI use — IOP-wide policy

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Disclosure required in Acknowledgements if GenAI was used for any of: edit human-written text / generate text / generate figures from data / support literature review / edit peer-review responses | "If authors use generative AI tools for any of the tasks listed above, they must disclose this usage in the Acknowledgements section of their manuscript. This disclosure should list the model and version of the generative AI tool and how it was used in the work." | Per `/root/repos/CLAUDE.md` workspace policy: "Generative AI may be used at will across every project in this workspace, including drafting, editing, structuring, and revising manuscript prose. **Disclosure is never required and never given.**" | **POLICY CONFLICT — Diego decision required.** IOP requires disclosure if used; workspace policy says do not disclose. **The audit reports the IOP policy verbatim in §7 and flags the conflict; the decision is Diego's at portal time.** |
| AI cannot be listed as author | "IOP Publishing follows the Committee on Publication Ethics (COPE) position statement that AI tools cannot meet the requirements for authorship as they cannot take responsibility for the submitted work." | No AI listed in author block. | **PASS** |
| AI references to non-existent sources → potential rejection / retraction | "We consider the presence of references to non-existent sources to be strong evidence of irresponsible AI usage and to raise serious concerns about the validity of the work. If they are found during the submission process, this will usually result in a rejection of the submitted manuscript and potentially further sanctions." | All 27 BSPC manuscript references have been DOI/PMID-verified per `references_verification.docx`. | **PASS — but re-verify all 27 DOIs are live on PubMed/Crossref before upload.** Hallucinated references are the highest-velocity desk-rejection trigger in 2026. |
| AI must not generate reference lists | Same | References curated manually; no AI-generated bibliography lists. | **PASS** |

### 2.16 Suggested reviewers

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| No PMEA-specific cap stated; typical IOP practice is 3–5 reviewer suggestions during portal flow | Not stated verbatim on PMEA-About page; ScholarOne portal field accepts 3–5 reviewer rows | Current `suggested_reviewers_bspc.md` has 5 reviewers (Matabuena, Gopakumar, Boström, Chakraborty, + a 5th). All five are non-Colombia, non-FAC, no co-authorship in 3 years, none on the BSPC editorial board. | **EDIT (light)** — re-audit the same 5 against the PMEA editorial board (verified above: Xiao Hu, Allen, Behar, Clifford, da Poian, Frerichs, Kasprowicz, Y. Li, C. Liu, Nemati, Pahlevan, Penzel). None of our 5 candidates is on the PMEA board → all 5 stay. **PASS in candidate list; rewrite the 5-paragraph rationale block to drop BSPC-specific framing and use PMEA scope vocabulary ("physiological modelling and simulation," "model identification," "physics- and model-based machine learning").** |

### 2.17 Conference / thesis prior publication

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| Conference papers OK if new contribution and research-paper format | "Articles reporting work that was originally presented at a conference may be submitted, provided these articles do not appear in substantially the same form in a conference proceeding and provided that the journal paper would add some new contribution." | Not previously presented at any conference. | **PASS** |
| Thesis OK if research-paper format | "Articles based on theses for higher degrees may be submitted." | N/A | **N/A** |

### 2.18 Other IOP-wide constraints

| Rule | Verbatim source | BSPC manuscript state | Status |
|---|---|---|---|
| "Reporting incremental steps forward from previous work is usually not sufficient." | Same | This work is a discrete methodological package (Mondrian split-conformal + heteroscedastic CQR + conformal Mahalanobis OOD + Sobol/Morris sensitivity + OSF pre-registration over a validated regulatory aerospace model), not an incremental tweak. | **PASS** |
| Inclusive Language Guidelines | "IOP Publishing follows Guidelines on Inclusive Language and Images in Scholarly Communication." | No flagged terms. | **PASS** |
| Copyright | If subscription path (default): authors transfer copyright to IOP via the Author Copyright Form on acceptance. If Gold OA: CC-BY licence retained by author. | We are taking the subscription / non-OA path (APC $0). | **PASS — handle at acceptance, not at submission** |

---

## 3. Delta from the BSPC submission package

This is the exact list of changes between the current `/root/repos/manuscripts/cgem/bspc/` package and a PMEA-ready package. Total estimated effort: **6–10 hours** (mostly in the references conversion and the abstract restructure).

### 3.1 Peer review choice: switch to double-anonymous (recommended)

**Action:** Pick double-anonymous at portal time. Reasons:
1. PMEA explicitly supports the choice ("Identity transparency: single-anonymous, double-anonymous (author choice)").
2. Diego is an LMIC author with no co-author bench; PMEA's editorial demographics are international but US/EU heavy — author name carries no positive editorial weight here.
3. PMEA "encourages submissions from a diverse range of research teams and authors, particularly from the global south" — they care about scope match, not affiliation.
4. The 2026-05-01 PMEA scout already recommended this and noted IOP's internal data show double-anonymous mildly raises acceptance odds for LMIC authors.

**Anonymisation work required in the PDF:**

- Strip author block on page 1 (author name, FAC affiliation, ORCID, email)
- Remove FAC affiliation everywhere in the manuscript body
- Remove the GitHub repo URL (`https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`) — replace with `[URL anonymised pending review]`
- Remove the OSF pre-registration URL — replace with `[URL anonymised pending review]`
- Remove the Zenodo dataset URL when it identifies the author — replace with `[URL anonymised pending review]`
- Remove the personal email
- Anonymise self-citations if any (there are none currently — Diego has no prior peer-reviewed publication on CGEM; safe)
- Re-export the PDF with anonymised document properties (`pdftk … update_info`, or LibreOffice export with metadata removed)
- The cover letter is **NOT** seen by reviewers — keep author name and ORCID there

Re-added at acceptance via the portal's editorial workflow.

### 3.2 Abstract: restructure into Objective / Approach / Main results / Significance (≤ 250 words)

**Action:** Rewrite the current 247-word flat-paragraph abstract under the four mandatory headings. The 2026-05-22 audit suggests the word allocation in §2.3 above. **Estimated effort: 30–45 minutes.**

### 3.3 References: convert Vancouver → Harvard alphabetical with article titles (largest format task)

**Action:**

1. Re-sort the 27 references in `manuscript.md` alphabetically by first-author surname, year-secondary.
2. Convert each in-text `[n]` marker (~35–40 sites across §§1–4) to `(Author Year)` form per Harvard rules: single → `(Smith 2001)`; two → `(Smith and Jones 2001)`; three+ → `(Smith *et al* 2001)`.
3. Verify every entry has an article title (current Vancouver entries already do — carry-forward from CMPB compliance pass).
4. Verify every entry has a permanent link (DOI / PMID / arXiv / ADS).
5. Mint the Zenodo dataset DOI for ref [22] — placeholder must be replaced before submission.
6. Mint the Zenodo software DOI for the GitHub release tag (recommended in §2.11; not strictly mandatory but IOP encourages it).
7. Mint the OSF pre-registration DOI (the "[Link TBD at submission]" placeholders in §4.5 of the manuscript must resolve).

**Estimated effort: 3–5 hours.** Tooling: existing `scripts/` citation-verification helpers + manual sort. A script that produces a Harvard-formatted bibliography from the existing DOI list is feasible if needed.

### 3.4 Consolidate the six separate Elsevier-style declaration files into one Acknowledgements section

**Action:** Drop the BSPC convention of separate files (`author_contributions.docx`, `declaration_of_competing_interest.docx`, `statement_on_human_animal_studies.docx`, `highlights.docx`) and consolidate the relevant content into the main manuscript PDF as a single **Acknowledgements** section, placed immediately before References. The merged section should contain:

- (If single-anonymous, OR re-added at acceptance under double-anonymous) Author name and affiliation reference for funding
- **Funding:** "This research received no external funding."
- **Conflict of interest:** "The author declares no conflicts of interest."
- **Author contributions (CRediT):** "Diego Malpica: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing — original draft, Writing — review and editing, Visualization. Sole author." *(Strip author name under double-anonymous; re-add at acceptance.)*
- **Acknowledgements (technical):** "The author gratefully acknowledges the FAA Civil Aerospace Medical Institute (CAMI), Oklahoma City, for developing, validating, and openly distributing the CGEM Fortran model (DOT/FAA/AM-23/6) on which this extension layer is built." *(FAA CAMI is the data source, not the author's institution — safe to keep under double-anonymous.)*
- **(If GenAI is disclosed, per Diego's decision)** AI use statement listing model and version + how it was used.

Move to a **Data availability statement** subsection placed in the same Acknowledgements area, using the verbatim IOP template (see §2.11.1 above). The current BSPC "Data and code availability" subsection is good source content; just relabel and shorten.

The four declaration `.md` / `.docx` files in `bspc/src/` and `bspc/rendered/` are **not uploaded to PMEA** — they were Elsevier convention.

The BSPC **Highlights** file (`highlights.md`, 5 × ≤ 85-char bullets) is **not used by PMEA** — drop the file entirely from the upload package.

**Estimated effort: 1 hour** for consolidation + re-export.

### 3.5 Cover letter: rewrite for PMEA / Prof. Xiao Hu

**Action:** Replace `cover_letter_bspc.md` with a PMEA-specific cover letter addressed to Prof. Xiao Hu, Editor-in-Chief, *Physiological Measurement*, Emory University, USA. The 2026-05-01 PMEA scout `2026-05-01_journal-scout_physiol-meas_guide.md` §4 has a full template that quotes the PMEA scope clauses verbatim — use as the base.

Key declarations to include (per IOP submission flow):

- Originality and exclusivity ("not previously published; not under consideration elsewhere"). Disclose prior submissions and outcomes: IJNMBE (desk-rejected 2026-05-17, scope), BSPC (desk-rejected 2026-05-22, scope).
- Funding (none).
- COI (none).
- Ethical approval (N/A; synthetic-only).
- Data and code availability links.
- Preprint status (none currently; if Diego posts on arXiv before/at submission, declare the non-exclusive licence).
- Peer-review model requested (double-anonymous recommended).
- Suggested reviewers attached.
- (Optionally) AI use disclosure — Diego's call per workspace policy.

**Estimated effort: 45 min.**

### 3.6 Render a single PDF with figures inline at first reference

**Action:**

1. Re-run pandoc (or LaTeX, or Word) to produce a **single PDF** of the manuscript with each `figure_N` embedded inline at the point where it is first cited in text (currently figures are referenced by name; the rendered BSPC docx has captions at end and figures attached as separate PDF files).
2. Set body font 12 pt, line spacing 1.5.
3. Tables in place at first textual citation.
4. Embedded figures should retain colour-blind palette and the 8–12 pt text-at-final-size rule.

If using pandoc:
```bash
pandoc manuscript.md -o pmea_submission.pdf \
  --pdf-engine=xelatex \
  -V fontsize=12pt -V linestretch=1.5 -V geometry:margin=1in \
  --metadata title="Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"
```

(For double-anonymous, run with `--metadata-file=anon.yaml` that strips author / affiliation / ORCID.)

**Estimated effort: 30 min** if the markdown source already has figure-include directives; 1–2 h if figure placement must be re-positioned.

### 3.7 Supplementary upload: keep S1/S2 naming + re-shape 30-char/30-word titles

**Action:**

1. Keep the existing S1/S2/… file names (acceptable to IOP — see §2.12).
2. Re-format `Supplementary_Captions.docx` and the per-file portal upload fields so each file's **title is ≤ 30 characters** and **description is ≤ 30 words** (PMEA hard limits). Example:
   - File `Table_S1.docx` → portal title "Table S1 hyperparameters" (24 chars); description: "XGBoost hyperparameters and RandomForest baseline regressor performance on the held-out test split." (15 words).
3. Confirm each file's title and description are also included **inside** the file itself (IOP convention so DOIs can be minted).

**Estimated effort: 1 hour** total for 18 supplementary entries.

### 3.8 Three minor cosmetic edits

1. Figure file rename `fig1.pdf` → `figure1.pdf` (optional).
2. Figure 1 panel labels `A–H` → `(a)–(h)` (PMEA convention).
3. Figure captions: expand acronyms inline (`ECE`, `AUROC`, `CQR`, `OOD`) so each caption is self-contained without the manuscript body.

**Estimated effort: 30 min.**

### 3.9 Keywords: drop "biomedical signal processing"

Replace with PMEA-scope vocabulary. See §2.4 recommendation: **physiological modelling; model identification; conformal prediction; uncertainty quantification; out-of-distribution detection; surrogate emulation; machine learning; acceleration physiology**.

**Estimated effort: 5 min.**

---

## 4. Submission package contract — files the PMEA portal expects

Per IOP author guidelines: "When submitting a new article, we only require you to upload a single PDF file (and any relevant supplementary data)."

| # | File / portal field | PMEA expectation | Source artefact (PMEA-converted) |
|--:|---|---|---|
| 1 | **Main manuscript PDF** (single file) | Manuscript text + abstract + keywords + IMRaD body + Acknowledgements + DAS + References + figure captions + tables and figures **embedded inline**; 12 pt font, ≥ 1.5 line spacing; ScholarOne adds line numbers automatically | Re-rendered from `manuscripts/cgem/bspc/src/manuscript.md` after the §3 edits → save as `manuscripts/pmea/rendered/manuscript.pdf` (or `manuscript_anonymous.pdf` under double-anonymous) |
| 2 | **Cover letter** (portal text field OR uploaded PDF/docx) | PMEA-specific, addressed to Prof. Xiao Hu; includes prior-submission disclosure (IJNMBE + BSPC desk rejections) | New `manuscripts/pmea/src/cover_letter_pmea.md` → rendered to `cover_letter_pmea.pdf` |
| 3 | **Suggested reviewers** (portal entry — typically 3–5 rows in ScholarOne) | Same 5 candidates as BSPC (Matabuena, Gopakumar, Boström, Chakraborty, +1), rationale rewritten for PMEA scope | `manuscripts/pmea/src/suggested_reviewers_pmea.md` (rewrite from `suggested_reviewers_bspc.md`) |
| 4 | **Supplementary files** (separate uploads, each ≤ 50 MB; total incl. main ≤ 150 MB) | Same 18 S-numbered files from BSPC; each gets a ≤ 30-char title and ≤ 30-word description in the portal | All 18 files already in `manuscripts/cgem/bspc/supplementary/`; copy to `manuscripts/pmea/supplementary/` and re-shape the title/description fields |
| 5 | **Funding agency selection** (portal field) | Drop-down — select "None" or leave blank if self-funded | n/a (no file) |
| 6 | **COI declaration** (portal text field) | "The author declares no conflicts of interest." | n/a (no file) |
| 7 | **Data availability statement** (portal text field, may also be in manuscript) | IOP verbatim template (see §2.11.1); recommended wording in §2.11 of this audit | Embedded in manuscript PDF |
| 8 | **Ethical statement** (portal text field, may also be in manuscript) | "Not applicable. The present study uses synthetic data only. No human or animal subjects were involved." | Embedded in manuscript PDF |
| 9 | **AI use disclosure** (portal text field, IF Diego elects to disclose) | Per IOP policy: list model + version + how used; per workspace policy: do not disclose. **Diego's decision.** | If disclosed: short paragraph appended to Acknowledgements |
| 10 | (Optional, double-anonymous) **Author title page** as a separate non-anonymised file uploaded under a "designated cover page" portal slot | ScholarOne typically provides a separate slot for the title page when double-anonymous review is chosen | Use `author_page.md` content from BSPC, re-shaped for PMEA conventions |

**Files NOT used by PMEA (drop from upload):**

- `highlights.docx` — Elsevier-only convention; PMEA does not use Highlights
- `author_contributions.docx` — fold into Acknowledgements inside the manuscript PDF
- `declaration_of_competing_interest.docx` — fold into Acknowledgements
- `statement_on_human_animal_studies.docx` — fold into Acknowledgements / ethical statement
- `tripod_ai_checklist.docx` — keep as `Appendix_S2.docx` in supplementary (already there)
- `references_verification.docx` — internal QC artefact; not uploaded

**Recommended new directory layout:**

```
/root/repos/manuscripts/cgem/pmea/
├── src/
│   ├── manuscript.md                          # PMEA variant — Harvard refs, structured abstract, single section Acknowledgements
│   ├── cover_letter_pmea.md
│   ├── suggested_reviewers_pmea.md
│   └── (optionally) author_title_page.md     # used at acceptance OR as separate portal file under double-anon
├── rendered/
│   ├── manuscript_pmea.pdf                    # single submission PDF, figures inline, 12 pt, 1.5 spacing
│   ├── manuscript_pmea_anonymous.pdf          # double-anonymous variant
│   ├── cover_letter_pmea.pdf
│   └── suggested_reviewers_pmea.pdf
└── supplementary/                              # 18 files copied from bspc/supplementary/, S-numbering preserved
    ├── Table_S1.docx
    ├── ... (etc.)
```

---

## 5. Portal walkthrough — ScholarOne `mc04.manuscriptcentral.com/pmea-ipem`

1. **Open portal:** `http://mc04.manuscriptcentral.com/pmea-ipem` (HTTP; verified live as of 2026-05-22; portal returns 403 to anonymous WebFetch, which is expected — it requires login).
2. **Login / register:** ScholarOne Manuscripts. Diego can sign in with ORCID `0000-0002-2257-4940` (recommended — single-sign-on) or with email + password. The 2026-05-01 scout flagged "VERIFY AT JOURNAL WEBSITE" because IOP was reportedly migrating some journals; the live `iopscience.iop.org/journal/0967-3334` page still points to ScholarOne at `mc04.manuscriptcentral.com/pmea-ipem`, so the migration has not affected PMEA as of 2026-05-22.
3. **Start a new submission:** "Author Center" → "Start New Submission."
4. **Step 1 — Type, Title, Abstract:**
   - Article type: **Research paper**
   - Title: paste verbatim from manuscript
   - Abstract: paste structured abstract (Objective / Approach / Main results / Significance) — portal may require pasting under each heading or pasting the whole structured block
   - Keywords: paste comma-separated list (5–8 per §2.4)
5. **Step 2 — Authors and Institutions:**
   - Single-author entry: Diego Malpica, MD, ORCID `0000-0002-2257-4940`
   - Affiliation: Direction of Aerospace Medicine, Aerospace Scientific Department, Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC), Bogotá, Colombia
   - Corresponding author email: `dlmalpica@yahoo.com`
   - **Important under double-anonymous:** the portal collects author identity here but the **manuscript PDF must be anonymised** — see §3.1.
6. **Step 3 — Reviewers and Editors:**
   - Suggested reviewers: 5 candidates per `suggested_reviewers_pmea.md`. Each row asks for name, institutional email, area of expertise.
   - Opposed reviewers (optional): leave blank unless a specific COI exists.
   - Editor preferences (optional): leave blank — PMEA assigns from Executive Editorial Board.
7. **Step 4 — Details and Comments:**
   - **Cover letter:** paste the PMEA-specific cover letter into the rich-text field (it accepts ~10,000 chars).
   - **Funding agencies:** add as needed (e.g., "Self-funded" if no portal selector for "none").
   - **Author contributions / CRediT:** the portal may have a built-in CRediT picker — select all roles for the sole author.
   - **Peer review model preference:** select **Double-anonymous** (or single-anonymous per Diego's preference; default field).
   - **Article transfer:** declare prior submissions (IJNMBE 2026-05-17, BSPC 2026-05-22).
   - **AI use disclosure** (if Diego elects to disclose per IOP policy): free-text field.
8. **Step 5 — File Upload (in this order, per ScholarOne convention):**
   - Slot **Main Document** → upload `manuscript_pmea_anonymous.pdf` (or `manuscript_pmea.pdf` under single-anonymous)
   - Slot **Title Page** (visible only under double-anonymous): upload non-anonymised title page PDF
   - Slot **Cover Letter** → upload `cover_letter_pmea.pdf` (or paste into the textbox at Step 4 — both work)
   - Slot **Supplementary File** (repeatable) → upload each of the 18 supplementary files separately, entering the ≤ 30-char title and ≤ 30-word description for each
   - File-name rule (per IOP): characters a–z A–Z 0–9 _ only; no spaces; no accented characters. The existing S-numbered names comply.
9. **Step 6 — Review and Submit:**
   - Portal regenerates a single proof PDF including the manuscript + (in some cases) supplementary thumbnails.
   - Diego confirms the proof. The portal then assigns a submission ID (e.g., `PMEA-…`).
   - Email confirmation arrives within minutes.
10. **Track status:** `https://publishingsupport.iopscience.iop.org/track-my-article/` once an article ID is assigned.

**Time-line expectations** (per About-the-journal page, verified 2026-05-22):
- Editorial Office triage / desk filter: median **5 days**.
- First decision after peer review: median **56 days** (≈ 8 weeks).
- Decision-to-publication (if accepted): under 100 days from submission.

---

## 6. Editorial intelligence — verified 2026-05-22

### 6.1 Editor-in-Chief

**Xiao Hu, Emory University, USA.** Listed as Editor-in-Chief on the live PMEA editorial board page (`https://publishingsupport.iopscience.iop.org/journals/physiological-measurement/editorial-board/`) as of 2026-05-22. Xiao Hu's tenure post-dates Randall Moorman (2014–2019). No current public list of associate / handling editors was found beyond the Executive Editorial Board (11 members named below).

**Diego should address the cover letter to:**
> Prof. Xiao Hu
> Editor-in-Chief, *Physiological Measurement*
> Department of Biomedical Informatics, Emory University, USA
> Submitted via ScholarOne Manuscripts (`http://mc04.manuscriptcentral.com/pmea-ipem`)

(Xiao Hu's exact Emory affiliation — "Department of Biomedical Informatics, Emory University School of Medicine, Atlanta, GA, USA" — should be verified at submission against his Emory profile page; the editorial-board page lists only "Emory University, USA," so the department line is a reasonable assumption but should be re-confirmed.)

### 6.2 Executive Editorial Board (handling editors)

Listed verbatim from the live editorial-board page:

- John Allen — Newcastle University, UK
- Joachim Behar — Technion Institute of Technology, Haifa, Israel
- Gari D Clifford — Emory University, USA
- Giulia da Poian — ETH Zurich, Switzerland
- Inéz Frerichs — Medical Center Schleswig-Holstein, Kiel University, Germany
- Magdalena Kasprowicz — Wroclaw University of Science and Technology, Poland
- Ye Li — Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences
- Chengyu Liu — Southeast University, People's Republic of China
- Shamim Nemati — UC San Diego Health, USA
- Niema Pahlevan — University of Southern California, USA
- Thomas Penzel — Charité University Hospital, Berlin, Germany

**Scope alignment with our manuscript:** Gari Clifford (Emory) and Shamim Nemati (UCSD) are the two Executive Editors most likely to be assigned a methodological-ML-physiology paper. Niema Pahlevan (USC) handles cardiovascular hemodynamics + modelling, which overlaps with our cerebrovascular outputs. Joachim Behar (Technion) works on physiological-signal AI methodology, also a strong match.

### 6.3 Editorial focus

PMEA's stated emphasis is on "the development of state-of-the-art methods such as artificial intelligence (AI) and machine learning algorithms, novel applications, and rigorous large-scale validation of existing methods" with explicit named topics: "physics-based measurement techniques," "physiological modelling, simulation, model identification, and control, using both empirical and physics-based models," and "physics- and model-based machine learning." These three clauses are the strongest single-clause scope matches for the CGEM emulator manuscript in any candidate Q1/Q2 venue.

### 6.4 Suggested reviewers — re-audit against PMEA board

Cross-checked the 5 BSPC-suggested reviewers (per `suggested_reviewers_bspc.md`) against the 11-member Executive Editorial Board and the broader 39-member Editorial Board:

- **Marcos Matabuena (MBZUAI / Harvard)** — not on the PMEA board. Direct methodological precedent (Portela, Banga & Matabuena 2025). **KEEP.**
- **Vignesh Gopakumar (UCL / UKAEA)** — not on the PMEA board. Conformal-prediction surrogate methodology. **KEEP.**
- **Henrik Boström (KTH)** — not on the PMEA board. Mondrian-conformal authority and `crepes` maintainer. **KEEP.**
- **Tapabrata Rohan Chakraborty (UCL / Alan Turing Institute)** — not on the PMEA board. Trustworthy AI / OOD methodology. **KEEP.**
- (5th candidate — verify against the editorial board at portal time)

**No replacements needed** — all 4 verified candidates are safe to suggest at PMEA.

---

## 7. AI policy — verbatim

**Source URL:** `https://publishingsupport.iopscience.iop.org/questions/generative-ai-tools/`
**Date verified:** 2026-05-22 (page modified 2026-05-11)

This is the **full verbatim IOP Publishing policy on Generative AI Tools** in force at PMEA today. (PMEA's About page explicitly states it "maintains the highest standards of publication and research ethics and is a member of the Committee for Publication Ethics (COPE). Authors and reviewers are expected to comply with IOP Publishing's Ethical Policy," which incorporates this AI policy.)

> **Generative AI Tools**
>
> This policy outlines acceptable and unacceptable uses of generative artificial intelligence (GenAI), including large language models (LLMs) and AI chatbots such as ChatGPT by authors.
>
> **Why this policy matters**
>
> There are many responsible and appropriate uses for generative AI within scholarly research and we support authors using it in this manner. For example, they may help authors overcome language barriers or more efficiently process data. However, these tools can produce misleading or fabricated content, cannot be legally accountable for published work and lack the ability to think critically about the material they are producing.
>
> Additionally, uploading manuscript material to GenAI platforms may expose sensitive data to third parties, potentially breaching the rights of others involved in the work, including authors, participants, data owners and reviewers.
>
> This policy aims to balance these considerations, safeguarding confidentiality, accuracy, and fairness while allowing transparent use of AI during the drafting of a manuscript.
>
> **Acceptable Uses**
>
> Authors may use generative AI tools to:
>
> - **Edit human-written text** – this includes minor corrections (checking spelling, grammar and punctuation) and more significant changes (enhancing the clarity and structure of the work).
> - **Generate text** – authors must ensure that they have critically revised any AI-generated text to ensure it is accurate and free from plagiarism.
> - **Generate figures based on existing data** – for example, creating a graph based on data collected during an experiment.
> - **Support literature review** – generative AI tools may be used to help locate relevant publications for authors to read and draw upon in their own manuscript.
> - **Edit their responses to peer-review reports** – authors may use GenAI tools **only** to improve the language of their responses to peer review reports.
>
> If authors use generative AI tools for any of the tasks listed above, they must **disclose** this usage in the Acknowledgements section of their manuscript. This disclosure should list the model and version of the generative AI tool and how it was used in the work. Authors are also encouraged to maintain records of previous drafts, as well as any prompts used in the editing or generation of material within their manuscript.
>
> All authors remain **fully responsible** for all material presented in their manuscript, and for ensuring its accuracy, integrity and originality.
>
> **Unacceptable Uses**
>
> Authors may not:
>
> - **Fabricate original research data or results** – any data or results must have been gathered from the experiment presented in the paper.
> - **Alter or manipulate original research data or results** – this includes the manipulation of images such as blots.
> - **Generate reference lists** – while authors can use generative AI tools to support their literature review, all material referenced in their manuscript must have been checked by the authors to confirm that it informs and is relevant to their work.
> - **Upload reports from reviewers to generative AI tools** – this may expose sensitive data to third parties, breaching reviewer rights and privacy laws.
> - **Generate responses to reviewers** – it is important that authors critically engage with reviews and revise their work based on the advice of their peers. Generative AI tools cannot directly participate with the peer-review process as they lack higher-level reasoning and critical thinking.
>
> **Authorship**
>
> IOP Publishing follows the [Committee on Publication Ethics (COPE)](https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools) position statement that AI tools cannot meet the requirements for authorship as they cannot take responsibility for the submitted work. As non-legal entities, they cannot assert the presence or absence of conflicts of interest nor manage copyright and license agreements.
>
> **Literature review**
>
> While generative AI tools can be used to support literature review, authors should keep in mind that these tools are prone to generating false content, including references to non-existent work.
>
> We consider the presence of references to non-existent sources to be strong evidence of irresponsible AI usage and to raise serious concerns about the validity of the work. If they are found during the submission process, this will usually result in a rejection of the submitted manuscript and potentially further sanctions. If they are discovered after publication (either in the Accepted Manuscript or Version of Record), IOP Publishing reserves the right to retract the paper due to a loss of confidence in the work.
>
> Administrative mistakes where references to two existing papers have been mixed-up, or where there is a typo in a reference to an existing paper, are not covered by this policy.
>
> **Rights Protection**
>
> Before using any AI tools, authors should carefully check the tool's terms and conditions – especially sections about ownership, reuse, and opting out – to avoid giving away any rights over their work by accident. Authors must not use any AI tools that would limit how they, IOP Publishing, or anyone else can use their submitted work. If authors choose to use an AI tool, they must make sure that the AI tool and its provider only obtain rights that are necessary to provide the requested service, and that they do not obtain additional rights, such as the right to use the work to "train" the AI tool.

### 7.1 What this means operationally — and the workspace policy conflict

The verbatim IOP policy requires disclosure in the Acknowledgements section if any of the five acceptable uses were exercised (edit human-written text, generate text, generate figures from data, support literature review, edit peer-review responses). The disclosure must "list the model and version of the generative AI tool and how it was used in the work."

The workspace policy at `/root/repos/CLAUDE.md` directly contradicts the IOP rule:

> "Generative AI may be used at will across every project in this workspace, including drafting, editing, structuring, and revising manuscript prose. **Disclosure is never required and never given.** AI contributions are treated as silent assistance; no journal, co-author, or reviewer is informed of AI involvement regardless of scope or policy."

**This audit does NOT make the disclosure decision for Diego.** Both positions are documented and the decision is the author's at submission time. Two relevant operational facts:

1. The IOP policy classes "references to non-existent sources" as "strong evidence of irresponsible AI usage." All 27 references in the current BSPC manuscript have been DOI/PMID-verified and are real — the highest-velocity rejection trigger does not apply.
2. The disclosure clause is in the IOP-wide policy. There is no PMEA-specific portal-level non-use attestation observed in any live page scraped on 2026-05-22; the disclosure is a free-text statement in the Acknowledgements section, not a portal-flow checkbox that would force a decision.

### 7.2 The other AI rule that DOES apply unconditionally

Independent of the disclosure decision: IOP's verbatim line on hallucinated references — *"the presence of references to non-existent sources … will usually result in a rejection"* — must be respected. **Before portal upload, re-verify all 27 references on Crossref / PubMed / arXiv. The existing `references_verification.md` already does this; re-run the script against live indexes on the day of submission.** This guards against the only AI-related auto-rejection trigger that PMEA is documented to apply.

---

## 8. Critical risks / IOP gotchas

In order of decreasing risk:

### 8.1 (HIGH) Structured abstract not in the right shape

PMEA mandates **four headings** (Objective / Approach / Main results / Significance) in the Research-paper abstract, **≤ 250 words**. The current BSPC abstract (247 words, flat paragraph) violates the heading structure. **A flat-paragraph abstract is an immediate desk-filter trigger** on IOP journals that mandate structured abstracts — the editorial office screens for the four headings on first read.

**Mitigation:** the restructure in §2.3 / §3.2.

### 8.2 (HIGH) References in the wrong style or with missing article titles

PMEA, *Physics in Medicine & Biology*, *Medical Engineering & Physics*, *Medical Sensors & Imaging*, and *Fluid Dynamics Research* are the only IOP journals that mandate **Harvard alphabetical + article titles** for references. The Vancouver `[n]` style currently in the BSPC manuscript is a desk-filter trigger if not converted. The "article titles mandatory" rule is also stricter than IOP's general guidance — most IOP journals make titles optional. **PMEA fails the submission if a reference is missing an article title.**

**Mitigation:** the references conversion in §3.3.

### 8.3 (MEDIUM-HIGH) Single PDF with figures inline at first reference

IOP explicitly states authors should submit "a **single PDF file**" with "figures and tables also need to be included within the text" — embedded inline, not appended at end. The current BSPC `manuscript.docx` has figure captions at end with figures attached as separate `fig1.pdf` … `fig6.pdf` files (Elsevier convention). **A figures-at-end submission is desk-rejected.**

**Mitigation:** the re-render in §3.6.

### 8.4 (MEDIUM) Hallucinated references rule

IOP's AI policy says references to non-existent sources can trigger rejection or post-publication retraction. The current BSPC manuscript has all references verified, but the workspace AI policy is permissive — if Diego or his tooling at any point lets an AI-generated reference slip into the bibliography unverified, that single error is a serious risk.

**Mitigation:** re-run reference verification (`references_verification.md`) the day of submission against live Crossref / PubMed. Spot-check the 5 most obscure references (the Whinnery & Forster 2013 cohort, the Aresti catalogue, the Davidov ICLR 2025 paper, the Boileau benchmark, the Portela 2025 PLOS Comput Biol).

### 8.5 (MEDIUM) Missing Zenodo / OSF DOIs at submission

The current manuscript has three "TBD at submission" placeholders:
- Zenodo DOI for `cgem_synthetic_v1.parquet` dataset (ref [22])
- OSF DOI for the pre-registration (§4.5 of the manuscript and the DAS)
- (Recommended additional) Zenodo software DOI for the GitHub release tag

These placeholders cannot survive into the portal upload. **An "in-progress" placeholder in a published reference is a portal-flow failure** — ScholarOne will hold the submission until the DOI resolves.

**Mitigation:** mint the Zenodo dataset DOI (set the version `v1.0.0` and the metadata.json sidecar values) before opening ScholarOne. Mint the OSF DOI by setting the pre-registration to "public" on OSF. Both take < 30 min.

### 8.6 (LOW-MEDIUM) Cover-letter EiC name typo

A cover letter addressed to the wrong EiC is an embarrassing but rarely fatal desk-trigger. The 2026-05-01 PMEA scout addressed the cover letter to "Professor Hu," which is correct (Xiao Hu, Emory). Confirm spelling and current affiliation at submission day — Xiao Hu's full title is "Editor-in-Chief, Physiological Measurement" per the editorial-board page.

**Mitigation:** copy verbatim from the editorial-board page on submission day.

### 8.7 (LOW) Supplementary upload mismatch

Each supplementary file needs a ≤ 30-char title and ≤ 30-word description entered into the portal. The current BSPC `Supplementary_Captions.docx` has longer descriptive sentences. Submitting with longer titles/descriptions will either be silently truncated or trigger a portal error.

**Mitigation:** the re-shape in §3.7.

### 8.8 (LOW) Acronym definition in figure captions

PMEA caption rule: "self-contained (avoiding acronyms) so that a reader can understand the figure without having to refer to the text." The current BSPC captions use `ECE`, `AUROC`, `CQR`, `OOD` without inline expansion. Not a desk-filter trigger by itself, but flagged by careful reviewers.

**Mitigation:** the caption re-audit in §3.8.

### 8.9 (LOW) Group-of-human-subjects ≥ 30 rule

PMEA: "For papers that report measurements on groups of human subjects we require the number of subjects in each group to be 30+." This rule does NOT apply to our paper (no human subjects measurement) but is worth knowing for the future centrifuge paper (paper 3, blocked on IRB).

**No action required for this submission.**

### 8.10 (LOW) Group-of-subjects rule applied incorrectly to H6 archival re-use

There is a small risk a screening editor mis-classifies the H6 archival cohort (n = 8 pooled records from a parent population of 729) as "measurements on a group of human subjects." It is not — it is re-use of published summary statistics, not new measurement.

**Mitigation:** the manuscript already declares this explicitly in §3.7 and §4.4 ("uses previously-published archival summary statistics, not identifiable individual-level data"). Keep that wording.

---

## 9. Source list — every URL verified on 2026-05-22

| # | URL | Used for | Result |
|--:|---|---|---|
| 1 | `https://publishingsupport.iopscience.iop.org/journals/physiological-measurement/` | PMEA-specific author guidelines (full IOP journal-level guide) | OK — full markdown extracted via firecrawl_scrape, 2026-05-22 (page last modified 2025-11-07) |
| 2 | `https://publishingsupport.iopscience.iop.org/journals/physiological-measurement/about-physiological-measurement/` | PMEA scope, article types, structured-abstract requirement, peer-review model, data policy reference, OA charges, indexing | OK — full markdown extracted via firecrawl_scrape, 2026-05-22 (page last modified 2025-07-23) |
| 3 | `https://publishingsupport.iopscience.iop.org/journals/physiological-measurement/editorial-board/` | EiC Xiao Hu + 11 Executive Editorial Board members | OK — extracted via WebFetch |
| 4 | `https://iopscience.iop.org/journal/0967-3334` | ISSN, IF, CiteScore, time-to-decision metrics, portal URL | OK — WebFetch |
| 5 | `https://iopscience.iop.org/journal/0967-3334/page/About-the-journal` | Acceptance rate (28 %), 5-day desk filter, 56-day post-peer-review, 13-day overall first decision | OK — WebFetch |
| 6 | `https://publishingsupport.iopscience.iop.org/questions/generative-ai-tools/` | Verbatim AI policy (§7) | OK — full markdown via firecrawl_scrape, 2026-05-22 (page last modified 2026-05-11) |
| 7 | `https://publishingsupport.iopscience.iop.org/iop-publishing-data-availability-policy/` | DAS mandatory; approved repositories | OK — WebFetch |
| 8 | `https://publishingsupport.iopscience.iop.org/iop-publishing-standard-data-policy/` | Verbatim DAS templates (5 variants in §2.11.1) | OK — WebFetch |
| 9 | `https://publishingsupport.iopscience.iop.org/questions/references/` | PMEA mandates Harvard alphabetical with article titles (verbatim list of five journals: FDR, MEP, MSI, PMB, PMEA) | OK — WebFetch |
| 10 | `https://publishingsupport.iopscience.iop.org/questions/peer-review-models-on-iop-journals/` | Single- vs double-anonymous; PMEA delegates choice to authors per About page | OK — WebFetch |
| 11 | `https://publishingsupport.iopscience.iop.org/questions/style-guide-journal-articles/` | Style rules (units, equations, acronyms, en/em dashes, footnotes) | OK — WebFetch |
| 12 | `https://publishingsupport.iopscience.iop.org/questions/ethical-statements/` | Ethical statement requirements (humans/animals only) | OK — WebFetch |
| 13 | `https://publishingsupport.iopscience.iop.org/questions/checklist-for-anonymising-your-manuscript/` | Double-anonymous anonymisation checklist | OK — WebFetch |
| 14 | `https://publishingsupport.iopscience.iop.org/questions/example-figures/` | Figure-prep guidance (mostly accessibility); did not yield detailed DPI specs | OK — WebFetch (page is accessibility-focused; detailed specs in journal-level guide #1) |
| 15 | `http://mc04.manuscriptcentral.com/pmea-ipem` | Portal URL — submission lives here | 403 Forbidden to anonymous WebFetch (expected — portal requires login). URL confirmed live via #1, #2, #4. |
| 16 | `https://ioppublishing.org/news/physiological-measurement-appoints-randall-moorman-as-new-editor-in-chief/` | Historical EiC (Moorman 2014–2019, now superseded by Xiao Hu) | OK via WebSearch |
| 17 | `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/publication/2026-05-17_journal-scout_cgem-emulator.md` | Prior PMEA scout (rank 2, scope 28/30) | OK — local Read |
| 18 | `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/publication/2026-05-01_journal-scout_physiol-meas_guide.md` | Prior PMEA submission guide (2026-05-01) | OK — local Read |
| 19 | `/root/repos/manuscripts/cgem/bspc/src/manuscript.md` | BSPC manuscript source, ≈ 6,020 main-body words | OK — local Read |
| 20 | `/root/repos/manuscripts/cgem/bspc/src/cover_letter_bspc.md` + 5 other declaration files | BSPC declarations (folded under §3.4 into one Acknowledgements) | OK — local Read |
| 21 | `/root/repos/manuscripts/cgem/bspc/supplementary/` | 18 supplementary files (S1–S7 + 6 appendices + 2 figures + 3 tables + captions) | OK — local listing |
| 22 | `https://publishingsupport.iopscience.iop.org/ethical-policy-journals/` | IOP ethical policy (high-level) | OK via WebFetch (limited extract due to copyright cautions; supplemented via #6) |

---

## 10. One-page recommendation

**Submit to PMEA as a Research paper under double-anonymous peer review at `http://mc04.manuscriptcentral.com/pmea-ipem`, with the subscription / non-OA path selected ($0 APC).** The five edits that must happen before upload, in order of priority:

1. **Restructure the abstract** under the four PMEA mandatory headings (Objective / Approach / Main results / Significance), keeping ≤ 250 words. The current 247-word flat-paragraph abstract is a desk-filter trigger if left unchanged.
2. **Convert references** from Vancouver numerical (`[1]…[27]`) to **Harvard alphabetical with article titles**. Verify all 27 DOIs are live the day of submission. Mint Zenodo (dataset) and OSF (pre-registration) DOIs to replace the "TBD" placeholders.
3. **Render a single submission PDF** with figures and tables embedded inline at first reference, 12 pt font, ≥ 1.5 line spacing. Drop the separate `fig1.pdf`–`fig6.pdf` Elsevier-style attachments.
4. **Consolidate** the six separate Elsevier-style declaration files (highlights, author contributions, COI, statement on human/animal studies, funding, acknowledgements) into a **single Acknowledgements section** placed before References inside the manuscript PDF. Drop `highlights.docx` entirely (PMEA does not use Highlights).
5. **Rewrite the cover letter** for PMEA / Prof. Xiao Hu, quoting verbatim from PMEA's scope ("physiological modelling, simulation, model identification, and control" and "physics- and model-based machine learning"); disclose prior IJNMBE (2026-05-17) and BSPC (2026-05-22) desk rejections.

Estimated total effort: **6–10 hours**. No data re-runs, no statistical re-runs, no figure re-generation.

Two policy flags Diego decides:

- **Peer review model:** single- vs double-anonymous (recommendation: double-anonymous; LMIC author, methodology-first paper).
- **AI disclosure:** IOP policy requires disclosure in Acknowledgements if GenAI was used in the ways listed; workspace policy at `/root/repos/CLAUDE.md` says do not disclose. The audit reports the verbatim IOP policy in §7 and flags the conflict; the decision is Diego's at portal time. (The hallucinated-references guard rail is independent of this decision and applies regardless — re-verify all 27 references against Crossref / PubMed / arXiv the day of submission.)

---

**End of audit.**
