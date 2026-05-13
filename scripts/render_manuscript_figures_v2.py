"""Nature/IJNMBE-grade manuscript figures via matplotlib.

Re-renders fig1–5 from raw data (not from the ECharts JSONs, which are
display-stage artefacts). Keeps fig6 as a hand-coded SVG. Output:

    manuscripts/ijnmbe/rendered/figures/fig{1..6}.{svg,pdf,png}

Type-42 (TrueType) PDF fonts are non-negotiable for Wiley CNM production.
Liberation Sans (metric-compatible with Arial) is the system font fallback.

Usage:
    python3 scripts/render_manuscript_figures_v2.py
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Publication rcParams (Type-42 fonts, sans-serif, print-size legible)
# ---------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "font.size": 7,
    "axes.labelsize": 8, "axes.titlesize": 8, "axes.titleweight": "normal",
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "legend.frameon": False,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 3,   "ytick.major.size": 3,
    "xtick.direction": "out", "ytick.direction": "out",
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# Okabe-Ito palette (colour-blind safe, IJNMBE-compliant)
OK_BLUE   = "#0072B2"  # championship
OK_VERM   = "#D55E00"  # conceptual
OK_GREEN  = "#009E73"  # extreme_post_stall
OK_PINK   = "#CC79A7"  # military_acm
OK_YELLOW = "#F0E442"
OK_SKY    = "#56B4E9"
OK_BLACK  = "#000000"
GREY      = "#666666"
LGREY     = "#bdbdbd"

CATEGORY_COLORS = {
    "championship":       OK_BLUE,
    "conceptual":         OK_VERM,
    "extreme_post_stall": OK_GREEN,
    "military_acm":       OK_PINK,
}
CATEGORY_LABELS = {
    "championship":       "Championship",
    "conceptual":         "Conceptual",
    "extreme_post_stall": "Extreme post-stall",
    "military_acm":       "Military ACM",
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO = Path(__file__).resolve().parent.parent
_DATA = _REPO / "data" / "results" / "figures"
_SENS = _REPO / "data" / "results" / "sensitivity"
_OUT  = _REPO / "manuscripts" / "ijnmbe" / "rendered" / "figures"
_OUT.mkdir(parents=True, exist_ok=True)


def _save(fig, name: str) -> None:
    """Save figure as PDF (vector), SVG (vector), PNG @ 600 dpi."""
    for ext in ("pdf", "svg"):
        fig.savefig(_OUT / f"{name}.{ext}")
    fig.savefig(_OUT / f"{name}.png", dpi=600)
    print(f"  [PDF/SVG/PNG] {name}")


# ===========================================================================
# Figure 1 — Parity plots, 8 panels (a–h)  4×2 layout, double-column
# ===========================================================================

PARITY_TARGETS = [
    ("hlap_min",                       "hlap_min",  "mmHg",   False),
    ("c_bank_min",                     "c_bank_min", r"cm$\,$s$^{-1}$", False),
    ("time_to_greyout_s_classifier",   "time-to-greyout (classifier)",    "P(event)", True),
    ("time_to_greyout_s_regressor",    "time-to-greyout (regressor)",     "s",        False),
    ("time_to_blackout_s_classifier",  "time-to-blackout (classifier)",   "P(event)", True),
    ("time_to_blackout_s_regressor",   "time-to-blackout (regressor)",    "s",        False),
    ("time_to_gloc_s_classifier",      "time-to-G-LOC (classifier)",      "P(event)", True),
    ("time_to_gloc_s_regressor",       "time-to-G-LOC (regressor)",       "s",        False),
]


def fig1_parity() -> None:
    print("\nFigure 1 — parity plots")
    data = json.loads((_DATA / "parity_data.json").read_text())

    fig, axes = plt.subplots(2, 4, figsize=(7.0, 3.7))
    panels = "abcdefgh"

    for i, (key, title, units, is_classifier) in enumerate(PARITY_TARGETS):
        ax = axes[i // 4, i % 4]
        t = data["targets"][key]
        y_true = np.asarray(t["y_true"])
        y_pred = np.asarray(t["y_pred"])
        cats = np.asarray(t["category"])

        # Scatter by category
        for cat in ["championship", "conceptual", "extreme_post_stall", "military_acm"]:
            mask = cats == cat
            if mask.sum() == 0:
                continue
            ax.scatter(y_true[mask], y_pred[mask],
                       s=5, c=CATEGORY_COLORS[cat],
                       alpha=0.45, edgecolors="none",
                       label=CATEGORY_LABELS[cat] if i == 0 else None,
                       rasterized=True)

        # y=x reference
        lo = min(y_true.min(), y_pred.min())
        hi = max(y_true.max(), y_pred.max())
        pad = (hi - lo) * 0.05 if hi > lo else 0.1
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad],
                ls="--", color=GREY, lw=0.6, zorder=0)
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_aspect("equal", adjustable="box")

        # Metrics
        n = len(y_true)
        if is_classifier:
            # Brier and AUROC handled elsewhere; report n + mean(y_true)
            txt = f"$n$ = {n}\nBase rate = {y_true.mean():.3f}"
        else:
            ss_res = float(((y_true - y_pred) ** 2).sum())
            ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
            rmse = float(np.sqrt(((y_true - y_pred) ** 2).mean()))
            txt = f"$n$ = {n}\n$R^2$ = {r2:.3f}\nRMSE = {rmse:.3g}"

        ax.text(0.97, 0.04, txt,
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=6, color="#222",
                bbox=dict(boxstyle="round,pad=0.18",
                          facecolor="white", edgecolor="none", alpha=0.85))

        # Panel label (Nature lowercase) at upper-left, OUTSIDE the title row
        ax.text(-0.22, 1.05, panels[i], transform=ax.transAxes,
                fontsize=10, fontweight="bold", va="bottom", ha="left")
        ax.set_title(title, pad=3, fontsize=7.5, loc="center")

        ax.set_xlabel(f"CGEM ({units})", labelpad=2)
        ax.set_ylabel(f"Surrogate ({units})", labelpad=2)
        ax.tick_params(pad=2)

    # Single legend at the bottom
    fig.legend(loc="lower center",
               bbox_to_anchor=(0.5, -0.02),
               ncol=4, frameon=False,
               handletextpad=0.4, columnspacing=1.4,
               markerscale=2.2)
    fig.subplots_adjust(hspace=0.60, wspace=0.48,
                        left=0.07, right=0.99, top=0.93, bottom=0.10)
    _save(fig, "fig1")
    plt.close(fig)


# ===========================================================================
# Figure 2 — Mondrian conformal coverage, dot plot
# ===========================================================================

COVERAGE_TARGETS = [
    ("hlap_min",                       "hlap_min"),
    ("c_bank_min",                     "c_bank_min"),
    ("time_to_greyout_s_classifier",   "Greyout (cls)"),
    ("time_to_greyout_s_regressor",    "Greyout (reg)"),
    ("time_to_blackout_s_classifier",  "Blackout (cls)"),
    ("time_to_blackout_s_regressor",   "Blackout (reg)"),
    ("time_to_gloc_s_classifier",      "G-LOC (cls)"),
    ("time_to_gloc_s_regressor",       "G-LOC (reg)"),
]
STRATA = ["championship", "conceptual", "extreme_post_stall", "military_acm"]
# Per the manuscript: zero-event cells are structurally undefined for
# censored regressors; show as "n/a" rather than 0.
STRUCTURAL_NA = {
    ("conceptual", "time_to_greyout_s_regressor"),
    ("conceptual", "time_to_blackout_s_regressor"),
    ("conceptual", "time_to_gloc_s_regressor"),
    ("extreme_post_stall", "time_to_blackout_s_regressor"),
    ("extreme_post_stall", "time_to_gloc_s_regressor"),
}


def fig2_coverage() -> None:
    print("\nFigure 2 — Mondrian coverage")
    data = json.loads((_DATA / "coverage_data.json").read_text())

    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    nominal = data["nominal_coverage"]

    n_targets = len(COVERAGE_TARGETS)
    y_targets = np.arange(n_targets)

    # Per-stratum dots with small vertical jitter for separation
    jitter = np.linspace(-0.22, 0.22, len(STRATA))

    for j, stratum in enumerate(STRATA):
        xs, ys = [], []
        for i, (tk, _) in enumerate(COVERAGE_TARGETS):
            if (stratum, tk) in STRUCTURAL_NA:
                continue
            cov = data["targets"][tk][stratum]
            if cov == 0:  # zero-event safety; still skip
                continue
            xs.append(cov)
            ys.append(i + jitter[j])
        ax.scatter(xs, ys, s=28, c=CATEGORY_COLORS[stratum],
                   label=CATEGORY_LABELS[stratum],
                   edgecolors="white", linewidth=0.4, zorder=3)

    # Nominal 95% reference + ±5pp band
    ax.axvline(nominal, color=OK_BLACK, lw=0.8, ls="--", zorder=1,
               label=f"Nominal {int(nominal*100)} %")
    ax.axvspan(nominal - 0.05, nominal + 0.05, color=LGREY, alpha=0.18, zorder=0)

    # n/a markers
    for i, (tk, _) in enumerate(COVERAGE_TARGETS):
        for j, stratum in enumerate(STRATA):
            if (stratum, tk) in STRUCTURAL_NA:
                ax.text(0.04, i + jitter[j], "n/a",
                        ha="left", va="center", fontsize=5.5,
                        color=LGREY, transform=ax.get_yaxis_transform())

    ax.set_yticks(y_targets)
    ax.set_yticklabels([lbl for _, lbl in COVERAGE_TARGETS])
    ax.set_xlim(0.55, 1.04)
    ax.set_xlabel("Empirical conformal coverage on held-out test split")
    ax.invert_yaxis()
    ax.grid(axis="x", color=LGREY, lw=0.3, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)

    ax.legend(loc="lower left", bbox_to_anchor=(0.0, -0.32),
              ncol=5, frameon=False, handletextpad=0.4,
              columnspacing=1.2, markerscale=1.0)
    fig.tight_layout()
    _save(fig, "fig2")
    plt.close(fig)


# ===========================================================================
# Figure 3 — Reliability diagrams (5 targets, 2×3 grid)
# ===========================================================================

CALIB_TARGETS = [
    ("hlap_min",          "hlap_min",          "mmHg",   False),
    ("c_bank_min",        "c_bank_min",        r"cm$\,$s$^{-1}$", False),
    ("time_to_greyout_s", "time-to-greyout",   None,     True),
    ("time_to_blackout_s","time-to-blackout",  None,     True),
    ("time_to_gloc_s",    "time-to-G-LOC",     None,     True),
]


def fig3_calibration() -> None:
    print("\nFigure 3 — reliability diagrams")
    data = json.loads((_DATA / "calibration_data.json").read_text())

    fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.2))
    panels = "abcde"
    for i, (key, title, units, is_classifier) in enumerate(CALIB_TARGETS):
        ax = axes[i // 3, i % 3]
        t = data["targets"][key]
        pred = np.asarray(t["bin_predicted"], dtype=float)
        obs  = np.asarray(t["bin_observed"], dtype=float)
        counts = np.asarray(t["bin_counts"], dtype=float)
        ece = float(t["ece"])

        # Filter infinite/nan bins (occurs at -inf bin edges for some targets)
        valid = np.isfinite(pred) & np.isfinite(obs) & (counts > 0)
        pred, obs, counts = pred[valid], obs[valid], counts[valid]

        # Marker size proportional to bin count (sqrt scale)
        sizes = 8 + 40 * np.sqrt(counts / max(counts.max(), 1))

        # y = x reference
        lo = min(pred.min(), obs.min())
        hi = max(pred.max(), obs.max())
        pad = (hi - lo) * 0.05 if hi > lo else 0.05
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad],
                ls="--", color=GREY, lw=0.6, zorder=0)
        ax.scatter(pred, obs, s=sizes, c=OK_BLUE,
                   edgecolors="white", linewidth=0.4, alpha=0.85, zorder=2)

        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_aspect("equal", adjustable="box")

        if is_classifier:
            xlbl, ylbl = "Predicted P(event)", "Observed fraction"
        else:
            xlbl = f"Predicted ({units})" if units else "Predicted"
            ylbl = f"Observed ({units})" if units else "Observed"
        ax.set_xlabel(xlbl, labelpad=2)
        ax.set_ylabel(ylbl, labelpad=2)
        ax.tick_params(pad=2)
        ax.set_title(title, pad=3, fontsize=7.5)
        ax.text(-0.22, 1.05, panels[i], transform=ax.transAxes,
                fontsize=10, fontweight="bold", va="bottom", ha="left")
        ax.text(0.97, 0.04, f"ECE = {ece:.3g}",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=6, color="#222",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.85))

    # Use the empty 6th panel as the legend area
    legend_ax = axes[1, 2]
    legend_ax.set_xticks([]); legend_ax.set_yticks([])
    for spine in legend_ax.spines.values():
        spine.set_visible(False)
    legend_ax.set_xlim(0, 1); legend_ax.set_ylim(0, 1)
    handles = []
    for ct, lbl in [(50, "n = 50"), (150, "n = 150"), (300, "n = 300")]:
        size = 8 + 40 * np.sqrt(ct / 300)
        handles.append(plt.scatter([], [], s=size, c=OK_BLUE,
                                   edgecolors="white", linewidth=0.4, alpha=0.85,
                                   label=lbl))
    # Add the y=x line as a separate legend entry
    handles.append(plt.Line2D([], [], color=GREY, ls="--", lw=0.6, label="Perfect calibration"))
    legend_ax.legend(handles=handles, title="Bin count (marker size)",
                     loc="center", frameon=False,
                     fontsize=7, title_fontsize=7.5,
                     handletextpad=0.4, labelspacing=0.8)
    fig.subplots_adjust(hspace=0.6, wspace=0.45,
                        left=0.07, right=0.99, top=0.94, bottom=0.10)
    _save(fig, "fig3")
    plt.close(fig)


# ===========================================================================
# Figure 4 — OOD Mahalanobis distance distributions
# ===========================================================================

def fig4_ood() -> None:
    print("\nFigure 4 — OOD Mahalanobis distributions")
    data = json.loads((_DATA / "ood_scores.json").read_text())

    in_scores = np.asarray(data["in_distribution"]["scores"])
    logo_scores = np.concatenate([
        np.asarray(data["logo_folds"][k]["scores"])
        for k in ["championship", "conceptual", "extreme_post_stall", "military_acm"]
    ])
    chi2_thr     = float(data["in_distribution"]["chi2_threshold"])
    conformal_thr = float(data["in_distribution"]["conformal_threshold"])

    fig, ax = plt.subplots(figsize=(3.5, 2.6))

    # Log-spaced bin edges for heavy-tailed Mahalanobis distribution
    lo = max(min(in_scores.min(), logo_scores.min()), 1.0)
    hi = max(in_scores.max(), logo_scores.max()) * 1.05
    bins = np.logspace(np.log10(lo), np.log10(hi), 50)

    ax.hist(in_scores, bins=bins, density=True,
            color=OK_BLUE, alpha=0.55, label=f"In-distribution ($n$ = {len(in_scores)})",
            edgecolor=OK_BLUE, linewidth=0.3, zorder=2)
    ax.hist(logo_scores, bins=bins, density=True,
            color=OK_VERM, alpha=0.55, label=f"LOGO folds ($n$ = {len(logo_scores)})",
            edgecolor=OK_VERM, linewidth=0.3, zorder=3)

    # Threshold lines with inline labels
    ax.axvline(chi2_thr, color=GREY, lw=0.8, ls=":")
    ax.text(chi2_thr, ax.get_ylim()[1] * 0.92,
            f"  $\\chi^2_{{17, .95}}$ = {chi2_thr:.1f}",
            color=GREY, fontsize=6, ha="left", va="top", rotation=90)
    ax.axvline(conformal_thr, color=OK_BLACK, lw=0.8, ls="--")
    ax.text(conformal_thr, ax.get_ylim()[1] * 0.92,
            f"  conformal threshold = {conformal_thr:.1f}",
            color=OK_BLACK, fontsize=6, ha="left", va="top", rotation=90)

    ax.set_xscale("log")
    ax.set_xlabel("Squared Mahalanobis distance ($d^2$, 17-D feature space)")
    ax.set_ylabel("Density")
    ax.legend(loc="upper left", handletextpad=0.4)
    fig.tight_layout()
    _save(fig, "fig4")
    plt.close(fig)


# ===========================================================================
# Figure 5 — Sobol total-order index heatmap
# ===========================================================================

def fig5_sobol() -> None:
    print("\nFigure 5 — Sobol ST heatmap")
    df = pd.read_csv(_SENS / "sobol_first_total.csv")

    # Build target/feature matrix of ST and its CI
    targets_order = ["hlap_min", "c_bank_min",
                     "time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s"]
    target_label = {
        "hlap_min":            "hlap_min",
        "c_bank_min":          "c_bank_min",
        "time_to_greyout_s":   "time-to-greyout",
        "time_to_blackout_s":  "time-to-blackout",
        "time_to_gloc_s":      "time-to-G-LOC",
    }
    feature_order = ["g_peak_abs", "dgdt_max_g_per_s", "profile_duration_s",
                     "agsm_effectiveness", "gsuit_coverage_fraction",
                     "gsuit_max_psi", "pbg_max_mmhg",
                     "dehydration_level", "g_tolerance_multiplier"]
    feature_label = {
        "g_peak_abs":             "g_peak_abs",
        "dgdt_max_g_per_s":       "dgdt_max_g_per_s",
        "profile_duration_s":     "profile_duration_s",
        "agsm_effectiveness":     "agsm_effectiveness",
        "gsuit_coverage_fraction":"gsuit_coverage_fraction",
        "gsuit_max_psi":          "gsuit_max_psi",
        "pbg_max_mmhg":           "pbg_max_mmhg",
        "dehydration_level":      "dehydration_level",
        "g_tolerance_multiplier": "g_tolerance_multiplier",
    }

    # Heatmap matrix
    M = np.full((len(targets_order), len(feature_order)), np.nan)
    M_lo = np.full_like(M, np.nan)
    for _, row in df.iterrows():
        if row["target"] in targets_order and row["feature"] in feature_order:
            ti = targets_order.index(row["target"])
            fi = feature_order.index(row["feature"])
            st = float(row["ST"])
            stc = float(row["ST_conf"])
            M[ti, fi] = min(st, 1.0)  # cap visually at 1.0
            M_lo[ti, fi] = st - stc

    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto",
                   interpolation="none")

    # Cell annotations + significance markers (CI brackets zero ⇒ dot)
    for ti in range(len(targets_order)):
        for fi in range(len(feature_order)):
            v = M[ti, fi]
            if not np.isfinite(v):
                continue
            color = "white" if v > 0.5 else "#222"
            ax.text(fi, ti, f"{v:.2f}", ha="center", va="center",
                    fontsize=6.5, color=color)
            # Mark non-significant: CI of S_T brackets zero (smaller, top-right)
            if M_lo[ti, fi] <= 0:
                ax.text(fi + 0.34, ti - 0.30, "n.s.",
                        ha="right", va="center", fontsize=5.5, fontstyle="italic",
                        color="white" if v > 0.5 else "#777")

    ax.set_xticks(range(len(feature_order)))
    ax.set_xticklabels([feature_label[f] for f in feature_order],
                       rotation=35, ha="right", fontsize=6.5)
    ax.set_yticks(range(len(targets_order)))
    ax.set_yticklabels([target_label[t] for t in targets_order])
    ax.tick_params(length=0)
    ax.set_xlabel("")
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Colourbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.015,
                        ticks=[0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_label("Total-order Sobol index, $S_T$", labelpad=4)
    cbar.outline.set_linewidth(0.4)
    cbar.ax.tick_params(width=0.4)

    # Annotation: significance marker
    ax.text(0.0, 1.10, "n.s.  = $S_T$ bootstrap CI brackets zero (non-significant)",
            transform=ax.transAxes, fontsize=6.5, color="#444", ha="left",
            fontstyle="italic")

    fig.tight_layout()
    _save(fig, "fig5")
    plt.close(fig)


# ===========================================================================
# Figure 6 — System architecture (hand-coded SVG; preserve from v1)
# ===========================================================================

def fig6_architecture() -> None:
    print("\nFigure 6 — System architecture (hand-coded SVG)")
    import cairosvg
    from PIL import Image

    W, H = 900, 540
    CX = W // 2
    BG = "#ffffff"; TEXT = "#333333"

    layers = [
        (30,  90, 820, "#E8F4F8", OK_BLUE,   OK_BLUE,
         "Application Layer",
         "Vite / React frontend   ·   FastAPI service (/predict  /run-cgem  /ood/score  /sensitivity/sobol  /sweep  …)"),
        (155, 90, 820, "#EAF4EE", OK_GREEN,  OK_GREEN,
         "ML Extension Layer",
         "XGBoost surrogate emulator   ·   Mondrian conformal intervals   ·   CQR (time-to-G-LOC)   ·   Mahalanobis OOD   ·   Sobol/Morris sensitivity"),
        (280, 90, 820, "#FEF3E8", OK_VERM,   OK_VERM,
         "Python Wrapper",
         "Input encoding   ·   Subprocess orchestration (isolated tmpdir per call)   ·   Output parsing   ·   Batch + parallel support"),
        (405, 90, 820, "#F0F9F4", OK_GREEN,  "#1a6b4a",
         "FAA-validated CGEM Fortran Core",
         "Fortran ODE solver (src/cgem.f)   ·   Cardiovascular / cerebrovascular +Gz physiology   ·   NOT modified"),
    ]

    def _box(y_top, bh, bw, fill, stroke, lbl_color, label, sublabel):
        x0 = (W - bw) // 2
        lines = textwrap.wrap(sublabel, width=98)
        text_items = ""
        for i, line in enumerate(lines):
            text_items += (f'<text x="{CX}" y="{y_top + 54 + i*16}" '
                           f'text-anchor="middle" font-size="10" fill="{TEXT}" '
                           f'font-family="Arial,Helvetica,sans-serif">{line}</text>\n')
        return (f'<rect x="{x0}" y="{y_top}" width="{bw}" height="{bh}" '
                f'rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"/>\n'
                f'<text x="{CX}" y="{y_top + 22}" text-anchor="middle" '
                f'font-size="13" font-weight="bold" fill="{lbl_color}" '
                f'font-family="Arial,Helvetica,sans-serif">{label}</text>\n'
                + text_items)

    def _up_arrow(y_from, y_to):
        return (f'<line x1="{CX}" y1="{y_from}" x2="{CX}" y2="{y_to}" '
                f'stroke="#666666" stroke-width="1.5" '
                f'marker-end="url(#arrow)"/>\n')

    boxes_svg = "".join(_box(*L) for L in layers)
    arrows_svg = (_up_arrow(405 - 4, 280 + 90 + 4) +
                  _up_arrow(280 - 4, 155 + 90 + 4) +
                  _up_arrow(155 - 4, 30  + 90 + 4))

    flow_label = (f'<text x="{CX}" y="{H - 18}" text-anchor="middle" '
                  f'font-size="10" fill="#888" '
                  f'font-family="Arial,Helvetica,sans-serif">'
                  f'Data flow: bottom → top   ·   '
                  f'Additive wrapper — CGEM core unchanged</text>\n')

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#666666"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  {boxes_svg}
  {arrows_svg}
  {flow_label}
</svg>"""

    svg_path = _OUT / "fig6.svg"
    svg_path.write_text(svg, encoding="utf-8")
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(_OUT / "fig6.pdf"))
    scale = 600 / 96
    png_path = _OUT / "fig6.png"
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png_path),
                     output_width=int(W * scale), output_height=int(H * scale))
    img = Image.open(str(png_path))
    if img.mode == "RGBA":
        white = Image.new("RGB", img.size, (255, 255, 255))
        white.paste(img, mask=img.split()[3])
        white.save(str(png_path))
    print(f"  [SVG/PDF/PNG] fig6  (PNG {int(W*scale)}×{int(H*scale)} px @ 600 dpi)")


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    print(f"Output -> {_OUT}")
    fig1_parity()
    fig2_coverage()
    fig3_calibration()
    fig4_ood()
    fig5_sobol()
    fig6_architecture()
    print("\nAll 6 figures rendered.")


if __name__ == "__main__":
    main()
