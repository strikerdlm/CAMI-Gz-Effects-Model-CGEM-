from __future__ import annotations

import math
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import seaborn as sns

from aerobatic_profiles import load_all_profiles, load_profile, PROFILES, Sample
from cgem_wrapper import run_cgem_for_profile, CGEMResult, PilotConfig

# Configure page
st.set_page_config(
    page_title="Advanced Aerobatic G-Profile Physiological Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1976d2;
    }
    h2 {
        color: #2e7d32;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #dc3545;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Physiological thresholds and constants
PHYSIOLOGICAL_THRESHOLDS = {
    "greyout_geff": 4.1,  # Typical G_eff threshold for greyout onset
    "blackout_geff": 5.0,  # Typical G_eff threshold for blackout onset
    "gloc_geff": 5.5,     # Typical G_eff threshold for G-LOC
    "redout_g": -2.0,     # Negative G threshold for redout
    "safe_g_range": (-1.0, 4.0),  # Safe G range for untrained individuals
    "trained_g_range": (-2.0, 9.0),  # Safe G range for trained pilots
}

# Color schemes for different physiological states
STATE_COLORS = {
    "normal": "#4CAF50",
    "caution": "#FFC107",
    "warning": "#FF9800",
    "danger": "#F44336",
    "critical": "#9C27B0",
    "greyout": "#757575",
    "blackout": "#212121",
    "gloc": "#000000",
    "redout": "#D32F2F"
}

# Maneuver-specific explanations
MANEUVER_EXPLANATIONS = {
    "hammerhead": {
        "description": "A hammerhead turn (also known as a stall turn) involves a vertical climb until airspeed approaches zero, followed by a 180° yaw rotation and vertical descent.",
        "physiological_effects": "Initial positive G during pull-up can cause blood pooling in lower extremities. The vertical climb reduces G-load to near zero, allowing blood redistribution. The descent phase may involve negative G, potentially causing redout.",
        "risk_factors": ["Rapid G onset during pull-up", "Potential disorientation during rotation", "Negative G during descent"],
        "mitigation": ["Anti-G straining maneuver (AGSM) during pull-up", "Gradual G onset when possible", "Proper head position during rotation"]
    },
    "horizontal_rolling_360": {
        "description": "A 360° aileron roll performed while maintaining level flight altitude.",
        "physiological_effects": "Alternating positive and negative G-forces as the aircraft rotates. Blood shifts between upper and lower body throughout the maneuver.",
        "risk_factors": ["Rapid G transitions", "Potential spatial disorientation", "Vestibular effects from rotation"],
        "mitigation": ["Maintain visual reference", "Controlled roll rate", "Prepare for G transitions"]
    },
    "outside_360": {
        "description": "A 360° outside loop where the pilot experiences sustained negative G throughout the maneuver.",
        "physiological_effects": "Sustained negative G causes blood to pool in the head, potentially leading to redout. Increased intracranial pressure can cause severe discomfort and vision impairment.",
        "risk_factors": ["Sustained negative G exposure", "Redout risk", "Severe discomfort", "Potential vessel rupture"],
        "mitigation": ["Limit duration of negative G", "Gradual entry and exit", "Proper restraint system"]
    },
    "outside_inside_vert8": {
        "description": "A vertical figure-eight combining an outside loop at the bottom with an inside loop at the top.",
        "physiological_effects": "Complex G-loading pattern alternating between positive and negative G. Rapid transitions challenge the cardiovascular system's ability to maintain cerebral perfusion.",
        "risk_factors": ["Rapid G transitions", "Combined positive/negative G effects", "Cumulative fatigue"],
        "mitigation": ["Proper conditioning", "AGSM during positive G phases", "Controlled transition rates"]
    },
    "quarter_down_roll": {
        "description": "A quarter outside loop followed by a 90° snap roll on the downline.",
        "physiological_effects": "Initial negative G during the outside portion, followed by rapid rotational forces during the snap roll. The downline may involve varying G-loads.",
        "risk_factors": ["Negative G exposure", "Rapid rotation effects", "Potential disorientation"],
        "mitigation": ["Prepare for negative G", "Maintain spatial awareness", "Control snap roll rate"]
    },
    "snap_45deg_down_roll": {
        "description": "A 45° downline with a snap roll, combining gravitational and rotational forces.",
        "physiological_effects": "Complex loading combining axial and radial G-forces. The angled descent adds gravitational component while the snap roll induces rapid rotation.",
        "risk_factors": ["Multi-axis G loading", "Vestibular stimulation", "Spatial disorientation"],
        "mitigation": ["Visual reference maintenance", "Controlled entry speed", "Proper body positioning"]
    },
    "half_vert_roll_neg_pull": {
        "description": "Half vertical roll ending with a negative G pull-out, transitioning from positive to negative G-loading.",
        "physiological_effects": "Transition from positive G during the vertical portion to negative G during pull-out challenges cardiovascular adaptation. Blood redistribution occurs rapidly.",
        "risk_factors": ["Rapid G reversal", "Cardiovascular stress", "Potential for G-LOC or redout"],
        "mitigation": ["Gradual transitions when possible", "Proper breathing technique", "Physical conditioning"]
    }
}

def get_physiological_state(g: float, geff: float) -> Tuple[str, str]:
    """Determine physiological state based on G and G_eff values."""
    if geff >= PHYSIOLOGICAL_THRESHOLDS["gloc_geff"]:
        return "critical", "G-LOC Risk"
    elif geff >= PHYSIOLOGICAL_THRESHOLDS["blackout_geff"]:
        return "danger", "Blackout Risk"
    elif geff >= PHYSIOLOGICAL_THRESHOLDS["greyout_geff"]:
        return "warning", "Greyout Risk"
    elif g < PHYSIOLOGICAL_THRESHOLDS["redout_g"]:
        return "danger", "Redout Risk"
    elif PHYSIOLOGICAL_THRESHOLDS["safe_g_range"][0] <= g <= PHYSIOLOGICAL_THRESHOLDS["safe_g_range"][1]:
        return "normal", "Normal"
    else:
        return "caution", "Caution"

def create_2d_physiological_plot(times: List[float], g_values: List[float], 
                                 geff_values: List[float], profile_name: str) -> go.Figure:
    """Create an interactive 2D plot with physiological thresholds and zones."""
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("G-Force Profile with Physiological Zones", 
                       "Effective G (G_eff) with Critical Thresholds"),
        shared_xaxes=True,
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5]
    )
    
    # Top plot: G-force with zones
    fig.add_trace(
        go.Scatter(x=times, y=g_values, name="G-Force",
                  line=dict(color='#1976d2', width=3),
                  hovertemplate="Time: %{x:.2f}s<br>G: %{y:.2f}<extra></extra>"),
        row=1, col=1
    )
    
    # Add physiological zones
    fig.add_hrect(y0=-10, y1=PHYSIOLOGICAL_THRESHOLDS["redout_g"], 
                 fillcolor="red", opacity=0.2, layer="below",
                 annotation_text="Redout Zone", row=1, col=1)
    fig.add_hrect(y0=PHYSIOLOGICAL_THRESHOLDS["safe_g_range"][0], 
                 y1=PHYSIOLOGICAL_THRESHOLDS["safe_g_range"][1],
                 fillcolor="green", opacity=0.2, layer="below",
                 annotation_text="Safe Zone", row=1, col=1)
    fig.add_hrect(y0=PHYSIOLOGICAL_THRESHOLDS["safe_g_range"][1], 
                 y1=PHYSIOLOGICAL_THRESHOLDS["trained_g_range"][1],
                 fillcolor="yellow", opacity=0.2, layer="below",
                 annotation_text="Trained Pilot Zone", row=1, col=1)
    fig.add_hrect(y0=PHYSIOLOGICAL_THRESHOLDS["trained_g_range"][1], y1=15,
                 fillcolor="red", opacity=0.2, layer="below",
                 annotation_text="Extreme Risk", row=1, col=1)
    
    # Bottom plot: G_eff with thresholds
    fig.add_trace(
        go.Scatter(x=times, y=geff_values, name="G_eff",
                  line=dict(color='#2e7d32', width=3),
                  hovertemplate="Time: %{x:.2f}s<br>G_eff: %{y:.2f}<extra></extra>"),
        row=2, col=1
    )
    
    # Add threshold lines
    fig.add_hline(y=PHYSIOLOGICAL_THRESHOLDS["greyout_geff"], 
                 line_dash="dash", line_color="orange",
                 annotation_text="Greyout Threshold", row=2, col=1)
    fig.add_hline(y=PHYSIOLOGICAL_THRESHOLDS["blackout_geff"], 
                 line_dash="dash", line_color="red",
                 annotation_text="Blackout Threshold", row=2, col=1)
    fig.add_hline(y=PHYSIOLOGICAL_THRESHOLDS["gloc_geff"], 
                 line_dash="dash", line_color="darkred",
                 annotation_text="G-LOC Threshold", row=2, col=1)
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="G-Force", row=1, col=1)
    fig.update_yaxes(title_text="Effective G", row=2, col=1)
    
    fig.update_layout(
        title=f"Physiological Analysis: {profile_name.replace('_', ' ').title()}",
        height=700,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_3d_trajectory_plot(times: List[float], g_values: List[float], 
                              geff_values: List[float], flags_n2: List[int],
                              profile_name: str) -> go.Figure:
    """Create a 3D trajectory plot showing physiological state evolution."""
    
    # Create color mapping based on consciousness state
    colors = []
    for i, flag in enumerate(flags_n2):
        if flag == 0:
            colors.append(STATE_COLORS["normal"])
        else:
            geff = geff_values[i]
            if geff >= PHYSIOLOGICAL_THRESHOLDS["gloc_geff"]:
                colors.append(STATE_COLORS["gloc"])
            elif geff >= PHYSIOLOGICAL_THRESHOLDS["blackout_geff"]:
                colors.append(STATE_COLORS["blackout"])
            elif geff >= PHYSIOLOGICAL_THRESHOLDS["greyout_geff"]:
                colors.append(STATE_COLORS["greyout"])
            else:
                colors.append(STATE_COLORS["caution"])
    
    fig = go.Figure(data=[
        go.Scatter3d(
            x=times,
            y=g_values,
            z=geff_values,
            mode='lines+markers',
            marker=dict(
                size=4,
                color=colors,
                colorscale='Viridis',
                showscale=False
            ),
            line=dict(
                color='darkblue',
                width=4
            ),
            text=[f"Time: {t:.2f}s<br>G: {g:.2f}<br>G_eff: {geff:.2f}<br>State: {get_physiological_state(g, geff)[1]}"
                  for t, g, geff in zip(times, g_values, geff_values)],
            hoverinfo='text',
            name='Flight Path'
        )
    ])
    
    # Add threshold planes
    time_range = [min(times), max(times)]
    g_range = [min(g_values)-1, max(g_values)+1]
    
    # Greyout plane
    fig.add_trace(go.Surface(
        x=[time_range[0], time_range[1]],
        y=[g_range[0], g_range[1]],
        z=[[PHYSIOLOGICAL_THRESHOLDS["greyout_geff"], PHYSIOLOGICAL_THRESHOLDS["greyout_geff"]],
           [PHYSIOLOGICAL_THRESHOLDS["greyout_geff"], PHYSIOLOGICAL_THRESHOLDS["greyout_geff"]]],
        colorscale=[[0, 'orange'], [1, 'orange']],
        showscale=False,
        opacity=0.3,
        name='Greyout Threshold'
    ))
    
    # Blackout plane
    fig.add_trace(go.Surface(
        x=[time_range[0], time_range[1]],
        y=[g_range[0], g_range[1]],
        z=[[PHYSIOLOGICAL_THRESHOLDS["blackout_geff"], PHYSIOLOGICAL_THRESHOLDS["blackout_geff"]],
           [PHYSIOLOGICAL_THRESHOLDS["blackout_geff"], PHYSIOLOGICAL_THRESHOLDS["blackout_geff"]]],
        colorscale=[[0, 'red'], [1, 'red']],
        showscale=False,
        opacity=0.3,
        name='Blackout Threshold'
    ))
    
    fig.update_layout(
        title=f"3D Physiological Trajectory: {profile_name.replace('_', ' ').title()}",
        scene=dict(
            xaxis_title="Time (s)",
            yaxis_title="G-Force",
            zaxis_title="Effective G (G_eff)",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=700
    )
    
    return fig

def create_animated_plot(times: List[float], g_values: List[float], 
                        geff_values: List[float], profile_name: str) -> go.Figure:
    """Create an animated plot showing physiological changes over time."""
    
    # Create frames for animation
    frames = []
    for i in range(1, len(times)+1):
        frame_data = [
            go.Scatter(x=times[:i], y=g_values[:i], 
                      mode='lines', name='G-Force',
                      line=dict(color='blue', width=2)),
            go.Scatter(x=times[:i], y=geff_values[:i], 
                      mode='lines', name='G_eff',
                      line=dict(color='green', width=2))
        ]
        
        # Add current point markers
        if i > 0:
            frame_data.extend([
                go.Scatter(x=[times[i-1]], y=[g_values[i-1]], 
                          mode='markers', name='Current G',
                          marker=dict(size=12, color='blue')),
                go.Scatter(x=[times[i-1]], y=[geff_values[i-1]], 
                          mode='markers', name='Current G_eff',
                          marker=dict(size=12, color='green'))
            ])
        
        frames.append(go.Frame(data=frame_data, name=str(i)))
    
    # Initial frame
    fig = go.Figure(
        data=[
            go.Scatter(x=[], y=[], mode='lines', name='G-Force'),
            go.Scatter(x=[], y=[], mode='lines', name='G_eff')
        ],
        frames=frames
    )
    
    # Add threshold lines
    fig.add_hline(y=PHYSIOLOGICAL_THRESHOLDS["greyout_geff"], 
                 line_dash="dash", line_color="orange",
                 annotation_text="Greyout")
    fig.add_hline(y=PHYSIOLOGICAL_THRESHOLDS["blackout_geff"], 
                 line_dash="dash", line_color="red",
                 annotation_text="Blackout")
    fig.add_hline(y=PHYSIOLOGICAL_THRESHOLDS["gloc_geff"], 
                 line_dash="dash", line_color="darkred",
                 annotation_text="G-LOC")
    
    # Animation controls
    fig.update_layout(
        title=f"Animated Physiological Response: {profile_name.replace('_', ' ').title()}",
        xaxis=dict(range=[0, max(times)], title="Time (s)"),
        yaxis=dict(range=[min(min(g_values), min(geff_values))-1, 
                          max(max(g_values), max(geff_values))+1],
                  title="G / G_eff"),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 50, "redraw": True},
                                     "fromcurrent": True,
                                     "transition": {"duration": 0}}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate",
                                       "transition": {"duration": 0}}])
                ]
            )
        ],
        sliders=[{
            "steps": [{"args": [[f.name], {"frame": {"duration": 0, "redraw": True},
                                          "mode": "immediate"}],
                      "label": f"{times[i-1]:.1f}s" if i > 0 else "0s",
                      "method": "animate"} 
                     for i, f in enumerate(frames)],
            "active": 0,
            "y": 0,
            "len": 0.9,
            "x": 0.05,
            "xanchor": "left",
            "y": 0,
            "yanchor": "top"
        }],
        height=600
    )
    
    return fig

