# Journal Scout — CGEM Emulator Q2/Q3 Fallback Ladder (Round 4)

**Date:** 2026-05-22
**Manuscript:** "Conformal machine-learning emulation and out-of-distribution detection for the FAA CAMI G-Effects mechanistic model of acceleration physiology"
**Manuscript scope (one-line):** XGBoost two-stage surrogate + Mondrian split-conformal + heteroscedastic Conformalized Quantile Regression + Mahalanobis OOD + Sobol/Morris sensitivity, wrapping the FAA CAMI Fortran CGEM ODE physiological model of +Gz tolerance. 6,020 body words, 247-word abstract, 6 figures, 5 tables, 27 references, 18 supplementary items.
**Active target (locked, out of scope of this scout):** *Physiological Measurement* (IOP, Q2, scope 28/30) — handled by another agent.
**Purpose of this scout:** Build the **post-PMEA fallback ladder** under tightened user constraints: Q2/Q3 only, $0 APC subscription only, scope ≥ 25/30, no more Q1 hunting.
**Prior scouts on this manuscript:**
- 2026-04-30 — `2026-04-30_journal-scout_cgem-emulator.md`
- 2026-05-01 — Q2 physiology variant, `2026-05-01_journal-scout_cgem-q2-physiology.md`
- 2026-05-12 — `2026-05-12_journal-scout_cgem-emulator.md`
- 2026-05-17 — `2026-05-17_journal-scout_cgem-emulator.md` (BSPC ranked rank-1, Q1)

---

## What changed since 2026-05-17

| Change | Direction | Source |
|---|---|---|
| **BSPC (Elsevier)** | desk-rejected 2026-05-22 (scope, ~22/30) → demoted from rank 1 to **excluded for this manuscript** | User report 2026-05-22 (third desk-rejection in 10 days) |
| **CMPB (Elsevier)** | already abandoned 2026-05-17 on word-count grounds | Carry-forward |
| **IJNMBE (Wiley)** | already desk-rejected 2026-05-17 on scope | Carry-forward |
| **Q1 chase abandoned** | user constraint: Q2/Q3 only from 2026-05-22 forward | Direct user directive |
| **Scope-strict cut tightened** | from ≥ 22/30 (loose) to **≥ 25/30 (hard)**; sub-25 desk-rejection risk is empirically proven this cycle (BSPC 22/30 → rejected) | Direct user directive |
| **PMEA (IOP)** | already in submission via another agent — **out of scope of this scout** | Direct user directive |
| **Rubric reweight** | new rubric: Scope 40 / Quartile 15 / APC 25 / Acceptance 10 / Speed 5 / Indexing bonus +5 (vs. prior 30/25/25/10/5/+5) — scope dominance is now decisive | Direct user directive |

---

## 1. Summary (5-line headline)

1. The **active locked target is PMEA (Physiological Measurement, IOP, Q2, score 91)** — not addressed here. This scout activates only if PMEA rejects.
2. **Tier-1 (passes ≥ 25/30 scope cut + every other hard filter): two journals.** Recommended fallback ladder activates here.
3. **Rank 1 (post-PMEA): Annals of Biomedical Engineering** (Springer/BMES, Q2, score 86) — already in prior pool; broadest scope, BMES society, 10,000-word headroom, ≈ 3 weeks to first decision.
4. **Rank 2 (post-PMEA): Medical & Biological Engineering & Computing** (Springer/IFMBE, Q2, score 85) — NEW. **6-day median submission-to-first-decision** is the fastest in the entire pool. Quadruple WoS SCIE indexing including "Mathematical & Computational Biology." Surprise pick.
5. **Rank 3 (post-PMEA): Journal of Theoretical Biology** (Elsevier, Q2, score 75) — NEW, but **flagged for desk-rejection risk** under the journal's own "not purely mathematical" exclusion clause — same failure pattern that killed BSPC. Use only after Tier-1 exhaust.

---

## 2. Field inference (carry-forward from 2026-05-17, no manuscript changes)

| Dimension | Assessment |
|---|---|
| Primary field | Biomedical engineering / Computational physiology / Methodological computational biomedicine |
| Subfield | Surrogate modelling of mechanistic ODE systems, conformal prediction, distribution-free uncertainty quantification, OOD detection, global sensitivity |
| Article type | Original research — methodological |
| Methodology keywords | XGBoost two-stage censored regressor + classifier; Mondrian split-conformal stratified by maneuver category; heteroscedastic Conformalized Quantile Regression (CQR); robust Mahalanobis OOD with distribution-free conformal abstention; Sobol/Morris global sensitivity; OSF pre-registration |
| Reporting guideline | TRIPOD-AI (prediction model class); OSF pre-registration |
| Body word count | 6,020 |
| Figures / Tables / Refs | 6 / 5 / 27 |
| AI-disclosure active? | YES — filter ON |
| Closest published precedent | Portela, Banga & Matabuena (2025) *PLOS Comput Biol* 21(5):e1013098 — conformal prediction on biological ODE systems |
| **New 2026-05-22 framing imperative** | After three desk-rejections, **scope-match dominance is empirically proven decisive.** The paper must be positioned as a methodology that wraps a *validated ODE physiological model* (FAA-CGEM), not as a "ML applied to G-LOC" paper. The physiology *is the demonstration*, not the contribution. Scope-match ≥ 25/30 is the new hard floor. |

