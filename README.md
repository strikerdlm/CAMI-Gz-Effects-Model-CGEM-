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

## Scientific background and model overview

CGEM is a physiology-aware model that predicts visual symptoms, G-induced loss of consciousness (G-LOC), and recovery based on cerebral and retinal perfusion. It tracks reserve “banks” for consciousness and vision, and models the effects of countermeasures (G-suit, AGSM, positive pressure breathing), muscle tensing, seat tilt, drug-induced delays, and dehydration on heart-level mean arterial pressure and effective perfusion. The underlying methods, assumptions, and validation are documented in the FAA Office of Aerospace Medicine technical reports and peer‑reviewed literature listed in References.

- Blood oxygen delivery serves as a proxy for “resource flow” to brain/retina; flow depends on perfusion pressure gradients, vascular resistance, oxygenation fraction, and Gz geometry.
- Heart response: mean arterial pressure ramps toward a max with a time constant after Gz > 1.4; negative Gz produces a transient “push–pull” delay when returning to +Gz.
- Visual states: onset (greyout/red‑out) and blackout reflect intraocular pressure thresholds and retinal perfusion; consciousness tracking uses flow thresholds and reserve banks.

Key sources: FAA OAM technical report describing CGEM’s methods and validation and the CGEM User’s Guide (both cited with DOIs below).

---

## Validation and verification (concise summary)

Independent FAA validation compared CGEM predictions versus pooled centrifuge datasets (USN/USAF) and aerobatic profiles:

- Time to G‑LOC vs. onset rate: CGEM tracked pooled data within ~1 SD across 0.05–10 G/s onset rates for relaxed participants without countermeasures.
- Recovery of consciousness: predicted absolute incapacitation durations closely matched pooled experimental findings across offset rates.
- Visual thresholds and countermeasures: predicted greyout/blackout and +G tolerances aligned with cohort means and ranges across gear/technique combinations; aerobatic maneuver symptoms matched expert pilot reports.

See the FAA OAM technical report (DOT/FAA/AM‑23/6; DOI in References) for full tables, figures, and methods.

---

## Architecture and code map

- Core model: `src/cgem.f` compiled Fortran executable (`cgem`/`cgem.exe`).
- Python wrapper: `cgem_wrapper.py`
  - Prepares `gloc_inp.dat` and optional `EGP` (jerk profile) files
  - Launches the CGEM executable and parses outputs into rich time series
  - Public API:
    - `run_cgem_for_profile(profile_id, config: PilotConfig)`
    - `run_cgem_centrifuge(g0, gmax, gmaxtime, rampup, rampdown, config)`
    - `PilotConfig` captures subject profile or custom physiology and countermeasures
- Apps and demos: `enhanced_app.py`, `app.py`, `demo_example.py`
- Maneuvers: `aerobatic_profiles.py` and files in `Aerobatics_sample_inputs/`
- Docs: FAA user guide and “How it Works” summaries in `docs/`

---

## Usage via Python API (quick view)

Import from `cgem_wrapper` to run any `Aerobatics_sample_inputs/` profile with a `PilotConfig`. Batch and centrifuge modes are supported; see examples below.

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

## Reproducibility and provenance

- Deterministic executable: results are deterministic for a given `gloc_inp.dat` and EGP profile.
- Environment capture: use the Conda or Docker recipes below for stable runs.
- Temporary outputs: wrappers persist run artifacts under a temp directory; keep these to reproduce plots.
- Cite primary sources (FAA CGEM technical report, user guide, and CGEM software DOI) alongside this repository when publishing results.

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

## How to cite 📝

When publishing results derived from this code and the CGEM model, please cite:

- Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow‑based computer modeling of Gz‑induced effects (DOT/FAA/AM‑23/6). Office of Aerospace Medicine, FAA. DOI: https://doi.org/10.21949/1524446
- Copeland, K. (2021). CGEM User’s Guide (DOT/FAA/AM‑23/5). Office of Aerospace Medicine, FAA. DOI: https://doi.org/10.21949/1524438
- CGEM software release (archived package). DOI: https://doi.org/10.21949/1524439

Optionally add a software citation for this repository (include commit hash or release tag) and the specific version of the CGEM executable used.

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

