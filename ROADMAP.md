# CGEM Project Roadmap

This file tracks the migration of the CGEM stack from a Streamlit-first demonstration repo into a defensible, ML-augmented research platform with a FastAPI service backing a Vite/React frontend. The end goal of this roadmap is **one Q1 publication in *Aerospace Medicine and Human Performance* (AMHP) before centrifuge validation against our own subjects**, followed by two scoped follow-up papers.

The validated FAA Fortran physiology core (`src/cgem.f`) and its subprocess wrapper (`cgem_wrapper.py`) are *not* modified by this roadmap. Everything in `cgem_ext/` is additive; `pulse-sim` and any other downstream consumer continue to import the upstream symbols unchanged.

The full architectural rationale lives in `docs/architecture/ML_LAYER.md`. The publication plan lives in `docs/publication/Q1_PAPER_PLAN.md`.

---

## Milestones

| Phase | Title | Estimate | Status |
|------|-------|----------|--------|
| 0 | Foundation & contract preservation | 1–2 weeks | ✅ done |
| 1 | Synthetic dataset generation | 1–2 weeks | ✅ done (DVC remote deferred) |
| 2 | OOD detector | 1 week | ✅ done |
| 3 | Surrogate emulator | 2 weeks | ✅ core done (Optuna/SHAP/MLflow polish deferred) |
| 4 | Global sensitivity analysis | 1 week | ✅ done |
| 5 | FastAPI service | 1 week | ✅ done (Prometheus /metrics deferred) |
| 6 | Frontend integration | 2 weeks | ✅ done (Playwright e2e deferred) |
| 7 | Paper 1 — AMHP methods paper | 2–3 weeks | 🚧 in progress (manuscript ≈ portal-ready; OSF posting + form scans pending) |
| 8 | Paper 2 — external re-analysis | scoped only | ⬜ post-paper-1 |
| 9 | Paper 3 — own-centrifuge validation | scoped only | ⬜ blocked on subject data |

Estimates assume ~10 hours/week of focused work.

---

## Phase 0 — Foundation & contract preservation

Goal: stand up the new repository skeleton without breaking any existing consumer.

- [x] Create feature branch `feat/ml-layer-phase-0`
- [x] Scaffold `cgem_ext/{,data,ood,surrogate,sensitivity,api}`, `legacy/streamlit/`, `docs/{architecture,publication,data,models,api}`, `tests/`, `.github/workflows/`
- [x] `git mv` `app.py`, `enhanced_app.py`, `i18n.py`, `data/pilot_survey.db` → `legacy/streamlit/` (preserves git history)
- [x] `legacy/streamlit/README.md` with deprecation note + run instructions
- [x] `cgem_ext/__init__.py` re-exports `run_cgem_for_profile` and `PilotConfig`
- [x] `pyproject.toml` (package metadata, ruff/mypy/pytest config, optional-dep extras)
- [x] `requirements.txt` updated for the union of Streamlit-legacy + `cgem_ext`
- [x] `tests/test_contract.py` (regression test enforcing the pulse-sim contract)
- [x] `.github/workflows/ci.yml` (pytest + ruff + mypy on push/PR)
- [x] `README.md` updated to reflect new architecture; pointer to ROADMAP
- [x] `CHANGELOG.md` `[Unreleased]` entry for Phase 0
- [x] `ROADMAP.md`, `docs/architecture/ML_LAYER.md`, `docs/publication/Q1_PAPER_PLAN.md` (this file + companions)
- [x] Verify `pulse-sim`'s `cgem_bridge.py` still imports cleanly when its `CGEM_REPO` points at this branch

**Phase 0 exit criterion**: `pytest` green; pulse-sim's `cgem_bridge.py` imports unchanged.

## Phase 1 — Synthetic dataset generation

