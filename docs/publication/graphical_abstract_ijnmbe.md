# Graphical Abstract & Graphical Table of Contents — IJNMBE submission

> **Two mandatory items at IJNMBE.** Both upload separately in the Wiley
> CNM portal:
> - The **graphic** (image file) → portal label **"Graphical Table of Contents"**.
> - The **mini-abstract text** (this document, content below) → portal label **"Graphical Abstract"**.

---

## (a) Mini-abstract text — upload as **"Graphical Abstract"**

**Title:** Conformal machine-learning emulation and out-of-distribution
detection for the FAA CAMI G-Effects mechanistic model of acceleration
physiology.

**Author:** Diego Malpica, MD\*

\* Corresponding author. Direction of Aerospace Medicine, Aerospace
Scientific Department, Colombian Aerospace Force, Bogotá, Colombia.
ORCID: 0000-0002-2257-4940.

**Mini-abstract (≤ 80 words / ≤ 3 sentences):**

A four-element machine-learning wrapper — XGBoost surrogate, Mondrian
split-conformal intervals stratified by maneuver category, conformal-
distance out-of-distribution abstention, and global Sobol sensitivity —
surrounds the FAA-validated CGEM Fortran ODE model of +Gz acceleration
physiology without modifying it. On a 3,240-row pre-registered held-out
test split, the surrogate is ~180 × faster than direct subprocess
invocation and conformal coverage stays within 4.6 percentage points of
nominal 95 % on 4 of 5 targets. The additive-wrapper pattern generalises
to any validated biomedical ODE model.

**Self-audit:**

- Word count of the mini-abstract paragraph: **78 words** / 80. PASS.
- Sentence count: **3 sentences** / 3 max. PASS.
- Self-contained; no citations; no figure / table / equation references.
  PASS.
- Quantitative anchors present (~180×, ≤4.6 pp, 4 of 5 targets, 95 %).
  PASS.

---

## (b) Graphical Table of Contents — image specification

**Upload portal label:** **"Graphical Table of Contents"**.

**Output target:** `data/results/figures/graphical_toc.png` (300 dpi
raster) **or** `data/results/figures/graphical_toc.pdf` (vector,
preferred).

**Specifications (verified against the IJNMBE Author Guidelines):**

| Spec | Value |
|---|---|
| Resolution | ≥ 300 dpi raster, or vector PDF/EPS |
| Aspect ratio | square (1 : 1) or wide (5 : 3); avoid extreme ratios |
| Thumbnail readability | text inside the graphic legible at ~ 200 px tall |
| Colour | colour-blind-safe palette (Okabe-Ito or equivalent) |
| Greyscale safety | rendered figure must remain interpretable in greyscale |
| Tints rule | **no greyscale shading** to encode categorical data — IJNMBE explicitly forbids tints; use solid colour fills, line styles, hatching, or explicit labels |
| Caption | embed legend in the artwork itself, not in a separate caption |

**Suggested layout** — three-panel composite that conveys the central
methodological insight at thumbnail size:

```
+-------------------------------+----------------------------------+
|                               |                                  |
|   PANEL A                     |   PANEL B                        |
|   (ARCHITECTURE DIAGRAM)      |   (SPEED + COVERAGE SUMMARY)     |
|                               |                                  |
|   [ CGEM Fortran core ]       |   ~180×  faster                  |
|         |                     |   ──────────────────             |
|   [ Python wrapper ]          |   95 % nominal coverage          |
|         |                     |   ▓▓▓▓▓▓▓▓▓░  4 of 5 targets     |
|   ┌─────┴─────┐               |    within ±4.6 pp                |
|   │ Surrogate │               |                                  |
|   │ Conformal │               |   OOD calibration:               |
|   │   OOD     │               |   ▓▓▓▓▓▓▓▓▓▓  0.953              |
|   │  Sobol    │               |    (nominal 0.95)                |
|   └─────┬─────┘               |                                  |
|         |                     |                                  |
|   [ FastAPI service /         |                                  |
|     React frontend ]          |                                  |
+-------------------------------+----------------------------------+
|                                                                  |
|   PANEL C (TITLE STRIP)                                          |
|   Conformal ML wrapper for a validated ODE physiological model   |
|                                                                  |
+------------------------------------------------------------------+
```

