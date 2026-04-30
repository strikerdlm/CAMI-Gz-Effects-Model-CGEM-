# `cgem_ext` — ML Extension Layer Architecture

## Why this layer exists

The CAMI G-Effects Model is implemented in Fortran (`src/cgem.f`, 1,729 LOC) and distributed as a compiled binary (`cgem`, `cgem.exe`) that the FAA validates against archival centrifuge data. **That validation is a property of the artifact, not of the equations on paper.** Re-implementing CGEM in Python — or rewriting the integrator, or recompiling with different flags — would break the validation chain in ways that are difficult to detect without re-running the FAA's full empirical suite.

We therefore treat the Fortran binary as a black-box ground-truth oracle and build an **ML extension layer around it**. The extension layer:

1. Runs CGEM via `cgem_wrapper.run_cgem_for_profile` exactly as it always has.
2. Produces a labeled synthetic dataset by sweeping CGEM over a defensible input grid.
3. Trains a fast, calibrated surrogate that emulates CGEM ~10⁵× faster.
4. Detects when input features fall outside CGEM's validated envelope.
5. Quantifies which inputs drive G-LOC most via global sensitivity analysis.
6. Serves the above through a FastAPI service with a typed TS client.

Critically, **the extension never alters the Fortran binary, the `.f` source, or the wrapper's call shape**. Downstream consumers (notably `pulse-sim`'s `cgem_bridge.py`) continue to import `from cgem_wrapper import run_cgem_for_profile, PilotConfig` and receive the same object they always have.

## Layer diagram

```
┌──────────────────────────────────────────────────────────┐
│  React/TypeScript frontend (frontend/)                   │
│  Vite 7 · React 19 · TS 5.9 · ECharts 5.6 · React Query  │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP (axios) — typed via openapi-typescript
                     ▼
┌──────────────────────────────────────────────────────────┐
│  cgem_ext.api — FastAPI service                          │
│  /predict · /sweep · /sensitivity · /run-cgem · /ood     │
│  Pydantic schemas mirror the v2.2.0 CGEMRun JSON contract│
└──────┬───────────────────────────────────────┬───────────┘
       │ fast path (ms)                        │ ground-truth path (s)
       ▼                                       ▼
┌──────────────────────────┐         ┌─────────────────────────┐
│ cgem_ext (this layer)    │         │ cgem_wrapper.py         │
│  data/        generators │         │ subprocess → ./cgem     │
│  ood/        Mahalanobis │         │ Fortran physiology core │
│  surrogate/  XGBoost+CP  │         │ (FAA AAM-631, validated)│
│  sensitivity/ Sobol      │         └─────────────────────────┘
└──────────────────────────┘                     ▲
                                                 │
                          ┌──────────────────────┘
                          │ same import path used by pulse-sim
                          │ (preserved verbatim — see tests/test_contract.py)
                          ▼
                    ┌───────────────────────────────────┐
                    │ pulse-sim/integrations/cgem_bridge│
                    │ (downstream consumer, untouched)  │
                    └───────────────────────────────────┘
```

## Module boundaries

### `cgem_ext.data`

- `generate_dataset.py`: cross-product CGEM runner, parallelized over independent subprocess workers. Output schema: input feature columns + per-event-time output columns + per-trace summary statistics. Reproducibility key: `(seed, dataset_version, cgem_binary_sha256)`.
- `splits.py`: `stratified_split(df, seed)` returns 70/15/15 stratified by maneuver category; `leave_one_group_out(df, group)` returns disjoint train/test pairs for OOD-style validation.

### `cgem_ext.ood`

- `mahalanobis.py`: fits `sklearn.covariance.MinCovDet` (robust covariance) on the train split's input features; scores any input by squared Mahalanobis distance; threshold via χ²(df, 0.95).
- `conformal.py`: split-conformal calibration on the validation split, target abstention rate α = 0.05.
- Public API: `is_in_envelope(features: dict | pd.DataFrame) -> bool` (cheap; ms latency).

### `cgem_ext.surrogate`

- Per-target separate models — fitting one big multi-output regressor would couple errors across physiologically independent endpoints. Targets:
  - `time_to_greyout_s`
  - `time_to_blackout_s`
  - `time_to_gloc_s`
  - `HLAP_min`
  - `c_bank_min`
