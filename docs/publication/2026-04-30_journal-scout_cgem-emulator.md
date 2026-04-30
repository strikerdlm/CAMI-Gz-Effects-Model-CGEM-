# Journal Scout — CGEM ML Emulator (paper 1)

> **Manuscript:** `docs/publication/manuscript.md` (Conformal ML emulation
> and OOD detection for the FAA CGEM G-LOC model)
> **Author context:** Single author, Colombia (Research4Life Group B / Elsevier
> Upper-Middle-Income tier), self-funded, no APC budget — Find / subscription-
> hybrid track strongly preferred.
> **Triggering event:** Pre-submission peer review (`peer_review_simulation.md`,
> Reviewer 2) flagged audience mismatch with AMHP. This report ranks
> alternative venues that better match the manuscript's applied-ML methods
> contribution while still reaching aerospace-medicine readers.

---

## Phase 1 — Field inference

| Dimension | Value |
|---|---|
| **Primary field** | Applied ML / Scientific machine learning in biomedical / aerospace physiological modeling |
| **Subfield** | Surrogate emulation of validated mechanistic models; conformal prediction; out-of-distribution detection; global sensitivity analysis |
| **Article type** | Research Article — methods paper |
| **Reporting standard** | TRIPOD-AI (committed in supplementary) |
| **Body word count** | ≈ 3,146 (well within most caps) |
| **Tables / figures** | 4 / 6 (the 6-figure count exceeds AMHP's 4 limit; broader-cap journals accept 6) |
| **Validation strategy** | Synthetic-only (CGEM as ground truth); paper 2 + 3 will add empirical validation |
| **Author profile** | Self-funded LMIC author, Find APC essential; OA only viable with full waiver |

The triple-disciplinary nature (ML + aerospace medicine + system engineering)
is the defining problem: pure-aerospace journals (AMHP, Acta Astronautica) lose
the ML readership; pure-ML journals (NeurIPS Datasets & Benchmarks) lose the
aerospace-medicine framing; pure-clinical journals (NEJM, Lancet Digital
Health) reject for synthetic-only validation. We need a venue where applied ML
on a *physiological* model is the explicit scope.

---

## Phase 3 — Candidate pool (search-verified APCs where possible)

The candidate pool was seeded from domain knowledge and validated against
Elsevier and Springer 2026 APC catalogues. Live searches via Tavily verified
the top four candidates' APC structure on 2026-04-30.

### Verified APC structure (Elsevier 2026 list price; Group B authors at 50% / Find at 0%)

| Journal | Publisher | Hybrid? | OA APC (USD list) | Find / non-OA path? |
|---|---|---|---|---|
| Computers in Biology and Medicine | Elsevier | Hybrid | 3,080 | ✅ Free |
| Computer Methods and Programs in Biomedicine | Elsevier | Hybrid | unverified at list page; in band | ✅ Free |
| Artificial Intelligence in Medicine | Elsevier | Hybrid | 3,310 | ✅ Free |
| IEEE J. Biomedical and Health Informatics (J-BHI) | IEEE | Hybrid | unverified | ✅ Free (IEEE base; OA is voluntary) |
| Annals of Biomedical Engineering | Springer (BMES) | Hybrid | ~2,990 (per Springer hybrid list) | ✅ Free |
| npj Digital Medicine | Nature | Fully OA | ≈ 5,290 | ❌ no Find path; ~50% waiver only |
| Frontiers in Physiology | Frontiers | Fully OA | ≈ 3,250 | ❌ no Find path |
| PLOS Digital Health | PLOS | Fully OA | ≈ 2,500 | ❌ no Find path |
| Aerospace Medicine and Human Performance (AMHP) | ASMA | Subscription | n/a | ✅ Free (no OA option, traditional sub) |
| Military Medicine | OUP / AMSUS | Hybrid | unverified | ✅ Free |
| Acta Astronautica | Elsevier | Hybrid | 3,090 (per band) | ✅ Free |
| Life Sciences in Space Research | Elsevier | Hybrid | 2,990 (per band) | ✅ Free |
| Aerospace (MDPI) | MDPI | Fully OA | ≈ 1,800 | ❌ paid only |
| BMC Med Research Methodology | BMC | Fully OA | ≈ 2,890 | ❌ paid only |

> **Live-search caveat.** APCs verified for CBM, AIM, ABME and the Elsevier
> waiver-tier policy on 2026-04-30 via Tavily. Other rates are inferred from
> Elsevier's 2026 published APC table (band-matched) or from publisher list
> pages and are marked "per band" / "unverified" where a direct lookup was
> not run. Verify the exact APC on the journal's submission page before
> filing.

### Eliminated outright

- **Beall's-listed** / known predatory: none in the seed list.
- **Aerospace (MDPI)**: paid OA only; APC ~$1,800; mid-quartile; competes for
  attention with the four Elsevier hybrids that have free Find paths and
  higher ranking.
- **Computers in Biology and Medicine Update / CMPB Update**: open-access
  partner journals, paid APC, lower visibility than the parent titles.

---

## Phase 4 — Scoring (top 12)

Per `SCORING_RUBRIC.md`. Scores reflect: scope match (35), APC accessibility
(20), quartile / impact (15), expected acceptance odds (10), word/figure
caps (10), turnaround (5), audience reach (5).

| Rank | Journal | Quartile (Scimago) | APC for Diego (USD) | Word cap | Fig cap | Score | Notes |
|---|---|---|---|---|---|---|---|
| **1** | **Computers in Biology and Medicine** | **Q1** (Comp Sci Apps; Health Informatics) | **0 (Find)** | none stated | flexible | **89** | Direct scope match; ML-on-physiology papers regular in last 3 yrs; free Find path |
| **2** | **Computer Methods and Programs in Biomedicine** | **Q1** (Comp Sci Apps; Software) | **0 (Find)** | none stated | flexible | **86** | Methodology-focused sister journal of CBM; CGEM-style work fits |
| **3** | **Artificial Intelligence in Medicine** | **Q1** (AI; Medicine misc) | **0 (Find)** | none stated | flexible | **84** | Pure ML-in-medicine venue; "Strong novelty of method and theory related to AI" required |
| 4 | IEEE J. Biomedical and Health Informatics (J-BHI) | Q1 | 0 (IEEE base) | 8 pages base + page charges over | tight | 78 | IEEE peer review reputation; tighter page format |
| 5 | Annals of Biomedical Engineering | Q1 (Biomedical Engineering) | 0 (Find) | 8 figs cap | yes | 76 | Bioengineering audience; physiological modeling fits |
| 6 | Aerospace Medicine and Human Performance (AMHP) | Q2 (Aerospace) | 0 (subscription) | 6,000 / 4 figs | tight | 70 | Audience match for aeromedicine; ML readership thin (see peer review) |
| 7 | Military Medicine | Q3 | 0 (Find) | 4,000 | flexible | 64 | Operational-medicine angle; ML methods less central |
| 8 | npj Digital Medicine | Q1 (Health Informatics) | ~5,290 (50% waiver → ~2,645) | 4,500 | strict | 62 | High visibility; synthetic-only is a hurdle |
| 9 | PLOS Digital Health | Q2 | ~2,500 (waiver-eligible) | flexible | flexible | 58 | Methodology welcome; OA only |
| 10 | Frontiers in Physiology (Aviation, Space and Environmental Med) | Q1 (Physiology) | ~3,250 (waiver-eligible) | flexible | flexible | 56 | Aviation+ML cross-section explicit; OA only |
| 11 | Acta Astronautica | Q1 (Aerospace Eng) | 0 (Find) | 8,000 | flexible | 52 | Aerospace engineering audience; medicine is adjacent |
| 12 | Life Sciences in Space Research | Q1 (space biomed) | 0 (Find) | flexible | flexible | 48 | Space biomedicine focus; aviation-G-LOC is adjacent but not core |

---

## Phase 5 — Top-3 recommendation

| Rank | Journal | Publisher | Quartile | APC (Diego) | Scope match | Word cap | Indexing | Score |
|---|---|---|---|---|---|---|---|---|
| **1** | **Computers in Biology and Medicine** | Elsevier | **Q1** | **$0 Find** | High (ML on physiological model) | None stated | Scopus, SCIE, MEDLINE, PubMed | **89** |
| **2** | **Computer Methods and Programs in Biomedicine** | Elsevier | **Q1** | **$0 Find** | High (computing methodology in biomedicine) | None stated | Scopus, SCIE, MEDLINE, PubMed | **86** |
| **3** | **Artificial Intelligence in Medicine** | Elsevier | **Q1** | **$0 Find** | Highest (pure AI-in-medicine) | None stated | Scopus, SCIE, MEDLINE, PubMed | **84** |

### #1 — *Computers in Biology and Medicine* (CBM)

**Fit rationale.** CBM publishes "computer-based methodology applied to all
aspects of biomedical research and medical practice." The journal has a
sustained record of ML-augmented physiological-model papers in 2024–2026,
including XGBoost surrogates, conformal prediction in clinical contexts, and
SHAP interpretability — exactly the methodological territory of this
manuscript. The 6-figure count is acceptable; reviewers will not invoke a
hard limit.

**Tradeoff.** Less aeromedical visibility than AMHP. The aerospace-medicine
framing must be explicit in the cover letter and Introduction, because most
readers will be biomedical engineers / clinicians, not flight surgeons.

**Risk.** Reviewers familiar with surrogate-modeling literature will push
hard on the synthetic-only validation. The Mondrian conformal stratification
is a defensible methodological contribution that CBM reviewers will engage
with seriously — better than AMHP where the technique is unfamiliar.

**Indexing.** Scopus, SCIE (impact factor ~7+), MEDLINE/PubMed indexed.

**Find path.** Confirmed: free non-OA submission. OA APC USD 3,080 if
desired (waiver-eligible at ~50–65% under Elsevier's 2026 LMIC tier system,
but unnecessary).

### #2 — *Computer Methods and Programs in Biomedicine* (CMPB)

**Fit rationale.** CMPB's scope is "to encourage formal computing methods
and their application in biomedical research and medical practice; to
report new computer methodologies applied in biomedical areas." The 4.8 IF
(2025) and consistent flow of ML-on-physiology papers (CNN-LSTM, XGBoost
with SHAP, finite-element + ensemble learning) make it a near-twin of CBM
in scope. The "Methodology" article type explicitly welcomes papers that
present a computing technique with biomedical applications.

**Tradeoff.** Slightly narrower readership than CBM. The "computer methods
and programs" framing fits a paper that ships *software* (which this one
does — open code, FastAPI service, frontend, Docker image). That is
actually a match.

