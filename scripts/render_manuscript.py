"""Render the AMHP submission package from the markdown sources.

Outputs (under ``docs/publication/rendered/``):
- ``manuscript.docx``        depersonalized body (Editorial Manager: "Manuscript")
- ``manuscript.html``        side-by-side HTML preview for review
- ``author_page.docx``       Title Page file (Editorial Manager: "Title Page")
- ``cover_letter.docx``      cover letter (Editorial Manager: "Cover Letter")
- ``tripod_ai_checklist.docx``  supplementary
- ``suggested_reviewers.docx``  supplementary

AMHP formatting requirements that Pandoc cannot enforce automatically
(double-spacing, ragged-right, upper-right page numbers, superscript
in-text citations) are applied as post-render edits in Word/LibreOffice
before portal upload — see ``docs/publication/render_checklist.md``.

Usage:
    python -m scripts.render_manuscript

Skips files that are already up-to-date (mtime comparison) unless
``--force`` is passed.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PUB = REPO / "docs" / "publication"
OUT = PUB / "rendered"

SOURCES: tuple[tuple[str, str], ...] = (
    ("manuscript.md", "manuscript.docx"),
    ("manuscript.md", "manuscript.html"),
    ("author_page.md", "author_page.docx"),
    ("cover_letter.md", "cover_letter.docx"),
    ("tripod_ai_checklist.md", "tripod_ai_checklist.docx"),
    ("suggested_reviewers.md", "suggested_reviewers.docx"),
    ("references_verification.md", "references_verification.docx"),
)


def _need_render(src: Path, dst: Path, force: bool) -> bool:
    if force or not dst.is_file():
        return True
    return src.stat().st_mtime > dst.stat().st_mtime


def _render_one(src: Path, dst: Path) -> None:
    cmd = ["pandoc", str(src), "-o", str(dst), "--standalone"]
    if dst.suffix == ".html":
        cmd += ["--metadata", f"title={src.stem}", "--toc"]
    print(f"  pandoc {src.name} -> {dst.name}", flush=True)
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-render all outputs.")
    args = parser.parse_args()

    if shutil.which("pandoc") is None:
        print("ERROR: pandoc not found on PATH. Install via your package manager.")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    rendered = 0
    skipped = 0
    for src_name, dst_name in SOURCES:
        src = PUB / src_name
        dst = OUT / dst_name
        if not src.is_file():
            print(f"  skip {src_name}: source missing")
            continue
        if not _need_render(src, dst, args.force):
            skipped += 1
            continue
        _render_one(src, dst)
        rendered += 1

    print(f"\nRendered {rendered}, skipped {skipped} (up-to-date).")
    print(f"Outputs at {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
