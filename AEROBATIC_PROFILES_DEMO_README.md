# Aerobatic Profiles Demonstration

This repository contains a comprehensive demonstration of aerobatic maneuver G-profiles, including data verification, visualization, and analysis tools ready for integration with physiological models like CGEM (Combined G-Effects Model).

## 🎯 Overview

Aerobatic G-profiles represent time-series data of normal acceleration (Nz) values during aerobatic maneuvers. These profiles are essential for:

- **Physiological Modeling**: Integration with CGEM and other medical research models
- **Flight Training Analysis**: Understanding G-force exposure during training
- **Medical Research**: Studying effects of G-forces on human physiology
- **Aircraft Performance Evaluation**: Analyzing maneuver characteristics

## 📁 Files and Structure

### Core Files
- **`aerobatic_profiles.py`** - Main Python module for loading and managing profiles
- **`aerobatic_profiles_demo.ipynb`** - Comprehensive Jupyter notebook demonstration
- **`test_profiles_demo.py`** - Verification script to test all functionality

### Profile Data
- **`Aerobatics_sample_inputs/`** - Directory containing raw profile data files
  - `hammerhead.txt` - Hammerhead (stall-turn) maneuver
  - `horizontalrolling360.txt` - Level flight aileron roll
  - `outside360.txt` - Outside loop with sustained negative G
  - `outsideinsidevertical8.txt` - Vertical figure-eight maneuver
  - `quarterdownroll.txt` - Quarter loop with snap roll
  - `snap45degdownroll.txt` - 45° downline with snap roll
  - `halfverticalrollwnegpullout.txt` - Half vertical roll with negative pullout

### Documentation
- **`README_AEROBATICS.md`** - Technical documentation for the profiles module
- **`AEROBATIC_PROFILES_DEMO_README.md`** - This comprehensive guide

## 🚀 Quick Start

### Prerequisites

Ensure you have the required Python packages installed:

```bash
# Ubuntu/Debian
sudo apt install python3-numpy python3-matplotlib python3-seaborn python3-pandas

# Or using pip (in a virtual environment)
pip install numpy matplotlib seaborn pandas
```

### Verification Test

Run the verification script to ensure everything is working:

```bash
python3 test_profiles_demo.py
```

Expected output:
```
✅ Successfully loaded 7 profiles
✅ Basic plotting functionality works
✅ Statistical analysis completed
✅ All profiles ready for model integration
🎉 ALL SYSTEMS READY FOR JUPYTER NOTEBOOK DEMONSTRATION!
```

### Using the Jupyter Notebook

1. **Start Jupyter** (if available):
   ```bash
   jupyter notebook aerobatic_profiles_demo.ipynb
   ```

2. **Or run cells individually** in your preferred Python environment

## 📊 Available Aerobatic Profiles

| Profile | Duration | G-Range | Samples | Description |
|---------|----------|---------|---------|-------------|
| **Hammerhead** | 24.0s | -2.0G to +2.0G | 22 | Vertical climb, stall-turn, vertical descent |
| **Horizontal Rolling 360** | 29.5s | -3.7G to +2.9G | 33 | 360° aileron roll while maintaining level flight |
| **Outside 360** | 39.0s | -2.0G to +1.0G | 37 | 360° outside loop sustaining −G |
| **Outside Inside Vert8** | 42.0s | -3.2G to +7.8G | 32 | Vertical figure-eight – outside loop bottom, inside loop top |
| **Quarter Down Roll** | 14.5s | -2.2G to +4.1G | 16 | Quarter outside loop followed by downline snap roll |
| **Snap 45° Down Roll** | 16.3s | -3.0G to +6.0G | 18 | 45° downline with a snap roll |
| **Half Vert Roll Neg Pull** | 31.0s | -2.1G to +2.5G | 27 | ½ vertical roll ending with negative G pull-out |

**Total**: 7 profiles, 185 samples, 196.3 seconds of flight data

## 🔧 Programming Interface

### Basic Usage

```python
from aerobatic_profiles import load_all_profiles, load_profile

# Load all profiles
profiles = load_all_profiles()

# Load specific profile
hammerhead_data = load_profile('hammerhead')

# Access data
for sample in hammerhead_data:
    print(f"G: {sample.nz}, Duration: {sample.duration_ms}ms")
```

### Data Structure

