# Reviewer Report — Aerospace Physiology / G-LOC
**Reviewer:** Anonymous Reviewer 3 (aerospace physiology / +Gz tolerance / G-LOC; centrifuge research; FAA / USAF / EASA aeromedical certification).
**Date:** 2026-05-22
**Manuscript:** "An additive ML wrapper for validated ODE physiological models: conformal prediction, out-of-distribution detection, and global sensitivity, applied to the FAA CAMI G-Effects Model."
**Journal:** *Physiological Measurement* (IOP Publishing).
**Recommendation:** **Major Revisions.**

---

## Summary of the manuscript

The author wraps the FAA Civil Aerospace Medical Institute's CGEM Fortran model of +Gz cerebrovascular physiology in an additive machine-learning layer that delivers (i) a fast XGBoost surrogate emulator (~50 µs/row vs ~9 ms direct CGEM); (ii) Mondrian split-conformal prediction intervals stratified by maneuver category, with a heteroscedastic Conformalized Quantile Regression (CQR) layer for the long-tailed `time_to_gloc_s` target; (iii) a robust-Mahalanobis out-of-distribution detector with distribution-free conformal abstention; and (iv) Sobol / Morris global sensitivity rankings. The validated Fortran core is preserved byte-for-byte. The framework is exercised on 3,240 synthetic CGEM runs (72 maneuvers from Aresti CIVA 2019 / IAC Known–Unknown / USAFSAM profiles, 45 pilot configurations per maneuver, master seed 42). The protocol was OSF-pre-registered before test-set evaluation, with amendments dated 2026-05-06 adding the CQR layer (H5) and an archival external validation against Whinnery & Forster (2013) Phase A data (H6). On the H6 cohort (n = 8 onset-rate × time-to-LOC records, parent n = 729 relaxed-subject centrifuge participants), the calibrated surrogate is in-bracket on every record at onset ≥ 1 G/s and under-predicts by δ̄ = +26.6 s [95 % CI +6.3, +52.1] at onset ≤ 0.5 G/s, recovering — quantitatively — the documented CGEM-vs-reality discrepancy attributable to non-AGSM muscle tension in relaxed participants at low onset rates.

The methodological contribution is real and the scope is honest about its limits. However, the manuscript contains **material factual errors in its dataset-descriptive numbers** (§3.1) that contradict the manuscript's own §3.5 table, three **manuscript-versus-code inconsistencies in the input-grid description** (§2.2), and one **terminological imprecision** about how G-LOC is detected (§2.1). The civil-aviation-certification claim (§2.1) is over-stated as written. None of these are fatal to the methodological framing, but they collectively put the manuscript below the accuracy floor *Physiological Measurement* expects for a domain-applied paper, and they will be quickly flagged by any reader with operational +Gz background. **Major revisions are required before this manuscript can be published.**

---

## Major concerns

### 1. §3.1 — Dataset descriptive numbers do not match the data product.

The manuscript reports: "category sizes of 720 (championship, 22.2 %), 720 (conceptual, 22.2 %), 720 (extreme post-stall, 22.2 %), and 1,080 (military ACM, 33.3 %); event rates were 64.8 % (greyout), 58.3 % (blackout), and 50.6 % (G-LOC)."

The actual committed dataset (`data/datasets/cgem_synthetic_v1.parquet`, 3,240 rows) reports:

| Category | Manuscript §3.1 | Actual dataset |
|---|---:|---:|
| Championship | 720 (22.2 %) | 1,575 (48.6 %) |
| Conceptual | 720 (22.2 %) | 135 (4.2 %) |
| Extreme post-stall | 720 (22.2 %) | 540 (16.7 %) |
| Military ACM | 1,080 (33.3 %) | 990 (30.6 %) |

| Event | Manuscript §3.1 | Actual dataset |
|---|---:|---:|
| Greyout | 64.8 % | 18.8 % |
| Blackout | 58.3 % | 11.4 % |
| G-LOC | 6.3 % | 6.3 %* |
| *(footnote)* | (manuscript says "50.6 %") | |

\*G-LOC actually 6.3 % overall; the manuscript's 50.6 % cannot be reproduced from the dataset.

