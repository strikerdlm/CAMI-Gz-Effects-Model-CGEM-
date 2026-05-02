# Journal Scout — CGEM ML Emulator (paper 1) — **Q2 physiology pivot**

> **Manuscript:** `docs/publication/manuscript.md` (Conformal ML emulation
> and OOD detection for the FAA CGEM G-LOC model)
> **Author context:** Single author, Colombia (Research4Life Group B / Elsevier
> upper-middle-income tier), self-funded, no APC budget. Subscription /
> hybrid Find-path required.
> **Triggering event:** User redirect (2026-05-01) — drop the CMPB Q1 plan;
> identify a **Q2** venue with the same scope ("integrating AI into a
> mechanistic model in the field of physiology"). Higher acceptance odds
> and a venue where reviewers naturally frame ML-on-physiology as the
> object of the paper, not as an unusual add-on to a clinical question.
> **Supersedes:** `2026-04-30_journal-scout_cgem-emulator.md` (which ranked
> CBM / CMPB / AIM as Q1 finalists).
> **Last verification pass:** 2026-05-01 — IJNMBE scope and submission
> guidelines re-verified directly from the Wiley homepage
> (`onlinelibrary.wiley.com/page/journal/20407947`) and against a
> user-provided copy of the live Author Guidelines.

---

## ⚠ Critical disambiguation — IJNMBE vs IJNME

Wiley publishes two similarly-named journals; do **not** confuse them.

| Item | **IJNMBE** (the journal recommended in this report) | **IJNME** (a different Wiley journal — out of scope for this paper) |
|---|---|---|
| Full name | International Journal for Numerical Methods in Biomedical Engineering | International Journal for Numerical Methods in Engineering |
| Print ISSN | 2040-7939 | 0029-5981 |
| Online ISSN | **2040-7947** | **1097-0207** |
| Wiley journal code | **NMB** (portal: `authors.wiley.com/journal/CNM`) | NME (portal: `authors.wiley.com/journal/NME`) |
| Editor-in-Chief | Perumal Nithiarasu (Swansea) | a different EiC |
| Scope | DE-based biomedical models + their numerical solutions; AI in scope | general computational engineering — FEA, structural mechanics, geomechanics |
| Letters section topic | biomedical engineering | "geomechanics" — a tell-tale sign you're on the wrong page |
| In scope for this paper? | **yes** | **no** — out of scope |

If you ever land on Author Guidelines that mention NME, geomechanics, or
ISSN 1097-0207, you are reading the wrong journal. Close the tab and use
ISSN 2040-7947.

---

## Phase 1 — Field inference (re-stated for the Q2 venue search)

| Dimension | Value |
|---|---|
| **Primary field** | Computational physiology / scientific machine learning applied to a validated ODE physiological model |
| **Secondary fields** | Biomedical engineering, mathematical biology, conformal prediction, OOD detection, sensitivity analysis |
| **Article type** | Original research / methods paper |
| **Reporting standard** | TRIPOD-AI (already in supplementary) |
| **Body word count** | ≈ 5,430 — generous on most Q2 candidates (none cap below 6,000) |
| **Tables / figures** | 4 / 6 — none of the Q2 candidates impose a hard 4-figure cap |
| **Validation strategy** | Synthetic-only (CGEM as ground truth) — fits methods-focused journals; clinical journals would still reject |
| **Software artefact** | FastAPI service + frontend + Docker image ship with the paper |
| **Author profile** | Self-funded LMIC author, **subscription / Find-path mandatory**; OA APCs out of scope |

The user's framing ("AI integrated into a mechanistic model in physiology") shifts
emphasis from clinical-aviation-medicine relevance toward the
*pattern itself*: a black-box surrogate + Mondrian conformal + Mahalanobis OOD
+ Sobol/Morris stack wrapping any validated ODE physiology model. Q2
modeling-and-simulation / mathematical-biology / numerical-biomedical-engineering
journals are exactly the venues where this framing reads as a contribution
rather than an oddity.

---

## Phase 3 — Candidate pool (search-verified APCs and quartiles, 2026-05-01)

Quartiles taken from Scimago 2024 (most recent available at search time);
JIFs from 2025 JCR / journalmetrics.org / journal homepages. Subscription /
non-OA "Find path" status reconfirmed against publisher policy pages.

| # | Journal | Publisher | Best Scimago quartile | JIF (2025) | OA status | APC for Diego (USD) | Find / non-OA path |
|---|---|---|---|---|---|---|---|
| A | International Journal for Numerical Methods in Biomedical Engineering | Wiley | **Q2** (Applied Math, Modeling & Sim, Software, Comp Theory) — Q3 Biomed Eng | **2.4** | Hybrid | 4,430 (OA, optional) | ✅ Free non-OA |
| B | Physiological Measurement | IOP Publishing / IPEM | **Q2** (Biomedical Engineering, Biophysics) — Q3 Physiology, Physiology (medical) | **2.7** | Hybrid | unverified at search | ✅ Free non-OA (IOP hybrid) |
| C | Mathematical Biosciences | Elsevier | **Q2** (Modeling & Sim, Applied Math, Medicine misc, Stats & Probability) | **1.8** | Hybrid (subscription primary) | unverified | ✅ Free non-OA |
| D | Journal of Theoretical Biology | Elsevier (Academic Press) | **Q2** (Modeling & Sim, Applied Math, Medicine misc, Stats & Prob) | **2.0** | Hybrid (subscription primary) | unverified | ✅ Free non-OA |
| E | Bulletin of Mathematical Biology | Springer | Best **Q1** (Math misc, Agri & Biol Sci misc); Q2 in Modeling & Sim, Comp Theory, Pharmacology | **2.2** | Hybrid | 2,990 (OA, optional) | ✅ Free non-OA |
| F | Computer Methods in Biomechanics and Biomedical Engineering | Taylor & Francis | Q3 Biomed Eng (WoS 22.3%) — borderline Q2/Q3 | 1.6 | Hybrid | unverified | ✅ Free non-OA |

### Eliminated outright (would be re-included if the Q2 cap were relaxed)

- **Computers in Biology and Medicine** (Q1) — primary recommendation in the prior scout; Q1 violates the new constraint.
- **Computer Methods and Programs in Biomedicine** (Q1) — was the previous target; Q1 violates the new constraint.
- **Artificial Intelligence in Medicine** (Q1) — same.
- **Annals of Biomedical Engineering** (Q1 in Biomed Eng) — same.
- **Frontiers in Physiology** (Q1) — also fully OA, no Find path.
- **PLOS Computational Biology** (Q1) — fully OA.
- **Journal of Computational Science** (Q1 in CS Theory & Methods, JIF 3.7) — Q1, eliminated by the user's quartile constraint.

### Eliminated on policy / scope grounds

- **Medical Engineering & Physics** (Elsevier/IPEM) — Scimago shows Q3 in both Biomedical Engineering and Biophysics in 2024; below the Q2 cut.
- **Computer Methods in Biomechanics and Biomedical Engineering** — kept as a fallback only; biomechanics-skewed scope (orthopaedics, dental, soft-tissue FEA) is a poor fit for cerebrovascular ODE physiology.
- **Bioengineering / Diagnostics / Sensors** (MDPI) — paid OA only, no subscription path.

### Honesty caveats

- APCs marked "unverified" were not lookup-confirmed at search time. They are
  not load-bearing because the user's path is the **subscription / Find-path**
  (free) on every candidate above; APCs only matter if Diego switches to OA.
- Journal-quartile databases sometimes disagree by one tier (Resurchify Q1
  vs. journalmetrics Q1 for Biocybernetics; Resurchify Q2 vs. WoS percentile
  Q3 for CMBBE). Where databases disagree, the table records the more
  conservative reading and flags it inline.

---

## Phase 4 — Scoring (top 6, Q2 cap enforced)

Per `SCORING_RUBRIC.md`. Weights: scope match (35) — heavier than the prior
scout because the Q2 cap removes the broad-scope Q1 alternatives;
APC accessibility (20); quartile / impact (15); expected acceptance odds (10);
word/figure caps (10); turnaround (5); audience reach (5).

| Rank | Journal | Quartile | JIF | APC for Diego | Word cap | Fig cap | Score | Notes |
|---|---|---|---|---|---|---|---|---|
| **1** | **International Journal for Numerical Methods in Biomedical Engineering** | **Q2** | **2.4** | **0 (Find)** | none stated | flexible | **86** | Surrogate ML wrapping a numerical biomedical ODE is *core* scope; Wiley peer-review is rigorous but methodology-friendly. |
| **2** | **Physiological Measurement** | **Q2** | **2.7** | **0 (Find)** | none stated | flexible | **84** | Scope explicitly lists "physiological modelling and simulation" + "novel methods of measurement and their validation"; EiC Xiao Hu publishes on AI in physiological signals. |
| **3** | **Mathematical Biosciences** | **Q2** | **1.8** | **0 (Find)** | none stated | flexible | **78** | Mathematical models of biological systems is the journal's stated remit; ML-as-surrogate of an ODE physiology model fits. Lower JIF; longer review cycle than #1 / #2. |
| 4 | Journal of Theoretical Biology | Q2 | 2.0 | 0 (Find) | none stated | flexible | 70 | Scope welcomes physiology + computational/statistical modeling, **but explicitly states "papers should bear significant importance on the biology *per se*, not the mathematical analysis"** — risk of desk-rejection of a method-forward manuscript unless the Discussion is rewritten with G-LOC mechanism as the lead. |
| 5 | Bulletin of Mathematical Biology | Q2 (best Q1) | 2.2 | 0 (Find) | none stated | flexible | 68 | Active "Tutorials on AI/ML in Classical Mathematical Biosciences" call is a tactical match, but best Scimago quartile is Q1 — borderline for a strict-Q2 ask. |
| 6 | Computer Methods in Biomechanics and Biomedical Engineering | Q2/Q3 borderline | 1.6 | 0 (Find) | none stated | flexible | 56 | Biomechanics framing is the wrong axis; would force re-positioning the manuscript away from cardiovascular/cerebral physiology. |

---

## Phase 5 — Top-3 recommendation

| Rank | Journal | Publisher | Quartile | APC (Diego) | Scope match | Word cap | Indexing | Score |
|---|---|---|---|---|---|---|---|---|
| **1** | **Int. J. Numerical Methods in Biomedical Engineering (IJNMBE)** | Wiley | **Q2** (Applied Math; Modeling & Sim; Software) | **$0 Find** | High — surrogate ML on a numerical biomedical ODE is core scope | None stated | Scopus, SCIE, MEDLINE, PubMed | **86** |
| **2** | **Physiological Measurement** | IOP / IPEM | **Q2** (Biomedical Engineering; Biophysics) | **$0 Find** | Highest — "physiological modelling and simulation" + measurement validation are explicit scope items | None stated | Scopus, SCIE, MEDLINE, PubMed | **84** |
| **3** | **Mathematical Biosciences** | Elsevier | **Q2** (Modeling & Sim; Medicine misc; Stats & Prob) | **$0 Find** | Strong — wraps a validated ODE biological model with a methodological contribution generalisable to other systems | None stated | Scopus, SCIE | **78** |

### #1 — *International Journal for Numerical Methods in Biomedical Engineering* (IJNMBE)

**Verified scope (Wiley homepage, 2026-05-01):**

> "All differential equation based models for biomedical applications and
> their novel solutions (using either established numerical methods such
> as finite difference, finite element and finite volume methods or new
> numerical methods) are within the scope of this journal. Manuscripts
> with experimental and analytical themes are also welcome if a component
> of the paper deals with numerical methods. **Special cases that may
> not involve differential equations such as image processing, meshing
> and artificial intelligence are within the scope.** Any research that
> is broadly linked to the wellbeing of the human body, either directly
> or indirectly, is also within the scope of this journal."

**Verified explicit filter (template / aims-and-scope guidance):**

> "Authors are reminded that application of a standard numerical procedure
> to a standard problem is not within the scope of this journal."

**Fit rationale.** Two scope clauses are load-bearing for this manuscript:
the explicit "**artificial intelligence** is within the scope" clause, and
"any research broadly linked to the wellbeing of the human body, either
directly or indirectly." The CGEM paper is an AI-augmented wrapper of an
ODE physiological model used in civil-aviation regulation — a direct match
on both. Editor-in-Chief **Perumal Nithiarasu** (Swansea) is a
computational-cardiovascular-physiology editor with a long publication
record on patient-specific arterial flow modelling, lumped-parameter
cardiovascular systems, and one-dimensional arterial blood-flow surrogates;
the cerebrovascular and cardiovascular ODE machinery in CGEM is native
territory for him. Recent IJNMBE papers in the surrogate-of-physiological-
ODE space include Kakhaia et al. (2021) on inverse uncertainty
quantification of mechanical arterial-tissue models with ML surrogates,
and a published benchmark study of numerical schemes for one-dimensional
arterial blood flow.

**Tradeoff.** Scimago classifies IJNMBE as Q2 in Applied Mathematics,
Computational Theory and Mathematics, Modeling and Simulation, and Software,
and Q3 in Biomedical Engineering and Molecular Biology. The JIF 2.4 (2025;
5-year IF 2.4) is slightly below Physiological Measurement's 2.7. Best
ranking in WoS is "Mathematics, Interdisciplinary Applications" (73.5%).

**Risk and what addresses it.** The "no standard procedure on a standard
problem" filter is the principal risk: a reviewer reading "we applied
XGBoost to a Fortran model" will trigger a desk-rejection on this clause.
The paper must lead with the *combination* — Mondrian split-conformal
prediction stratified by maneuver category + conformal-Mahalanobis OOD
abstention + the two-stage classifier-then-regressor pattern for
right-censored event-time targets — as the methodological contribution,
with CGEM as the worked example. The novelty pitch already exists in the
manuscript; it just needs to be the explicit lead in §1 and in the
mandatory **Novelty File** (≤ 100 words, see practical specifics below).
TRIPOD-AI compliance and OSF pre-registration are assets at this venue,
not curiosities.

**Practical specifics relevant to this manuscript (verified 2026-05-01).**

| Item | IJNMBE rule |
|---|---|
| Submission portal | `https://authors.wiley.com/journal/CNM` |
| Submission style | **Free Format** — references in any consistent style; abstract structured *or* unstructured |
| Abstract cap | **≤ 400 words** (current 341 → in compliance) |
| Keywords | up to **6** in the Manuscript Style section (some Free Format guidance says 7) — use 6 to be safe |
| **Novelty File** | **mandatory**, separate file, itemised list, ≤ 100 words, not a duplicate of the abstract |
| **Graphical Abstract + Graphical TOC** | **mandatory** — graphic + ≤ 80-word / 3-sentence mini-abstract |
| Practitioner Points | optional, ≤ 3 bullets |
| Title page declarations | data availability, funding, COI, ethics, patient consent (n/a here), permissions, clinical-trial registration (n/a here) — all on the title page |
| Page charges | **none** |
| Colour figures | **free** when colour aids understanding |
| Figures | one per file at revision; compound figures (1a, 1b…) in one file; **no tints** (greyscale shading); legends below each figure AND a complete legend list in the text |
| Reference style | Free Format on submission; AMA-like in production; DOIs at end of each reference |
| Data and code | mandatory archiving in a public repository; data accessibility statement published with the article; data and code uploaded as **Data Files** (separate from Supporting Information); on acceptance Wiley deposits Data Files to figshare under CC-Zero by default |
| Data citation | data must be cited formally in the reference list per the Joint Declaration of Data Citation Principles |
| Peer review | single-anonymous (Wiley default; double-anonymous **not** offered on this title) |
| Continuous Publication | yes — fast time to citable VoR |
| Preprint policy | arXiv / bioRxiv / engrXiv permitted; update preprint with link to final article on publication |
| Find path | Wiley hybrid: subscription submission is the default and free; OA APC ~ USD 4,430 if elected (not needed) |

**Indexing.** Scopus, SCIE (categories: Mathematical & Computational Biology;
Mathematics, Interdisciplinary Applications; Engineering, Biomedical),
MEDLINE, PubMed.

**Find path.** Wiley hybrid; subscription submission is the default and is
free. OA APC ~USD 4,430 if elected (not needed).

**Companion skill.** A reusable submission skill is installed at
`~/.claude/skills/ijnmbe-submit/`. Invoke with `/ijnmbe-submit` plus a
mode (`status`, `check`, `cover-letter`, `novelty`, `graphical`, `upload`,
`reviewers`, `revision`, `rules`) to drive any IJNMBE-bound manuscript
through the submission workflow.

### #2 — *Physiological Measurement* (IOP Publishing / IPEM)

**Fit rationale.** Physiological Measurement's scope explicitly enumerates
"physiological modelling and simulation" alongside "advanced methods of
time series and other data analysis," "biomedical and clinical engineering,"
and the "development of new methods of measurement and their *validation*."
The manuscript validates a surrogate of a regulatory physiological model,
calibrates conformal intervals, and benchmarks a novel OOD detector — all
inside the journal's stated remit. Editor-in-Chief Xiao Hu (Emory) is an
active publisher of AI / ML in physiological monitoring; the paper's
positioning aligns with the editorial direction.

**Tradeoff.** Physiology and Physiology (medical) sit at Q3 in the Scimago
table for this journal; the Q2 ranking comes from Biomedical Engineering
and Biophysics. The journal is an excellent home for the *measurement-
validation* framing of the paper, less so for a "regulatory physiological
model" framing — the cover letter should foreground the validation /
calibration / OOD-guard angle. JIF 2.7 (2025) is the highest of the three
Q2 finalists.

**Risk.** The journal's modal paper is signal-/measurement-driven (PPG,
ECG, EIT, federated learning on sleep data). A paper without primary
physiological measurements may need extra explicit framing as a "validation
methodology for measurement-derived ODE models" rather than as a pure
ML-on-Fortran piece.

