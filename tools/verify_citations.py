import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

import requests


REFERENCES_HEADER = "### References (APA 7th)"
HTTP_PATTERN = re.compile(r"https?://\S+")


def read_file_text(file_path: Path) -> str:
	return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_reference_lines_from_enhanced_app(source_text: str) -> List[str]:
	lines = source_text.splitlines()
	ref_start_idx = None
	for idx, line in enumerate(lines):
		if line.strip() == REFERENCES_HEADER:
			ref_start_idx = idx
			break
	if ref_start_idx is None:
		return []
	# The references live in a triple-quoted markdown block; collect until the block ends
	references: List[str] = []
	for idx in range(ref_start_idx + 1, len(lines)):
		line = lines[idx]
		# Stop at the closing triple quotes of the surrounding st.markdown block
		if line.strip().endswith('"""'):
			break
		references.append(line.rstrip())
	return references


def extract_links(text: str) -> List[str]:
	return HTTP_PATTERN.findall(text)


def verify_links_reachable(urls: List[str], timeout_s: float = 10.0) -> List[Tuple[str, int]]:
	results: List[Tuple[str, int]] = []
	for url in urls:
		try:
			resp = requests.head(url, allow_redirects=True, timeout=timeout_s)
			results.append((url, resp.status_code))
		except Exception:
			results.append((url, -1))
	return results


def main() -> int:
	parser = argparse.ArgumentParser(description="Verify citations in enhanced_app.py have DOI/URL and optionally validate reachability.")
	parser.add_argument("--strict", action="store_true", help="Also perform HTTP HEAD requests to ensure links are reachable (2xx/3xx).")
	args = parser.parse_args()

	repo_root = Path(__file__).resolve().parents[1]
	enhanced_app_path = repo_root / "enhanced_app.py"
	if not enhanced_app_path.exists():
		print(f"Error: {enhanced_app_path} not found.")
		return 2

	source_text = read_file_text(enhanced_app_path)
	reference_lines = extract_reference_lines_from_enhanced_app(source_text)
	if not reference_lines:
		print("Warning: No References block found in enhanced_app.py.")
		return 0

	missing_link_lines: List[str] = []
	unreachable_links: List[Tuple[str, int]] = []

	for line in reference_lines:
		trim = line.strip()
		# Skip blank separators inside the block
		if not trim:
			continue
		# Skip the subheader itself if encountered (already handled)
		if trim.startswith("###"):
			continue
		urls = extract_links(trim)
		if not urls:
			missing_link_lines.append(trim)
			continue
		if args.strict:
			for url, status in verify_links_reachable(urls):
				if status < 200 or status >= 400:
					unreachable_links.append((url, status))

	status_code = 0
	if missing_link_lines:
		status_code = 1
		print("Citations missing DOI/URL:")
		for ln in missing_link_lines:
			print(f"  - {ln}")

	if args.strict and unreachable_links:
		status_code = 1
		print("\nLinks not reachable (non-2xx/3xx):")
		for url, code in unreachable_links:
			print(f"  - {url} (status={code})")

	if status_code == 0:
		print("Citations OK: all entries include a DOI or URL" + (" and are reachable" if args.strict else ""))
	return status_code


if __name__ == "__main__":
	sys.exit(main())
