# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a **CGEM-based G-LOC Modeling and Visualization Suite** for aerospace medicine research. The repository provides Python tools for modeling G-induced loss of consciousness (G-LOC) and visualizing physiological effects during aerobatic maneuvers using the FAA's Combined-G Effects Model (CGEM).

**Key Components:**
- **CGEM Wrapper**: Python interface to Fortran CGEM executable
- **Aerobatic Profiles**: Library of flight maneuver G-force profiles  
- **Streamlit Apps**: Interactive visualization dashboards
- **Medical CLI**: Command-line tool for medical data collection
- **Research Tools**: Jupyter notebooks for analysis and demos

## Core Architecture

### 1. CGEM Integration Layer
- **`cgem_wrapper.py`**: Main interface to CGEM Fortran executable
- **`cgem` executable**: Compiled Fortran model (v1.1.0.1)
- **`gloc_inp.dat`**: CGEM configuration template
- **Input/Output Flow**: Python → EGP files → CGEM → Parsed results

### 2. Aerobatic Profile System  
- **`aerobatic_profiles.py`**: Profile loader and data structures
- **`Aerobatics_sample_inputs/`**: Raw maneuver data files
- **Profile Format**: Text files with `Nz, duration_ms` samples
- **Available Maneuvers**: 16 aerobatic profiles (hammerhead, loops, rolls, etc.)

### 3. Visualization Framework
- **`enhanced_app.py`**: Advanced Streamlit dashboard with physiological analysis
- **`app.py`**: Basic Streamlit interface  
- **Visualization Types**: 2D/3D plots, animated timelines, heatmaps, cardiovascular estimates

### 4. Medical Data Tools
- **`medical_office_cli.py`**: CLI for medical data collection
- **Data Structure**: Patient info, vitals, symptoms, medical history, medications/allergies

## Development Commands

### Environment Setup
```bash
# Virtual environment setup (basic)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Conda environment (recommended for scientific computing)
conda create -n cgem-env -y python=3.11
conda activate cgem-env
conda install -y -c conda-forge numpy pandas scipy matplotlib seaborn plotly pillow pip
pip install "streamlit>=1.28"
```

### Running Applications
```bash
# Main interactive visualization app (recommended)
streamlit run enhanced_app.py

# Basic app
streamlit run app.py

# Run aerobatic profiles demo
python demo_example.py

# Medical data collection CLI
python medical_office_cli.py
```

### Working with Profiles
```bash
# List all available aerobatic profiles
python aerobatic_profiles.py

# Get specific profile data as JSON
python aerobatic_profiles.py hammerhead

# Run CGEM analysis on a profile
python cgem_wrapper.py hammerhead
```

### Testing and Development
```bash
# Test CGEM wrapper functionality  
python -c "from cgem_wrapper import run_cgem_for_profile; print(run_cgem_for_profile('hammerhead'))"

# Validate profile data integrity
python -c "from aerobatic_profiles import load_all_profiles; print(len(load_all_profiles()))"

# Verify citations (if tools are available)
npm run verify:citations

# Clean whitespace issues
python cleanup_whitespace.py
```

## Key Development Patterns

### CGEM Execution Flow
1. **Profile Loading**: Load aerobatic maneuver from text files
2. **EGP Generation**: Convert to CGEM input format (dgdt, duration_ms)
3. **CGEM Execution**: Run Fortran executable in temp directory
4. **Result Parsing**: Extract physiological event times and full time series
5. **Cleanup**: Temp directory preserved for inspection

### Profile Data Structure
```python
@dataclass
class Sample:
    nz: float          # Normal acceleration (G-force)
    duration_ms: int   # Duration in milliseconds

@dataclass 
class CGEMResult:
    time_to_greyout_s: Optional[float]
    time_to_blackout_s: Optional[float] 
    time_to_gloc_s: Optional[float]
    times_s: List[float]           # Full time series
    g_values: List[float]          # G-force values
    geff_values: List[float]       # Effective G values
    flags_n2: List[int]            # Consciousness flags
    # ... additional physiological flags
```

### Pilot Configuration System
```python
# Standard physiology presets (who=1..6) or custom configuration
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
```

### Streamlit App Architecture
- **Caching**: Uses `@st.cache_data` for expensive CGEM computations
- **Tabs**: Multi-tab interface (Profile, Analysis, Details, Comparison, Education)
- **State Management**: Session state for UI persistence
- **Visualization**: Plotly for interactive plots, ECharts for advanced visualizations

## Important File Locations

### Core Python Modules
- `cgem_wrapper.py` - CGEM interface and result parsing
- `aerobatic_profiles.py` - Profile loading and data structures  
- `enhanced_app.py` - Advanced Streamlit visualization app
- `app.py` - Basic Streamlit app
- `medical_office_cli.py` - Medical data collection CLI
- `demo_example.py` - Demo script for profiles

### Data and Configuration
- `Aerobatics_sample_inputs/` - Aerobatic maneuver profiles (16 maneuvers)
- `gloc_inp.dat` - CGEM configuration template
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies (for ECharts)

