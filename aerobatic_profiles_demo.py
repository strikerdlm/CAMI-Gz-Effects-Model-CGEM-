## Conclusion

This notebook has successfully demonstrated:

1. **Profile Verification**: All 7 aerobatic maneuver profiles are loaded and verified
2. **Data Integrity**: Each profile contains valid G-force and duration data
3. **Comprehensive Visualizations**: 
   - Individual profile plots with statistics
   - Comparative analysis across all maneuvers
   - G-force distribution analysis
4. **Statistical Analysis**: Detailed statistics for each maneuver
5. **Model Readiness**: All profiles are validated and ready for use

### Available Aerobatic Profiles:

1. **Hammerhead** - Vertical climb, stall-turn, vertical descent
2. **Horizontal Rolling 360** - Level flight aileron roll
3. **Outside 360** - Sustained negative-G loop
4. **Outside Inside Vertical 8** - Complex figure-eight maneuver
5. **Quarter Down Roll** - Outside loop with snap roll
6. **Snap 45° Down Roll** - Downline with snap roll
7. **Half Vertical Roll with Negative Pull** - Complex recovery maneuver

All profiles are now ready for integration with physiological models like CGEM or other research applications!def validate_profile_integrity():
    """Comprehensive validation of all profiles for model readiness."""
    validation_results = []
    
    for profile_id, samples in profiles.items():
        result = {
            'profile': profile_id,
            'samples_count': len(samples),
            'data_integrity': True,
            'duration_consistency': True,
            'g_range_valid': True,
            'file_accessible': True,
            'issues': []
        }
        
        # Check data integrity
        for i, sample in enumerate(samples):
            if not isinstance(sample.nz, (int, float)):
                result['data_integrity'] = False
                result['issues'].append(f"Sample {i}: Invalid G-value type")
            
            if not isinstance(sample.duration_ms, int) or sample.duration_ms <= 0:
                result['duration_consistency'] = False
                result['issues'].append(f"Sample {i}: Invalid duration")
            
            if abs(sample.nz) > 15:  # Reasonable upper limit for aerobatic maneuvers
                result['g_range_valid'] = False
                result['issues'].append(f"Sample {i}: Extreme G-value ({sample.nz}G)")
        
        # Check if original file is accessible
        try:
            load_profile(profile_id)
        except Exception as e:
            result['file_accessible'] = False
            result['issues'].append(f"File access error: {str(e)}")
        
        validation_results.append(result)
    
    return validation_results

# Run validation
validation_results = validate_profile_integrity()

print("Model Integration Readiness Report")
print("=" * 50)

all_valid = True
for result in validation_results:
    status = "✅ READY" if all([
        result['data_integrity'],
        result['duration_consistency'],
        result['g_range_valid'],
        result['file_accessible']
    ]) else "❌ ISSUES"
    
    if status == "❌ ISSUES":
        all_valid = False
    
    print(f"\n{result['profile'].ljust(25)} {status}")
    print(f"  Samples: {result['samples_count']}")
    
    if result['issues']:
        print(f"  Issues: {'; '.join(result['issues'])}")

print("\n" + "=" * 50)
if all_valid:
    print("🎉 ALL PROFILES ARE READY FOR MODEL INTEGRATION!")
    print("\nAvailable integration formats:")
    print("- Python objects (aerobatic_profiles.py)")
    print("- CSV export (for data analysis)")
    print("- JSON export (for web applications)")
    print("- CGEM input format (for physiological modeling)")
    
    print("\nQuick integration example:")
    print("```python")
    print("from aerobatic_profiles import load_profile")
    print("hammerhead_data = load_profile('hammerhead')")
    print("for sample in hammerhead_data:")
    print("    print(f'G: {sample.nz}, Duration: {sample.duration_ms}ms')")
    print("```")
else:
    print("⚠️  SOME PROFILES HAVE ISSUES - CHECK ABOVE FOR DETAILS")

# Summary statistics
total_profiles = len(profiles)
total_samples = sum(len(samples) for samples in profiles.values())
total_duration = sum(sum(sample.duration_ms for sample in samples) for samples in profiles.values())

print(f"\nSummary Statistics:")
print(f"- Total Profiles: {total_profiles}")
print(f"- Total Samples: {total_samples}")
print(f"- Total Duration: {total_duration/1000:.1f} seconds ({total_duration/60000:.1f} minutes)")
print(f"- Average Profile Duration: {(total_duration/1000)/total_profiles:.1f} seconds")
print(f"- Average Samples per Profile: {total_samples/total_profiles:.1f}")## 5. Model Integration Ready Check

Final verification that all profiles are ready for model integration.# Create comprehensive statistics table
stats_data = []

for profile_id, samples in profiles.items():
    g_values = [sample.nz for sample in samples]
    durations = [sample.duration_ms for sample in samples]
    
    # Calculate weighted statistics (accounting for duration)
    total_duration = sum(durations)
    weighted_mean = sum(g * d for g, d in zip(g_values, durations)) / total_duration
    
    stats = {
        'Profile': profile_id.replace('_', ' ').title(),
        'Samples': len(samples),
        'Duration (s)': total_duration / 1000,
        'Max +G': max(g_values),
        'Max -G': min(g_values),
        'G Range': max(g_values) - min(g_values),
        'Mean G': np.mean(g_values),
        'Weighted Mean G': weighted_mean,
        'Std Dev': np.std(g_values),
        'Positive G Time (%)': sum(d for g, d in zip(g_values, durations) if g > 0) / total_duration * 100,
        'Negative G Time (%)': sum(d for g, d in zip(g_values, durations) if g < 0) / total_duration * 100,
        'Zero G Time (%)': sum(d for g, d in zip(g_values, durations) if g == 0) / total_duration * 100
    }
    stats_data.append(stats)

