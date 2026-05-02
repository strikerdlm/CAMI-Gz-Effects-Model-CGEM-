# Submission guide — *Physiological Measurement* (IOP / IPEM)

> **Manuscript:** `docs/publication/manuscript.md` (Conformal ML emulation
> and OOD detection for the FAA CGEM G-LOC model)
> **Companion files:** `cover_letter.md`, `highlights.md`, `author_page.md`,
> `references_verification.md`, `tripod_ai_checklist.md`,
> `peer_review_simulation.md`.
> **Author context:** Single author, Colombia (Research4Life Group B), no
> APC budget — submits via the **subscription / non-OA** path.
> **Source for the IOP rules below:** the user-pasted IOP general "Information
> for authors" page (covers all IOP journals) plus a 2026-05-01 Tavily lookup
> of the journal-specific IOP Publishing Support page (peer-review model,
> referencing system).

---

## 0 · One-line verdict

**Submissible, borderline-positive fit.** Physiological Measurement's
scope explicitly includes "physiological modelling and simulation" and
"advanced methods of time series and other data analysis" — both core
to the manuscript — but the journal's editorial centre of gravity is on
**measurement methods and their validation** (PPG, ECG, EIT, sleep
signals, sensor design). The CGEM paper is one step downstream of
measurement: it wraps a validated mechanistic model that *consumes*
measurement-derived inputs, rather than developing a new measurement
itself. To submit here, the abstract and §1 must lead with the
**measurement-derived inputs and their validation propagation** angle,
not with "we wrapped a Fortran black box." If you don't want to make
that re-framing, the cleaner Q2 alternatives are IJNMBE (Wiley) or
Mathematical Biosciences (Elsevier) per
`2026-05-01_journal-scout_cgem-q2-physiology.md`.

---

## 1 · Fit assessment

### 1.1 The scope check, point by point

| Journal scope item (from IPEM "Scope" page) | Manuscript hit |
|---|---|
| applied physiology in illness and health | partial — G-LOC physiology, but synthetic-only |
| electrical bioimpedance, optical and acoustic measurement techniques | **no** |
| advanced methods of time series and other data analysis | **yes** — XGBoost regressors over G-time-series features; Mondrian conformal calibration |
| biomedical and clinical engineering | **yes** — applied to civil-aviation regulatory physiology |
| in-patient and ambulatory monitoring | **no** |
| point-of-care technologies | **no** |
| novel clinical measurements of cardiovascular, neurological, and musculoskeletal systems | partial — model predictions of cerebrovascular and cardiovascular response, no direct measurement |
| measurements in molecular, cellular and organ physiology and electrophysiology | **no** |
| **physiological modeling and simulation** | **yes — direct hit** |
| novel biomedical sensors, instruments, devices and systems | **no** |
| measurement standards and guidelines | partial — calibration of a regulatory model that informs measurement standards |

Direct-hit count: **2 of 11**. Partial-hit count: **3 of 11**.
The "physiological modeling and simulation" line is the load-bearing one.
The editor will decide on the strength of that single match plus the
quality of the methodological framing.

### 1.2 The IOP submission-acceptance bar

The IOP general guidelines you pasted state, verbatim:
> "Reporting incremental steps forward from previous work is usually not
> sufficient."

This favours the manuscript. The contribution is not incremental: a
**Mondrian split-conformal regressor stratified by maneuver category**, a
**conformal-abstention OOD detector calibrated on the squared Mahalanobis
distance**, and a **two-stage classifier-then-regressor pattern for
right-censored event-time targets**, all wrapping a validated regulatory
physiological model — that's a discrete methodological package, not an
incremental tweak. The TRIPOD-AI checklist and OSF pre-registration are
also load-bearing on the rigour bar.

### 1.3 Where the fit is weakest

- **No primary measurement.** The dataset is fully synthetic (CGEM as
  ground truth). Most Physiological Measurement papers report a
  measurement protocol applied to humans, animals, or phantoms.
- **No measurement-method novelty.** The novelty is methodological-ML, not
  sensor-/signal-acquisition-related.
- **Aerospace-medicine framing.** The journal does not have an established
  aerospace-medicine readership; the cover letter must avoid the AMHP
  idiom and instead emphasise *generalisability* to other physiological
  models that ingest measurement-derived inputs.

