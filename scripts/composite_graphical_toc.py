#!/usr/bin/env python3
"""Composite the IJNMBE Graphical TOC final image (PDF + PNG @ 300 dpi).

Reads the two pre-rendered panel SVGs produced by
``scripts/build_graphical_toc.py``:

- ``data/results/figures/graphical_toc_panel_a.svg`` — architecture diagram
- ``data/results/figures/graphical_toc_panel_b.svg`` — speed + coverage + OOD

Builds a master SVG at 1500 × 900 px (5 : 3) with:

- Panel A on the left (40 % width).
- Panel B on the right (55 % width).
- Title strip across the bottom.

Then renders to ``data/results/figures/graphical_toc.{pdf,png}`` at 300 dpi
via cairosvg. Per the IJNMBE Author Guidelines this final composite is the
file that uploads at the Wiley CNM portal under the
"Graphical Table of Contents" designation.

Run with::

    python scripts/composite_graphical_toc.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

FIG_DIR = _REPO_ROOT / "data" / "results" / "figures"
PANEL_B_SVG = FIG_DIR / "graphical_toc_panel_b.svg"
OUT_SVG = FIG_DIR / "graphical_toc.svg"
OUT_PDF = FIG_DIR / "graphical_toc.pdf"
OUT_PNG = FIG_DIR / "graphical_toc.png"

# Master canvas — 1500 x 900 px (5 : 3) per the spec in
# docs/publication/graphical_abstract_ijnmbe.md.
W, H = 1500, 900

# Layout grid (px in the master canvas).
TITLE_BAND_H = 90
PANEL_A_BOX = (30, 50, 560, H - TITLE_BAND_H - 80)         # left, top, width, height
PANEL_B_BOX = (610, 50, 860, H - TITLE_BAND_H - 80)
TITLE_Y = H - TITLE_BAND_H + 50

TITLE_TEXT = (
    "Conformal ML wrapper for a validated ODE physiological model "
    "— FAA CGEM case study"
)

# Okabe-Ito colour-blind-safe palette (matches build_graphical_toc.py and
# manuscript figs 1-5).
COLOUR_CORE = "#0072B2"
COLOUR_ML = "#0072B2"
COLOUR_WRAP = "#FFFFFF"
COLOUR_DEPLOY = "#999999"


def _strip_xml_decl(svg: str) -> str:
    """Drop the leading XML declaration / DOCTYPE if present."""
    s = svg.lstrip()
    if s.startswith("<?xml"):
        s = s.split("?>", 1)[1].lstrip()
    if s.startswith("<!DOCTYPE"):
        s = s.split(">", 1)[1].lstrip()
    return s


def _extract_inner_svg(svg_text: str) -> tuple[str, str]:
    """Return ``(viewbox_attrs, inner_xml)``.

    Reads the outer ``<svg ...>`` opening tag of a child SVG, captures its
    ``viewBox`` (and ``preserveAspectRatio`` if any) so the parent can place
    the child cleanly, and returns the content between ``<svg ...>`` and
    the matching closing ``</svg>``.
    """
    s = _strip_xml_decl(svg_text)
    m = re.match(r"<svg([^>]*)>", s, flags=re.DOTALL)
    if not m:
        raise ValueError("input does not start with a valid <svg> opening tag")
    open_attrs = m.group(1)

    # Extract viewBox.
    vb_m = re.search(r'\bviewBox\s*=\s*"([^"]+)"', open_attrs)
    if not vb_m:
        # Fall back: synthesize a viewBox from explicit width/height.
        w_m = re.search(r'\bwidth\s*=\s*"(\d+(?:\.\d+)?)', open_attrs)
        h_m = re.search(r'\bheight\s*=\s*"(\d+(?:\.\d+)?)', open_attrs)
        if not (w_m and h_m):
            raise ValueError("child SVG has no viewBox or width/height")
        vb = f"0 0 {w_m.group(1)} {h_m.group(1)}"
    else:
        vb = vb_m.group(1)

    pa_m = re.search(r'\bpreserveAspectRatio\s*=\s*"([^"]+)"', open_attrs)
    pa = pa_m.group(1) if pa_m else "xMidYMid meet"

    inner = s[m.end():]
    inner = inner.rsplit("</svg>", 1)[0]
    return f'viewBox="{vb}" preserveAspectRatio="{pa}"', inner


def _panel_a_svg(box: tuple[int, int, int, int]) -> str:
    """Hand-coded Panel A — 4-tier additive-wrapper architecture diagram.

    Drawn directly as SVG primitives (rectangles + text + arrows) to avoid
    the Mermaid CSS / @import-font dependency that doesn't survive cairosvg
    embedding. Visually equivalent to the Mermaid source at
    ``data/results/figures/graphical_toc_panel_a.mmd`` but self-contained.
    """
    x0, y0, w, h = box

    # 4 tier boxes, top-down: deployment → ML → wrapper → CORE.
    tiers = [
        ("Deployment",
         "FastAPI · React frontend · Docker",
         COLOUR_DEPLOY, "#FFFFFF", "#333333"),
        ("ML extension",
         "XGBoost surrogate · Mondrian conformal\n"
         "Mahalanobis OOD · Sobol / Morris",
         COLOUR_ML, COLOUR_ML, "#FFFFFF"),
        ("Python wrapper",
         "cgem_wrapper · subprocess I/O",
         COLOUR_CORE, "#FFFFFF", COLOUR_CORE),
        ("FAA-validated CGEM",
         "Fortran ODE physiology  (NEVER MODIFIED)",
         COLOUR_CORE, "#FFFFFF", COLOUR_CORE),
    ]

    n = len(tiers)
    box_w = int(w * 0.86)
    box_x = x0 + (w - box_w) // 2
    pad_top = 30
    gap = 28
    box_h = (h - pad_top - gap * (n - 1)) // n

    parts: list[str] = []
    parts.append(
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" '
        f'fill="#FAFAFA" stroke="#E0E0E0" stroke-width="1" rx="4" ry="4"/>'
    )
    parts.append(
        f'<text x="{x0 + w / 2}" y="{y0 + 22}" text-anchor="middle" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="14" '
        f'font-weight="bold" fill="#0072B2">A. Additive ML wrapper over CGEM</text>'
    )

    box_centres: list[tuple[float, float]] = []
    for i, (heading, body, stroke, fill, text_col) in enumerate(tiers):
        bx = box_x
        by = y0 + pad_top + i * (box_h + gap)
        cx = bx + box_w / 2
        cy = by + box_h / 2
        box_centres.append((cx, cy))

        stroke_w = "3" if i in (1, 3) else ("2" if i == 2 else "1.5")
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" '
            f'rx="6" ry="6" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_w}"/>'
        )

        # Heading (bold)
        parts.append(
            f'<text x="{cx}" y="{by + 26}" text-anchor="middle" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="15" '
            f'font-weight="bold" fill="{text_col}">{heading}</text>'
        )
        # Body (smaller; supports two lines via the explicit \n)
        body_lines = body.split("\n")
        for li, line in enumerate(body_lines):
            parts.append(
                f'<text x="{cx}" y="{by + 50 + li * 16}" text-anchor="middle" '
                f'font-family="Helvetica, Arial, sans-serif" font-size="12" '
                f'fill="{text_col}">{line}</text>'
            )

    # Arrows between consecutive boxes (top-down).
    for i in range(n - 1):
        cx_top, cy_top = box_centres[i]
        # Tail of arrow at bottom edge of upper box; head at top edge of lower box.
        ay_tail = y0 + pad_top + i * (box_h + gap) + box_h
        ay_head = y0 + pad_top + (i + 1) * (box_h + gap)
        parts.append(
            f'<line x1="{cx_top}" y1="{ay_tail}" x2="{cx_top}" y2="{ay_head - 8}" '
            f'stroke="#333333" stroke-width="2"/>'
        )
        parts.append(
            f'<polygon points="{cx_top - 7},{ay_head - 9} '
            f'{cx_top + 7},{ay_head - 9} {cx_top},{ay_head - 1}" '
            f'fill="#333333"/>'
        )

    return "\n  ".join(parts)


def _build_master_svg() -> str:
    panel_b = PANEL_B_SVG.read_text(encoding="utf-8")
    b_attrs, b_inner = _extract_inner_svg(panel_b)

    bx, by, bw, bh = PANEL_B_BOX
    panel_a_xml = _panel_a_svg(PANEL_A_BOX)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <!-- Background: pure white. -->
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>

  <!-- Frame (very faint, helps the composite read as a single graphic). -->
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}"
        fill="none" stroke="#E0E0E0" stroke-width="1"/>

  <!-- Panel A (architecture, hand-coded; no Mermaid CSS dependency) -->
  {panel_a_xml}

  <!-- Panel B (speed + coverage + OOD; ECharts SSR SVG) -->
  <text x="{bx + bw/2}" y="{by - 8}" text-anchor="middle"
        font-family="Helvetica, Arial, sans-serif" font-size="14"
        font-weight="bold" fill="#0072B2">B. Speed, coverage, and OOD calibration</text>
  <g transform="translate({bx}, {by})">
    <svg width="{bw}" height="{bh}" {b_attrs}>{b_inner}</svg>
  </g>

  <!-- Title strip -->
  <rect x="0" y="{H - TITLE_BAND_H}" width="{W}" height="{TITLE_BAND_H}" fill="#0072B2"/>
  <text x="{W/2}" y="{TITLE_Y}" text-anchor="middle"
        font-family="Helvetica, Arial, sans-serif" font-size="22"
        font-weight="bold" fill="#FFFFFF">{TITLE_TEXT}</text>
</svg>
"""


