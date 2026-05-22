"""Build the complete PMEA (Physiological Measurement / IOP) submission package.

Sources:   /root/repos/manuscripts/cgem/pmea/src/
Outputs:   /root/repos/manuscripts/cgem/pmea/rendered/

Files produced
--------------
manuscript.docx      Main manuscript (single document with figures inline, Acknowledgements before References)
manuscript.pdf       PDF render of the above (12 pt body, 1.5 line spacing)
cover_letter.docx    Cover letter to Prof. Xiao Hu, EiC
cover_letter.pdf     PDF render of the cover letter
suggested_reviewers.docx   Suggested reviewer slate (4 candidates + 1 contingency)

PMEA submits a single-PDF manuscript with figures and tables embedded inline at first
reference, 12 pt font, ≥ 1.5 line spacing. References are Harvard alphabetical with
article titles. The Acknowledgements section consolidates Funding, Conflict of
Interest, Author Contributions, Ethics, and Data Availability into a single
section placed immediately before References. No AI use statement is included
(per Diego's directive, 2026-05-22).

DOI placeholders for Zenodo and OSF remain in the manuscript and cover letter
until Diego mints them at portal upload time.

Usage
-----
    cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
    python scripts/build_pmea_submission.py [--force]

Pass --force to rebuild all files regardless of mtime.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

# PMEA tree lives at /root/repos/manuscripts/cgem/pmea/ (sibling to bspc/)
MANUSCRIPTS = Path("/root/repos/manuscripts/cgem/pmea")
SRC = MANUSCRIPTS / "src"
OUT = MANUSCRIPTS / "rendered"

# (source_md, output_basename, description) — same basename used for .docx and .pdf
SOURCES: list[tuple[str, str, str]] = [
    ("manuscript.md", "manuscript", "Main manuscript"),
    ("cover_letter_pmea.md", "cover_letter", "Cover letter"),
    ("suggested_reviewers_pmea.md", "suggested_reviewers", "Suggested reviewers"),
]


def _need_render(src: Path, dst: Path, force: bool) -> bool:
    if force or not dst.is_file():
        return True
    return src.stat().st_mtime > dst.stat().st_mtime


def _render_docx(src: Path, dst: Path) -> None:
    cmd = [
        "pandoc",
        str(src),
        "-o", str(dst),
        "--standalone",
        "--wrap=none",
        "--resource-path", str(src.parent),
    ]
    print(f"  pandoc {src.name} -> {dst.name}", flush=True)
    subprocess.run(cmd, check=True, capture_output=False)


def _render_pdf(src: Path, dst: Path) -> None:
    """Render PDF with 12 pt body, 1.5 line spacing, 1-inch margins.

    The --resource-path flag ensures pandoc resolves relative image paths
    (e.g., ../../_archive/bspc/rendered/fig1.pdf) against the source file's
    directory.

    For the main manuscript PDF only, _linenumbers.tex is included in the
    LaTeX header to satisfy PMEA's continuous-line-numbers requirement.
    Cover letter and suggested reviewers are rendered without line numbers.
    """
    cmd = [
        "pandoc",
        str(src),
        "-o", str(dst),
        "--standalone",
        "--wrap=none",
        "--pdf-engine=xelatex",
        "--resource-path", str(src.parent),
        "-V", "fontsize=12pt",
        "-V", "linestretch=1.5",
        "-V", "geometry:margin=1in",
        "-V", "mainfont=DejaVu Serif",
        "-V", "monofont=DejaVu Sans Mono",
    ]
    if src.name.startswith("manuscript"):
        cmd.extend(["--include-in-header", str(SRC / "_linenumbers.tex")])
    print(f"  pandoc {src.name} -> {dst.name}", flush=True)
    subprocess.run(cmd, check=True, capture_output=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Rebuild all outputs.")
    args = parser.parse_args()

    if shutil.which("pandoc") is None:
        print("ERROR: pandoc not found on PATH.")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    rendered = errors = 0

    for src_name, dst_base, label in SOURCES:
        src = SRC / src_name
        if not src.is_file():
            print(f"  MISSING source: {src_name} -- skipping {label}")
            errors += 1
            continue

        # DOCX
        dst_docx = OUT / f"{dst_base}.docx"
        if _need_render(src, dst_docx, args.force):
            try:
                _render_docx(src, dst_docx)
                rendered += 1
            except subprocess.CalledProcessError as e:
                print(f"  ERROR rendering {src_name} -> .docx: {e}")
                errors += 1
        else:
            print(f"  skip   {dst_docx.name} (up-to-date)")

        # PDF
        dst_pdf = OUT / f"{dst_base}.pdf"
        if _need_render(src, dst_pdf, args.force):
            try:
                _render_pdf(src, dst_pdf)
                rendered += 1
            except subprocess.CalledProcessError as e:
                print(f"  ERROR rendering {src_name} -> .pdf: {e}")
                errors += 1
        else:
            print(f"  skip   {dst_pdf.name} (up-to-date)")

    print(f"\nRendered {rendered} | Errors {errors}")
    print(f"Output dir: {OUT}")

    if errors:
        print("\nResolve errors before portal upload.")
        return 1

    print("\nSubmission package complete.")
    print("Diego-action items before portal upload:")
    print("  1. Mint Zenodo dataset/code archive DOI -> replace placeholder in manuscript.md and cover_letter_pmea.md")
    print("  2. Mint OSF preregistration DOI -> replace placeholder in manuscript.md and cover_letter_pmea.md")
    print("  3. Set cover letter date to actual submission date")
    print("  4. Select peer-review model (single-anonymous vs double-anonymous) at portal")
    print("  5. Upload to ScholarOne portal at http://mc04.manuscriptcentral.com/pmea-ipem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
