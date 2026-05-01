# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

ML-augmented research platform built on the FAA CAMI G-Effects Model (CGEM). The validated FAA Fortran physiology core in `src/cgem.f` and the `cgem` / `cgem.exe` binary at the repo root are the authoritative model. Everything under `cgem_ext/` is an **additive** Python layer — surrogate emulator, OOD detector, global sensitivity analysis, FastAPI service. The Vite/React frontend in `frontend/` consumes the API exclusively.

The publication target is *Aerospace Medicine and Human Performance* (AMHP); see `ROADMAP.md` and `docs/publication/` for the pre-registration and paper plan.

## Two contracts that must NEVER break

1. **Python contract** — `cgem_wrapper.run_cgem_for_profile` and `cgem_wrapper.PilotConfig` are re-exported from `cgem_ext` and consumed downstream by `pulse-sim`'s `cgem_bridge.py`. Re-exports live in `cgem_ext/__init__.py`. Enforced by `tests/test_contract.py`.
2. **JSON contract** — `POST /run-cgem` returns the v2.2.0 `CGEMRun` JSON shape that `pulse-sim` parses. Enforced by `tests/test_api.py`.

CI has a dedicated `pulse-sim-contract` job (`.github/workflows/ci.yml`) that runs `tests/test_contract.py` after the matrix. Do not change the public shape of these symbols, do not modify `src/cgem.f`, and do not touch `cgem_wrapper.py`'s `run_cgem_for_profile` / `PilotConfig` signatures without updating the contract tests deliberately.

## Architecture in one paragraph

`cgem_wrapper.py` shells out to the compiled Fortran binary in an isolated tmpdir per call (input: an EGP profile + `gloc_inp.dat`; output: parsed time series + event flags). `cgem_ext/data/generate_dataset.py` drives this in parallel across 72 maneuvers × pilot configs to produce `data/datasets/cgem_synthetic_v1.parquet` (3,240 rows, seed 42, SHA logged in the `.meta.json` sidecar). On top of that frozen dataset: `cgem_ext/ood/` (Mahalanobis + split-conformal abstention over a frozen 17-d feature space), `cgem_ext/surrogate/` (XGBoost regressors + two-stage censored classifier/regressor with per-target monotonicity priors and Mondrian conformal CIs stratified by `maneuver_category`), and `cgem_ext/sensitivity/` (SALib Sobol + Morris driven by the surrogate, ~38 s for 102k evaluations vs days via direct subprocess). `cgem_ext/api/main.py` builds and trains all of the above in a FastAPI lifespan handler at startup (~30 s) and exposes 7 endpoints (`/`, `/healthz`, `/version`, `/sensitivity/{target}`, `/predict`, `/sweep`, `/run-cgem`).

`legacy/streamlit/` holds deprecated Streamlit demos that still run but are not on the publication path.

The maneuver library (72 profiles, 4 categories) lives in `maneuvers_catalog.py`. Raw aerobatic input files are in `Aerobatics_sample_inputs/`.

## Common commands

```bash
# Setup (Linux requires the Fortran runtime for the binary)
sudo apt-get install -y libgfortran5
python -m venv .venv && source .venv/bin/activate
pip install -e .[ml,api,dev]

# Test suite (~16 s locally; CI matrix on 3.10/3.11/3.12)
pytest tests/ -v
pytest -m "not needs_cgem_binary" -v   # what CI runs (matches GitHub Actions)
pytest tests/test_surrogate.py::TestXGBSurrogate -v   # single test class
pytest tests/test_contract.py -v        # the contract gate, no extras needed

# Lint + type-check (must pass before push; CI gates on these)
ruff check cgem_ext tests
mypy cgem_ext tests

# FastAPI service (lifespan trains everything on first boot, ~30 s)
uvicorn cgem_ext.api.main:app --reload   # http://localhost:8000/docs

# Re-export the OpenAPI spec after any schema change in cgem_ext/api/schemas.py
python -m scripts.export_openapi         # writes docs/api/openapi.json

# Regenerate Sobol + Morris CSVs (drives the surrogate, not the Fortran)
python -m scripts.run_sensitivity        # writes data/results/sensitivity/

# Frontend (talks to the FastAPI service; set VITE_API_URL if not localhost:8000)
cd frontend && npm install && npm run dev    # http://localhost:5173
npm run lint                                  # ESLint
npm run type-check                            # tsc --noEmit
npm run build                                 # tsc -b && vite build

# One-shot CGEM call
python -c "from cgem_wrapper import run_cgem_for_profile; print(run_cgem_for_profile('hammerhead'))"

# Whole-catalogue batch
python run_cgem_batch.py --maneuvers all --who all --configs all
```