# Create DataFrame and display
df_stats = pd.DataFrame(stats_data)
print("Comprehensive Statistical Analysis of Aerobatic Profiles")
print("=" * 80)
print(df_stats.round(2).to_string(index=False))## 4. Statistical Analysis

Let's perform detailed statistical analysis of each maneuver.# Create a comparison plot with all profiles
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

# Top plot: All profiles overlaid
colors = plt.cm.tab10(np.linspace(0, 1, len(profiles)))

for i, (profile_id, samples) in enumerate(profiles.items()):
    # Convert to time series
    time_points = []
    g_values = []
    current_time = 0
    
    for sample in samples:
        time_points.extend([current_time, current_time + sample.duration_ms])
        g_values.extend([sample.nz, sample.nz])
        current_time += sample.duration_ms
    
    time_points = [t/1000 for t in time_points]  # Convert to seconds
    
    ax1.plot(time_points, g_values, linewidth=2, alpha=0.8, 
            color=colors[i], label=profile_id.replace('_', ' ').title())

ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('Normal Acceleration (G)')
ax1.set_title('All Aerobatic Profiles Comparison', fontsize=16, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

# Bottom plot: G-force distribution histogram
all_g_values = []
profile_labels = []

for profile_id, samples in profiles.items():
    g_vals = [sample.nz for sample in samples]
    all_g_values.extend(g_vals)
    profile_labels.extend([profile_id.replace('_', ' ').title()] * len(g_vals))

# Create histogram
ax2.hist(all_g_values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
ax2.axvline(x=0, color='red', linestyle='--', alpha=0.8, linewidth=2, label='Zero G')
ax2.set_xlabel('Normal Acceleration (G)')
ax2.set_ylabel('Frequency')
ax2.set_title('G-Force Distribution Across All Maneuvers', fontsize=16, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.show()## 3. Comparative Analysis

Let's compare all profiles side by side and analyze their characteristics.def plot_profile(profile_id, samples, ax=None):
    """Plot a single aerobatic profile with enhanced visualization."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    # Convert to time series
    time_points = []
    g_values = []
    current_time = 0
    
    for sample in samples:
        time_points.extend([current_time, current_time + sample.duration_ms])
        g_values.extend([sample.nz, sample.nz])
        current_time += sample.duration_ms
    
    # Convert to seconds for better readability
    time_points = [t/1000 for t in time_points]
    
    # Plot the profile
    ax.plot(time_points, g_values, linewidth=2.5, alpha=0.8)
    ax.fill_between(time_points, g_values, alpha=0.3)
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    
    # Highlight positive and negative G regions
    ax.fill_between(time_points, g_values, 0, where=[g >= 0 for g in g_values], 
                   color='red', alpha=0.2, label='Positive G (+Gz)')
    ax.fill_between(time_points, g_values, 0, where=[g < 0 for g in g_values], 
                   color='blue', alpha=0.2, label='Negative G (-Gz)')
    
    # Formatting
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Normal Acceleration (G)', fontsize=12)
    ax.set_title(f'{profile_id.replace("_", " ").title()} Profile', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add statistics text box
    max_g = max(g_values)
    min_g = min(g_values)
    duration = max(time_points)
    stats_text = f'Max: +{max_g:.1f}G\\nMin: {min_g:.1f}G\\nDuration: {duration:.1f}s'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    return ax

# Create individual plots for each profile
fig, axes = plt.subplots(len(profiles), 1, figsize=(15, 4*len(profiles)))
if len(profiles) == 1:
    axes = [axes]

for i, (profile_id, samples) in enumerate(profiles.items()):
    plot_profile(profile_id, samples, axes[i])
    
    # Add description
    description = PROFILES[profile_id][1]
    axes[i].text(0.5, -0.15, description, transform=axes[i].transAxes, 
                ha='center', va='top', fontsize=10, style='italic')

plt.tight_layout()
plt.show()## 2. Individual Profile Visualizations

Let's create detailed visualizations for each aerobatic maneuver.# Load all profiles
profiles = load_all_profiles()

print("Profile Verification Summary:")
print("=" * 50)

for profile_id, samples in profiles.items():
    filename, description = PROFILES[profile_id]
    total_duration = sum(sample.duration_ms for sample in samples)
    max_pos_g = max((sample.nz for sample in samples), default=0)
    min_neg_g = min((sample.nz for sample in samples), default=0)
    
    print(f"\n📁 {profile_id}:")
    print(f"   File: {filename}")
    print(f"   Description: {description}")
    print(f"   Samples: {len(samples)}")
    print(f"   Duration: {total_duration/1000:.1f} seconds")
    print(f"   G-range: {min_neg_g:.1f}G to +{max_pos_g:.1f}G")

print(f"\n✅ Successfully verified {len(profiles)} aerobatic profiles!")## 1. Load and Verify All Profiles

Let's load all available aerobatic profiles and verify their integrity.# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import pandas as pd
from aerobatic_profiles import load_all_profiles, load_profile, PROFILES

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("Libraries imported successfully!")
print(f"Available profiles: {list(PROFILES.keys())}")# Aerobatic Profiles Demonstration

This notebook demonstrates all available aerobatic maneuver profiles and provides comprehensive visualizations for analysis.

## Overview

Aerobatic G-profiles represent the time-series of normal acceleration (Nz) values during aerobatic maneuvers. These profiles are essential for:
- Physiological modeling (e.g., CGEM - Combined G-Effects Model)
- Flight training analysis
- Medical research on G-force effects
- Aircraft performance evaluation

Each profile consists of:
- **Nz**: Normal acceleration in G-units (+Gz for positive, -Gz for negative)
- **Duration**: Time duration in milliseconds for each acceleration value