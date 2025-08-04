# Save analysis results to JSON for further use
results_summary = {
    'subject_parameters': {
        'height_cm': standard_male.height_cm,
        'weight_kg': standard_male.weight_kg,
        'baseline_bp': f"{standard_male.systolic_bp_start}/{standard_male.diastolic_bp_start}",
        'g_tolerance_multiplier': standard_male.g_tolerance_multiplier
    },
    'maneuver_statistics': maneuver_stats,
    'physiological_analyses': {
        name: {
            'risk_level': analysis['overall_risk'],
            'max_gz': analysis['max_gz'],
            'min_gz': analysis['min_gz'],
            'min_brain_pressure_mmhg': analysis['min_brain_pressure_mmhg'],
            'risk_factors': analysis['risk_factors']
        }
        for name, analysis in physiological_analyses.items()
    },
    'analysis_timestamp': pd.Timestamp.now().isoformat()
}

# Save to JSON file
with open('aerobatic_simulation_results.json', 'w') as f:
    json.dump(results_summary, f, indent=2, default=str)

print("💾 Analysis results saved to 'aerobatic_simulation_results.json'")
print("🎯 Simulation complete! All maneuvers analyzed with physiological assessment.")
print(f"📊 Total maneuvers analyzed: {len(all_profiles)}")
print(f"🧠 Standard fit male subject parameters applied throughout analysis")
print("\n✅ Jupyter notebook simulation completed successfully!")## Summary and Conclusions

This simulation has analyzed several aerobatic maneuvers and their physiological impacts on a standard fit male subject. The analysis includes:

### Key Findings:

1. **G-Force Profiles**: Each maneuver has distinct G-force characteristics
   - **Hammerhead**: Moderate positive and negative G-forces with dynamic transitions
   - **Outside 360°**: Sustained negative G-forces challenging to pilot physiology  
   - **Horizontal Rolling 360°**: Gentle maneuver maintaining near 1G throughout
   - **Vertical Figure-8**: Complex profile with both positive and negative G exposures

2. **Physiological Considerations**:
   - Blood pressure changes due to hydrostatic effects of G-forces
   - Consciousness risk assessment based on cerebral blood flow
   - G-force exposure time analysis for safety evaluation

3. **Risk Assessment**:
   - Maneuvers are classified as LOW, MODERATE, or HIGH risk
   - Factors include peak G-forces, exposure duration, and blood pressure effects
   - Standard fit male subject parameters used for baseline analysis

### Applications:
- **Pilot Training**: Understanding physiological demands of different maneuvers
- **Aircraft Design**: G-force envelope requirements for aerobatic aircraft
- **Medical Research**: Baseline data for G-tolerance studies
- **Safety Analysis**: Risk assessment for aerobatic flight operations

### Future Enhancements:
- Integration with full CGEM (Combined G-Effects Model) simulation
- Analysis of G-suit and other protective equipment effects
- Comparison across different pilot demographics
- Real-time physiological monitoring integration# Perform physiological analysis for all maneuvers
print("🏥 Conducting Physiological Risk Assessment...")
print("="*60)

physiological_analyses = {}
for name, samples in all_profiles.items():
    analysis = analyze_g_tolerance(name, samples, standard_male)
    physiological_analyses[name] = analysis
    
    print(f"\n🩺 {name.replace('_', ' ').title()}:")
    print(f"   G-Force Range: {analysis['min_gz']:.1f}G to {analysis['max_gz']:.1f}G")
    print(f"   Min Brain Pressure: {analysis['min_brain_pressure_mmhg']:.0f} mmHg")
    print(f"   Max Pressure Drop: {analysis['max_pressure_drop_mmhg']:.0f} mmHg")
    print(f"   High G Exposure (>4G): {analysis['high_g_exposure_s']:.1f}s")
    print(f"   Negative G Exposure (<-1.5G): {analysis['negative_g_exposure_s']:.1f}s")
    print(f"   Overall Risk Level: {analysis['overall_risk']}")
    
    if analysis['risk_factors']:
        print(f"   ⚠️  Risk Factors:")
        for factor in analysis['risk_factors']:
            print(f"      • {factor}")