These descriptives **contradict the manuscript's own §3.5 LOGO table** (Table 4) which reports training/test row counts of `championship 1,665 / 1,575`, `conceptual 3,105 / 135`, `extreme post-stall 2,700 / 540`, `military ACM 2,250 / 990` — these match the actual dataset, not the §3.1 figures. The §3.1 numbers also imply event-positive row counts in the test split (~315 G-LOC events) that are an order of magnitude larger than the n = 36 cited in Table 2's footnote for the conformal G-LOC coverage cell. The internal inconsistency is unambiguous.

This is the single most important fix in the paper. Recommend: replace §3.1 entirely with the actual `value_counts()` of `maneuver_category` and the per-target `event_<x>` means from the committed Parquet file, audited line-by-line against the dataset hash in `cgem_synthetic_v1.meta.json`. The current category and event-rate paragraph appears to have been carried in from an earlier version of the data product (BSPC pre-pivot?) and was not refreshed for the PMEA submission. A descriptive-statistics audit script that runs as part of the manuscript-render pipeline would prevent recurrence.

### 2. §2.2 — Pilot-configuration tier definitions do not match the code.

The manuscript says: "three countermeasure tiers — baseline (no G-suit, no AGSM, no PBG), moderate (G-suit 5 psi, AGSM 0.5, no PBG), maximum (G-suit 10 psi, AGSM 1.0, PBG 30 mmHg)" and "dehydration level ∈ {0.0, 0.04, 0.08} (fractional plasma volume loss)."

The actual `cgem_ext.data.generate_dataset.COUNTERMEASURES_LEVELS` dictionary is:

| Tier | gsuit_max_psi | agsm_effectiveness | pbg_max_mmhg | gsuit_coverage_fraction |
|---|---:|---:|---:|---:|
| `none` | 0.0 | 0.0 | 0.0 | 0.0 |
| `agsm` | 0.0 | 0.6 | 0.0 | 0.0 |
| `suit_agsm` | 10.0 | 0.8 | 15.0 | 0.7 |

And `DEHYDRATION_LEVELS = {none: 0.0, mild: 0.3, severe: 0.7}`, with `cgem_wrapper.py` line 224 implementing the level as a dimensionless 0–1 scaling that subtracts 10 × dehydr mmHg from BSP/MSP and 5 × dehydr from BDP/MDP, and reduces normal/max flows by 10 % at dehydr = 1. The wrapper docstring explicitly says "Dehydration level as fraction 0.0 (none) .. 1.0 (severe)" — not fractional plasma volume loss.

These two discrepancies matter to an aerospace reader because:

- **PBG.** The manuscript's claim of "PBG 30 mmHg" as the maximum tier is half the CGEM-documented maximum useful pressure (60 mmHg, per OAM202305 §"pbg" and OAM202306 ¶ on PBG limits), and the actual training-set value is **15 mmHg** — a quarter of the documented maximum. Modern operational PBG (e.g., COMBAT EDGE on the F-15/F-16, BRAG / Libelle, EASA-certified pressure-breathing rigs) typically operates at 50–60 mmHg ITP during peak +Gz exposure. The training set therefore does not exercise the operationally relevant high-PBG regime, and the §3.6 Sobol finding that PBG has near-zero ST may reflect this restricted range rather than physiological irrelevance.
- **Dehydration.** Re-labelling a dimensionless 0–1 scaling as "fractional plasma volume loss" implies a quantitative interpretation (4 % and 8 % PV loss are clinically meaningful targets — 4 % is mild dehydration; 8 % is moderate-to-severe and operationally degrading) that the underlying empirical model in `cgem_wrapper.py` does not support. The dehydration knob is a phenomenological scaling factor, not a plasma-volume parameter.
- **AGSM tiers.** The manuscript lists discrete AGSM-effectiveness values of 0.5 (moderate) and 1.0 (maximum); the code grid uses 0.6 and 0.8. The 1.0 maximum tier does not appear in the training data. Sobol/Morris results derive from the training distribution, not from the manuscript's described grid.

