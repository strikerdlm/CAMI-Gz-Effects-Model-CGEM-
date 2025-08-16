# ML Modernisation & Enhancement Proposal

> **Project components analysed:**
> 1. `src/cgem.f` – FORTRAN **Combined-G-Effects-Model (CGEM)** predicting G-LOC and visual-impairment from acceleration profiles.
> 2. `aerobatic_profiles.py` (+ sample input files) – Python loader for discretised **G-profiles** recorded in aerobatic flights.
> 3. `medical_office_cli.py` (+ demo) – CLI that captures **patient/vital-sign data** and stores it as JSON.
>
> The repository therefore already provides: (a) a physiologically-based simulator, (b) structured data-capture tooling, and (c) real flight profiles.  No machine-learning model is yet implemented.

---

## 1. Quick Wins (≤2 weeks)

| Area | Recommendation | Latest Tooling |
|------|----------------|----------------|
| **Data handling** | Load JSON & text inputs into a unified Pandas / PyArrow table; version with **DVC** or **LakeFS**. | `pandas 2.2`, `pyarrow 15`, `dvc 3` |
| **Experiment tracking** | Start logging all runs, parameters, & metrics. | `MLflow 2.10`, `Weights & Biases` |
| **Hyper-parameter tuning** | Automated sweeps for tree & neural models. | `Optuna 3.5`, `Ray Tune` |
| **Explainability** | Global + per-sample feature attribution. | `SHAP 0.44`, `captum` |
| **Packaging** | Export trained models to **ONNX** for language-agnostic inference; serve with **Triton IS**. | `onnxruntime 1.17`, `nvcr.io/nvidia/tritonserver` |

---

## 2. Predictive Modelling Roadmap

1. **Surrogate model for CGEM (speed-up 10-100×)**  
   • Gather ≥10 k simulated runs (varying pilot demographics & G-profiles).  
   • Train physics-informed networks (PINNs) or gradient-boosted trees to predict `t_blackout`, `t_G-LOC`, etc.  
   • Candidate libraries: `torch-pinns`, `PyTorch 2.2`, `LightGBM 4.3`.

2. **Time-series model for real-time G-LOC risk**  
   • Input: streaming Nz + biosignals (heart-rate, BP).  
   • Architectures: Temporal Convolutional Network, `ts-transformer` (Nixtla `tstransformer 0.5`), `InceptionTime`, `GluonTS`.

3. **Tabular patient-outcome model**  
   • Combine CLI-captured data with historical outcomes.  
   • Try AutoML for tabular: `TabPFN`, `AutoGluon 0.8`, `PyCaret 3`.

4. **Multi-modal fusion**  
   • Merge (1)+(2)+(3) inside a unified model with separate encoders (TabNet + Transformer) followed by a joint head.  
   • Frameworks: `pytorch-forecasting`, `lightning-flash`.

---

## 3. Data Augmentation & Simulation

• **Generative Adversarial Networks (GANs)** to create realistic but unseen G-profiles for rare manoeuvres.  
• **Diffusion models** to vary acceleration curves while respecting physical constraints.  
• **Synthetic patient generators** (`SDV 1.8`) for privacy-preserving clinical data.

---

## 4. MLOps Pipeline (Dev → Prod)

1. **Workflow Orchestration** – `Prefect 2` or `Airflow 2.7` DAG triggers: simulate ➜ train ➜ test ➜ deploy.
2. **Containerisation** – Build multi-arch images with `Docker` + `conda-pack`; push to GHCR.
3. **Continuous Integration** – Add GitHub Actions running unit tests & notebook smoke-tests (use `pytest-nb`).
4. **Model Registry** – MLflow Tracking Server + S3/GCS backend.
5. **Online Serving** – Deploy best model via `KServe` or `FastAPI` + `Uvicorn`.
6. **Monitoring** – Latency & data-drift alerts (`Evidently AI`).

---

## 5. Future Research Directions

| Topic | Motivation | Starter Resources |
|-------|------------|-------------------|
| **Reinforcement Learning for Anti-G Straining Manoeuvres** | Optimise AGSM timing based on biosensor feedback. | `stable-baselines3`, FAA datasets |
| **NLP on Unstructured Clinical Notes** | Extract comorbidities & symptoms from free-text; feed into risk models. | `spaCy 3.7`, `HuggingFace Transformers 4.39` |
| **Graph Neural Networks** | Represent physiological systems or manoeuvre sequences as graphs. | `DGL 1.1`, `PyTorch Geometric 2.5` |
| **Federated Learning / Differential Privacy** | Train on distributed clinic data without sharing raw PHI. | `Flower 1.6`, `PySyft` |
| **Explainable Physics-ML Hybrids** | Blend first-principles (CGEM) with learned residuals for interpretability. | PINN literature |

---

## 6. Proposed File/Module Additions

```
/experiments/           ← notebooks & scripts for data exploration
ml_pipeline/
  ├── data_ingest.py    ← load & clean JSON / G-profile files
  ├── train_surrogate.py
  ├── train_timeseries.py
  ├── utils.py          ← common plotting / feature-eng
  └── requirements.txt  ← pinned versions (see above)
models/
  └── cgem_surrogate.onnx
```

---

## 7. Next Steps Checklist

- [ ] Set up DVC remote & commit raw datasets
- [ ] Implement data-ingestion script (`ml_pipeline/data_ingest.py`)
- [ ] Generate 10 k CGEM simulations for training
- [ ] Create baseline LightGBM surrogate & log to MLflow
- [ ] Draft CI workflow (`.github/workflows/ml.yml`)
- [ ] Review results & iterate on model architectures

---

*Prepared by: AI assistant • Month 2025*