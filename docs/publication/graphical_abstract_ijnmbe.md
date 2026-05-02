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

**Render instructions:**

1. Use the `publication-visuals` skill or the existing ECharts pipeline
   (`scripts/build_figure_options.py`) to generate Panel A from the
   already-committed `data/results/figures/fig6_architecture.mmd` Mermaid
   source.
2. Render Panel B as a small bar/score panel from `coverage_data.json`
   and `ood_scores.json`.
3. Composite the two panels + title strip in a vector tool (Inkscape /
   Affinity Designer / Illustrator) at 1500 × 900 px (5:3) and export
   as `graphical_toc.pdf` and `graphical_toc.png` (300 dpi).
4. **No tints.** Audit the PDF/PNG for any greyscale gradient before
   upload — solid fills only.
5. Save final artefacts to `data/results/figures/graphical_toc.{pdf,png}`
   and link from this document with their final paths once rendered.

**Status:** specification complete; **render still TODO** (one of the
remaining FAIL items in `2026-05-01_ijnmbe-status.md`). The mini-abstract
text above (item (a)) is finalised and ready for portal upload.