**Indexing.** Scopus, SCIE, MEDLINE, PubMed.

**Find path.** IOP hybrid: subscription submission free; OA APC optional.

### #3 — *Mathematical Biosciences* (Elsevier)

**Fit rationale.** Mathematical Biosciences "publishes work providing new
concepts or new understanding of biological systems using mathematical
models, or methodological articles likely to find application to multiple
biological systems." The CGEM paper's stated generalisability — "the
surrogate + conformal + OOD pattern generalises to any validated ODE
physiological model" — maps directly onto the journal's "methodological
articles likely to find application to multiple biological systems"
clause. Mondrian conformal stratification and Mahalanobis-conformal OOD
abstention are exactly the kind of methodological vocabulary the journal
prefers.

**Tradeoff.** JIF 1.8 (2025) — the lowest of the three finalists. A modest
reach but a clean methodological match. Reviewer pool is mathematical
biologists, who will engage seriously with the conformal coverage tables
and the Sobol indices but may regard XGBoost as workmanlike rather than
novel; the methodology novelty pitch must lead with the *Mondrian
stratification by maneuver category + conformal OOD as a unified
abstention layer*, not with the surrogate per se.

**Risk.** Mathematical Biosciences favours papers with explicit dynamical-
systems insight (stability, bifurcation, asymptotic analysis). The CGEM
paper does not provide that; it provides a calibrated emulator. The
paper's contribution should therefore be framed as *methodological*
("a generalisable wrapper pattern for validated ODE biological models")
rather than as an analytical study of CGEM's dynamics, to avoid a
scope-mismatch desk decision.