### Documentation  
- `README.md` - Main repository documentation with full features overview
- `docs/AEROBATIC_PROFILES_DEMO_README.md` - Aerobatic profiles documentation
- `docs/FEATURES_IMPLEMENTATION_ROADMAP.md` - Development roadmap
- `docs/ML_Upgrade_Proposal.md` - Machine learning enhancement plans
- `docs/Variables.md` - Comprehensive list of modeled and missing physiological variables

### Research and Development
- `aerobatic_maneuvers_simulation.ipynb` - Main simulation analysis notebook
- `aerobatic_profiles_demo.py` - Profile demonstration script
- `docs/` - Additional documentation and implementation guides

## System Dependencies

### Required Executables
- **CGEM Fortran executable** (`cgem` or `cgem.exe`)
- **GNU Fortran runtime** (Linux: `libgfortran5`)

### Python Requirements  
- **Core**: pandas>=2.0, numpy>=1.24, matplotlib>=3.7, seaborn>=0.12, plotly>=5.17
- **UI**: streamlit>=1.28, kaleido>=0.2.1
- **Scientific**: scipy>=1.10  
- **Utilities**: Pillow>=10.0, fpdf2>=2.7.9, openpyxl>=3.1.0

### Platform Considerations
- **Windows**: Uses `cgem.exe`, PowerShell-compatible scripts
- **Linux**: Requires `libgfortran5` installation (`sudo apt-get install -y libgfortran5`)
- **Cross-platform**: Docker support available

## Available Aerobatic Maneuvers

The repository includes 16 aerobatic maneuvers in `Aerobatics_sample_inputs/`:

| Identifier | Description |
|------------|-------------|
| `hammerhead` | Hammerhead (stall-turn): vertical climb, 180° yaw, vertical descent |
| `horizontal_rolling_360` | 360° aileron roll while maintaining level flight |
| `outside_360` | 360° outside loop sustaining −G |
| `outside_inside_vert8` | Vertical figure-of-eight – outside loop bottom, inside loop top |
| `quarter_down_roll` | Quarter outside loop followed by a downline snap roll |
| `snap_45deg_down_roll` | 45° downline with a snap roll |
| `half_vert_roll_neg_pull` | ½ vertical roll ending with a negative G pull-out |
| `triple_push_pull_loop` | Triple push–pull loop: repeated push (−G) then pull (+G) ×3 |
| `triple_push_pull_immelmann` | Triple push–pull Immelmann: push–pull + half-roll repeated ×3 |
| `triple_push_pull_split_s` | Triple push–pull Split S: three consecutive push–pull Split S entries |
| `high_g_turn` | Sustained high-G level turn with 6–7 G plateau and on/off modulation |
| `loop_standard` | Standard loop with 3–5 G pull-up and pull-out phases |
| `immelmann_turn` | Half-loop to half-roll Immelmann with high +G pull-up |
| `split_s` | Split-S: roll inverted then descending half-loop with high +G pull-out |
| `cuban_eight` | Cuban Eight: two looping segments joined by half-rolls |
| `vertical_eight` | Vertical figure eight with repeated +G exposures and brief −G transitions |

## Research Context

### Physiological Modeling
- **CGEM v1.1.0.1**: FAA's Combined-G Effects Model
- **Subject Profiles**: 6 standard profiles (midrange male=2 as default)  
- **Thresholds**: Greyout (~4.1 G_eff), Blackout (~5.0 G_eff), G-LOC (~5.5 G_eff)
- **Output Flags**: Consciousness (n2), Vision (ne2), Blackout (non2)

### Future Development Areas
Based on `docs/FEATURES_IMPLEMENTATION_ROADMAP.md`:
- Scenario Builder for multi-leg maneuvers
- ML surrogate models with LightGBM
- Real-time simulator integration
- Enhanced pilot profile parameterization
- Medical CLI TUI improvements

### Missing Physiological Variables
Key variables not fully modeled (from `docs/Variables.md`):
- Sleep quality/duration (highest priority)
- Heart Rate Variability 
- Blood glucose levels
- Core body temperature
- Stress/cortisol levels
- Training recency effects

## Troubleshooting

### Common Issues
- **Missing libgfortran**: Install GNU Fortran runtime on Linux (`sudo apt-get install -y libgfortran5`)
- **CGEM executable not found**: Ensure `cgem`/`cgem.exe` is present and executable
- **Profile loading errors**: Check file format in `Aerobatics_sample_inputs/`
- **Streamlit import errors**: Reinstall requirements, check Python version compatibility

### Debug Commands
```bash
# Test CGEM executable directly
./cgem  # Should run without Python wrapper

# Validate profile data
python -c "from aerobatic_profiles import load_profile; print(load_profile('hammerhead')[:3])"

# Check Streamlit installation  
streamlit --version

# Test medical CLI
python medical_office_cli.py
```

## Docker Usage

```bash
# Build Docker image
docker build -t cgem-app:latest .

# Run container
docker run --rm -p 8501:8501 cgem-app:latest

# Development with volume mount
docker run --rm -p 8501:8501 -v $(pwd):/app cgem-app:latest
```

This repository represents a comprehensive aerospace medicine research toolkit combining computational modeling, data visualization, and medical data management for G-force physiology studies.