Recommend: replace the §2.2 tier paragraph with the code's actual tier dictionaries verbatim, and reframe `dehydration_level` as "a dimensionless empirical scaling of resting and maximum arterial pressures and normal/maximum cerebral blood flow, as implemented in CGEM, with our grid spanning {0.0, 0.3, 0.7}." If the author wishes to retain a plasma-volume interpretation, the supplementary should show how the 0–1 knob maps onto a plasma-volume mechanism (Sawka, 2000-vintage hydration physiology) — but as currently described, the labelling is misleading.

### 3. §2.1 — G-LOC event detection is described incorrectly.

The manuscript states: "Event-time scalars — greyout, blackout, and G-LOC — are the earliest samples at which **visual function** crosses predefined thresholds (right-censored if never crossed)."

This is not how CGEM defines G-LOC in the published `cgem_wrapper.py` parsing logic (lines 464–474):

- `t_grey` ← first transition of `ne2` flag (vision)
- `t_black` ← first transition of `non2` flag (blackout, from `bo_bank` reserve)
- `t_gloc` ← first transition of `n2` flag (consciousness state, driven primarily by the consciousness-reserve depletion mechanism in the Fortran core)

Visual function (`f_vis` = `FON`, retinal flow at central retina) is involved in greyout/blackout via retinal ischaemia thresholding, but **G-LOC is a consciousness-state event** (`n2`), not a visual-function event. The author should:

- Clearly state that CGEM's internal `n2` flag is a **proxy** for the clinical / operator-observed G-LOC endpoint (typically scored from impaired motor response, post-LOC nystagmus, or EEG/EOG in instrumented centrifuge protocols — e.g., Whinnery 1990, Lyons et al. 1992, Forster & Whinnery 2014).
- Note that this proxy was validated by Copeland & Whinnery (2023, DOT/FAA/AM-23/6) against pooled centrifuge data and is the same proxy used in every CGEM-derived publication. The proxy is not a manuscript-specific weakness, but it should be explicitly named.
- Distinguish A-LOC (almost-LOC / cognitive incapacitation without full unconsciousness) from full G-LOC. CGEM does not model A-LOC; the surrogate inherits this gap. A one-sentence acknowledgement protects against reviewer / clinician confusion.

### 4. §2.1 — "CGEM underpins G-tolerance standards in civil-aviation certification" is over-stated.

The current text reads (line 29): "CGEM now underpins G-tolerance standards in civil-aviation certification — so preserving it byte-for-byte is both a scientific and a regulatory requirement."