**Indexing.** Scopus, SCIE, Embase.

**Find path.** Elsevier hybrid: subscription submission is the default and
is free for all authors; per Elsevier policy, hybrid OA APCs are *not*
waivable, but the subscription path requires no waiver.

---

## Cross-cutting observations

### Why Q2, not Q1 — the explicit acceptance-rate tradeoff

The Q1 set in the prior scout (CBM / CMPB / AIM, all JIF ~5–7) has a
broader readership and higher citation potential, but in 2024 desk-rejection
rates at all three are anecdotally 50–60 %, with peer-review acceptance
rates in the 15–25 % range. The Q2 finalists above operate at 30–45 %
acceptance ranges anecdotally; the methods-paper framing also lands more
easily on Q2 modeling-and-simulation editors who are looking for exactly
this kind of contribution.

The honest tradeoff is that Q2 placement costs roughly half a citation
percentile and a notch of JIF, in exchange for materially higher first-
submission acceptance odds and a more methodology-friendly review pool.
For paper 1 of a three-paper series — where paper 2 (own-centrifuge data)
and paper 3 (full real-world validation) will be the citation drivers
anyway — Q2 placement of paper 1 is a defensible strategic choice.

### What changes vs. the CMPB submission package

If switching from CMPB to **IJNMBE** (top recommendation):