# Create risk summary table
print(f"\n📊 RISK SUMMARY TABLE")
print("="*60)
print(f"{'Maneuver':<25} {'Risk Level':<12} {'Max +G':<8} {'Max -G':<8} {'Min BP':<8}")
print("-" * 60)
for name, analysis in physiological_analyses.items():
    maneuver_name = name.replace('_', ' ').title()[:24]
    print(f"{maneuver_name:<25} {analysis['overall_risk']:<12} {analysis['max_gz']:>6.1f}G {analysis['min_gz']:>6.1f}G {analysis['min_brain_pressure_mmhg']:>6.0f}")

print(f"\n💡 Key Findings:")
print(f"   • Standard fit male subject (179cm, 75kg) with normal G-tolerance")
print(f"   • Blood pressure baseline: {standard_male.systolic_bp_start}/{standard_male.diastolic_bp_start} mmHg")
print(f"   • Critical brain pressure threshold: ~60 mmHg systolic")
print(f"   • Analysis includes hydrostatic pressure effects of G-forces")# Physiological response modeling functions
def estimate_blood_pressure_response(gz_profile: np.ndarray, subject: PhysiologicalParams) -> Dict:
    """
    Estimate blood pressure response based on G-force profile
    Simplified model based on hydrostatic pressure changes
    """
    # Hydrostatic pressure change due to G-force (approximate)
    # ΔP ≈ ρ * g * h * (Gz - 1) where h is effective height (heart to brain ~30cm)
    height_heart_to_brain = 0.30  # meters
    blood_density = 1060  # kg/m³
    g = 9.81  # m/s²
    
    pressure_changes = []
    consciousness_risk = []
    
    for gz in gz_profile:
        # Calculate hydrostatic pressure change in mmHg
        delta_p_pa = blood_density * g * height_heart_to_brain * (gz - 1.0)
        delta_p_mmhg = delta_p_pa * 0.00750062  # Pa to mmHg conversion
        
        # Estimate effective blood pressure at brain level
        effective_systolic = subject.systolic_bp_start - delta_p_mmhg
        effective_diastolic = subject.diastolic_bp_start - delta_p_mmhg
        
        pressure_changes.append({
            'gz': gz,
            'delta_p_mmhg': delta_p_mmhg,
            'brain_systolic': max(0, effective_systolic),
            'brain_diastolic': max(0, effective_diastolic)
        })
        
        # Assess consciousness risk (simplified)
        if effective_systolic < 60:  # Critical hypotension
            risk = "HIGH"
        elif effective_systolic < 80:  # Moderate hypotension
            risk = "MODERATE"
        elif gz > 5.0:  # High positive G
            risk = "MODERATE"
        elif gz < -2.0:  # High negative G
            risk = "MODERATE"
        else:
            risk = "LOW"
        
        consciousness_risk.append(risk)
    
    return {
        'pressure_changes': pressure_changes,
        'consciousness_risk': consciousness_risk,
        'max_pressure_drop': max([p['delta_p_mmhg'] for p in pressure_changes], default=0),
        'min_brain_pressure': min([p['brain_systolic'] for p in pressure_changes], default=subject.systolic_bp_start)
    }

