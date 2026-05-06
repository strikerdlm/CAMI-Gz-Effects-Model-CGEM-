# Datasheet — archival validation cohort (`centrifuge_tables.parquet`)

> Datasheet per Gebru et al. (2018). The cohort backs the H6 hypothesis
> in OSF amendment 2026-05-06. Phase A (this version): 13 aggregated
> mean ± SD records reproduced from FAA AM-23/6's open-source
> rendering of Whinnery & Forster (2013) and Whinnery, Forster &
> Rogers (2014). Phase B (deferred): per-subject extraction.

---

## Motivation

### For what purpose was the dataset created?

To build an external validation cohort for the CGEM ML extension
layer (the `cgem_ext` Python package and its surrogate / OOD /
sensitivity components), so that the manuscript's CQR-based
prediction intervals on `time_to_gloc_s` can be evaluated against
real centrifuge outcomes — not just against CGEM-as-ground-truth on
the synthetic dataset `cgem_synthetic_v1`.

### Who created the dataset?

Diego Malpica, MD (sole author of the present manuscript), via the
deterministic transcription script `scripts/extract_archival_tables.py`.
Source numbers were transcribed from the FAA technical report
DOT/FAA/AM-23/6 (Copeland & Whinnery 2023, doi 10.21949/1524446),
which itself reproduces Whinnery & Forster (2013) Figure 2 and
Whinnery, Forster & Rogers (2014) Table 2.

### Who funded the dataset?

No external funding. The transcription was carried out within the
CGEM repository under the originality-uplift plan
(`/root/.claude/plans/moonlit-stargazing-wolf.md`, Scenario B).

---

## Composition

### What do the instances represent?

Each row is an *aggregated* (mean ± SD) summary statistic across a
fixed acceleration profile, drawn from a centrifuge cohort of
predominantly male USN + USAF participants. Phase A holds 13 such
rows (8 onset-rate rows from WF2013, 5 offset-rate rows from
WFR2014). Phase B will add per-subject rows when the underlying
papers' table-level grain is extractable.

### How many instances are there in total?

Phase A: **13 rows**. Combined parent cohort sizes: WF2013 n = 729,
WFR2014 n = 715 (overlapping samples per the WFR2014 paper). The 13
aggregated rows therefore *represent* a much larger underlying
participant pool.

### Is there a label or target associated with each instance?

Yes. Each row carries one of:
- `time_to_gloc_s_mean` and `time_to_gloc_s_sd` (WF2013 onset-rate
  rows): the mean ± SD time from start of +Gz onset to loss of
  consciousness, in seconds.
- `duration_incap_s_mean` (WFR2014 offset-rate rows): the mean
  duration of absolute incapacitation following a G-LOC event, in
  seconds.

A test in `tests/test_archival.py::test_archival_endpoints_match_cgem_outcomes`
enforces that the two endpoints occupy disjoint rows.

### Is any information missing from individual instances?

Yes, by construction. The aggregated rows do not preserve
per-subject anthropometry, age, sex, body habitus, or hydration
state. The cohort is therefore appropriate for validating
*population-level* CGEM predictions (with the `who_profile = 4`
mapping) but not for per-pilot calibration. Per-pilot calibration is
deferred per OSF amendment H6 and the originality plan's Scenario C.

### Are relationships between individual instances made explicit?

The `source_id` column groups rows by upstream paper. Within each
group, the rows are ordered by acceleration onset (WF2013) or offset
(WFR2014) rate.

---

## Collection process

### How was the data acquired?

Two-step:

1. The upstream centrifuge data were collected at USN / USAF
   facilities under each of the two source studies (Whinnery &
   Forster 2013, Whinnery Forster & Rogers 2014). Per the upstream
   papers and the FAA AM-23/6 summary, the protocols were
   relaxed-participant +Gz exposures with no anti-G countermeasures,
   on a centrifuge with a 9.4 G ceiling and a 10° posterior seat
   tilt.
2. The numerical values transcribed into this cohort were copied
   from the FAA AM-23/6 report tables (Figures 1 and 2 of that
   report) into the deterministic Python script
   `scripts/extract_archival_tables.py`. The FAA report is the
   authoritative open-source rendering of these tables.

### Over what timeframe was the data collected?

Underlying centrifuge protocols span the late 1980s through the
mid-2000s per the source papers. The transcription into this
repository was performed on 2026-05-06 (recorded in the
`transcribed_on` column of every row).

### Were any ethical review processes conducted?

The upstream centrifuge experiments were approved under the relevant
USN / USAF medical IRB processes documented in the source papers.
The present transcription is a third-party reuse of already-published
mean ± SD summary statistics; no additional IRB approval is required.

### Has the data been pre-processed/cleaned/labelled?

Yes — the FAA AM-23/6 authors pre-processed the per-subject data
into the mean ± SD aggregates this cohort uses. No further cleaning
was applied; values are transcribed verbatim.

---

## Uses

### What tasks could the dataset be used for?

- Validate the CGEM `time_to_gloc_s` predictions against real
  centrifuge outcomes at population-average physiology.
- Evaluate the calibrated CGEM ± surrogate-CI bracket coverage on
  archival event-time data (the H6 hypothesis).
- Anchor the discrepancy term δ(x) = real(x) − CGEM(x) for a future
  multi-fidelity or Bayesian per-pilot extension (originality plan
  Scenario C).

### Are there tasks for which the dataset should not be used?

- Per-pilot risk prediction: the cohort is aggregated, so individual
  pilot inferences are not supported.
- Validation of CGEM under non-relaxed countermeasure tiers: every
  Phase A row is a baseline/no-countermeasures record. Validation
  of CGEM under AGSM, G-suit, or PBG is **out of scope** for Phase A
  and would require a different cohort.
- Validation of CGEM at +Gz levels above the centrifuge experimental
  ceiling (9.4 G).

---

## Distribution

### How will the dataset be distributed?

The parquet is committed under `data/archival/centrifuge_tables.parquet`
and is regenerable via `python -m scripts.extract_archival_tables`.
Provenance is in `data/archival/PROVENANCE.md`.

### What licence applies?

The numerical values are reproduced from FAA Office of Aviation
Medicine technical reports (DOT/FAA/AM-23/6 and the upstream
*Extreme Physiology and Medicine* papers under CC-BY 4.0). The
transcription script and the schema are MIT-licensed, matching the
rest of the `cgem_ext` package.

---

## Maintenance

### Who is supporting/hosting/maintaining the dataset?

Diego Malpica, MD, as part of the `strikerdlm/CAMI-Gz-Effects-Model-CGEM-`
repository on GitHub.

### Will the dataset be updated?

Yes. Phase B (per-subject extraction) is the next planned update;
its closure criteria are specified in OSF amendment 2026-05-06 §B-H6
and `data/archival/PROVENANCE.md`.

### How will errors be communicated and corrected?

Schema errors are caught by `tests/test_archival.py`. Numerical
errors in transcription must be corrected in
`scripts/extract_archival_tables.py` (the source of truth) and the
parquet regenerated. Each row carries `transcribed_on` and
`transcribed_by` so the audit trail survives corrections.