- **Cover letter** — drop the CMPB-specific block, replace with Wiley's
  standard cover-letter structure (originality, conflict declaration,
  significance pitch). Lead the significance pitch with the *numerical-
  methods* framing: "a generalisable surrogate + conformal + OOD pattern
  for validated biomedical ODE models," with CGEM / G-LOC as the worked
  example. Address to **EiC Perumal Nithiarasu**.
- **Novelty File** — **new mandatory file** at IJNMBE; ≤ 100 words, itemised
  list of new contributions, **must not duplicate the abstract**. Lead with
  the Mondrian split-conformal stratification by maneuver category, the
  conformal-Mahalanobis OOD abstention, the two-stage censored-event-time
  pattern, and the additive-wrapper preservation of the FAA-validated core.
- **Graphical Abstract + Graphical TOC entry** — **new mandatory items**;
  one graphic + ≤ 80-word / 3-sentence mini-abstract summarising the key
  result (e.g., the Mondrian conformal coverage table or a side-by-side
  speed/coverage summary).
- **Title** — already good for IJNMBE; could optionally read "Conformal
  ML emulation, OOD detection, and global sensitivity analysis for a
  validated ODE physiological model: the FAA CGEM G-LOC case study."
- **Suggested reviewers** — swap the CMPB editorial-board picks for IJNMBE
  editorial-board members in computational cardiovascular / cerebrovascular
  modeling; keep the AMHP-era aerospace-medicine reviewer as a domain-
  application reviewer.