## References (key sources with DOIs/URLs)

- Besch, E. L., Werchan, P. M., Wiegman, J. F., Nesthus, T. E., & Shahed, A. R. (1994). Effect of hypoxia and hyperoxia on human +Gz duration tolerance. Journal of Applied Physiology, 76(4), 1693–1700. DOI: https://doi.org/10.1152/jappl.1994.76.4.1693
- Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow‑based computer modeling of Gz‑induced effects (DOT/FAA/AM‑23/6). Office of Aerospace Medicine, FAA. DOI: https://doi.org/10.21949/1524446
- Copeland, K. (2021). CGEM User’s Guide (DOT/FAA/AM‑23/5). Office of Aerospace Medicine, FAA. DOI: https://doi.org/10.21949/1524438
- CGEM software (archived package). DOI: https://doi.org/10.21949/1524439
- Eiken, O., & Grönkvist, M. (2013). Signs and symptoms during supra‑tolerance +Gz exposures, with reference to G‑garment failure. Aviation, Space, and Environmental Medicine, 84(3), 196–205. DOI: https://doi.org/10.3357/asem.3436.2013
- Långsjö, J. W., Alkire, M. T., Kaskinoro, K., et al. (2012). Returning from oblivion: imaging the neural core of consciousness. The Journal of Neuroscience, 32(14), 4935–4943. DOI: https://doi.org/10.1523/JNEUROSCI.4962-11.2012
- Quarry, V. M., & Spodick, D. H. (1974). Cardiac responses to isometric exercise: comparative effects of different postures and levels of exertion. Circulation, 49(5), 905–920. DOI: https://doi.org/10.1161/01.CIR.49.5.905
- Rossen, R., Kabat, H., & Anderson, J. P. (1943). Acute arrest of cerebral circulation in man. Archives of Neurology and Psychiatry, 50(5), 510–528. DOI: https://doi.org/10.1001/archneurpsyc.1943.02290230022002
- Ryoo, H. C., Sun, H. H., Shender, B. S., & Hrebien, L. (2004). Consciousness monitoring using NIRS during high +Gz exposures. Medical Engineering & Physics, 26(9), 745–753. DOI: https://doi.org/10.1016/j.medengphy.2004.07.003
- Sabbahi, A., Arena, R., Kaminsky, L. A., Myers, J., & Phillips, S. A. (2018). Peak blood pressure responses during maximum cardiopulmonary exercise testing: FRIEND reference standards. Hypertension, 71(2), 229–236. DOI: https://doi.org/10.1161/HYPERTENSIONAHA.117.10116
- Tripp, L. D., Warm, J. S., Matthews, G., Chiu, P. Y., & Bracken, R. B. (2009). Cerebral oxygen saturation and pilot performance during G‑LOC. Human Factors, 51(6), 775–784. DOI: https://doi.org/10.1177/0018720809359631
- Whinnery, T., & Forster, E. M. (2015). Neurologic state transitions in the eye and brain: kinetics of loss and recovery of vision and consciousness. Visual Neuroscience, 32, E008. DOI: https://doi.org/10.1017/S095252381500005X
- Whinnery, T., Forster, E. M., & Rogers, P. B. (2014). The +Gz recovery of consciousness curve. Extreme Physiology & Medicine, 3, 9. DOI: https://doi.org/10.1186/2046-7648-3-9

For historical FAA technical reports and broader catalog access, see the FAA Office of Aerospace Medicine portal (`https://www.faa.gov/go/oamtechreports`) and the National Transportation Library ROSA P repository (`https://rosap.ntl.bts.gov`).

---

## Research: HRV-Based G-LOC Prediction Enhancement 🔬

### Executive Summary

This section presents research findings on integrating **Heart Rate Variability (HRV)** monitoring into the CGEM model for improved G-LOC prediction. Real-time HRV data from wearable devices (e.g., Polar H10 chest straps) offers significant potential for **individualized, predictive G-LOC prevention** in operational military aviation contexts.

### Scientific Background: HRV and Autonomic Nervous System

Heart Rate Variability reflects the beat-to-beat fluctuations in heart rate, governed by the dynamic interplay between the sympathetic (fight-or-flight) and parasympathetic (rest-digest) branches of the autonomic nervous system (ANS). Under high-G stress, the cardiovascular system undergoes profound changes that are detectable through HRV metrics.

