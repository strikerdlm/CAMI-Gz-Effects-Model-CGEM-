from __future__ import annotations

import math
from pathlib import Path
from typing import List, Dict

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import streamlit as st

from aerobatic_profiles import load_all_profiles, load_profile, PROFILES, Sample
from cgem_wrapper import run_cgem_for_profile

st.set_page_config(page_title="Aerobatic G-Profile CGEM Demo", layout="wide")

st.title("Aerobatic G-Profile – CGEM Prediction Demo")

# Sidebar – profile selection
profiles = load_all_profiles()
profile_keys = list(PROFILES.keys())
selected_key = st.sidebar.selectbox(
    "Select aerobatic manoeuvre",
    profile_keys,
    format_func=lambda k: k.replace("_", " ").title(),
)

filename, description = PROFILES[selected_key]
st.sidebar.markdown(f"**Description**: {description}")

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

@st.cache_data(show_spinner=False)
def cached_run(profile_id: str):
    result, tmp_dir = run_cgem_for_profile(profile_id)
    # Return only serializable bits to cache
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


tab1, tab2, tab3 = st.tabs(["Profile", "Prediction (CGEM)", "All Profiles (Batch)"])

with tab1:
    st.subheader("Normal Acceleration vs Time")
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(points_t, points_g, color="#1976d2", linewidth=2)
    ax.axhline(0, color="black", linestyle="--", alpha=0.5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Normal Acceleration (G)")
    ax.set_title(selected_key.replace("_", " ").title())
    ax.grid(True, alpha=0.3)
    st.pyplot(fig, clear_figure=True)

    # Show basic stats
    g_vals = [s.nz for s in samples]
    durations = [s.duration_ms for s in samples]
    total_s = sum(durations) / 1000.0
    weighted_mean = sum(g * d for g, d in zip(g_vals, durations)) / max(1, sum(durations))

    colA, colB, colC, colD = st.columns(4)
    colA.metric("Duration", f"{total_s:.1f} s")
    colB.metric("Max +G", f"{max(g_vals):.1f}")
    colC.metric("Max -G", f"{min(g_vals):.1f}")
    colD.metric("Weighted mean G", f"{weighted_mean:.2f}")

with tab2:
    st.subheader("CGEM Model Prediction (Healthy, midrange subject)")

    if st.button("Run CGEM Prediction", type="primary"):
        with st.spinner("Running CGEM model..."):
            try:
                data, tmp_dir = cached_run(selected_key)
            except Exception as exc:
                st.error(f"Model run failed: {exc}")
            else:
                times = data["times_s"]
                g = data["g_values"]
                geff = data["geff_values"]

                col1, col2, col3 = st.columns(3)
                grey = "—" if data["time_to_greyout_s"] is None else f"{data['time_to_greyout_s']:.2f} s"
                black = "—" if data["time_to_blackout_s"] is None else f"{data['time_to_blackout_s']:.2f} s"
                gloc = "—" if data["time_to_gloc_s"] is None else f"{data['time_to_gloc_s']:.2f} s"
                col1.metric("Time to greyout", grey)
                col2.metric("Time to blackout", black)
                col3.metric("Time to G-LOC", gloc)

                st.caption(f"Temporary run files saved in: {tmp_dir}")

                # 2D plot: Geff vs Time
                if times and geff:
                    fig2, ax2 = plt.subplots(figsize=(9, 4))
                    ax2.plot(times, geff, color="#2e7d32", linewidth=2, label="G_eff")
                    ax2.plot(times, g, color="#0277bd", linewidth=1.2, alpha=0.7, label="G")
                    ax2.set_xlabel("Time (s)")
                    ax2.set_ylabel("G / G_eff")
                    ax2.set_title("Predicted Effective G vs Time")
                    ax2.grid(True, alpha=0.3)
                    ax2.legend()
                    st.pyplot(fig2, clear_figure=True)

                # 3D plot: Time vs G vs G_eff
                if times and geff and g:
                    fig3 = plt.figure(figsize=(8, 6))
                    ax3 = fig3.add_subplot(111, projection='3d')
                    ax3.plot(times, g, geff, color="#6a1b9a", linewidth=2)
                    ax3.set_xlabel("Time (s)")
                    ax3.set_ylabel("G")
                    ax3.set_zlabel("G_eff")
                    ax3.set_title("3D Trajectory: Time vs G vs G_eff")
                    st.pyplot(fig3, clear_figure=True)

with tab3:
    st.subheader("Batch Predictions for All Profiles (Healthy, midrange subject)")
    run_all = st.button("Run Predictions for All Profiles", type="secondary")

    if run_all:
        for key in profile_keys:
            with st.expander(key.replace("_", " ").title(), expanded=False):
                with st.spinner(f"Running CGEM for {key}..."):
                    try:
                        data, tmp_dir = cached_run(key)
                    except Exception as exc:
                        st.error(f"Model run failed: {exc}")
                        continue

                times = data.get("times_s", [])
                g = data.get("g_values", [])
                geff = data.get("geff_values", [])

                # Metrics row
                col1, col2, col3 = st.columns(3)
                grey = "—" if data["time_to_greyout_s"] is None else f"{data['time_to_greyout_s']:.2f} s"
                black = "—" if data["time_to_blackout_s"] is None else f"{data['time_to_blackout_s']:.2f} s"
                gloc = "—" if data["time_to_gloc_s"] is None else f"{data['time_to_gloc_s']:.2f} s"
                col1.metric("Greyout", grey)
                col2.metric("Blackout", black)
                col3.metric("G-LOC", gloc)

                # Layout: side-by-side 2D and 3D
                c1, c2 = st.columns(2)
                with c1:
                    if times and geff:
                        fig2, ax2 = plt.subplots(figsize=(6, 3.6))
                        ax2.plot(times, geff, color="#2e7d32", linewidth=2, label="G_eff")
                        ax2.plot(times, g, color="#0277bd", linewidth=1.2, alpha=0.7, label="G")
                        ax2.set_xlabel("Time (s)")
                        ax2.set_ylabel("G / G_eff")
                        ax2.set_title("Effective G vs Time")
                        ax2.grid(True, alpha=0.3)
                        ax2.legend()
                        st.pyplot(fig2, clear_figure=True)
                with c2:
                    if times and geff and g:
                        fig3 = plt.figure(figsize=(6, 3.6))
                        ax3 = fig3.add_subplot(111, projection='3d')
                        ax3.plot(times, g, geff, color="#6a1b9a", linewidth=2)
                        ax3.set_xlabel("Time (s)")
                        ax3.set_ylabel("G")
                        ax3.set_zlabel("G_eff")
                        ax3.set_title("3D: Time vs G vs G_eff")
                        st.pyplot(fig3, clear_figure=True)

st.sidebar.info(
    "Predictions use the published CGEM v1.1.0.1 Fortran model with the midrange male subject profile (who=2)."
)