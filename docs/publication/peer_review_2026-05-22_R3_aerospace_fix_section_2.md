# §2.1 + §2.2 Methods Correction

This document reconciles Methods §2.1 (G-LOC detection paragraph) and §2.2
(Synthetic dataset, all subsections) of the PMEA manuscript with the actual
behaviour of the committed `cgem_ext` and CGEM-wrapper code, in response to
Reviewer 3's Major concerns 2 and 3.

`§1` and the abstract were inspected for downstream impact only and were
**not modified**.

## Source code paths inspected

- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/cgem_ext/data/generate_dataset.py`
  - Tier dictionaries: `DEHYDRATION_LEVELS` (lines 73–77); `COUNTERMEASURES_LEVELS`
    (lines 83–102); `G_TOLERANCE_TIERS` (line 106); `WHO_PROFILES` (line 108).
  - Grid enumeration: `_enumerate_grid` (lines 355–411) and module docstring
    (lines 1–39) — confirms the per-maneuver row math (standard 6 × 3 = 18;
    custom 3 × 3 × 3 = 27; 45 per maneuver × 72 = 3,240 total).
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/cgem_wrapper.py`
  - `PilotConfig` dataclass (lines 73–113), including `pbg_max_mmhg` documented
    range `0..60`, the `agsm_effectiveness` documented range `0..1`, the
    `gsuit_coverage_fraction` documented range `0.0 - 0.7`, and the
    `dehydration_level` docstring "fraction 0.0 (none) .. 1.0 (severe)".
  - Dehydration implementation: `_prepare_gloc_inp` lines 222–245 and the
    mirror block in `_prepare_gloc_inp_internal` lines 333–355 — the
    `dehydration_level` knob is a dimensionless 0–1 scaler that subtracts
    `10 × dehydr` mmHg from systolic BPs (BSP, MSP), `5 × dehydr` mmHg from
    diastolic BPs (BDP, MDP), and multiplies the normal and maximum cerebral
    flow constants (FNORM, FMAX) by `(1 − 0.10 × dehydr)`. It is not a
    plasma-volume parameter.
  - Event-flag parsing: `_parse_cgem_output` lines 432–474 — the output deck
    is the CGEM `custom()` format-700 table whose last three columns are the
    integer flags `n2` (consciousness), `ne2` (vision / peripheral retinal
    bank), and `non2` (blackout / central retinal bank). `t_grey`, `t_black`,
    and `t_gloc` are each the first sample at which the respective flag
    transitions 0 → 1; `f_vis` (`FON`, central retinal flow) is captured as
    a time series but is **not** the discriminant.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/maneuvers_catalog.py`
  - Category enum at lines 41–46; the 72 registered maneuvers partition as
    35 `championship` / 22 `military_acm` / 12 `extreme_post_stall` /
    3 `conceptual` (confirmed by `grep` count). The reviewer's audit of the
    actual parquet `value_counts()` reconstructs as 35 × 45 = 1,575; 22 × 45
    = 990; 12 × 45 = 540; 3 × 45 = 135, matching the committed dataset and
    the §3.5 LOGO table — i.e. the **catalogue**, not §3.1, is correct.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/cgem_ext/ood/features.py`
  - Feature-vector definition (lines 39–57) — 9 numeric + 7 one-hot
    `who_profile` indicators + 1 ordinal (`cm_ordinal ∈ {0, 1, 2}`), total
    17, matching §2.5 of the manuscript.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/OAM202305(User_Guide).md`
  - Line 1048–1050 fixes the `who_profile` mapping verbatim: `1 = high-resistance
    male, 2 = average male, 3 = low-resistance male, 4 = high-resistance
    female, 5 = average female, 6 = low-resistance female`.
- `/root/repos/CAMI-Gz-Effects-Model-CGEM-/docs/OAM202306(How_it_Works).md`
  - Lines 222–231 describe the four CGEM reserve banks (consciousness bank,
    life bank, peripheral retinal bank, central retinal bank) whose
    depletion drives the three flag transitions used by
    `_parse_cgem_output`.
  - Line 663 (Copeland & Whinnery 2023 §4) — the documented gradient-onset
    limitation that the H6 finding recovers, cited in §3.7.

## §2.1 G-LOC detection — Original vs Corrected

The original sentence at line 45 of `manuscript.md` is the second sentence of
the second paragraph of §2.1 ("CGEM integrates a system of ODEs …"). The
correction (i) restates the discriminant as the integer flag transitions in
the CGEM `custom()` output table, (ii) explains which CGEM internal reserve
bank each flag tracks, (iii) names this as the model's proxy for the clinical
G-LOC endpoint, and (iv) acknowledges that CGEM does not model A-LOC.
Citations are restricted to references already present in the bibliography
(Copeland and Whinnery 2023; Whinnery 1990).

### Original

> CGEM integrates a system of ODEs over the maneuver window, producing
> per-sample time series for compartmental arterial pressures (eye-level,
> brain-level, heart-level), cerebral blood flow velocity (`c_bank`), brain
> oxygenation (`bo_bank`), retinal oxygen delivery, and visual function
> indices (`f_vis`, `f_bo`). Event-time scalars — greyout, blackout, and
> G-LOC — are the earliest samples at which visual function crosses
> predefined thresholds (right-censored if never crossed).

### Corrected

> CGEM integrates a system of ODEs over the maneuver window, producing
> per-sample time series for compartmental arterial pressures (eye-level,
> brain-level, heart-level), cerebral blood flow velocity (`c_bank`),
> brain oxygenation (`bo_bank`), retinal oxygen delivery (`f_vis`, `f_bo`),
> and four internal reserve-bank balances that drive the model's event
> logic (Copeland and Whinnery 2023). Event-time scalars — greyout
> (`time_to_greyout_s`), blackout (`time_to_blackout_s`), and G-LOC
> (`time_to_gloc_s`) — are taken from the earliest 0 → 1 transition of
> the three integer state flags written into the `custom()` output table:
> `ne2` (peripheral retinal bank depletion → greyout), `non2` (central
> retinal bank depletion → blackout), and `n2` (consciousness bank
> depletion → G-LOC). Each flag is the discrete realisation of its
> reserve bank crossing zero balance, not a threshold on `f_vis` or any
> other continuous channel; events are right-censored if the
> corresponding flag never transitions during the simulated window.
> `n2` is CGEM's proxy for the clinical / centrifuge-operator G-LOC
> endpoint that is typically scored from impaired motor response or EEG
> in instrumented protocols (Whinnery 1990; Copeland and Whinnery 2023);
> the model does not represent A-LOC (almost-LOC / cognitive
> incapacitation without full unconsciousness), and the surrogate
> inherits that gap.

## §2.2 Synthetic dataset — Original vs Corrected

The original §2.2 is lines 49–61 of `manuscript.md`. The correction replaces
the inline parameter values for the **standard-arm countermeasure tiers** and
the **custom-arm grid** with the verbatim contents of
`cgem_ext.data.generate_dataset.{COUNTERMEASURES_LEVELS, G_TOLERANCE_TIERS,
DEHYDRATION_LEVELS}`. The "moderate" tier (G-suit 5 psi, AGSM 0.5, no PBG)
that the original paragraph asserted is removed — it does not exist in the
code; the three labels in the dictionary are `none`, `agsm` (AGSM alone,
no suit, no PBG), and `suit_agsm` (G-suit 10 psi at 0.7 body coverage,
AGSM 0.8, PBG 15 mmHg). The original framing of `dehydration_level ∈ {0,
0.04, 0.08}` as "fractional plasma volume loss" is replaced with a
description of the empirical 0–1 scaling on resting / maximum arterial
pressures and cerebral flow that CGEM-wrapper implements (lines 222–245 of
`cgem_wrapper.py`), with the actual grid `{0.0, 0.3, 0.7}` from the code.
A one-line FAA `who_profile` legend is added (per OAM202305 line 1049) so
the §3.7 H6 anchor can be read without forward-reference. The post-stall
inclusion rationale (Reviewer 3 Major concern 5) is added as a short
clarifying clause; this is the minimum correction to align the dataset
description with the catalogue's actual category balance and the §3.5 LOGO
report. Row counts (18 / 27 / 45 per maneuver, 1,296 / 1,944 / 3,240 total)
are preserved.

### Original (full §2.2)

> ### 2.2 Synthetic dataset
>
> A structured synthetic dataset (`cgem_synthetic_v1`) was generated by
> enumerating a cross-product input grid and invoking CGEM once per
> (maneuver, pilot configuration) pair.
>
> **Maneuvers.** 72 aerobatic, military, and extreme post-stall maneuvers
> were selected from the Aresti CIVA catalogue (Aresti System 2019), IAC
> Known/Unknown programmes (2015–2020), and published USAFSAM/ASEM
> centrifuge profiles (Copeland 2021). Each maneuver is a (time, Nz) trace
> in the `Aerobatics_sample_inputs/*.txt` format consumed by CGEM;
> `maneuvers_catalog.py` records category (`championship`, `conceptual`,
> `extreme_post_stall`, `military_acm`), Aresti family, G-peak,
> max |dG/dt|, and duration.
>
> **Pilot configurations — standard arm.** Six FAA `who_profile` presets
> (1–6) × three countermeasure tiers — baseline (no G-suit, no AGSM, no
> PBG), moderate (G-suit 5 psi, AGSM 0.5, no PBG), maximum (G-suit 10 psi,
> AGSM 1.0, PBG 30 mmHg). The Fortran model overrides subject physiology
> to the FAA preset whenever `who_profile ∈ {1..6}`, so
> `g_tolerance_multiplier` and `dehydration_level` are no-ops on the
> standard arm and were held at canonical values (1.0, 0.0). Standard arm:
> 6 × 3 = 18 rows per maneuver, 1,296 rows total.
>
> **Pilot configurations — custom arm.** A 3 × 3 × 3 grid: G-tolerance
> multiplier ∈ {0.85, 1.00, 1.15}, dehydration level ∈ {0.0, 0.04, 0.08}
> (fractional plasma volume loss), countermeasure tier ∈ {baseline,
> moderate, maximum}, all under `who_custom` (synthetic profile with
> editable physiology). Custom arm: 27 rows per maneuver, 1,944 rows total.
>
> The full grid yields 18 + 27 = 45 rows per maneuver × 72 maneuvers =
> **3,240 rows**. Each row carries a deterministic
> `row_seed = SHA256(master_seed || row_id)` with master seed 42;
> generation is parallelized via `multiprocessing.Pool` (`spawn` start,
> `cpu_count − 1` workers, isolated tmpdir per worker).
>
> **Reproducibility.** The dataset is fully reproducible from the CGEM
> binary, the maneuver catalog at the committed SHA, the master seed (42),
> the tier definitions in `cgem_ext.data.generate_dataset`, and the
> compiled binary's SHA-256 hash; re-running
> `python -m cgem_ext.data.generate_dataset --seed 42` against the same
> binary produces an identical parquet file (verified by
> `tests/test_data.py::test_generator_is_deterministic`). The dataset
> schema and documentation follow the datasheet framework of Gebru et al.
> (2018); the full datasheet is included as supplementary material.

### Corrected (full §2.2)

> ### 2.2 Synthetic dataset
>
> A structured synthetic dataset (`cgem_synthetic_v1`) was generated by
> enumerating a cross-product input grid and invoking CGEM once per
> (maneuver, pilot configuration) pair. The grid is defined verbatim in
> `cgem_ext.data.generate_dataset`; the dictionaries quoted in the
> paragraphs below are reproduced from that module without editorial
> rounding.
>
> **Maneuvers.** A catalogue of 72 maneuvers was assembled from the
> Aresti CIVA catalogue (Aresti System 2019), IAC Known / Unknown
> programmes (2015–2020), and published USAFSAM / ASEM centrifuge profiles
> (Copeland 2021). Each maneuver is a (time, Nz) trace in the
> `Aerobatics_sample_inputs/*.txt` format consumed by CGEM, with
> structured metadata recorded in `maneuvers_catalog.py` (category, Aresti
> family, peak +Gz, peak −Gz, onset rate, sustained Gz and duration). The
> catalogue partitions into four categories: `championship` (n = 35),
> `military_acm` (n = 22), `extreme_post_stall` (n = 12), and `conceptual`
> (n = 3). The `extreme_post_stall` category (Pugachev cobra, kulbit,
> tailslide variants, hammerhead) is included as a boundary-condition
> probe of low-sustained-Gz / high-angle-of-attack inputs — operationally
> these maneuvers stress the vestibular system rather than cerebrovascular
> physiology, so they populate the low-G end of the surrogate's training
> envelope and supply a low-event-rate stratum for the §3.5 LOGO probe
> rather than a primary G-tolerance regime.
>
> **Pilot configurations — standard arm.** Six FAA `who_profile` presets
> ($1$ = high-resistance male, $2$ = average male, $3$ = low-resistance
> male, $4$ = high-resistance female, $5$ = average female, $6$ =
> low-resistance female; Copeland and Whinnery 2023) crossed with three
> countermeasure tiers from `COUNTERMEASURES_LEVELS`:
>
> | Tier label | `gsuit_max_psi` | `gsuit_coverage_fraction` | `agsm_effectiveness` | `pbg_max_mmhg` |
> |---|---:|---:|---:|---:|
> | `none` | 0.0 | 0.0 | 0.0 | 0.0 |
> | `agsm` | 0.0 | 0.0 | 0.6 | 0.0 |
> | `suit_agsm` | 10.0 | 0.7 | 0.8 | 15.0 |
>
> The Fortran model overrides subject physiology (resting / maximum
> arterial pressures, cerebral flow constants, sex, height) to the FAA
> preset whenever `who_profile ∈ {1, …, 6}`, so the custom-arm knobs
> `g_tolerance_multiplier` and `dehydration_level` are no-ops on the
> standard arm and were held at their canonical values ($1.0$ and $0.0$
> respectively). Standard arm: $6 \times 3 = 18$ rows per maneuver, $1{,}296$
> rows total. We note for the operational reader that the `suit_agsm`
> tier's $\text{PBG} = 15$ mmHg is well below the operational PBG
> envelope of $50$–$60$ mmHg used in modern G-protection rigs (Eiken et
> al. 2007); the §3.6 sensitivity finding that PBG carries near-zero
> total-order index should therefore be read as a property of this
> training-grid setting, not as a physiological claim about PBG in
> general.
>
> **Pilot configurations — custom arm.** A $3 \times 3 \times 3$ grid
> exercises the custom-subject path (`who_profile = None`, encoded as
> `who_custom = 1` in the OOD feature vector): `g_tolerance_multiplier`
> $\in \{0.85, 1.00, 1.15\}$ from `G_TOLERANCE_TIERS`, `dehydration_level`
> $\in \{0.0, 0.3, 0.7\}$ from `DEHYDRATION_LEVELS`, and the same three
> countermeasure tiers. `dehydration_level` is the dimensionless empirical
> scaling factor implemented by the CGEM Python wrapper: at level $d$, the
> baseline and maximum systolic arterial pressures are reduced by $10 \times d$
> mmHg, the baseline and maximum diastolic pressures by $5 \times d$ mmHg,
> and the normal and maximum cerebral blood flow constants by a factor
> $(1 - 0.10 \times d)$; it is a phenomenological scaling of resting /
> maximum BP and flow, not a plasma-volume parameter. Custom arm:
> $3 \times 3 \times 3 = 27$ rows per maneuver, $1{,}944$ rows total.
>
> The full grid yields $18 + 27 = 45$ rows per maneuver $\times$ 72 maneuvers
> $= \mathbf{3{,}240}$ rows. Each row carries a deterministic
> `row_seed = SHA256(master_seed || row_id)` with master seed $42$;
> generation is parallelised via `multiprocessing.Pool` (`spawn` start,
> `cpu_count − 1` workers, isolated tmpdir per worker).
>
> **Reproducibility.** The dataset is fully reproducible from the CGEM
> binary, the maneuver catalogue at the committed SHA, the master seed
> ($42$), the three tier dictionaries
> (`COUNTERMEASURES_LEVELS`, `G_TOLERANCE_TIERS`, `DEHYDRATION_LEVELS`) in
> `cgem_ext.data.generate_dataset`, and the compiled binary's SHA-256
> hash recorded in `cgem_synthetic_v1.meta.json`; re-running
> `python -m cgem_ext.data.generate_dataset --seed 42` against the same
> binary produces an identical parquet file (verified by
> `tests/test_data.py::test_generator_is_deterministic`). The dataset
> schema and documentation follow the datasheet framework of Gebru et al.
> (2018); the full datasheet is included as supplementary material.

## Per-claim audit

All line references in the right-hand columns are zero-indexed absolute file
lines (i.e. the same numbers `Read`/`cat -n` would report). Original-text
line numbers refer to `manuscripts/cgem/pmea/src/manuscript.md`.

| Claim in original | Actual code value | Code file / line | Action |
|---|---|---|---|
| Event-time scalars are "the earliest samples at which visual function crosses predefined thresholds" (§2.1 line 45) | `t_grey` ← `ne2` 0→1 flag transition; `t_black` ← `non2` 0→1 flag transition; `t_gloc` ← `n2` 0→1 flag transition. `f_vis`/`FON` is captured but not the discriminant. | `cgem_wrapper.py` lines 432–474 (parser); 60–62 (flag docstrings on `CGEMResult`); OAM202306 lines 222–231 (reserve-bank semantics) | Replace sentence — extend correction to all three events, not just G-LOC, since `f_vis` does not drive any of them. |
| "three countermeasure tiers — baseline (no G-suit, no AGSM, no PBG), moderate (G-suit 5 psi, AGSM 0.5, no PBG), maximum (G-suit 10 psi, AGSM 1.0, PBG 30 mmHg)" (§2.2 line 55) | Three labels: `none`, `agsm`, `suit_agsm`. No "moderate" tier exists. | `cgem_ext/data/generate_dataset.py` lines 83–102 | Replace with verbatim dictionary table (see Corrected §2.2). |
| "G-suit 5 psi" in the moderate tier | The middle tier (`agsm`) is AGSM-only with `gsuit_max_psi = 0.0`; the only non-zero suit pressure in the grid is `gsuit_max_psi = 10.0` in `suit_agsm`. | `cgem_ext/data/generate_dataset.py` lines 90–94 (`agsm`); 96–101 (`suit_agsm`) | Remove the 5-psi claim; replace with the dictionary table. |
| "AGSM 0.5" (moderate tier) | The middle tier uses `agsm_effectiveness = 0.6`. | `cgem_ext/data/generate_dataset.py` line 93 | Replace with 0.6. |
| "AGSM 1.0" (maximum tier) | The maximum tier uses `agsm_effectiveness = 0.8`. | `cgem_ext/data/generate_dataset.py` line 99 | Replace with 0.8. |
| "PBG 30 mmHg" (maximum tier) | The maximum tier uses `pbg_max_mmhg = 15.0`. | `cgem_ext/data/generate_dataset.py` line 100 | Replace with 15.0 mmHg; flag in the prose that this is well below modern operational PBG. |
| `gsuit_coverage_fraction` not mentioned in §2.2 | The coverage fraction is part of every tier (0.0, 0.0, 0.7) and is part of the OOD feature vector. | `cgem_ext/data/generate_dataset.py` lines 85, 92, 98; `cgem_ext/ood/features.py` line 44 | Add to the §2.2 tier table. |
| Tier labels "baseline / moderate / maximum" | Code labels are `none / agsm / suit_agsm`. | `cgem_ext/data/generate_dataset.py` lines 84, 90, 96 | Use the code labels in the corrected §2.2 (matches OOD `cm_ordinal` encoding 0/1/2 in `cgem_ext/ood/features.py` line 62). |
| "dehydration level ∈ {0.0, 0.04, 0.08} (fractional plasma volume loss)" (§2.2 line 57) | `DEHYDRATION_LEVELS = {"none": 0.0, "mild": 0.3, "severe": 0.7}`; the wrapper implements `dehydration_level` as a dimensionless 0–1 scaler on BPs (−10×d / −5×d mmHg) and on cerebral flow ((1 − 0.10×d)×fnorm, (1 − 0.10×d)×fmax). The `PilotConfig` docstring explicitly calls this "fraction 0.0 (none) .. 1.0 (severe)". | `cgem_ext/data/generate_dataset.py` lines 73–77; `cgem_wrapper.py` lines 111 (docstring), 222–245 (implementation), 333–355 (mirror block) | Replace with `{0.0, 0.3, 0.7}` and re-describe as a BP / flow scaling, dropping "fractional plasma volume loss". |
| "all under `who_custom` (synthetic profile with editable physiology)" (§2.2 line 57) | `who_profile = None` is the user-facing input that internally maps to `who = 0` (custom subject); `who_custom = 1` is the OOD-feature-space encoding. | `cgem_wrapper.py` lines 86 (default), 198 (mapping); `cgem_ext/ood/features.py` lines 71–73 | Clarify that `who_custom` is the OOD-encoding name; keep the manuscript's existing terminology. |
| "category (`championship`, `conceptual`, `extreme_post_stall`, `military_acm`), Aresti family, G-peak, max |dG/dt|, and duration" (§2.2 line 53) | Confirmed (`ManeuverCategory` enum has exactly those four members; the dataclass records all listed fields). | `maneuvers_catalog.py` lines 41–46, 49–65 | No change needed — but the corrected §2.2 adds the actual category counts so a reader can match §3.5 LOGO without arithmetic. |
| "Six FAA `who_profile` presets (1–6)" (§2.2 line 55) | Confirmed: `WHO_PROFILES = [1, 2, 3, 4, 5, 6]`. | `cgem_ext/data/generate_dataset.py` line 108 | Keep; corrected §2.2 also expands the legend per OAM202305 line 1049. |
| Standard-arm row count "6 × 3 = 18 rows per maneuver, 1,296 rows total" (§2.2 line 55) | Confirmed by enumeration. | `cgem_ext/data/generate_dataset.py` lines 370–389 | No change. |
| Custom-arm row count "27 rows per maneuver, 1,944 rows total" (§2.2 line 57) | Confirmed by enumeration. | `cgem_ext/data/generate_dataset.py` lines 390–411 | No change. |
| Total dataset "18 + 27 = 45 rows per maneuver × 72 maneuvers = 3,240 rows" (§2.2 line 59) | Confirmed. | Module docstring line 21; `_enumerate_grid` lines 355–411 | No change. |
| Reproducibility block (`row_seed`, master seed 42, parallelisation, binary SHA-256) (§2.2 lines 59, 61) | Confirmed end-to-end (seed → `_row_seed` → `RowSpec.seed`; binary SHA-256 in `metadata` block). | `cgem_ext/data/generate_dataset.py` lines 116–119, 122–127, 457, 504–525 | No change. |

## Additional findings

Several adjacent inconsistencies surfaced during this audit. They are not
inside §2.1 or §2.2 and should not be folded into the corrected text blocks
above, but they should be noted because the same revision pass should not
ship the manuscript with them unresolved.

1. **`who_profile = 4` in §3.7 (line 232) is "high-resistance female", not
   "high-resistance male".** Reviewer 3's report (line 152) describes
   `who_profile = 4` as "high-resistance male", but `docs/OAM202305(User_Guide).md`
   line 1049 is unambiguous: `4 = high-resistance female`. The manuscript
   text at line 232 does not itself state which preset `who_profile = 4`
   is — it simply says "`who_profile = 4`, baseline countermeasures" — but
   any §3.7 expansion that names the preset (e.g. for the
   suggested-reviewer-friendly legend the reviewer also requests at line 152)
   must use the female-high-resistance label. This also matters for the
   §3.7 H6 framing: relaxed-subject Whinnery–Forster 2013 data are
   majority-male, so anchoring the H6 query at `who_profile = 4` (highest
   female G-tolerance) is a defensible high-resistance choice but is not a
   like-for-like sex match to the source cohort and should be acknowledged
   in §3.7. This is **out of scope for the §2.1 / §2.2 correction**, but
   the OSF amendment 2026-05-06 §B-H6 and the legend in §2.1 (line 43)
   should be cross-checked when this revision pass closes.

2. **Standard-arm "baseline countermeasures" language in §3.7 (line 232).**
   The H6 query uses the `none` countermeasure tier (per the rules locked
   in OSF amendment 2026-05-06). The manuscript line 232 says "baseline
   countermeasures", which is the language replaced by the §2.2 correction.
   When §2.2 is updated to use the `none` / `agsm` / `suit_agsm` labels, the
   §3.7 reference should be updated to "the `none` countermeasure tier" for
   internal consistency. Mechanical replacement; not a science fix.

3. **§2.1 line 43 parameter list — "PBG max pressure" with no value.** The
   sentence at line 43 lists `gloc_inp.dat` fields including "PBG max
   pressure". The `PilotConfig` docstring (line 105 of `cgem_wrapper.py`)
   documents this knob as `pbg_max_mmhg: float = 0.0  # 0..60`, and CGEM
   docstrings cite 60 mmHg as the physiological / operational ceiling
   (OAM202305 §"pbg"; Eiken et al. 2007). The manuscript should state the
   admissible range somewhere — supplementary Table S1 (`PilotConfig`
   schema) is the natural home. This is not §2.1 / §2.2 text; it is a
   supplementary-table item that the reviewer's Major concern 2 implicitly
   asks the manuscript to clarify when it asks for the dictionary verbatim.

4. **§2.5 17-feature breakdown is correct.** Reviewer's Major concerns do
   not touch §2.5, and the §2.5 feature-vector description matches
   `cgem_ext/ood/features.py` lines 39–57 (9 numeric + 7 one-hot
   `who_profile` indicators + 1 ordinal). No change.

5. **Table 1 forward-reference in §2.1 line 43 ("full parameter definitions
   in Table 1").** Table 1 in the current PMEA manuscript is the
   regression-performance table, not a `PilotConfig` schema. The §2.1
   line-43 forward reference is therefore broken. Either Table 1 should be
   re-promised to the supplementary `PilotConfig` schema table (the natural
   home), or the §2.1 sentence should drop the forward reference. This is
   a typography/cross-reference fix, not a science fix; the §2.1 corrected
   block above does not touch it, because Reviewer 3's concern is the
   sentence at line 45, not the sentence at line 43.

6. **§3.1 dataset descriptives are wrong (Reviewer 3 Major concern 1).** Not
   in scope here, but the §2.2 catalogue-count addition ("`championship`
   $n = 35$ / `military_acm` $n = 22$ / `extreme_post_stall` $n = 12$ /
   `conceptual` $n = 3$") in the corrected §2.2 is consistent with what
   §3.1 should be rewritten to, so the two fixes interlock — when §3.1 is
   regenerated from the parquet, it should report category sizes of $1{,}575$
   / $990$ / $540$ / $135$ rows (i.e. $\text{catalogue count} \times 45$).

`§1` and the abstract were inspected for downstream impact and were not
modified.
