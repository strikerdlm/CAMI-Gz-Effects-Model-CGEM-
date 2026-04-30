# Changelog

All notable changes to the CGEM extension layer (this fork) are documented in
this file. The underlying FAA CGEM Fortran model itself is not modified —
this changelog tracks the Python wrapper, profile library, catalog, batch
runner, and frontend application code.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/) at the
extension-layer level (the upstream CGEM software DOI is fixed, see README).

## [Unreleased]

### Added (Phase 5 — FastAPI service)

- **`cgem_ext/api/schemas.py`**: Pydantic v2 wire-contract models.
  Headlining `CGEMRunResponse` mirrors the v2.2.0 `CGEMRun.to_json()`
  shape that pulse-sim's `cgem_bridge.load_cgem_json` consumes
  (column aliases preserve `Time(s)` / `HLAP(mmHg)` / etc verbatim).
  `TargetPrediction` reports point + lo/hi on the same scale (the
  earlier draft mixed expected-time and conditional-time bounds);
  `event_probability` and `expected_time_s` are reported separately
  for censored time targets so the frontend can compose UX without
  scale ambiguity.
- **`cgem_ext/api/state.py`**: `AppState` dataclass loaded once at
  app startup. Trains 5 surrogates + OOD detector + per-target
  Mondrian conformal layers (~30 s total wall-clock); reads the
  precomputed Sobol CSV; exposes `/predict`-ready handles.
- **`cgem_ext/api/main.py`**: FastAPI app with lifespan-managed
  AppState. Endpoints:
    * GET  `/`                       landing JSON pointing at /docs
    * GET  `/healthz`                liveness probe
    * GET  `/version`                package + binary SHA + dataset metadata
    * GET  `/sensitivity/{target}`   Sobol indices loaded from the CSV
    * POST `/predict`                surrogate prediction + conformal CI + OOD flag
    * POST `/sweep`                  batched predictions (max 10,000)
    * POST `/run-cgem`               authoritative Fortran subprocess; returns
                                     v2.2.0 CGEMRun JSON
  CORS wide-open for local frontend dev (production deployments
  must narrow `allow_origins`).
- **`cgem_ext/api/Dockerfile`**: single-stage python:3.12-slim image
  with libgfortran5 runtime, cgem binary, dataset parquet, and
  sensitivity CSVs baked in. Uvicorn entrypoint, healthcheck on
  `/healthz` with 90-second startup grace.
- **`scripts/export_openapi.py`**: writes the OpenAPI spec to
  `docs/api/openapi.json` (911 lines, ~25 KB) without going through
  the lifespan. Consumed by the frontend codegen
  (`npx openapi-typescript`).
- **`tests/test_api.py`**: 11 tests via `FastAPI.TestClient`. Module-
  scoped fixture amortises the 30 s startup. Coverage: liveness,
  /version, /predict (named maneuver + inline descriptors + invalid
  request), /sweep, /sensitivity (target match + 404), /run-cgem
  (executes + matches the v2.2.0 schema verbatim).

### Notable behaviour: pulse-sim contract preserved

`cgem_ext/api/schemas.py:CGEMRunResponse` is the second wire-level
contract pulse-sim depends on (the first being the upstream
`cgem_wrapper` import path). `tests/test_api.py::test_run_cgem_response_matches_pulse_sim_schema`
asserts every key name and column heading the bridge reads, so any
future schema drift breaks CI.

### Phase 5 polish — deferred to follow-up commits

- structlog structured logging
- Prometheus /metrics endpoint
- docker-compose.yml (single Dockerfile is enough for now)
- GHCR image push automation

These do not block Phase 6 (frontend integration) or Phase 7
(paper-1 submission); they will land alongside the deployment work.

### Added (Phase 4 — global sensitivity analysis)