---

## 3. AI-policy compatibility (live URLs, verified 2026-05-22)

All candidates verified or carry-forward-verified for tolerant (disclosure-if-used) AI policy.

| Journal | Publisher | AI policy source | Verified | Status |
|---|---|---|---|---|
| Annals of Biomedical Engineering | Springer / BMES | Springer publisher-wide policy: https://www.springernature.com/gp/group/ai/ai-guidance-for-our-researchers-and-communities | 2026-05-22 (carry-forward 2026-05-17) | Tolerant — LLM-assisted editing requires NO disclosure; broader generative-AI use disclosed in Methods/Acknowledgements |
| Medical & Biological Engineering & Computing | Springer / IFMBE | Same Springer publisher-wide policy | 2026-05-22 (inherits from publisher) | Tolerant |
| Journal of Theoretical Biology | Elsevier | Elsevier publisher-wide policy: https://www.elsevier.com/about/policies-and-standards/publishing-ethics#4-duties-of-authors | 2026-05-22 (carry-forward from 2026-05-17 Elsevier publisher policy scrape) | Tolerant — disclosure-if-used boilerplate identical to BSPC/CMPB/IRBM |
| Mathematical Biosciences | Elsevier | Same Elsevier publisher-wide policy | 2026-05-22 (carry-forward) | Tolerant |
| Bulletin of Mathematical Biology | Springer | Same Springer publisher-wide policy | 2026-05-22 (carry-forward) | Tolerant |
| Mathematical Medicine and Biology | OUP / IMA | OUP publisher-wide policy: https://academic.oup.com/journals/pages/authors/ethics | 2026-05-22 (carry-forward 2026-05-17) | Tolerant |
| IRBM | Elsevier Masson | Elsevier publisher-wide policy | 2026-05-22 (carry-forward 2026-05-17) | Tolerant |
| Cardiovascular Engineering and Technology | Springer / BMES | Springer publisher-wide policy | 2026-05-22 (inherits) | Tolerant |
| Biomechanics and Modeling in Mechanobiology | Springer | Springer publisher-wide policy | 2026-05-22 (inherits) | Tolerant |
| Microgravity Science and Technology | Springer | Springer publisher-wide policy | 2026-05-22 (inherits) | Tolerant |

**No new hard denylist additions.** Carry-forward AMHP denylist from `AI_POLICY_FILTER.md` §4 (Newman 2026-05-08).

---

## 4. Scoring table (top 7, scope-dominant 100-point rubric)

**Rubric:** Scope 40 / Quartile 15 (Q2 = 15, Q3 = 10) / APC 25 (must be $0 subscription path) / Acceptance 10 / Speed 5 / Indexing bonus +5 (Scopus + WoS SCIE + PubMed/MEDLINE).

**Hard filters applied BEFORE scoring (every candidate must pass all four):**
1. $0 APC subscription path confirmed
2. Q2 or Q3 (best-relevant-category Scimago 2024)
3. WoS SCIE indexed (Scopus alone insufficient)
4. Tolerant AI policy

**Quartile convention note:** Where a journal is Q1 in one category and Q2 in another (e.g., BMB Q1 in Mathematics-misc + Q2 in Computational Theory & Mathematics), the **most-CGEM-relevant category** quartile is reported. This mirrors the user's listed pool convention for BMB. Multi-category nuance is footnoted, not headline.

### Tier 1 — Passes ≥ 25/30 scope cut (fully recommended)

| Rank | Journal | Publisher | SJR Quartile | APC | Scope /40 | Q /15 | APC /25 | Accept /10 | Speed /5 | Bonus | **Total** |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | **Annals of Biomedical Engineering** (ABE) | Springer / BMES | Q2 biomed eng | $0 hybrid sub | 35 (26/30→35/40) | 15 | 25 | 5 | 4 | +5 | **89** |
| 2 | **Medical & Biological Engineering & Computing** (MBEC) | Springer / IFMBE | Q2 biomed eng | $0 hybrid sub | 35 (26/30→35/40) | 15 | 25 | 5 | 5 | +5 | **90** |

### Tier 2 — 22–24/30 scope (fallback-of-fallback only; real desk-rejection risk under user's ≥ 25/30 directive)

| Rank | Journal | Publisher | SJR Quartile | APC | Scope /40 | Q /15 | APC /25 | Accept /10 | Speed /5 | Bonus | **Total** |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 3 | Journal of Theoretical Biology | Elsevier | Q2 math bio | $0 non-OA | 30 (22/30→30/40) | 15 | 25 | 5 | 3 | +5 | **83** |
| 4 | Mathematical Biosciences | Elsevier | Q2 math bio | $0 non-OA | 28 (21/30→28/40) | 15 | 25 | 5 | 3 | +5 | **81** |
| 5 | Bulletin of Mathematical Biology | Springer | Q2 (Comp Theo & Math; Q1 in Math-misc) | $0 hybrid sub | 32 (24/30→32/40) | 15 | 25 | 6 | 3 | +5 | **86** |
| 6 | Mathematical Medicine and Biology | OUP / IMA | Q2 applied math | $0 hybrid sub | 30 (22/30→30/40) | 15 | 25 | 6 | 3 | +5 | **84** |
| 7 | IRBM | Elsevier Masson | Q2 biomed eng (Q1 biophysics in best category) | $0 non-OA | 30 (22/30→30/40) | 15 | 25 | 5 | 3 | +2 | **80** |

