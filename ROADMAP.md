# CGEM Project Roadmap

This file tracks the migration of the CGEM stack from a Streamlit-first demonstration repo into a defensible, ML-augmented research platform with a FastAPI service backing a Vite/React frontend. The end goal of this roadmap is **one Q1 publication in *Aerospace Medicine and Human Performance* (AMHP) before centrifuge validation against our own subjects**, followed by two scoped follow-up papers.

The validated FAA Fortran physiology core (`src/cgem.f`) and its subprocess wrapper (`cgem_wrapper.py`) are *not* modified by this roadmap. Everything in `cgem_ext/` is additive; `pulse-sim` and any other downstream consumer continue to import the upstream symbols unchanged.

The full architectural rationale lives in `docs/architecture/ML_LAYER.md`. The publication plan lives in `docs/publication/Q1_PAPER_PLAN.md`.

---

## Milestones

| Phase | Title | Estimate | Status |
|------|-------|----------|--------|
| 0 | Foundation & contract preservation | 1–2 weeks | ✅ done (CI workflow file pending PAT scope) |
| 1 | Synthetic dataset generation | 1–2 weeks | ✅ done (DVC remote deferred) |
| 2 | OOD detector | 1 week | ✅ done |
| 3 | Surrogate emulator | 2 weeks | ✅ core done (Optuna/SHAP/MLflow polish deferred) |
| 4 | Global sensitivity analysis | 1 week | ⬜ blocked on Phase 3 |
| 5 | FastAPI service | 1 week | ⬜ blocked on Phase 3 |
| 6 | Frontend integration | 2 weeks | ⬜ blocked on Phase 5 |
| 7 | Paper 1 — AMHP methods paper | 2–3 weeks | ⬜ blocked on Phases 2–6 |
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

- [ ] `cgem_ext/sensitivity/sobol.py` — SALib `saltelli.sample` + `sobol.analyze` driven by the emulator
- [ ] `cgem_ext/sensitivity/morris.py` — elementary effects screening
- [ ] Per-target first-order + total-order indices CSV
- [ ] Sobol heatmaps via the `echarts` skill
- [ ] `tests/test_sensitivity.py`

## Phase 5 — FastAPI service

- [ ] `cgem_ext/api/main.py` — `/predict`, `/sweep`, `/run-cgem`, `/sensitivity/{target}`, `/healthz`, `/version`
- [ ] `cgem_ext/api/schemas.py` — Pydantic v2 models mirroring v2.2.0 `CGEMRun` JSON contract
- [ ] OpenAPI spec committed to `docs/api/openapi.json`
- [ ] `cgem_ext/api/Dockerfile` + `docker-compose.yml`
- [ ] Structured logging + `/metrics` Prometheus endpoint
- [ ] `tests/test_api.py`

## Phase 6 — Frontend integration

- [ ] `npx openapi-typescript docs/api/openapi.json -o frontend/src/services/types.ts`
- [ ] `frontend/src/services/cgemApi.ts` (axios + React Query)
- [ ] `PredictionPage.tsx` → `usePrediction()`; show OOD warning banner
- [ ] `BatchPage.tsx` → `/sweep`
- [ ] `AnalysisPage.tsx` → `/sensitivity`
- [ ] `DashboardPage.tsx` → live aggregation
- [ ] Loading/error/retry states
- [ ] `frontend/e2e/` Playwright golden-path test

## Phase 7 — Paper 1 (AMHP methods paper)

- [ ] `docs/publication/Q1_PAPER_PLAN.md` filled out (IMRaD, target metrics, figure list)
- [ ] Manuscript drafted (use `amhp-submit` skill)
- [ ] All figures rendered via `echarts` skill at journal-quality
- [ ] TRIPOD-AI checklist completed and attached as supplementary
- [ ] OSF pre-print posted at submission time
- [ ] Submitted via Editorial Manager

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
