#!/usr/bin/env python3
"""Build the IJNMBE Graphical Table of Contents components.

Drives the two **data panels** of the Graphical TOC composite specified in
``docs/publication/graphical_abstract_ijnmbe.md``. Outputs:

- ``data/results/figures/graphical_toc_panel_a.mmd`` — Mermaid source for
  the simplified architecture diagram (Panel A).
- ``data/results/figures/graphical_toc_panel_a.svg`` — rendered Panel A
  SVG, fetched from mermaid.ink (the same renderer the
  ``cli-anything-mermaid`` skill uses); fallback only if the local
  mermaid-cli is broken (it tends to be on this host because
  ``mmdc`` runs as root and Puppeteer Chromium refuses to launch).
- ``data/results/figures/graphical_toc_panel_b.json`` — ECharts option
  object for the speed + coverage + OOD summary panel (Panel B).

Composite Panels A + B + a title strip in Inkscape / Illustrator at
1500 × 900 px (5 : 3) per the spec, then export to:

    data/results/figures/graphical_toc.{pdf,png}  (300 dpi)

Run with::

    python scripts/build_graphical_toc.py

If mermaid.ink is unreachable for any reason, use the fallback
``cli-anything-mermaid`` skill or ``mmdc`` locally.
"""

from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

FIG_DIR = _REPO_ROOT / "data" / "results" / "figures"
OUT_PANEL_A_MMD = FIG_DIR / "graphical_toc_panel_a.mmd"
OUT_PANEL_A_SVG = FIG_DIR / "graphical_toc_panel_a.svg"
OUT_PANEL_B_JSON = FIG_DIR / "graphical_toc_panel_b.json"
OUT_PANEL_B_SVG = FIG_DIR / "graphical_toc_panel_b.svg"
NODE_RENDERER = _REPO_ROOT / "scripts" / "render_echarts_svg.mjs"

# Okabe-Ito colour-blind-safe palette, consistent with figs 1-5 in this manuscript.
COLOUR_PRIMARY = "#0072B2"   # sky blue   — surrogate / wrapper layer
COLOUR_SECONDARY = "#D55E00"  # vermillion — OOD / abstention
COLOUR_ACCENT = "#009E73"    # bluish green — coverage / accept
COLOUR_NEUTRAL = "#999999"   # grey       — reference lines only, NEVER for data encoding


# ──────────────────────────────────────────────────────────────────────
# Panel A — simplified architecture (Mermaid)
# ──────────────────────────────────────────────────────────────────────


def _panel_a_mermaid() -> str:
    """Return the simplified Mermaid source for the architecture panel.

    Compared to ``data/results/figures/fig6_architecture.mmd`` (the full
    manuscript Figure 6), this version drops:

    - The frontend / backend / package-name labels.
    - The pulse-sim contract annotations.
    - The CI test-job annotations.
    - All endpoint enumerations.

    What remains is a four-tier vertical stack — *core ⇄ wrapper ⇄ ML
    layer ⇄ deployment* — that conveys the additive-wrapper concept at
    thumbnail size in the journal's online table of contents.
    """

    return """%% IJNMBE Graphical TOC — Panel A (simplified architecture).
%%
%% Companion to data/results/figures/fig6_architecture.mmd (the full
%% manuscript Figure 6). This thumbnail-readable version drops endpoint,
%% contract, and CI-test annotations; it conveys ONLY the additive-wrapper
%% concept (core <- wrapper <- ML layer <- deployment).
%%
%% Render:
%%   npx -y @mermaid-js/mermaid-cli@latest \\
%%     -i data/results/figures/graphical_toc_panel_a.mmd \\
%%     -o data/results/figures/graphical_toc_panel_a.svg \\
%%     -b transparent --width 700 --height 900

flowchart TB
    DEPLOY["Deployment<br/>FastAPI + React frontend + Docker"]
    ML["ML extension<br/>XGBoost surrogate · Mondrian conformal · Mahalanobis OOD · Sobol/Morris"]
    WRAP["Python wrapper<br/>cgem_wrapper · subprocess I/O"]
    CORE["FAA-validated CGEM<br/>(Fortran ODE, NEVER MODIFIED)"]

    DEPLOY --> ML
    ML --> WRAP
    WRAP --> CORE

    classDef core   fill:#FFF,stroke:#0072B2,stroke-width:3px,color:#0072B2,font-weight:bold;
    classDef wrap   fill:#FFF,stroke:#0072B2,stroke-width:1.5px,color:#0072B2;
    classDef ml     fill:#0072B2,stroke:#0072B2,stroke-width:2px,color:#FFF,font-weight:bold;
    classDef deploy fill:#FFF,stroke:#999,stroke-width:1px,color:#333;

    class CORE core;
    class WRAP wrap;
    class ML ml;
    class DEPLOY deploy;
"""


