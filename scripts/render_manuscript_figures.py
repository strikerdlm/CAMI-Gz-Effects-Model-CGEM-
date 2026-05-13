"""Render all 6 IJNMBE manuscript figures to SVG + PDF + 300-dpi PNG.

Usage (from repo root):
    python scripts/render_manuscript_figures.py

Outputs to manuscripts/ijnmbe/rendered/figures/:
    fig{1..6}.svg, fig{1..6}.pdf, fig{1..6}.png

Design choices:
- ECharts SSR (render_echarts_svg.mjs) for fig1–5, then cairosvg for PDF/PNG.
- Fig 6 hand-coded SVG (Mermaid @import-font bug does not survive cairosvg).
- Okabe-Ito palette throughout; solid fills (no opacity < 1); white background.
- 300 dpi PNG via cairosvg scale = 300/96.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import cairosvg  # type: ignore[import-not-found]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO = Path(__file__).resolve().parent.parent
_FIG_SRC = _REPO / "data" / "results" / "figures" / "echarts_options"
_MJS = _REPO / "scripts" / "render_echarts_svg.mjs"
_OUT = _REPO / "manuscripts" / "ijnmbe" / "rendered" / "figures"
_OUT.mkdir(parents=True, exist_ok=True)
_TMP = _OUT / "_tmp"
_TMP.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
_BLUE = "#0072B2"
_VERMILLION = "#D55E00"
_GREEN = "#009E73"
_PINK = "#CC79A7"
_YELLOW = "#F0E442"
_GREY = "#999999"
_TEXT = "#333333"
_GRID = "#e8e8e8"
_BG = "#ffffff"

# Common text style injected into every option
_TEXT_STYLE = {"fontFamily": "Arial, Helvetica, sans-serif", "color": _TEXT, "fontSize": 12}

# ---------------------------------------------------------------------------
# Helper: apply global polish to any ECharts option dict
# ---------------------------------------------------------------------------

def _polish(opt: dict, *, title: str | None = None) -> dict:
    """Apply IJNMBE-compliant polish to an ECharts option object."""
    import copy
    opt = copy.deepcopy(opt)

    opt["backgroundColor"] = _BG
    opt["textStyle"] = _TEXT_STYLE

    # Remove any opacity < 1 from series itemStyle / lineStyle (IJNMBE: no tints)
    for s in opt.get("series", []):
        if "itemStyle" in s:
            s["itemStyle"].pop("opacity", None)
        if "lineStyle" in s:
            s["lineStyle"].pop("opacity", None)

    # Clean up axis styling (support list or single dict)
    for axis_key in ("xAxis", "yAxis"):
        axes = opt.get(axis_key, [])
        if isinstance(axes, dict):
            axes = [axes]
        for ax in axes:
            ax.setdefault("axisLine", {})["lineStyle"] = {"color": "#aaaaaa"}
            ax.setdefault("axisTick", {})["lineStyle"] = {"color": "#aaaaaa"}
            ax.setdefault("splitLine", {})["lineStyle"] = {"color": _GRID, "type": "solid"}
            ax.setdefault("axisLabel", {}).setdefault("color", _TEXT)

    # Clean up grid
    grids = opt.get("grid", [])
    if isinstance(grids, dict):
        grids = [grids]
    for g in grids:
        g.setdefault("show", False)

    # Remove inline title blocks (panel labels go in the artwork via title[])
    # but keep structured title arrays (multi-panel panel labels)

    # Improve legend styling
    if "legend" in opt:
        leg = opt["legend"]
        leg.setdefault("textStyle", {"color": _TEXT, "fontSize": 11})
        leg.setdefault("itemWidth", 14)
        leg.setdefault("itemHeight", 10)
        leg.setdefault("borderRadius", 2)

    # Improve tooltip
    if "tooltip" in opt:
        opt["tooltip"].setdefault("backgroundColor", "rgba(255,255,255,0.95)")
        opt["tooltip"].setdefault("borderColor", "#cccccc")

    return opt


# ---------------------------------------------------------------------------
# Helper: write polished JSON and render via MJS → SVG
# ---------------------------------------------------------------------------

def _render_echarts(fig_name: str, opt: dict, w: int, h: int) -> Path:
    """Write polished JSON → render SVG via render_echarts_svg.mjs."""
    json_path = _TMP / f"{fig_name}.json"
    svg_path = _OUT / f"{fig_name}.svg"
    json_path.write_text(json.dumps(opt, indent=2), encoding="utf-8")
    result = subprocess.run(
        ["node", str(_MJS), str(json_path), str(svg_path), str(w), str(h)],
        capture_output=True, text=True, cwd=str(_REPO),
    )
    if result.returncode != 0:
        print(f"  ERROR rendering {fig_name}:", result.stderr[:400])
        sys.exit(1)
    print(f"  [SVG] {svg_path.relative_to(_REPO)}")
    return svg_path


# ---------------------------------------------------------------------------
# Helper: SVG → PDF + 300-dpi PNG
# ---------------------------------------------------------------------------
_DPI = 300
_SCREEN_DPI = 96
_SCALE = _DPI / _SCREEN_DPI  # ≈ 3.125


def _export(svg_path: Path, w_px: int, h_px: int) -> None:
    """Convert SVG to PDF + 300-dpi PNG (white-background RGB)."""
    from PIL import Image
    svg_bytes = svg_path.read_bytes()

    pdf_path = svg_path.with_suffix(".pdf")
    cairosvg.svg2pdf(bytestring=svg_bytes, write_to=str(pdf_path))
    print(f"  [PDF] {pdf_path.relative_to(_REPO)}")

    png_path = svg_path.with_suffix(".png")
    out_w = int(w_px * _SCALE)
    out_h = int(h_px * _SCALE)
    cairosvg.svg2png(bytestring=svg_bytes, write_to=str(png_path),
                     output_width=out_w, output_height=out_h)

    # Flatten RGBA → white-background RGB (ECharts SSR leaves alpha channel)
    img = Image.open(str(png_path))
    if img.mode == "RGBA":
        white = Image.new("RGB", img.size, (255, 255, 255))
        white.paste(img, mask=img.split()[3])
        white.save(str(png_path), "PNG")

    print(f"  [PNG] {png_path.relative_to(_REPO)}  ({out_w}×{out_h} px @ {_DPI} dpi)")


# ===========================================================================
# Figure 1 — Parity plots (8 panels, 4×2 layout)
# ===========================================================================

def fig1() -> None:
    print("\n--- Figure 1: Parity plots (8-panel 4×2) ---")
    opt = json.loads((_FIG_SRC / "fig1_parity.json").read_text())
    opt = _polish(opt)

    # Panel labels A–H from figure caption
    LABELS = ["A", "B", "C", "D", "E", "F", "G", "H"]
    TARGET_NAMES = [
        "hlap_min", "c_bank_min",
        "Greyout classifier", "Greyout regressor",
        "Blackout classifier", "Blackout regressor",
        "G-LOC classifier", "G-LOC regressor",
    ]

    # Replace multi-title array with clean panel labels
    if isinstance(opt.get("title"), list):
        new_titles = []
        for i, t in enumerate(opt["title"]):
            t["text"] = LABELS[i] if i < len(LABELS) else t.get("text", "")
            t["textStyle"] = {"fontSize": 11, "fontWeight": "bold", "color": _TEXT}
            new_titles.append(t)
        opt["title"] = new_titles
    else:
        # Build panel labels from grid positions
        grids = opt.get("grid", [])
        opt["title"] = []
        for i, g in enumerate(grids):
            label = LABELS[i] if i < len(LABELS) else str(i + 1)
            opt["title"].append({
                "text": label,
                "left": g.get("left", "0%"),
                "top": g.get("top", "0%"),
                "textStyle": {"fontSize": 11, "fontWeight": "bold", "color": _TEXT},
            })

    # Ensure reference diagonal lines are black dashed (no opacity)
    for s in opt.get("series", []):
        if s.get("type") == "line" and s.get("name", "").startswith("y=x"):
            s["lineStyle"] = {"type": "dashed", "color": "#444444", "width": 1.0}
            s["showSymbol"] = False

    # Ensure scatter symbols are semi-transparent Okabe-Ito without opacity keyword
    # (solid fill is required; use smaller symbol size for readability)
    for s in opt.get("series", []):
        if s.get("type") == "scatter":
            s["symbolSize"] = 4
            s.setdefault("itemStyle", {}).pop("opacity", None)

    W, H = 1600, 900
    svg = _render_echarts("fig1", opt, W, H)
    _export(svg, W, H)


# ===========================================================================
# Figure 2 — Mondrian coverage (grouped bars)
# ===========================================================================

def fig2() -> None:
    print("\n--- Figure 2: Mondrian conformal coverage ---")
    opt = json.loads((_FIG_SRC / "fig2_coverage.json").read_text())
    opt = _polish(opt)

    # Clean up x-axis labels: shorter names
    SHORT_LABELS = [
        "hlap_min", "c_bank_min",
        "Greyout\n(class.)", "Greyout\n(reg.)",
        "Blackout\n(class.)", "Blackout\n(reg.)",
        "G-LOC\n(class.)", "G-LOC\n(reg.)",
    ]
    ax = opt["xAxis"]
    if isinstance(ax, list):
        ax = ax[0]
    ax["data"] = SHORT_LABELS
    ax["axisLabel"] = {
        "rotate": 0,
        "fontSize": 10,
        "interval": 0,
        "color": _TEXT,
        "rich": {},
    }

    # Add y-axis min = 0 to show full scale context, keep cap at 1.05
    ya = opt["yAxis"]
    if isinstance(ya, list):
        ya = ya[0]
    ya["min"] = 0.0
    ya["max"] = 1.05
    ya["axisLabel"] = {"formatter": "{value}", "color": _TEXT, "fontSize": 10}

    # Ensure the nominal 95% reference line is clean
    for s in opt.get("series", []):
        if s.get("name") == "Nominal 95%":
            s["lineStyle"] = {"type": "dashed", "color": "#222222", "width": 1.5}
            s["showSymbol"] = False
            # Remove the redundant markLine (the series line itself suffices)
            s.pop("markLine", None)

    # Legend at top, horizontal
    opt["legend"] = {
        "data": ["championship", "conceptual", "extreme_post_stall", "military_acm", "Nominal 95%"],
        "top": 8,
        "itemWidth": 14,
        "itemHeight": 10,
        "textStyle": {"color": _TEXT, "fontSize": 10},
        "orient": "horizontal",
    }

    # Improve grid margins for rotated labels
    opt["grid"] = {
        "left": 70, "right": 20, "bottom": 80, "top": 50,
        "containLabel": False,
    }

    W, H = 1200, 620
    svg = _render_echarts("fig2", opt, W, H)
    _export(svg, W, H)


# ===========================================================================
# Figure 3 — Reliability diagrams (5-panel 3+2 layout)
# ===========================================================================

def fig3() -> None:
    print("\n--- Figure 3: Reliability diagrams (5-panel) ---")
    opt = json.loads((_FIG_SRC / "fig3_calibration.json").read_text())
    opt = _polish(opt)

    # Panel labels from figure caption: one per grid
    PANEL_LABELS = ["A", "B", "C", "D", "E"]
    grids = opt.get("grid", [])
    if isinstance(grids, dict):
        grids = [grids]

    if isinstance(opt.get("title"), list):
        for i, t in enumerate(opt["title"]):
            if i < len(PANEL_LABELS):
                t["textStyle"] = {"fontSize": 11, "fontWeight": "bold", "color": _TEXT}
    else:
        opt["title"] = []
        for i, g in enumerate(grids):
            opt["title"].append({
                "text": PANEL_LABELS[i] if i < len(PANEL_LABELS) else "",
                "left": g.get("left", "0%"),
                "top": g.get("top", "0%"),
                "textStyle": {"fontSize": 11, "fontWeight": "bold", "color": _TEXT},
            })

    # Clean reference diagonals
    for s in opt.get("series", []):
        if s.get("type") == "line" and ("calibration" in s.get("name", "").lower()
                                         or "diagonal" in s.get("name", "").lower()
                                         or s.get("name", "").startswith("y=")):
            s["lineStyle"] = {"type": "dashed", "color": "#444444", "width": 1.0}
            s["showSymbol"] = False

    W, H = 1400, 900
    svg = _render_echarts("fig3", opt, W, H)
    _export(svg, W, H)


# ===========================================================================
# Figure 4 — OOD Mahalanobis distributions
# ===========================================================================

def fig4() -> None:
    print("\n--- Figure 4: OOD Mahalanobis distributions ---")
    opt = json.loads((_FIG_SRC / "fig4_ood.json").read_text())
    opt = _polish(opt)

    # Ensure threshold lines are visually distinct
    for s in opt.get("series", []):
        if s.get("type") == "line":
            name = s.get("name", "").lower()
            if "conformal" in name:
                s["lineStyle"] = {"type": "dashed", "color": _VERMILLION, "width": 2}
            elif "chi2" in name or "chi" in name or "χ" in name:
                s["lineStyle"] = {"type": "dashed", "color": _GREY, "width": 1.5}
            s["showSymbol"] = False

    # Fill distributions (bars/area) with Okabe-Ito: in-dist = blue, OOD = orange
    for s in opt.get("series", []):
        if s.get("type") in ("bar", "line"):
            name = s.get("name", "").lower()
            if "in-dist" in name or "in_dist" in name or "training" in name:
                s.setdefault("itemStyle", {})["color"] = _BLUE
            elif "out" in name or "ood" in name or "logo" in name:
                s.setdefault("itemStyle", {})["color"] = _VERMILLION

    opt["grid"] = {"left": 70, "right": 30, "bottom": 60, "top": 40}

    W, H = 900, 580
    svg = _render_echarts("fig4", opt, W, H)
    _export(svg, W, H)


# ===========================================================================
# Figure 5 — Sobol ST heatmap
# ===========================================================================

def fig5() -> None:
    print("\n--- Figure 5: Sobol total-order index heatmap ---")
    opt = json.loads((_FIG_SRC / "fig5_sobol.json").read_text())
    opt = _polish(opt)

    # Ensure visualMap uses white→blue (no tints rule: continuous color scale is fine)
    if "visualMap" in opt:
        vm = opt["visualMap"]
        vm["inRange"] = {"color": ["#ffffff", _BLUE]}
        vm["min"] = 0.0
        vm["max"] = 1.0
        vm.setdefault("textStyle", {"color": _TEXT})

    # Ensure cell labels are visible
    for s in opt.get("series", []):
        if s.get("type") == "heatmap":
            s.setdefault("label", {})["show"] = True
            s["label"]["fontSize"] = 10
            s["label"]["color"] = _TEXT

    opt["grid"] = {"left": 140, "right": 100, "bottom": 80, "top": 40}

    W, H = 1000, 680
    svg = _render_echarts("fig5", opt, W, H)
    _export(svg, W, H)


# ===========================================================================
# Figure 6 — System architecture (hand-coded SVG)
# ===========================================================================

def fig6() -> None:
    """Hand-code the architecture SVG to avoid Mermaid @import-font issues."""
    print("\n--- Figure 6: System architecture (hand-coded SVG) ---")

    W, H = 900, 620
    CX = W // 2

    # Layer geometry — bottom→top data flow: CGEM is lowest visual block.
    # Arrows point upward (y decreases toward top in SVG coords).
    # (y_top, box_h, box_w, fill, stroke, label_color, label, sublabel)
    layers = [
        (30,  90, 820, "#E8F4F8", "#0072B2", "#0072B2",
         "Application Layer",
         "Vite / React frontend   ·   FastAPI service (/predict  /run-cgem  /ood/score  /sensitivity/sobol  /sweep  …)"),
        (155, 90, 820, "#EAF4EE", "#009E73", "#009E73",
         "ML Extension Layer",
         "XGBoost surrogate emulator   ·   Mondrian conformal intervals   ·   CQR (time-to-G-LOC)   ·   Mahalanobis OOD   ·   Sobol/Morris sensitivity"),
        (280, 90, 820, "#FEF3E8", "#D55E00", "#D55E00",
         "Python Wrapper",
         "Input encoding   ·   Subprocess orchestration (isolated tmpdir per call)   ·   Output parsing   ·   Batch + parallel support"),
        (405, 90, 820, "#F0F9F4", "#009E73", "#1a6b4a",
         "FAA-validated CGEM Fortran Core",
         "Fortran ODE solver (src/cgem.f)   ·   Cardiovascular / cerebrovascular +Gz physiology   ·   NOT modified"),
    ]

    # Upward arrows (bottom → top data flow), in the gaps between boxes
    # Gap positions (y_from=bottom_of_upper_box, y_to=top_of_lower_box-gap)
    # Each gap: from y_bottom_lower to y_top_upper means arrow points upward
    upward_arrows = [
        (405 - 1, 280 + 90 + 1),   # gap between Wrapper and ML: from y=404 up to y=371
        (280 - 1, 155 + 90 + 1),   # gap between ML and Application: from y=279 up to y=246
        (155 - 1, 30 + 90 + 1),    # not needed for this layout
    ]
    # Simpler: just draw arrows in each gap pointing upward
    arrow_gaps = [
        (405 - 15, 405 - 2),    # Wrapper→ML: from y=390 to y=403, pointing UP so reverse
        (280 - 15, 280 - 2),    # ML→App: same pattern
        (155 - 15, 155 - 2),    # (unused in 4-layer)
    ]

    def box(y_top: int, bh: int, bw: int, fill: str, stroke: str, lbl_color: str,
            label: str, sublabel: str) -> str:
        x0 = (W - bw) // 2
        lines = textwrap.wrap(sublabel, width=98)
        text_items = ""
        for i, line in enumerate(lines):
            text_items += (
                f'<text x="{CX}" y="{y_top + 54 + i * 16}" '
                f'text-anchor="middle" font-size="10" fill="{_TEXT}" '
                f'font-family="Arial,Helvetica,sans-serif">{line}</text>\n'
            )
        return (
            f'<rect x="{x0}" y="{y_top}" width="{bw}" height="{bh}" '
            f'rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"/>\n'
            f'<text x="{CX}" y="{y_top + 22}" text-anchor="middle" '
            f'font-size="13" font-weight="bold" fill="{lbl_color}" '
            f'font-family="Arial,Helvetica,sans-serif">{label}</text>\n'
            + text_items
        )

    def up_arrow(y_from: int, y_to: int) -> str:
        """Arrow pointing upward from y_from to y_to (y_to < y_from in SVG coords)."""
        return (
            f'<line x1="{CX}" y1="{y_from}" x2="{CX}" y2="{y_to}" '
            f'stroke="#666666" stroke-width="1.5" '
            f'marker-end="url(#arrow)"/>\n'
        )

    boxes_svg = "".join(
        box(ly, lh, lw, lf, ls, lc, ll, lsl)
        for ly, lh, lw, lf, ls, lc, ll, lsl in layers
    )
    # Upward arrows between layers (data flows bottom → top)
    arrows_svg = (
        up_arrow(405 - 4, 280 + 90 + 4) +   # CGEM top → Wrapper bottom
        up_arrow(280 - 4, 155 + 90 + 4) +   # Wrapper top → ML bottom
        up_arrow(155 - 4, 30  + 90 + 4)     # ML top → App bottom
    )

    # Add data-flow label
    flow_label = (
        f'<text x="{CX}" y="{H - 18}" text-anchor="middle" '
        f'font-size="10" fill="#888" font-family="Arial,Helvetica,sans-serif">'
        f'Data flow: bottom layer → top layer   ·   Additive wrapper — CGEM core unchanged</text>\n'
    )

    # Figure label
    fig_label = (
        f'<text x="16" y="24" font-size="13" font-weight="bold" '
        f'fill="{_TEXT}" font-family="Arial,Helvetica,sans-serif">Figure 6. System Architecture</text>\n'
    )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#666666"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="{_BG}"/>
  {fig_label}
  {boxes_svg}
  {arrows_svg}
  {flow_label}
</svg>"""

    svg_path = _OUT / "fig6.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"  [SVG] {svg_path.relative_to(_REPO)}")
    _export(svg_path, W, H)


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    print(f"Output → {_OUT.relative_to(_REPO)}/")
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    print("\nAll 6 figures rendered.")


if __name__ == "__main__":
    main()