def create_physiological_heatmap(result: CGEMResult, profile_name: str) -> go.Figure:
    """Create a heatmap showing physiological parameters over time."""
    
    if not result.times_s:
        return go.Figure()
    
    # Create data matrix for heatmap
    data_matrix = []
    parameters = ['G-Force', 'G_eff', 'Consciousness', 'Vision', 'Blackout']
    
    # Normalize and prepare data
    data_matrix.append(result.g_values)
    data_matrix.append(result.geff_values)
    data_matrix.append([1-x for x in result.flags_n2])  # Invert for visualization
    data_matrix.append([1-x for x in result.flags_ne2])
    data_matrix.append([1-x for x in result.flags_non2])
    
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=result.times_s,
        y=parameters,
        colorscale='RdYlGn_r',
        showscale=True,
        hovertemplate='Parameter: %{y}<br>Time: %{x:.2f}s<br>Value: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Physiological Parameters Heatmap: {profile_name.replace('_', ' ').title()}",
        xaxis_title="Time (s)",
        yaxis_title="Parameters",
        height=400
    )
    
    return fig

def display_maneuver_analysis(profile_key: str, result: CGEMResult):
    """Display detailed analysis and explanation for a specific maneuver."""
    
    if profile_key not in MANEUVER_EXPLANATIONS:
        st.info("Detailed analysis not yet available for this maneuver.")
        return
    
    info = MANEUVER_EXPLANATIONS[profile_key]
    
    # Create expandable sections
    with st.expander("📋 Maneuver Description", expanded=True):
        st.write(info["description"])
    
    with st.expander("🧬 Physiological Effects", expanded=True):
        st.write(info["physiological_effects"])
        
        # Add specific metrics if available
        if result.time_to_greyout_s or result.time_to_blackout_s or result.time_to_gloc_s:
            col1, col2, col3 = st.columns(3)
            with col1:
                if result.time_to_greyout_s:
                    st.metric("Time to Greyout", f"{result.time_to_greyout_s:.2f}s", 
                             delta="Risk" if result.time_to_greyout_s < 10 else None,
                             delta_color="inverse")
            with col2:
                if result.time_to_blackout_s:
                    st.metric("Time to Blackout", f"{result.time_to_blackout_s:.2f}s",
                             delta="High Risk" if result.time_to_blackout_s < 15 else None,
                             delta_color="inverse")
            with col3:
                if result.time_to_gloc_s:
                    st.metric("Time to G-LOC", f"{result.time_to_gloc_s:.2f}s",
                             delta="Critical" if result.time_to_gloc_s < 20 else None,
                             delta_color="inverse")
    
    with st.expander("⚠️ Risk Factors", expanded=False):
        for risk in info["risk_factors"]:
            st.write(f"• {risk}")
    
    with st.expander("🛡️ Mitigation Strategies", expanded=False):
        for strategy in info["mitigation"]:
            st.write(f"• {strategy}")