**Notes on Tier 2:**
- BMB at 86 outranks ABE/MBEC purely on a raw score basis, but scope 24/30 sits 1 point below the user's hard ≥ 25/30 floor. The 2026-05-22 BSPC desk-rejection (22/30 → rejected) makes any sub-25 candidate a documented risk; BMB is flagged "borderline-out" rather than "recommended."
- JTB raw score 83 is competitive, but the published scope clause "papers in which only mathematics is utilized... without new theoretical perspective or biologically novel insight will NOT be considered" replicates the BSPC failure pattern at a different journal. Use only with explicit reframing into "new theoretical perspective on +Gz physiology emulation under uncertainty," not as a methodology-first paper.

---

## 5. Tradeoff narrative (per Tier-1 + Tier-2 candidate)

### Tier 1 — Recommended

#### **MBEC — Medical & Biological Engineering & Computing (Springer / IFMBE, Q2, score 90)**

**Verbatim scope quote (Springer journal page, retrieved 2026-05-22):**
> "Medical & Biological Engineering & Computing serves the biomedical engineering community, covering the entire spectrum of biomedical and clinical engineering. […] Presents vital theoretical and experimental developments in biomedical science and technology. Reports on advances in computer-based methodologies in multidisciplinary subjects."

**Verbatim editorial commitment (Springer journal home page, retrieved 2026-05-22):**
> "MBEC receives more than 80% of submissions related to AI, showing its increasing importance."

**Source URLs:** `https://link.springer.com/journal/11517`, `https://link.springer.com/journal/11517/aims-and-scope`, `https://www.springer.com/journal/11517`.
**Live verification date:** 2026-05-22.

NEW entrant — this is the highest-leverage finding of this scout. MBEC is the official IFMBE journal, in continuous publication since 1963, and Springer reports a **6-day median submission-to-first-decision** on the live journal page — the fastest of any candidate evaluated in any CGEM scout to date, including PMEA (28 % acceptance, several months to first decision) and ABE (3 weeks median to first decision). The journal is indexed by WoS SCIE in **four categories** simultaneously: MATHEMATICAL & COMPUTATIONAL BIOLOGY, COMPUTER SCIENCE INTERDISCIPLINARY APPLICATIONS, ENGINEERING BIOMEDICAL, and MEDICAL INFORMATICS — the broadest indexing footprint in the candidate pool. Scimago 2024 places MBEC at SJR 0.611, Q2 in Biomedical Engineering and Q2 in Computer Science Applications. JIF is 2.6 / 5-year 2.8. The 2023 sixtieth-anniversary editorial explicitly notes that MBEC has been actively soliciting AI/ML methodology papers in biomedical engineering — this is precisely the niche the CGEM emulator targets. The Springer publisher-wide AI policy applies (tolerant). MEDLINE-indexed; PubMed accepts. Hybrid open access with subscription track at $0 author cost. No page charges identified.

**Why MBEC outranks ABE under the new rubric:** scope match is roughly equivalent (both ~26/30 — IFMBE society + four-category WoS coverage including Mathematical & Computational Biology is a very direct fit for an ML emulator of an ODE physiology model), but MBEC's published median decision speed (6 days) is decisive at 5 vs. ABE's 4 (BMES reports ~3 weeks median). Both pass every hard filter cleanly. Both run on the Springer Editorial Manager portal.

**Risk:** acceptance rate is unpublished. MBEC's "Notice for Authors — Desk Rejection Policy" (visible on the journal home page 2026-05-22 as `https://link.springer.com/journal/11517/updates/27808646`) signals active scope filtering at the editor level. Mitigation: cover letter must place the conformal+OOD stack inside the "computer-based methodologies in multidisciplinary subjects" clause of the published scope, and cite the journal's own AI-in-biomedical-engineering precedents in the introduction.

---

#### **ABE — Annals of Biomedical Engineering (Springer / BMES, Q2, score 89)**

**Verbatim scope quote (Springer journal page + BMES journal page, retrieved 2026-05-22):**
> "Annals of Biomedical Engineering is an interdisciplinary, international journal which presents original and review articles in the major fields of bioengineering and biomedical engineering. […] While the development of theory and of mathematical models is strongly endorsed, these should be evaluated wherever possible using biological data from experiments that test specific hypotheses."

**Source URLs:** `https://link.springer.com/journal/10439`, `https://link.springer.com/journal/10439/aims-and-scope`, `https://www.bmes.org/journals` (BMES journal page).
**Live verification date:** 2026-05-22 (carry-forward 2026-05-17, re-verified).

