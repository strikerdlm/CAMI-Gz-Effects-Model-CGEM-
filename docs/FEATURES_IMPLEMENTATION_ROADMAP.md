# Features & Implementation Roadmap (Complement to FUTURE_IMPLEMENTATIONS and ML_Upgrade_Proposal)

This document proposes pragmatic, near- to mid-term features and concrete implementation steps for the aerobatic physiology visualizer (Streamlit apps, CGEM wrapper) and the medical office CLI. It complements `FUTURE_IMPLEMENTATIONS.md` (vision, long-term) and `ML_Upgrade_Proposal.md` (ML track) with actionable, scoped work packages.

## Legend
- [S] small (≤2 days)  •  [M] medium (≤2 weeks)  •  [L] large (≥2 weeks)
- [A] aerobatics/visualizer  •  [M] medical CLI  •  [X] cross-cutting

---

## 1) Productizing the Visualizer [A]

### 1.1 Scenario Builder & Profiles [M]
- Add UI to compose multi-leg manoeuvres with durations and G targets.
- Save/load `.json` scenario files; add sample library.
- Implementation:
  - Add `schemas/scenario.schema.json` + `src/scenarios.py` (parse/validate).
  - New Streamlit tab "Scenario Builder" in `enhanced_app.py`.
  - Export to CGEM input via adapter.

### 1.2 Pilot Profiles & Parameterization [S→M]
- Expose CGEM subject presets (untrained/basic/advanced/fighter) and custom parameters (age, mass, training).
- Implementation:
  - Extend `cgem_wrapper.run_cgem_for_profile(..., subject: SubjectProfile)`.
  - Sidebar selector with preset + advanced expanders.

### 1.3 Session Save/Share [S]
- Persist UI state, selected manoeuvre, toggles; export a shareable `.viz.json`.
- Implementation: `st.session_state` snapshot + download button.

### 1.4 Report Export [M]
- One-click PDF/HTML report with key plots, thresholds crossed, and timings.
- Implementation:
  - Generate HTML with Plotly static images; convert via `weasyprint` or `wkhtmltopdf`.

### 1.5 Accessibility & UX Polishing [S]
- Dark mode toggle; larger labels; keyboard shortcuts; tooltips.
- Implementation: CSS theme variables; help icons with `st.tooltip()` equivalents.

---

## 2) CGEM Integration Hardening [A, X]

### 2.1 Deterministic, Cached Runs [S]
- Hash inputs to a cache key; store results on disk for reuse in batch.
- Implementation: `cache/` directory + SHA256 of input deck; hydrate from `parquet`.

### 2.2 Input/Output Contracts [S]
- Formalize input deck generator and parsed outputs.
- Implementation: `pydantic` models for `CGEMInput`, `CGEMResult` with version fields.

### 2.3 Unit & Golden Tests [M]
- Golden files for known profiles; validate times and flags within tolerances.
- Implementation: `tests/test_cgem_wrapper.py` with fixtures; CI job.

### 2.4 Performance Profiling [S]
- Time per profile; show ETA in UI; warn on slow runs.
- Implementation: simple timers; Streamlit status text.

---

## 3) Visualization Enhancements [A]

### 3.1 Threshold Editor & What-If [S]
- Allow editing greyout/blackout/G-LOC thresholds; compare curves.
- Implementation: sidebar sliders; overlay baseline vs custom.

### 3.2 Multi-Run Compare [M]
- Compare up to N runs side-by-side; synchronized cursor.
- Implementation: add a compare tab; color-coded runs; shared x-axis.

### 3.3 Timeline Annotations [S]
- Mark events (greyout, blackout, G-LOC) with tooltips and links to explanations.
- Implementation: Plotly shapes/annotations + `MANEUVER_EXPLANATIONS` lookup.

### 3.4 Video Overlay (Optional) [L]
- Sync in-cockpit video to timeline if provided.
- Implementation: upload video, set FPS/time offset; scrub with plot events.

---

## 4) Real-Time & External Integrations [A, X]

### 4.1 Simulator Bridge MVP [M]
- Receive live Nz from X-Plane/MSFS via UDP; display live risk gauge.
- Implementation: `src/sim_bridge.py` (async UDP listener), queue ➜ UI.

### 4.2 Wearable Data Ingest (Offline) [M]
- Import CSV from Garmin/Polar/Apple HR/SpO2; align to profile time.
- Implementation: `src/wearables_ingest.py` with vendor mappers.