- **Introduction §1** — already inverts the framing the right way for
  IJNMBE; no rewrite needed beyond a 1-paragraph primer on the cerebrovascular
  ODE physiology for the broader biomedical-engineering audience and a
  1-paragraph rebuttal of the implicit "standard procedure on standard
  problem" filter (i.e., what specifically is *not* standard about the
  combined Mondrian + conformal-OOD + Sobol-on-surrogate stack).
- **Methods §2** — no change. The TRIPOD-AI checklist and the pre-registration
  remain assets.
- **Discussion §4** — re-emphasise the *generalisability* claim (any
  validated ODE physiological model) and explicitly cite recent IJNMBE
  precedents (Kakhaia et al. 2021 on arterial-tissue ML surrogates with
  inverse UQ; the IJNMBE benchmark study of one-dimensional arterial
  blood-flow numerical schemes).
- **Reference list** — add 2–3 ML-surrogate-on-ODE references that have
  appeared in IJNMBE / IJNMF / Comp Methods Appl Mech Eng (e.g., Liang et
  al. on aortic-geometry ML surrogate; multi-fidelity surrogate modeling
  for soft-tissue FEA papers from CBM 2022–2024). Cite the dataset
  formally in the reference list per the Joint Declaration of Data Citation
  Principles (Authors; Year; Dataset; Repository; Version; DOI).