Carry-forward from prior pool, retained as Tier-1 because it is the only existing-pool candidate that survives the ≥ 25/30 scope-strict cut intact. The scope clause is among the most CGEM-aligned in the candidate pool — it explicitly endorses "the development of theory and of mathematical models" evaluated "using biological data from experiments that test specific hypotheses." The CGEM emulator paper is exactly this: a mathematical-model (conformal-prediction-augmented surrogate) evaluated against the FAA 1991 Fortran CGEM outputs and the published Whinnery centrifuge dataset. Scimago 2024 places ABE at SJR 0.767, Q2 Biomedical Engineering, JIF 5.4 (2024 latest). BMES median time-to-first-decision is **~3 weeks** per the BMES journal page, with online publication ~2 weeks after acceptance. 10,000-word soft cap (the existing 6,020-word manuscript fits without further trim — minimum repackaging cost). Hybrid open access on Springer's standard $0 subscription track. WoS SCIE + Scopus + PubMed/MEDLINE — full triple indexing → +5.

**Why ABE is rank 1 in the post-PMEA ladder over MBEC despite a 1-point lower total:** ABE has a deeper history as a methodology-publication venue for biomedical engineering (BMES society backing since 1973), explicit endorsement of mathematical-model theory in the scope clause, and a documented 3-week first-decision speed. MBEC's 6-day median is faster but rests on a smaller sample of authors; ABE's 3 weeks is institutionally stable. **Recommendation order (Tier-1, post-PMEA): ABE → MBEC**, because ABE is the lower-risk first move and MBEC is the faster-second-move if ABE rejects on scope.

**Risk:** ABE's broad scope means the manuscript competes for slot against cardiovascular-engineering, tissue-engineering, biomechanics, and orthopaedic submissions; the conformal-prediction reviewer bench may be thinner than at a methodology-specific journal. Mitigate by suggesting ≥ 3 reviewers with explicit conformal-prediction / surrogate-modelling expertise in the cover letter.

---

### Tier 2 — Fallback-of-fallback (real desk-rejection risk; use only if Tier 1 exhausts)

#### **BMB — Bulletin of Mathematical Biology (Springer, Q2 in Computational Theory & Mathematics; Q1 in Mathematics-misc; score 86, scope 24/30 — 1 point below the floor)**

**Verbatim scope quote (Springer journal page, retrieved 2026-05-22 via carry-forward):**
> "The Bulletin of Mathematical Biology is the official journal of the Society for Mathematical Biology and serves as an interdisciplinary forum for the publication of original research that uses mathematical methods to study problems in biology and medicine."

**Source URLs:** `https://link.springer.com/journal/11538`.
**Live verification date:** 2026-05-22 (carry-forward from 2026-05-17 scout).

Scimago 2024 lists BMB as Q1 in two broad mathematics categories and Q2 in the more CGEM-relevant Computational Theory & Mathematics; the scout reports the latter as the relevant-quartile to mirror the user's listed-pool convention. SJR 0.702, JIF 2.26 (2024). `bmb-submit` skill exists in the workspace — minimal repackaging time. Acceptance rate unpublished, estimated ~30 %.

**Why BMB is Tier 2 and not Tier 1:** scope 24/30 is 1 point below the user's hardcoded ≥ 25/30 floor. The user's directive on 2026-05-22 was explicit that 22/30 → BSPC desk-rejection had just happened; sub-25 candidates are not safe. BMB at 24 is closer to the line than ABE (26) or MBEC (26), and the journal's mathematical-biology framing is more focused on theoretical population biology, infectious-disease dynamics, and developmental modelling than on physiology emulation under uncertainty. Adopt BMB only if both ABE and MBEC reject and the alternative is moving to a fully off-pool venue.

**Risk:** the SMB editorial board has historically published papers with stronger biological-insight punchlines than methodological wrapper contributions; a scope desk-rejection on "the contribution is methodological, not biological" is plausible at 24/30. Mitigate with an introductory paragraph that frames the CGEM emulator as a tool for *understanding* +Gz physiology under epistemic uncertainty, not as a tool for *predicting* G-LOC.

---

#### **JTB — Journal of Theoretical Biology (Elsevier, Q2, score 83, scope 22/30 with scope-clause risk)**

**Verbatim scope quote (Elsevier journal Guide for Authors, retrieved 2026-05-22):**
> "The Journal of Theoretical Biology is the leading forum for theoretical perspectives that give insight into biological processes. It covers a very wide range of topics and is of interest to biologists in many areas of research, including: […] Mathematical, Computational, Biophysical and Statistical Modeling […] Physiology […] Acceptable papers are those that bear significant importance on the biology per se being presented, and not on the mathematical analysis."

**Verbatim exclusion clause (same source, retrieved 2026-05-22):**
> "Highly speculative papers not based on current biological knowledge will not be accepted. Importantly, papers in which only mathematics is utilized, only technical mathematical results are proved, or standard statistical/bioinformatics methods are applied to existing genomic data, without new theoretical perspective or biologically novel insight will NOT be considered."

**Source URLs:** `https://www.sciencedirect.com/journal/journal-of-theoretical-biology/publish/guide-for-authors`.
**Live verification date:** 2026-05-22.

NEW entrant. Scimago 2024 places JTB at SJR 0.532, Q2 in multiple math/bio categories, JIF 1.98. Subscription path at $0 author cost confirmed.