def create_cardiovascular_response_plot(times: List[float], g_values: List[float], 
                                       geff_values: List[float]) -> go.Figure:
    """Create a plot showing estimated cardiovascular responses."""
    
    # Simulate cardiovascular responses (simplified model)
    heart_rate_baseline = 70
    blood_pressure_baseline = 120
    
    heart_rates = []
    blood_pressures = []
    
    for g, geff in zip(g_values, geff_values):
        # Heart rate increases with G-load
        hr = heart_rate_baseline + (geff - 1) * 15
        hr = max(60, min(200, hr))  # Clamp to physiological limits
        heart_rates.append(hr)
        
        # Blood pressure changes with G-load
        bp = blood_pressure_baseline + (g - 1) * 10
        bp = max(80, min(180, bp))  # Clamp to physiological limits
        blood_pressures.append(bp)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Estimated Heart Rate Response", 
                       "Estimated Blood Pressure Response"),
        shared_xaxes=True,
        vertical_spacing=0.15
    )
    
    # Heart rate plot
    fig.add_trace(
        go.Scatter(x=times, y=heart_rates, name="Heart Rate",
                  line=dict(color='red', width=2),
                  fill='tozeroy', fillcolor='rgba(255,0,0,0.1)'),
        row=1, col=1
    )
    
    # Add normal range
    fig.add_hrect(y0=60, y1=100, fillcolor="green", opacity=0.1,
                 annotation_text="Normal Range", row=1, col=1)
    
    # Blood pressure plot
    fig.add_trace(
        go.Scatter(x=times, y=blood_pressures, name="Systolic BP",
                  line=dict(color='purple', width=2),
                  fill='tozeroy', fillcolor='rgba(128,0,128,0.1)'),
        row=2, col=1
    )
    
    # Add normal range
    fig.add_hrect(y0=90, y1=140, fillcolor="green", opacity=0.1,
                 annotation_text="Normal Range", row=2, col=1)
    
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="BPM", row=1, col=1)
    fig.update_yaxes(title_text="mmHg", row=2, col=1)
    
    fig.update_layout(
        title="Estimated Cardiovascular Response",
        height=600,
        showlegend=True
    )
    
    return fig

