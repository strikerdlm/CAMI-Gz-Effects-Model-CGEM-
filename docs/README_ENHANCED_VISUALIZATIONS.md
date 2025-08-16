# Enhanced Aerobatic G-Profile Physiological Visualization System

## Overview
This enhanced visualization system provides comprehensive, scientifically accurate visualizations of physiological changes during flight maneuvers. The system includes 2D plots, 3D trajectories, animated timelines, and detailed physiological analysis for each aerobatic maneuver.

## Features

### 🎯 Advanced Visualizations
- **2D Physiological Plots**: Interactive plots showing G-forces and effective G with physiological zones and thresholds
- **3D Trajectory Visualization**: 3D representation of the physiological state evolution during maneuvers
- **Animated Timeline**: Real-time animation showing the progression of physiological stress
- **Physiological Heatmap**: Comprehensive view of all parameters over time
- **Cardiovascular Response**: Estimated heart rate and blood pressure responses

### 🧬 Physiological Analysis
- Real-time G-LOC, blackout, and greyout risk assessment
- Physiological state tracking with color-coded indicators
- Threshold-based warnings and alerts
- Detailed explanations for each maneuver

### 📊 Maneuver-Specific Features
Each maneuver includes:
- Detailed description and physiological effects
- Risk factors and mitigation strategies
- Critical event timing (greyout, blackout, G-LOC)
- Comparative analysis across all maneuvers

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Instructions

1. **Clone the repository** (if not already done):
```bash
git clone <repository-url>
cd <repository-directory>
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify CGEM executable**:
Ensure the `cgem` executable has proper permissions:
```bash
chmod +x cgem
```

## Running the Application

### Standard Visualization App
To run the original app:
```bash
streamlit run app.py
```

### Enhanced Visualization App
To run the enhanced visualization system with advanced features:
```bash
streamlit run enhanced_app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage Guide

### 1. Select a Maneuver
- Use the sidebar dropdown to select an aerobatic maneuver
- View the maneuver description in the sidebar

### 2. Configure Visualization Options
In the sidebar, enable/disable:
- 2D Physiological Plots
- 3D Trajectory Plot
- Animated Timeline
- Parameter Heatmap
- Cardiovascular Response

### 3. Run Physiological Simulation
- Navigate to the "Physiological Analysis" tab
- Click "Run CGEM Physiological Simulation"
- View the generated visualizations and analysis

### 4. Explore Different Tabs

#### 📈 Profile Overview
- View the basic G-force profile
- See key statistics (duration, max/min G, etc.)

#### 🧬 Physiological Analysis
- Run simulations and view all enabled visualizations
- Check critical physiological events
- Explore interactive plots

#### 🎯 Maneuver Details
- Read detailed explanations of physiological effects
- Review risk factors and mitigation strategies
- See timing of critical events

#### 📊 Comparative Analysis
- Run batch analysis across all maneuvers
- Compare G-forces and physiological impacts
- View aggregated statistics

#### 📚 Educational Resources
- Learn about G-forces and physiology
- Understand mitigation techniques
- Get help interpreting visualizations

## Visualization Types Explained

### 2D Physiological Plots
- **Top Graph**: Shows actual G-forces with color-coded safety zones
  - Green: Safe zone for untrained individuals
  - Yellow: Trained pilot zone
  - Red: Extreme risk zones
- **Bottom Graph**: Effective G (G_eff) with physiological thresholds
  - Orange line: Greyout threshold
  - Red line: Blackout threshold
  - Dark red line: G-LOC threshold

### 3D Trajectory Plot
- **Axes**: Time (X), G-Force (Y), Effective G (Z)
- **Color Coding**: Physiological state at each point
- **Threshold Planes**: Visual representation of critical boundaries

### Animated Timeline
- Shows real-time progression of G and G_eff
- Play/Pause controls for detailed analysis
- Slider for manual time navigation

### Physiological Heatmap
- Rows represent different parameters
- Color intensity indicates parameter values
- Quickly identify critical time periods

### Cardiovascular Response
- Estimated heart rate and blood pressure changes
- Normal range indicators
- Response patterns to G-loading

## Interpreting Results

### Critical Events
- **Greyout**: Peripheral vision loss, typically at ~4.1 G_eff
- **Blackout**: Complete vision loss, typically at ~5.0 G_eff
- **G-LOC**: Loss of consciousness, typically at ~5.5 G_eff
- **Redout**: Risk with negative G below -2.0

### Color Codes
- 🟢 **Green**: Normal/Safe state
- 🟡 **Yellow**: Caution required
- 🟠 **Orange**: Warning - approaching limits
- 🔴 **Red**: Danger - critical state
- ⚫ **Black**: Extreme danger/incapacitation

## Advanced Features

### Pilot Profile Selection
Choose training level to adjust analysis:
- Untrained
- Basic Training
- Advanced Training
- Fighter Pilot

### Batch Analysis
Run analysis on all maneuvers simultaneously for comparison

### Export Options
- Save plots as images
- Export data for further analysis

## Troubleshooting

### Common Issues

1. **CGEM executable not found**:
   - Ensure `cgem` file is in the project directory
   - Check file permissions: `chmod +x cgem`

2. **Missing dependencies**:
   - Run `pip install -r requirements.txt`
   - For plotly issues: `pip install plotly --upgrade`

3. **Simulation fails**:
   - Check that input files are in `Aerobatics_sample_inputs/`
   - Verify `gloc_inp.dat` is present

4. **Visualization not displaying**:
   - Clear browser cache
   - Try a different browser
   - Check console for JavaScript errors

## Performance Tips

- For faster loading, disable unused visualizations
- Run batch analysis during off-peak hours
- Use Chrome or Firefox for best performance
- Close other browser tabs to free memory

## Future Enhancements

See `FUTURE_IMPLEMENTATIONS.md` for planned features including:
- Machine learning predictions
- Real-time sensor integration
- VR/AR visualization
- Mobile companion app
- Medical record integration

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## License

[Specify your license here]

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Contact the development team

## Acknowledgments

- CGEM model developers
- Aerospace medicine research community
- Open source visualization libraries

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Status**: Active Development