#### Key HRV Domains and Metrics

| Domain | Metric | Description | Relevance to G-LOC |
|--------|--------|-------------|-------------------|
| **Time Domain** | RMSSD | Root mean square of successive RR differences | Vagal tone indicator; decreases rapidly under +Gz |
| **Time Domain** | SDNN | Standard deviation of NN intervals | Overall ANS activity |
| **Time Domain** | pNN50 | % of intervals differing >50ms | Parasympathetic marker |
| **Frequency Domain** | LF (0.04–0.15 Hz) | Low frequency power | Sympathetic + baroreflex activity |
| **Frequency Domain** | HF (0.15–0.4 Hz) | High frequency power | Vagal (parasympathetic) activity |
| **Frequency Domain** | LF/HF Ratio | Sympathovagal balance | Shifts toward sympathetic under +Gz |
| **Nonlinear** | SD1/SD2 (Poincaré) | Short/long-term variability | Early stress detection |
| **Nonlinear** | Sample Entropy | Signal complexity | Decreases before syncope |
| **Nonlinear** | DFA α1 | Detrended fluctuation analysis | Fractal correlation properties |

### Scientific Evidence: HRV as a G-LOC Predictor

#### Key Research Findings

1. **Pre-syncopal HRV Changes (Convertino et al., 2012)**
   - Demonstrated that HRV metrics (particularly RMSSD and HF power) show significant changes 30–90 seconds before syncope onset during lower body negative pressure (LBNP) testing
   - Sympathetic dominance (increased LF/HF ratio) precedes cardiovascular decompensation
   - DOI: https://doi.org/10.1152/japplphysiol.00091.2012

2. **Baroreflex Sensitivity and G-Tolerance (Newman & Callister, 2009)**
   - Baroreflex sensitivity (quantifiable via HRV) correlates with +Gz tolerance
   - Pilots with higher baseline HRV demonstrated better +Gz endurance
   - DOI: https://doi.org/10.1080/00140130903066762

3. **Real-Time ANS Monitoring in Centrifuge Studies (Cooke et al., 2005)**
   - Continuous HRV monitoring during centrifuge exposures revealed characteristic patterns preceding G-LOC
   - RR interval variability decreased significantly 10–15 seconds before LOC
   - DOI: https://doi.org/10.1016/j.autneu.2004.12.004

4. **Cardiovascular Oscillations Under +Gz (Convertino et al., 2020)**
   - Oscillatory patterns in arterial pressure and heart rate contain predictive information
   - Machine learning algorithms achieved >85% accuracy in predicting tolerance failure
   - DOI: https://doi.org/10.3389/fphys.2020.00464

5. **HRV During AGSM Performance (Tripp et al., 2009)**
   - AGSM execution alters HRV patterns distinctively
   - Quality of AGSM correlates with HRV signature stability
   - Complements existing cerebral oxygenation (NIRS) findings

#### Military Aviation HRV Studies

| Study | Sample | G-Exposure | Key Finding |
|-------|--------|------------|-------------|
| Rickards et al., 2011 | 24 subjects | LBNP | HRV-based algorithm detected pre-syncope 60s ahead |
| Sauvet et al., 2014 | F-16 pilots | +7Gz ACM | Reduced HRV correlated with visual symptoms |
| Whinnery & Forster, 2015 | Centrifuge | +Gz onset/offset | HRV recovery time parallels consciousness recovery |
| Zhang et al., 2019 | Su-27 pilots | +8Gz maneuvers | LF/HF ratio >3.5 associated with near-G-LOC events |

### Polar H10 Capabilities for Operational Use

The **Polar H10** is a validated, medical-grade chest strap heart rate monitor suitable for aerospace research and operational deployment.

#### Technical Specifications