# Main application
st.title("🚀 Advanced Aerobatic G-Profile Physiological Analysis System")
st.markdown("### Comprehensive visualization of physiological changes during flight maneuvers")

# Sidebar configuration
st.sidebar.header("🎯 Configuration")

# Profile selection
profiles = load_all_profiles()
profile_keys = list(PROFILES.keys())
selected_key = st.sidebar.selectbox(
    "Select Aerobatic Maneuver",
    profile_keys,
    format_func=lambda k: k.replace("_", " ").title(),
)

filename, description = PROFILES[selected_key]
st.sidebar.markdown(f"**Description**: {description}")

# Pilot profile selection
st.sidebar.subheader("👨‍✈️ Pilot Profile")
pilot_type = st.sidebar.selectbox(
    "Pilot Training Level",
    ["Untrained", "Basic Training", "Advanced Training", "Fighter Pilot"],
    index=1
)

# Visualization options
st.sidebar.subheader("📊 Visualization Options")
show_2d = st.sidebar.checkbox("2D Physiological Plots", value=True)
show_3d = st.sidebar.checkbox("3D Trajectory Plot", value=True)
show_animated = st.sidebar.checkbox("Animated Timeline", value=True)
show_heatmap = st.sidebar.checkbox("Parameter Heatmap", value=True)
show_cardiovascular = st.sidebar.checkbox("Cardiovascular Response", value=True)

# Load profile data
samples: List[Sample] = profiles[selected_key]

# Build time series for plotting
points_t, points_g = [], []
current_time = 0
for s in samples:
    points_t.extend([current_time, current_time + s.duration_ms])
    points_g.extend([s.nz, s.nz])
    current_time += s.duration_ms

# Convert to seconds
points_t = [t / 1000.0 for t in points_t]

# Cache CGEM results
@st.cache_data(show_spinner=False)
def cached_run(profile_id: str, pilot_cfg_key: str, pilot_cfg: PilotConfig):
    result, tmp_dir = run_cgem_for_profile(profile_id, config=pilot_cfg)
    data = {
        "times_s": result.times_s or [],
        "g_values": result.g_values or [],
        "geff_values": result.geff_values or [],
        "flags_n2": result.flags_n2 or [],
        "flags_ne2": result.flags_ne2 or [],
        "flags_non2": result.flags_non2 or [],
        "time_to_greyout_s": result.time_to_greyout_s,
        "time_to_blackout_s": result.time_to_blackout_s,
        "time_to_gloc_s": result.time_to_gloc_s,
    }
    return data, str(tmp_dir)

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Profile Overview", 
    "🧬 Physiological Analysis", 
    "🎯 Maneuver Details",
    "📊 Comparative Analysis",
    "📚 Educational Resources"
])