def analyze_g_tolerance(maneuver_name: str, samples: List[Sample], subject: PhysiologicalParams) -> Dict:
    """
    Comprehensive G-tolerance analysis for a maneuver
    """
    time_array, gz_array = process_maneuver_profile(samples)
    bp_response = estimate_blood_pressure_response(gz_array, subject)
    
    # G-force exposure analysis
    high_g_threshold = 4.0
    extreme_g_threshold = 6.0
    negative_g_threshold = -1.5
    
    high_g_exposure = np.sum(gz_array > high_g_threshold) * (time_array[1] - time_array[0]) if len(time_array) > 1 else 0
    extreme_g_exposure = np.sum(gz_array > extreme_g_threshold) * (time_array[1] - time_array[0]) if len(time_array) > 1 else 0
    negative_g_exposure = np.sum(gz_array < negative_g_threshold) * (time_array[1] - time_array[0]) if len(time_array) > 1 else 0
    
    # Risk assessment
    risk_factors = []
    if bp_response['min_brain_pressure'] < 60:
        risk_factors.append("Critical cerebral hypotension risk")
    if extreme_g_exposure > 2.0:
        risk_factors.append("Extended extreme G-force exposure")
    if negative_g_exposure > 3.0:
        risk_factors.append("Extended negative G-force exposure")
    if max(gz_array) > 7.0:
        risk_factors.append("G-force exceeds typical human tolerance")
    
    overall_risk = "HIGH" if len(risk_factors) > 2 else "MODERATE" if len(risk_factors) > 0 else "LOW"
    
    return {
        'maneuver': maneuver_name,
        'max_gz': max(gz_array),
        'min_gz': min(gz_array),
        'high_g_exposure_s': high_g_exposure,
        'extreme_g_exposure_s': extreme_g_exposure,
        'negative_g_exposure_s': negative_g_exposure,
        'min_brain_pressure_mmhg': bp_response['min_brain_pressure'],
        'max_pressure_drop_mmhg': bp_response['max_pressure_drop'],
        'risk_factors': risk_factors,
        'overall_risk': overall_risk,
        'blood_pressure_response': bp_response
    }

print("🧠 Physiological analysis functions defined")## Physiological Response Analysis

Let's analyze the physiological implications of these G-force profiles for our standard fit male subject.# Compare four key maneuvers
selected_maneuvers = ['hammerhead', 'outside_360', 'horizontal_rolling_360', 'outside_inside_vert8']
comparison_fig = plot_maneuver_comparison(all_profiles, standard_male, selected_maneuvers)
plt.show()

print("📊 Comparative Analysis Summary:")
print("="*50)
for name in selected_maneuvers:
    stats = maneuver_stats[name]
    print(f"\n{name.replace('_', ' ').title()}:")
    print(f"   Duration: {stats['total_duration_s']:.1f}s")
    print(f"   G-Range: {stats['max_positive_g']:.1f}G to {stats['max_negative_g']:.1f}G")
    print(f"   High-G Time: {stats['high_positive_g_time_s']:.1f}s")
    print(f"   Negative-G Time: {stats['negative_g_time_s']:.1f}s")## Maneuver Comparison Analysis

Now let's compare multiple maneuvers side by side to understand their relative physiological demands.# Plot Horizontal Rolling 360°
print("🎯 Simulating Horizontal Rolling 360°...")
horizontal_roll_fig = plot_single_maneuver('horizontal_rolling_360', all_profiles['horizontal_rolling_360'], standard_male)
plt.show()

horizontal_stats = maneuver_stats['horizontal_rolling_360']
print(f"\n🔍 Horizontal Rolling 360° Analysis:")
print(f"   A 360° aileron roll while maintaining level flight - relatively gentle on G-forces.")
print(f"   Peak positive G-force: {horizontal_stats['max_positive_g']:.1f}G")
print(f"   Peak negative G-force: {horizontal_stats['max_negative_g']:.1f}G")
print(f"   This maneuver shows how skilled aerobatic pilots can maintain near 1G throughout complex maneuvers.")# Plot Outside 360° Loop
print("🎯 Simulating Outside 360° Loop...")
outside360_fig = plot_single_maneuver('outside_360', all_profiles['outside_360'], standard_male)
plt.show()

outside360_stats = maneuver_stats['outside_360']
print(f"\n🔍 Outside 360° Loop Analysis:")
print(f"   This maneuver involves a complete outside loop with sustained negative G-forces.")
print(f"   Peak positive G-force: {outside360_stats['max_positive_g']:.1f}G")
print(f"   Peak negative G-force: {outside360_stats['max_negative_g']:.1f}G")
print(f"   ⚠️  Negative G exposure is particularly challenging for pilot physiology!")
if outside360_stats['negative_g_time_s'] > 0:
    print(f"   ⚠️  Negative G exposure (<-1G): {outside360_stats['negative_g_time_s']:.1f} seconds")# Plot Hammerhead maneuver