# ──────────────────────────────────────────────────────────────────────
# Panel B — speed + coverage + OOD summary (ECharts options)
# ──────────────────────────────────────────────────────────────────────


def _panel_b_echarts() -> dict:
    """Return an ECharts option object for the headline-numbers panel.

    Three rows, each conveying one quantitative anchor from the manuscript:

    1. Speed: surrogate (50 us) vs Fortran (9 ms) — log scale bar.
    2. Conformal coverage: 4 of 5 targets within +/- 4.6 pp of nominal 95 %.
    3. OOD calibration: empirical 0.953 vs nominal 0.95.

    Colour scheme: Okabe-Ito (#0072B2 + #D55E00 + #009E73). No tints.
    All categorical encoding is solid colour fills with explicit labels;
    the only grey (#999) is the nominal-95 % reference line in row 2/3.

    Render to SVG/PDF via the same ECharts toolchain used for figs 1-5
    (e.g. via the ``echarts`` skill, or ``npx echarts2img``).
    """

    return {
        "title": [
            {
                "text": "Speed-up:  surrogate vs CGEM Fortran  (ms)",
                "left": "2%",
                "top": "0%",
                "textStyle": {"fontSize": 12, "fontWeight": "bold", "color": "#333"},
            },
            {
                "text": "Mondrian conformal coverage",
                "left": "2%",
                "top": "35%",
                "textStyle": {"fontSize": 12, "fontWeight": "bold", "color": "#333"},
            },
            {
                "text": "Conformal OOD calibration",
                "left": "2%",
                "top": "70%",
                "textStyle": {"fontSize": 12, "fontWeight": "bold", "color": "#333"},
            },
        ],
        "grid": [
            # Row 1 — speed bar (linear ms)
            {"left": "18%", "right": "18%", "top": "10%", "bottom": "70%"},
            # Row 2 — coverage strip
            {"left": "20%", "right": "10%", "top": "45%", "bottom": "37%"},
            # Row 3 — OOD strip
            {"left": "20%", "right": "10%", "top": "80%", "bottom": "5%"},
        ],
        "xAxis": [
            {
                "gridIndex": 0,
                "type": "value",
                "min": 0,
                "max": 10,
                "axisLabel": {
                    "formatter": "{value} ms",
                    "fontSize": 9,
                    "color": "#333",
                },
                "splitLine": {"show": False},
                "axisLine": {"lineStyle": {"color": "#333"}},
            },
            {
                "gridIndex": 1,
                "type": "value",
                "min": 0.85,
                "max": 1.0,
                "axisLabel": {
                    "formatter": "{value}",
                    "fontSize": 9,
                    "color": "#333",
                },
                "splitLine": {"show": False},
                "axisLine": {"lineStyle": {"color": "#333"}},
            },
            {
                "gridIndex": 2,
                "type": "value",
                "min": 0.92,
                "max": 0.97,
                "axisLabel": {
                    "formatter": "{value}",
                    "fontSize": 9,
                    "color": "#333",
                },
                "splitLine": {"show": False},
                "axisLine": {"lineStyle": {"color": "#333"}},
            },
        ],
        "yAxis": [
            # Row 1 — categorical: two bars (surrogate, CGEM)
            {
                "gridIndex": 0,
                "type": "category",
                "data": ["surrogate", "CGEM"],
                "axisLabel": {"fontSize": 10, "color": "#333"},
                "axisLine": {"lineStyle": {"color": "#333"}},
            },
            # Row 2 — categorical: 5 targets
            {
                "gridIndex": 1,
                "type": "category",
                "data": [
                    "time_to_gloc_s",
                    "time_to_blackout_s",
                    "time_to_greyout_s",
                    "c_bank_min",
                    "hlap_min",
                ],
                "axisLabel": {"fontSize": 8, "color": "#333"},
                "axisLine": {"lineStyle": {"color": "#333"}},
            },
            # Row 3 — single category: empirical OOD calibration
            {
                "gridIndex": 2,
                "type": "category",
                "data": ["conformal abstention"],
                "axisLabel": {"fontSize": 10, "color": "#333"},
                "axisLine": {"lineStyle": {"color": "#333"}},
            },
        ],
        "series": [
            # Row 1 — speed bars (in milliseconds; per-bar labels)
            {
                "name": "latency",
                "type": "bar",
                "xAxisIndex": 0,
                "yAxisIndex": 0,
                "data": [
                    {
                        "value": 0.05,  # 50 us = 0.05 ms
                        "itemStyle": {"color": COLOUR_PRIMARY},
                        "label": {
                            "show": True,
                            "position": "right",
                            "fontSize": 11,
                            "fontWeight": "bold",
                            "color": "#333",
                            "formatter": "0.05 ms (50 µs)   ≈180× faster",
                        },
                    },
                    {
                        "value": 9.0,  # 9 ms
                        "itemStyle": {"color": COLOUR_SECONDARY},
                        "label": {
                            "show": True,
                            "position": "right",
                            "fontSize": 11,
                            "color": "#333",
                            "formatter": "9 ms",
                        },
                    },
                ],
                "barCategoryGap": "30%",
            },
            # Row 2 — coverage points (one per target) plus 95% nominal line.
            {
                "name": "coverage",
                "type": "bar",
                "xAxisIndex": 1,
                "yAxisIndex": 1,
                "data": [
                    {"value": 0.861, "itemStyle": {"color": COLOUR_SECONDARY}},  # under-coverage flagged
                    {"value": 0.948, "itemStyle": {"color": COLOUR_ACCENT}},
                    {"value": 0.946, "itemStyle": {"color": COLOUR_ACCENT}},
                    {"value": 0.950, "itemStyle": {"color": COLOUR_ACCENT}},
                    {"value": 0.953, "itemStyle": {"color": COLOUR_ACCENT}},
                ],
                "label": {
                    "show": True,
                    "position": "right",
                    "fontSize": 9,
                    "color": "#333",
                    "formatter": "{c}",
                },
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"color": COLOUR_NEUTRAL, "type": "dashed", "width": 1.2},
                    "label": {
                        "show": True,
                        "position": "end",
                        "formatter": "nominal 95%",
                        "fontSize": 9,
                        "color": COLOUR_NEUTRAL,
                    },
                    "data": [{"xAxis": 0.95}],
                },
            },
            # Row 3 — OOD calibration point.
            {
                "name": "ood",
                "type": "bar",
                "xAxisIndex": 2,
                "yAxisIndex": 2,
                "data": [
                    {"value": 0.953, "itemStyle": {"color": COLOUR_ACCENT}},
                ],
                "label": {
                    "show": True,
                    "position": "right",
                    "fontSize": 10,
                    "color": "#333",
                    "formatter": "0.953  (nominal 0.95; +0.3 pp)",
                },
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"color": COLOUR_NEUTRAL, "type": "dashed", "width": 1.2},
                    "label": {
                        "show": True,
                        "position": "end",
                        "formatter": "nominal 95%",
                        "fontSize": 9,
                        "color": COLOUR_NEUTRAL,
                    },
                    "data": [{"xAxis": 0.95}],
                },
            },
        ],
        "_render_hints": {
            "viewport": [800, 900],
            "background": "transparent",
            "note": "All categorical encoding by solid colour (Okabe-Ito); "
                    "grey #999 used only for the nominal-95% reference line. "
                    "Compliant with the IJNMBE 'no tints' rule.",
        },
    }


