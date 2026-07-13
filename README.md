# CGEM — ML-Augmented CAMI G-Effects Model

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](https://en.wikipedia.org/wiki/Cross-platform)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-3178C6?logo=react&logoColor=white)](https://react.dev)
[![API](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Software platform for modelling G-induced loss of consciousness (G-LOC) with the FAA CAMI G-Effects Model (CGEM) and an additive machine-learning extension layer. The original FAA Fortran physiology core (`src/cgem.f`) is preserved byte-for-byte. The Python extension (`cgem_ext/`) provides a surrogate emulator, out-of-distribution (OOD) detection, global sensitivity analysis, conformal uncertainty quantification, and a FastAPI service consumed by a Vite + React + TypeScript frontend.

Developed by **Dr. Diego Malpica** (Direction of Aerospace Medicine, Colombian Aerospace Force — Aerospace Scientific Department). Forked from the original [FAA AAM-631 CGEM project](https://doi.org/10.21949/1524439).

---

## Validation Benchmarks

The metrics below were produced from `cgem_synthetic_v1` (3,240 rows × 60 columns; 72 aerobatic, military, and extreme-post-stall maneuvers; master seed 42). Reproduction checks are implemented in `tests/`.

### Surrogate emulator

#### Continuous targets

| Target | Test R² | RMSE | RF baseline R² |
|---|---|---|---|
| `hlap_min` (head-level arterial pressure) | **1.000** | 0.008 mmHg | 1.000 |
| `c_bank_min` (consciousness reserve bank) | **0.938** | 0.950 s | 0.939 |

#### Event classifiers

| Target | Test AUROC |
|---|---|
| `time_to_greyout_s` — event flag | **0.996** |
| `time_to_blackout_s` — event flag | **0.999** |
| `time_to_gloc_s` — event flag | **0.996** |

#### Conditional regressors

| Target | Test R² | RMSE | RF baseline R² |
|---|---|---|---|
| `time_to_greyout_s` | **0.880** | 0.519 s | −0.835 |
| `time_to_blackout_s` | **0.903** | 0.458 s | −1.427 |
| `time_to_gloc_s` | **0.821** | 1.142 s | −1.029 |

The RandomForest baseline shows negative R² on censored targets because its `predict_expected_time = P(event) × E[time | event]` is heavily damped on high-event-rate test rows; XGBoost's monotonicity-constrained two-stage approach is not subject to this issue.

### Mondrian split-conformal coverage

Empirical coverage of 95 % prediction intervals on the held-out test split, calibrated on the validation split.

| Target | Empirical coverage | Observation |
|---|---|---|
| `hlap_min` | 0.928 | Below nominal |
| `c_bank_min` | 0.949 | Near nominal |
| `time_to_greyout_s` (event = 1) | 1.000 | Over-coverage |
| `time_to_blackout_s` (event = 1) | 1.000 | Over-coverage |
| `time_to_gloc_s` (event = 1) | 0.861 | Under-coverage on long-tail cases |

### OOD detector calibration and discrimination

#### Calibration

| Detector | Test in-envelope rate |
|---|---|
| Mahalanobis + split-conformal abstention | **0.953** |

#### Leave-one-group-out discrimination

| Fold held out | Mahalanobis AUROC | IsolationForest AUROC |
|---|---|---|
| `championship` | 0.576 | 0.551 |
| `military_acm` | 0.659 | 0.594 |
| `extreme_post_stall` | 0.600 | 0.588 |
| `conceptual` | 0.527 | 0.540 |

The moderate AUROC values reflect overlap between maneuver categories in the continuous feature space; the categories are not cleanly separable by the nine input dimensions. Additional details are documented in `docs/models/ood_card.md`.

### Sensitivity analysis stability

First-order (S1) and total-order (ST) Sobol indices computed via the surrogate at n_base = 1,024 (102,000 evaluations), wall-clock ~38 s. Stability assessed via Spearman rank correlation across two independent Saltelli samples.

| Target | Top driver (S1 / ST) | Second driver | ST > S1 note |
|---|---|---|---|
| `time_to_greyout_s` | `g_peak_abs` (0.65 / 0.88) | `profile_duration_s` (0.08 / 0.28) | Interaction effect g_peak × duration |
| `time_to_blackout_s` | `g_peak_abs` (0.74 / 0.92) | `profile_duration_s` (0.02 / 0.20) | Same |
| `time_to_gloc_s` | `g_peak_abs` (0.68 / 0.94) | `profile_duration_s` (0.09 / 0.25) | Same |
| `hlap_min` | `dehydration_level` (1.00 / 1.00) | `profile_duration_s` (~0) | Deterministically dominated by dehydration |
| `c_bank_min` | `g_peak_abs` (0.74 / 0.79) | `profile_duration_s` (0.17 / 0.22) | Weaker interaction than time targets |

Total-order Spearman rank correlations range from 0.983 to 1.000 across the five targets. First-order correlations range from 0.466 to 0.983; near-zero S1 values are sensitive to small changes in features whose effects are primarily interaction-mediated.

### Evaluation speed

| Method | Time per row | Notes |
|---|---|---|
| Direct CGEM subprocess | ~9 ms | Single core, isolated tmpdir |
| XGBoost surrogate | ~50 µs | In-process, single core |
| **Speedup** | **~180×** | Vectorises across batches |

The surrogate reduces the per-row evaluation time used by large Sobol and Morris batches.

---

## Architecture

```
cgem-ext/
├── src/cgem.f                  # FAA Fortran core — NEVER MODIFIED
├── cgem_wrapper.py             # Subprocess wrapper; public API preserved
│
├── cgem_ext/
│   ├── data/
│   │   ├── generate_dataset.py # Parallelized CGEM runner → parquet
│   │   └── splits.py           # Stratified 70/15/15 + LOGO splitter
│   ├── ood/
│   │   ├── features.py         # Frozen 17-d feature space (contract)
│   │   ├── mahalanobis.py      # MinCovDet + χ²(df, 0.95) threshold
│   │   ├── conformal.py        # Split-conformal abstention layer
│   │   └── baseline.py         # IsolationForest baseline
│   ├── surrogate/
│   │   ├── features.py         # Re-exports OOD feature space
│   │   ├── targets.py          # 5-target catalogue + monotonicity priors
│   │   ├── xgb.py              # XGBSurrogate + TwoStageXGBSurrogate
│   │   ├── baseline.py         # RFSurrogate + TwoStageRFSurrogate
│   │   └── conformal.py        # MondrianSplitConformal (per category)
│   ├── sensitivity/
│   │   ├── space.py            # 9-d Sobol problem definition
│   │   ├── sobol.py            # SobolAnalyzer (SALib Saltelli)
│   │   └── morris.py           # MorrisAnalyzer (elementary effects)
│   └── api/
│       ├── schemas.py          # Pydantic v2 wire contract (preserves
│       │                       #   pulse-sim CGEMRun JSON shape)
│       ├── state.py            # Lifespan-managed AppState model store
│       ├── main.py             # FastAPI app: 7 endpoints
│       └── Dockerfile          # python:3.12-slim + cgem binary baked in
│
├── frontend/                   # Vite 7 · React 19 · TS 5.9 · ECharts 5.6
├── legacy/streamlit/           # Deprecated Streamlit demos (still run)
├── data/
│   ├── datasets/               # cgem_synthetic_v1.parquet + sidecar
│   └── results/sensitivity/    # Sobol + Morris CSVs + manifest
├── scripts/                    # run_sensitivity.py · export_openapi.py
├── tests/                      # Contract, model, API, and integration tests
└── docs/
    ├── api/openapi.json        # Auto-exported OpenAPI spec
    ├── models/                 # Model cards (Mitchell et al. 2019)
    └── data/                   # Datasheet (Gebru et al. 2018)
```

The validated FAA Fortran binary is invoked unchanged through `cgem_wrapper.run_cgem_for_profile`, **and** the FastAPI `/run-cgem` response mirrors the v2.2.0 `CGEMRun` JSON shape that pulse-sim's `cgem_bridge.load_cgem_json` consumes. Both contracts are enforced by regression tests in `tests/test_contract.py` and `tests/test_api.py` on every push.

---

## Run the Web Application

The application has two processes: the Python API on port 8000 and the React frontend on port 5173. Keep both terminals open while using the app.

### Prerequisites

- Python 3.10–3.12.
- Node.js 20.19+ or 22.13+ (Node 22 LTS is recommended) and npm.
- Windows: the committed `cgem.exe` is used by the authoritative predictor.
- Linux: install the Fortran runtime with `sudo apt-get install -y libgfortran5` so the committed `cgem` binary can run.

### Windows PowerShell — step by step

1. Open PowerShell in the repository root and create the Python environment:

```powershell
cd path\to\CAMI-Gz-Effects-Model-CGEM-
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[ml,api,dev]"
```

If you already use a Conda environment, activate it instead of creating `.venv`, then run the two `python -m pip` commands above.

2. In the same terminal, start the API from the repository root:

```powershell
python -m uvicorn cgem_ext.api.main:app --host 127.0.0.1 --port 8000
```

The first start fits the OOD detector, five surrogates, and conformal layers. Do not open the predictor until Uvicorn prints:

```text
Application startup complete.
```

`Waiting for application startup` means the API is not ready yet. Verify it from another PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
# Expected: status = ok
```

For automatic code reload during development, append `--reload` to the Uvicorn command.

3. Open a second PowerShell window, return to the repository, and start the frontend:

```powershell
cd path\to\CAMI-Gz-Effects-Model-CGEM-\frontend
npm install
npm run dev -- --host 127.0.0.1
```

4. Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The CGEM API address shown in the UI should be `http://127.0.0.1:8000`.

### Linux or macOS

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[ml,api,dev]"
python -m uvicorn cgem_ext.api.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, activate the environment, then run `cd frontend && npm install && npm run dev -- --host 127.0.0.1`. The authoritative Fortran call additionally requires a compatible `cgem` binary and runtime for the host OS.

### API service

The API exposes the surrogate, OOD detector, conformal CIs, sensitivity rankings, and authoritative Fortran subprocess behind seven endpoints.

- API root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI document: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

| Endpoint | Method | Purpose |
|---|---|---|
| `/`                       | GET  | Landing payload |
| `/healthz`                | GET  | Liveness probe |
| `/version`                | GET  | Package version + binary SHA-256 + dataset metadata |
| `/sensitivity/{target}`   | GET  | Precomputed Sobol indices for one target |
| `/predict`                | POST | One-row prediction (surrogate + conformal CI + OOD flag) |
| `/sweep`                  | POST | Batched predictions (1..10,000 rows) |
| `/run-cgem`               | POST | Authoritative Fortran subprocess; returns the v2.2.0 pulse-sim `CGEMRun` JSON shape verbatim |

A frozen OpenAPI spec is committed at [`docs/api/openapi.json`](docs/api/openapi.json) for frontend codegen.

### Docker

```bash
docker build -f cgem_ext/api/Dockerfile -t cgem-ext-api:0.1.0 .
docker run --rm -p 8000:8000 cgem-ext-api:0.1.0
# Single-stage python:3.12-slim image with libgfortran5, the cgem binary,
# the canonical dataset, and the precomputed sensitivity CSVs baked in.
# Healthcheck on /healthz with a 90 s start grace.
```

### React + TypeScript frontend

The frontend talks to the FastAPI service exclusively. The default is
`http://127.0.0.1:8000`; set `VITE_API_URL` before `npm run dev` if the API is elsewhere.

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### If the UI says “API unreachable”

1. Confirm the API terminal reached `Application startup complete.`
2. Open [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz) and confirm `{"status":"ok"}`.
3. In the frontend **Settings** page, set the API base URL to `http://127.0.0.1:8000` or click **Default**.
4. Make sure port 8000 is not occupied by a stale process: `Get-NetTCPConnection -LocalPort 8000 -State Listen` in PowerShell.
5. Start Uvicorn with `python -m uvicorn ...` so it uses the same environment where the project dependencies were installed.

The Sobol CSV is committed at `data/results/sensitivity/sobol_first_total.csv`, so the Global Sensitivity panel works as soon as the API is ready. To deliberately regenerate Sobol and Morris results, run `python -m scripts.run_sensitivity` from the repository root and restart the API afterward.

Frontend features:

- **Prediction page** — surrogate `/predict` (~50 ms) with conformal CI + OOD banner, plus authoritative `/run-cgem` (~3 s) for full Fortran time-series.
- **Batch page** — a single `POST /sweep` over all 72 maneuvers; sortable table with per-row OOD score and event probability.
- **Analysis page** — Sobol indices panel (S1 + ST bars) per target, served from the precomputed CSV via `/sensitivity/{target}`; the existing maneuver-explanation tree is preserved.
- **Dashboard** — `/version` status header showing package version + binary SHA + dataset seed.

### Legacy Streamlit demos (deprecated, still work)

```bash
streamlit run legacy/streamlit/enhanced_app.py
```

---

## Python API

### Standard use

```python
from cgem_wrapper import run_cgem_for_profile, PilotConfig

cfg = PilotConfig(
    who_profile=2,
    gsuit_max_psi=5.0,
    gsuit_coverage_fraction=0.35,
    agsm_effectiveness=0.5,
    dehydration_level=0.3,
    seat_tilt_deg=10.0,
)

result, _ = run_cgem_for_profile("hammerhead", config=cfg)
print(result.time_to_greyout_s, result.time_to_blackout_s, result.time_to_gloc_s)
```

### ML surrogate (fast prediction + uncertainty)

```python
import pandas as pd
from cgem_ext.data.splits import stratified_split
from cgem_ext.surrogate import XGBSurrogate, TwoStageXGBSurrogate, MondrianSplitConformal

df   = pd.read_parquet("data/datasets/cgem_synthetic_v1.parquet")
sp   = stratified_split(df, seed=42)
train_df, val_df, test_df = sp.apply(df)

# Continuous target
xgb = XGBSurrogate("hlap_min").fit(train_df)
cp  = MondrianSplitConformal(alpha=0.05).fit(
    cal_predictions=xgb.predict(val_df),
    cal_targets=val_df["hlap_min"],
    cal_strata=val_df["maneuver_category"],
)
lo, hi = cp.predict_interval(xgb.predict(test_df), test_df["maneuver_category"])

# Censored time target — classifier + conditional regressor
two = TwoStageXGBSurrogate("time_to_gloc_s").fit(train_df)
p_event  = two.predict_event_probability(test_df)   # P(G-LOC occurs)
t_cond   = two.predict(test_df)                      # E[t | G-LOC occurs]
t_expect = two.predict_expected_time(test_df)        # P(event) × E[t | event]
```

### OOD detection

```python
from cgem_ext.ood import MahalanobisOOD, ConformalAbstention

ood = MahalanobisOOD().fit(train_df)
abstain = ConformalAbstention(alpha=0.05).calibrate(ood.score(val_df))
in_envelope = abstain.is_in_envelope(ood.score(test_df))   # True → in-distribution
```

### FastAPI client

```python
import httpx

with httpx.Client(base_url="http://localhost:8000") as c:
    r = c.post("/predict", json={
        "maneuver": {"maneuver": "high_g_turn"},
        "pilot": {
            "who_profile": 2,
            "countermeasures_label": "agsm",
            "agsm_effectiveness": 0.6,
        },
    })
    out = r.json()
    print("OOD:", out["ood"], "score:", round(out["ood_score"], 1))
    for t in out["targets"]:
        if t["censored"]:
            print(f"{t['target']:22s} P(event)={t['event_probability']:.3f} "
                  f"E[t|ev]={t['point']:.2f}s CI=[{t['lo']:.2f}, {t['hi']:.2f}]s")
        else:
            print(f"{t['target']:22s} {t['point']:.3f} ± "
                  f"({t['lo']:.3f}, {t['hi']:.3f})")
```

---

## Maneuver Library

72 registered profiles across four categories, curated from Aresti/IAC catalogues, fighter-doctrine BFM manuals, and post-stall literature. The full catalogue with metadata (peak ±Gz, onset rate, hemodynamic concern, source citation) lives in `maneuvers_catalog.py`.

| Category | Count | Representative maneuvers |
|---|---|---|
| Championship (Aresti / IAC) | 35 | Hammerhead, loop, Cuban eight, outside loop, tailslide, snap roll (3 variants), hesitation roll (4-pt / 8-pt), Lomcovák, English bunt, torque roll |
| Military ACM / BFM | 22 | 9-G defensive break, sustained 9-G turn, corner velocity turn, high/low yo-yo, barrel roll, lag pursuit, scissors (flat/rolling), push-pull missile evasion, rate fight (8 G / 22 s) |
| Extreme / post-stall | 12 | Pugachev's Cobra, Kulbit, Herbst J-turn, Russian helicopter, falling leaf, snake-modulated falling leaf, inverted Cobra |
| Conceptual (push-pull stress) | 3 | Triple push-pull loop / Immelmann / split-S |

### Batch runner

```bash
# All 72 maneuvers × all pilot configs × all WHO presets
python run_cgem_batch.py --maneuvers all --who all --configs all

# Generate per-maneuver hemodynamic Markdown report
python tools/build_hemodynamics_report.py
# → docs/MANEUVER_HEMODYNAMICS.md
```

Available `--configs`: `no_countermeasures`, `gsuit_only`, `agsm_only`, `full_countermeasures`, `dehydrated`.

**Model caveats for high-onset maneuvers**

- CGEM is validated through ~10 G/s onset (Copeland & Whinnery 2023). Snap rolls, Cobra-class spikes, and Lomcovák tumbles encode 30–60 G/s; behaviour above the validation ceiling is extrapolated and should be interpreted with caution.
- CGEM models ±Gz only. Lateral (Gy) and longitudinal (Gx) loads from flat spins and tumbling maneuvers are not represented; the +Gz time series understates physiological stress for those cases.

---

## Global Sensitivity Analysis

SALib Sobol + Morris screening driven by the surrogate (102,000 evaluations, ~38 s).

```bash
python scripts/run_sensitivity.py
# Writes to data/results/sensitivity/: sobol_first_total.csv,
# sobol_second_order.csv, morris.csv, manifest.json
```

Key finding: **dehydration_level fully controls `hlap_min`** (S1 = ST = 1.0), independently of G-load. All time-to-event outputs are primarily driven by **g_peak_abs**, with a meaningful interaction with `profile_duration_s` (ST > S1). Countermeasures (AGSM, G-suit, pressure breathing) contribute ~5–10 % to total-order effects on the time-to-event targets. Full tables are in `data/results/sensitivity/`.

---

## Reproducibility

- **Fortran core**: deterministic for a given `gloc_inp.dat` and EGP profile; SHA-256 of the binary logged in `data/datasets/cgem_synthetic_v1.meta.json`.
- **Dataset**: `cgem_synthetic_v1.parquet` — 3,240 rows, master seed 42, per-row seeds derived deterministically; the file hash is recorded in the metadata sidecar.
- **Splits**: `cgem_ext.data.splits.stratified_split(df, seed=42)` — deterministic stratified train, validation, and test partitions with no test-set leakage.
- **CI**: GitHub Actions matrix (Python 3.10/3.11/3.12) — `pytest`, `ruff`, `mypy`, plus a dedicated `pulse-sim-contract` job on every push.

---

## References

| Citation | DOI |
|---|---|
| Copeland & Whinnery (2023). *Gz-induced effects computer model* (DOT/FAA/AM-23/6) | [10.21949/1524446](https://doi.org/10.21949/1524446) |
| Copeland (2021). *CGEM User's Guide* (DOT/FAA/AM-23/5) | [10.21949/1524438](https://doi.org/10.21949/1524438) |
| Mitchell et al. (2019). *Model Cards for Model Reporting* | [arXiv:1810.03677](https://arxiv.org/abs/1810.03677) |
| Gebru et al. (2018). *Datasheets for Datasets* | [arXiv:1803.09010](https://arxiv.org/abs/1803.09010) |
| Romano et al. (2019). *Conformalized quantile regression* | [arXiv:1905.03222](https://arxiv.org/abs/1905.03222) |
| Whinnery & Forster (2015). *Neurologic state transitions*. Visual Neuroscience, 32, E008 | [10.1017/S095252381500005X](https://doi.org/10.1017/S095252381500005X) |
| Whinnery, Forster & Rogers (2014). *+Gz recovery of consciousness curve*. Extreme Physiology & Medicine, 3, 9 | [10.1186/2046-7648-3-9](https://doi.org/10.1186/2046-7648-3-9) |
| Eiken & Grönkvist (2013). *Supra-tolerance +Gz exposures*. Aviat Space Environ Med, 84(3), 196–205 | [10.3357/asem.3436.2013](https://doi.org/10.3357/asem.3436.2013) |
| Tripp et al. (2009). *Cerebral oxygen saturation and G-LOC*. Human Factors, 51(6), 775–784 | [10.1177/0018720809359631](https://doi.org/10.1177/0018720809359631) |
| Newman & Callister (2009). *Gz environment in F/A-18 ACM*. Aviat Space Environ Med | [10.3357/asem.2361.2009](https://doi.org/10.3357/asem.2361.2009) |
| Ryoo et al. (2004). *Consciousness monitoring with NIRS under +Gz*. Med Eng Phys | [10.1016/j.medengphy.2004.07.003](https://doi.org/10.1016/j.medengphy.2004.07.003) |
| Rossen, Kabat & Anderson (1943). *Acute arrest of cerebral circulation*. Arch Neurol Psychiatry | [10.1001/archneurpsyc.1943.02290230022002](https://doi.org/10.1001/archneurpsyc.1943.02290230022002) |

For historical FAA technical reports, see the [FAA Office of Aerospace Medicine portal](https://www.faa.gov/go/oamtechreports) and the [ROSA P repository](https://rosap.ntl.bts.gov).

---

## Attribution

- **Original FAA CGEM model**: Kyle Copeland and collaborators, FAA Civil Aerospace Medical Institute (CAMI), AAM-631. See source headers in `src/cgem.f`. Please retain attribution to the FAA CGEM model in derivative works.
- **This fork and ML extension layer**: Dr. Diego Malpica, MD — Direction of Aerospace Medicine, Colombian Aerospace Force, Aerospace Scientific Department.

AI assistants were used for code scaffolding and documentation editing. All commits are sole-authored by `strikerdlm`.

---

## Disclaimer

This toolkit is intended for research, education, and training support. It does not substitute for operational aeromedical guidance or certification. Not an official product of the FAA or the U.S. Department of Defense. All views are those of the contributors.