- **Data and code** — must be archived in a public repository (GitHub +
  OSF satisfy this); upload as **Data Files** (separate from Supporting
  Information) at submission; on acceptance, Wiley deposits Data Files to
  figshare under CC-Zero by default.
- **Title page** — Wiley requires the data availability, funding,
  COI, ethics, permissions statements on the title page (not at the end
  of the manuscript).
- **Reference style conversion** — **none required at submission** (Free
  Format — current Vancouver-style is accepted as long as it is consistent).
  Production will reformat to AMA-like.

If switching to **Physiological Measurement** instead, additionally:

- Foreground "calibration of a physiological measurement-derived model" in
  the abstract (not "emulation of a Fortran black-box") — this is the
  scope-fit lever for IOP/IPEM.
- Add a paragraph in §2 on how CGEM's input variables are *measured* in
  centrifuge protocols (Nz time series, anthropometric inputs) — this
  re-anchors the paper inside Physiological Measurement's measurement-
  centric remit.

If switching to **Mathematical Biosciences** instead, additionally:

- Lead the abstract with the *methodological pattern* and de-emphasise
  CGEM-specific aerospace context to avoid a scope-mismatch desk decision.
- Add a half-page §2 subsection on the structural identifiability /
  monotonicity assumptions imposed in the surrogate — this is the kind of
  mathematical content Mathematical Biosciences reviewers expect even from
  a methods paper.

