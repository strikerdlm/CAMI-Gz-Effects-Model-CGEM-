# G-Effects Model by Civil Aerospace Medicine Institute 🚀

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](https://en.wikipedia.org/wiki/Cross-platform)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Status](https://img.shields.io/badge/Status-Research-blueviolet)](https://en.wikipedia.org/wiki/Research)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Modern, stylish, and professional toolkit for modeling G-induced loss of consciousness (G-LOC) and visualizing aerospace physiology using the FAA’s CGEM foundations. This repository brings together computational models, simulations, and interactive visualizations to support training, safety analysis, and research in aerospace medicine.

Forked from the original FAA AAM-631 CGEM project ("CAMI-Gz-Effects-Model-CGEM-") and extended with modern visualization and configuration tools.

Developed by **Dr. Diego Malpica** (Direction of Aerospace Medicine, Colombian Aerospace Force, Aerospace Scientific Department). ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940).

## Highlights

- **Physiology-aware modeling 🧬**: CGEM-based computations for greyout, blackout, and G-LOC risk.
- **Interactive visualizations 📊**: Streamlit dashboards for scenarios, thresholds, timelines, and maneuver profiles.
- **Reproducible workflows 🔁**: Notebooks and scripts for demos and experiments.
- **Extensible 🧩**: Modular code to customize models, parameters, and data pipelines.

---

## Quick Start ⚡

1. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Linux users: if CGEM fails to run, install the Fortran runtime
# sudo apt-get update && sudo apt-get install -y libgfortran5
```

1. Launch the interactive visualization app

```bash
streamlit run enhanced_app.py
```

1. Run the aerobatic profiles demo (optional)

```bash
python demo_example.py
```

1. Explore notebooks

- Open `aerobatic_profiles_demo.ipynb` or `aerobatic_maneuvers_simulation.ipynb` in your favorite environment.

---

## Features ✨

- Interactive visualization suite
  - 2D Plotly charts: G vs time with safety zones; G_eff vs thresholds (greyout, blackout, G-LOC)
  - 3D Plotly trajectory: time × G × G_eff with state coloring
  - Animated timeline playback for physiological response
  - Scientific dashboard (ECharts): Lines, Heatmap (flags), Histogram (G distribution), Radar (summary metrics), Scatter (state-colored), Durations (time-in-state), Flows (F_con/F_vis/F_bo), Banks (consciousness/blackout), HLAP, and 3D (ECharts GL)
- Pilot physiology configuration
  - Standard physiology presets (`who=1..6`) or fully custom inputs (sex, height, BP ranges, cerebral flow thresholds, heart-response tau, reserve banks)
  - Countermeasures and state: G-suit pressure/coverage, AGSM effectiveness, pressure-breathing, other muscle strain, non-AGSM tensing limit, seat tilt, drug-induced HR delay, dehydration level
  - Result caching per (maneuver × pilot configuration)
- Maneuver library and batch analysis
  - Select any included aerobatic profile; view stats and descriptive analysis
  - Batch run across all maneuvers for comparative metrics and charts
- Centrifuge experiment mode
  - Internal ramp-up/ramp-down experiment driver (G0, Gmax, hold@Gmax, dG/dt up/down)
- CGEM integration
  - Wrapper collects times, G, G_eff, consciousness/vision/blackout flags, time-to-events, flows (F_con/F_vis/F_bo), reserve banks (c_bank/bo_bank), and HLAP series
- Cross-platform research app
  - Streamlit UI; works on Windows, macOS, Linux; Docker recipe included
  - Figures can be downloaded via Plotly/ECharts built-in exporters for reporting

---

## Supported Aerobatic Maneuvers 🛩️

All maneuver inputs live in `Aerobatics_sample_inputs/` and follow the `Nz, duration_ms` format. The application currently includes:

| Identifier | Source file | Description |
|------------|-------------|-------------|
| `hammerhead` | `hammerhead.txt` | Hammerhead (stall-turn): vertical climb, 180° yaw, vertical descent |
| `horizontal_rolling_360` | `horizontalrolling360.txt` | 360° aileron roll while maintaining level flight |
| `outside_360` | `outside360.txt` | 360° outside loop sustaining −G |
| `outside_inside_vert8` | `outsideinsidevertical8.txt` | Vertical figure-of-eight – outside loop bottom, inside loop top |
| `quarter_down_roll` | `quarterdownroll.txt` | Quarter outside loop followed by a downline snap roll |
| `snap_45deg_down_roll` | `snap45degdownroll.txt` | 45° downline with a snap roll |
| `half_vert_roll_neg_pull` | `halfverticalrollwnegpullout.txt` | ½ vertical roll ending with a negative G pull-out |
| `triple_push_pull_loop` | `triple_push_pull_loop.txt` | Triple push–pull loop: repeated push (−G) then pull (+G) ×3 |
| `triple_push_pull_immelmann` | `triple_push_pull_immelmann.txt` | Triple push–pull Immelmann: push–pull + half-roll repeated ×3 |
| `triple_push_pull_split_s` | `triple_push_pull_split_s.txt` | Triple push–pull Split S: three consecutive push–pull Split S entries |
| `high_g_turn` | `high_g_turn.txt` | Sustained high-G level turn with 6–7 G plateau and on/off modulation |
| `loop_standard` | `loop_standard.txt` | Standard loop with 3–5 G pull-up and pull-out phases |
| `immelmann_turn` | `immelmann_turn.txt` | Half-loop to half-roll Immelmann with high +G pull-up |
| `split_s` | `split_s.txt` | Split-S: roll inverted then descending half-loop with high +G pull-out |
| `cuban_eight` | `cuban_eight.txt` | Cuban Eight: two looping segments joined by half-rolls |
| `vertical_eight` | `vertical_eight.txt` | Vertical figure eight with repeated +G exposures and brief −G transitions |

Notes:

- Some entries are conceptual/demo profiles intended for physiology and risk visualization rather than flight training guidance. You can add your own maneuvers by dropping a properly formatted file into `Aerobatics_sample_inputs/` and updating the mapping in `aerobatic_profiles.py`.

---

## Pilot Configuration (Personalized Physiology) 👨‍✈️

You can now personalize the model with pilot-specific parameters from the UI or programmatically. This enables subject-specific predictions and “what-if” countermeasure exploration.

### In the Streamlit apps

- Open either `enhanced_app.py` or `app.py` via Streamlit and locate the “Pilot configuration” panel.
- Choose a profile and set parameters:
  - Standard subject profile (`who`): pick one of 6 standard physiology presets or choose “Custom”.
  - Dehydration level: 0.0–1.0. Applied as a modest reduction in baseline/max BP and normal/max cerebral flow.
  - Countermeasures and state:
    - G-suit max pressure (PSI), suit coverage fraction (0.0–0.7)
    - AGSM effectiveness (0–1), pressure breathing max (mmHg)
    - Pre-test other strain HLAP (mmHg), non-AGSM tensing limit (mmHg)
    - Seat tilt (deg), drug-induced heart-rate response delay (s)
  - If you select “Custom”, additional physiology fields appear:
    - Sex, height (cm)
    - Baseline and max blood pressures (BSP/BDP, MSP/MDP)
    - G tolerance multiplier (gtm) and heart response time constant (beta, s)
    - Consciousness and life reserves (bankcon, banklife, s)

Notes:

- When a standard `who` profile (1..6) is selected, the model’s internal `Subject()` routine overrides subject physiology (flows, BP, sex, height). Your countermeasure and state inputs still apply.
- When “Custom” is selected, the app writes your physiology fields directly to the model input (equivalent to `who=0`).
- The app caches results using both the maneuver and the pilot configuration, so different setups won’t conflict.

### Programmatic use 💻

You can configure and run CGEM directly from Python using `PilotConfig`:

```python
from cgem_wrapper import run_cgem_for_profile, PilotConfig

