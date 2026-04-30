#!/usr/bin/env python3
"""Build ECharts option JSON files for AMHP Paper 1 (Figs 1-5).

Reads figure data from ``data/results/figures/`` and
``data/results/sensitivity/``, constructs per-figure ECharts option
objects, and writes them to ``data/results/figures/echarts_options/``.

Run after ``scripts/generate_figure_data.py``::

    python scripts/build_figure_options.py

Outputs (5 files):
- fig1_parity.json
- fig2_coverage.json
- fig3_calibration.json
- fig4_ood.json
- fig5_sobol.json
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

FIG_DIR = _REPO_ROOT / "data" / "results" / "figures"
SENS_DIR = _REPO_ROOT / "data" / "results" / "sensitivity"
OUT_DIR = FIG_DIR / "echarts_options"

# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def _panel_label(i: int) -> str:
    return chr(65 + i)  # A, B, C, ...


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert #RRGGBB → rgba(r, g, b, a)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _write_json(name: str, option: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    txt = json.dumps(option, indent=2, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print(f"  {name}  ({os.path.getsize(path):,} bytes)")
    return path


# ──────────────────────────────────────────────────────────────────────
# Fig 1 — Parity scatter (2×4 multi-panel)
# ──────────────────────────────────────────────────────────────────────


def _fig1(parity: dict) -> dict:
    targets = parity["targets"]
    tnames = list(targets.keys())
    n = len(tnames)  # 8
    ncols = 4
    nrows = math.ceil(n / ncols)

    panels = []
    for i, tname in enumerate(tnames):
        td = targets[tname]
        panels.append({
            "tname": tname,
            "units": td["units"],
            "data": list(zip(td["y_true"], td["y_pred"])),
        })

    # Build grid/xAxis/yAxis/series arrays for multi-panel
    grids, xaxes, yaxes, series = [], [], [], []

    for idx, p in enumerate(panels):
        row = idx // ncols
        col = idx % ncols
        left_pct = col * (100 // ncols) + 1
        right_pct = 100 - (col + 1) * (100 // ncols) + 1
        top_pct = row * (100 // nrows) + 5
        bottom_pct = 100 - (row + 1) * (100 // nrows) + 5

        grids.append({
            "left": f"{left_pct}%",
            "right": f"{right_pct}%",
            "top": f"{top_pct}%",
            "bottom": f"{bottom_pct}%",
        })
        xaxes.append({
            "gridIndex": idx,
            "type": "value",
            "name": f"Observed ({p['units']})",
            "nameLocation": "middle",
            "nameGap": 28,
            "scale": True,
            "splitLine": {"show": False},
        })
        yaxes.append({
            "gridIndex": idx,
            "type": "value",
            "name": f"Predicted ({p['units']})",
            "nameLocation": "middle",
            "nameGap": 36,
            "scale": True,
        })

        # Scatter series
        series.append({
            "name": p["tname"],
            "type": "scatter",
            "xAxisIndex": idx,
            "yAxisIndex": idx,
            "data": [[float(x), float(y)] for x, y in p["data"]],
            "symbolSize": 4,
            "itemStyle": {"opacity": 0.5, "color": "#0072B2"},
        })
        # Diagonal reference line
        xs = [x for x, _ in p["data"]]
        if xs:
            lo, hi = min(xs), max(xs)
            margin = (hi - lo) * 0.05
            series.append({
                "name": f"{p['tname']}_ref",
                "type": "line",
                "xAxisIndex": idx,
                "yAxisIndex": idx,
                "data": [[float(lo - margin), float(lo - margin)],
                         [float(hi + margin), float(hi + margin)]],
                "showSymbol": False,
                "lineStyle": {"width": 1, "type": "dashed", "color": "#999999"},
                "silent": True,
            })

    titles = [
        {"text": _panel_label(idx),
         "left": f"{col * (100 // ncols) + 1}%",
         "top": f"{row * (100 // nrows) + 1}%",
         "textStyle": {"fontSize": 12, "fontWeight": "bold"}}
        for idx, p in enumerate(panels)
        for row, col in [(idx // ncols, idx % ncols)]
    ]

    return {
        "title": titles,
        "grid": grids,
        "xAxis": xaxes,
        "yAxis": yaxes,
        "series": series,
        "tooltip": {"trigger": "item", "formatter": "Observed: {c[0]}<br/>Predicted: {c[1]}"},
    }


# ──────────────────────────────────────────────────────────────────────
# Fig 2 — Coverage bar chart
# ──────────────────────────────────────────────────────────────────────


def _fig2(coverage: dict) -> dict:
    targets = coverage["targets"]
    tnames = list(targets.keys())
    strata_order = ["championship", "conceptual", "extreme_post_stall", "military_acm"]

    categories = []
    bar_data, overall_data = [], []
    for tname in tnames:
        td = targets[tname]
        categories.append(tname)
        bar_data.append({s: td.get(s, 0) for s in strata_order})
        overall_data.append(td.get("_overall", 0))

    series = []
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    for si, stratum in enumerate(strata_order):
        series.append({
            "name": stratum,
            "type": "bar",
            "data": [d[stratum] for d in bar_data],
            "itemStyle": {"color": colors[si], "opacity": 0.85},
        })

    # Nominal 95% reference mark
    nominal_series = {
        "name": "Nominal 95%",
        "type": "line",
        "data": [0.95] * len(tnames),
        "showSymbol": False,
        "silent": True,
        "lineStyle": {"width": 2, "type": "dashed", "color": "#000000"},
        "markLine": {
            "silent": True,
            "symbol": "none",
            "lineStyle": {"type": "dashed", "color": "#000000", "width": 1.5},
            "data": [{"yAxis": 0.95, "label": {"formatter": "Nominal 95%"}}],
        },
    }

    return {
        "grid": {"left": 120, "right": 40, "bottom": 120, "top": 50},
        "legend": {"data": strata_order, "top": 5},
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLabel": {"rotate": 30, "fontSize": 9, "interval": 0},
        },
        "yAxis": {
            "type": "value",
            "name": "Empirical Coverage",
            "nameLocation": "middle",
            "nameGap": 48,
            "min": 0.60,
            "max": 1.05,
        },
        "series": series + [nominal_series],
        "tooltip": {"trigger": "axis"},
    }


# ──────────────────────────────────────────────────────────────────────
# Fig 3 — Reliability diagrams (multi-panel, per target)
# ──────────────────────────────────────────────────────────────────────


def _fig3(calibration: dict) -> dict:
    targets = calibration["targets"]
    tnames = list(targets.keys())  # 5
    ncols = 3
    nrows = math.ceil(len(tnames) / ncols)

    grids, xaxes, yaxes, series = [], [], [], []
    for idx, tname in enumerate(tnames):
        td = targets[tname]
        row = idx // ncols
        col = idx % ncols
        left_pct = col * (100 // ncols) + 2
        right_pct = 100 - (col + 1) * (100 // ncols) + 2
        top_pct = row * (100 // nrows) + 5
        bottom_pct = 100 - (row + 1) * (100 // nrows) + 5

        grids.append({
            "left": f"{left_pct}%",
            "right": f"{right_pct}%",
            "top": f"{top_pct}%",
            "bottom": f"{bottom_pct}%",
        })
        xaxes.append({
            "gridIndex": idx,
            "type": "value",
            "name": "Predicted",
            "nameLocation": "middle",
            "nameGap": 25,
            "scale": True,
        })
        yaxes.append({
            "gridIndex": idx,
            "type": "value",
            "name": "Observed",
            "nameLocation": "middle",
            "nameGap": 36,
            "scale": True,
        })

        # Strip inf from centers for visualisation; use predicted/observed bins
        centers = td["bin_centers"]
        predicted = td["bin_predicted"]
        observed = td["bin_observed"]

        # Bar: observed fraction per bin, centered at bin center
        series.append({
            "name": f"{tname}_observed",
            "type": "bar",
            "xAxisIndex": idx,
            "yAxisIndex": idx,
            "data": [[float(predicted[i]), float(observed[i])] for i in range(len(predicted))],
            "barWidth": "80%",
            "itemStyle": {"opacity": 0.6, "color": "#0072B2"},
        })

        # Diagonal reference
        all_vals = predicted + observed
        lo, hi = min(all_vals), max(all_vals)
        if hi - lo < 1e-6:
            hi = lo + 1
        margin = (hi - lo) * 0.05
        series.append({
            "name": f"{tname}_ref",
            "type": "line",
            "xAxisIndex": idx,
            "yAxisIndex": idx,
            "data": [[float(lo - margin), float(lo - margin)],
                     [float(hi + margin), float(hi + margin)]],
            "showSymbol": False,
            "lineStyle": {"width": 1, "type": "dashed", "color": "#999999"},
            "silent": True,
        })

    titles = [
        {"text": f"{_panel_label(idx)}  {tname}\nECE={targets[tname]['ece']:.4f}",
         "left": f"{col * (100 // ncols) + 2}%",
         "top": f"{row * (100 // nrows) + 1}%",
         "textStyle": {"fontSize": 10, "fontWeight": "bold"}}
        for idx, tname in enumerate(tnames)
        for row, col in [(idx // ncols, idx % ncols)]
    ]

    return {"title": titles, "grid": grids, "xAxis": xaxes, "yAxis": yaxes, "series": series}


# ──────────────────────────────────────────────────────────────────────
# Fig 4 — OOD score histograms
# ──────────────────────────────────────────────────────────────────────


def _fig4(ood: dict) -> dict:
    id_data = ood["in_distribution"]
    logo = ood["logo_folds"]

    id_scores = id_data["scores"]
    conf_threshold = id_data["conformal_threshold"]
    chi2_threshold = id_data["chi2_threshold"]

    # In-dist histogram
    id_bins = np.histogram_bin_edges(id_scores, bins="scott")
    id_counts, _ = np.histogram(id_scores, bins=id_bins)

    # Combine all LOGO scores into one "OOD" distribution
    all_ood_scores = []
    for fold in logo.values():
        all_ood_scores.extend(fold["scores"])

    ood_bins = np.histogram_bin_edges(all_ood_scores, bins="scott")
    ood_counts, _ = np.histogram(all_ood_scores, bins=ood_bins)

    return {
        "grid": {"left": 80, "right": 40, "bottom": 60, "top": 50},
        "legend": {"data": ["In-Distribution (test)", "OOD (LOGO folds)"], "top": 5},
        "xAxis": {
            "type": "value",
            "name": "Squared Mahalanobis Distance",
            "nameLocation": "middle",
            "nameGap": 30,
        },
        "yAxis": {
            "type": "value",
            "name": "Density",
            "nameLocation": "middle",
            "nameGap": 40,
        },
        "series": [
            {
                "name": "In-Distribution (test)",
                "type": "bar",
                "data": [[id_bins[i], id_bins[i+1], float(id_counts[i])] for i in range(len(id_counts))],
                "barWidth": "99%",
                "itemStyle": {"opacity": 0.5, "color": "#0072B2"},
            },
            {
                "name": "OOD (LOGO folds)",
                "type": "bar",
                "data": [[ood_bins[i], ood_bins[i+1], float(ood_counts[i])] for i in range(len(ood_counts))],
                "barWidth": "99%",
                "itemStyle": {"opacity": 0.4, "color": "#D55E00"},
            },
            {
                "name": "Conformal Threshold",
                "type": "line",
                "data": [],
                "showSymbol": False,
                "silent": True,
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"color": "#D55E00", "width": 1.5, "type": "dashed"},
                    "data": [{"xAxis": conf_threshold, "label": {"formatter": "Conformal"}}],
                },
            },
            {
                "name": "Chi² Threshold",
                "type": "line",
                "data": [],
                "showSymbol": False,
                "silent": True,
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"color": "#999999", "width": 1.5, "type": "dashed"},
                    "data": [{"xAxis": chi2_threshold, "label": {"formatter": "χ²(0.95)"}}],
                },
            },
        ],
    }


# ──────────────────────────────────────────────────────────────────────
# Fig 5 — Sobol heatmap
# ──────────────────────────────────────────────────────────────────────


def _fig5() -> dict:
    sobol = pd.read_csv(SENS_DIR / "sobol_first_total.csv")
    targets_order = [
        "time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s",
        "hlap_min", "c_bank_min",
    ]
    features = sorted(sobol["feature"].unique().tolist())

    # Build heatmap data for ST (total-order indices)
    heat_data_st = []
    for fi, feat in enumerate(features):
        for ti, tname in enumerate(targets_order):
            row = sobol[(sobol["feature"] == feat) & (sobol["target"] == tname)]
            if len(row):
                heat_data_st.append([ti, fi, round(float(row["ST"].iloc[0]), 3)])

    return {
        "title": {
            "text": "Total-Order Sobol Indices (ST)",
            "left": "center",
            "top": 5,
            "textStyle": {"fontSize": 14},
        },
        "grid": {"left": 140, "right": 80, "bottom": 80, "top": 40},
        "xAxis": {
            "type": "category",
            "data": targets_order,
            "axisLabel": {"rotate": 25, "fontSize": 9, "interval": 0},
            "splitArea": {"show": True},
        },
        "yAxis": {
            "type": "category",
            "data": features,
            "splitArea": {"show": True},
        },
        "visualMap": {
            "min": 0,
            "max": 1,
            "calculable": True,
            "orient": "vertical",
            "right": 10,
            "top": "center",
            "inRange": {"color": ["#ffffff", "#0072B2"]},
            "text": ["1.0", "0.0"],
            "textStyle": {"fontSize": 10},
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b1} → {b0}<br/>ST = {c[2]}",
        },
        "series": [
            {
                "type": "heatmap",
                "data": heat_data_st,
                "label": {"show": True, "formatter": "{@[2]}", "fontSize": 9},
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}},
            }
        ],
    }


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────


def _load_json(name: str) -> dict:
    path = FIG_DIR / name
    if not path.is_file():
        sys.exit(f"Missing data file: {path}\nRun scripts/generate_figure_data.py first.")
    return json.loads(path.read_text())


def main() -> None:
    print("Building ECharts option files ...\n")

    parity = _load_json("parity_data.json")
    coverage = _load_json("coverage_data.json")
    calibration = _load_json("calibration_data.json")
    ood = _load_json("ood_scores.json")

    builders = [
        ("fig1_parity.json",       lambda: _fig1(parity)),
        ("fig2_coverage.json",     lambda: _fig2(coverage)),
        ("fig3_calibration.json",  lambda: _fig3(calibration)),
        ("fig4_ood.json",          lambda: _fig4(ood)),
        ("fig5_sobol.json",        _fig5),
    ]

    paths = {}
    for filename, builder in builders:
        option = builder()
        paths[filename] = _write_json(filename, option)

    print(f"\nAll options written to {OUT_DIR}")
    print(f"Next: render each with echarts skill's render.js")


if __name__ == "__main__":
    main()