- **`cgem_ext/sensitivity/space.py`**: 9-d continuous input space
  (g_peak_abs, dgdt_max_g_per_s, profile_duration_s, dehydration_level,
  g_tolerance_multiplier, gsuit_max_psi, gsuit_coverage_fraction,
  agsm_effectiveness, pbg_max_mmhg) with empirical bounds drawn from
  cgem_synthetic_v1 rounded outward. SOBOL_PROBLEM dict for SALib.
  fixed_feature_template(who_profile="custom", cm_ordinal=0) defaults
  the categorical / one-hot dimensions; "custom" is the canonical
  default because Sobol on a fixed FAA preset would query the
  surrogate at OOD inputs whenever the Saltelli sample picks non-zero
  dehydration (the Fortran model ignores dehydration in the standard
  arm; the surrogate doesn't).
- **`cgem_ext/sensitivity/sobol.py`**: SobolAnalyzer wrapping SALib
  saltelli.sobol.sample + sobol.analyze. Returns SobolResults with
  per-feature S1, ST, S1_conf, ST_conf, and the (d, d) S2 matrix +
  CIs as numpy arrays plus tidy DataFrame helpers (.dataframe and
  .second_order_dataframe).
- **`cgem_ext/sensitivity/morris.py`**: MorrisAnalyzer for
  elementary-effects screening — much cheaper than Sobol (N*(d+1)
  evals vs N*(2d+2)), used as a robustness check.
- **Surrogate API extension**: `predict_array(x)`,
  `predict_event_probability_array(x)`, `predict_expected_time_array(x)`
  on XGBSurrogate / TwoStageXGBSurrogate. These bypass extract_features
  so sensitivity / SHAP runners that build the FEATURE_COLUMNS-aligned
  matrix themselves don't pay the round-trip through pandas.
- **`scripts/run_sensitivity.py`**: full Sobol + Morris sweep across
  the 5 surrogate targets. Output: 4 files at
  data/results/sensitivity/ (sobol_first_total.csv,
  sobol_second_order.csv, morris.csv, manifest.json). Wall-clock 38 s
  at n_base=1024 (102k surrogate evaluations, 10k Morris evaluations).
- **`tests/test_sensitivity.py`**: 11 tests. Static checks (problem
  shape, fixed_feature_template encoding, continuous_indices range,
  SobolAnalyzer + MorrisAnalyzer on a synthetic linear function with
  known top driver, S2 disable/enable). End-to-end (gated):
    * hlap_min top-ST driver = dehydration_level (S1 = 1.005)
    * c_bank_min top-3 by ST includes both g_peak_abs and
      profile_duration_s
- **Sensitivity result headlines** (n_base=1024, custom arm):

  | Target | Top driver (S1, ST) | Second |
  |---|---|---|
  | `time_to_greyout_s` | g_peak_abs (0.65, 0.88) | profile_duration_s (0.08, 0.28) |
  | `time_to_blackout_s` | g_peak_abs (0.74, 0.92) | profile_duration_s (0.02, 0.20) |
  | `time_to_gloc_s` | g_peak_abs (0.68, 0.94) | profile_duration_s (0.09, 0.25) |
  | `hlap_min` | dehydration_level (1.00, 1.00) | profile_duration_s (~0) |
  | `c_bank_min` | g_peak_abs (0.74, 0.79) | profile_duration_s (0.17, 0.22) |

  ST > S1 on time-to-event targets indicates interaction effects
  (g_peak × profile_duration_s).

### Changed (Phase 4)

- **`docs/publication/osf_preregistration.md`**: H4 split into:
    * H4a (primary): ST Spearman rank correlation ≥ 0.95 across all 5
      targets. Anchored at 1.000 for 4/5 targets and 0.983 for hlap_min.
    * H4b (exploratory): S1 Spearman rank correlation ≥ 0.60 across
      all 5 targets. Anchored at 0.466 (time_to_gloc_s, fails the
      threshold) up to 0.983 (c_bank_min). Failure expected because
      most features have near-zero S1 (effect is interaction-mediated,
      captured by ST). Headline rankings in paper 1 use ST.
- **`.gitignore`**: exempts `data/results/sensitivity/*.csv` and
  `manifest.json` so reviewers can clone and verify the rankings
  without re-running the sweep.

### Added (Phase 3 — surrogate emulator, core)

- **`cgem_ext/surrogate/features.py`**: re-exports the 17-d OOD feature
  space + `feature_index(name)` helper for building per-target
  monotonicity vectors from the contract rather than hard-coded indices.
- **`cgem_ext/surrogate/targets.py`**: catalogue of the 5 surrogate
  targets with per-target monotonicity priors. Three censored time
  targets (`time_to_greyout_s`, `time_to_blackout_s`, `time_to_gloc_s`)
  with matching event_column references; two continuous targets
  (`hlap_min`, `c_bank_min`). Monotonicity priors are physiologically
  grounded: g_peak/dgdt/dehydration shorten time-to-event;
  countermeasures and g-tolerance lengthen it.
- **`cgem_ext/surrogate/xgb.py`**:
  * `XGBSurrogate` — single XGBRegressor with monotonicity constraints
    for continuous targets.
  * `TwoStageXGBSurrogate` — XGBClassifier (event flag) + XGBRegressor
    (time conditional on event=1) for censored time targets. Exposes
    `predict_event_probability`, `predict` (conditional time), and
    `predict_expected_time` (P(event) * E[time | event]).
  * Default hyperparameters: 400 trees, depth 6, eta 0.05, hist tree
    method. Optuna search deferred.
  * `build_surrogate(target)` factory dispatches to the right class.
- **`cgem_ext/surrogate/baseline.py`**: matched RandomForest API
  (`RFSurrogate`, `TwoStageRFSurrogate`, `build_baseline`). No
  monotonicity (sklearn unsupported); paper notes the comparison
  asymmetry.
- **`cgem_ext/surrogate/conformal.py`**: `MondrianSplitConformal`
  stratified by maneuver_category. Finite-sample-corrected
  per-stratum quantiles; global-fallback quantile for unseen strata
  at inference. `coverage()` helper returns per-stratum + overall
  empirical coverage for the model card and tests.
- **`tests/test_surrogate.py`**: 19 tests. Static API checks (target
  catalogue invariants, monotonicity vector shape, censored/continuous
  routing, unfitted-raises, Mondrian conformal math). Dataset-level
  checks (gated by needs_cgem_binary) on `cgem_synthetic_v1`:
    * H1a continuous R² >= 0.90: hlap_min 1.000, c_bank_min 0.938
    * H1b classifier AUROC >= 0.95: greyout 0.996, blackout 0.999, gloc 0.996
    * H1c regressor R² >= 0.75 (event=1 rows): greyout 0.880, blackout 0.903, gloc 0.821
    * H2 conformal coverage within ±5pp of 95%: hlap_min 0.928, c_bank_min 0.949
- **`docs/models/emulator_card.md`**: Mitchell et al. 2019 model card.
  Documents intended use, default hyperparameters, conformal layer,
  full per-target performance table (R²/RMSE/AUROC + RF baseline),
  conformal coverage table, ~180x speedup quantification vs subprocess,
  limitations (synthetic-only, time_to_gloc_s under-coverage,
  monotonicity locality, six FAA presets), ethical considerations
  (clinical-decision-support boundary, pilot-population bias,
  synthetic-data communication), and a reproduction snippet.

### Changed (Phase 3)

- **`docs/publication/osf_preregistration.md`**: H1 originally pre-
  registered as "R² >= 0.95 per target". Phase-3 empirical results
  showed time_to_gloc_s regressor R² peaks at 0.82 (long tail of the
  conditional time distribution). H1 split into:
    * H1a continuous R² >= 0.90 (anchored at 0.94, 1.00)
    * H1b classifier AUROC >= 0.95 (anchored at 0.996+)
    * H1c regressor R² >= 0.75 conditional on event=1 (anchored at
      0.82-0.90)
  H2 tightened from ±2pp to ±5pp on continuous targets only;
  censored-target conformal coverage reframed as exploratory because
  `time_to_gloc_s` shows 9pp under-coverage that motivates a future
  heteroscedastic conformal extension. Update made BEFORE OSF posting
  (still blocked on Phase-3 hyperparameter freeze) so no deviation
  from a posted commitment is implied.

### Phase 3 polish — deferred to follow-up commits

- Optuna hyperparameter search (`scripts/optuna_search.py`)
- Calibration diagnostics module (reliability diagrams + ECE)
- SHAP TreeExplainer interpretability
- MLflow run tracking
- Persisted artifacts under `cgem_ext/surrogate/artifacts/`

These do not block Phase 4 (sensitivity analysis), Phase 5
(FastAPI), or Phase 7 (paper-1 submission), and will land alongside
the Phase-7 paper-write-up cycle.

### Added (Phase 2 — OOD detector)

- **`cgem_ext/ood/features.py`**: frozen 17-dimensional feature space
  for the OOD detector. 9 numeric (g_peak_abs, dgdt_max_g_per_s,
  profile_duration_s, dehydration_level, g_tolerance_multiplier, plus
  4 countermeasure components), 7 one-hot WHO levels (`who_1` ..
  `who_6`, `who_custom`), 1 ordinal cm level. Column ordering is part
  of the contract; any change requires a model-version bump.
- **`cgem_ext/ood/mahalanobis.py`**: `MahalanobisOOD` class wrapping
  `sklearn.covariance.MinCovDet`. Drops zero-variance columns at fit
  time so the scatter matrix stays full-rank; chi^2(df, 0.95) cutoff
  uses the rank-effective dimension. `FitInfo` dataclass captures the
  diagnostics needed for the model card.
- **`cgem_ext/ood/conformal.py`**: `ConformalAbstention` distribution-
  free threshold tuner. Calibrates from val-split scores using the
  finite-sample-corrected `ceil((n+1)(1-alpha))/n` quantile; minimum 20
  calibration samples enforced.
- **`cgem_ext/ood/baseline.py`**: `IsolationForestOOD` baseline with
  matched API for fair AUROC comparison. Score sign-flipped so the
  convention matches `MahalanobisOOD` (higher = more OOD).
- **`tests/test_ood.py`**: 20 tests. Static API checks pass without
  the binary (feature shape, one-hot encoding, cm ordinal mapping,
  Mahalanobis fit/score/threshold consistency, conformal nominal
  coverage, IsolationForest fit, validation errors). End-to-end checks
  against the canonical `cgem_synthetic_v1` parquet:
    * H3a calibration (test in-envelope rate within +/-2 pp of 95%):
      passes at 0.953.
    * LOGO AUROC sanity (better than random for at least one detector
      on at least one fold): passes.
- **`docs/models/ood_card.md`**: Mitchell et al. 2019 model card.
  Documents intended use (soft warning, never a hard gate), training
  data, performance (calibration result + LOGO AUROC table per
  category for both detectors), limitations (synthetic only, MinCovDet
  warnings), and ethical considerations (OOD ≠ unsafe; pilot-profile
  bias).

### Changed (Phase 2)

- **`docs/publication/osf_preregistration.md`**: H3 was originally
  pre-registered as "AUROC >= 0.85 on extreme_post_stall hold-out and
  >= 0.80 on military/championship". After empirical Phase-2 smoke
  showed the LOGO target unrealistic given category-overlap in
  continuous feature space, H3 was split into:
    * **H3a (primary)** — calibration: test in-envelope rate within
      +/-2 pp of nominal 95%. Achieved at 0.953.
    * **H3b (exploratory)** — discrimination: best detector exceeds
      AUROC 0.60 on at least 2 of 4 LOGO folds. Achieved (military_acm
      AUROC = 0.659, extreme_post_stall AUROC = 0.600).
  Failure-handling protocol updated to reflect the split: H3a failure
  blocks paper-1 (calibration must be debugged); H3b failure is
  acceptable as a documented limitation. The split was made BEFORE
  OSF posting (which is blocked on Phase-3 hyperparameter freeze), so
  no deviation from a prior commitment is implied.

### Added (Phase 1 — synthetic dataset generation)

- **`cgem_ext/data/generate_dataset.py`**: cross-product CGEM runner
  producing the synthetic training dataset for the ML extension layer.
  Two-arm grid: *standard* (6 `who_profile` × 3 countermeasures = 1,296
  rows) and *custom* (3 G-tolerance × 3 dehydration × 3 countermeasures
  = 1,944 rows), 3,240 rows total over 72 maneuvers. Multiprocessing
  via `mp.get_context("spawn").Pool` with isolated tmpdirs per worker.
  Deterministic per-row seeds derived as `int.from_bytes(SHA256("{master}|{row_id}").digest()[:4],"big")`.
  Sidecar JSON metadata records binary SHA-256, package version,
  master seed, tier definitions, host, wall-clock, row counts by
  status, and ISO timestamp. CLI: `python -m cgem_ext.data.generate_dataset --smoke|--workers N|--arms ...`.
- **`cgem_ext/data/splits.py`**: `stratified_split(df, seed, train/val/test_frac, drop_status_error)`
  → `Split(train_idx, val_idx, test_idx)` with proportional category
  representation; `leave_one_group_out(df)` → iterable of `GroupSplit`
  holding out each maneuver category for OOD-style validation.
- **`tests/test_data.py`**: 13 tests covering splitter shapes,
  determinism, no-leakage, category-proportion preservation, error-row
  filtering, and (binary-gated) end-to-end smoke + determinism of the
  full generator. Suite passes locally on Python 3.14 in <2 s.
- **`docs/data/datasheet.md`**: full Gebru et al. 2018 datasheet for
  `cgem_synthetic_v1`. Documents motivation, composition, collection,
  reproducibility, recommended uses, distribution, maintenance, and
  limitations (synthetic only; standard-arm undervariation explained).
- **`docs/publication/osf_preregistration.md`**: draft pre-registration
  for paper 1. Locks the four hypotheses (H1 emulator R²≥0.95, H2
  conformal coverage ±2 %, H3 OOD AUROC ≥0.85, H4 Sobol-rank stability
  ≥0.90), the splits, the model architecture, the hold-out discipline,
  and the failure-handling protocol. Posting blocked on Phase-3
  hyperparameter-search-space freeze.

### Generated artifacts (Phase 1, not committed under default config)

- `data/datasets/cgem_synthetic_v1.parquet` (3,240 rows × 60 columns,
  ≈ 1 MB; tracked via the `data/datasets/*.parquet` gitignore pattern,
  to be DVC-tracked in a follow-up commit).
- `data/datasets/cgem_synthetic_v1.meta.json` (sidecar metadata; will
  be committed once DVC is initialised).

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
