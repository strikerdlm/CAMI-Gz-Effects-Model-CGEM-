# Legacy Streamlit demos

This directory contains the original Streamlit-based UI for CGEM. As of `feat/ml-layer-phase-0`, the Streamlit dashboards are **deprecated** in favour of the FastAPI service (`cgem_ext.api`) and the Vite/React/TypeScript frontend in `frontend/`. They are retained here to keep existing demonstrations runnable until the new stack reaches feature parity.

See `ROADMAP.md` at the repo root for the migration timeline.

## Files

- `app.py` — minimal Streamlit demo: profile picker + one CGEM run + ECharts plot.
- `enhanced_app.py` — full Streamlit dashboard: profile selection, batch CGEM, PDF export, pilot survey ingestion, 3D animation, HRV scaffolding.
- `i18n.py` — language selector + EN/ES translations used by both apps.
- `data/pilot_survey.db` — SQLite store populated by the Streamlit form in `enhanced_app.py`. Read-only from the new stack.

## Running the legacy apps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ../../requirements.txt
streamlit run legacy/streamlit/enhanced_app.py
```

Streamlit must be invoked from the repository root so the apps can resolve `aerobatic_profiles`, `cgem_wrapper`, `maneuvers_catalog`, and `Aerobatics_sample_inputs/` via relative imports/paths.

## Why deprecated

The new architecture separates concerns: the Python layer becomes a stateless API (`cgem_ext.api`) backed by surrogate ML, OOD detection, and the Fortran ground truth; the UI lives independently in TypeScript/React. This:

- Removes Python-side rendering logic so we can iterate on the UI without restarting the kernel.
- Lets the ML extension layer (`cgem_ext/`) ship as a packaged library, importable by external consumers (e.g. `pulse-sim`).
- Enables OpenAPI schema codegen for typed TS clients.
- Makes the CGEM stack deployable as a service rather than a notebook.

## Do not extend

New features should land in `cgem_ext/` (Python service) and `frontend/` (UI). Bug fixes here are accepted only if they unblock active research using the legacy demos.
