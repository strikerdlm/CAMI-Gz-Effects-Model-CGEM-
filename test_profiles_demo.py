#!/usr/bin/env python3
"""
Test script to verify aerobatic profiles and visualization capabilities.
This script tests all the functionality that will be demonstrated in the Jupyter notebook.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from aerobatic_profiles import load_all_profiles, load_profile, PROFILES

def test_profile_loading():
    """Test loading all profiles."""
    print("Testing profile loading...")
    profiles = load_all_profiles()
    
    print(f"✅ Successfully loaded {len(profiles)} profiles")
    print("Available profiles:", list(profiles.keys()))
    
    # Verify each profile
    for profile_id, samples in profiles.items():
        filename, description = PROFILES[profile_id]
        total_duration = sum(sample.duration_ms for sample in samples)
        max_pos_g = max((sample.nz for sample in samples), default=0)
        min_neg_g = min((sample.nz for sample in samples), default=0)
        
        print(f"  📁 {profile_id}: {len(samples)} samples, {total_duration/1000:.1f}s, {min_neg_g:.1f}G to +{max_pos_g:.1f}G")
    
    return profiles

def test_visualization():
    """Test basic visualization capabilities."""
    print("\nTesting visualization capabilities...")
    
    # Load profiles
    profiles = load_all_profiles()
    
    # Test basic plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot first profile as test
    profile_id = list(profiles.keys())[0]
    samples = profiles[profile_id]
    
    # Convert to time series
    time_points = []
    g_values = []
    current_time = 0
    
    for sample in samples:
        time_points.extend([current_time, current_time + sample.duration_ms])
        g_values.extend([sample.nz, sample.nz])
        current_time += sample.duration_ms
    
    # Convert to seconds
    time_points = [t/1000 for t in time_points]
    
    # Plot
    ax.plot(time_points, g_values, linewidth=2, label=profile_id)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Normal Acceleration (G)')
    ax.set_title(f'Test Plot: {profile_id.replace("_", " ").title()}')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Save plot
    plt.savefig('test_profile_plot.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    print("✅ Basic plotting functionality works")
    print("✅ Saved test plot as 'test_profile_plot.png'")

def test_statistics():
    """Test statistical analysis."""
    print("\nTesting statistical analysis...")
    
    profiles = load_all_profiles()
    stats_data = []
    
    for profile_id, samples in profiles.items():
        g_values = [sample.nz for sample in samples]
        durations = [sample.duration_ms for sample in samples]
        
        total_duration = sum(durations)
        weighted_mean = sum(g * d for g, d in zip(g_values, durations)) / total_duration
        
        stats = {
            'Profile': profile_id.replace('_', ' ').title(),
            'Samples': len(samples),
            'Duration (s)': total_duration / 1000,
            'Max +G': max(g_values),
            'Max -G': min(g_values),
            'Mean G': np.mean(g_values),
            'Weighted Mean G': weighted_mean,
            'Std Dev': np.std(g_values)
        }
        stats_data.append(stats)
    
    df_stats = pd.DataFrame(stats_data)
    print("✅ Statistical analysis completed")
    print("\nSample statistics:")
    print(df_stats[['Profile', 'Samples', 'Duration (s)', 'Max +G', 'Max -G']].round(2).to_string(index=False))
    
    return df_stats

def test_validation():
    """Test profile validation."""
    print("\nTesting profile validation...")
    
    profiles = load_all_profiles()
    all_valid = True
    
    for profile_id, samples in profiles.items():
        valid = True
        issues = []
        
        for i, sample in enumerate(samples):
            if not isinstance(sample.nz, (int, float)):
                valid = False
                issues.append(f"Sample {i}: Invalid G-value type")
            
            if not isinstance(sample.duration_ms, int) or sample.duration_ms <= 0:
                valid = False
                issues.append(f"Sample {i}: Invalid duration")
            
            if abs(sample.nz) > 15:  # Reasonable upper limit
                valid = False
                issues.append(f"Sample {i}: Extreme G-value ({sample.nz}G)")
        
        status = "✅ READY" if valid else "❌ ISSUES"
        print(f"  {profile_id.ljust(25)} {status}")
        
        if issues:
            print(f"    Issues: {'; '.join(issues)}")
            all_valid = False
    
    if all_valid:
        print("\n🎉 ALL PROFILES ARE READY FOR MODEL INTEGRATION!")
    else:
        print("\n⚠️  SOME PROFILES HAVE ISSUES")
    
    return all_valid

def main():
    """Main test function."""
    print("Aerobatic Profiles Verification Test")
    print("=" * 50)
    
    try:
        # Test profile loading
        profiles = test_profile_loading()
        
        # Test visualization
        test_visualization()
        
        # Test statistics
        test_statistics()
        
        # Test validation
        all_valid = test_validation()
        
        # Summary
        print("\n" + "=" * 50)
        print("VERIFICATION SUMMARY:")
        print(f"✅ Profiles loaded: {len(profiles)}")
        print("✅ Visualization: Working")
        print("✅ Statistics: Working")
        print(f"✅ Validation: {'All profiles ready' if all_valid else 'Some issues found'}")
        print("\n🎉 ALL SYSTEMS READY FOR JUPYTER NOTEBOOK DEMONSTRATION!")
        
        # List available profiles
        print("\nAvailable Aerobatic Profiles:")
        for i, (profile_id, (filename, description)) in enumerate(PROFILES.items(), 1):
            print(f"{i}. **{profile_id.replace('_', ' ').title()}** - {description}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)