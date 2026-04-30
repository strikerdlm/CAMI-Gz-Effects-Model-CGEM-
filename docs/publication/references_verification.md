# Reference list verification — AMHP submission

> **AMHP §3 / §6 / §10**: References must be in NLM/MEDLINE style with
> abbreviated journal names per the NLM Title Abbreviation catalog.
> Each reference below is annotated with verification status and
> outstanding actions required before the portal upload step.

## Per-reference status

### [1] Lyons TJ, Harding R, Freeman J, Oakley C. *G-induced loss of consciousness accidents in the US Air Force.* Aviat Space Environ Med. 1992;63(6):500-503.

- **Status:** ⚠️ Verify
- **Action:** Confirm via PubMed (PMID search "Lyons G-LOC accidents 1992");
  AMHP's predecessor *Aviat Space Environ Med* journal abbreviation is
  correct.

### [2] Newman DG. *High G flight: physiological effects and countermeasures.* Routledge; 2015.

- **Status:** ✅ Plausible book; AMHP's current EIC is the author.
  Verify ISBN / publisher imprint (Routledge / Ashgate).
- **Action:** Add ISBN: 978-1-4094-7173-1 (verify at submission).

### [3] Green NDC. *Long duration acceleration.* In: Gradwell DP, Rainford DJ, eds. Ernsting's Aviation and Space Medicine. 5th ed. CRC Press; 2016:149-164.

- **Status:** ✅ Standard textbook chapter. Verify ISBN.

### [4] Whinnery JE, Whinnery AM. *The electroencephalographic response to +Gz stress.* Aviat Space Environ Med. 1990;61(5):435-439.

- **Status:** ⚠️ Verify
- **Action:** Confirm PMID and exact title via PubMed search.

### [5] Burns JW, Kruger MT. *Mathematical model of G-LOC onset time: validation and sensitivity analysis.* Aviat Space Environ Med. 1997;68(2):120-126.

- **Status:** ⚠️ Verify (citation looks real; titled-and-dated check
  against PubMed required).

### [6] Copeland K, Knarr J, Whinnery JE. *Mathematical model of +Gz acceleration tolerance: effect of countermeasures and pilot configuration.* Aviat Space Environ Med. 2000;71(4):370-375.

- **Status:** ⚠️ Verify
- **Action:** PubMed; FAA Library cross-reference.

### [7] Copeland K. *Civil Aerospace Medicine Institute G-Effects Model (CGEM).* FAA Office of Aerospace Medicine; 2020. Technical Report DOT/FAA/AM-20/XX.

- **Status:** ❌ **PLACEHOLDER** (`/AM-20/XX`)
- **Action:** Replace with the real technical-report number. The
  README links to DOI:10.21949/1524446 (Copeland & Whinnery 2023,
  DOT/FAA/AM-23/6). The canonical citation should likely be:
  > Copeland K, Whinnery JE. *Cerebral blood flow-based computer
  > modeling of Gz-induced effects.* FAA Office of Aerospace Medicine;
  > 2023. Technical Report DOT/FAA/AM-23/6. doi:10.21949/1524446.

### [8] Copeland K, Knarr J, Rogers D. *CGEM applications to acceleration physiology.* FAA Office of Aerospace Medicine; 2018. Technical Report DOT/FAA/AM-18/XX.

- **Status:** ❌ **PLACEHOLDER** (`/AM-18/XX`).
- **Action:** Either (a) fill in the real DOT/FAA/AM-18 number after
  searching the FAA technical-reports archive, or (b) drop this
  reference if a 2018 application paper cannot be confirmed and
  re-cite via [7]. Until verified, do not submit.

### [9] Whinnery JE, Copeland K. *CGEM-predicted G tolerance across standardized pilot profiles.* Aerosp Med Hum Perform. 2019;90(3):215-220.

- **Status:** ⚠️ Verify
- **Action:** Confirm via PubMed / AMHP archives. AMHP renamed from
  ASEM in 2015, so 2019 in AMHP is plausible.

### [10] Aresti System. *Catalogue of Aerobatic Figures.* FAI/CIVA; 2019 ed.

- **Status:** ✅ Standard reference; cite the FAI/CIVA web URL.
- **Action:** Add the canonical URL: <https://www.fai.org/civa/aresti-catalog>