### 1.4 Mitigations that materially raise the desk-acceptance odds

1. **Re-frame the abstract** so the lead clause is "calibration and
   uncertainty quantification of a measurement-driven physiological model"
   rather than "ML emulator of a Fortran model." Suggested opening:
   > "We present a calibration and uncertainty-quantification methodology
   > for measurement-driven mechanistic physiological models, applied to
   > the FAA's CGEM regulatory model of +Gz acceleration physiology, which
   > integrates measurement-derived inputs (Nz time-series, anthropometric
   > and hemodynamic measurements) into clinical-risk predictions for
   > G-induced loss of consciousness."
2. **Add a half-page §2 subsection** titled e.g. "Measurement-derived
   inputs to CGEM" that enumerates which CGEM inputs originate from
   physiological measurement (Nz from inertial measurement; anthropometric
   inputs from clinical body-composition measurements; cardiovascular
   parameters from centrifuge-based hemodynamic measurements). This anchors
   the paper to the measurement community, even though the *paper* doesn't
   collect new measurements.
3. **Recast the conformal intervals** as quantifying the propagation of
   measurement uncertainty into model-derived predictions — not as
   surrogate-emulation error alone. This is essentially a re-framing of
   what the conformal intervals already do; the math doesn't change.
4. **Add 2–3 measurement-relevant references** (e.g., centrifuge cardiovascular
   measurement studies, IMU-based G-onset measurement methods) so the
   reference list signals engagement with the measurement community.
5. **Choose double-anonymous review.** IOP allows author choice between
   single- and double-anonymous; double-anonymous mildly raises acceptance
   odds for global-south first authors per IOP's own internal data
   (referenced on their `ioppublishing.org` blog). The manuscript already
   carries no identifying author info in the body (the title-page lives in
   `author_page.md`), so the cost of opting double-anonymous is minimal.

If steps 1–3 are uncomfortable to make, send the paper to **IJNMBE**
instead — IJNMBE accepts the "wrapper of a numerical biomedical ODE"
framing without re-positioning.

---

## 2 · Submission package — Physiological Measurement specifics

### 2.1 Manuscript Format