## Tooling configuration that affects edits

- **`pyproject.toml`**: ruff and mypy both **exclude** `legacy/`, `frontend/`, `src/` (Fortran), `tmp_run*`. `cgem_wrapper`, `aerobatic_profiles`, `maneuvers_catalog` are mypy `ignore_missing_imports`. The package layout is `cgem_ext*` only — anything else is intentionally out of the wheel.
- **`pytest`**: two custom markers — `slow` and `needs_cgem_binary`. CI runs `-m "not needs_cgem_binary"`. Tests gated by the marker need the compiled binary at the repo root and `libgfortran5` installed.
- **`tests/conftest.py`** prepends the repo root to `sys.path` so tests import `cgem_wrapper`, `aerobatic_profiles`, and `cgem_ext` without an editable install. The `cgem_binary_available` fixture reports whether the gated tests can run.
- **Frontend lives in its own npm workspace** under `frontend/` (React 19 + Vite 7 + TS 5.9 + ECharts 5.6, Tailwind v4). The root `package.json` only carries citation-verification helpers and is not the frontend's package.

## Where things live

- Authoritative model: `src/cgem.f`, compiled to `cgem` (POSIX) / `cgem.exe` (Windows), driven by `gloc_inp.dat` template + per-run EGP profile.
- Subprocess wrapper + result dataclasses (`CGEMResult`, `PilotConfig`): `cgem_wrapper.py`.
- Frozen dataset: `data/datasets/cgem_synthetic_v1.parquet` + `.meta.json` (binary SHA + seed).
- Pre-registration / publication: `docs/publication/`. Model cards: `docs/models/`. Datasheet: `docs/data/`. Architecture rationale: `docs/architecture/ML_LAYER.md`.
- Sensitivity outputs (paper-1 supplementary): `data/results/sensitivity/`.
- OpenAPI spec for frontend codegen: `docs/api/openapi.json` (regenerate via `scripts/export_openapi.py`).

## Caveats baked into the model

- CGEM models **±Gz only**. Lateral (Gy) and longitudinal (Gx) loads from flat spins / tumbling maneuvers are not represented.
- Validation ceiling is ~10 G/s onset. Snap rolls, Cobra-class spikes, and Lomcovák tumbles encode 30–60 G/s — those rows are extrapolation, not prediction.
- The Fortran model **ignores `dehydration_level` and `g_tolerance_multiplier` when `who_profile` is set**. The dataset's "custom" arm is what exercises those parameters; varying them in the standard arm just produces redundant rows.

## Operational rules for this repo

- Do not modify `src/cgem.f`, the compiled binaries, or `gloc_inp.dat` semantics.
- Do not change the wire shape of `cgem_ext.api.schemas.CGEMRunResponse` / `CGEMRunData` or the public surface of `run_cgem_for_profile` / `PilotConfig` without updating the contract tests in the same PR.
- After any change to `cgem_ext/api/schemas.py`, regenerate `docs/api/openapi.json` so the frontend types stay in sync.
- When adding a new MCP server or settings tweak at the *user* level, remember Diego's environment requires `/root/.claude/mcp.json` and `/root/.claude/settings.json` to stay synchronized — see `/root/CLAUDE.md` for the broader environment notes that apply across all his repos.
