from __future__ import annotations

import math
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sqlite3
from datetime import datetime
import io
import json
import base64

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import streamlit.components.v1 as components
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import seaborn as sns

from aerobatic_profiles import load_all_profiles, load_profile, PROFILES, Sample
from cgem_wrapper import run_cgem_for_profile, run_cgem_centrifuge, CGEMResult, PilotConfig

# Configure page
def _find_icon_path() -> Optional[Path]:
    here = Path(__file__).parent
    candidates = [
        here / "icon.png",
        here / "assets" / "icon.png",
        Path.cwd() / "icon.png",
        Path.cwd() / "assets" / "icon.png",
        Path.cwd() / "images" / "icon.png",
        Path.cwd() / "docs" / "icon.png",
    ]
    for p in candidates:
        try:
            if p.exists():
                return p
        except Exception:
            continue
    return None

ICON_PATH = _find_icon_path()
page_icon_arg: Optional[str] = str(ICON_PATH) if ICON_PATH else None
st.set_page_config(
    page_title="G-Effects Model",
    page_icon=page_icon_arg,
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
        background-color: #f8fafc;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
    }
    /* Title styling: light and dark mode */
    :root {
        --title-color-light: #0f172a;
        --title-color-dark: #f8fafc;
    }
    h1, .stApp h1 {
        color: var(--title-color-light);
        letter-spacing: 0.2px;
        font-weight: 800;
    }
    @media (prefers-color-scheme: dark) {
        h1, .stApp h1 {
            color: var(--title-color-dark) !important;
            text-shadow: 0 1px 1px rgba(0,0,0,0.4);
        }
    }
    [data-theme="dark"] h1, [data-theme="dark"] .stApp h1 {
        color: var(--title-color-dark) !important;
        text-shadow: 0 1px 1px rgba(0,0,0,0.4);
    }
    /* Header with logo */
    .app-header { display: flex; align-items: center; gap: 14px; margin: 0.25rem 0 0.75rem; }
    .app-logo { width: 56px; height: 56px; border-radius: 14px; box-shadow: 0 8px 22px rgba(0,0,0,0.25); }
    @media (max-width: 480px) { .app-logo { width: 44px; height: 44px; border-radius: 12px; } }
    .app-subtitle { margin-top: -6px; color: #475569; font-size: 0.92rem; }
    .app-subtitle em { color: inherit; }
    .app-subtitle a { color: inherit; text-decoration: underline; }
    @media (prefers-color-scheme: dark) { .app-subtitle { color: #cbd5e1; } }
    [data-theme="dark"] .app-subtitle { color: #cbd5e1; }
    h2 {
        color: #334155;
        letter-spacing: 0.2px;
    }
    /* Tabs: slightly tighter and professional */
    div.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    div.stTabs [data-baseweb="tab"] { font-size: 0.95rem; padding: 0.3rem 0.6rem; }
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
    },
    "triple_push_pull_loop": {
        "description": "Three successive push–pull loops: brief −G push into inverted arc followed by +G pull-up, repeated three times.",
        "physiological_effects": "Alternating cephalad and caudad blood shifts stress autoregulation; repeated transitions tax baroreflex and may accumulate fatigue.",
        "risk_factors": ["Rapid +/−G transitions", "Potential redout during pushes", "Greyout/blackout risk during pulls"],
        "mitigation": ["Moderate transition rates", "AGSM on +G phases", "Limit −G duration"]
    },
    "triple_push_pull_immelmann": {
        "description": "Immelmann elements with push–pull entry repeated three times (conceptual variant).",
        "physiological_effects": "Mixed −G, +G, and roll elements challenge vestibular and cardiovascular systems; half-rolls interspersed with G changes.",
        "risk_factors": ["Spatial disorientation", "Rapid G swings", "Vision compromise"],
        "mitigation": ["Stable sight picture before roll", "AGSM during +G", "Limit −G exposure"]
    },
    "triple_push_pull_split_s": {
        "description": "Three consecutive Split S–style entries with push–pull cadence (conceptual variant).",
        "physiological_effects": "Repeated negative-to-positive transitions on descending segments elevate cumulative load and fatigue.",
        "risk_factors": ["Accumulated cardiovascular strain", "Greyout during sustained +G", "Redout if −G is extended"],
        "mitigation": ["Adequate entry altitude", "Careful pacing", "Training and hydration"]
    },
    "high_g_turn": {
        "description": "Sustained high-G level turn with brief on/off modulation around a 6–7 G plateau.",
        "physiological_effects": "Sustained +G reduces cerebral perfusion leading to greyout/blackout and potential G-LOC without countermeasures.",
        "risk_factors": ["High G-onset rate", "Sustained +G exposure", "Fatigue"],
        "mitigation": ["AGSM", "Anti-G suit/PPB", "Manage onset rate"]
    },
    "loop_standard": {
        "description": "Standard loop with 3–5 G pull-up and pull-out phases.",
        "physiological_effects": "Peak +G at entry/exit may induce greyout; low/near 0 G over the top allows reperfusion.",
        "risk_factors": ["High entry speed", "Aggressive pull", "Disorientation"],
        "mitigation": ["Energy management", "AGSM during pull", "Altitude margins"]
    },
    "immelmann_turn": {
        "description": "Half-loop followed by half-roll (direction reversal with altitude gain).",
        "physiological_effects": "+G during half-loop can approach tolerance; roll introduces vestibular stress.",
        "risk_factors": ["Rapid G-onset", "Spatial disorientation"],
        "mitigation": ["Gradual pull", "AGSM"]
    },
    "split_s": {
        "description": "Roll inverted then descending half-loop with high +G pull-out.",
        "physiological_effects": "Pull-out +G is the primary risk for greyout/blackout; altitude loss is substantial.",
        "risk_factors": ["High +G at pull-out", "Altitude margin"],
        "mitigation": ["Adequate entry altitude", "AGSM"]
    },
    "cuban_eight": {
        "description": "Two looping segments joined by half-rolls (lazy eight in vertical plane).",
        "physiological_effects": "Repeated +G peaks; roll segments at low G reduce perfusion strain briefly.",
        "risk_factors": ["Cumulative +G", "Disorientation"],
        "mitigation": ["Pacing", "AGSM"]
    },
    "vertical_eight": {
        "description": "Vertical figure eight with repeated +G exposures and brief −G transitions.",
        "physiological_effects": "Alternating +/−G can introduce push–pull effect reducing +G tolerance.",
        "risk_factors": ["Push–pull effect", "Repeated +G peaks"],
        "mitigation": ["Limit −G duration", "AGSM on +G phases"]
    }
}

#############################
# Local Survey DB utilities #
#############################

def _get_survey_db_path() -> Path:
    data_dir = Path.cwd() / "data"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fallback to project root if data dir cannot be created
        data_dir = Path.cwd()
    return data_dir / "pilot_survey.db"

def _get_db_connection() -> sqlite3.Connection:
    db_path = _get_survey_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pilot_survey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pilot_id TEXT NOT NULL,
            collected_by TEXT,
            collected_at TEXT DEFAULT (datetime('now')),
            payload_json TEXT NOT NULL
        )
        """
    )
    return conn

def _insert_survey_record(pilot_id: str, collected_by: Optional[str], payload_json: str) -> int:
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pilot_survey (pilot_id, collected_by, payload_json) VALUES (?, ?, ?)",
            (pilot_id, collected_by or "", payload_json),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()

def _load_all_records() -> List[Dict[str, object]]:
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, pilot_id, collected_by, collected_at, payload_json FROM pilot_survey ORDER BY id DESC")
        rows = cur.fetchall()
        records: List[Dict[str, object]] = []
        for rid, pid, by, at, payload in rows:
            try:
                payload_dict = json.loads(payload or "{}")
            except Exception:
                payload_dict = {}
            rec = {"id": rid, "pilot_id": pid, "collected_by": by, "collected_at": at}
            rec.update(payload_dict)
            records.append(rec)
        return records
    finally:
        conn.close()

def _delete_records_by_ids(ids: List[int]) -> int:
    if not ids:
        return 0
    conn = _get_db_connection()
    try:
        qmarks = ",".join(["?"] * len(ids))
        cur = conn.cursor()
        cur.execute(f"DELETE FROM pilot_survey WHERE id IN ({qmarks})", ids)
        conn.commit()
        return cur.rowcount or 0
    finally:
        conn.close()

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

def _classify_state(g: float, geff: float) -> str:
    state, _ = get_physiological_state(g, geff)
    if g < PHYSIOLOGICAL_THRESHOLDS["redout_g"]:
        return "redout"
    if geff >= PHYSIOLOGICAL_THRESHOLDS["gloc_geff"]:
        return "gloc"
    if geff >= PHYSIOLOGICAL_THRESHOLDS["blackout_geff"]:
        return "blackout"
    if geff >= PHYSIOLOGICAL_THRESHOLDS["greyout_geff"]:
        return "greyout"
    if state == "normal":
        return "normal"
    return "caution"

def _compute_state_durations(times: List[float], g_values: List[float], geff_values: List[float]) -> Dict[str, float]:
    if not times or not g_values or not geff_values or len(times) != len(g_values) or len(times) != len(geff_values):
        return {k: 0.0 for k in ["normal", "caution", "greyout", "blackout", "gloc", "redout"]}
    durations: Dict[str, float] = {"normal": 0.0, "caution": 0.0, "greyout": 0.0, "blackout": 0.0, "gloc": 0.0, "redout": 0.0}
    for i in range(len(times) - 1):
        dt = max(0.0, times[i+1] - times[i])
        state = _classify_state(float(g_values[i]), float(geff_values[i]))
        durations[state] += dt
    return durations

def _load_local_echarts_js() -> Optional[str]:
    candidates = [
        Path("node_modules") / "echarts" / "dist" / "echarts.min.js",
        Path.cwd() / "node_modules" / "echarts" / "dist" / "echarts.min.js",
    ]
    for p in candidates:
        try:
            if p.exists():
                return p.read_text(encoding="utf-8")
        except Exception:
            continue
    return None

def render_echarts_dashboard(times: List[float], g_values: List[float], geff_values: List[float],
                             flags_n2: List[int], profile_name: str,
                             layout_mode: str = "Grid", chart_choice: Optional[str] = None,
                             c_bank: Optional[List[float]] = None,
                             f_con: Optional[List[float]] = None,
                             f_vis: Optional[List[float]] = None,
                             f_bo: Optional[List[float]] = None,
                             bo_bank: Optional[List[float]] = None,
                             hlap: Optional[List[float]] = None):
    if not times or not g_values or not geff_values:
        st.info("Run the physiological simulation first to populate the ECharts dashboard.")
        return

    durations = _compute_state_durations(times, g_values, geff_values)

    # Histogram data
    try:
        bins = 20
        hist_counts, hist_edges = np.histogram(np.array(g_values, dtype=float), bins=bins)
        hist_labels = [f"{hist_edges[i]:.1f}–{hist_edges[i+1]:.1f}" for i in range(len(hist_edges)-1)]
        hist_values = hist_counts.tolist()
    except Exception:
        hist_labels, hist_values = [], []

    # Heatmap for flags (consciousness, vision, blackout proxies)
    heat_params = ["Consciousness", "Vision", "Blackout"]
    heat_matrix = []
    flag_len = len(times)
    cons = [(1 - int(flags_n2[i])) if i < len(flags_n2) else 1 for i in range(flag_len)]
    vision = cons
    blackout = [(1 if _classify_state(float(g_values[i]), float(geff_values[i])) in ("blackout", "gloc") else 0) for i in range(flag_len)]
    heat_matrix.append(cons)
    heat_matrix.append(vision)
    heat_matrix.append(blackout)

    # Radar metrics
    time_above_greyout = sum(max(0.0, times[i+1] - times[i]) for i in range(len(times)-1) if geff_values[i] >= PHYSIOLOGICAL_THRESHOLDS["greyout_geff"]) if len(times) > 1 else 0.0
    time_below_redout = sum(max(0.0, times[i+1] - times[i]) for i in range(len(times)-1) if g_values[i] < PHYSIOLOGICAL_THRESHOLDS["redout_g"]) if len(times) > 1 else 0.0
    weighted_mean_g = float(np.average(g_values, weights=np.diff(times + [times[-1] + 1e-9])) if len(times) > 1 else np.mean(g_values))

    radar_schema = [
        {"name": "Max G", "max": max(10.0, float(max(g_values)) + 1.0)},
        {"name": "Max G_eff", "max": max(10.0, float(max(geff_values)) + 1.0)},
        {"name": "> Greyout (s)", "max": max(1.0, float(time_above_greyout) * 1.2)},
        {"name": "< Redout (s)", "max": max(1.0, float(time_below_redout) * 1.2)},
        {"name": "Mean G", "max": max(10.0, abs(float(weighted_mean_g)) * 2.0 + 1.0)},
    ]
    radar_values = [
        float(max(g_values)),
        float(max(geff_values)),
        float(time_above_greyout),
        float(time_below_redout),
        float(abs(weighted_mean_g)),
    ]

    # Scatter coloring by state
    scatter_points = [
        {
            "g": float(g_values[i]),
            "geff": float(geff_values[i]),
            "state": _classify_state(float(g_values[i]), float(geff_values[i]))
        }
        for i in range(len(times))
    ]

    payload = {
        "times": times,
        "g": g_values,
        "geff": geff_values,
        "thresholds": {
            "greyout": PHYSIOLOGICAL_THRESHOLDS["greyout_geff"],
            "blackout": PHYSIOLOGICAL_THRESHOLDS["blackout_geff"],
            "gloc": PHYSIOLOGICAL_THRESHOLDS["gloc_geff"],
            "redout": PHYSIOLOGICAL_THRESHOLDS["redout_g"]
        },
        "durations": durations,
        "hist": {"labels": hist_labels, "values": hist_values},
        "heat": {"params": heat_params, "matrix": heat_matrix},
        "radar": {"schema": radar_schema, "values": radar_values},
        "scatter": scatter_points,
        "stateColors": STATE_COLORS,
        "banks": {
            "c_bank": c_bank or [],
            "bo_bank": bo_bank or []
        },
        "flows": {
            "f_con": f_con or [],
            "f_vis": f_vis or [],
            "f_bo": f_bo or []
        },
        "hlap": hlap or [],
        "profile": profile_name.replace("_", " ").title(),
        "ui": {"layoutMode": layout_mode, "chartChoice": chart_choice or ""}
    }

    echarts_js = _load_local_echarts_js()
    data_json = json.dumps(payload)

    # Containers based on layout
    choice_to_id = {
        "Lines": "c1",
        "Heatmap": "c2",
        "Histogram": "c3",
        "Radar": "c4",
        "Scatter": "c5",
        "Durations": "c6",
        "Flows": "c7",
        "Banks": "c8",
        "HLAP": "c9",
        "3D (ECharts)": "c10",
    }
    selected_id = choice_to_id.get(chart_choice or "Lines", "c1")
    if (layout_mode or "").lower().startswith("single"):
        containers_html = f"""
  <div class=\"grid single\"> 
    <div class=\"tile\"><div class=\"title\">{chart_choice or 'Lines'}</div><div id=\"{selected_id}\" class=\"chart\"></div></div>
  </div>
        """
        height_value = 460
    else:
        containers_html = """
  <div class=\"grid\"> 
    <div class=\"tile\"><div class=\"title\">Lines</div><div id=\"c1\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Heatmap</div><div id=\"c2\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Histogram</div><div id=\"c3\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Radar</div><div id=\"c4\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Scatter</div><div id=\"c5\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Durations</div><div id=\"c6\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Flows</div><div id=\"c7\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">Banks</div><div id=\"c8\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">HLAP</div><div id=\"c9\" class=\"chart\"></div></div>
    <div class=\"tile\"><div class=\"title\">3D (ECharts)</div><div id=\"c10\" class=\"chart\"></div></div>
  </div>
        """
        height_value = 1210

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <style>
    body {{ margin: 0; font-family: -apple-system, Segoe UI, Roboto, Arial; background: #0b1220; color: #e5e7eb; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); grid-auto-rows: 400px; gap: 16px; padding: 12px; }}
    .grid.single {{ grid-template-columns: 1fr; grid-auto-rows: 420px; }}
    .tile {{ background: #111827; border: 1px solid #1f2937; border-radius: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); position: relative; }}
    .title {{ position: absolute; top: 8px; left: 12px; font-weight: 600; color: #cbd5e1; z-index: 2; font-size: 12px; }}
    .chart {{ position: absolute; inset: 0; }}
  </style>
  {('<script>' + echarts_js + '</script>') if echarts_js else ''}
  <script src="https://cdn.jsdelivr.net/npm/echarts-gl@2/dist/echarts-gl.min.js"></script>
  <script>
    window.__ECHARTS_DATA__ = {data_json};
    function initCharts() {{
      var data = window.__ECHARTS_DATA__;
      var stateColors = data.stateColors;
      var colors = {{ text: '#e5e7eb', axis: '#cbd5e1', grid: '#1f2937', tile: '#111827' }};
      function el(id) {{ return document.getElementById(id); }}
      function mkChart(id) {{ var node = el(id); return node ? echarts.init(node) : null; }}
      var baseTextStyle = {{ color: colors.text, fontSize: 10 }};
      var axisCommon = {{
        axisLabel: {{ color: colors.axis, fontSize: 10 }},
        axisLine: {{ lineStyle: {{ color: colors.grid }} }},
        splitLine: {{ show: true, lineStyle: {{ color: colors.grid }} }}
      }};
      var legendTextStyle = {{ textStyle: {{ color: colors.axis, fontSize: 10 }} }};
      var titleTextStyle = {{ textStyle: {{ color: colors.text, fontSize: 12 }} }};
      var tooltipCommon = {{ backgroundColor: colors.tile, borderColor: colors.grid, textStyle: {{ color: colors.text }} }};
      var charts = [];

      var line = mkChart('c1');
      if (line) {{
        line.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'G and G_eff vs Time — ' + data.profile }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'axis' }}, tooltipCommon),
          legend: Object.assign({{ data: ['G', 'G_eff'] }}, legendTextStyle),
          xAxis: Object.assign({{ type: 'category', data: data.times }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'G' }}, axisCommon),
          series: [
            {{ name: 'G', type: 'line', data: data.g, smooth: true, lineStyle: {{ width: 2, color: '#60a5fa' }} }},
            {{ name: 'G_eff', type: 'line', data: data.geff, smooth: true, lineStyle: {{ width: 2, color: '#34d399' }} }}
          ],
          grid: {{ left: 55, right: 24, top: 36, bottom: 40, containLabel: true }}
        }});
        charts.push(line);
      }}

      var heat = mkChart('c2');
      if (heat) {{
        var heatData = [];
        for (var r = 0; r < data.heat.matrix.length; r++) {{
          for (var c = 0; c < data.times.length; c++) {{
            heatData.push([c, r, data.heat.matrix[r][c]]);
          }}
        }}
        heat.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'Physiological Flags Heatmap' }}, titleTextStyle),
          tooltip: Object.assign({{ position: 'top' }}, tooltipCommon),
          grid: {{ left: 60, right: 24, top: 36, bottom: 44, containLabel: true }},
          xAxis: {{ type: 'category', data: data.times, splitArea: {{ show: true }}, axisLabel: {{ color: colors.axis, fontSize: 10 }} }},
          yAxis: {{ type: 'category', data: data.heat.params, splitArea: {{ show: true }}, axisLabel: {{ color: colors.axis, fontSize: 10 }} }},
          visualMap: {{ min: 0, max: 1, calculable: false, orient: 'horizontal', left: 'center', bottom: 10,
                        textStyle: {{ color: colors.axis, fontSize: 10 }} }},
          series: [{{ name: 'Flag', type: 'heatmap', data: heatData }}]
        }});
        charts.push(heat);
      }}

      var hist = mkChart('c3');
      if (hist) {{
        hist.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'G Distribution' }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'axis' }}, tooltipCommon),
          xAxis: Object.assign({{ type: 'category', data: data.hist.labels, axisLabel: {{ rotate: 45 }} }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'Count' }}, axisCommon),
          series: [{{ type: 'bar', data: data.hist.values, itemStyle: {{ color: '#60a5fa' }} }}],
          grid: {{ left: 55, right: 24, top: 36, bottom: 60, containLabel: true }}
        }});
        charts.push(hist);
      }}

      var radar = mkChart('c4');
      if (radar) {{
        radar.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'Summary Metrics (Radar)' }}, titleTextStyle),
          tooltip: tooltipCommon,
          legend: Object.assign({{ data: [data.profile] }}, legendTextStyle),
          radar: {{ indicator: data.radar.schema, name: {{ textStyle: {{ color: colors.axis, fontSize: 10 }} }} }},
          series: [{{ type: 'radar', data: [{{ value: data.radar.values, name: data.profile }}],
                     areaStyle: {{ opacity: 0.15 }}, lineStyle: {{ color: '#34d399' }}, itemStyle: {{ color: '#34d399' }} }}]
        }});
        charts.push(radar);
      }}

      var scatter = mkChart('c5');
      if (scatter) {{
        scatter.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'G vs G_eff (State-colored)' }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'item' }}, tooltipCommon),
          legend: Object.assign({{ data: ['normal','caution','greyout','blackout','gloc','redout'] }}, legendTextStyle),
          xAxis: Object.assign({{ type: 'value', name: 'G' }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'G_eff' }}, axisCommon),
          series: ['normal','caution','greyout','blackout','gloc','redout'].map(function(cat) {{
            var pts = data.scatter.filter(p => p.state === cat).map(p => [p.g, p.geff]);
            return {{ name: cat, type: 'scatter', data: pts, symbolSize: 5, itemStyle: {{ color: stateColors[cat] || '#94a3b8' }} }};
          }})
        }});
        charts.push(scatter);
      }}

      var dur = mkChart('c6');
      // Flows line chart
      var flow = mkChart('c7');
      if (flow) {{
        flow.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'Flows over Time (F, F_vis, F_bo)' }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'axis' }}, tooltipCommon),
          legend: Object.assign({{ data: ['F_con','F_vis','F_bo'] }}, legendTextStyle),
          xAxis: Object.assign({{ type: 'category', data: data.times }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'dl/min' }}, axisCommon),
          series: [
            {{ name: 'F_con', type: 'line', data: data.flows.f_con, smooth: true }},
            {{ name: 'F_vis', type: 'line', data: data.flows.f_vis, smooth: true }},
            {{ name: 'F_bo', type: 'line', data: data.flows.f_bo, smooth: true }}
          ],
          grid: {{ left: 55, right: 24, top: 36, bottom: 40, containLabel: true }}
        }});
        charts.push(flow);
      }}

      // Banks line chart
      var bank = mkChart('c8');
      if (bank) {{
        bank.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'Reserve Banks over Time' }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'axis' }}, tooltipCommon),
          legend: Object.assign({{ data: ['Consciousness bank','Blackout bank'] }}, legendTextStyle),
          xAxis: Object.assign({{ type: 'category', data: data.times }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'seconds of normal flow' }}, axisCommon),
          series: [
            {{ name: 'Consciousness bank', type: 'line', data: data.banks.c_bank, smooth: true }},
            {{ name: 'Blackout bank', type: 'line', data: data.banks.bo_bank, smooth: true }}
          ],
          grid: {{ left: 55, right: 24, top: 36, bottom: 40, containLabel: true }}
        }});
        charts.push(bank);
      }}

      // HLAP line chart
      var hlapC = mkChart('c9');
      if (hlapC) {{
        hlapC.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'Heart-Level MAP (HLAP) over Time' }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'axis' }}, tooltipCommon),
          xAxis: Object.assign({{ type: 'category', data: data.times }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'mmHg' }}, axisCommon),
          series: [ {{ name: 'HLAP', type: 'line', data: data.hlap, smooth: true }} ],
          grid: {{ left: 55, right: 24, top: 36, bottom: 40, containLabel: true }}
        }});
        charts.push(hlapC);
      }}

      // 3D trajectory (ECharts GL)
      var chart3d = mkChart('c10');
      if (chart3d && echarts && echarts.graphic) {{
        var seriesData = data.times.map(function(t, i){{ return [t, data.g[i] || 0, data.geff[i] || 0]; }});
        chart3d.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: '3D Trajectory (time, G, G_eff)' }}, titleTextStyle),
          tooltip: tooltipCommon,
          xAxis3D: {{ type: 'value', name: 'Time (s)' }},
          yAxis3D: {{ type: 'value', name: 'G' }},
          zAxis3D: {{ type: 'value', name: 'G_eff' }},
          grid3D: {{ viewControl: {{ projection: 'perspective' }} }},
          series: [{{ type: 'line3D', data: seriesData, lineStyle: {{ width: 3, color: '#34d399' }} }}]
        }});
        charts.push(chart3d);
      }}
      if (dur) {{
        var cats = ['normal','caution','greyout','blackout','gloc','redout'];
        var secs = cats.map(c => +(data.durations[c] || 0).toFixed(2));
        dur.setOption({{
          backgroundColor: 'transparent',
          textStyle: baseTextStyle,
          title: Object.assign({{ text: 'Time in State (s)' }}, titleTextStyle),
          tooltip: Object.assign({{ trigger: 'axis' }}, tooltipCommon),
          xAxis: Object.assign({{ type: 'category', data: cats }}, axisCommon),
          yAxis: Object.assign({{ type: 'value', name: 'Seconds' }}, axisCommon),
          series: [{{ type: 'bar', data: secs, itemStyle: {{ color: function(params) {{ return stateColors[cats[params.dataIndex]]; }} }} }}],
          grid: {{ left: 55, right: 24, top: 36, bottom: 40, containLabel: true }}
        }});
        charts.push(dur);
      }}

      window.addEventListener('resize', function() {{ charts.forEach(c => c && c.resize()); }});
    }}
  </script>
  {'' if echarts_js else '<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js" onload="window.initCharts()"></script>'}
</head>
<body onload="{ 'initCharts()' if echarts_js else '' }">
  {containers_html}
</body>
</html>
"""

    components.html(html, height=height_value, scrolling=True)

# Main application
APA_CITATION = (
    "Copeland, K., & Whinnery, J. E. (2023). Cerebral blood flow based computer modeling of Gz-induced effects. "
    "<em>Aerospace Medicine and Human Performance, 94</em>(1), 39–45. "
    "<a href=\"https://doi.org/10.3357/AMHP.6179.2023\" target=\"_blank\">https://doi.org/10.3357/AMHP.6179.2023</a>"
)
DEV_CREDIT = (
    "Developer for Colombian Aerospace Force: Dr. Diego Malpica — "
    "<a href=\"https://orcid.org/0000-0002-2257-4940\" target=\"_blank\">ORCID 0000-0002-2257-4940</a>"
)

if ICON_PATH and ICON_PATH.exists():
    try:
        with open(ICON_PATH, "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode("utf-8")
        st.markdown(
            f"""
            <div class="app-header">
                <img src="data:image/png;base64,{_b64}" alt="App logo" class="app-logo" />
                <h1>G-Effects Model</h1>
            </div>
            <div class="app-subtitle">{APA_CITATION}<br/>{DEV_CREDIT}</div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        st.title("G-Effects Model")
else:
    st.title("G-Effects Model")
    st.markdown(f"<div class=\"app-subtitle\">{APA_CITATION}<br/>{DEV_CREDIT}</div>", unsafe_allow_html=True)
    st.caption("Tip: place 'icon.png' in the project root or in 'assets/', 'images/', or 'docs/' to display the logo.")


# Sidebar configuration
# Sidebar logo at the top (centered)
if ICON_PATH and ICON_PATH.exists():
    try:
        with open(ICON_PATH, "rb") as _sf:
            _sb64 = base64.b64encode(_sf.read()).decode("utf-8")
        st.sidebar.markdown(
            f"<div style=\"text-align:center;margin:0.25rem 0 0.5rem;\"><img src=\"data:image/png;base64,{_sb64}\" alt=\"Logo\" style=\"width:72px;height:72px;border-radius:16px;box-shadow:0 6px 18px rgba(0,0,0,0.25);\"/></div>",
            unsafe_allow_html=True,
        )
    except Exception:
        pass

st.sidebar.header("Configuration ⚙️")

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
st.sidebar.subheader("Pilot Profile 👨‍✈️")
pilot_type = st.sidebar.selectbox(
    "Pilot Training Level",
    ["Untrained", "Basic Training", "Advanced Training", "Fighter Pilot"],
    index=1
)

# Visualization options
st.sidebar.subheader("Visualization Options 📊")
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
        # Additional series
        "c_bank_values": result.c_bank_values or [],
        "f_con_values": result.f_con_values or [],
        "f_vis_values": result.f_vis_values or [],
        "f_bo_values": result.f_bo_values or [],
        "bo_bank_values": result.bo_bank_values or [],
        "hlap_values": result.hlap_values or [],
    }
    return data, str(tmp_dir)

# Main content area
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Profile Overview 📈", 
    "Physiological Analysis 🧬", 
    "Maneuver Details 🎯",
    "Comparative Analysis 📊",
    "ECharts Dashboard ✨",
    "Pilot Survey 🧑‍✈️📋",
    "Educational Resources 📚"
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
    st.subheader("Advanced Physiological Analysis")
    
    st.markdown("#### Pilot configuration")
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

    # Prefill survey defaults from current Pilot configuration
    try:
        survey_prefill: Dict[str, object] = {}
        if who_profile in (1, 2, 3, 4, 5, 6):
            d = PROFILE_DEFS[int(who_profile)]
            survey_prefill = {
                "sex": "Male" if d.get("male", 1) == 1 else "Female",
                "height_cm": float(d.get("howtall", 179.0)),
                "systolic_bp": int(d.get("BSP", 120)),
                "diastolic_bp": int(d.get("BDP", 80)),
            }
        else:
            if 'male' in locals() and male is not None:
                survey_prefill["sex"] = str(male)
            if 'height_cm' in locals() and height_cm is not None:
                survey_prefill["height_cm"] = float(height_cm)
            if 'bsp' in locals() and bsp is not None:
                survey_prefill["systolic_bp"] = int(bsp)
            if 'bdp' in locals() and bdp is not None:
                survey_prefill["diastolic_bp"] = int(bdp)
        st.session_state["survey_prefill"] = survey_prefill
    except Exception:
        pass

    # Run mode selection
    st.markdown("#### Run mode")
    run_mode = st.radio("Select simulation mode", ["Custom EGP (aerobatic profile)", "Internal centrifuge experiment"], index=0, horizontal=True)
    if run_mode == "Internal centrifuge experiment":
        colR1, colR2, colR3, colR4, colR5 = st.columns(5)
        with colR1:
            r_g0 = st.number_input("G0", 0.0, 1.4, 1.0, 0.1, key="i_g0")
        with colR2:
            r_gmax = st.number_input("Gmax", 2.0, 15.0, 9.0, 0.1, key="i_gmax")
        with colR3:
            r_hold = st.number_input("Hold @Gmax (s)", 0.0, 20.0, 1.0, 0.5, key="i_hold")
        with colR4:
            r_up = st.number_input("Ramp up (G/s)", 0.01, 10.0, 0.5, 0.01, key="i_rup")
        with colR5:
            r_down = st.number_input("Ramp down (G/s)", 0.01, 10.0, 0.5, 0.01, key="i_rdown")

    if st.button("Run CGEM Physiological Simulation", type="primary", key="run_sim"):
        with st.spinner("Running physiological simulation..."):
            try:
                if run_mode == "Internal centrifuge experiment":
                    @st.cache_data(show_spinner=False)
                    def cached_run_centrifuge(g0, gmax, hold, rup, rdown, pilot_cfg_key: str, pilot_cfg: PilotConfig):
                        res, tmp_dir = run_cgem_centrifuge(g0=g0, gmax=gmax, gmaxtime=hold, rampup=rup, rampdown=rdown, config=pilot_cfg)
                        d = {
                            "times_s": res.times_s or [],
                            "g_values": res.g_values or [],
                            "geff_values": res.geff_values or [],
                            "flags_n2": res.flags_n2 or [],
                            "flags_ne2": res.flags_ne2 or [],
                            "flags_non2": res.flags_non2 or [],
                            "time_to_greyout_s": res.time_to_greyout_s,
                            "time_to_blackout_s": res.time_to_blackout_s,
                            "time_to_gloc_s": res.time_to_gloc_s,
                            "c_bank_values": res.c_bank_values or [],
                            "f_con_values": res.f_con_values or [],
                            "f_vis_values": res.f_vis_values or [],
                            "f_bo_values": res.f_bo_values or [],
                            "bo_bank_values": res.bo_bank_values or [],
                            "hlap_values": res.hlap_values or [],
                        }
                        return d, str(tmp_dir)

                    data, tmp_dir = cached_run_centrifuge(r_g0, r_gmax, r_hold, r_up, r_down, pilot_cfg_key=pilot_cfg.to_cache_key(), pilot_cfg=pilot_cfg)
                else:
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
                st.markdown("### Critical Physiological Events")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if data["time_to_greyout_s"]:
                        st.error(f"Greyout at {data['time_to_greyout_s']:.2f}s")
                    else:
                        st.success("No Greyout")
                
                with col2:
                    if data["time_to_blackout_s"]:
                        st.error(f"Blackout at {data['time_to_blackout_s']:.2f}s")
                    else:
                        st.success("No Blackout")
                
                with col3:
                    if data["time_to_gloc_s"]:
                        st.error(f"G-LOC at {data['time_to_gloc_s']:.2f}s")
                    else:
                        st.success("No G-LOC")
                
                # Display selected visualizations
                if show_2d:
                    st.markdown("### 2D Physiological Analysis")
                    fig_2d = create_2d_physiological_plot(
                        data["times_s"], data["g_values"], 
                        data["geff_values"], selected_key
                    )
                    st.plotly_chart(fig_2d, use_container_width=True)
                
                if show_3d:
                    st.markdown("### 3D Physiological Trajectory")
                    fig_3d = create_3d_trajectory_plot(
                        data["times_s"], data["g_values"],
                        data["geff_values"], data["flags_n2"],
                        selected_key
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)
                
                if show_animated:
                    st.markdown("### Animated Physiological Response")
                    fig_anim = create_animated_plot(
                        data["times_s"], data["g_values"],
                        data["geff_values"], selected_key
                    )
                    st.plotly_chart(fig_anim, use_container_width=True)
                
                if show_heatmap:
                    st.markdown("### Physiological Parameters Heatmap")
                    fig_heat = create_physiological_heatmap(result, selected_key)
                    st.plotly_chart(fig_heat, use_container_width=True)
                
                if show_cardiovascular:
                    st.markdown("### Cardiovascular Response Estimation")
                    fig_cardio = create_cardiovascular_response_plot(
                        data["times_s"], data["g_values"], data["geff_values"]
                    )
                    st.plotly_chart(fig_cardio, use_container_width=True)

                # Save last run for other tabs
                st.session_state["last_run_data"] = data
                st.session_state["last_run_mode"] = run_mode
                
            except Exception as exc:
                st.error(f"Simulation failed: {exc}")

with tab3:
    st.subheader(f"Detailed Analysis: {selected_key.replace('_', ' ').title()}")
    
    # Run simulation if not already done
    try:
        data = st.session_state.get("last_run_data")
        if not data:
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
    st.subheader("Comparative Analysis Across All Maneuvers")
    
    if st.button("Run Batch Analysis", type="secondary"):
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
                    "Greyout Time": (data["time_to_greyout_s"] if data["time_to_greyout_s"] is not None else np.nan),
                    "Blackout Time": (data["time_to_blackout_s"] if data["time_to_blackout_s"] is not None else np.nan),
                    "G-LOC Time": (data["time_to_gloc_s"] if data["time_to_gloc_s"] is not None else np.nan)
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
    st.subheader("ECharts Scientific Dashboard")
    st.caption("Powered by Apache ECharts; prefers local `node_modules/echarts` when available.")
    # Layout controls
    colL, colR = st.columns([1, 2])
    with colL:
        layout_mode = st.radio("Layout", ["Grid (all charts)", "Single (one chart)"], index=0)
    with colR:
        chart_choice = st.selectbox("Chart", ["Lines", "Heatmap", "Histogram", "Radar", "Scatter", "Durations", "Flows", "Banks", "HLAP", "3D (ECharts)"], index=0)
    try:
        data = st.session_state.get("last_run_data")
        if not data:
            data, _ = cached_run(selected_key, pilot_cfg_key=pilot_cfg.to_cache_key(), pilot_cfg=pilot_cfg)
        render_echarts_dashboard(
            data.get("times_s", []),
            data.get("g_values", []),
            data.get("geff_values", []),
            data.get("flags_n2", []),
            selected_key,
            layout_mode="Single" if layout_mode.startswith("Single") else "Grid",
            chart_choice=chart_choice,
            c_bank=data.get("c_bank_values", []),
            f_con=data.get("f_con_values", []),
            f_vis=data.get("f_vis_values", []),
            f_bo=data.get("f_bo_values", []),
            bo_bank=data.get("bo_bank_values", []),
            hlap=data.get("hlap_values", []),
        )
    except Exception as exc:
        st.error(f"Unable to render ECharts dashboard: {exc}")

with tab6:
    st.subheader("Pilot Survey")
    st.caption("Local-only data collection. Exports to CSV/Excel. Objective data can be entered by the flight surgeon.")

    survey_tab, db_tab = st.tabs(["New Entry 📝", "Database & Export 💾"])

    with survey_tab:
        pref = st.session_state.get("survey_prefill", {})
        with st.form("pilot_survey_form"):
            st.markdown("### Administrative")
            col_admin1, col_admin2, col_admin3 = st.columns(3)
            with col_admin1:
                pilot_id = st.text_input("Pilot ID (required)", help="Unique identifier for this pilot")
            with col_admin2:
                collected_by = st.text_input("Collected by (Flight Surgeon)")
            with col_admin3:
                collection_time = st.text_input("Collection time (auto)", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disabled=True)

            st.markdown("### Pilot Demographics & Experience")
            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            with col_d1:
                age = st.number_input("Age (years) (required)", min_value=16, max_value=80, value=30)
                sex_options = ["Male", "Female", "Other"]
                sex_default = str(pref.get("sex", "Male"))
                sex_index = sex_options.index(sex_default) if sex_default in sex_options else 0
                sex = st.selectbox("Sex (required)", sex_options, index=sex_index)
                height_cm = st.number_input("Height (cm) (required)", min_value=140.0, max_value=210.0, value=float(pref.get("height_cm", 179.0)), step=0.1)
            with col_d2:
                weight_kg = st.number_input("Weight (kg) (required)", min_value=40.0, max_value=150.0, value=80.0, step=0.1)
                unit = st.text_input("Military unit")
                aircraft_type = st.text_input("Current aircraft type (required)")
            with col_d3:
                total_hours = st.number_input("Total flight hours (all)", min_value=0.0, value=1000.0, step=1.0)
                current_ac_hours = st.number_input("Hours in current aircraft", min_value=0.0, value=250.0, step=1.0)
                hours_2w = st.number_input("Hours flown (last 2 weeks)", min_value=0.0, value=10.0, step=0.5)
            with col_d4:
                hours_1m = st.number_input("Hours flown (last month)", min_value=0.0, value=20.0, step=0.5)
                years_mil = st.number_input("Years military flight exp", min_value=0.0, value=5.0, step=0.5)
                types_flown = st.number_input("# aircraft types flown", min_value=0, value=3, step=1)

            col_exp = st.columns(3)
            with col_exp[0]:
                days_since_g = st.number_input("Days since last G-exposure flight", min_value=0, value=7)
            with col_exp[1]:
                avg_g_exp = st.number_input("Avg G-exposures/month (current role)", min_value=0, value=8)
            with col_exp[2]:
                typical_max_g = st.number_input("Typical max G (current ops)", min_value=-5.0, max_value=15.0, value=6.0, step=0.1)

            st.markdown("### G-Force Experience History")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                greyout_year = st.number_input("Greyout episodes (past year)", min_value=0, value=0)
                blackout_year = st.number_input("Blackout episodes (past year)", min_value=0, value=0)
                gloc_year = st.number_input("G-LOC episodes (past year)", min_value=0, value=0)
            with col_g2:
                last_greyout_days = st.number_input("Most recent greyout (days)", min_value=0, value=0)
                last_blackout_days = st.number_input("Most recent blackout (days)", min_value=0, value=0)
                last_gloc_days = st.number_input("Most recent G-LOC (days)", min_value=0, value=0)
            with col_g3:
                highest_g = st.number_input("Highest G in career", min_value=-5.0, max_value=20.0, value=9.0, step=0.1)

            st.markdown("### Sleep & Fatigue Assessment")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                avg_sleep = st.number_input("Avg sleep hours/night (past week)", min_value=0.0, max_value=14.0, value=7.0, step=0.25)
                sleep_quality = st.slider("Sleep quality (1–10)", 1, 10, 7)
                short_nights = st.number_input("Nights with <6h sleep (week)", min_value=0, max_value=7, value=0)
            with col_s2:
                hours_before_flight = st.number_input("Hours of sleep before current flight", min_value=0.0, max_value=24.0, value=7.0, step=0.25)
                duty_no_rest = st.number_input("Duty days without adequate rest (month)", min_value=0, max_value=31, value=0)
                shift_changes = st.number_input("Shift changes per month", min_value=0, max_value=31, value=0)
            with col_s3:
                tz_changes = st.number_input("Time zone changes (past 2 weeks)", min_value=0, max_value=20, value=0)
                last_sleep_time = st.time_input("Time of last sleep before flight")

            st.markdown("### Physical Health & Fitness")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                resting_hr = st.number_input("Resting heart rate (bpm)", min_value=30, max_value=220, value=70)
                systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=70, max_value=260, value=int(pref.get("systolic_bp", 120)))
                diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=160, value=int(pref.get("diastolic_bp", 80)))
            with col_p2:
                exercise_freq = st.number_input("Exercise frequency (/week)", min_value=0, max_value=14, value=3)
                exercise_type = st.selectbox("Primary exercise type", ["Aerobic", "Strength", "Mixed", "None"])
                hours_exercise = st.number_input("Hours of exercise per week", min_value=0.0, max_value=50.0, value=3.0, step=0.5)
            with col_p3:
                body_fat_pct = st.number_input("Body fat %", min_value=0.0, max_value=60.0, value=18.0, step=0.1)
                cv_meds = st.selectbox("Cardiovascular meds?", ["No", "Yes"])
                bp_meds = st.selectbox("Blood pressure meds?", ["No", "Yes"])
            col_p4, col_p5 = st.columns(2)
            with col_p4:
                current_illness = st.selectbox("Current illness/infection?", ["No", "Yes"]) 
            with col_p5:
                days_since_illness = st.number_input("Days since last illness", min_value=0, value=0)

            st.markdown("### Physiological Status (Day of Survey)")
            col_ps1, col_ps2, col_ps3, col_ps4 = st.columns(4)
            with col_ps1:
                hours_since_meal = st.number_input("Hours since last meal", min_value=0.0, max_value=72.0, value=4.0, step=0.5)
                hours_since_caffeine = st.number_input("Hours since caffeine", min_value=0.0, max_value=72.0, value=6.0, step=0.5)
            with col_ps2:
                cups_caffeine = st.number_input("Cups caffeine (24h)", min_value=0, max_value=50, value=0)
                water_glasses = st.number_input("Glasses of water today", min_value=0, max_value=50, value=6)
            with col_ps3:
                alcohol_24 = st.number_input("Alcohol (units, 24h)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
                alcohol_week = st.number_input("Alcohol (units, week)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            with col_ps4:
                stress_level = st.slider("Current stress (1–10)", 1, 10, 5)
                energy_level = st.slider("Energy now (1–10)", 1, 10, 6)
            col_temp, col_med = st.columns(2)
            with col_temp:
                body_temp_c = st.number_input("Body temperature (°C)", min_value=34.0, max_value=42.0, value=36.8, step=0.1)
            with col_med:
                meds_24h = st.text_area("Any medication taken in past 24h (list)")

            st.markdown("### Environmental & Operational Factors")
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                base_altitude = st.number_input("Base operations altitude (m)", min_value=0, max_value=6000, value=0)
                cockpit_temp = st.selectbox("Avg cockpit temperature", ["Hot", "Comfortable", "Cold"])
            with col_e2:
                noise_hours = st.number_input("Noise exposure (hrs/week)", min_value=0.0, max_value=168.0, value=5.0, step=0.5)
                vibration_hours = st.number_input("Vibration exposure (hrs/week)", min_value=0.0, max_value=168.0, value=3.0, step=0.5)
            with col_e3:
                mission_combat = st.number_input("Mission: combat %", min_value=0, max_value=100, value=0)
                mission_training = st.number_input("Mission: training %", min_value=0, max_value=100, value=100)
                mission_transport = st.number_input("Mission: transport %", min_value=0, max_value=100, value=0)
            col_e4, col_e5, col_e6 = st.columns(3)
            with col_e4:
                gsuit_available = st.selectbox("G-suit availability", ["No", "Yes"])
            with col_e5:
                gsuit_usage = st.selectbox("G-suit usage frequency", ["Never", "Rarely", "Sometimes", "Often", "Always"])
            with col_e6:
                anti_g_training_weeks = st.number_input("Anti-G training recency (weeks)", min_value=0, max_value=520, value=12)
            col_e7, col_e8 = st.columns(2)
            with col_e7:
                breathing_training = st.selectbox("Breathing technique training", ["None", "Basic", "Advanced"])    
            with col_e8:
                agsm_proficiency = st.slider("AGSM proficiency (1–10)", 1, 10, 7)

            st.markdown("### Lifestyle & Behavioral Factors")
            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                smoking_status = st.selectbox("Smoking status", ["Never", "Former", "Current"]) 
                cigs_per_day = st.number_input("Cigarettes per day (if current)", min_value=0, max_value=80, value=0)
                diet_pattern = st.selectbox("Dietary pattern", ["Regular meals", "Irregular", "Skip meals"]) 
            with col_l2:
                hydration_habits = st.selectbox("Hydration habits", ["Excellent", "Good", "Fair", "Poor"]) 
                supplements = st.text_input("Supplement usage (list)")
                relaxation = st.selectbox("Relaxation/meditation frequency", ["Never", "Occasionally", "Weekly", "Daily"]) 
            with col_l3:
                stress_sources = st.text_area("Mental stress sources (notes)")
                time_off_month = st.number_input("Time off from flying duties (days, month)", min_value=0, max_value=31, value=0)

            st.markdown("### Performance & Symptoms")
            col_sym1, col_sym2, col_sym3 = st.columns(3)
            with col_sym1:
                self_gtol = st.selectbox("Self-rated G-tolerance vs peers", ["Much lower", "Lower", "Average", "Higher", "Much higher"]) 
                warn_signs = st.text_input("Typical warning signs before greyout")
            with col_sym2:
                recovery_time_s = st.number_input("Recovery time after high-G (s)", min_value=0.0, max_value=600.0, value=30.0, step=1.0)
                post_fatigue = st.selectbox("Post-flight fatigue frequency", ["Never", "Rarely", "Sometimes", "Often", "Always"]) 
            with col_sym3:
                headaches_freq = st.selectbox("Headaches after high-G", ["Never", "Rarely", "Sometimes", "Often", "Always"]) 
                vision_changes = st.selectbox("Vision changes after G-exposure", ["No", "Yes"]) 
            col_sym4, col_sym5 = st.columns(2)
            with col_sym4:
                concentration_diff = st.selectbox("Concentration difficulties after high-G", ["No", "Yes"]) 
            with col_sym5:
                phys_symptoms = st.multiselect("Physical symptoms during high-G", ["Nausea", "Muscle fatigue", "Breathing difficulty", "Dizziness", "Other"]) 

            st.markdown("### Training & Countermeasures")
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                breathing_proficiency = st.slider("Breathing control proficiency (1–10)", 1, 10, 7)
                gsuit_fit = st.selectbox("G-suit fit quality", ["Poor", "Adequate", "Excellent"]) 
            with col_t2:
                gsuit_use_frequency = st.selectbox("Frequency of G-suit use", ["Never", "Rarely", "Sometimes", "Often", "Always"]) 
                muscle_tensing = st.selectbox("Muscle tensing/gripping techniques used?", ["No", "Yes"]) 
            with col_t3:
                preflight_prep = st.selectbox("Pre-flight preparation routine consistency", ["Low", "Moderate", "High"]) 
                conditioning_focus = st.selectbox("Physical conditioning focus", ["General", "G-specific", "None"]) 

            st.markdown("### Psychological Factors")
            col_psi1, col_psi2, col_psi3 = st.columns(3)
            with col_psi1:
                confidence = st.slider("Confidence during high-G (1–10)", 1, 10, 7)
                anxiety = st.slider("Anxiety before high-G flights (1–10)", 1, 10, 3)
            with col_psi2:
                motivation = st.slider("Motivation for current duties (1–10)", 1, 10, 8)
                job_satisfaction = st.slider("Job satisfaction (1–10)", 1, 10, 8)
            with col_psi3:
                mental_workload = st.slider("Mental workload during typical flights (1–10)", 1, 10, 5)
                attention_focus = st.slider("Attention/focus during high-G (1–10)", 1, 10, 7)
            risk_tolerance = st.selectbox("Risk tolerance personality", ["Conservative", "Moderate", "Aggressive"]) 

            st.markdown("### Flight Surgeon Objective Data (optional)")
            col_obj1, col_obj2 = st.columns(2)
            with col_obj1:
                measured_hr = st.number_input("Measured HR (bpm)", min_value=30, max_value=220, value=70)
                measured_bp_sys = st.number_input("Measured SBP (mmHg)", min_value=70, max_value=260, value=120)
                measured_bp_dia = st.number_input("Measured DBP (mmHg)", min_value=40, max_value=160, value=80)
            with col_obj2:
                measured_temp_c = st.number_input("Measured temperature (°C)", min_value=34.0, max_value=42.0, value=36.8, step=0.1)
                objective_notes = st.text_area("Additional objective findings/notes")

            submitted = st.form_submit_button("Save Survey Entry", type="primary")
            if submitted:
                errors: List[str] = []
                if not pilot_id.strip():
                    errors.append("Pilot ID is required.")
                if not aircraft_type.strip():
                    errors.append("Current aircraft type is required.")
                if weight_kg < 40.0 or weight_kg > 150.0:
                    errors.append("Weight out of expected range (40–150 kg).")
                if height_cm < 140.0 or height_cm > 210.0:
                    errors.append("Height out of expected range (140–210 cm).")
                mission_sum = mission_combat + mission_training + mission_transport
                if mission_sum != 100:
                    st.warning(f"Mission percentages sum to {mission_sum}%. Consider adjusting to total 100%.")

                if errors:
                    st.error("Please correct the following:")
                    for e in errors:
                        st.write(f"- {e}")
                else:
                    payload = {
                        "admin": {
                            "pilot_id": pilot_id.strip(),
                            "collected_by": collected_by.strip(),
                            "collected_at_local": collection_time,
                        },
                        "demographics_experience": {
                            "age": age, "sex": sex, "height_cm": height_cm, "weight_kg": weight_kg,
                            "military_unit": unit, "current_aircraft_type": aircraft_type,
                            "total_flight_hours": total_hours, "current_aircraft_hours": current_ac_hours,
                            "hours_last_2_weeks": hours_2w, "hours_last_month": hours_1m,
                            "years_military_flight": years_mil, "num_aircraft_types_flown": types_flown,
                            "days_since_last_g": days_since_g, "avg_g_exposures_per_month": avg_g_exp,
                            "typical_max_g": typical_max_g
                        },
                        "g_experience_history": {
                            "greyout_episodes_year": greyout_year, "blackout_episodes_year": blackout_year,
                            "gloc_episodes_year": gloc_year, "last_greyout_days": last_greyout_days,
                            "last_blackout_days": last_blackout_days, "last_gloc_days": last_gloc_days,
                            "highest_g_career": highest_g
                        },
                        "sleep_fatigue": {
                            "avg_sleep_hours": avg_sleep, "sleep_quality_1_10": sleep_quality,
                            "nights_lt6h": short_nights, "last_sleep_time": str(last_sleep_time),
                            "hours_sleep_before_flight": hours_before_flight, "duty_days_no_rest_month": duty_no_rest,
                            "shift_changes_month": shift_changes, "tz_changes_2w": tz_changes
                        },
                        "physical_health": {
                            "resting_hr_bpm": resting_hr, "systolic_bp": systolic_bp, "diastolic_bp": diastolic_bp,
                            "exercise_freq_per_week": exercise_freq, "primary_exercise_type": exercise_type,
                            "hours_exercise_week": hours_exercise, "body_fat_pct": body_fat_pct,
                            "cv_meds": cv_meds, "bp_meds": bp_meds, "current_illness": current_illness,
                            "days_since_last_illness": days_since_illness
                        },
                        "phys_status_today": {
                            "hours_since_meal": hours_since_meal, "hours_since_caffeine": hours_since_caffeine,
                            "cups_caffeine_24h": cups_caffeine, "glasses_water_today": water_glasses,
                            "alcohol_units_24h": alcohol_24, "alcohol_units_week": alcohol_week,
                            "stress_level_1_10": stress_level, "energy_level_1_10": energy_level,
                            "body_temp_c": body_temp_c, "meds_24h": meds_24h
                        },
                        "environment_operational": {
                            "base_altitude_m": base_altitude, "avg_cockpit_temp": cockpit_temp,
                            "noise_hours_week": noise_hours, "vibration_hours_week": vibration_hours,
                            "mission_combat_pct": mission_combat, "mission_training_pct": mission_training,
                            "mission_transport_pct": mission_transport, "gsuit_available": gsuit_available,
                            "gsuit_usage_frequency": gsuit_usage, "anti_g_training_recency_weeks": anti_g_training_weeks,
                            "breathing_training_level": breathing_training, "agsm_proficiency_1_10": agsm_proficiency
                        },
                        "lifestyle_behavior": {
                            "smoking_status": smoking_status, "cigarettes_per_day": cigs_per_day,
                            "dietary_pattern": diet_pattern, "hydration_habits": hydration_habits,
                            "supplement_usage": supplements, "relaxation_frequency": relaxation,
                            "stress_sources": stress_sources, "time_off_flying_days_month": time_off_month
                        },
                        "performance_symptoms": {
                            "self_rated_g_tolerance": self_gtol, "warning_signs": warn_signs,
                            "recovery_time_s": recovery_time_s, "post_flight_fatigue": post_fatigue,
                            "headaches_frequency": headaches_freq, "vision_changes": vision_changes,
                            "concentration_difficulties": concentration_diff, "physical_symptoms": phys_symptoms
                        },
                        "training_countermeasures": {
                            "breathing_control_proficiency": breathing_proficiency, "gsuit_fit_quality": gsuit_fit,
                            "gsuit_use_frequency": gsuit_use_frequency, "muscle_tensing_used": muscle_tensing,
                            "preflight_prep_consistency": preflight_prep, "conditioning_focus": conditioning_focus
                        },
                        "psychological_factors": {
                            "confidence_1_10": confidence, "anxiety_1_10": anxiety,
                            "motivation_1_10": motivation, "job_satisfaction_1_10": job_satisfaction,
                            "mental_workload_1_10": mental_workload, "attention_focus_1_10": attention_focus,
                            "risk_tolerance": risk_tolerance
                        },
                        "objective_data": {
                            "measured_hr_bpm": measured_hr, "measured_sbp": measured_bp_sys,
                            "measured_dbp": measured_bp_dia, "measured_temp_c": measured_temp_c,
                            "objective_notes": objective_notes
                        }
                    }
                    try:
                        record_id = _insert_survey_record(pilot_id=pilot_id.strip(), collected_by=collected_by.strip(), payload_json=json.dumps(payload))
                        st.success(f"Saved survey entry (ID {record_id})")
                    except Exception as exc:
                        st.error(f"Failed to save: {exc}")

    with db_tab:
        st.markdown("### Database")
        records = _load_all_records()
        if records:
            df = pd.DataFrame(records)
            if "collected_at" in df.columns:
                df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce")

            with st.expander("Filters", expanded=True):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    pilot_filter = st.text_input("Filter by Pilot ID contains")
                    collected_by_filter = st.text_input("Filter by Collected By contains")
                with col_f2:
                    date_range = st.date_input("Date range (collected_at)", [])
                global_search = st.text_input("Search in any field")

            filtered_df = df.copy()
            if pilot_filter:
                mask = filtered_df["pilot_id"].astype(str).str.contains(pilot_filter, case=False, na=False)
                filtered_df = filtered_df[mask]
            if collected_by_filter:
                mask = filtered_df["collected_by"].astype(str).str.contains(collected_by_filter, case=False, na=False)
                filtered_df = filtered_df[mask]
            if date_range and len(date_range) == 2 and "collected_at" in filtered_df.columns:
                start_dt = pd.to_datetime(date_range[0])
                end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
                mask = (filtered_df["collected_at"] >= start_dt) & (filtered_df["collected_at"] < end_dt)
                filtered_df = filtered_df[mask]
            if global_search:
                gs = global_search
                mask = filtered_df.apply(lambda row: row.astype(str).str.contains(gs, case=False, na=False).any(), axis=1)
                filtered_df = filtered_df[mask]

            st.dataframe(filtered_df, use_container_width=True, height=360)

            st.markdown("#### Export")
            now_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name=f"pilot_survey_export_{now_tag}.csv",
                mime="text/csv",
            )
            xls_buffer = io.BytesIO()
            try:
                with pd.ExcelWriter(xls_buffer, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, sheet_name="Surveys", index=False)
                xls_buffer.seek(0)
                st.download_button(
                    "Download Excel",
                    data=xls_buffer.getvalue(),
                    file_name=f"pilot_survey_export_{now_tag}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except Exception as exc:
                st.warning(f"Excel export unavailable: {exc}")

            st.markdown("#### Delete records")
            selectable_ids = [int(r.get("id")) for r in records]
            ids_to_delete = st.multiselect("Select record IDs to delete", selectable_ids, [])
            if st.button("Delete selected", type="secondary"):
                try:
                    removed = _delete_records_by_ids(ids_to_delete)
                    st.success(f"Deleted {removed} record(s).")
                    st.experimental_rerun()
                except Exception as exc:
                    st.error(f"Failed to delete: {exc}")
        else:
            st.info("No survey records yet. Save your first entry in the New Entry tab.")

with tab7:
    st.subheader("Educational Resources")
    
    with st.expander("Understanding G-Forces and Physiology"):
        st.markdown("""
        ### What are G-Forces?
        G-forces represent the acceleration relative to Earth's gravity. 1G is normal Earth gravity.
        
        ### Physiological Effects:
        - **Positive G (+Gz)**: Blood pools in lower body, reducing brain perfusion
        - **Negative G (-Gz)**: Blood rushes to the head, increasing intracranial pressure
        - **Lateral G (Gy)**: Side-to-side forces, generally better tolerated
        
        ### Critical Thresholds:
        - **Greyout**: ≈4.1 G_eff - Peripheral vision loss
        - **Blackout**: ≈5.0 G_eff - Complete vision loss
        - **G-LOC**: ≈5.5 G_eff - Loss of consciousness
        - **Redout**: < −2 G - Blood vessel rupture risk
        """)
    
    with st.expander("G-Force Mitigation Techniques"):
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
    
    with st.expander("Understanding the Visualizations"):
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

    with st.expander("Comprehensive Review of Sustained Acceleration Physiology"):
        st.markdown("""
### Introduction

Sustained linear acceleration represents a pervasive environmental stressor in modern high-performance aviation and spaceflight. When the vector of force acts along the longitudinal (+Gz head-to-foot or ‑Gz foot-to-head) or orthogonal (+Gx, ±Gy) axes, a cascade of hydrostatic, cardiovascular, respiratory, neurological, ocular, and musculoskeletal adaptations is invoked to preserve cerebral perfusion and sensorimotor performance. This narrative review synthesises mechanistic insights, quantifies human tolerance, examines countermeasures, surveys operational epidemiology, and summarises contemporary modelling efforts.

### Core Physiology and Mechanisms

**Hydrostatic gradients.** Each +1 Gz produces ≈0.77 mmHg per cm vertical pressure drop (ΔP = ρ·g·h; blood density ≈ 1.06 g·cm⁻³), decreasing mean arterial pressure (MAP) at the Circle of Willis by ≈55 mmHg at +3 Gz for a 24 cm heart–brain distance (Pollock et al., 2021). Baroreflex-mediated tachycardia and vasoconstriction partly restore MAP but saturate beyond +4–5 Gz.

**Cerebral autoregulation.** Cerebral blood flow remains relatively constant while MAP at the Circle of Willis lies between ~60–160 mmHg. Acceleration-induced hydrostatic depression can drive MAP below the lower autoregulatory bound, precipitating retinal ischaemia (greyout), cortical hypoxia (blackout), and G-LOC (Lathers et al., 1984; Blaber et al., 2001).

**Venous compliance and splanchnic pooling.** Venous capacitance expansion sequesters ≥2 L of blood in the abdomen and legs under +Gz, reducing preload and cardiac output; sympathetic activation constricts capacitance vessels yet cannot fully offset pooling (Convertino et al., 1989).

**Respiratory mechanics.** Upward diaphragm displacement increases transpulmonary pressure and the work of breathing by ≈50% at +5 Gz. Positive pressure breathing elevates intrathoracic pressure, improving heart-level MAP but can impede venous return if excessive (Crandall & González-Alonso, 2010).

**Ocular and neurocognitive phenomena.** Retinal arterial pressure falling below intraocular pressure (~20 mmHg) triggers greyout/blackout. Sustained ‑Gz causes cephalad congestion and redout. Vestibular misinterpretation of otolith signals under sustained acceleration degrades spatial orientation (Previc & Ercoline, 2004).

**Musculoskeletal loading.** A 2 kg helmet equates to ≈20 kg effective mass at +9 Gz, elevating cervical spine injury risk (Previc & Ercoline, 2004).

### Human Tolerance and Dose–Response

Unprotected rapid-onset (≥2 G·s⁻¹) +Gz tolerance averages 5–6 Gz for ≤8 s; greyout ≈4.1 Gz, blackout ≈5 Gz, G-LOC ≈5.5 Gz (Burton & Smith, 1982). Slower onset allows additional baroreflex compensation (approximately +1 G). AGSM proficiency adds ≈1–2 G; pneumatic anti-G suits add ≈1 G; integrated positive-pressure breathing enables +9 Gz for ≈15–45 s (Banks et al., 2014). ‑Gz tolerance (≈−2 to −3 Gz for ≈10 s) is limited by cerebral hyperaemia (Vogt, 1976). Lateral ±Gy and fore–aft +Gx loads invoke lower cardiovascular strain but earlier vestibular/respiratory limitations mitigated by semi-reclined seating (Pattarini et al., 2020).

### Countermeasures

- **AGSM:** Isometric tensing with cyclic forced exhalation; adds ≈1–2 G tolerance, efficacy decays with fatigue and poor technique (Storm et al., 1990).
- **Anti-G suits:** CSU-13B/P inflates ~25 mmHg·G⁻¹ above +2 G (≈1 G protection). ATAGS and gradient liquid suits provide faster inflation and ~1.4 G protection but at comfort/logistical cost (Watenpaugh et al., 1996).
- **Positive pressure breathing (PPB/COMBAT EDGE):** Mask pressure up to ≈60 mmHg synchronised with suit inflation confers an extra ≈2–3 G tolerance; risk of reduced venous return necessitates training (Crandall & González-Alonso, 2010).
- **Ergonomics & hydration:** ≈30° seat recline shortens the heart–brain vertical distance by ≈8 cm, improving +Gz tolerance by ≈0.7 G; pre-flight isotonic hydration expands plasma volume (≈0.5 G gain) (Convertino et al., 1989).

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
st.sidebar.markdown("### 🔬 Model Information")
st.sidebar.markdown("""
- **Model**: CGEM v1.1.0.1
- **Default Subject**: Male: median physiology (who=2)
- **Purpose**: Educational/Research
""")

# Sidebar developer credit at the bottom
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align:center; font-size: 0.9rem;">
      Developer for Colombian Aerospace Force:<br/>
      <strong>Dr. Diego Malpica, MD</strong><br/>
      <a href="https://orcid.org/0000-0002-2257-4940" target="_blank">ORCID 0000-0002-2257-4940</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Global footer
st.markdown("---")
st.markdown(
    """
    <div class="app-subtitle" style="font-size: 0.95rem;">
      Developed by <strong>Dr Diego Malpica, MD (Aerospace Medicine)</strong>. Subdirectorate of Aerospace Sciences and the Direction of Aerospace Medicine. Colombian Aerospace Force. 
      <a href="https://orcid.org/0000-0002-2257-4940" target="_blank">ORCID 0000-0002-2257-4940</a>
    </div>
    """,
    unsafe_allow_html=True,
)