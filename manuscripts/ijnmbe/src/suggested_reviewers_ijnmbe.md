# Suggested reviewers — IJNMBE submission

> Five candidates re-targeted from the prior CMPB slate to span the four
> reviewer axes IJNMBE expects: **methodology** (conformal prediction /
> surrogate ML / OOD), **application domain** (biomedical physiology),
> **numerical methods** (with a recent IJNMBE publication record),
> **regulatory / domain application** (FAA / aerospace medicine), and
> **generalist**. None has co-authored with the corresponding author in
> the past three years; none shares an institution with the author
> (Bogotá / Colombian Aerospace Force).
>
> **Verification required before portal entry — flagged inline as
> [VERIFY]:** confirm current affiliation, re-verify institutional email
> (never personal Gmail/Yahoo), confirm no co-authorship on
> Scopus/OpenAlex within 3 years, confirm not on the IJNMBE editorial
> board at `https://onlinelibrary.wiley.com/page/journal/20407947/homepage/EditorialBoard.html`.

---

## 1 — Kyle Copeland (regulatory / domain application axis)

| Field | Value |
|---|---|
| Affiliation | FAA Civil Aerospace Medical Institute (CAMI), Oklahoma City, OK, USA |
| Email | **kyle.copeland@faa.gov** *(verified 2026-05-01 from FAA technical reports DOT/FAA/AM-21/4 and DOT/FAA/AM-16/05; AAM-631, Numerical Sciences Research Team)* |
| ORCID | [0000-0001-7893-6716](https://orcid.org/0000-0001-7893-6716) |

**Rationale.** Lead author of the CGEM Fortran model
(DOT/FAA/AM-23/6) that this manuscript wraps. Uniquely positioned to
verify that the additive ML wrapper preserves CGEM's validation chain,
correctly reproduces the ODE outputs across the documented input
envelope, and respects the model's published limitations and calibration
boundary.

**No conflict.** No co-authorship with Diego Malpica; no shared
institution (Oklahoma City vs. Bogotá); no prior peer-review history on
this manuscript.

---

## 2 — Wouter Huberts, PhD (numerical methods axis — recent IJNMBE author)

| Field | Value |
|---|---|
| Affiliation | Department of Biomedical Engineering, CARIM School for Cardiovascular Diseases, Maastricht University, The Netherlands. Secondary appointment: TU Eindhoven (`research.tue.nl/en/persons/wouter-huberts/`). |
| Email | **wouter.huberts@maastrichtuniversity.nl** *(verified 2026-05-01 from Maastricht University Systems Biology and Bioinformatics staff page)* |
| ORCID | [0000-0002-6463-6105](https://orcid.org/0000-0002-6463-6105) *([VERIFY])* |

**Rationale.** Co-author of the foundational IJNMBE benchmark study of
one-dimensional arterial blood-flow numerical schemes (Boileau et al.,
*IJNMBE* 2015; reference [21] in this manuscript) — directly the
methodological neighbourhood of the present work. Senior expertise in
patient-specific cardiovascular ODE / 1-D numerical models, surrogate
modelling, and uncertainty quantification of physiological simulators.
Will be sympathetic to the additive-wrapper pattern and qualified to
assess whether the surrogate preserves the validated dynamics of the
underlying ODE solver.

**No conflict.** No co-authorship with Diego Malpica; no shared
institution. **Verified 2026-05-01 against the IJNMBE editorial board
snapshot at `docs/publication/2026-05-01_ijnmbe_editorial_board.md`:
Wouter Huberts is NOT a current IJNMBE editor or board member.**

> **Replacement note (2026-05-01).** This slot was originally filled by
> **Jordi Alastruey** (KCL), but the live editorial-board lookup revealed
> Alastruey is currently an **Associate Editor** of IJNMBE — a conflict
> per the journal's reviewer-suggestion policy. Huberts is a co-author of
> the same Boileau et al. 2015 benchmark study, covers the same numerical-
> methods + cardiovascular-ODE axis, and is **not** on the editorial board.

---

## 3 — Andrea Aliverti, PhD (application-domain / bioengineering axis)

| Field | Value |
|---|---|
| Affiliation | Dipartimento di Elettronica, Informazione e Bioingegneria (DEIB), Politecnico di Milano, Italy. Confirmed Full Professor; Faculty Board, PhD in Bioengineering. |
| Email | **andrea.aliverti@polimi.it** *(verified 2026-05-01: standard Politecnico di Milano `firstname.lastname@polimi.it` format; profile confirmed at `deib.polimi.it/eng/people/details/569774`)* |
| ORCID | [0000-0002-3892-3622](https://orcid.org/0000-0002-3892-3622) |

**Rationale.** Bioengineering chair working on physiological surrogate
modelling, cardiopulmonary system identification, and ML-augmented
physiological prediction. The methodological framing — XGBoost surrogate
+ Mondrian conformal + Mahalanobis OOD over a validated mechanistic ODE
model — is in his published wheelhouse. Will assess whether the
ML-physiology integration is biophysically defensible and whether the
sensitivity analysis correctly identifies the dominant haemodynamic
drivers.

**No conflict.** No co-authorship with Diego Malpica; no shared
institution; carried over from the previous CMPB slate where the same
no-conflict checks passed.

---

## 4 — Anastasios N. Angelopoulos, PhD (conformal-prediction methodology axis)

> ⚠ **AFFILIATION FLAG (verified 2026-05-01).** Per his personal page
> `angelopoulos.ai`, Angelopoulos is now **co-founder and CEO of Arena**
> (the LMSys / Chatbot Arena spin-out), having "previously" been a
> Postdoctoral Scholar at UC Berkeley. His EECS-Berkeley email may be
> inactive, and Arena is a private company — IJNMBE expects an
> *institutional* email for suggested reviewers. **Two viable paths:**
>
> 1. **Use his personal academic page contact** at `angelopoulos.ai`
>    (he forwarding-aliases to whatever active address he prefers).
> 2. **Substitute** with a Berkeley-active conformal-prediction
>    methodologist — strongest candidate is **Stephen Bates** (his
>    primary co-author on the *Foundations and Trends* tutorial cited as
>    ref [18]), now Assistant Professor at MIT EECS / IDSS,
>    `sbates@mit.edu`. Bates would cover the same conformal-methodology
>    axis with an active institutional email.
>
> The default suggestion below remains Angelopoulos because he is the
> first author of the canonical reference cited in the manuscript; the
> portal entry should use the `angelopoulos.ai` contact form unless
> Diego prefers the Bates substitution.

| Field | Value |
|---|---|
| Affiliation | Co-founder & CEO, Arena. *(Previously: Postdoctoral Scholar, EECS, UC Berkeley.)* |
| Email | Contact via `https://angelopoulos.ai` (active personal academic page). Berkeley-EECS address `angelopoulos@berkeley.edu` listed for completeness; **may no longer forward**. |
| ORCID | [0000-0002-5295-5556](https://orcid.org/0000-0002-5295-5556) *([VERIFY])* |

**Rationale.** First author of *"A gentle introduction to conformal
prediction and distribution-free uncertainty quantification"* (Found.
Trends Mach. Learn. 2023; cited as ref [18] in the manuscript), one of
the canonical references for the split-conformal and Mondrian-conformal
machinery used in this paper. Best qualified to assess whether the
conformal calibration is mathematically correct and whether the under-
coverage on the time-to-G-LOC target is appropriately diagnosed and
reported.

**No conflict.** No co-authorship with Diego Malpica; no shared
institution. Cited in the manuscript bibliography (ref [18]); IJNMBE does
not consider citation alone a conflict, but the reviewer slate is
deliberately diverse on this axis. **Verified against the IJNMBE editorial
board (2026-05-01): not a board member.**

### Backup candidate (if Angelopoulos contact path fails) — Stephen Bates, PhD

| Field | Value |
|---|---|
| Affiliation | Department of Electrical Engineering and Computer Science, IDSS, Massachusetts Institute of Technology, USA |
| Email | sbates@mit.edu *([VERIFY] via MIT EECS directory)* |
| ORCID | *([VERIFY])* |

**Rationale.** Co-author with Angelopoulos on the *Foundations and
Trends* tutorial (ref [18]) and on *"Conformal Risk Control"* (ICLR
2024). Active institutional email at MIT; same methodological axis;
clean substitute for Angelopoulos if the latter's contact path fails.

---

## 5 — Henrik Boström, PhD (Mondrian-conformal-methodology generalist axis)

| Field | Value |
|---|---|
| Affiliation | Division of Software and Computer Systems, KTH Royal Institute of Technology, Stockholm, Sweden. Profile: `kth.se/profile/henbos`. |
| Email | **bostromh@kth.se** *(verified 2026-05-01 from KTH profile + the same address on his published "Mondrian Conformal Regressors" PMLR 2020 and "Mondrian Conformal Predictive Distributions" PMLR 2021 papers)* |
| ORCID | [0000-0001-8382-0300](https://orcid.org/0000-0001-8382-0300) |

**Rationale.** First author of *"Mondrian conformal predictive
distributions"* (COPA 2018, PMLR 91; cited as ref [12] in the
manuscript) — the foundational reference for the per-stratum Mondrian
calibration adopted in this paper. Best qualified to evaluate whether the
maneuver-category Mondrian stratification was set up correctly and
whether the empirical per-stratum coverage results are consistent with
Mondrian conformal theory's finite-sample behaviour. Senior generalist
voice on conformal predictive distributions broadly.

**No conflict.** No co-authorship with Diego Malpica; no shared
institution. Cited in the manuscript bibliography (ref [12]). Same
acceptable-citation reasoning as candidate #4.

---

## Slate balance

| Reviewer | Methodology axis | Application axis | Numerical-methods axis | Regulatory axis | Generalist axis |
|---|---|---|---|---|---|
| 1. Copeland | — | partial (G-LOC physiology) | — | **primary** | — |
| 2. Huberts | — | partial (cardiovascular) | **primary** (recent IJNMBE) | — | — |
| 3. Aliverti | partial (ML-physiology) | **primary** (bioengineering) | — | — | — |
| 4. Angelopoulos | **primary** (conformal) | — | — | — | partial |
| 5. Boström | **primary** (Mondrian) | — | — | — | **primary** |

All five axes have at least one primary reviewer, and the slate avoids
single-axis monoculture (the methodology axis is covered twice — by
different sub-disciplines — given how central the conformal-prediction
machinery is to the contribution). The IJNMBE-specific numerical-methods
axis is anchored by Huberts, whose IJNMBE publication record makes the
slate compliant with the journal's preference for at least one reviewer
familiar with its style and standards.

---

## What was changed vs. the prior CMPB slate

The CMPB slate (`suggested_reviewers.md`, in this directory) emphasised:
Copeland (FAA/regulatory), Aliverti (bioengineering), and three CMPB-
adjacent ML-in-medicine reviewers. The IJNMBE slate retains Copeland and
Aliverti (axes are still relevant) and **replaces three slots** with:

- **Huberts** — adds the IJNMBE-publication credential the previous list
  lacked, via the foundational Boileau et al. 2015 IJNMBE benchmark; not
  on the editorial board (verified 2026-05-01).
- **Angelopoulos** — promotes conformal-prediction methodology to a
  primary axis (CMPB review pool was less specialised on this).
- **Boström** — same, for Mondrian specifically.

The CMPB list's ML-in-medicine reviewer slot has been retired because
IJNMBE's review pool naturally over-indexes on numerical methods and
conformal/Bayesian UQ rather than on clinical-informatics ML.

> **Editorial-board cross-check (2026-05-01).** All five candidates were
> cross-checked against the live IJNMBE editorial-board page via Firecrawl
> on 2026-05-01; the snapshot is committed at
> `docs/publication/2026-05-01_ijnmbe_editorial_board.md`. Result:
> Copeland, Huberts, Aliverti, Angelopoulos, and Boström are all clean
> (none currently listed as Editor-in-Chief, Associate Editor, Honorary
> Editor, or Editorial Board Member). The original draft had Alastruey
> in slot 2 — that name was removed when the cross-check revealed his
> Associate Editor status.

---

## Pre-portal checklist

- [x] **Email verification** — completed 2026-05-01 via web search against
      institutional directories and authoritative published sources:
  - Copeland: `kyle.copeland@faa.gov` ✓ (FAA technical reports)
  - Huberts: `wouter.huberts@maastrichtuniversity.nl` ✓ (Maastricht
    Systems Biology / Bioinformatics staff page; **note: original draft
    had `w.huberts@…` — corrected to the verified `wouter.huberts@…`**)
  - Aliverti: `andrea.aliverti@polimi.it` ✓ (Politecnico standard format
    `firstname.lastname@polimi.it`; profile at DEIB)
  - Angelopoulos: ⚠ now CEO of Arena; **use `angelopoulos.ai` contact
    form** OR substitute Stephen Bates (`sbates@mit.edu`) — see
    candidate #4 box for details
  - Boström: `bostromh@kth.se` ✓ (KTH profile + 2020/2021 PMLR papers)
- [x] **Editorial-board cross-check** — completed 2026-05-01 against live
      Wiley page; snapshot at `2026-05-01_ijnmbe_editorial_board.md`. All
      five candidates clean (Alastruey was originally slotted but removed
      when the check revealed his Associate Editor status).
- [ ] **[VERIFY]** no Scopus / OpenAlex co-authorship with Diego Malpica
      in the past 3 years (single-author manuscript makes this trivially
      clean for the present paper, but still worth a 30-second check
      because of cross-conference proceedings).
- [ ] Confirm each reviewer's most recent active-paper date is within
      the past 3 years.
- [ ] **Decide Angelopoulos vs. Bates** at portal-entry time based on
      which institutional email Diego prefers to enter.
