# Render checklist — manual edits before AMHP submission

> Pandoc renders the markdown sources to .docx with reasonable
> defaults, but AMHP's Feb-2026 formatting rules require a small set
> of manual adjustments that are not automated. Walk this checklist
> in Word or LibreOffice on every output file before uploading to
> Editorial Manager.

## Per-file outputs

After running `python -m scripts.render_manuscript`:

| Source markdown | Output | Editorial Manager portal label |
|---|---|---|
| `manuscript.md`            | `rendered/manuscript.docx`            | Manuscript |
| `author_page.md`           | `rendered/author_page.docx`           | Title Page |
| `cover_letter.md`          | `rendered/cover_letter.docx`          | Cover Letter |
| `tripod_ai_checklist.md`   | `rendered/tripod_ai_checklist.docx`   | Supplementary |
| `suggested_reviewers.md`   | `rendered/suggested_reviewers.docx`   | (paste into the portal Step 7 fields; not uploaded as a file) |
| `references_verification.md` | `rendered/references_verification.docx` | (internal verification log; not submitted) |

## Manuscript.docx — manual edits

### 1. Spacing and margins

- Select all → Format → Paragraph → Line spacing: **Double**.
- Set ragged-right (left-aligned, no justification).
- Confirm 1-inch margins all sides.

### 2. Page numbers

- Insert → Page Numbers → Top of Page → Plain Number 3 (upper right).
- Page numbers start on the title page (page 1).

### 3. Citation conversion (the big one)

The markdown source uses `[1]`, `[1-3]`, `[7,8]` bracket form because
Pandoc's NLM citation processor (citeproc) is not invoked here. AMHP
requires **superscript Arabic numerals**, citation-order, ≤ 3 per
callout. Convert each `[N]` → `<sup>N</sup>` (or just superscript-format
the digits without the brackets).

Recommended Word find-and-replace pattern: enable "Use wildcards" and
search for `\[([0-9,\-]+)\]`, then format the matched digits as
superscript. (This needs to be done by hand or via a macro because
Word's superscript toggle does not survive find-and-replace cleanly.)

### 4. Table formatting

The four tables are rendered as Markdown tables → docx tables. Check:

- Table number is Roman (Table I, II, III, IV) — Pandoc emits
  Arabic; rename manually.
- Each table on its own page, after the References section.
- Table caption above the table, in italics.

### 5. Figure handling

- Remove the inline `![]()` figure-placeholder rendering Pandoc may
  insert (the manuscript markdown does not include image references,
  so this should be a no-op).
- Confirm figure captions live as a single page at the end of the
  manuscript, before tables. The current markdown has them as the
  last section before "Supplementary materials".
- Move calibration (Fig 3) and OOD-score-distribution (Fig 4) to the
  Supplementary materials list per the figure-count plan in
  `author_page.md`.

### 6. Headers and section numbering

- Pandoc renders `## 1. Introduction` as a heading with the explicit
  number; AMHP allows either numbered or unnumbered. Keep the numbering
  for clarity.
- Verify the running head (`CONFORMAL CGEM EMULATION`) appears in the
  upper-left header on every page.

### 7. References section

- Confirm references are formatted as a hanging-indent list.
- Replace the bracketed list markers `[1]` `[2]` ... with
  superscript-style entries that match the in-text format. AMHP's
  preferred reference style uses raw numbering (e.g., `1.`) without
  brackets in the bibliography, with **superscript Arabic in
  text**.

## Author_page.docx (Title Page) — manual edits

- Match manuscript spacing and margins (double-spaced, ragged right,
  1-inch margins, page number upper right).
- Verify all author identity fields are present: full name, degrees,
  ORCID, institution, city, country, corresponding-author email.
- Confirm the ICMJE contribution statement covers all four ICMJE
  criteria (this is the most common reviewer flag).

## Cover_letter.docx — manual edits

- AMHP submissions use single-spacing for cover letters.
- Replace the placeholder `[Date: TBD at submission]` with the actual
  submission date.
- Replace OSF DOI placeholder if/when the pre-registration is
  posted.
- Ensure the corresponding author's signature block is at the bottom.

## TRIPOD_AI_checklist.docx and supplementary — manual edits

- Single-spaced.
- Compress the section/page/line citations into "see manuscript §N"
  shorthand if they read awkwardly in docx.

## Final check — figure files

The 5 ECharts options + 1 Mermaid file at `data/results/figures/` are
the source-of-truth. Render to TIFF/EPS at submission time:

```bash
# ECharts via Node CLI (install once)
npx -p echarts-cli echarts render \
    data/results/figures/echarts_options/fig1_parity.json \
    --output docs/publication/rendered/fig1_parity.svg --type svg

# Convert SVG → 1200 dpi TIFF for line art (AMHP requirement)
convert -density 1200 -compress lzw \
    docs/publication/rendered/fig1_parity.svg \
    docs/publication/rendered/fig1_parity.tif

# Mermaid via mmdc
mmdc -i data/results/figures/fig6_architecture.mmd \
     -o docs/publication/rendered/fig6_architecture.svg
convert -density 1200 -compress lzw \
    docs/publication/rendered/fig6_architecture.svg \
    docs/publication/rendered/fig6_architecture.tif
```

Each TIFF: ≥ 1200 dpi for line art, ≥ 600 dpi for combination
halftone, grayscale unless requesting print color (it would require
the Color Surcharge form).

## Final check — forms

Four signed PDFs must accompany the submission:

- Author Checklist (signed by corresponding author only)
- Copyright Release Form (signed by all authors — single author here)
- Conflict of Interest Form (one combined or one per author)
- Color Surcharge Agreement — only if requesting color print
  (currently NOT requesting; skip)

Forms come from the AMHP Editorial Manager portal Step 6 download
links. Print → wet-sign or DocuSign → scan to PDF → upload.