The architecture diagram in Panel A is essentially the simplified version
of manuscript Figure 6, conveying the *additive-wrapper* concept at a
glance. Panel B carries the headline empirical anchor (180× speedup +
calibrated coverage). Panel C carries the title strip so the figure is
self-explanatory in the journal's online table-of-contents.

**Render pipeline (automated, run from the repo root):**

```bash
python scripts/build_graphical_toc.py
```

The script (`scripts/build_graphical_toc.py`) produces both panels
end-to-end:

- **Panel A — architecture diagram.** Source: a simplified four-tier
  Mermaid flowchart at `data/results/figures/graphical_toc_panel_a.mmd`
  (deployment → ML extension → wrapper → FAA-validated CGEM). Rendered
  to SVG via `mermaid.ink` (the same upstream service the
  `cli-anything-mermaid` skill uses). Output:
  `data/results/figures/graphical_toc_panel_a.svg`.
- **Panel B — speed + coverage + OOD summary.** Source: an ECharts 6
  option object at `data/results/figures/graphical_toc_panel_b.json`
  (three rows — log-scale speed bar, Mondrian coverage strip vs nominal
  95 %, conformal OOD calibration). Rendered to SVG via
  `scripts/render_echarts_svg.mjs` (Node + jsdom + ECharts SSR). Output:
  `data/results/figures/graphical_toc_panel_b.svg`.

Both renders use the **Okabe-Ito colour-blind-safe palette** (`#0072B2`
sky blue / `#D55E00` vermillion / `#009E73` bluish-green); the only
greyscale (`#999`) is reference / threshold lines, never categorical
encoding — compliant with the IJNMBE "no tints" rule.

**Final composite step (now automated):**

```bash
python scripts/build_graphical_toc.py        # Panel sources + per-panel SVGs
python scripts/composite_graphical_toc.py    # Master SVG + PDF + PNG @ 300 dpi
```

The composite script (`scripts/composite_graphical_toc.py`) places Panel
A on the left, Panel B on the right, and a title strip at the bottom on
a 1500 × 900 px (5:3) master canvas. Outputs:

- `data/results/figures/graphical_toc.svg` — master SVG
- `data/results/figures/graphical_toc.pdf` — vector PDF (Wiley-preferred)
- `data/results/figures/graphical_toc.png` — 4687 × 2812 px raster @ 300 dpi

Implementation notes:

- Panel A is hand-coded inside `composite_graphical_toc.py` (4 stacked
  rectangles + arrows + text labels) rather than embedded from the
  Mermaid SVG. The Mermaid render contains a `<style>@import …</style>`
  rule for fonts that does not survive cairosvg compositing — a
  dedicated hand-coded panel preserves all text in the final PDF and
  PNG and lets the colour/typography stay perfectly consistent with the
  Okabe-Ito palette and the IJNMBE "no tints" rule.
- Panel B is the Node-rendered ECharts SVG, embedded as an `<svg>`
  child of the master via inline XML; per-bar labels are set via the
  ECharts `data: [{value, label, …}]` form (so the surrogate and CGEM
  bars carry distinct, accurate annotations).
- Final render path: `cairosvg.svg2pdf` and `cairosvg.svg2png` at 300
  dpi; no Inkscape / GUI step required.

**Status (2026-05-01):** **F4 closed.** The final composite is rendered
and committed at `data/results/figures/graphical_toc.{svg,pdf,png}` and
is portal-ready. Upload the PDF (or PNG fallback) at the Wiley CNM
portal under the "Graphical Table of Contents" designation. The
mini-abstract text in item (a) above is finalised and ready for the
"Graphical Abstract" portal field.
