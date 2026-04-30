# Changelog

All notable changes to the CGEM extension layer (this fork) are documented in
this file. The underlying FAA CGEM Fortran model itself is not modified —
this changelog tracks the Python wrapper, profile library, catalog, batch
runner, and frontend application code.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/) at the
extension-layer level (the upstream CGEM software DOI is fixed, see README).

## [Unreleased]

### Added (Phase 0 — ML extension layer foundation)

- **`ROADMAP.md`** at repo root: phase tracker for the migration to a
  FastAPI + React + ML stack culminating in a Q1 publication in
  *Aerospace Medicine and Human Performance* (AMHP). Tracks Phases 0–9
  (foundation → dataset → OOD → surrogate → sensitivity → API →
  frontend → AMHP paper → external re-analysis → own-centrifuge
  validation). Each phase has checkbox-tracked deliverables.
- **`docs/architecture/ML_LAYER.md`**: technical architecture spec for
  the additive `cgem_ext` layer. Documents module boundaries,
  versioning policy, reproducibility chain, and the constraint that
  the FAA Fortran core (`src/cgem.f`) must remain unmodified to
  preserve the validation chain.
- **`docs/publication/Q1_PAPER_PLAN.md`**: AMHP methods-paper IMRaD
  outline, target metrics, figure list, TRIPOD-AI / datasheet / model
  card supplementary plan, OSF pre-registration commitment.
- **`cgem_ext/`**: Python package skeleton with subpackages
  `data/`, `ood/`, `surrogate/`, `sensitivity/`, `api/`. Each has a
  docstring describing its phase deliverables.
- **`cgem_ext/__init__.py`** re-exports `run_cgem_for_profile` and
  `PilotConfig` from the upstream wrapper so consumers can use one
  stable import path. The original `from cgem_wrapper import ...`
  path used by `pulse-sim`'s CGEM bridge is preserved verbatim.
- **`pyproject.toml`**: modern Python packaging declaring the
  `cgem-ext` package, optional-dependency extras (`ml`, `api`, `dev`),
  and configuration for `ruff`, `mypy`, and `pytest`.
- **`tests/test_contract.py`**: regression test that enforces the
  pulse-sim consumer contract — imports, function signature,
  `PilotConfig(who_profile=int)` keyword, and the `CGEMResult`
  attribute set the bridge reads. Static checks always run; the
  binary-execution check skips when the compiled `cgem` is absent.
- **`tests/conftest.py`**: shared import-path setup and
  `cgem_binary_available` fixture.
- **`.github/workflows/ci.yml`**: GitHub Actions matrix running
  `pytest` (Python 3.10/3.11/3.12), `ruff`, `mypy`, plus a dedicated
  `pulse-sim-contract` job that runs the contract test in isolation.
- **`legacy/streamlit/`**: the Streamlit demos retain their behaviour
  but are now explicitly deprecated. `legacy/streamlit/README.md`
  documents the rationale and how to keep running them.

### Changed (Phase 0)

- **`requirements.txt`**: uncommented `scikit-learn` and `xgboost`,
  and added `optuna`, `shap`, `SALib`, `mlflow`, `fastapi`, `uvicorn`,
  `pydantic`, `structlog`, `prometheus-client`, `pytest`, `pytest-cov`,
  `ruff`, `mypy`, and `pyarrow`. The new ML and API dependencies are
  authoritative in `pyproject.toml` `[project.optional-dependencies]`;
  `requirements.txt` is the union for `pip install -r` flows.
- **`README.md`**: replaced the Streamlit-first highlights with the
  new ML / FastAPI / React architecture, added a roadmap pointer,
  updated Quick Start to install via `pip install -e .[ml,api,dev]`,
  pointed the legacy Streamlit instructions at `legacy/streamlit/`.
- **Streamlit apps moved to `legacy/streamlit/`** (preserves git
  history via `git mv`):
  - `app.py` → `legacy/streamlit/app.py`
  - `enhanced_app.py` → `legacy/streamlit/enhanced_app.py`
  - `i18n.py` → `legacy/streamlit/i18n.py`
  - `data/pilot_survey.db` → `legacy/streamlit/data/pilot_survey.db`
- **Dockerfile in README**: updated to invoke the legacy Streamlit
  app from its new path; the canonical container image once Phase 5
  lands will live at `cgem_ext/api/Dockerfile`.

### Preserved (no change — important)

- `src/cgem.f` and the compiled binaries (`cgem`, `cgem.exe`).
- `cgem_wrapper.py` public surface: `run_cgem_for_profile`,
  `PilotConfig`, `CGEMResult` (all attributes pulse-sim depends on).
- The `aerobatic_profiles`, `maneuvers_catalog`, and `run_cgem_batch`
  modules.
- The Vite + React TypeScript frontend in `frontend/` (its
  `mockData.ts` keeps the demo running until Phase 6 wires it to the
  FastAPI backend).

### Original [Unreleased] section follows below

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