### 4.3 Basic Alerting [S]
- Configurable thresholds; sound/vibrate (if supported) or on-screen alerts.

---

## 5) Analytics & ML (Near-Term) [X]

Refers to `ML_Upgrade_Proposal.md` for full plan. Near-term additions:

### 5.1 LightGBM Surrogate (Batch) [M]
- Train a baseline surrogate for `t_greyout`, `t_blackout`, `t_gloc` on simulated dataset.
- Implementation: `ml_pipeline/train_surrogate.py`; log to MLflow; export ONNX.

### 5.2 Risk Scoring Heuristics [S]
- Deterministic score combining peak G, rate of change, duration above thresholds.
- Implementation: `src/risk_scores.py`; show score badges in UI.

### 5.3 Drift & Range Checks [S]
- Input validation: warn if profile outside trained distribution.
- Implementation: feature ranges stored with model; UI warning banner.

---

## 6) Medical Office CLI Upgrades [M]

### 6.1 TUI Mode (Rich/Textual) [M]
- Replace pure CLI with structured TUI forms and navigation.
- Implementation: `textual` app with sections for demographics/vitals/symptoms.

### 6.2 Encryption & PHI Safety [M]
- Encrypt saved JSON with age-keyed passphrase or local KMS; redact exports.
- Implementation: `cryptography` Fernet or age; CLI flags `--encrypt`, `--redact`.

### 6.3 Validation Library & Schemas [S]
- Centralize validators; JSON Schema; unit tests.
- Implementation: `pydantic` models; `schemas/medical_data.schema.json`.

### 6.4 FHIR Export (Read-Only) [M]
- Map captured data to FHIR `Patient`, `Observation` bundles.
- Implementation: `fhir.resources` package; `--export-fhir` flag.

### 6.5 Import/Resume Sessions [S]
- Load existing JSON to resume/edit; track provenance fields.

---

## 7) DevEx, Packaging, and QA [X]

### 7.1 CI Pipeline [S]
- Lint, type-check, unit tests, notebook smoke tests.
- Implementation: GitHub Actions with `ruff`, `mypy`, `pytest`, `pytest-nb`.

### 7.2 App Packaging [S]
- `pipx`-installable CLIs and `streamlit` apps; lock files.
- Implementation: `pyproject.toml`; entry points; pinned `requirements*.txt`.

### 7.3 Release Channels [S]
- Pre-release `-rc` builds; changelog.
- Implementation: `semantic-release` or `commitizen` + GH Actions.

### 7.4 Telemetry (Optional, Opt-in) [S]
- Anonymous usage metrics to prioritize features.
- Implementation: simple event pings with hashed session ID.

---

## 8) Security & Compliance (Incremental) [X]
- Role-based access to advanced/medical features in the app [M].
- PHI redaction by default for shared artifacts [S].
- Audit log for data exports and simulations [S].

---

## Suggested Phased Roadmap

### Phase 0 (Week 1–2)
- 1.2 Pilot profiles
- 2.1 Cached runs
- 3.1 Threshold editor
- 7.1 CI pipeline

### Phase 1 (Month 1)
- 1.1 Scenario builder (MVP)
- 1.4 Report export
- 6.3 Validation + schemas
- 5.2 Risk scoring heuristics

### Phase 2 (Month 2)
- 3.2 Multi-run compare
- 4.1 Simulator bridge MVP
- 5.1 LightGBM surrogate (batch)
- 6.1 TUI mode (skeleton)

### Phase 3 (Month 3+)
- 4.2 Wearable ingest
- 6.2 Encryption & PHI safety
- 6.4 FHIR export
- 3.4 Video overlay (if needed)

---

## Acceptance Criteria Examples
- Scenario file created in UI can be saved, reloaded, and reproduced via CGEM wrapper.
- Pilot profile changes alter outputs deterministically; cached results are reused across tabs.
- Report export generates a PDF with plots and a summary of threshold crossings and event times.
- ML surrogate reproduces CGEM event times with MAE ≤ 0.3 s on validation data.
- Medical CLI TUI captures all fields, validates against schema, and can export FHIR Bundle JSON.

---

## Dependencies & Notes
- Keep this doc aligned with `FUTURE_IMPLEMENTATIONS.md` and `ML_Upgrade_Proposal.md`.
- Prefer additive modules in `src/` to avoid bloating `enhanced_app.py`.
- Ensure headless CI Plotly/Matplotlib rendering via `Agg` backend.