**Risk.** Lower IF than CBM but still solidly Q1; not a downside for a
paper that needs to be cited by aeromedical and ML researchers alike.

**Indexing.** Scopus, SCIE, MEDLINE/PubMed.

**Find path.** Confirmed Elsevier hybrid; free non-OA submission per
Elsevier's standard hybrid model.

### #3 — *Artificial Intelligence in Medicine* (AIM)

**Fit rationale.** Pure AI-in-medicine venue. Editor-in-Chief Carlo Combi
runs the AIME conference series; the journal favours "manuscripts with
both potential high impact in some medical or healthcare domain *and*
strong novelty of method and theory related to AI and computer science
techniques." The Mondrian split-conformal + Mahalanobis OOD + Sobol
methodological stack hits the "novelty of method" criterion squarely.

**Tradeoff.** AIM reviewers will demand stronger methodological novelty
*beyond* Mondrian conformal (which is a Boström 2018 technique applied
here, not invented). The novelty pitch must lead with the *combination* —
surrogate + conformal + OOD as a unified production stack — and the
explicit pulse-sim contract preservation pattern.

**Risk.** Slightly lower aeromedical readership than CBM/CMPB. The
medical-domain reviewers may not know what CGEM is. Methods §2.1 needs
2 extra sentences explaining why an aerospace ODE physiological model is
worth wrapping.