# ──────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────


def _render_panel_a_via_mermaid_ink(mmd_source: str, out_svg: Path) -> bool:
    """Render the cleaned Mermaid source via mermaid.ink (HTTPS, no Puppeteer).

    mermaid.ink is the same upstream renderer used by the
    ``cli-anything-mermaid`` skill. It accepts a base64-url-encoded Mermaid
    source and returns rendered SVG/PNG. Comments and Unicode middle-dots
    can trip it; we strip both before encoding.

    Returns True on a clean fetch (HTTP 200, body starts with ``<svg``),
    False otherwise — the .mmd source is always written even if rendering
    fails, so the user can render later.
    """
    cleaned = re.sub(r"^\s*%%.*$", "", mmd_source, flags=re.M)
    cleaned = cleaned.replace("·", "|")  # · -> |
    cleaned = re.sub(r"\n\n+", "\n\n", cleaned).strip() + "\n"
    encoded = base64.urlsafe_b64encode(cleaned.encode("utf-8")).decode().rstrip("=")
    url = f"https://mermaid.ink/svg/{encoded}"
    # mermaid.ink rejects urllib's default User-Agent (HTTP 403); use a normal
    # browser-like UA. This matches what the cli-anything-mermaid skill does.
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (cgem-ext build_graphical_toc.py)",
        "Accept": "image/svg+xml,*/*",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            if resp.status == 200 and body.lstrip().startswith(b"<svg"):
                out_svg.write_bytes(body)
                return True
    except Exception as exc:  # noqa: BLE001 — best-effort fallback
        print(f"  WARN: mermaid.ink render failed: {exc}")
    return False