# Example: standard midrange male with some countermeasures and mild dehydration
cfg = PilotConfig(
    who_profile=2,                 # 1..6 for standard subjects; None for custom
    gsuit_max_psi=5.0,
    gsuit_coverage_fraction=0.35,
    agsm_effectiveness=0.5,
    pbg_max_mmhg=20.0,
    dehydration_level=0.3,
    seat_tilt_deg=10.0,
)

result, tmp_dir = run_cgem_for_profile("hammerhead", config=cfg)
print(result.time_to_greyout_s, result.time_to_blackout_s, result.time_to_gloc_s)
```

Custom physiology example:

```python
cfg = PilotConfig(
    who_profile=None,             # use custom fields below
    male=1, height_cm=176.0,
    baseline_systolic_bp=118.0, baseline_diastolic_bp=78.0,
    max_systolic_bp=185.0, max_diastolic_bp=90.0,
    g_tolerance_multiplier=1.05, heart_response_tau_s=2.3,
    conbank_s=8.0, lifebank_s=180.0,
    agsm_effectiveness=0.6, pbg_max_mmhg=30.0,
    gsuit_max_psi=6.0, gsuit_coverage_fraction=0.4,
    seat_tilt_deg=15.0, drug_delay_s=0.0,
    dehydration_level=0.2,
)
result, _ = run_cgem_for_profile("outside_360", config=cfg)
```

Dehydration mapping (heuristic): decreases baseline/max BP and slightly reduces normal/max flow; intended for exploratory use only.

---

## Contributors & Attribution 🙏

- **Original model (FAA CGEM)**: Developed and maintained within the FAA Civil Aerospace Medical Institute (CAMI), AAM-631. Foundational work by Kyle Copeland (FAA CAMI) and collaborators; see source headers in `src/cgem.f` and the FAA report cited below.
- **This fork and application layer**: **Dr. Diego Malpica** (Direction of Aerospace Medicine, Colombian Aerospace Force, Aerospace Scientific Department). ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940).
- **Upstream origin**: Forked from AAM-631/CAMI-Gz-Effects-Model-CGEM-.

Please retain attribution to the FAA CGEM model and authors in derivative works and cite the original FAA report.

## Acknowledgments 💡

This work is built upon and inspired by foundational research conducted within the **Federal Aviation Administration (FAA)** Office of Aerospace Medicine and decades of operational physiology experience. We gratefully acknowledge the contributions of the **U.S. Military** community—aviators, aircrew, and allied professionals—who served both as scientists and as research participants in the studies underpinning this modeling approach. Their service and commitment to safety and science made this work possible.

Special recognition is due to the FAA researchers and collaborators whose efforts developed, validated, and documented the CGEM approach and related physiology insights.

---

## How to Cite 📝

If you use this repository in academic or technical work, please cite the foundational FAA report:

Malpica, D. (Developer). (2025). CGEM-based G-LOC Modeling and Visualization Suite [Computer software].

And include the original research reference (APA format):

Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow-based computer modeling of Gz-induced effects (DOT/FAA/AM-23/6). Office of Aerospace Medicine, Federal Aviation Administration, Washington, DC.

---

## Disclaimer ⚠️

- This toolkit is intended for research, education, and training support. It does not substitute for operational aeromedical guidance or certification processes.
- This project is not an official product of the FAA or the U.S. Department of Defense. All views expressed are those of the contributors.

---

## Repository Guide 📁

- `enhanced_app.py`: Streamlit UI for interactive modeling and visualization
- `app.py`, `demo_example.py`: Additional demos and app entry points
- `src/`: Core model code (e.g., CGEM implementation and related utilities)
- `Aerobatics_sample_inputs/`: Example input profiles for scenarios
- `docs/`: Guides and related documents
- `notebooks/`: Research and demo notebooks

---

## Running with Conda (recommended for science stacks) 🧪

Create an isolated Conda environment with all dependencies (CPU-only):

```bash
# Create environment
conda create -n cgem-env -y python=3.11

