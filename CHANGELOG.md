# Changelog

All notable changes to the CGEM extension layer (this fork) are documented in
this file. The underlying FAA CGEM Fortran model itself is not modified —
this changelog tracks the Python wrapper, profile library, catalog, batch
runner, and frontend application code.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/) at the
extension-layer level (the upstream CGEM software DOI is fixed, see README).

## [Unreleased]

### Added

- **56 new aerobatic / military / extreme maneuver profiles** in
  `Aerobatics_sample_inputs/`, expanding the registered library from 16 to 72.
  - **Championship (23, Aresti / IAC)**: avalanche, tailslide ±, humpty bump ±,
    square loop, reverse Cuban eight, snap roll (level / vertical / outside),
    hesitation roll (4-pt / 8-pt), slow roll, inverted spin, flat spin
    (positive / inverted), English bunt, torque roll, knife-edge pass with
    high-G entry, double Immelmann, quarter clover, reverse half-Cuban,
    lazy eight.
  - **Military ACM / BFM (21)**: defensive break (9 G), sustained 9-G turn,
    corner velocity turn, high yo-yo, low yo-yo, barrel-roll attack, lag
    pursuit roll, flat scissors, rolling scissors, defensive jink, last-ditch
    break, combat Immelmann, combat Split-S, defensive break with chaff/flare,
    strike-turn strafing pull-out, push-pull missile evasion, defensive
    spiral, rate fight (sustained 8 G / 22 s), vertical climb missile
    evasion, helicopter (low-energy) bug-out, slatted high-AOA turn.
  - **Extreme / post-stall (12)**: Pugachev's Cobra, Kulbit, Lomcovák,
    Lomcovák repeats, Herbst / J-turn, Russian helicopter ('Bell'),
    falling leaf, snake-modulated falling leaf, tailslide-tumble combination,
    inverted Cobra, inverted spin recovery, Bell tailslide.
- **`maneuvers_catalog.py`** — structured metadata registry covering all 72
  maneuvers with Aresti family, peak ±Gz, onset rate, sustained-G plateau,
  hemodynamic concern, and source citation. Exposes `ManeuverCategory` enum
  (`championship`, `military_acm`, `extreme_post_stall`, `training`,
  `conceptual`) and `by_category(...)` / `get(identifier)` helpers.
- **`run_cgem_batch.py`** — batch runner that executes CGEM on every
  registered maneuver across multiple `PilotConfig` presets
  (`no_countermeasures`, `gsuit_only`, `agsm_only`, `full_countermeasures`,
  `dehydrated`) and pilot subjects (1–6). Persists per-run JSON time-series
  and a rollup `summary.json` / `summary.parquet` under
  `data/batch_results/`.
- **`tools/extension_profiles.py`** — single source of truth for the new
  profile data (Nz, duration_ms rows + metadata).
- **`tools/generate_extension.py`** — generator that emits the 56 `.txt`
  files into `Aerobatics_sample_inputs/` and registry snippets, with
  row-count assertions.
- **`tools/build_hemodynamics_report.py`** — analysis script that turns
  `data/batch_results/summary.json` into a per-maneuver Markdown report.
- **`docs/MANEUVER_HEMODYNAMICS.md`** — cross-sectional CGEM analysis:
  top-10 G-LOC-prone maneuvers, countermeasure efficacy, push-pull stress
  index (ms below 0 G), per-category cross-config tables, sustained-G
  endurance comparison.
- **`docs/MANEUVER_INDEX.md`** — categorized index of all 72 maneuvers with
  links to source files and metadata fields.

### Changed

- **`aerobatic_profiles.py`** — `PROFILES` dict expanded from 16 to 72
  entries, grouped by section header comment (championship / military
  ACM / extreme post-stall).
- **`README.md`** — documents the new maneuver categories, the
  `maneuvers_catalog.py` registry, the batch runner CLI, and the
  hemodynamics report pipeline.
- **`.gitignore`** — excludes the generated intermediate snippet files
  produced by `tools/generate_extension.py`.

### Methodology and provenance

Profiles added in this release are **kinematic-phase reconstructions**
calibrated against the canonical CGEM sample inputs and the following
domain references (cited at the title level — DOIs included where the
reference is uniquely indexed):

- FAI/CIVA Aresti Aerocryptographic System catalogue (families 1–9).
- IAC (International Aerobatic Club) Known/Free programmes (Unlimited &
  Advanced).
- FAA-H-8083-9 *Aerobatic Flying Handbook*.
- Shaw, R. L. (1985). *Fighter Combat: Tactics and Maneuvering.* Naval
  Institute Press.
- Newman, D. G., & Callister, R. (2009). DOI:
  [10.3357/asem.2361.2009](https://doi.org/10.3357/asem.2361.2009).
- Herbst, W. B. (1980). *Dynamics of Air Combat.* Journal of Aircraft 17(8).
- NASA Langley / Dryden high-AOA, post-stall, and spin-recovery technical
  literature (Foster, J. V.; Chambers, J. R.; Bihrle Applied Research).
- Banks, R. D. et al. — push-pull effect literature in *Aviation, Space, and
  Environmental Medicine* (1990s).
- Burton, R. R. — −Gz physiology, USAFSAM technical reports (1980s–1990s).
- USAF AFMAN 11-2F-16 / 11-2F-22 / 11-2F-15 / 11-2F/A-18 / 11-2A-10 BFM
  volumes (cited by name; portions controlled-distribution).

The new profiles are **stress-test inputs to CGEM, not flight-test
telemetry**. Per-maneuver source notes live in `tools/extension_profiles.py`.

### CGEM model caveats reaffirmed

- **Scalar Nz only.** CGEM models +Gz / −Gz exclusively. Lateral (Gy) and
  longitudinal (Gx) loads from snap rolls, flat spins, and Lomcovák-class
  tumbling are not represented; the +Gz time series understates true
  physiologic stress for those maneuvers.
- **Onset-rate ceiling.** CGEM is validated through ~10 G/s onset (Copeland
  & Whinnery 2023, DOI:10.21949/1524446). Snap rolls, Cobra-class spikes,
  and Lomcovák tumbles in this release encode 30–60 G/s onset rates;
  behaviour above the validation ceiling is extrapolated.
- **No baroreflex-fatigue term.** CGEM is most likely to under-predict
  G-LOC for `lomcovak_repeats`, `tailslide_tumble`, and other maneuvers
  with sustained alternating ±G that exhausts vagal tone over many cycles.

---

## Prior history

See `git log` for commit-level history of the upstream FAA CGEM port and
the TypeScript frontend additions (premium model dynamics workspace,
ECharts dashboards, CGEM wrapper improvements).