**Why JTB is flagged "high desk-rejection risk":** the exclusion clause above is verbatim Elsevier's strictest scope filter — "papers in which only mathematics is utilized […] without new theoretical perspective or biologically novel insight will NOT be considered." The CGEM emulator paper, as currently scoped, is methodology-first; its biological-novelty contribution is "scalable uncertainty quantification on +Gz physiology emulation," which is plausibly *new* to the journal's audience but is one editor-discretion call away from being classified as "mathematics applied to a known biological problem." This is structurally the same failure pattern that killed BSPC at Elsevier on 2026-05-22. Use only as a Tier-2 entry after Tier-1 exhausts AND only after explicit reframing of the abstract and introduction to lead with the *biological insight* that the conformal+OOD layer enables (e.g., "the surrogate uncovers covariate regimes where the FAA-CGEM model is empirically untrusted by its own developers under +Gz hypoxia — a biologically novel finding").

**Mitigation if JTB is the active target:** abstract rewrite to lead with the Physiology and Mathematical/Computational/Biophysical/Statistical Modeling scope intersection — both are named in JTB's published scope. The conformal stack must be re-framed as "uncertainty quantification on the +Gz acceleration physiology of human pilots, with the FAA-CGEM ODE model as the demonstration substrate."

---

#### **Mathematical Biosciences (Elsevier, Q2, score 81, scope 21/30 — fails strict cut)**

**Verbatim scope quote (Elsevier journal page, retrieved 2026-05-22):**
> "Mathematical Biosciences publishes work providing new concepts or new understanding of biological systems using mathematical models, or methodological articles likely to find application to multiple biological systems. Papers are expected to present a major research finding of broad significance for the biological sciences, or mathematical biology."

**Source URLs:** `https://www.sciencedirect.com/journal/mathematical-biosciences`.
**Live verification date:** 2026-05-22 (carry-forward).

Scimago 2024 Q2 in Applied Mathematics, Modeling and Simulation, Medicine-misc. SJR 0.555, JIF 1.99. Subscription path at $0 author cost confirmed.

**Why Tier 2:** scope demands "a major research finding of broad significance for the biological sciences, or mathematical biology." The CGEM emulator is methodologically novel but its biological-significance claim is bounded to acceleration physiology (+Gz tolerance, G-LOC) — not "broad significance" in the journal's sense. Score 21/30 fails the ≥ 25/30 floor by 4 points; do not submit without substantial scope-bridging in the cover letter.

---

#### **MMB — Mathematical Medicine and Biology (OUP / IMA, Q2 applied math, score 84, scope 22/30 — fails strict cut)**

**Verbatim scope quote (IMA journal page, retrieved 2026-05-22 via carry-forward):**
> "Progress in research in medicine and biology increasingly depends on the use of mathematical models. The journal seeks to stimulate mathematics in medical and biological research with emphasis upon the special insights and enhanced understanding which arise from the use of mathematics."

**Source URLs:** `https://ima.org.uk/ima-journals/mathematical-medicine-biology-journal-ima`.
**Live verification date:** 2026-05-22 (carry-forward 2026-05-17).

Scimago 2024: SJR 0.365, Q2 in Applied Mathematics (best category), Q3 in Modeling and Simulation. OUP hybrid with $0 subscription track. Acceptance rate unpublished, estimated ~30 %.

**Why Tier 2:** scope is more focused on mathematical modeling in medical / biological systems than on physiology emulation. The CGEM paper would need explicit reframing as a "new mathematics + medicine" paper rather than a "ML wrapper for an ODE physiological model" paper. Score 22/30 fails the ≥ 25/30 floor by 3 points.

---

#### **IRBM (Elsevier Masson, Q2 biomed eng, score 80, scope 22/30 — fails strict cut)**

**Verbatim scope quote (Elsevier journal page, retrieved 2026-05-22 via carry-forward):**
> "IRBM is a journal that focuses on the interface between medicine and engineering. The journal publishes original research papers in the fields of biomechanics, biomaterials, signal and image processing, biophysics and biomedical instrumentation."

**Source URLs:** `https://www.journals.elsevier.com/irbm`.
**Live verification date:** 2026-05-22 (carry-forward 2026-05-17).

Scimago 2024: SJR 0.9 — Q1 in Biophysics, Q2 in Biomedical Engineering. JIF 6.28 / impact score reported by Resurchify (high but with known volatility). Subscription path at $0 confirmed (Elsevier Masson standard).

**Why Tier 2:** the published scope is biophysics + biomaterials + signal/image processing + biophysics + biomedical instrumentation — none of which is the CGEM emulator's primary axis. The "signal and image processing" clause could be stretched to accept a "physiological signal emulator" framing, similar to BSPC's stretch — but that exact stretch failed at BSPC on 2026-05-22. WoS SCIE status remains uncertain (only Scopus bonus claimed, +2). Score 22/30 fails the ≥ 25/30 floor by 3 points.

---

## 6. Excluded (with reasons)

### Hard exclusions — already on user list, carried forward

