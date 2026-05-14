"""Render SHAP bar plots and Morris μ* vs σ scatter plots per target.

The manuscript supplementary list (items 8 and 9) calls for plots, not raw
data, so this script renders one PNG per target for each of the two
sensitivity views:

  SHAP TreeExplainer mean(|SHAP|) bar chart (5 targets × 1 plot)
  Morris μ* vs σ scatter             (5 targets × 1 plot, 9 features)

Outputs are written under:
  data/results/supplementary/plots/
  manuscripts/ijnmbe/rendered/supplementary/plots/

Matplotlib is used (vector PDF + 300-dpi PNG) to keep the supplementary
artifacts publication-grade and language-agnostic — IJNMBE allows PNG/PDF/
EPS as supporting figures.

Usage:
    cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
    /root/.venvs/cgem-ci/bin/python scripts/build_shap_morris_plots.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
SHAP_JSON = REPO / "data" / "results" / "supplementary" / "shap_importance.json"
MORRIS_CSV = REPO / "data" / "results" / "sensitivity" / "morris.csv"

OUT_DIRS = [
    REPO / "data" / "results" / "supplementary" / "plots",
    REPO / "manuscripts" / "ijnmbe" / "rendered" / "supplementary" / "plots",
]
for d in OUT_DIRS:
    d.mkdir(parents=True, exist_ok=True)


def _save(fig, name: str) -> None:
    for d in OUT_DIRS:
        for ext in ("png", "pdf"):
            path = d / f"{name}.{ext}"
            fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def render_shap_plots():
    data = json.loads(SHAP_JSON.read_text())
    targets = data["rows"]

    n = len(targets)
    fig, axes = plt.subplots(1, n, figsize=(4.0 * n, 4.5), constrained_layout=True)
    if n == 1:
        axes = [axes]
    for ax, row in zip(axes, targets):
        names = row["feature_columns"]
        vals = np.asarray(row["mean_abs_shap"], dtype=float)
        order = np.argsort(vals)[::-1]
        ax.barh(
            np.array(names)[order][::-1],
            vals[order][::-1],
            color="#3b67c2",
            edgecolor="black",
            linewidth=0.5,
        )
        ax.set_title(row["target"], fontsize=10)
        ax.set_xlabel("mean(|SHAP|)", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(axis="x", alpha=0.3)
    fig.suptitle(
        "Supplementary Figure S1 — SHAP TreeExplainer feature importance per target",
        fontsize=11,
    )
    _save(fig, "fig_s1_shap_importance")

    # Per-target individual plots too
    for row in targets:
        fig, ax = plt.subplots(figsize=(6, 4.5), constrained_layout=True)
        names = row["feature_columns"]
        vals = np.asarray(row["mean_abs_shap"], dtype=float)
        order = np.argsort(vals)[::-1]
        ax.barh(
            np.array(names)[order][::-1],
            vals[order][::-1],
            color="#3b67c2",
            edgecolor="black",
            linewidth=0.5,
        )
        ax.set_title(f"SHAP TreeExplainer | target: {row['target']} (n_test = {row['n_test']})", fontsize=10)
        ax.set_xlabel("mean(|SHAP|)")
        ax.grid(axis="x", alpha=0.3)
        _save(fig, f"fig_s1_shap_{row['target']}")


def render_morris_plots():
    rows: dict[str, dict[str, list]] = {}
    with MORRIS_CSV.open() as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            t = r["target"]
            rows.setdefault(t, {"feature": [], "mu_star": [], "sigma": []})
            rows[t]["feature"].append(r["feature"])
            rows[t]["mu_star"].append(float(r["mu_star"]))
            rows[t]["sigma"].append(float(r["sigma"]))

    targets = list(rows)
    n = len(targets)
    fig, axes = plt.subplots(1, n, figsize=(4.0 * n, 4.5), constrained_layout=True)
    if n == 1:
        axes = [axes]
    for ax, t in zip(axes, targets):
        d = rows[t]
        mu = np.asarray(d["mu_star"])
        sigma = np.asarray(d["sigma"])
        ax.scatter(mu, sigma, color="#c2683b", edgecolor="black", linewidth=0.5, s=60, zorder=3)
        for i, lab in enumerate(d["feature"]):
            ax.annotate(lab, (mu[i], sigma[i]), fontsize=7, alpha=0.8,
                        xytext=(4, 2), textcoords="offset points")
        ax.set_xlabel("μ* (Morris)")
        ax.set_ylabel("σ (Morris)")
        ax.set_title(t, fontsize=10)
        ax.grid(alpha=0.3)
        ax.tick_params(labelsize=8)
    fig.suptitle(
        "Supplementary Figure S2 — Morris Elementary Effects μ* vs σ per target",
        fontsize=11,
    )
    _save(fig, "fig_s2_morris_mu_star_sigma")

    for t in targets:
        d = rows[t]
        mu = np.asarray(d["mu_star"])
        sigma = np.asarray(d["sigma"])
        fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
        ax.scatter(mu, sigma, color="#c2683b", edgecolor="black", linewidth=0.5, s=60, zorder=3)
        for i, lab in enumerate(d["feature"]):
            ax.annotate(lab, (mu[i], sigma[i]), fontsize=8, alpha=0.85,
                        xytext=(4, 3), textcoords="offset points")
        ax.set_xlabel("μ* (Morris)")
        ax.set_ylabel("σ (Morris)")
        ax.set_title(f"Morris Elementary Effects | target: {t}", fontsize=10)
        ax.grid(alpha=0.3)
        _save(fig, f"fig_s2_morris_{t}")


def main() -> int:
    render_shap_plots()
    render_morris_plots()
    for d in OUT_DIRS:
        n = len(list(d.glob("*.png")))
        print(f"  wrote {n} PNGs + {n} PDFs under: {d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