### [11] Gebru T, Morgenstern J, Vecchione B, et al. *Datasheets for datasets.* arXiv:1803.09010; 2018.

- **Status:** ✅ Verified (arXiv preprint; widely cited).

### [12] Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World.* Springer; 2005.

- **Status:** ✅ Standard textbook reference. ISBN: 978-0-387-25061-8.

### [13] Boström H, Johansson U, Löfström T. *Mondrian conformal predictive distributions.* Proc COPA; 2018.

- **Status:** ⚠️ Verify exact venue and DOI.
- **Action:** Boström et al.'s Mondrian conformal regression work
  appeared in the *Proceedings of Machine Learning Research* (PMLR)
  COPA volumes; pin the volume and page number. Cite v91 (2018) or
  similar.

### [14] Lundberg SM, Lee SI. *A unified approach to interpreting model predictions.* NeurIPS; 2017.

- **Status:** ✅ Verified (NeurIPS 2017; 30:4765-4774).

### [15] Kissas G, Yang Y, Hwuang E, et al. *Machine learning in cardiovascular flows modeling: Predicting arterial blood pressure from non-invasive 4D flow MRI data using physics-informed neural networks.* Comput Methods Appl Mech Eng. 2020;358:112623.

- **Status:** ⚠️ Verify (likely real; check exact title).

### [16] Melis ME, Bursi C, Colombo G. *Surrogate-based uncertainty quantification for aerospace compartment models.* Aerosp Sci Technol. 2021;110:106478.

- **Status:** ⚠️ **Likely fabricated.** AI-generated reference style
  matches the others but the exact citation cannot be confirmed
  without an external search. Either (a) confirm via DOI search and
  keep, or (b) replace with a real surrogate-modeling citation in the
  aerospace-physiology adjacent literature, or (c) drop and rephrase
  the surrounding sentence to require fewer citations.

### [17] Romano Y, Patterson E, Candès EJ. *Conformalized quantile regression.* NeurIPS; 2019.

- **Status:** ✅ Verified (NeurIPS 2019; arXiv:1905.03222).

### [18] Convertino VA. *Blood volume: its adaptation to endurance training and implications for orthostatic tolerance.* Med Sci Sports Exerc. 1991;23(7):815-822.

- **Status:** ⚠️ Verify (Convertino is a real and prolific author in
  this domain; specific 1991 paper requires PubMed lookup).

---

## Action items before portal upload

| # | Action | Severity |
|---|---|---|
| 1 | Replace ref [7] with the real Copeland & Whinnery 2023 (DOT/FAA/AM-23/6, doi:10.21949/1524446) | 🔴 Blocker |
| 2 | Verify ref [8] technical-report number, or drop the citation and rephrase Methods §2.1 / §4.3 | 🔴 Blocker |
| 3 | Verify ref [16] (Melis 2021); replace with a confirmed surrogate-aerospace citation if cannot be found | 🟠 High |
| 4 | Verify refs [1], [4], [5], [6], [9], [13], [15], [18] via PubMed / DOI lookup; add DOIs where available | 🟡 Standard |
| 5 | Confirm AMHP's preferred journal-name abbreviations (NLM catalog) for all journal references | 🟡 Standard |
| 6 | Convert in-text citations from `[N]` bracketed format to superscript Arabic in the final Word/PDF render | 🟡 Standard |
| 7 | Add ISBNs to refs [2], [3], [12] (book references) | 🟡 Standard |

## Verification workflow

1. For each ⚠️ reference, query PubMed with `(author) AND (year) AND
   (key title word)`.
2. If PMID is found, paste the official NLM citation into the manuscript.
3. If PMID is NOT found, escalate: search the journal's archive
   directly, search Crossref by DOI, or replace the reference with a
   confirmed alternative.
4. For the two FAA technical reports (refs [7], [8]), the FAA's
   public-access library at <https://www.faa.gov/data_research/research/med_humanfacs/>
   should be the source of truth.
5. The Boström et al. 2018 Mondrian conformal reference (ref [13])
   is best cited via the PMLR / COPA proceedings page directly.

## Final deliverable for submission

A clean reference list in NLM format, with no `XX` or other
placeholders, is required for portal upload. The AMHP submission is
**blocked** on actions 1 and 2 above.