print("🎯 Simulating Hammerhead Maneuver...")
hammerhead_fig = plot_single_maneuver('hammerhead', all_profiles['hammerhead'], standard_male)
plt.show()

# Display detailed analysis
hammerhead_stats = maneuver_stats['hammerhead']
print(f"\n🔍 Hammerhead Analysis:")
print(f"   This is a classic aerobatic maneuver involving a vertical climb to zero airspeed,")
print(f"   followed by a 180° yaw turn and vertical descent.")
print(f"   Peak positive G-force: {hammerhead_stats['max_positive_g']:.1f}G")
print(f"   Peak negative G-force: {hammerhead_stats['max_negative_g']:.1f}G")
if hammerhead_stats['high_positive_g_time_s'] > 0:
    print(f"   ⚠️  High G exposure (>3G): {hammerhead_stats['high_positive_g_time_s']:.1f} seconds")
if hammerhead_stats['negative_g_time_s'] > 0:
    print(f"   ⚠️  Negative G exposure (<-1G): {hammerhead_stats['negative_g_time_s']:.1f} seconds")## Individual Maneuver Simulations

Let's analyze each aerobatic maneuver individually, showing the G-force profile and its physiological implications for our standard fit male subject.# Plotting functions for G-force analysis
def plot_single_maneuver(name: str, samples: List[Sample], subject: PhysiologicalParams, 
                        figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot G-force vs time for a single maneuver with physiological context
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1])
    
    # Process the maneuver data
    time_array, gz_array = process_maneuver_profile(samples)
    stats = calculate_maneuver_stats(samples)
    
    # Main G-force plot
    ax1.plot(time_array, gz_array, linewidth=2.5, color='darkblue', label='Gz Profile')
    ax1.fill_between(time_array, gz_array, alpha=0.3, color='lightblue')
    
    # Add physiological reference lines
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3, label='1G (Level Flight)')
    ax1.axhline(y=3.0, color='orange', linestyle='--', alpha=0.7, label='3G (Moderate Stress)')
    ax1.axhline(y=5.0, color='red', linestyle='--', alpha=0.7, label='5G (High Stress)')
    ax1.axhline(y=-1.0, color='purple', linestyle='--', alpha=0.7, label='-1G (Negative G)')
    ax1.axhline(y=-3.0, color='darkred', linestyle='--', alpha=0.7, label='-3G (High -G Stress)')
    
    # Highlight critical G-force regions
    ax1.fill_between(time_array, 3.0, np.maximum(gz_array, 3.0), 
                    where=(gz_array > 3.0), alpha=0.2, color='orange', label='High +G Zone')
    ax1.fill_between(time_array, -1.0, np.minimum(gz_array, -1.0), 
                    where=(gz_array < -1.0), alpha=0.2, color='purple', label='Negative G Zone')
    
    ax1.set_xlabel('Time (seconds)', fontsize=12)
    ax1.set_ylabel('G-Force (Gz)', fontsize=12)
    ax1.set_title(f'{name.replace("_", " ").title()}\n{PROFILES[name][1]}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Statistics subplot
    ax2.axis('off')
    stats_text = f"""
    Maneuver Statistics (Standard Fit Male - {subject.height_cm}cm, {subject.weight_kg}kg):
    • Total Duration: {stats['total_duration_s']:.1f} seconds
    • Maximum +G: {stats['max_positive_g']:.1f}G
    • Maximum -G: {stats['max_negative_g']:.1f}G
    • Time above 3G: {stats['high_positive_g_time_s']:.1f}s
    • Time below -1G: {stats['negative_g_time_s']:.1f}s
    • G-Force Range: {stats['g_range']:.1f}G
    • Average G-Force: {stats['avg_g']:.1f}G
    """
    ax2.text(0.02, 0.95, stats_text, transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def plot_maneuver_comparison(profiles: Dict[str, List[Sample]], subject: PhysiologicalParams,
                           selected_maneuvers: List[str] = None) -> plt.Figure:
    """
    Plot multiple maneuvers for comparison
    """
    if selected_maneuvers is None:
        selected_maneuvers = list(profiles.keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(selected_maneuvers)))
    
    # Plot individual maneuvers
    for i, (name, color) in enumerate(zip(selected_maneuvers[:4], colors)):
        if i >= 4:
            break
            
        ax = axes[i]
        samples = profiles[name]
        time_array, gz_array = process_maneuver_profile(samples)
        
        ax.plot(time_array, gz_array, linewidth=2, color=color, label=name.replace('_', ' ').title())
        ax.fill_between(time_array, gz_array, alpha=0.3, color=color)
        
        # Add reference lines
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.axhline(y=3.0, color='orange', linestyle='--', alpha=0.5)
        ax.axhline(y=-1.0, color='purple', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('G-Force (Gz)')
        ax.set_title(name.replace('_', ' ').title())
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add stats
        stats = calculate_maneuver_stats(samples)
        stats_text = f"Max: {stats['max_positive_g']:.1f}G / {stats['max_negative_g']:.1f}G\nDuration: {stats['total_duration_s']:.1f}s"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Hide unused subplots
    for i in range(len(selected_maneuvers), 4):
        axes[i].set_visible(False)
    
    plt.suptitle(f'Aerobatic Maneuvers Comparison - Standard Fit Male Subject', fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig

print("📈 Plotting functions defined successfully")# Load and process aerobatic maneuver profiles
def process_maneuver_profile(samples: List[Sample]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert maneuver samples to time series arrays for plotting
    
    Args:
        samples: List of Sample objects with nz and duration_ms
        
    Returns:
        Tuple of (time_array, gz_array) in seconds and G-forces
    """
    if not samples:
        return np.array([]), np.array([])
    
    # Convert to time series
    time_points = []
    gz_values = []
    
    current_time = 0.0
    for sample in samples:
        # Add start point
        time_points.append(current_time)
        gz_values.append(sample.nz)
        
        # Add end point (duration in milliseconds -> seconds)
        current_time += sample.duration_ms / 1000.0
        time_points.append(current_time)
        gz_values.append(sample.nz)
    
    return np.array(time_points), np.array(gz_values)

def calculate_maneuver_stats(samples: List[Sample]) -> Dict:
    """Calculate statistics for a maneuver profile"""
    if not samples:
        return {}
    
    gz_values = [sample.nz for sample in samples]
    durations = [sample.duration_ms for sample in samples]
    
    total_duration = sum(durations) / 1000.0  # Convert to seconds
    max_positive_g = max([g for g in gz_values if g > 0], default=0)
    max_negative_g = min([g for g in gz_values if g < 0], default=0)
    
    # Calculate G-force exposure metrics
    positive_g_time = sum(d for g, d in zip(gz_values, durations) if g > 3.0) / 1000.0
    negative_g_time = sum(d for g, d in zip(gz_values, durations) if g < -1.0) / 1000.0
    
    return {
        'total_duration_s': total_duration,
        'max_positive_g': max_positive_g,
        'max_negative_g': max_negative_g,
        'high_positive_g_time_s': positive_g_time,  # Time above 3G
        'negative_g_time_s': negative_g_time,       # Time below -1G
        'avg_g': np.mean(gz_values),
        'g_range': max_positive_g - max_negative_g
    }

# Load all available maneuver profiles
print("🛩️ Loading aerobatic maneuver profiles...")
all_profiles = load_all_profiles()

# Process and display basic info about each maneuver
maneuver_stats = {}
for name, samples in all_profiles.items():
    stats = calculate_maneuver_stats(samples)
    maneuver_stats[name] = stats
    description = PROFILES[name][1]  # Get description from PROFILES mapping
    
    print(f"\n📊 {name.replace('_', ' ').title()}:")
    print(f"   Description: {description}")
    print(f"   Duration: {stats['total_duration_s']:.1f}s")
    print(f"   Max +G: {stats['max_positive_g']:.1f}G")
    print(f"   Max -G: {stats['max_negative_g']:.1f}G")
    print(f"   Time >3G: {stats['high_positive_g_time_s']:.1f}s")
    print(f"   Time <-1G: {stats['negative_g_time_s']:.1f}s")

print(f"\n✅ Loaded {len(all_profiles)} maneuver profiles successfully")# Define physiological parameters for standard fit male subject
@dataclass
class PhysiologicalParams:
    """Physiological parameters for G-force tolerance modeling"""
    height_cm: float = 179.0  # Height in cm (from gloc_inp.dat)
    weight_kg: float = 75.0   # Typical weight for fit male
    sex: int = 1              # 1 = male, 0 = female
    
    # Blood flow parameters (dl/min)
    normal_brain_flow: float = 49.5    # Normal flow rate through brain
    max_brain_flow: float = 110.0      # Maximum flow rate
    consciousness_flow: float = 19.0   # Flow needed for consciousness
    life_flow: float = 9.0             # Flow needed for life
    
    # G-tolerance parameters
    g_tolerance_multiplier: float = 1.0  # Relative to normal
    heart_ramp_time: float = 2.5         # Heart response time constant
    
    # Blood pressure parameters (mmHg)
    systolic_bp_start: float = 120.0
    diastolic_bp_start: float = 80.0
    systolic_bp_max: float = 177.0
    diastolic_bp_max: float = 80.0
    
    # Consciousness parameters
    consciousness_time: float = 7.1    # Seconds after flow stops
    cell_life_time: float = 180.0      # Seconds of cell life after flow stops
    
    # Equipment parameters (none for baseline)
    anti_g_suit_pressure: float = 0.0
    anti_g_suit_coverage: float = 0.0
    strain_effectiveness: float = 0.0
    pressure_breathing: float = 0.0
    seat_tilt_degrees: float = 10.0

# Create standard fit male subject
standard_male = PhysiologicalParams()

print("👨 Standard Fit Male Subject Parameters:")
print(f"   Height: {standard_male.height_cm} cm")
print(f"   Weight: {standard_male.weight_kg} kg")
print(f"   Normal brain flow: {standard_male.normal_brain_flow} dl/min")
print(f"   G-tolerance multiplier: {standard_male.g_tolerance_multiplier}")
print(f"   Starting BP: {standard_male.systolic_bp_start}/{standard_male.diastolic_bp_start} mmHg")
print(f"   Consciousness threshold: {standard_male.consciousness_time}s after flow loss")# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
import seaborn as sns

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Import the aerobatic profiles module
from aerobatic_profiles import load_profile, load_all_profiles, Sample, PROFILES

print("✅ Libraries imported successfully")
print(f"📁 Available maneuvers: {list(PROFILES.keys())}")# Aerobatic Maneuvers G-Force Simulation

This notebook simulates several aerobatic maneuvers and analyzes the G-force profiles and their physiological effects on a standard fit male subject.

## Overview

- **Objective**: Simulate various aerobatic maneuvers and plot Gz vs time curves
- **Subject**: Standard fit male (179cm height, normal G-tolerance)
- **Maneuvers**: Hammerhead, Outside 360°, Horizontal Rolling 360°, and more
- **Analysis**: G-force profiles, physiological parameters, and safety considerations

## Data Sources

The maneuver data comes from real in-flight measurements that have been discretized for simulation purposes. Each maneuver is represented as a time series of (Nz, duration_ms) pairs where:
- **Nz**: Instantaneous normal acceleration (+Gz for positive, -Gz for negative)
- **duration_ms**: Duration that acceleration is maintained in milliseconds