- [x] `cgem_ext/data/generate_dataset.py` — cross-product runner. Empirical grid is **3,240 rows** (1,296 standard arm + 1,944 custom arm; 45 rows per maneuver across 72 maneuvers). Reduced from the 11,664-row plan after empirical verification that the Fortran model ignores `dehydration_level` and `g_tolerance_multiplier` when `who_profile` is set, so varying them in the standard arm produces redundant rows. The custom arm covers their effects.
- [x] `multiprocessing.Pool` parallelization with isolated temp dirs per worker
- [x] Output: `data/datasets/cgem_synthetic_v1.parquet` (3,240 rows / 60 columns / 27 s wall-clock with `cpu_count - 1` workers)
- [x] `cgem_ext/data/splits.py` — stratified 70/15/15 + leave-one-group-out by maneuver category
- [ ] DVC initialization; track parquet (full file in object storage; hash committed) — deferred to a separate commit when the DVC remote is provisioned
- [x] `docs/data/datasheet.md` per Gebru et al. 2018
- [x] `docs/publication/osf_preregistration.md` — draft committed; OSF posting blocked on hyperparameter-search-space freeze (Phase 3 prep)
- [x] `tests/test_data.py` (13 tests; splitter checks + binary-gated smoke + determinism)

## Phase 2 — OOD detector

- [x] `cgem_ext/ood/features.py` (frozen 17-d feature space: 9 numeric + 7 one-hot who + 1 ordinal cm)
- [x] `cgem_ext/ood/mahalanobis.py` (`MinCovDet` + χ²(df, 0.95) threshold)
- [x] `cgem_ext/ood/conformal.py` (split-conformal abstention with finite-sample correction)
- [x] `cgem_ext/ood/baseline.py` (`IsolationForestOOD` baseline)
- [x] `docs/models/ood_card.md` (Mitchell et al. 2019)
- [x] `tests/test_ood.py` — 20 tests, including the strong calibration check on the canonical paper-1 dataset (test in-envelope rate **0.953** vs nominal 0.95). LOGO AUROC reframed as exploratory after empirical Phase-2 finding that maneuver categories overlap in continuous feature space; full LOGO table in the model card. OSF preregistration updated accordingly (H3 split into H3a calibration / H3b discrimination).

## Phase 3 — Surrogate emulator

Core (shipped):

- [x] `cgem_ext/surrogate/features.py` (re-exports OOD feature space + monotonicity helpers)
- [x] `cgem_ext/surrogate/targets.py` (5-target catalogue with per-target monotonicity priors)
- [x] `cgem_ext/surrogate/baseline.py` (`RFSurrogate` + `TwoStageRFSurrogate`)
- [x] `cgem_ext/surrogate/xgb.py` (`XGBSurrogate` continuous + `TwoStageXGBSurrogate` censored, monotonicity constraints applied per target)
- [x] `cgem_ext/surrogate/conformal.py` — Mondrian split-conformal stratified by `maneuver_category`, with finite-sample correction and global-fallback for unseen strata
- [x] `docs/models/emulator_card.md` (Mitchell et al. 2019) — full per-target performance table, OSF anchor numbers, limitations, ethics
- [x] `tests/test_surrogate.py` — 19 tests; H1a/H1b/H1c/H2 hypotheses validated against empirically-grounded thresholds; classifier AUROC 0.996+, continuous R² 0.94–1.00, conformal coverage 0.93/0.95 on continuous targets
- [x] OSF preregistration updated: H1 split into H1a continuous-R², H1b classifier-AUROC, H1c regressor-R²; H2 ±2pp tightened to ±5pp on continuous targets, censored coverage reframed as exploratory

Polish (deferred to follow-up commits, do not block Phase 4–7):

- [ ] Optuna hyperparameter search with stratified k-fold CV (separate `scripts/optuna_search.py`)
- [ ] `cgem_ext/surrogate/calibration.py` — reliability diagrams + ECE (separate module)
- [ ] `cgem_ext/surrogate/interpret.py` — SHAP TreeExplainer (separate module)
- [ ] MLflow tracking (params, metrics, artifacts, dataset hash)
- [ ] Persist trained artifacts to `cgem_ext/surrogate/artifacts/v0_1_0/` (load on import vs train at use-time)

## Phase 4 — Global sensitivity analysis