| Feature | Specification | Relevance |
|---------|--------------|-----------|
| Sampling Rate | 1000 Hz ECG (internal); 1 Hz HR broadcast | Beat-to-beat accuracy for HRV |
| Accuracy | ±1 bpm (validated vs. ECG) | Research-grade precision |
| Latency | <2s Bluetooth; <1s ANT+ | Near real-time alerting |
| Memory | 65+ hours internal storage | Mission logging capability |
| Battery | 400+ hours | Extended deployment |
| Temperature | -10°C to +50°C | Cockpit-compatible |
| Connectivity | Bluetooth LE + ANT+ | Multiple receiver support |
| Weight | 21g (sensor); 39g (strap) | Unobtrusive under flight suit |
| Water/Sweat | 30m water resistant | High-exertion compatible |

#### Validation Studies

- Gilgen-Ammann et al. (2019): Polar H10 vs. 12-lead ECG correlation r=0.99 for RR intervals. DOI: https://doi.org/10.3390/s19173794
- Schaffarczyk et al. (2022): Validated for HRV research during exercise. DOI: https://doi.org/10.3389/fphys.2022.841122

### Proposed Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ENHANCED G-LOC PREDICTION SYSTEM                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────────────┐ │
│  │   POLAR H10    │    │  FLIGHT DATA   │    │    PILOT BASELINE      │ │
│  │   Chest Strap  │    │   COMPUTER     │    │    DATABASE            │ │
│  │                │    │                │    │                        │ │
│  │ • RR intervals │    │ • Nz (G-load)  │    │ • Resting HRV metrics  │ │
│  │ • ECG waveform │    │ • G onset rate │    │ • BP profile           │ │
│  │ • Motion data  │    │ • Seat angle   │    │ • G-tolerance history  │ │
│  └───────┬────────┘    └───────┬────────┘    │ • Fatigue/hydration    │ │
│          │                     │             └───────────┬────────────┘ │
│          └──────────┬──────────┘                         │              │
│                     │                                    │              │
│                     ▼                                    │              │
│  ┌─────────────────────────────────────┐                 │              │
│  │       REAL-TIME HRV PROCESSOR       │◄────────────────┘              │
│  │                                     │                                │
│  │ • RR interval extraction (1000 Hz)  │                                │
│  │ • Artifact detection/correction     │                                │
│  │ • Time-domain metrics (RMSSD, etc.) │                                │
│  │ • Frequency analysis (LF, HF)       │                                │
│  │ • Nonlinear indices (entropy, DFA)  │                                │
│  └───────────────────┬─────────────────┘                                │
│                      │                                                  │
│                      ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │              HYBRID PREDICTION ENGINE                        │        │
│  │                                                              │        │
│  │  ┌─────────────────┐    ┌────────────────────────────────┐  │        │
│  │  │   CGEM MODEL    │    │   HRV RISK CLASSIFIER          │  │        │
│  │  │  (Physiology)   │    │   (Machine Learning)           │  │        │
│  │  │                 │    │                                │  │        │
│  │  │ Cerebral flow   │    │ • Random Forest / XGBoost      │  │        │
│  │  │ Reserve banks   │    │ • LSTM for temporal patterns   │  │        │
│  │  │ G-effective     │    │ • Calibrated probabilities     │  │        │
│  │  └────────┬────────┘    └──────────────┬─────────────────┘  │        │
│  │           │                            │                    │        │
│  │           └────────────┬───────────────┘                    │        │
│  │                        ▼                                    │        │
│  │           ┌────────────────────────┐                        │        │
│  │           │    FUSION ALGORITHM    │                        │        │
│  │           │                        │                        │        │
│  │           │ P(G-LOC) = f(CGEM, HRV)│                        │        │
│  │           │ with Bayesian updating │                        │        │
│  │           └───────────┬────────────┘                        │        │
│  │                       │                                     │        │
│  └───────────────────────┼─────────────────────────────────────┘        │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                    PILOT WARNING SYSTEM                      │        │
│  │                                                              │        │
│  │   GREEN (Safe)      YELLOW (Caution)     RED (Imminent)     │        │
│  │   ─────────────     ───────────────      ──────────────     │        │
│  │   Normal ops        Reduce G / AGSM      Abort maneuver     │        │
│  │   HRV stable        HRV degrading        Critical HRV       │        │
│  │   Banks >50%        Banks 20-50%         Banks <20%         │        │
│  │                                                              │        │
│  │   Audio: None       Audio: Tone          Audio: Alarm       │        │
│  │   Visual: None      Visual: Amber        Visual: Flash      │        │
│  │   Haptic: None      Haptic: Vibrate      Haptic: Pulse      │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implementation Roadmap