| Item | Rule | Status of current manuscript |
|---|---|---|
| Article type | Research paper (default), Topical Review, Roadmap, Editorial, Perspective. **Use "research paper".** | ✅ |
| Language | English; Roman characters only in body and references | ✅ |
| Submission file | **Single PDF**, ≥ 12-pt font, ≥ 1.5 line spacing, figures embedded inline at first reference | ⚠ rendered PDF in `docs/publication/rendered/` may need re-export to embed figures inline |
| Author block | Single-anonymous → include names + affiliations at the start; Double-anonymous → strip names, affiliations, acknowledgements, identifying citations from the PDF (re-add at acceptance) | Choose: **double-anonymous recommended** (see §1.4) |
| Article title | Concise, informative, search-engine-friendly; avoid long systemic names; key terms early | ✅ "Conformal ML emulation and OOD detection for the FAA CGEM G-LOC model" — strong; consider also "for a validated regulatory ODE physiological model" to broaden |
| Word count | Journal's general page does not state a hard cap; IOP guidance is "appropriate to the content"; PMEA's modal research paper is ≈ 6,000 words | Current ≈ 5,430 words → **OK** |
| Section structure | IMRaD: Introduction → Methods → Results → Discussion → Conclusion | ✅ |
| Acronyms | All acronyms defined on first use | ✅ already audited in CMPB compliance pass |
| Inclusive language | IOP requires adherence to the [Inclusive Language and Images guidelines](https://assets.pubpub.org/jcnh8c3v/71666271791414.pdf) | ✅ no flagged terms |
| Lena image | Forbidden | n/a |

### 2.2 Abstract

| Rule | Status |
|---|---|
| **≤ 300 words** (IOP general; PMEA does not relax this) | ⚠ **current abstract is 341 words → must trim 41 words** |
| Structured? | IOP does not require a structured abstract for Physiological Measurement (unlike CMPB). The current Background / Methods / Results / Conclusions structure is *acceptable* but **convert to a single flowing paragraph** if you want to maximise the chance the editor reads it as a measurement-validation paper rather than a clinical-trials piece |
| No undefined acronyms | ✅ |
| No figure / table / equation references | ✅ |
| First two sentences should contain key search terms | ⚠ rewrite to lead with "physiological modelling and simulation," "measurement-derived inputs," "uncertainty quantification" — these are the words an editor will search for |

### 2.3 Keywords

Pick 5–8. Suggested set, ranked by editorial relevance:

1. physiological modelling
2. surrogate emulation
3. conformal prediction
4. out-of-distribution detection
5. uncertainty quantification
6. acceleration physiology
7. cerebrovascular hemodynamics
8. global sensitivity analysis

### 2.4 References — **mandatory Harvard alphabetical with article titles**

This is the largest format-conversion task vs. the current manuscript.

**Current state.** Manuscript uses **Vancouver numerical** style ([1] … [19]) per the CMPB compliance pass.

**Required state for Physiological Measurement.** Per IOP's style guide,
all references must be in **Harvard alphabetical** style. Article titles
are **mandatory** for Physiological Measurement (most other IOP journals
make them optional). Format example IOP style guide:

> Smith J, Jones A and Brown C 2023 *Title of the paper Journal Name*
> **45** 123–145

In-text citations therefore become:
- single author → "Smith (2001)" or "(Smith 2001)"
- two authors → "Smith and Jones (2001)" or "(Smith and Jones 2001)"
- three+ authors → "Smith *et al.* (2001)" or "(Smith *et al.* 2001)"
- multiple papers same author + year → 2001a, 2001b
- specific page → "Smith (2001, p 39)"

**Conversion plan.**

1. Take the existing `references_verification.md` (19 entries, all DOI-verified).
2. Convert in-text [n] markers to (Author Year) markers — there are
   approximately 35–40 cite-markers across §§1–4.
3. Re-order the bibliography alphabetically by first author surname,
   year-secondary.
4. **Add article titles** to every entry; the current bibliography may
   omit titles for some Vancouver-style entries that compressed to
   "Author year. Journal vol pp" — re-pull from CrossRef where missing.
5. Use IOP-permitted DOI / arXiv / PMID links.
6. Drop bracketed numbers from the body; the alphabetical bibliography
   is sufficient.

This is a half-day to one-day editorial pass; tooling exists in
`scripts/` for the citation-verification side.

### 2.5 Figures and Tables

| Rule | Status |
|---|---|
| Embedded inline in the submission PDF (not appended at end) | ⚠ verify the rendered PDF in `docs/publication/rendered/` |
| Vector preferred (EPS / PDF) at 8.5 cm (1-col) or 15 cm (2-col) final width | the current 6 figures (`scripts/render_figures.py` outputs in `data/figures/`) are PNG at 300 dpi — **acceptable**, but EPS/PDF would be preferable |
| 8–12 pt text in figure characters at final size | ⚠ check final-size fonts; some current panels embed 6-pt subtitles |
| **Avoid colour-only encoding** — use shape/line-style/fill so figures remain readable in greyscale and to colour-blind readers | ✅ ECharts pipeline already uses colour-blind-safe palette and encodes by line style + colour, but re-audit panels (a)–(c) of Fig. 3 to confirm |
| Figure captions self-contained; no acronyms; describe key conclusion | ⚠ current captions are descriptive but could be more outcome-led ("Mondrian conformal coverage by maneuver category, with all four strata within ±5 pp of nominal 95 %" rather than "coverage by stratum") |
| File naming | `figure1.eps`, `figure2.eps`, …, with multi-part files as `figure3a_3d.eps` | — apply at file-rename time |
| Tables | colour-free; use bold/italic to distinguish; sequentially numbered; concise captions | ✅ current 4 tables comply |

No hard figure cap; 6 figures + 4 tables is comfortable for a research
paper at this journal.

### 2.6 Acknowledgements & declarations (single section, before References)

The pasted IOP page mandates these in the acknowledgements section:

1. **Funding statement** with funder name + grant number — for this paper:
   self-funded, no external grant. State explicitly:
   > "This research received no specific grant from any funding agency in
   > the public, commercial, or not-for-profit sectors."
2. **Conflict of interest declaration** — single author, no commercial
   ties to FAA, IPEM, or any aerospace-medicine vendor. State:
   > "The author declares no competing interests."
3. **Author contributions** — single author; the CRediT taxonomy collapses
   to: conceptualization, methodology, software, validation, formal
   analysis, investigation, data curation, writing — original draft,
   writing — review and editing. State all roles attributed to the sole
   author.
4. **Data availability statement** — point to the OSF pre-registration
   and the public GitHub repo (`https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-`).

**Double-anonymous specific:** if you opt double-anonymous, *strip*
items 1–3 and the data-availability links from the submission PDF (any
URL that identifies the author or institution must be removed). Re-add
at acceptance via the editorial portal. Funding agency name and grant
number can also be entered into the portal at submission.

### 2.7 Ethical statement

The manuscript reports a **synthetic-only** validation; no human or
animal subjects were studied in this work. A short ethical statement is
still required by IOP. Suggested wording (place at the end of Methods or
in a dedicated subsection):

> "This study used a fully synthetic dataset generated by the FAA CAMI
> G-Effects Model (CGEM) Fortran reference implementation. No human or
> animal subjects were involved. Empirical validation against own-centrifuge
> human-subject data is reported in companion paper 3 (in preparation,
> CACOM-1 protocol, IRB approval pending at the corresponding site). All
> code, the dataset, and the OSF pre-registration are publicly available."

### 2.8 Supplementary material

Permitted, free, hosted on IOPscience, each gets its own DOI. Up to 50 MB
per file, 150 MB total including main article. Recommended files:

- `supp_dataset_card.pdf` — Gebru et al. (2018) datasheet for `cgem_synthetic_v1`
- `supp_tripod_ai_checklist.pdf` — already prepared
- `supp_osf_preregistration.pdf` — OSF pre-registration timestamp + content
- `supp_optuna_search_spaces.json` — frozen hyperparameter search spaces
- `supp_sobol_full.csv`, `supp_morris_full.csv` — full sensitivity tables
- `supp_shap_summary.pdf` — SHAP summary plots per target
- (optional) `supp_video_demo.mp4` — 30-second demo of the FastAPI service
  + frontend; H264 / MP4, 480×360, 15 fps, ≤ 10 MB — meets the IOP limits

Each file needs a 30-character title and 30-word description; provide
these at submission, not in the file metadata only.

### 2.9 Preprint policy

IOP allows posting an unrefereed preprint anywhere at any time, provided:
1. ownership of copyright is **not** transferred or assigned to the
   preprint server; and
2. an **exclusive** licence is **not** granted to the preprint server.

arXiv (default CC-BY-NC-ND or CC-BY licence) and OSF are both compliant.
The OSF pre-registration is *not* a preprint and is fine; if you also
want an arXiv preprint, post under arXiv's default non-exclusive licence.

### 2.10 Peer-review model — the key choice

| Option | Choose if … | Implications |
|---|---|---|
| Single-anonymous (default) | … you want the reviewers to see your aerospace-medicine track record (helpful at AMHP / aviation venues; less so at IOP, which has no aerospace-medicine community) | Author identity visible to reviewers; reviewer identity hidden |
| **Double-anonymous (recommended)** | … you are an LMIC author whose name and affiliation may carry less editorial weight than the methodology of the paper itself | Author identity hidden in the submitted PDF; per IOP's own data, double-anonymous submissions are *more likely* to be accepted overall, with a particularly favourable effect for under-represented author origins |

Practical impact on the submission PDF if you choose double-anonymous:

- **Strip:** author names, affiliations, ORCIDs, the entire acknowledgements
  section, any URL or identifier that resolves back to the author (GitHub
  repo URL, OSF URL, personal email).
- **Anonymise self-citations:** "as the author has shown previously
  (Anonymous, 2024)" rather than "as Malpica (2024) has shown."
- **Keep:** the OSF pre-registration content (timestamp anonymised), the
  TRIPOD-AI checklist, the ethical statement (rewritten to avoid IRB-site
  identification — say "IRB approval pending at the relevant site").
- The IOP submission portal has a checklist for this.

### 2.11 Submission portal

Physiological Measurement submits via **ScholarOne Manuscripts**
([https://mc.manuscriptcentral.com/pmea](https://mc.manuscriptcentral.com/pmea)
— **[VERIFY AT JOURNAL WEBSITE]** before submission, as IOP has been
migrating some journals to a unified Editorial Manager workflow). The
portal flow:

1. Create a ScholarOne account (or log in via ORCID).
2. Choose article type: "Paper" (the journal's default).
3. Choose peer-review model (single- vs double-anonymous).
4. Upload the single submission PDF + each supplementary file separately.
5. Suggest **3–5 reviewers** (prefer no editorial-board overlap to avoid
   conflict checks; current `suggested_reviewers.md` has 5 candidates →
   re-audit for IOP / IPEM / measurement-community membership and replace
   any AMHP-only reviewers).
6. Funding declaration entry; conflict declaration entry.
7. Submit.

### 2.12 What to remove from the CMPB submission package

The recent commits `79347c8` and `d6375eb` adapted the package to CMPB.
Items to drop or re-target before sending to Physiological Measurement:

- The "structured abstract" reformat (CMPB-mandated; PMEA does not
  require it). Convert back to a flowing-paragraph abstract ≤ 300 words.
- The CMPB-specific cover-letter highlights block (not needed at IOP).
- Any reference to "Editor-in-Chief Filippo Molinari" / CMPB → swap to
  "Editor-in-Chief Xiao Hu" (Emory) at Physiological Measurement.
- The CMPB ≤ 3,500-word body limit warning (not applicable here).
- The CMPB `Highlights` ≤ 85-character bullets (PMEA does not require a
  Highlights file; you can drop the file or simply not upload it).

### 2.13 What to add for Physiological Measurement

- Harvard-style bibliography (see §2.4).
- A Data-Availability statement linked to the GitHub repo + OSF (or
  anonymised proxy under double-anonymous).
- The measurement-validation re-framing of the Abstract and §1 (see §1.4).
- A short §2 subsection on measurement-derived inputs.
- A short ethical statement (synthetic-only, no human/animal subjects).
- Suggested-reviewer slate revised toward IPEM / IOP / measurement community.

---

## 3 · A pre-submission checklist

```
[ ] Decide single- vs double-anonymous (recommend double)
[ ] Trim abstract from 341 → ≤ 300 words
[ ] Convert references from Vancouver numerical → Harvard alphabetical with article titles
[ ] Re-frame Abstract + §1 toward measurement-derived inputs / validation propagation
[ ] Add §2.x "Measurement-derived inputs to CGEM" subsection
[ ] Re-audit figure captions for self-contained, outcome-led wording
[ ] Re-export figures as EPS/PDF (currently PNG@300dpi is acceptable but not preferred)
[ ] Verify all figures readable in greyscale and color-blind palette
[ ] Add Acknowledgements section: funding, COI, author-contributions (CRediT)
[ ] Add Ethical statement (synthetic-only)
[ ] Add Data-availability statement
[ ] Replace CMPB cover letter with PMEA cover letter (see §4 template)
[ ] Identify 3–5 PMEA-aligned reviewers (replace any AMHP-only entries)
[ ] If double-anonymous: strip names / affiliations / URLs / acknowledgements / self-citations
[ ] Render single-PDF submission (figures embedded inline at first mention)
[ ] Prepare supplementary files with 30-char titles + 30-word descriptions
[ ] Verify portal URL [VERIFY AT JOURNAL WEBSITE]: https://mc.manuscriptcentral.com/pmea
[ ] Submit; record submission ID
```

---

## 4 · Cover-letter template — Physiological Measurement

> Dear Professor Hu and the Editorial Team of *Physiological Measurement*,
>
> I am pleased to submit for your consideration a research paper entitled
> **"Conformal ML emulation and OOD detection for the FAA CGEM G-LOC
> model: a generalisable methodology for measurement-derived mechanistic
> physiological models"** by Diego Malpica, MD.
>
> **Why Physiological Measurement.** This work develops a methodology
> that addresses three limitations of validated regulatory physiological
> models that integrate measurement-derived inputs (here, Nz time-series,
> anthropometric measurements, and centrifuge-derived hemodynamic inputs):
> computational cost, absence of calibrated uncertainty quantification,
> and absence of input-envelope detection. The methodology — surrogate
> emulator + Mondrian split-conformal prediction intervals + conformal
> Mahalanobis-distance OOD abstention + Sobol/Morris global sensitivity
> analysis — is illustrated against the FAA's CAMI G-Effects Model (CGEM),
> a regulatory model of +Gz acceleration physiology, and is generalisable
> to any validated ODE physiological model that consumes measurement-
> derived inputs. The paper aligns with the journal's scope on
> "physiological modelling and simulation" and on "advanced methods of
> time series and other data analysis," and contributes to the journal's
> long-standing emphasis on the development of new methods for the
> *validation* of physiological measurements once they are propagated
> into clinical-risk predictions.
>
> **What is new.** A two-stage classifier-then-regressor pattern for
> right-censored event-time targets calibrated under Mondrian split-
> conformal prediction stratified by maneuver category; a robust-Mahalanobis
> OOD detector with distribution-free conformal abstention applied to
> a frozen 17-dimensional feature space; and an end-to-end pre-registered
> validation protocol that locks split indices and success thresholds
> before test-set evaluation. Empirical coverage of the conformal
> intervals stayed within 4.6 percentage points of the nominal 95 % on
> 4 of 5 targets, and the conformal OOD threshold gave an empirical
> in-envelope rate of 0.953 on held-out data.
>
> **Reporting standards.** The paper follows TRIPOD-AI (checklist
> attached as supplementary). The validation protocol is registered on
> the Open Science Framework before any test-set evaluation. All code,
> the dataset metadata, and the OSF pre-registration are publicly
> available; the submitted figures and tables are colour-blind-safe.
>
> **Originality and exclusivity.** This work has not been published
> previously and is not under consideration at another journal. A
> non-exclusive preprint may be posted on arXiv at submission, in line
> with IOP's Preprint pre-publication policy; if so, copyright remains
> with the author and no exclusive licence is granted to the preprint
> server. We declare no competing interests; the work received no
> external funding.
>
> **Peer-review model.** The author requests **double-anonymous review**.
>
> **Suggested reviewers.** A list of five candidate reviewers from the
> measurement-validation, conformal-prediction, and computational-
> cardiovascular-physiology communities is provided in the portal.
>
> Thank you for considering this submission. I look forward to the
> editorial board's response.
>
> Sincerely,
> Diego Malpica, MD — Aerospace-medicine physician and researcher,
> Bogotá, Colombia.

(For double-anonymous, the cover letter remains attributable to the
corresponding author; only the *PDF manuscript* is anonymised. The cover
letter is not seen by reviewers.)

---

## 5 · Honest tradeoff vs. the IJNMBE alternative

| Axis | Physiological Measurement | IJNMBE (Wiley) |
|---|---|---|
| Quartile (Scimago 2024) | Q2 (Biomedical Engineering, Biophysics) | Q2 (Applied Mathematics, Modeling & Simulation, Software) |
| JIF (2025) | 2.7 | 2.4 |
| Scope match | "physiological modelling and simulation" — direct hit; broader scope is measurement-driven | numerical ODE methods + biomedical applications — direct hit on the methodology |
| Re-framing burden | **moderate** (rewrite abstract + §1, add measurement-inputs §2.x, convert references to Harvard) | **low** (existing CMPB-shaped manuscript ports almost unchanged; references can stay Vancouver) |
| LMIC accessibility | IOP encourages global-south submissions; double-anonymous available | Wiley standard hybrid; single-anonymous default |
| Editorial fit | High if the measurement-validation framing is adopted; lower otherwise | High regardless of framing |
| Audience reach | Larger physiology + clinical-engineering readership | Computational engineering + applied math |

**If reframing is acceptable, Physiological Measurement is a strong Q2
target with the higher JIF.** If reframing is unwelcome, IJNMBE is the
faster path. Both keep the subscription / non-OA Find path free for
the LMIC author profile.

---

## 6 · Final summary

```
✓ Submission guide built — Physiological Measurement
  Verdict:                Submissible, borderline-positive fit
  Critical re-framing:    abstract + §1 + new §2.x "measurement inputs"
  Critical format change: Harvard alphabetical references with article titles
  Critical trim:          abstract 341 → ≤ 300 words
  Recommended PR model:   double-anonymous
  Output:                 docs/publication/2026-05-01_journal-scout_physiol-meas_guide.md
  Verification status:    portal URL [VERIFY AT JOURNAL WEBSITE]
                          word cap [VERIFY AT JOURNAL WEBSITE — IOP general guidance only]
                          OA APC unverified (subscription path is free; OA not needed)
```