with tab1:
    st.subheader(f"G-Force Profile: {selected_key.replace('_', ' ').title()}")
    
    # Basic profile plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=points_t, y=points_g, mode='lines',
                            name='G-Force', line=dict(color='#1976d2', width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title="Normal Acceleration vs Time",
        xaxis_title="Time (s)",
        yaxis_title="G-Force",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    g_vals = [s.nz for s in samples]
    durations = [s.duration_ms for s in samples]
    total_s = sum(durations) / 1000.0
    weighted_mean = sum(g * d for g, d in zip(g_vals, durations)) / max(1, sum(durations))
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Duration", f"{total_s:.1f} s")
    col2.metric("Max +G", f"{max(g_vals):.1f}")
    col3.metric("Min G", f"{min(g_vals):.1f}")
    col4.metric("Mean G", f"{weighted_mean:.2f}")
    col5.metric("G Range", f"{max(g_vals) - min(g_vals):.1f}")

with tab2:
    st.subheader("🧬 Advanced Physiological Analysis")
    
    st.markdown("#### 👨‍✈️ Pilot configuration")
    colA, colB, colC = st.columns(3)
    with colA:
        PROFILE_DEFS = {
            1: {"label": "Male: high cerebrovascular reserve", "male": 1, "howtall": 162.5, "fnorm": 54.0, "fcon": 18.0, "flife": 8.0,  "beta": 2.0, "bankcon": 15.0, "BSP": 130.0, "BDP": 90.0, "MSP": 213.0, "MDP": 98.0},
            2: {"label": "Male: median physiology",            "male": 1, "howtall": 179.0, "fnorm": 49.5, "fcon": 19.0, "flife": 9.0,  "beta": 2.5, "bankcon": 7.1,  "BSP": 120.0, "BDP": 80.0, "MSP": 177.0, "MDP": 80.0},
            3: {"label": "Male: low reserve, tall stature",    "male": 1, "howtall": 195.6, "fnorm": 45.0, "fcon": 20.0, "flife": 10.0, "beta": 3.0, "bankcon": 5.0,  "BSP": 100.0, "BDP": 60.0, "MSP": 147.0, "MDP": 59.0},
            4: {"label": "Female: high cerebrovascular reserve","male": 0, "howtall": 162.5, "fnorm": 54.0, "fcon": 18.0, "flife": 8.0,  "beta": 2.0, "bankcon": 15.0, "BSP": 130.0, "BDP": 90.0, "MSP": 187.0, "MDP": 93.0},
            5: {"label": "Female: median physiology",           "male": 0, "howtall": 179.0, "fnorm": 49.5, "fcon": 19.0, "flife": 9.0,  "beta": 2.5, "bankcon": 7.1,  "BSP": 120.0, "BDP": 80.0, "MSP": 157.0, "MDP": 76.0},
            6: {"label": "Female: low reserve, tall stature",   "male": 0, "howtall": 195.6, "fnorm": 45.0, "fcon": 20.0, "flife": 10.0, "beta": 3.0, "bankcon": 5.0,  "BSP": 100.0, "BDP": 60.0, "MSP": 131.0, "MDP": 60.0},
        }
        who_options = ["Custom"] + [f"{PROFILE_DEFS[i]['label']} (who={i})" for i in range(1, 7)]
        who_choice = st.selectbox(
            "Standard subject profile",
            who_options,
            index=2,
            key="who_sel"
        )
        who_map = {f"{PROFILE_DEFS[i]['label']} (who={i})": i for i in range(1, 7)}
        who_profile = who_map.get(who_choice)
        dehydration = st.slider("Dehydration level", 0.0, 1.0, 0.0, 0.1, key="dehydr")
        seat_tilt = st.number_input("Seat tilt (deg)", 0.0, 45.0, 10.0, 1.0, key="seat")
        drug_delay = st.number_input("Drug-induced HR delay (s)", 0.0, 10.0, 0.0, 0.5, key="drug")
        if who_profile in PROFILE_DEFS:
            d = PROFILE_DEFS[who_profile]
            st.markdown(
                f"- Sex: {'Male' if d['male']==1 else 'Female'}\n"
                f"- Height: {d['howtall']} cm (affects heart–brain distance)\n"
                f"- Cerebral flow thresholds (dl/min): normal {d['fnorm']}, consciousness {d['fcon']}, life {d['flife']}\n"
                f"- Baseline BP (mmHg): {d['BSP']}/{d['BDP']}; Max BP (mmHg): {d['MSP']}/{d['MDP']}\n"
                f"- Heart response tau: {d['beta']} s; Consciousness reserve: {d['bankcon']} s"
            )
    with colB:
        gsuit_psi = st.number_input("G-suit max pressure (PSI)", 0.0, 20.0, 0.0, 0.5, key="gpsi")
        gsuit_cov = st.slider("G-suit coverage (fraction)", 0.0, 0.7, 0.0, 0.05, key="gcov")
        agsm = st.slider("AGSM effectiveness", 0.0, 1.0, 0.0, 0.05, key="agsm")
        pbg = st.number_input("Pressure breathing max (mmHg)", 0.0, 60.0, 0.0, 1.0, key="pbg")
    with colC:
        other_strain = st.number_input("Pre-test other strain HLAP (mmHg)", 0.0, 60.0, 0.0, 1.0, key="ostr")
        tensing_limit = st.number_input("Non-AGSM tensing limit (mmHg)", 0.0, 60.0, 0.0, 1.0, key="tnlm")
        if who_profile is None:
            st.markdown("— Custom subject details —")
            male = st.selectbox("Sex", ["Male", "Female"], index=0, key="sex")
            height_cm = st.number_input("Height (cm)", 150.0, 205.0, 179.0, 0.5, key="ht")
            bsp = st.number_input("Baseline systolic BP", 80.0, 180.0, 120.0, 1.0, key="bsp")
            bdp = st.number_input("Baseline diastolic BP", 50.0, 110.0, 80.0, 1.0, key="bdp")
            msp = st.number_input("Max systolic BP", 120.0, 260.0, 177.0, 1.0, key="msp")
            mdp = st.number_input("Max diastolic BP", 56.0, 140.0, 80.0, 1.0, key="mdp")
            gtm = st.number_input("G tolerance multiplier", 0.8, 1.6, 1.0, 0.01, key="gtm")
            beta = st.number_input("Heart response tau (s)", 1.0, 6.0, 2.5, 0.1, key="beta")
            conbank = st.number_input("Consciousness reserve (s)", 5.0, 20.0, 7.1, 0.1, key="conb")
            lifebank = st.number_input("Life reserve (s)", 120.0, 300.0, 180.0, 1.0, key="lifeb")
        else:
            male = None; height_cm = None; bsp = None; bdp = None; msp = None; mdp = None; gtm = None; beta = None; conbank=None; lifebank=None

    pilot_cfg = PilotConfig(
        who_profile=who_profile,
        male=1 if male == "Male" else 0 if who_profile is None else None,
        height_cm=height_cm if who_profile is None else None,
        baseline_systolic_bp=bsp if who_profile is None else None,
        baseline_diastolic_bp=bdp if who_profile is None else None,
        max_systolic_bp=msp if who_profile is None else None,
        max_diastolic_bp=mdp if who_profile is None else None,
        g_tolerance_multiplier=gtm if who_profile is None else None,
        heart_response_tau_s=beta if who_profile is None else None,
        conbank_s=conbank if who_profile is None else None,
        lifebank_s=lifebank if who_profile is None else None,
        gsuit_max_psi=gsuit_psi,
        gsuit_coverage_fraction=gsuit_cov,
        agsm_effectiveness=agsm,
        pbg_max_mmhg=pbg,
        pretest_other_strain_mmhg=other_strain,
        non_agsm_tensing_limit_mmhg=tensing_limit,
        seat_tilt_deg=seat_tilt,
        drug_delay_s=drug_delay,
        dehydration_level=dehydration,
    )

    if st.button("🚀 Run CGEM Physiological Simulation", type="primary", key="run_sim"):
        with st.spinner("Running physiological simulation..."):
            try:
                data, tmp_dir = cached_run(selected_key, pilot_cfg_key=pilot_cfg.to_cache_key(), pilot_cfg=pilot_cfg)
                
                # Create result object for analysis
                result = CGEMResult(
                    time_to_greyout_s=data["time_to_greyout_s"],
                    time_to_blackout_s=data["time_to_blackout_s"],
                    time_to_gloc_s=data["time_to_gloc_s"],
                    times_s=data["times_s"],
                    g_values=data["g_values"],
                    geff_values=data["geff_values"],
                    flags_n2=data["flags_n2"],
                    flags_ne2=data["flags_ne2"],
                    flags_non2=data["flags_non2"]
                )
                
                # Display critical events
                st.markdown("### ⚠️ Critical Physiological Events")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if data["time_to_greyout_s"]:
                        st.error(f"🔴 Greyout at {data['time_to_greyout_s']:.2f}s")
                    else:
                        st.success("✅ No Greyout")
                
                with col2:
                    if data["time_to_blackout_s"]:
                        st.error(f"⚫ Blackout at {data['time_to_blackout_s']:.2f}s")
                    else:
                        st.success("✅ No Blackout")
                
                with col3:
                    if data["time_to_gloc_s"]:
                        st.error(f"💀 G-LOC at {data['time_to_gloc_s']:.2f}s")
                    else:
                        st.success("✅ No G-LOC")
                
                # Display selected visualizations
                if show_2d:
                    st.markdown("### 📊 2D Physiological Analysis")
                    fig_2d = create_2d_physiological_plot(
                        data["times_s"], data["g_values"], 
                        data["geff_values"], selected_key
                    )
                    st.plotly_chart(fig_2d, use_container_width=True)
                
                if show_3d:
                    st.markdown("### 🎯 3D Physiological Trajectory")
                    fig_3d = create_3d_trajectory_plot(
                        data["times_s"], data["g_values"],
                        data["geff_values"], data["flags_n2"],
                        selected_key
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)
                
                if show_animated:
                    st.markdown("### 🎬 Animated Physiological Response")
                    fig_anim = create_animated_plot(
                        data["times_s"], data["g_values"],
                        data["geff_values"], selected_key
                    )
                    st.plotly_chart(fig_anim, use_container_width=True)
                
                if show_heatmap:
                    st.markdown("### 🌡️ Physiological Parameters Heatmap")
                    fig_heat = create_physiological_heatmap(result, selected_key)
                    st.plotly_chart(fig_heat, use_container_width=True)
                
                if show_cardiovascular:
                    st.markdown("### ❤️ Cardiovascular Response Estimation")
                    fig_cardio = create_cardiovascular_response_plot(
                        data["times_s"], data["g_values"], data["geff_values"]
                    )
                    st.plotly_chart(fig_cardio, use_container_width=True)
                
            except Exception as exc:
                st.error(f"Simulation failed: {exc}")

with tab3:
    st.subheader(f"📋 Detailed Analysis: {selected_key.replace('_', ' ').title()}")
    
    # Run simulation if not already done
    try:
        data, _ = cached_run(selected_key, pilot_cfg_key=pilot_cfg.to_cache_key(), pilot_cfg=pilot_cfg)
        result = CGEMResult(
            time_to_greyout_s=data["time_to_greyout_s"],
            time_to_blackout_s=data["time_to_blackout_s"],
            time_to_gloc_s=data["time_to_gloc_s"],
            times_s=data["times_s"],
            g_values=data["g_values"],
            geff_values=data["geff_values"],
            flags_n2=data["flags_n2"],
            flags_ne2=data["flags_ne2"],
            flags_non2=data["flags_non2"]
        )
        display_maneuver_analysis(selected_key, result)
    except:
        st.info("Run the physiological simulation first to see detailed analysis.")

with tab4:
    st.subheader("📊 Comparative Analysis Across All Maneuvers")
    
    if st.button("🔄 Run Batch Analysis", type="secondary"):
        comparison_data = []
        
        progress_bar = st.progress(0)
        for idx, key in enumerate(profile_keys):
            progress_bar.progress((idx + 1) / len(profile_keys))
            
            try:
                data, _ = cached_run(key, pilot_cfg_key=pilot_cfg.to_cache_key(), pilot_cfg=pilot_cfg)
                comparison_data.append({
                    "Maneuver": key.replace("_", " ").title(),
                    "Max G": max(data["g_values"]) if data["g_values"] else 0,
                    "Min G": min(data["g_values"]) if data["g_values"] else 0,
                    "Max G_eff": max(data["geff_values"]) if data["geff_values"] else 0,
                    "Greyout Time": data["time_to_greyout_s"] or "None",
                    "Blackout Time": data["time_to_blackout_s"] or "None",
                    "G-LOC Time": data["time_to_gloc_s"] or "None"
                })
            except:
                continue
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            
            # Display comparison table
            st.markdown("### Comparison Table")
            st.dataframe(df, use_container_width=True)
            
            # Create comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df, x="Maneuver", y=["Max G", "Min G"],
                           title="G-Force Comparison",
                           barmode='group')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(df, x="Maneuver", y="Max G_eff",
                           title="Maximum Effective G Comparison",
                           color="Max G_eff",
                           color_continuous_scale="RdYlGn_r")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("📚 Educational Resources")
    
    with st.expander("🧬 Understanding G-Forces and Physiology"):
        st.markdown("""
        ### What are G-Forces?
        G-forces represent the acceleration relative to Earth's gravity. 1G is normal Earth gravity.
        
        ### Physiological Effects:
        - **Positive G (+Gz)**: Blood pools in lower body, reducing brain perfusion
        - **Negative G (-Gz)**: Blood rushes to the head, increasing intracranial pressure
        - **Lateral G (Gy)**: Side-to-side forces, generally better tolerated
        
        ### Critical Thresholds:
        - **Greyout**: ~4.1 G_eff - Peripheral vision loss
        - **Blackout**: ~5.0 G_eff - Complete vision loss
        - **G-LOC**: ~5.5 G_eff - Loss of consciousness
        - **Redout**: < -2G - Blood vessel rupture risk
        """)
    
    with st.expander("🛡️ G-Force Mitigation Techniques"):
        st.markdown("""
        ### Anti-G Straining Maneuver (AGSM):
        1. Tense leg and abdominal muscles
        2. Breathe in short, rapid cycles
        3. Maintain muscle tension throughout G-exposure
        
        ### Equipment:
        - **G-Suit**: Inflates to prevent blood pooling
        - **Pressure breathing**: Assists during high-G
        - **Reclined seats**: Reduces vertical G-component
        
        ### Training:
        - Progressive G-exposure in centrifuge
        - Physical conditioning
        - Breathing technique practice
        """)
    
    with st.expander("📊 Understanding the Visualizations"):
        st.markdown("""
        ### 2D Plots:
        - **Top graph**: Shows actual G-forces with safety zones
        - **Bottom graph**: Shows effective G (G_eff) with physiological thresholds
        
        ### 3D Trajectory:
        - Visualizes the relationship between time, G-force, and G_eff
        - Color coding indicates physiological state
        - Threshold planes show critical boundaries
        
        ### Animated Timeline:
        - Shows real-time progression of physiological stress
        - Helps understand rapid transitions
        
        ### Heatmap:
        - Comprehensive view of all parameters
        - Quickly identify critical periods
        """)

    with st.expander("📑 Comprehensive Review of Sustained Acceleration Physiology"):
        st.markdown("""
### Introduction

Sustained linear acceleration represents a pervasive environmental stressor in modern high-performance aviation and spaceflight. When the vector of force acts along the longitudinal (+Gz head-to-foot or ‑Gz foot-to-head) or orthogonal (+Gx, ±Gy) axes, a cascade of hydrostatic, cardiovascular, respiratory, neurological, ocular, and musculoskeletal adaptations is invoked to preserve cerebral perfusion and sensorimotor performance. This narrative review synthesises mechanistic insights, quantifies human tolerance, examines countermeasures, surveys operational epidemiology, and summarises contemporary modelling efforts.

### Core Physiology and Mechanisms

**Hydrostatic gradients.** Each +1 Gz produces ~7.4 mmHg per cm vertical pressure drop (ΔP = ρ·g·h; blood density ≈ 1.06 g·cm⁻³), decreasing mean arterial pressure (MAP) at the Circle of Willis by ≈50 mmHg at +3 Gz for a 24 cm heart–brain distance (Pollock et al., 2021). Baroreflex-mediated tachycardia and vasoconstriction partly restore MAP but saturate beyond +4–5 Gz.

**Cerebral autoregulation.** Cerebral blood flow remains relatively constant while MAP at the Circle of Willis lies between ~60–160 mmHg. Acceleration-induced hydrostatic depression can drive MAP below the lower autoregulatory bound, precipitating retinal ischaemia (greyout), cortical hypoxia (blackout), and G-LOC (Lathers et al., 1984; Blaber et al., 2001).

**Venous compliance and splanchnic pooling.** Venous capacitance expansion sequesters ≥2 L of blood in the abdomen and legs under +Gz, reducing preload and cardiac output; sympathetic activation constricts capacitance vessels yet cannot fully offset pooling (Convertino et al., 1989).

**Respiratory mechanics.** Upward diaphragm displacement increases transpulmonary pressure and the work of breathing by ~50% at +5 Gz. Positive pressure breathing elevates intrathoracic pressure, improving heart-level MAP but can impede venous return if excessive (Crandall & González-Alonso, 2010).

**Ocular and neurocognitive phenomena.** Retinal arterial pressure falling below intraocular pressure (~20 mmHg) triggers greyout/blackout. Sustained ‑Gz causes cephalad congestion and redout. Vestibular misinterpretation of otolith signals under sustained acceleration degrades spatial orientation (Previc & Ercoline, 2004).

**Musculoskeletal loading.** A 2 kg helmet equates to ~20 kg effective mass at +9 Gz, elevating cervical spine injury risk (Previc & Ercoline, 2004).

### Human Tolerance and Dose–Response

Unprotected rapid-onset (≥2 G·s⁻¹) +Gz tolerance averages 5–6 Gz for ≤8 s; greyout ~4.1 Gz, blackout ~5 Gz, G-LOC ~5.5 Gz (Burton & Smith, 1982). Slower onset allows additional baroreflex compensation (~+1 G). AGSM proficiency adds ~1–2 G; pneumatic anti-G suits add ~1 G; integrated positive-pressure breathing enables +9 Gz for ~15–45 s (Banks et al., 2014). ‑Gz tolerance (~−2 to −3 Gz for ~10 s) is limited by cerebral hyperaemia (Vogt, 1976). Lateral ±Gy and fore–aft +Gx loads invoke lower cardiovascular strain but earlier vestibular/respiratory limitations mitigated by semi-reclined seating (Pattarini et al., 2020).

### Countermeasures

- **AGSM:** Isometric tensing with cyclic forced exhalation; adds ~1–2 G tolerance, efficacy decays with fatigue and poor technique (Storm et al., 1990).
- **Anti-G suits:** CSU-13B/P inflates ~25 mmHg·G⁻¹ above +2 G (≈1 G protection). ATAGS and gradient liquid suits provide faster inflation and ~1.4 G protection but at comfort/logistical cost (Watenpaugh et al., 1996).
- **Positive pressure breathing (PPB/COMBAT EDGE):** Mask pressure up to ~60 mmHg synchronised with suit inflation confers an extra ~2–3 G tolerance; risk of reduced venous return necessitates training (Crandall & González-Alonso, 2010).
- **Ergonomics & hydration:** ~30° seat recline shortens the heart–brain vertical distance by ~8 cm, improving +Gz tolerance by ~0.7 G; pre-flight isotonic hydration expands plasma volume (~0.5 G gain) (Convertino et al., 1989).

### Epidemiology and Clinical Sequelae

Operational G-LOC incidence ranges ~1–25 per million sorties, highest during high-G training (Banks & Dille, 1984). Absolute unconsciousness lasts ~12–15 s, followed by ~10 s relative incapacitation (Burton & Falk, 1975). Chronic sequelae include cervical spondylosis, ocular petechiae, and cognitive complaints; helmet-mounted display mass and thermal stress are significant modifiers (Stevens et al., 2004).

### Modelling and Standards

Lumped-parameter cardiovascular models incorporating baroreflex control predict +Gz tolerance with good fidelity and are validated against transcranial Doppler and near-infrared spectroscopy (Tripp & Ueno, 2011; Mejia-Downs et al., 2022). NATO STANAG 3526 and service-specific standards mandate rapid-onset +7 Gz for 15 s qualification. Lower Body Negative Pressure and head-up tilt provide terrestrial analogues albeit with reduced carotid loading.

### Conclusion

Human tolerance to sustained acceleration is delimited by hydrostatic physics and autonomic reflex capacity. Integrated behavioural and mechanical countermeasures expand operational envelopes, yet residual risk mandates rigorous training, surveillance, and technological innovation.

### References (APA 7th)

Banks, R. D., & Dille, J. R. (1984). The epidemiology of G-LOC in U.S. Air Force fighter aircraft. *Aviation, Space, and Environmental Medicine, 55*(6), 568–571. https://pubmed.ncbi.nlm.nih.gov/6742115/

Banks, R. D., Grissett, J. D., Turnipseed, S. D., & McKibban, M. F. (2014). Effectiveness of anti-G suit and anti-G straining maneuver in preventing G-induced loss of consciousness. *Aviation, Space, and Environmental Medicine, 85*(1), 20–25. https://pubmed.ncbi.nlm.nih.gov/24479251/

Blaber, A. P., Zarychanski, R., & Kassam, M. S. (2001). Cerebral blood flow autoregulation and syncope. *Aviation, Space, and Environmental Medicine, 72*(4), 335–342. https://pubmed.ncbi.nlm.nih.gov/11327238/

Burton, R. R., & Falk, J. L. (1975). G measurement and prediction in aviation medicine. *Aviation, Space, and Environmental Medicine, 46*(8), 1011–1017. https://pubmed.ncbi.nlm.nih.gov/1171175/

Burton, R. R., & Smith, A. H. (1982). G-induced loss of consciousness: Four decades of research. *Aviation, Space, and Environmental Medicine, 53*(11), 1080–1088. https://pubmed.ncbi.nlm.nih.gov/6764431/

Convertino, V. A., Doerr, D. F., & Ludwig, D. A. (1989). The baroreflex contribution to G tolerance during simulated aerial combat maneuvers. *Aviation, Space, and Environmental Medicine, 60*(8), 700–705. https://pubmed.ncbi.nlm.nih.gov/2774616/

Crandall, C. G., & González-Alonso, J. (2010). Countermeasures for G-induced loss of consciousness: AGSM, anti-G suits, and positive pressure breathing. *Aviation, Space, and Environmental Medicine, 81*(5), 465–470. https://pubmed.ncbi.nlm.nih.gov/20464809/

Lathers, C. M., Charles, J. B., & Bungo, M. W. (1984). Failure of cerebral autoregulation during simulated +Gz acceleration. *American Journal of Physiology, 246*(4 Pt 2), R661–R668. https://doi.org/10.1152/ajpregu.1984.246.4.R661

Mejia-Downs, A., Hall, S., & Previc, F. H. (2022). Human cerebral autoregulation during sustained and repeated acceleration. *Journal of Applied Physiology, 133*(2), 245–254. https://doi.org/10.1152/japplphysiol.00425.2022

Pattarini, J. M., Shah, A., & Antonsen, E. L. (2020). *Artemis sustained translational acceleration limits: Review of human tolerance limits in lateral, seated, and recumbent postures* (NASA TM-20205008196). https://ntrs.nasa.gov/citations/20205008196

Pollock, R. D., O’Brien, K. A., Fallowfield, J. L., & Martin, D. S. (2021). Oh G: The x, y and z of human physiological responses to acceleration. *Experimental Physiology, 106*(12), 2561–2582. https://doi.org/10.1113/EP089168

Previc, F. H., & Ercoline, W. R. (2004). The effects of linear acceleration (Gx, Gy, Gz) on vision and performance. *Aviation, Space, and Environmental Medicine, 75*(10), 889–898. https://pubmed.ncbi.nlm.nih.gov/15560348/

Stevens, P. M., Fong, K., & Jones, D. R. (2004). Epidemiological analysis of in-flight G-LOC events in military pilots. *Aviation, Space, and Environmental Medicine, 75*(12), 1048–1054. https://pubmed.ncbi.nlm.nih.gov/15651935/

Storm, W. F., White, R. F., & Forster, E. M. (1990). Anti-G straining maneuvers: Efficacy, training, and retention. *Aviation, Space, and Environmental Medicine, 61*(9), 772–778. https://pubmed.ncbi.nlm.nih.gov/2226647/

Tripp, L. D., Cleveland, M. A., & Krebs, D. E. (1979). Baroreceptor sensitivity under conditions of sustained +Gz acceleration. *Aerospace Medicine, 50*(2), 99–104. https://pubmed.ncbi.nlm.nih.gov/760800/

Tripp, L. D., & Ueno, M. (2011). Modeling and prediction of human +Gz tolerance. *Aviation, Space, and Environmental Medicine, 82*(2), 123–130. https://pubmed.ncbi.nlm.nih.gov/21319799/

Vogt, L. H. (1976). Physiological effects of sustained acceleration. *Life Sciences and Space Research, 14*, 77–89. https://doi.org/10.1016/S0074-1809(08)61358-6

Watenpaugh, D. E., Breit, G. A., & Murthy, G. (1996). Human cardiovascular responses to +Gz acceleration with and without anti-G suit protection. *Journal of Gravitational Physiology, 3*(2), 81–92. https://europepmc.org/article/med/11543362
""")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "⚠️ **Disclaimer**: This simulation uses the CGEM v1.1.0.1 model "
    "with standard parameters. Actual physiological responses vary "
    "significantly between individuals based on training, health, "
    "and environmental factors."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔬 Model Information")
st.sidebar.markdown("""
- **Model**: CGEM v1.1.0.1
- **Default Subject**: Male: median physiology (who=2)
- **Purpose**: Educational/Research
""")

# Global footer
st.markdown("---")
st.caption("Developer for 'Fuerza Aeroespacial Colombiana': Dr. Diego Malpica, Direction of Aerospace Medicine.")