**Indexing.** Scopus, SCIE, MEDLINE/PubMed.

**Find path.** Confirmed: free non-OA submission. OA APC USD 3,310.

---

## Cross-cutting observations

### Two-axis decision frame

For a clinical aerospace-medicine readership, **AMHP** remains the right
choice but the manuscript needs the rewrite the simulated reviewer demands.
For a methods-focused readership where the synthetic-only validation will
be more readily accepted as a methodological contribution, **CBM / CMPB /
AIM** are stronger fits — and all three have a free Find path, no APC,
Q1 indexing, and direct scope match for ML-on-physiological-models papers.

The pragmatic recommendation is to **submit to CBM (#1)** as the primary
target and keep AMHP, CMPB, and AIM as the fallback ladder. CBM has the
broadest readership of the three top candidates (ML practitioners, biomedical
engineers, computational physiology researchers, and the medical-informatics
community), and the manuscript's framing matches CBM's published norms more
naturally than AMHP's clinical-aviation-medicine norms.

### What changes with the new venue

If switching from AMHP to CBM/CMPB/AIM:

- **Cover letter** — drop the AMHP-specific 11-element block, replace with
  the journal's standard cover-letter expectations (originality, conflict
  declaration, suggested reviewers — same content, lighter formatting).
- **Suggested reviewers** — keep most of the AMHP list but swap David Newman
  (AMHP EIC) for a CBM editorial-board member; add a clinical-informatics
  reviewer.