This is a strong regulatory claim. To my knowledge there is no FAR (14 CFR), Advisory Circular, EASA CS, ICAO Annex, or Aerospace Medical Examiner (AME) guidance document that adopts CGEM as a regulatory standard. CGEM is published as an FAA Office of Aerospace Medicine technical report (DOT/FAA/AM-23/5 user guide, AM-23/6 how-it-works), which is FAA-internal research documentation, not regulatory rulemaking. Civil-aviation G-tolerance certification (e.g., FAR Part 23 / Part 25 aircraft maneuver-load envelopes, FAA Class I medical certification, Aerocivil / EASA AME standards) does not, to my knowledge, cite CGEM. The closest regulatory touchpoint is the FAA Aircrew Standards documents (e.g., FAA-H-8083-3B for the General Aviation Pilot's Manual section on +Gz physiology), which cites the CAMI G-tolerance literature in narrative form but does not adopt CGEM as a computational standard.

Recommend: soften to language such as "CGEM is the FAA Civil Aerospace Medical Institute's reference computational model of +Gz physiology, published as an open-source technical artefact in support of FAA aeromedical research and used internally by the CAMI Aeromedical Research Division." If the author has a specific citation supporting the regulatory claim (FAR, AC, EASA CS, FOM, or analogous), please add it; otherwise the byte-for-byte preservation argument should rest on **scientific** reproducibility (which is sufficient), not on regulatory adoption.

### 5. §2.2 — "Extreme post-stall" maneuvers (cobras, hammerheads, kulbits) are operationally orthogonal to sustained-G-LOC physiology.

The maneuver catalogue (`maneuvers_catalog.py`) contains 12 extreme-post-stall identifiers (Pugachev cobra, kulbit, inverted cobra, tailslide / tailslide tumble / Bell tailslide, hammerhead, etc.). These manoeuvres are characterised by very high angle-of-attack, rapid pitch excursions, and momentary excursions through ±Gz at low airspeed; they do not produce **sustained** +Gz exposure of the kind that drives G-LOC physiology in CGEM. From an operational standpoint:

- Cobras, kulbits, and tailslides typically peak at < +2 to +3 Gz during pitch excursion (sometimes briefly negative Gz / negative Gx). The dominant physiological challenge is vestibular and proprioceptive (spatial disorientation, somatogyral / Coriolis illusions), not cerebrovascular.
- The manuscript's own Sobol decomposition (§3.6) shows `g_peak_abs` and `profile_duration_s` are the dominant +Gz risk drivers. Extreme post-stall maneuvers populate the low-G end of both axes.
- Their inclusion in the +Gz training distribution is therefore methodologically defensible only as out-of-distribution / boundary-condition probes — and that is *almost* what they are used for, given the §3.5 LOGO AUROC = 0.600 for the extreme-post-stall held-out fold. The author should make this explicit.

Recommend: add one paragraph to §2.2 explaining that the post-stall category is included to exercise the surrogate's behaviour at low / non-sustained +Gz exposures (i.e., as in-envelope but low-event-rate rows), not as a primary G-tolerance evaluation regime. Alternatively, the post-stall category can be moved to a supplementary OOD probe. The current framing — implying that post-stall maneuvers are part of the G-tolerance training distribution on equal footing with sustained military ACM turns — is operationally inaccurate.

### 6. §2.4 — AGSM as a continuous fraction in [0, 1] is CGEM's abstraction, not an operational reality.

CGEM models AGSM effectiveness as a continuous scalar (`agsm` line 22 of `gloc_inp.dat`), and the surrogate inherits this. Operationally, AGSM is closer to a binary-with-cadence behaviour: a pilot is either straining (with measurable inspiratory-expiratory cadence, muscle-group recruitment of legs / glutes / abdomen, and learned timing relative to the G ramp) or not. AGSM effectiveness varies by training (Whinnery 1990; Newman 2015; Green 2016 in *Ernsting's*) and degrades with fatigue (Eiken et al. 2007; Newman et al. 2014). The 0–1 dial is a useful population-level parametrisation but does not model the time-dynamics of an operational AGSM cycle.

This is **not** a manuscript-specific weakness — it is a CGEM abstraction the surrogate cannot remove. But the discussion (§4.2 or §4.4) should acknowledge that the AGSM input is a population-summary effectiveness, not a within-maneuver dynamic. Otherwise an operational reader (flight surgeon, AGSM instructor, centrifuge operator) will read "AGSM = 1.0" as "perfect AGSM" rather than "ceiling of population-mean AGSM benefit captured by the CGEM mechanism."

### 7. §3.7 — The H6 finding largely recovers a documented CGEM limitation, which trims the "discovery" framing.

The Copeland & Whinnery 2023 technical report (DOT/FAA/AM-23/6, the very reference cited by the author as the CGEM authority) states explicitly in its Discussion (¶ following Table I, my paraphrase from `docs/OAM202306(How_it_Works).md`):

> "CGEM predicts G-LOC in 54 s for an initially relaxed average-resistance male participant exposed to the gradual onset rate of 0.080 G/s. If, after passing 1.4 Gz, initially relaxed participants are allowed to increase the non-AGSM related muscle strain effect to a realistic physical maximum of 60 mmHg in 30 s, calculated time to G-LOC increases to 80 s, a gain of **26 s**."

The manuscript's headline H6 number — δ̄ = +26.6 s [95 % CI +6.3, +52.1] at slow onset — is numerically the same magnitude as the CGEM authors' own documented gradient-onset gain, and the explanation (non-AGSM muscle tension at slow onset) is identical. This is a strength in one sense (the surrogate faithfully reproduces a known CGEM limitation, validating the wrapper architecture) but it weakens the manuscript's implicit framing of H6 as a discovery of a CGEM-vs-reality discrepancy. The discrepancy is documented in Copeland & Whinnery 2023 §4 and traces to Quarry & Spodick 1974 and Burton 1988.

Recommend: in §3.7 and §4.3, explicitly acknowledge that the H6 finding recovers the documented CGEM limitation; reframe as "the conformal H6 test confirms, in calibrated-bracket terms, the CGEM gradient-onset under-prediction documented in Copeland & Whinnery 2023 §4." This is more honest and actually strengthens the methodological argument — the wrapper provides a *principled, quantified, bracket-honest* re-statement of a known limitation, rather than burying it.

### 8. Citations — significant aerospace-physiology omissions.

The 24-reference list is adequate for the methodological side (conformal prediction, XGBoost, SHAP, Sobol/Morris, datasheets, TRIPOD-AI) but is thin on aerospace-G-LOC primary literature. Omissions a domain reviewer will notice:

- **Burton RR.** *G-induced loss of consciousness: definition, history, current status.* Aviat Space Environ Med 1988; 59(1):2–5. The foundational definition paper and the source of the 15 mmHg muscle-tension reference used in CGEM. This citation is load-bearing for §3.7 / §4.3.
- **Self DA, Mandella JG, Prinzo OV, Forster EM, Shaffstall RM.** *Physiological equivalence of normobaric and hypobaric exposures of humans to 25,000 feet (7,620 m).* Aviat Space Environ Med 2011; 82(7):691–697. Not directly relevant, but the **Self et al. USAFSAM dynamic-G centrifuge data** (Self & Mandella et al. 2000–2010 series) is the modern US AGSM-benchmark reference.
- **Lalande S, Lyons TJ.** *Subjective acceleration perception during +Gz ramps.* Aviat Space Environ Med 2010; 81(12):1126–1131. The reference modern-era paper on dynamic G-onset perception, directly relevant to the manuscript's slow-onset / rapid-onset operational distinction.
- **Forster EM, Whinnery JE.** *Recovery from Gz-induced loss of consciousness.* Aviat Space Environ Med 1988; 59(6):517–522 — and the 2014 companion *Extreme Physiology and Medicine* recovery-of-consciousness curve paper (Whinnery, Forster, Rogers 2014; doi 10.1186/2046-7648-3-9) which is paired with the cited 2013 LOC curve and used in the H6 OSF amendment but not in the manuscript reference list.
- **Stoll AM.** *Human tolerance to positive G as determined by the physiological end points.* J Aviat Med 1956; 27(4):356–367. The historical reference for human +Gz tolerance limits and the foundation of the CAMI G-tolerance lineage that CGEM extends; citing it strengthens the byte-for-byte preservation argument.
- **Newman DG, Callister R.** *Cardiovascular training effects in fighter pilots induced by occupational high G exposure.* Aviat Space Environ Med 2008; 79(8):774–778 — the modern reference on individual G-tolerance variation that the custom-arm `g_tolerance_multiplier ∈ {0.85, 1.00, 1.15}` is parametrising.
- **Eiken O, Kölegård R, Bergsten E, Grönkvist M.** *G-protection mechanisms afforded by the anti-G system in the JAS 39 Gripen.* Aviat Space Environ Med 2007; 78(2):126–132. The PBG-effectiveness benchmark and the source of the "60 mmHg with 1:1 HLAP conversion" figure quoted in CGEM documentation.

These are not all required, but at least Burton 1988, Lalande & Lyons 2010, Newman & Callister 2008, and the Whinnery–Forster–Rogers 2014 recovery paper should be added. The current reference list reads like a methodology paper that lightly visits aerospace, rather than a methodology paper applied to aerospace.

---

## Minor concerns

- **Abstract.** "n = 36 event-positive" for `time_to_gloc_s` — fine for the abstract but the reader does not learn until §3.3 that all 36 are in the military ACM stratum, so the per-stratum claim is effectively a one-stratum claim. Add one half-sentence to the abstract or §3.3 lead-in.
- **Table 2.** The 0/0 cells for the championship / conceptual / extreme-post-stall strata under the regressor rows are correct given the §3.1 (actual) event rates, but a reader who took §3.1's 50.6 % G-LOC rate at face value will be confused. Fixing §3.1 (Major concern 1) fixes this.
- **Table 1.** R² = 1.000 with CI [1.000, 1.000] for `hlap_min` is a red flag at first glance; the author correctly identifies this as a deterministic mapping driven by `dehydration_level`. Add a parenthetical "(deterministic mapping; see §3.6 Sobol decomposition)" to the table caption.
- **§3.5.** AUROC = 0.387 (conceptual fold, Mahalanobis) is reported with appropriate language; this is "well-supported" not "OOD." Good. But a reader who is not familiar with conformal abstention may misread this as "the detector cannot find conceptual maneuvers." Add half-sentence reminder that the in-envelope coverage (0.953) is the primary OOD claim.
- **Figure 1 / 2 / 3 etc.** Figures are linked as PDFs from `_archive/bspc/rendered/` — for PMEA submission these will need to be re-issued under a PMEA-render branch. The supplementary captions file still refers to "BSPC submission" (Supplementary_Captions.md line 3); this is a pre-submission hygiene item.
- **§2.5.** The OOD feature space description correctly notes a 17-feature vector (9 numeric, 7 binary, 1 ordinal), but does not mention that the binary FAA-profile indicators are collinear with `cm_ordinal` × `g_tolerance_multiplier` for the standard arm (where the latter is held at canonical values). This is OK but should be acknowledged in the discussion of Mahalanobis-misspecification.
- **§3.6.** Sobol ST = 1.005 for `dehydration_level` on `hlap_min` — the author correctly flags this as finite-sample overshoot from the *N* = 1,024 Saltelli base sample. A *N* = 2,048 or *N* = 4,096 sensitivity check in supplementary would put this concern to rest with negligible compute cost (the surrogate runs at 50 µs/row).
- **§4.4.** The "lower bound" framing of the surrogate bracket at slow onset is operationally sensible, but the directionality may confuse: the bracket should be treated as a **lower bound on time-to-LOC** (i.e., real LOC times will be ≥ the bracket's upper limit), not a lower bound on the bracket itself. Reword.
- **References.** Aresti System 2019 catalogue URL — verify the FAI / CIVA link is still live; the catalogue is sometimes mirrored at different paths over time. Provide accessed-date.

---

## Specific line/section comments

- **Line 27 ¶2.** "Centrifuge training and anti-G countermeasures … have driven G-LOC incidence down substantially since the 1980s" — accurate but the citation (Lyons et al. 1992) is from 1992 and reports the *peak* of US Air Force G-LOC mishap data; the modern reference should add at least one post-2000 incidence figure (e.g., AFSAS / USAFSAM / Aerospace Medical Association incidence updates). Newman 2015 covers this.
- **Line 29.** Civil-aviation-certification claim (see Major concern 4).
- **Line 43.** "subject type (FAA `who_profile` 1–6)" — for the aerospace reader, please add a one-sentence summary of what each `who_profile` parametrises (low / average / high resistance × male / female; the CGEM User's Guide DOT/FAA/AM-23/5 §"Profile 1–6" tabulates this). The reader cannot interpret §3.7's `who_profile = 4` assignment without it.
- **Line 45–46.** "Event-time scalars … are the earliest samples at which visual function crosses predefined thresholds" — see Major concern 3.
- **Line 55.** "G-suit 5 psi" — does not exist in the code tier dictionary (see Major concern 2).
- **Line 57.** "fractional plasma volume loss" — see Major concern 2.
- **Line 113.** "20,480 × 9 ms ≈ 3 min" — arithmetic 20,480 × 0.009 s = 184 s ≈ 3 min; correct.
- **Line 123.** "category sizes of 720 … 720 … 720 … 1,080" — incorrect (see Major concern 1).
- **Line 123–124.** "event rates were 64.8 % (greyout), 58.3 % (blackout), and 50.6 % (G-LOC)" — incorrect (see Major concern 1).
- **Line 232.** "`who_profile = 4`, baseline countermeasures" — the OSF amendment defaults military pilots to `who_profile = 4` (high-resistance male). The reader does not know what `who_profile = 4` is unless §2.1 adds the table (see line-43 comment).
- **Line 247.** "discrepancy is statistically distinguishable from zero" — bootstrap CI lower bound +6.3 s is correctly cited; this language is fine.
- **Line 249.** "Copeland and Whinnery (2023) note explicitly that 'the underestimation of the time to loss of consciousness when compared with the data at very low onset rates suggests a completely relaxed participant may not be an accurate assumption'" — correctly quoted from OAM202306 ¶ on page 17 of the technical report. The full sentence in C&W2023 continues with the gain of "26 s" — adding that figure here would tighten the connection between the H6 finding and the documented limitation (see Major concern 7).
- **Lines 281–282.** "the regressor stage's R² of 0.82 is upper-bounded by how faithfully CGEM itself models the G-LOC time distribution at the long tail" — correct, but the bound is mechanistic, not statistical; clarify language ("the achievable R² is bounded above by the CGEM-vs-reality discrepancy").

---

## Strengths to preserve

The manuscript has substantive strengths that should not be lost in revision:

1. **Bootstrap CI lower bound reported honestly.** Table 1 reports a 95 % CI lower bound of **−0.055** for the `time_to_gloc_s` regressor R² — i.e., we cannot reject the null on the event-positive slice. Reporting this in the headline table, rather than burying it in supplementary, is exactly the kind of transparent statistics PMEA expects. This should be kept.
2. **OSF pre-registration with date-stamped amendments.** The 2026-05-06 amendment adding H5 (CQR) and H6 (archival validation) is timestamped before any test-set evaluation under the new hypotheses. The pre-registration discipline is exemplary for a single-author methodology paper.
3. **Reproducibility triad.** Open code (MIT), open dataset (Zenodo, with binary SHA-256 hash in metadata), Docker image, OSF pre-registration. This is the standard *Physiological Measurement* should expect, and rarely receives.
4. **Operational-scope restriction.** The author restricts the framework's validity to onset ≥ 1 G/s (fighter / aerobatic regime) and **explicitly excludes** onset ≤ 0.5 G/s (gradual-onset agricultural / large-aircraft regime). This is honest and operationally aligned with the H6 finding. Keep.
5. **Distinction between CQR-vs-CGEM and CGEM-vs-reality.** The §3.7 framing — the conformal layer is correctly calibrated against CGEM, the failure is a CGEM-vs-reality discrepancy not a CQR-vs-CGEM discrepancy — is precisely the conceptual distinction needed for an additive ML wrapper to be useful. This is the methodological argument of the paper and is well executed.
6. **Mondrian per-category stratification with under-coverage declared transparently.** The choice not to pool across `maneuver_category` strata is the right one for a paper that wants to support operational sub-population claims, and the under-coverage at low-event-rate strata is reported rather than masked.
7. **§4.6 paper-2 / paper-3 deferral.** Conformalized survival analysis as the principled successor to the two-stage classifier-then-regressor pattern is the right path forward (Candès et al. 2023; Gui et al. 2024; Davidov et al. 2025) and the deferral to paper 2 is technically appropriate.

---

## Recommendation rationale

This is a sound methodological paper with a credible aerospace demonstration substrate. The wrapper architecture (surrogate + Mondrian conformal + CQR + Mahalanobis-with-conformal-abstention + Sobol/Morris) is well constructed, the implementation is open and reproducible, the OSF pre-registration discipline is exemplary, and the H6 external-validation arm is set up to reveal CGEM-vs-reality discrepancies in a principled bracket-honest way. The PMEA scope fit (physiological modelling, model identification, physics-and-model-based ML) is direct.

However, the manuscript currently contains:

- Material factual errors in §3.1 dataset descriptives that contradict its own §3.5 table (must fix).
- Three manuscript-versus-code inconsistencies in §2.2 (countermeasure tiers, dehydration semantics, AGSM ceiling) that an operational reader will quickly identify (must fix).
- One terminology error in §2.1 (G-LOC event = `n2` consciousness flag, not `f_vis` visual function threshold) that is small but consequential for operational interpretation (must fix).
- An over-stated regulatory-adoption claim in §2.1 (must soften or substantiate).
- A "discovery" framing of H6 that does not credit the documented Copeland & Whinnery 2023 §4 gradient-onset limitation (should temper).
- An aerospace-physiology citation gap (Burton 1988, Lalande & Lyons 2010, Newman & Callister 2008, Whinnery–Forster–Rogers 2014 recovery curve, Eiken et al. 2007 PBG benchmark) that an aerospace reviewer will notice (should fix).

None of these are fatal. All are correctable in a single revision pass that consists of: (i) refreshing §3.1 directly from the committed Parquet file; (ii) replacing §2.2 with the verbatim code tier dictionaries and dropping the "plasma volume" labelling; (iii) clarifying §2.1 G-LOC detection and softening the certification claim; (iv) adding a one-paragraph H6 contextualisation in §3.7 / §4.3 citing C&W2023 §4; (v) adding the five-to-six aerospace references; (vi) re-issuing the figures and supplementary captions for PMEA.

**Recommendation: Major Revisions.** Re-review by the same reviewer recommended.

---

## Suggested response-letter preparation for the authors

When the authors prepare the revised manuscript, the response letter should address each Major concern explicitly with the structure: (i) verbatim concern quoted; (ii) revised manuscript text with line numbers; (iii) supporting evidence (committed Parquet hash for §3.1, code references for §2.2, OAM202306 quote for §3.7, FAR / AC citation or soften-statement for §2.1 regulatory claim).

For the §3.1 descriptives, I would strongly recommend the authors commit a small audit script (e.g., `scripts/audit_section_3_1.py`) that reads `cgem_synthetic_v1.parquet`, computes the four category sizes and three event rates, and prints them in the manuscript's table format. The script's output should be quoted verbatim in the revised §3.1, and a hash of the Parquet file should be cross-referenced in the response letter so the reviewer can confirm independently. This same audit script should run as part of the manuscript-render pipeline going forward; the descriptive-statistics drift between §3.1 and §3.5 in the current submission suggests the manuscript and the data product were last synchronised at an earlier version.

For the §2.2 tier descriptions, the cleanest fix is to inline the code dictionaries (or screenshot the relevant lines of `cgem_ext.data.generate_dataset.COUNTERMEASURES_LEVELS` and `DEHYDRATION_LEVELS`) directly into the manuscript, and to drop the manuscript's editorial gloss ("G-suit 5 psi, AGSM 0.5"). The text should describe what the dataset *is*, not what the authors *intended*.

For the §2.1 G-LOC detection clarification, a single sentence in the §2.1 paragraph beginning "CGEM integrates a system of ODEs over the maneuver window …" is sufficient: "G-LOC events are detected from CGEM's internal `n2` consciousness-state flag (transition 0 → 1), which is the model's proxy for the clinical / operator-observed G-LOC endpoint scored by impaired motor response in centrifuge protocols (Whinnery 1990; Forster & Whinnery 1988). CGEM does not model A-LOC."

For the regulatory claim in §2.1, the safest revision is to delete the "underpins G-tolerance standards in civil-aviation certification" clause entirely and replace with "CGEM is the FAA Civil Aerospace Medical Institute's reference research model of +Gz physiology, published as an open-source technical artefact (DOT/FAA/AM-23/5, AM-23/6) in support of CAMI aeromedical research." This is defensible without citation, removes the regulatory overreach, and still motivates the byte-for-byte preservation.

For the H6 framing, one paragraph at the end of §3.7 ("Relation to documented CGEM limitations") quoting the Copeland & Whinnery 2023 §4 passage on the 26-second gradient-onset gain, and noting that the H6 finding is a calibrated-bracket re-statement of that documented limitation, will both temper the discovery claim and **strengthen** the methodological argument (because it shows the wrapper recovers a known limitation through its independent statistical machinery, validating the architecture).

For the citation additions, the new references can be inserted with minimal disturbance: Burton 1988 and Quarry & Spodick 1974 in §3.7 / §4.3 (paired with the H6 finding); Lalande & Lyons 2010 and Newman & Callister 2008 in §1 ¶2 (G-LOC physiology multifactorial); Forster & Whinnery 1988 and Whinnery, Forster & Rogers 2014 in §2.1 (G-LOC definition and the LOC/ROC curve lineage); Eiken et al. 2007 in §2.2 (PBG benchmark).

I am available for re-review of the revised manuscript and would expect the revision to be straightforward given that the underlying analysis appears correct — only the description of the analysis in the manuscript is currently misaligned with the data product and the code.

---

*End of report.*