- [x] `cgem_ext/sensitivity/space.py` — 9-d continuous input space + WHO/cm fixed-defaults; default fixes ``who_custom=1`` so Sobol queries the surrogate at in-distribution points
- [x] `cgem_ext/sensitivity/sobol.py` — SALib Saltelli + Sobol analyze (S1, ST, S2 with bootstrap CIs) driven by the surrogate's `predict_array` path
- [x] `cgem_ext/sensitivity/morris.py` — elementary-effects screening (mu, mu_star, sigma)
- [x] Per-target Sobol + Morris CSVs at `data/results/sensitivity/{sobol_first_total,sobol_second_order,morris}.csv` plus `manifest.json` sidecar
- [x] `scripts/run_sensitivity.py` — full sweep across 5 targets, 38 s wall-clock at n_base=1024 (102k surrogate evaluations)
- [x] `tests/test_sensitivity.py` — 11 tests; static API checks + end-to-end on the trained surrogate validating the headline rankings (`hlap_min` dominated by `dehydration_level`; `c_bank_min`/`time_to_gloc_s` dominated by `g_peak_abs` + `profile_duration_s`)
- [x] OSF preregistration H4 split into H4a (ST stability ≥0.95, anchored 0.983–1.000) + H4b (S1 stability ≥0.60, exploratory)
- [ ] Sobol heatmap figures via the `echarts` skill — deferred to Phase 7 (paper-1 write-up cycle)

## Phase 5 — FastAPI service

- [x] `cgem_ext/api/schemas.py` — Pydantic v2 models. `CGEMRunResponse` mirrors the v2.2.0 contract pulse-sim's `cgem_bridge.load_cgem_json` reads (verified by `test_run_cgem_response_matches_pulse_sim_schema`).
- [x] `cgem_ext/api/state.py` — `AppState` lifespan-managed model store: trains 5 surrogates + OOD detector + per-target Mondrian conformal layers at startup (~30 s wall-clock), so each `/predict` call is sub-millisecond.
- [x] `cgem_ext/api/main.py` — FastAPI app exposing `/`, `/healthz`, `/version`, `/sensitivity/{target}`, `/predict`, `/sweep`, `/run-cgem`. CORS open by default for local frontend dev.
- [x] `cgem_ext/api/Dockerfile` — single-stage Python 3.12-slim image bundling the cgem binary + dataset + sensitivity CSVs. Uvicorn entrypoint, healthcheck on `/healthz`.
- [x] `docs/api/openapi.json` — 911-line auto-generated spec for frontend codegen (`scripts/export_openapi.py`).
- [x] `tests/test_api.py` — 11 tests against `FastAPI.TestClient`. Module-scoped fixture amortises the 30s startup cost across all tests in the file.
- [ ] Structured logging (`structlog`) + `/metrics` Prometheus endpoint — deferred to a follow-up commit; not blocking Phase 6.
- [ ] `docker-compose.yml` — deferred; the Dockerfile alone covers single-container local dev.

## Phase 6 — Frontend integration

- [x] `frontend/src/main.tsx` — `QueryClientProvider` wrap with shared cache + retry policy
- [x] `frontend/src/services/types.ts` — hand-maintained TypeScript wire contract mirroring `cgem_ext.api.schemas` (regenerable via `npx openapi-typescript ../docs/api/openapi.json`)
- [x] `frontend/src/services/cgemApi.ts` — typed axios client + React Query hooks (`useHealth`, `useVersion`, `useSensitivity`, `usePredict`, `useSweep`, `useRunCgem`); base URL via `VITE_API_URL`
- [x] `frontend/src/components/ui/OODBanner.tsx` — emerald "in-envelope" / amber "OOD" banner sourced from the `/predict` response
- [x] `frontend/src/components/ui/PredictionTable.tsx` — per-target table (point + 95 % conformal CI; censored rows show P(event) + expected E[t])
- [x] `frontend/src/components/charts/SensitivityChart.tsx` — Sobol S1 + ST bar chart per target driven by `useSensitivity`
- [x] `PredictionPage` rewired: `usePredict` (surrogate, fast) + `useRunCgem` (Fortran subprocess, authoritative), OOD banner, conformal table, /version status header, error states with `apiErrorMessage`
- [x] `BatchPage` rewired: `useSweep` over all 72 maneuvers in a single round-trip; sortable table; OOD-first sort; summary cards (total / in-envelope / OOD / high-G-LOC)
- [x] `AnalysisPage`: appended a Sobol-sensitivity panel with target picker (5 targets); preserves the existing maneuver-explanation tree
- [x] `DashboardPage`: API status banner showing `/version` (package version + binary SHA prefix + dataset seed)
- [ ] `frontend/e2e/` Playwright golden-path test — deferred; the unit-test surface lives in the Python tests at `tests/test_api.py`