- Censored outputs (no event during the maneuver) are handled by a two-stage classifier-then-regressor: first predict `event_occurred ∈ {0, 1}`, then predict the time conditional on `event_occurred = 1`. This avoids regressor pathology when censored values are encoded as sentinels.
- Mondrian split-conformal CIs stratified by maneuver category. The intervals widen on rare categories rather than failing silently — exactly the calibration property an aeromedical reviewer expects.
- SHAP TreeExplainer for interpretability (per-prediction feature attributions).

### `cgem_ext.sensitivity`

- `sobol.py`: SALib `saltelli.sample` + `sobol.analyze` over the emulator. The emulator is fast enough that 10⁴-sample Sobol studies run in seconds; against the Fortran subprocess they would take days.
- `morris.py`: elementary effects screening for cheap sweep across many maneuvers.
- Output: per-target first-order, total-order, and second-order indices with bootstrap confidence intervals.

### `cgem_ext.api`

- `main.py`: FastAPI app. Endpoints:
  - `POST /predict` — input features → `{point, lo, hi, ood, ood_score, model_version, cgem_version}`.
  - `POST /sweep` — input grid → batched predictions.
  - `POST /run-cgem` — same input → invokes the Fortran subprocess; returns the v2.2.0 CGEMRun JSON shape verbatim.
  - `GET /sensitivity/{target}` — precomputed Sobol indices.
  - `GET /healthz`, `GET /version`.
- `schemas.py`: Pydantic v2 models that **must** mirror the `CGEMRun` JSON contract. The contract itself is enforced by `tests/test_contract.py`.

## Versioning policy

- **Fortran core**: pinned by SHA-256 of the compiled `cgem` binary. Reported in `/version`.
- **Surrogate emulator**: SemVer (`emulator_v0.1.0` → `v1.0.0` at first publication). Each release carries: dataset hash, training random seed, hyperparameters, calibration metrics.
- **Dataset**: `cgem_synthetic_v{N}` with a frozen DVC hash; never regenerated in place.
- **Extension package**: SemVer at the package level (see `pyproject.toml`).

## Reproducibility chain

1. Pin `cgem` binary SHA in `cgem_ext.REPO_ROOT / "cgem"` (CI verifies on every run).
2. Dataset generation runs from a known `seed`; `multiprocessing.Pool` workers receive deterministic per-row seeds derived from the master seed.
3. Each MLflow run logs: dataset hash, package version, all hyperparameters, all metrics, the trained artifact, and the Git commit SHA.
4. The Docker image (`cgem_ext/api/Dockerfile`) bakes the binary + emulator artifacts at known versions and publishes to GHCR. External reviewers can pull the exact image used to generate the paper.

## Constraints and non-goals

- **No modification of `cgem.f`** — would break FAA validation.
- **No re-implementation of CGEM in Python** — would break FAA validation; would create a new model that needs its own validation chain.
- **No coupling of CGEM into Pulse's differential equations** — that's the deferred coupled-mode prototype tracked separately in pulse-sim.
- **No HRV-based risk prediction in this layer** — see `Docs/Manual.md` §HRV; that work waits for instrumented subjects (paper 3).
- **No invented physiology** — the extension layer reproduces and quantifies CGEM; it does not claim novel physiological insight.

## How `pulse-sim` consumes this layer

`pulse-sim/integrations/cgem_bridge.py` does *not* go through the FastAPI service. It imports `cgem_wrapper` directly via `sys.path` injection and calls `run_cgem_for_profile(maneuver, cfg)`. That path is preserved verbatim by this layer:

```python
# cgem_ext/__init__.py
from cgem_wrapper import PilotConfig, run_cgem_for_profile
__all__ = ["PilotConfig", "run_cgem_for_profile"]
```

So consumers can either:
- Use the upstream import path (`from cgem_wrapper import ...`) — pulse-sim's current behaviour, preserved.
- Use the centralized re-export (`from cgem_ext import ...`) — recommended for new consumers.

Both paths reach the same code; `tests/test_contract.py` enforces this invariant in CI.
