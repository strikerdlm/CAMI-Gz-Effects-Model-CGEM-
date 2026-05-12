"""Build the complete IJNMBE submission package from Markdown sources.

Sources:   manuscripts/ijnmbe/src/
Outputs:   manuscripts/ijnmbe/rendered/

Files produced
--------------
manuscript_submission_ijnmbe.docx   Main manuscript (double-spaced, line-numbered)
author_page_ijnmbe.docx             Title page
cover_letter_ijnmbe.docx            Cover letter
novelty_file_ijnmbe.docx            Novelty file (≤ 100 words)
graphical_abstract_ijnmbe.docx      Graphical abstract mini-text
suggested_reviewers_ijnmbe.docx     Suggested reviewers

The Graphical TOC image (graphical_toc.{pdf,png}) is built separately by
  python scripts/build_graphical_toc.py
  python scripts/composite_graphical_toc.py
and copied into manuscripts/ijnmbe/rendered/ if present.

IJNMBE uses Wiley Free Format — no rigid formatting required at initial
submission. The reference DOCX template (_reference.docx) enforces the
peer-review-friendly defaults: 12 pt Times New Roman, double-spaced,
continuous line numbering, A4 with 2.54 cm margins.

Usage
-----
    cd /root/repos/CAMI-Gz-Effects-Model-CGEM-
    python scripts/build_ijnmbe_submission.py [--force]

Pass --force to rebuild all files regardless of mtime.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "manuscripts" / "ijnmbe" / "src"
OUT = REPO / "manuscripts" / "ijnmbe" / "rendered"
REF = OUT / "_reference.docx"

# (source_md, output_docx, description)
SOURCES: list[tuple[str, str, str]] = [
    ("manuscript.md",              "manuscript_submission_ijnmbe.docx", "Main manuscript"),
    ("author_page_ijnmbe.md",      "author_page_ijnmbe.docx",          "Title page"),
    ("cover_letter_ijnmbe.md",     "cover_letter_ijnmbe.docx",         "Cover letter"),
    ("novelty_file_ijnmbe.md",     "novelty_file_ijnmbe.docx",         "Novelty file"),
    ("graphical_abstract_ijnmbe.md","graphical_abstract_ijnmbe.docx",  "Graphical abstract"),
    ("suggested_reviewers_ijnmbe.md","suggested_reviewers_ijnmbe.docx","Suggested reviewers"),
]

# Graphical TOC image candidates (built by separate scripts)
TOC_SOURCES = [
    REPO / "data" / "results" / "figures" / "graphical_toc.pdf",
    REPO / "data" / "results" / "figures" / "graphical_toc.png",
]


def _need_render(src: Path, dst: Path, force: bool) -> bool:
    if force or not dst.is_file():
        return True
    ref_mtime = REF.stat().st_mtime if REF.is_file() else 0
    return src.stat().st_mtime > dst.stat().st_mtime or ref_mtime > dst.stat().st_mtime


def _render_one(src: Path, dst: Path) -> None:
    cmd = [
        "pandoc",
        str(src),
        "-o", str(dst),
        "--standalone",
        "--wrap=none",          # preserve line wrapping from source
    ]
    if REF.is_file():
        cmd += [f"--reference-doc={REF}"]
    print(f"  pandoc {src.name} → {dst.name}", flush=True)
    subprocess.run(cmd, check=True, capture_output=False)


def _copy_toc_images() -> None:
    for src in TOC_SOURCES:
        if src.is_file():
            dst = OUT / src.name
            if not dst.is_file() or src.stat().st_mtime > dst.stat().st_mtime:
                shutil.copy2(src, dst)
                print(f"  copied {src.name} → rendered/")
            else:
                print(f"  skip   {src.name} (up-to-date)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Rebuild all outputs.")
    args = parser.parse_args()

    if shutil.which("pandoc") is None:
        print("ERROR: pandoc not found on PATH.")
        return 1

    if not REF.is_file():
        print(f"WARNING: reference DOCX not found at {REF}")
        print("         Run:  python scripts/build_ijnmbe_reference_docx.py")
        print("         Proceeding without reference template (default pandoc styles).")

    OUT.mkdir(parents=True, exist_ok=True)
    rendered = skipped = errors = 0

    for src_name, dst_name, label in SOURCES:
        src = SRC / src_name
        dst = OUT / dst_name
        if not src.is_file():
            print(f"  MISSING source: {src_name} — skipping {label}")
            errors += 1
            continue
        if not _need_render(src, dst, args.force):
            print(f"  skip   {dst_name} (up-to-date)")
            skipped += 1
            continue
        try:
            _render_one(src, dst)
            rendered += 1
        except subprocess.CalledProcessError as e:
            print(f"  ERROR rendering {src_name}: {e}")
            errors += 1

    _copy_toc_images()

    print(f"\nRendered {rendered} | Skipped {skipped} | Errors {errors}")
    print(f"Output dir: {OUT}")

    if errors:
        print("\nResolve errors before portal upload.")
        return 1

    print("\nSubmission package complete.")
    print("Remaining manual steps before portal upload:")
    print("  1. Mint OSF pre-registration DOI → replace 'TBD at submission'")
    print("  2. Archive dataset on Zenodo → replace reference [22] DOI")
    print("  3. Set cover letter date to actual submission date")
    print("  4. Verify graphical_toc.pdf renders cleanly at 200 px thumbnail")
    print("  5. Upload to Wiley CNM portal at https://authors.wiley.com/journal/CNM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