Each profile consists of `Sample` objects with:
- **`nz`** (float): Normal acceleration in G-units (+Gz for positive, -Gz for negative)
- **`duration_ms`** (int): Duration in milliseconds for which the G-value is sustained

### Available Profile Identifiers

- `hammerhead`
- `horizontal_rolling_360`
- `outside_360`
- `outside_inside_vert8`
- `quarter_down_roll`
- `snap_45deg_down_roll`
- `half_vert_roll_neg_pull`

## 📈 Demonstration Features

The Jupyter notebook (`aerobatic_profiles_demo.ipynb`) includes:

### 1. Profile Verification
- ✅ Data integrity checks
- ✅ File accessibility verification
- ✅ G-range validation
- ✅ Duration consistency checks

### 2. Individual Profile Visualizations
- Time-series plots for each maneuver
- Positive/negative G highlighting
- Statistical summaries
- Maneuver descriptions

### 3. Comparative Analysis
- All profiles overlaid for comparison
- G-force distribution histograms
- Cross-maneuver statistics

### 4. Statistical Analysis
- Comprehensive statistics table
- Duration analysis
- G-force range analysis
- Weighted mean calculations
- Standard deviation analysis

### 5. Model Integration Readiness
- Validation reports
- Export capabilities
- Integration examples
- Summary statistics

## 🔬 Model Integration

### CGEM Integration

The profiles are ready for direct integration with the Combined G-Effects Model:

```python
# Example CGEM integration
from aerobatic_profiles import load_profile

# Load profile data
profile_data = load_profile('hammerhead')

# Convert to CGEM input format
cgem_input = []
for sample in profile_data:
    cgem_input.append((sample.nz, sample.duration_ms))

# Feed to CGEM model
# model.process_g_profile(cgem_input)
```

### Export Formats

The module supports multiple export formats:

1. **Python Objects** - Direct integration with Python models
2. **CSV Format** - For data analysis and spreadsheet applications
3. **JSON Format** - For web applications and APIs
4. **CGEM Format** - Specific format for physiological modeling

## 🧪 Testing and Validation

### Automated Testing

Run the comprehensive test suite:

```bash
python3 test_profiles_demo.py
```

### Manual Verification

1. **Profile Loading**: Verify all 7 profiles load without errors
2. **Data Integrity**: Check G-values and durations are valid
3. **Visualization**: Confirm plots generate correctly
4. **Statistics**: Validate statistical calculations
5. **Export Functions**: Test various export formats

## 📋 Validation Results

All profiles have been verified as **READY FOR MODEL INTEGRATION**:

- ✅ **Data Integrity**: All samples contain valid G-values and durations
- ✅ **File Accessibility**: All source files are accessible and parseable
- ✅ **G-Range Validity**: All G-values are within reasonable aerobatic limits
- ✅ **Duration Consistency**: All durations are positive integers
- ✅ **Statistical Validity**: All calculations complete successfully

## 🎓 Educational Value

This demonstration serves as:

- **Reference Implementation**: Example of aerobatic data handling
- **Visualization Guide**: Best practices for G-profile visualization
- **Statistical Analysis**: Comprehensive analysis techniques
- **Model Integration**: Ready-to-use integration examples

## 🔍 Technical Details

### Data Format

Each profile file follows this structure:
```
22              ← Number of samples
0.0, 1000       ← G-value, duration_ms
2.0, 1000
0.3, 1000
...
```

### Coordinate System

- **+Gz**: Positive normal acceleration (pilot pressed into seat)
- **-Gz**: Negative normal acceleration (pilot lifted from seat)
- **Duration**: Time in milliseconds each G-value is sustained

### Physiological Significance

- **+2G to +4G**: Mild to moderate physiological stress
- **+4G to +6G**: Significant physiological effects
- **+6G+**: Severe physiological stress, potential G-LOC risk
- **-1G to -3G**: Negative G effects (blood pooling, red-out)

## 🎯 Next Steps

1. **Run the verification test**: `python3 test_profiles_demo.py`
2. **Explore the Jupyter notebook**: Open `aerobatic_profiles_demo.ipynb`
3. **Integrate with your model**: Use the provided API
4. **Extend the dataset**: Add new maneuver profiles as needed

## 📞 Support

For questions, improvements, or bug reports:
- Review the technical documentation in `README_AEROBATICS.md`
- Check the inline code documentation
- Run the test script for diagnostics

---

**🎉 All aerobatic profiles are verified and ready for model integration!**