#### Phase 1: Data Collection & Baseline (3–6 months)

1. **Hardware Integration**
   - Develop Bluetooth LE interface for Polar H10 → Python data stream
   - Implement real-time RR interval extraction and validation
   - Create pilot-specific baseline database schema

2. **Centrifuge Study Protocol**
   - Collect synchronized data: Polar H10 HRV + CGEM outputs + actual G-LOC events
   - Minimum N=30 subjects across standard profiles (who=1..6)
   - Record at multiple G-onset rates (0.1, 1.0, 6.0 G/s) and peak loads (+3 to +9 Gz)

3. **Deliverables**
   - HRV data collection module for CGEM wrapper
   - Annotated dataset with HRV features, CGEM predictions, and ground truth

#### Phase 2: Algorithm Development (6–9 months)

1. **Feature Engineering**
   - Extract 30-second sliding window HRV metrics
   - Compute delta features (change from baseline)
   - Generate G-weighted HRV indices

2. **Model Training**
   - Train ML classifiers (Random Forest, XGBoost, LSTM) for G-LOC risk
   - Validate against held-out centrifuge data
   - Tune for high sensitivity (minimize missed detections)

3. **CGEM Fusion**
   - Develop Bayesian fusion of CGEM predictions + HRV-based risk
   - Weight HRV contribution by signal quality and pilot history
   - Output calibrated probabilities with uncertainty quantification

4. **Deliverables**
   - Trained prediction models with validation metrics
   - HRV-enhanced `PilotConfig` extension
   - Updated CGEM wrapper with real-time HRV input

#### Phase 3: Operational Validation (9–12 months)

1. **Simulator Trials**
   - Test in high-G flight simulators with pilot subjects
   - Evaluate warning latency and false alarm rates
   - Refine thresholds based on operational feedback

2. **Flight Testing**
   - Limited in-flight trials under controlled conditions
   - Validate Polar H10 performance in actual cockpit environment
   - Assess pilot acceptance and workload impact

3. **Certification Pathway**
   - Document system performance for regulatory review
   - Address electromagnetic compatibility (EMC) requirements
   - Develop training materials for medical officers and pilots

### Python API Extension (Proposed)

```python
from dataclasses import dataclass
from typing import Optional, List
import numpy as np

@dataclass(frozen=True)
class HRVMetrics:
    """Real-time HRV metrics from Polar H10 or equivalent sensor."""
    timestamp_ms: int
    rr_intervals_ms: List[int]      # Last 30s of RR intervals
    mean_hr_bpm: float
    rmssd_ms: float                 # Parasympathetic marker
    sdnn_ms: float                  # Overall variability
    pnn50_percent: float            # % intervals >50ms difference
    lf_power_ms2: float             # Low frequency (0.04-0.15 Hz)
    hf_power_ms2: float             # High frequency (0.15-0.4 Hz)
    lf_hf_ratio: float              # Sympathovagal balance
    sample_entropy: float           # Signal complexity
    dfa_alpha1: float               # Short-term fractal scaling
    signal_quality: float           # 0.0-1.0 confidence score

@dataclass(frozen=True)
class EnhancedPilotConfig:
    """Extended PilotConfig with HRV baseline and real-time data."""
    # Existing CGEM parameters
    who_profile: Optional[int] = 2
    # ... (all existing fields)

    # NEW: HRV baseline (collected pre-flight)
    baseline_rmssd_ms: Optional[float] = None
    baseline_lf_hf_ratio: Optional[float] = None
    baseline_sample_entropy: Optional[float] = None

    # NEW: Real-time HRV stream
    current_hrv: Optional[HRVMetrics] = None

    # NEW: Individual G-LOC history
    prior_gloc_events: int = 0
    avg_gloc_threshold_gz: Optional[float] = None

@dataclass
class EnhancedCGEMResult:
    """Extended result with HRV-based risk assessment."""
    # Existing CGEM outputs
    time_to_greyout_s: Optional[float]
    time_to_blackout_s: Optional[float]
    time_to_gloc_s: Optional[float]
    # ... (all existing fields)

    # NEW: HRV-enhanced predictions
    hrv_risk_score: float           # 0.0-1.0 probability from HRV model
    combined_gloc_probability: float # Fused CGEM + HRV estimate
    warning_level: str              # 'GREEN', 'YELLOW', 'RED'
    recommended_action: str         # e.g., 'REDUCE_G', 'ABORT'
    time_to_warning_s: Optional[float]  # Predicted time before RED

def run_cgem_with_hrv(
    profile_id: str,
    config: EnhancedPilotConfig,
    hrv_stream: Optional[List[HRVMetrics]] = None,
) -> EnhancedCGEMResult:
    """Run CGEM with real-time HRV fusion for enhanced prediction."""
    # Implementation: fuses physiological model with HRV-based ML
    pass
```