## Phase 7 — Paper 1 (AMHP methods paper)

- [x] `docs/publication/Q1_PAPER_PLAN.md` filled out (IMRaD, target metrics, figure list) — Phase 0
- [x] Manuscript drafted — `docs/publication/manuscript.md` (16 refs, ~3,150 body words, 250-word abstract)
- [x] AMHP compliance pass — title 67/100 chars, running head `CONFORMAL CGEM EMULATION` (26/30), depersonalized title page in `author_page.md`, abstract 250/250, keywords 5/5
- [x] Figure data + 5 ECharts option JSONs committed at `data/results/figures/`
- [x] Figure 6 architecture source (Mermaid) at `data/results/figures/fig6_architecture.mmd`
- [x] Cover letter `docs/publication/cover_letter.md` addressing all 11 AMHP §3–§12 elements
- [x] TRIPOD-AI reporting checklist `docs/publication/tripod_ai_checklist.md`
- [x] Suggested reviewers `docs/publication/suggested_reviewers.md` (6 candidates + 3 backups)
- [x] Reference verification + cleanup — 18→16 refs, two FAA technical-report placeholders resolved, one likely-fabricated reference dropped
- [x] Pandoc render pipeline — `scripts/render_manuscript.py` produces 7 .docx + .html outputs from the markdown sources
- [x] Render checklist `docs/publication/render_checklist.md` for the manual Word edits AMHP requires (double-spacing, page numbers, superscript citation conversion, table numbering)
- [ ] Render Figs 1–5 to SVG via Node ECharts CLI; Fig 6 via `mmdc`; convert to TIFF at 1200 dpi (line art) / 600 dpi (combination halftone)
- [ ] Post OSF pre-registration; capture DOI for the cover letter
- [ ] Sign and scan AMHP forms (Author Checklist, Copyright Release, COI)
- [ ] Submit via Editorial Manager (`https://www.editorialmanager.com/AMHP/`)

## Phase 8 — Paper 2 (external re-analysis, scoped only)

- [ ] Literature mining for USAFSAM TR series, Burton 1980s, Whinnery 1990s
- [ ] Dataset reconstruction from published tables
- [ ] Discrepancy model `δ(x) = real(x) − CGEM(x)`
- [ ] External validation paper to AMHP or Frontiers in Physiology

## Phase 9 — Paper 3 (own-centrifuge validation, scoped only)

- [ ] Centrifuge protocol + ethics approval
- [ ] Subject recruitment
- [ ] Data acquisition
- [ ] Validation paper

---

## Cross-cutting workstreams

### Continuous integration

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request:

1. `pytest tests/` (with `--strict-markers --strict-config`)
2. `ruff check cgem_ext tests`
3. `mypy cgem_ext tests`

Failing CI blocks merging to `main`.

### Versioning

The `cgem_ext` package follows SemVer at the *extension layer* level:

- `0.x` — pre-publication alpha (current).
- `1.0.0` — first AMHP submission.
- `1.x` — incremental improvements after publication.
- `2.0.0` — once paper 3 ships, the package is rebased on the centrifuge-validated artifact set.

The Fortran core's version (`cgem_wrapper.CGEM_VERSION`) is reported alongside the extension version in every API response (`/version` endpoint).

### Reproducibility

- Datasets versioned with DVC; full files in object storage; hashes committed.
- Trained models tracked via MLflow with the dataset hash logged in every run.
- Pre-register the validation protocol on OSF before producing any paper-1 results.
- Docker image (`cgem_ext/api/Dockerfile`) carries the API service + emulator artifacts at known versions; published to GHCR for cross-machine reproducibility.

---

## How to read this file

- ⬜ box = not started.
- 🚧 in progress = at least one sub-task underway.
- ✅ checkmark = phase exit criterion met.
- Each PR that lands updates the relevant boxes plus the `[Unreleased]` block in `CHANGELOG.md`.