def _render_pdf_png(master_svg: str, dpi: int = 300) -> None:
    import cairosvg  # type: ignore[import-not-found]

    OUT_SVG.write_text(master_svg, encoding="utf-8")
    print(f"  wrote {OUT_SVG.relative_to(_REPO_ROOT)}  "
          f"({OUT_SVG.stat().st_size:,} bytes)")

    # 300 dpi PDF/PNG. cairosvg defaults to 96 dpi; raise via output_width.
    scale = dpi / 96.0
    out_w_px = int(W * scale)
    out_h_px = int(H * scale)

    cairosvg.svg2pdf(bytestring=master_svg.encode("utf-8"),
                     write_to=str(OUT_PDF))
    print(f"  wrote {OUT_PDF.relative_to(_REPO_ROOT)}  "
          f"({OUT_PDF.stat().st_size:,} bytes)")

    cairosvg.svg2png(bytestring=master_svg.encode("utf-8"),
                     write_to=str(OUT_PNG),
                     output_width=out_w_px,
                     output_height=out_h_px)
    print(f"  wrote {OUT_PNG.relative_to(_REPO_ROOT)}  "
          f"({OUT_PNG.stat().st_size:,} bytes; "
          f"{out_w_px}x{out_h_px}px @ {dpi} dpi)")


def main() -> None:
    if not PANEL_B_SVG.is_file():
        print("ERROR: Panel B SVG not found. Run scripts/build_graphical_toc.py first.")
        sys.exit(1)

    master = _build_master_svg()
    _render_pdf_png(master)

    print()
    print("Composite ready. Per the IJNMBE Author Guidelines, upload")
    print(f"  {OUT_PDF.relative_to(_REPO_ROOT)}  (or .png if PDF rejected)")
    print("at the Wiley CNM portal under the 'Graphical Table of Contents' label.")


if __name__ == "__main__":
    main()