def _render_panel_b_via_node(json_path: Path, out_svg: Path,
                              w: int = 800, h: int = 900) -> bool:
    """Render the ECharts option JSON to SVG via Node + jsdom + echarts SSR.

    Calls ``scripts/render_echarts_svg.mjs``, which uses ECharts 6's SSR
    SVG renderer in a jsdom virtual document. Both echarts and jsdom are
    expected at ``node_modules/`` (jsdom installed via ``npm i --no-save
    jsdom`` if missing).

    Returns True on success, False otherwise — the JSON is always written
    so the user can render later.
    """
    node_bin = shutil.which("node")
    if node_bin is None:
        print("  WARN: node not in PATH; skipping Panel B SVG render")
        return False
    if not (_REPO_ROOT / "node_modules" / "echarts").is_dir():
        print("  WARN: node_modules/echarts not present; run 'npm install' first")
        return False
    if not (_REPO_ROOT / "node_modules" / "jsdom").is_dir():
        # Try a quiet, non-saving install — small fix to keep the script
        # one-step on a fresh checkout.
        print("  installing jsdom (--no-save) for SSR …")
        try:
            subprocess.run(
                ["npm", "i", "--no-save", "jsdom"],
                cwd=_REPO_ROOT, check=True, capture_output=True, timeout=120,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  WARN: jsdom install failed: {exc}; skipping Panel B SVG render")
            return False

    try:
        result = subprocess.run(
            [node_bin, str(NODE_RENDERER), str(json_path), str(out_svg), str(w), str(h)],
            cwd=_REPO_ROOT, check=True, capture_output=True, timeout=60, text=True,
        )
        if result.stdout.strip():
            print(f"  {result.stdout.strip()}")
        return out_svg.is_file() and out_svg.stat().st_size > 0
    except subprocess.CalledProcessError as exc:
        print(f"  WARN: Panel B render failed: {exc.stderr or exc}")
        return False


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Panel A — Mermaid + mermaid.ink SVG
    panel_a_src = _panel_a_mermaid()
    OUT_PANEL_A_MMD.write_text(panel_a_src, encoding="utf-8")
    print(f"  wrote {OUT_PANEL_A_MMD.relative_to(_REPO_ROOT)}  "
          f"({OUT_PANEL_A_MMD.stat().st_size:,} bytes)")

    if _render_panel_a_via_mermaid_ink(panel_a_src, OUT_PANEL_A_SVG):
        print(f"  wrote {OUT_PANEL_A_SVG.relative_to(_REPO_ROOT)}  "
              f"({OUT_PANEL_A_SVG.stat().st_size:,} bytes)  "
              f"[via mermaid.ink]")
    else:
        print(f"  SKIPPED {OUT_PANEL_A_SVG.relative_to(_REPO_ROOT)}  "
              f"[mermaid.ink unreachable; render later]")

    # Panel B — ECharts JSON + Node SSR SVG
    panel_b = _panel_b_echarts()
    OUT_PANEL_B_JSON.write_text(json.dumps(panel_b, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {OUT_PANEL_B_JSON.relative_to(_REPO_ROOT)}  "
          f"({OUT_PANEL_B_JSON.stat().st_size:,} bytes)")

    if _render_panel_b_via_node(OUT_PANEL_B_JSON, OUT_PANEL_B_SVG):
        pass  # the helper already prints its own success line
    else:
        print(f"  SKIPPED {OUT_PANEL_B_SVG.relative_to(_REPO_ROOT)}  "
              f"[render manually via the echarts skill]")

    print()
    print("Next step (manual): composite Panels A + B + a title strip in a")
    print("vector tool (Inkscape / Illustrator) at 1500 x 900 px (5 : 3) and")
    print("export to data/results/figures/graphical_toc.{pdf,png}  (300 dpi).")
    print()
    print("Per the IJNMBE Author Guidelines, upload graphical_toc.pdf (or .png)")
    print("at the Wiley CNM portal under the 'Graphical Table of Contents' label.")


if __name__ == "__main__":
    main()