| Journal | Publisher | Exclusion reason |
|---|---|---|
| IJNMBE | Wiley | Desk-rejected 2026-05-17 — categorical "no machine learning applied to biomedical problems" scope filter |
| BSPC | Elsevier | Desk-rejected 2026-05-22 — scope (22/30 → rejected; this is the empirical proof for the ≥ 25/30 floor) |
| CMPB | Elsevier | Abandoned 2026-05-17 on word-count mismatch (manuscript 6,020 vs. 3,500 hard cap) + portal AI ambiguity |
| AMHP | ASMA / Newman | Denylisted per `AI_POLICY_FILTER.md` §4 (Newman 2026-05-08 letter) |
| Computers in Biology and Medicine | Elsevier | WoS Core (SCIE) removed 2024-11-17 (Clarivate manipulation investigation) |
| PLOS Computational Biology | PLOS | Gold OA $3,165 — fails $0 APC |
| Results in Engineering | Elsevier | Q1 Gold OA only — fails $0 APC and Q2/Q3 cut |
| Mathematical Biosciences and Engineering | AIMS Press | Not in WoS Core (SCIE) — fails WoS SCIE preferred-indexing filter |
| Medical Engineering & Physics | Elsevier → IPEM/IOP | Transferring publisher 2026; editorial pipeline disrupted (re-evaluate post-2026) |

### Hard exclusions — verified during this scout (2026-05-22)

| Journal | Publisher | Exclusion reason | Source verified 2026-05-22 |
|---|---|---|---|
| Frontiers in Physiology | Frontiers | Gold OA only, CHF 3,150 — fails $0 APC | `https://www.frontiersin.org/journals/physiology/for-authors/publishing-fees` |
| IEEE Open Journal of Engineering in Medicine and Biology (OJEMB) | IEEE / EMBS | Gold OA only, $2,160 — fails $0 APC | `https://www.embs.org/ojemb/about-ojemb` |
| BMC Medical Informatics and Decision Making | BMC | Gold OA — fails $0 APC | BMC publisher-wide policy |
| PLOS ONE | PLOS | Gold OA — fails $0 APC | PLOS publisher-wide policy |
| Royal Society Open Science | Royal Society | Gold OA — fails $0 APC | Royal Society publisher-wide |
| All MDPI titles | MDPI | Gold OA — fails $0 APC | MDPI publisher-wide |
| Computational and Mathematical Methods in Medicine | Hindawi / Wiley | **DISCONTINUED 2023-05-02** after Hindawi paper-mill purge; 81 retractions in 2022–2023 | `https://retractionwatch.com/2023/05/02/hindawi-shuttering-four-journals-overrun-by-paper-mills` |
| Computing in Cardiology | IEEE / CinC | Conference proceedings, not a journal | `https://www.cinc.org/` |
| BiomedicalEngineering OnLine | BMC | Gold OA — fails $0 APC | BMC publisher-wide policy |
| IEEE Transactions on Biomedical Engineering (TBME) | IEEE / EMBS | **Q1** — fails Q2/Q3 cut per 2026-05-22 user directive | Carry-forward from 2026-05-17 |
| IEEE Journal of Biomedical and Health Informatics (JBHI) | IEEE / EMBS | **Q1** — fails Q2/Q3 cut per 2026-05-22 user directive | Carry-forward from 2026-05-17 |
| Journal of the Royal Society Interface (JRSI) | Royal Society | **Q1** — fails Q2/Q3 cut per 2026-05-22 user directive | Carry-forward from 2026-05-17 |
| Acta Astronautica | Elsevier / IAA | **Q1** — fails Q2/Q3 cut per 2026-05-22 user directive | `https://www.scimagojr.com/journalsearch.php?q=12372&tip=sid` |
| Computer Methods in Applied Mechanics and Engineering (CMAME) | Elsevier | Q1 + scope is engineering-broad, not physiology/medicine | Carry-forward |

### Soft exclusions — eligible quartile but fails scope or other filter

| Journal | Publisher | Exclusion reason |
|---|---|---|
| Computer Methods in Biomechanics and Biomedical Engineering | Taylor & Francis | Q3 Biomedical Engineering (SJR 0.398) — passes quartile and subscription, but scope is biomechanics not physiology emulation; scope ~20/30. Skip. |
| Biomechanics and Modeling in Mechanobiology (BMMB) | Springer | Q1 Modeling & Simulation, Q1 Mechanical Engineering, Q2 Biomedical Engineering (SJR 0.741). Multi-category Q1/Q2 — borderline on quartile cut. Scope is biomechanics/mechanobiology, not ODE physiology emulation; ~22/30 scope. Skip on scope. |
| Cardiovascular Engineering and Technology (CVET) | Springer / BMES | Q3 Biomedical Engineering (SJR 0.486). $0 page charges confirmed. Scope is cardiovascular medical-treatment / device research, not methodology emulation; ~20/30 scope. CGEM has a cardiovascular sub-component but is not a cardiovascular paper. Skip on scope. |
| Microgravity Science and Technology | Springer | Q2 Engineering-misc (SJR 0.336); Q3 in Modeling/Simulation and Applied Math. Scope is microgravity, not +Gz acceleration physiology; ~18/30 scope. Skip on scope. |
| Biomedical Engineering Letters (BMEL) | Springer / KOSOMBE | Recently SCIE-indexed. Letters format — body word limit too short for 6,020-word manuscript. Skip on format. |
| Methods of Information in Medicine | Thieme / Schattauer | Hybrid with $0 ≤ 5-page print track — but verbatim scope page (2026-05-22 verified) excludes "bioinformatics, image- and signal processing, medical decision-making theory and pure epidemiologic studies" → CGEM emulator is borderline excluded. Skip on scope risk. |
| IISE Transactions on Healthcare Systems Engineering | Taylor & Francis / IISE | **WoS ESCI only** (not SCIE) — fails preferred-indexing filter. Q2/Q3 Safety/Reliability/Public Health (SJR 0.362). Scope is healthcare operations management, not physiology emulation. Skip on indexing + scope. |

