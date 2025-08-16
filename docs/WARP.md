# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a **CGEM-based G-LOC Modeling and Visualization Suite** for aerospace medicine research. The repository provides Python tools for modeling G-induced loss of consciousness (G-LOC) and visualizing physiological effects during aerobatic maneuvers using the FAA's Combined-G Effects Model (CGEM).

**Key Components:**
- **CGEM Wrapper**: Python interface to Fortran CGEM executable
- **Aerobatic Profiles**: Library of flight maneuver G-force profiles
- **Streamlit Apps**: Interactive visualization dashboards
- **Medical CLI**: Command-line tool for medical data collection
- **Research Notebooks**: Jupyter notebooks for analysis and demos

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
- **Available Maneuvers**: 7 aerobatic profiles (hammerhead, outside loops, rolls, etc.)

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
# Virtual environment setup
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Conda environment (recommended for scientific computing)
conda create -n cgem-env -y python=3.11
conda activate cgem-env
conda install -y -c conda-forge numpy pandas scipy matplotlib seaborn plotly pillow pip
pip install "streamlit>=1.28"
```

### Running Applications
```bash
# Main interactive visualization app
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
# Run profile demo tests
python test_profiles_demo.py

# Test CGEM wrapper functionality
python -c "from cgem_wrapper import run_cgem_for_profile; print(run_cgem_for_profile('hammerhead'))"

# Validate profile data integrity
python -c "from aerobatic_profiles import load_all_profiles; print(len(load_all_profiles()))"
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

### Streamlit App Architecture
- **Caching**: Uses `@st.cache_data` for expensive CGEM computations
- **Tabs**: Multi-tab interface (Profile, Analysis, Details, Comparison, Education)
- **State Management**: Session state for UI persistence
- **Visualization**: Plotly for interactive plots, Matplotlib for static plots

## Important File Locations

### Core Python Modules
- `cgem_wrapper.py` - CGEM interface and result parsing
- `aerobatic_profiles.py` - Profile loading and data structures
- `enhanced_app.py` - Advanced Streamlit visualization app
- `medical_office_cli.py` - Medical data collection CLI

### Data and Configuration
- `Aerobatics_sample_inputs/` - Aerobatic maneuver profiles
- `gloc_inp.dat` - CGEM configuration template
- `requirements.txt` - Python dependencies
- `sample_medical_data.json` - Example medical data format

### Documentation
- `README.md` - Main repository documentation
- `README_AEROBATICS.md` - Aerobatic profiles documentation  
- `FEATURES_IMPLEMENTATION_ROADMAP.md` - Development roadmap
- `ML_Upgrade_Proposal.md` - Machine learning enhancement plans

### Research and Development
- `notebooks/` - Jupyter notebooks for analysis
- `aerobatic_profiles_demo.ipynb` - Profile demonstration notebook
- `aerobatic_maneuvers_simulation.ipynb` - Simulation analysis
- `docs/` - Additional documentation and guides

## System Dependencies

### Required Executables
- **CGEM Fortran executable** (`cgem` or `cgem.exe`)
- **GNU Fortran runtime** (Linux: `libgfortran5`)

### Python Requirements
- **Core**: pandas, numpy, matplotlib, seaborn, plotly, streamlit
- **Scientific**: scipy (for advanced computations)
- **Utilities**: Pillow (image processing)

### Platform Considerations
- **Windows**: Uses `cgem.exe`, PowerShell-compatible scripts
- **Linux**: Requires `libgfortran5` installation
- **Cross-platform**: Docker support available

## Research Context

### Physiological Modeling
- **CGEM v1.1.0.1**: FAA's Combined-G Effects Model
- **Subject Profiles**: Midrange male (who=2) as default
- **Thresholds**: Greyout (~4.1 G_eff), Blackout (~5.0 G_eff), G-LOC (~5.5 G_eff)
- **Output Flags**: Consciousness (n2), Vision (ne2), Blackout (non2)

### Aerobatic Maneuvers
- **7 Standard Profiles**: Hammerhead, rolls, loops, vertical maneuvers
- **Data Format**: Time-series of G-force and duration pairs
- **Sampling Rate**: Variable duration samples (millisecond precision)

### Medical Applications
- **Training Support**: Pilot physiological education
- **Safety Analysis**: G-force exposure assessment  
- **Research Tool**: Aerospace medicine studies

## Development Notes

- **CGEM Integration**: Fortran executable must be present and executable
- **Temp Directory Management**: CGEM runs create temp dirs for inspection
- **Error Handling**: Robust parsing for CGEM output format variations
- **Performance**: CGEM computations are cached for repeated UI operations
- **Extensibility**: Modular design allows easy addition of new profiles and visualizations

## Troubleshooting

### Common Issues
- **Missing libgfortran**: Install GNU Fortran runtime on Linux
- **CGEM executable not found**: Ensure `cgem`/`cgem.exe` is present and executable
- **Profile loading errors**: Check file format in `Aerobatics_sample_inputs/`
- **Streamlit import errors**: Reinstall requirements, check Python version

### Debug Commands
```bash
# Test CGEM executable
./cgem  # Should run without Python wrapper

# Validate profile data
python -c "from aerobatic_profiles import load_profile; print(load_profile('hammerhead')[:3])"

# Check Streamlit installation
streamlit --version

# Test medical CLI
python medical_office_cli.py
```

This repository represents a comprehensive aerospace medicine research toolkit combining computational modeling, data visualization, and medical data management for G-force physiology studies.
