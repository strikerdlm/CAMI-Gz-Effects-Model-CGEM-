from __future__ import annotations

import math
from pathlib import Path
from typing import List

import pandas as pd
import matplotlib.pyplot as plt
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

tab1, tab2 = st.tabs(["Profile", "Prediction (CGEM)"])

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
    st.subheader("CGEM Model Prediction")

    if st.button("Run CGEM Prediction", type="primary"):
        with st.spinner("Running CGEM model..."):
            try:
                result, tmp_dir = run_cgem_for_profile(selected_key)
            except Exception as exc:
                st.error(f"Model run failed: {exc}")
            else:
                col1, col2, col3 = st.columns(3)
                grey = "—" if result.time_to_greyout_s is None else f"{result.time_to_greyout_s:.2f} s"
                black = "—" if result.time_to_blackout_s is None else f"{result.time_to_blackout_s:.2f} s"
                gloc = "—" if result.time_to_gloc_s is None else f"{result.time_to_gloc_s:.2f} s"
                col1.metric("Time to greyout", grey)
                col2.metric("Time to blackout", black)
                col3.metric("Time to G-LOC", gloc)

                st.caption(f"Temporary run files saved in: {tmp_dir}")
                if result.last_g is not None and result.last_geff is not None:
                    st.write(
                        f"Last snapshot: G={result.last_g:.2f}, G_eff={result.last_geff:.2f}"
                    )

st.sidebar.info(
    "Predictions use the published CGEM v1.1.0.1 Fortran model with the midrange male subject profile (who=2)."
)