### Hard "no" for paper 1 (unchanged from prior scout)

- **NEJM, Lancet Digital Health, Nature Medicine, JAMA, BMJ, npj Digital
  Medicine, npj Systems Biology** — synthetic-only validation is a hard
  rejection criterion; revisit at paper 3 (own-centrifuge data).

---

## Phase 8 — Summary

```
✓ Journal Scout complete (Q2 physiology pivot)
  Papers scouted:           1 (CGEM ML emulator, paper 1)
  Candidates considered:    11
  Q2 Find-path candidates:  6 (IJNMBE, Physiol Meas, Math Biosci,
                                J Theor Biol, Bull Math Biol, CMBBE)
  Top picks:
    #1 Int. J. Numer. Methods Biomed. Eng. (Wiley)   Q2  $0 Find  86
    #2 Physiological Measurement (IOP/IPEM)          Q2  $0 Find  84
    #3 Mathematical Biosciences (Elsevier)           Q2  $0 Find  78
  Output: docs/publication/2026-05-01_journal-scout_cgem-q2-physiology.md
  Verified: quartiles via Scimago 2024; JIFs via 2025 JCR / journalmetrics;
  Find-path policy via Elsevier / Wiley / IOP hybrid pages;
  IJNMBE scope re-verified directly from Wiley journal homepage
  (ISSN 2040-7947, NOT IJNME = 1097-0207) on 2026-05-01;
  IJNMBE submission rules re-verified from user-provided live Author
  Guidelines (Free Format, ≤ 400-word abstract, mandatory Novelty File,
  mandatory Graphical Abstract, single-anonymous, Continuous Publication,
  no page charges).
  Unverified: exact OA APCs at IOP and Elsevier hybrid pages
  (immaterial — Diego's path is subscription / Find).
  Companion skill: ~/.claude/skills/ijnmbe-submit/ (installed 2026-05-01)
```

### One-line recommendation

Submit paper 1 to **International Journal for Numerical Methods in
Biomedical Engineering** (Wiley, Q2, JIF 2.4, free Find path, scope-
matched on "numerical methods + biomedical applications"); keep
**Physiological Measurement** (IOP/IPEM) and **Mathematical Biosciences**
(Elsevier) as the fallback ladder if IJNMBE rejects on first round.

### What to do next

1. Pick one of the three finalists and confirm the choice.
2. On confirmation, run `/journal-scout guide IJNMBE` (or the chosen
   journal) to extract the full Author Guidelines and produce a
   submission package — cover letter, suggested-reviewer slate,
   declarations checklist, format-conversion plan from the existing
   CMPB-shaped manuscript.
3. Revert the recent CMPB-specific edits (commits `79347c8` and `d6375eb`)
   to a target-journal-agnostic baseline before re-tailoring; alternatively
   keep them on a `cmpb-backup` branch in case the Q2 path falls through
   and CMPB becomes plan B.
4. Re-export the OpenAPI spec and contract tests untouched; no code
   changes are implied by the venue change.