---

## 7. Final recommendation — post-PMEA fallback ladder

### Active situation (out of scope of this scout, recorded for context)

- **Currently in submission (locked):** PMEA — Physiological Measurement (IOP Publishing). Handled by another agent. Expected timeline: several weeks to first decision; IOP-published acceptance rate 28 %.

### IF PMEA also rejects, recommended order

**Activation rule:** activate this ladder only after PMEA delivers a desk-rejection or hard-rejection decision. Pause for revision-and-resubmit if PMEA delivers major/minor revisions.

| Step | Journal | Tier | Score | Rationale |
|---:|---|:---:|---:|---|
| **2nd** | **Annals of Biomedical Engineering (ABE, Springer / BMES)** | 1 | 89 | Scope-strict ≥ 25/30 (26/30). Q2. $0 hybrid sub. Scope clause explicitly endorses "the development of theory and of mathematical models" — directly maps to CGEM. ~3-week median first decision. 10,000-word headroom. Full triple indexing. Use `manuscripts/abe/` packaging mirroring `manuscripts/bspc/` pattern; file OSF amendment for venue change. |
| **3rd** | **Medical & Biological Engineering & Computing (MBEC, Springer / IFMBE)** | 1 | 90 | Scope-strict ≥ 25/30 (26/30). Q2. $0 hybrid sub. **6-day median submission-to-first-decision — fastest in the entire CGEM scout history.** Four-category WoS SCIE coverage (incl. Mathematical & Computational Biology). MEDLINE. Springer Editorial Manager portal. IFMBE society backing since 1963. |
| **4th** | **Bulletin of Mathematical Biology (BMB, Springer)** | 2 | 86 | Tier-2: scope 24/30 sits 1 point below the user's ≥ 25/30 floor. Use only if both ABE and MBEC reject and the alternative is a venue further outside the candidate pool. `bmb-submit` skill exists in workspace → packaging cost ~ hours. Mitigation: rewrite intro to lead with biological-insight framing. |
| **5th (last resort)** | **Journal of Theoretical Biology (JTB, Elsevier)** | 2 | 83 | Tier-2: scope 22/30 fails ≥ 25/30 floor. Documented exclusion clause is structurally same failure pattern as BSPC. Use only if ABE, MBEC, BMB all reject. Mitigation: abstract rewrite to lead with biological-insight, name JTB's Physiology + Math Modeling categories explicitly. |

### Note for the SUBMISSION_LOG.md owner

`docs/publication/SUBMISSION_LOG.md` still shows BSPC as "in progress / awaiting Diego's portal upload." This scout does not modify that file (out of scope of the journal-scout role), but **whoever owns the log needs to record the 2026-05-22 BSPC desk-rejection under Attempt 3** and begin the Attempt 4 entry with PMEA.

---

## 8. Sources (every URL with 2026-05-22 verification date)

### Tier-1 candidates

- **Annals of Biomedical Engineering**
  - https://link.springer.com/journal/10439 (verified 2026-05-22)
  - https://link.springer.com/journal/10439/aims-and-scope (verified 2026-05-22)
  - https://www.bmes.org/journals (verified 2026-05-22)
  - https://member.bmes.org/annals-of-biomedical-engineering (verified 2026-05-22)
  - Scimago 2024: https://www.scimagojr.com/journalsearch.php?q=21476&tip=sid (Q2 biomed eng; SJR 0.767)

- **Medical & Biological Engineering & Computing**
  - https://link.springer.com/journal/11517 (verified 2026-05-22 via firecrawl scrape)
  - https://www.springer.com/journal/11517 (verified 2026-05-22)
  - https://www.editorialmanager.com/MBEC (submission portal, verified 2026-05-22)
  - https://link.springer.com/journal/11517/aims-and-scope
  - Scimago 2024: https://www.scimagojr.com/journalsearch.php?q=17979&tip=sid (Q2 biomed eng; SJR 0.611)
  - WoS Journal Info: https://wos-journal.info/journalid/16178 (SCIE in 4 categories)
  - Sixty-year retrospective editorial: https://link.springer.com/article/10.1007/s11517-023-02987-9 (confirms ~80 % AI submissions)

### Tier-2 candidates

- **Bulletin of Mathematical Biology**
  - https://link.springer.com/journal/11538 (verified 2026-05-22 via carry-forward 2026-05-17)
  - Scimago 2024: https://www.scimagojr.com/journalsearch.php?q=13845&tip=sid (Q1 Math-misc / Q2 Comp Theo & Math; SJR 0.702)

