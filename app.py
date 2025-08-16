from __future__ import annotations

import math
from pathlib import Path
from typing import List, Dict

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import streamlit as st

from aerobatic_profiles import load_all_profiles, load_profile, PROFILES, Sample
from cgem_wrapper import run_cgem_for_profile, PilotConfig

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
def cached_run(profile_id: str, pilot_cfg_key: str, pilot_cfg: PilotConfig):
    result, tmp_dir = run_cgem_for_profile(profile_id, config=pilot_cfg)
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
        )
        who_map = {f"{PROFILE_DEFS[i]['label']} (who={i})": i for i in range(1, 7)}
        who_profile = who_map.get(who_choice)
        dehydration = st.slider("Dehydration level", 0.0, 1.0, 0.0, 0.1)
        seat_tilt = st.number_input("Seat tilt (deg)", 0.0, 45.0, 10.0, 1.0)
        drug_delay = st.number_input("Drug-induced HR delay (s)", 0.0, 10.0, 0.0, 0.5)
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
        gsuit_psi = st.number_input("G-suit max pressure (PSI)", 0.0, 20.0, 0.0, 0.5)
        gsuit_cov = st.slider("G-suit coverage (fraction)", 0.0, 0.7, 0.0, 0.05)
        agsm = st.slider("AGSM effectiveness", 0.0, 1.0, 0.0, 0.05)
        pbg = st.number_input("Pressure breathing max (mmHg)", 0.0, 60.0, 0.0, 1.0)
    with colC:
        other_strain = st.number_input("Pre-test other strain HLAP (mmHg)", 0.0, 60.0, 0.0, 1.0)
        tensing_limit = st.number_input("Non-AGSM tensing limit (mmHg)", 0.0, 60.0, 0.0, 1.0)
        if who_profile is None:
            st.markdown("— Custom subject details —")
            male = st.selectbox("Sex", ["Male", "Female"], index=0)
            height_cm = st.number_input("Height (cm)", 150.0, 205.0, 179.0, 0.5)
            bsp = st.number_input("Baseline systolic BP", 80.0, 180.0, 120.0, 1.0)
            bdp = st.number_input("Baseline diastolic BP", 50.0, 110.0, 80.0, 1.0)
            msp = st.number_input("Max systolic BP", 120.0, 260.0, 177.0, 1.0)
            mdp = st.number_input("Max diastolic BP", 56.0, 140.0, 80.0, 1.0)
            gtm = st.number_input("G tolerance multiplier", 0.8, 1.6, 1.0, 0.01)
            beta = st.number_input("Heart response tau (s)", 1.0, 6.0, 2.5, 0.1)
            conbank = st.number_input("Consciousness reserve (s)", 5.0, 20.0, 7.1, 0.1)
            lifebank = st.number_input("Life reserve (s)", 120.0, 300.0, 180.0, 1.0)
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

    if st.button("Run CGEM Prediction", type="primary"):
        with st.spinner("Running CGEM model..."):
            try:
                data, tmp_dir = cached_run(selected_key, pilot_cfg_key=pilot_cfg.to_cache_key(), pilot_cfg=pilot_cfg)
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