# Activate
conda activate cgem-env

# Core scientific stack
conda install -y -c conda-forge \
  numpy>=1.24 \
  pandas>=2.0 \
  scipy>=1.10 \
  matplotlib>=3.7 \
  seaborn>=0.12 \
  plotly>=5.17 \
  pillow>=10.0 \
  pip

# Streamlit and extras via pip (conda-forge streamlit is OK too)
pip install "streamlit>=1.28"
```

Run the app:

```bash
streamlit run enhanced_app.py
```

Note:

- The CGEM Fortran executable (`cgem`) requires the GNU Fortran runtime. On Linux, ensure `libgfortran5` is installed (e.g., `sudo apt-get install -y libgfortran5`). Inside Conda environments this is typically resolved by the system’s shared libraries.

---

## Dockerization 🐳

Use Docker to run the app with a reproducible environment.

### 1) Build the image

Create a `Dockerfile` in the project root with the following content:

```dockerfile
# Base image with Python and build tools
FROM python:3.11-slim

# Install system dependencies (GNU Fortran runtime for CGEM)
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
      libgfortran5 \
      && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy dependency manifests first (leverage Docker layer caching)
COPY requirements.txt ./

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the repo
COPY . .

# Streamlit configuration (optional)
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose Streamlit default port
EXPOSE 8501

# Default command runs the Streamlit app
CMD ["streamlit", "run", "enhanced_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Then build:

```bash
docker build -t cgem-app:latest .
```

### 2) Run the container

```bash
docker run --rm -p 8501:8501 cgem-app:latest
```

Open the app at `http://localhost:8501`.

### 3) Development mounts (optional)

To iterate on code without rebuilding:

```bash
docker run --rm -p 8501:8501 \
  -v $(pwd):/app \
  cgem-app:latest
```

This mounts your working directory into the container.

---

## Troubleshooting 🛠️

- Missing `libgfortran.so.5` when running CGEM:
  - On Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y libgfortran5`
- Streamlit not installed inside your environment:
  - Recreate your environment and re-run `pip install -r requirements.txt` (or Conda steps above).
- Persisting CGEM temp files:
  - The wrapper now stores run artifacts under `/tmp/cgem_run_*` and returns the path for inspection.

---

## Contact ✉️

Questions, collaborations, or feedback are welcome.

- Lead developer: **Dr. Diego Malpica**
- Please open an issue or pull request to start the conversation.