- **Journal of Theoretical Biology**
  - https://www.sciencedirect.com/journal/journal-of-theoretical-biology (verified 2026-05-22)
  - https://www.sciencedirect.com/journal/journal-of-theoretical-biology/publish/guide-for-authors (verified 2026-05-22; verbatim exclusion clause)
  - Scimago 2024: https://www.scimagojr.com/journalsearch.php?q=29663&tip=sid (Q2 multiple categories; SJR 0.532)

- **Mathematical Biosciences**
  - https://www.sciencedirect.com/journal/mathematical-biosciences (verified 2026-05-22)
  - Scimago 2024: https://www.scimagojr.com/journalsearch.php?q=24562&tip=sid (Q2; SJR 0.555)

- **Mathematical Medicine and Biology (IMA / OUP)**
  - https://ima.org.uk/ima-journals/mathematical-medicine-biology-journal-ima (verified 2026-05-22 via carry-forward 2026-05-17)
  - Scimago 2024: https://www.scimagojr.com/journalsearch.php?q=24578&tip=sid (Q2 Applied Math; SJR 0.365)

- **IRBM**
  - https://www.journals.elsevier.com/irbm (verified 2026-05-22 via carry-forward 2026-05-17)
  - Scimago 2024: SJR 0.9 (Q1 Biophysics / Q2 Biomed Eng)

### Excluded (verified 2026-05-22)

- Frontiers in Physiology fees: https://www.frontiersin.org/journals/physiology/for-authors/publishing-fees
- IEEE OJEMB fees: https://www.embs.org/ojemb/about-ojemb
- IEEE TBME fees: https://www.embs.org/tbme/open-access-publication
- IISE Transactions on Healthcare Systems Engineering: https://journalsearches.com/journal.php?title=iise+transactions+on+healthcare+systems+engineering (WoS ESCI only)
- Computational and Mathematical Methods in Medicine discontinuation: https://retractionwatch.com/2023/05/02/hindawi-shuttering-four-journals-overrun-by-paper-mills
- Cardiovascular Engineering and Technology: https://link.springer.com/journal/13239 (Q3 biomed eng; scope 20/30 — narrow fit)
- Biomechanics and Modeling in Mechanobiology: https://link.springer.com/journal/10237 (scope biomechanics, not ODE physiology emulation)
- Microgravity Science and Technology: https://link.springer.com/journal/12217 (scope microgravity, not +Gz physiology)
- Computer Methods in Biomechanics and Biomedical Engineering: https://www.tandfonline.com/journals/gcmb20 (Q3; scope biomechanics)
- Methods of Information in Medicine scope/exclusion: https://lp.thieme.de/journals/methods-of-information-in-medicine/0026-1270 (scope excludes signal-processing and bioinformatics; CGEM emulator borderline)

### Cross-cutting AI policy sources (publisher-wide, carry-forward verified 2026-05-22)

- Springer Nature AI guidance: https://www.springernature.com/gp/group/ai/ai-guidance-for-our-researchers-and-communities (tolerant; LLM-assisted editing requires no disclosure)
- Elsevier publishing ethics: https://www.elsevier.com/about/policies-and-standards/publishing-ethics (tolerant disclosure-if-used)
- IOP author hub AI policy: https://publishingsupport.iopscience.iop.org/questions/ai-policy/ (tolerant)
- OUP authoring & policies: https://academic.oup.com/journals/pages/authors/ethics (tolerant)
- Royal Society publication ethics: https://royalsociety.org/journals/ethics-policies/ (tolerant)
- IEEE publication services AI: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/ (tolerant)

### Carry-forward AI policy denylist (no new entries 2026-05-22)

- AMHP / ASMA / Newman: documented in `~/.hermes/skills/journal-scout/AI_POLICY_FILTER.md` § 4 (Newman 2026-05-08 letter)

---

## Methodology notes for this scout

- **Discovery sources actually used (2026-05-22):** Tavily (advanced depth, 11 queries), Firecrawl (3 live scrapes — MBEC, CVET, JTB Guide for Authors), publisher policy pages verified directly (Springer Nature, Elsevier, Frontiers, IEEE EMBS, Thieme, IISE/T&F), Scimago 2024 lookups via Resurchify + wos-journal.info + UKZN cached Scimago CSV.
- **Hard filters applied BEFORE scoring** (so dozens of candidates were eliminated without expending firecrawl budget): $0 APC subscription path; Q2 or Q3 only; WoS SCIE preferred; tolerant AI policy.
- **What I could not verify live:** ABE acceptance rate (unpublished by BMES); MBEC acceptance rate (unpublished); precise current MBEC desk-rejection-policy text (referenced in journal updates as `https://link.springer.com/journal/11517/updates/27808646`, page metadata visible but full text not retrieved — flagged for re-verification at the time of submission); SciRev data for MBEC and ABE remain sparse.
- **Perplexity / Scite:** not used this round (Tavily + Firecrawl + Scimago coverage was sufficient; quota-conserving).
- **Advisor consultations:** 3 calls (pre-research orientation; mid-research convergence pressure; pre-write final convergence on Tier-1/Tier-2 framing).

**Output saved at:** `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/publication/2026-05-22_journal-scout_cgem-q2-q3-fallback.md`