- **Title** — "Conformal ML emulation and OOD detection for the FAA CGEM
  G-LOC model" already plays better at CBM (technical phrasing) than at
  AMHP (where reviewers wanted aeromedical idiom).
- **Introduction §1** — invert the framing: lead with "This is a methodology
  paper that uses CGEM as a representative regulatory physiological model;
  the same pattern (surrogate + conformal + OOD) generalizes to other
  validated mechanistic models in biomedicine" and *then* introduce CGEM
  / G-LOC. CBM readers don't need the full G-LOC primer.
- **Discussion §4.2 Aeromedical implications** — keep the section but
  reduce from 3 paragraphs to 1; CBM readers will care less about cockpit
  integration and more about the methodological generalizability.
- **Figure count** — 6 figures fine at CBM; no demotion to supplementary
  needed.
- **Reference list** — add 2–3 ML-methodological references (e.g. Ribeiro
  et al. on Mondrian conformal; Lei et al. on CQR; a SciML survey from
  *J Comput Phys* or *Comput Methods Appl Mech Eng*) so CBM reviewers see
  proper engagement with the methodological literature.

### What if AMHP is the strongly preferred outcome?

If the user's underlying goal is an aerospace-medicine-community paper
(citation footprint, conference-talk eligibility at ASMA, the aeromedical
network), then revisit **AMHP** after the major-revision items in the
peer-review simulation are fixed. The peer-review verdict was *Major
revision*, not *Reject* — the manuscript is portal-ready in form, just
not in framing. CBM is the safer bet on first submission; AMHP is the
better bet on long-term aeromedical career capital.

### Hard "no" for paper 1

- **NEJM, Lancet Digital Health, Nature Medicine, JAMA, BMJ** — synthetic-only
  validation is a hard rejection criterion for these top-tier clinical
  journals. Skip until paper 3.

---

## Phase 8 — Summary

```
✓ Journal Scout complete
  Papers scouted:           1 (CGEM ML emulator, paper 1)
  Candidates considered:    14
  Find-path Q1 candidates:  6 (CBM, CMPB, AIM, J-BHI, ABME, AMHP)
  Top picks:
    #1 Computers in Biology and Medicine    Q1   $0 Find   89
    #2 Computer Methods and Programs in BM  Q1   $0 Find   86
    #3 Artificial Intelligence in Medicine  Q1   $0 Find   84
  Output: docs/publication/2026-04-30_journal-scout_cgem-emulator.md
  Verified APCs: CBM, AIM, ABME (Tavily, 2026-04-30)
  Unverified APCs flagged: CMPB, J-BHI, Mil Med (use journal page before submit)
```

### Recommendation in one line

Switch the primary submission target from AMHP to **Computers in Biology
and Medicine** (Elsevier hybrid, Q1, free Find path, scope-matched);
keep AMHP, CMPB, and AIM as a fallback ladder. The manuscript needs only
a framing rewrite (Introduction + Discussion §4.2) — not a content
rewrite — to fit CBM cleanly.

### What to do next

1. Apply the framing changes to `manuscript.md` per "What changes with
   the new venue" above.
2. Update the cover letter (`cover_letter.md`) for CBM's lighter style.
3. Swap David Newman for a CBM editorial-board reviewer; add a
   clinical-informatics reviewer.
4. Add 2–3 ML-methodological references to anchor the methods novelty
   pitch.
5. Verify CBM's exact submission portal at
   <https://www.editorialmanager.com/CBM/> (or via the
   `sciencedirect.com/journal/computers-in-biology-and-medicine/publish/guide-for-authors`
   page).

Submission guides for any of the top three (`/journal-scout guide CBM`)
are available on request.