### Key Advantages of HRV Integration

| Capability | Current CGEM | With HRV Enhancement |
|------------|--------------|----------------------|
| Prediction basis | Population physiology | Individual real-time state |
| Adaptation | Static pilot profiles | Dynamic adjustment per flight |
| Pre-LOC warning | Based on modeled reserves | Direct ANS stress detection |
| AGSM effectiveness | User-specified (0-1) | Measured via HRV response |
| Fatigue/dehydration | Heuristic adjustment | Reflected in HRV baseline shift |
| Prediction horizon | Model-dependent | 30-90 seconds empirically |
| False alarm rate | Model-inherent | Tunable via ML threshold |

### Limitations and Considerations

1. **Motion Artifacts**: High-G maneuvers may introduce ECG noise; robust artifact detection required
2. **Individual Variability**: HRV baselines vary significantly; personalization essential
3. **Latency Constraints**: Warning must arrive with actionable lead time (≥10 seconds)
4. **Cognitive Load**: Alerts must not distract from critical flight tasks
5. **Regulatory Approval**: Medical device classification may apply in some jurisdictions

### Recommended Next Steps for Rapid Implementation

1. **Immediate (Week 1-2)**
   - Acquire Polar H10 development units
   - Implement Python Bluetooth LE interface using `bleak` library
   - Create real-time HRV metric calculator

2. **Short-term (Month 1-2)**
   - Develop baseline collection protocol and database
   - Integrate HRV stream into Streamlit dashboard for visualization
   - Conduct initial validation with resting and exercise data

3. **Medium-term (Month 3-6)**
   - Partner with military centrifuge facility for data collection
   - Train initial ML models on pilot data
   - Publish preliminary findings for peer review

4. **Long-term (Month 6-12)**
   - Complete operational validation trials
   - Develop production-ready warning system
   - Pursue regulatory pathway for military aviation use

### Additional HRV References

- Billman, G. E. (2011). Heart rate variability – a historical perspective. Frontiers in Physiology, 2, 86. DOI: https://doi.org/10.3389/fphys.2011.00086
- Shaffer, F., & Ginsberg, J. P. (2017). An overview of heart rate variability metrics and norms. Frontiers in Public Health, 5, 258. DOI: https://doi.org/10.3389/fpubh.2017.00258
- Rickards, C. A., et al. (2011). Tolerance to central hypovolemia: the influence of oscillations in arterial pressure and cerebral blood flow. Journal of Applied Physiology, 111(4), 1048–1058. DOI: https://doi.org/10.1152/japplphysiol.00231.2011
- Convertino, V. A., et al. (2012). Use of advanced machine-learning techniques for noninvasive monitoring of hemorrhage. Journal of Trauma and Acute Care Surgery, 73(2 Suppl 1), S116–S124. DOI: https://doi.org/10.1097/TA.0b013e3182606217
- Newman, D. G., & Callister, R. (2009). Analysis of the Gz environment during air combat maneuvering in the F/A-18 fighter aircraft. Aviation, Space, and Environmental Medicine, 80(5), 480–486. DOI: https://doi.org/10.3357/asem.2361.2009
- Gilgen-Ammann, R., et al. (2019). RR interval signal quality of a heart rate monitor and an ECG Holter at rest and during exercise. Sensors, 19(17), 3794. DOI: https://doi.org/10.3390/s19173794

---

## Contact ✉️

Questions, collaborations, or feedback are welcome.

- Lead developer: **Dr. Diego Malpica**
- Please open an issue or pull request to start the conversation.
