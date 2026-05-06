# Archival validation cohort — provenance

> **Audit trail** for every record in
> `data/archival/centrifuge_tables.parquet`. Built by
> `scripts/extract_archival_tables.py`. The cohort backs OSF amendment
> 2026-05-06 hypothesis H6.

---

## Cohort phases

| Phase | Description | Status |
|---|---|---|
| A | Aggregated mean ± SD rows reproduced from FAA AM-23/6 (open-access summary of Whinnery & Forster 2013 Table 2 / Whinnery, Forster & Rogers 2014 Table 2) | ✅ shipped 2026-05-06 (this commit), n = 13 records |
| B | Per-subject records extracted directly from the upstream BMC open-access papers | ⬜ deferred — full-text scrape blocked by Springer Nature redirect chain on the current dev environment; planned for the next commit cycle |

Phase A is sufficient for the H6 success criterion (n ≥ 50 archival
event-time records combined across sources) once Phase B records are
added; Phase A alone (13 records) is reported as **exploratory** until
Phase B closes the gap. The threshold rules in OSF amendment §B (H6,
"failure handling") apply: if Phase B yields fewer than 30 additional
records, the archival arm is reframed as exploratory in §3.7 of the
manuscript.

---

## Phase A sources

### WF2013 — Whinnery & Forster (2013), 8 aggregated rows

- **Citation.** Whinnery JE, Forster EM. *The +Gz-induced loss of
  consciousness curve.* *Extreme Physiology and Medicine* 2(1):19,
  2013-06-06.
- **DOI.** 10.1186/2046-7648-2-19 (open access, CC-BY).
- **Cohort.** n = 729 USN + USAF participants, predominantly male.
- **Endpoint.** Time to loss of consciousness from the start of +Gz
  onset, for relaxed participants without anti-G countermeasures
  (no AGSM, no G-suit, no PBG).
- **Source table for this cohort.** Figure 2 of Whinnery & Forster
  (2013), reproduced numerically as Figure 1 of FAA technical report
  DOT/FAA/AM-23/6 (`docs/OAM202306(How_it_Works).md`, lines 314–382).
  The values transcribed here are taken from the FAA report, which
  is the authoritative open-source rendering of the Whinnery &
  Forster 2013 Figure 2 numerics.
- **Mapping rules to CGEM input space.** Each row reports a single
  acceleration onset rate (G/s); we map this verbatim to
  `dgdt_max_g_per_s`. The peak +Gz value is not reported per row;
  the experiment ceiling was 9.4 G. Subject-level anthropometry is
  unavailable; the CGEM `who_profile` mapping for this cohort uses
  `who_profile = 4` (military, average resistance, US data) per the
  rule locked in OSF amendment 2026-05-06 §B-H6. Countermeasure tier
  is "baseline" (no AGSM / no G-suit / no PBG).
- **Endpoint mapping.** The reported time-to-loss-of-consciousness is
  mapped to `time_to_gloc_s` directly (the FAA report and the upstream
  paper define LOCINDTI as the same quantity CGEM emits as
  `time_to_gloc_s`).

### WFR2014 — Whinnery, Forster & Rogers (2014), 5 aggregated rows

- **Citation.** Whinnery JE, Forster EM, Rogers PB. *The +Gz recovery
  of consciousness curve.* *Extreme Physiology and Medicine* 3:9,
  2014.
- **DOI.** 10.1186/2046-7648-3-9 (open access, CC-BY).
- **Cohort.** n = 715 USN + USAF participants, predominantly male
  (superset of the WF2013 cohort).
- **Endpoint.** Duration of absolute incapacitation following G-LOC,
  as a function of acceleration *offset* rate (rate of return to 1 G).
- **Source table for this cohort.** Table 2 of Whinnery, Forster &
  Rogers (2014), reproduced numerically as Figure 2 of FAA technical
  report DOT/FAA/AM-23/6 (`docs/OAM202306(How_it_Works).md`, lines
  393–474).
- **Mapping rules to CGEM input space.** The offset rate is reported
  in G/s; CGEM input-space does not currently encode offset rate
  separately from onset rate, so this column is preserved as
  `offset_rate_g_per_s` in the cohort but is *not* mapped to
  `dgdt_max_g_per_s`. The duration-of-incapacitation endpoint is
  reported as `duration_incap_s_mean`; CGEM does not currently emit a
  matching scalar (see §"Limitations" below), so these rows
  participate in H6's discrepancy quantification only when paired
  with a CGEM run that reports the analogous incapacitation duration
  via post-G-LOC c_bank recovery time.
- **Limitations.** The 2014 endpoint is *recovery* not *induction*; it
  validates a different aspect of CGEM than the 2013 onset-rate curve.
  We retain it in the cohort because it is the natural complement to
  WF2013 in the FAA report and because the mapping work is part of the
  Phase B per-subject extraction.

---

## Excluded sources (with reasons)

| Originally planned source | Reason for exclusion |
|---|---|
| Burns & Kruger (1997), "Mathematical model of G-LOC onset time…", *ASEM* 68(2):120–126 | **The cited paper does not exist.** Independent verification via PubMed (PMID 9143752 maps to Eshel et al. 1997 hyperthermia-induced cardiac arrest in monkeys), Crossref, scite, and PubMed phrase search returned zero records. Documented in OSF amendment 2026-05-06 §F. |
| Whinnery (1990), "The electroencephalographic response to +Gz stress", *ASEM* 61(5):435–439 | **The cited title and PMID do not match a real Whinnery paper.** PubMed PMID 2350248 maps to Avrushchenko et al. 1990 cerebral cortex chromatin, unrelated. The closest extant Whinnery 1990 paper is *ASEM* 61(5):406–411 (PMID 2350309), which is a different paper on a different topic and does not contain a tabulated G-LOC dataset usable for this cohort. Replaced as a manuscript reference (now ref [4]) but not used as a cohort source. |

---

## Reproducibility

- The parquet is regenerated by `python -m scripts.extract_archival_tables`.
- The script is deterministic — no network, no randomness; re-running
  against the same source markdown produces an identical parquet.
- Schema enforcement is in `tests/test_archival.py`.
- Every row carries `transcribed_on`, `transcribed_by`, `source_id`,
  `source_citation`, `source_doi`, and `source_table`. Per-row mapping
  rules are listed above and locked in OSF amendment 2026-05-06 §B-H6
  before any test-set evaluation under H6.

---

## Phase B (deferred) — per-subject extraction roadmap

To reach the H6 ≥ 50-record threshold with operationally meaningful
inputs, Phase B will retrieve per-subject records from the upstream
BMC open-access papers:

1. Pull
   `https://link.springer.com/article/10.1186/2046-7648-2-19` and
   `https://link.springer.com/article/10.1186/2046-7648-3-9` as PDF;
   parse Tables 1–3 of each.
2. For each per-subject row reported (if any), append to the
   parquet with `record_type="per_subject"` and `phase="B"`.
3. If the upstream tables are still pooled (no per-subject grain),
   retain Phase A as the cohort and either expand via additional
   open-source FAA / USAFSAM technical reports (DOT/FAA/AM-21/* and
   AFRL TRs published openly via NTRS) or downgrade H6 to
   exploratory per the OSF amendment's failure-handling rule.

Phase B kicks off in the next commit cycle; the deferral is recorded
here so the cite chain stays auditable.
