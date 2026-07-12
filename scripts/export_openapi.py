"""Export the FastAPI OpenAPI spec to ``docs/api/openapi.json``.

Usage:
    python -m scripts.export_openapi

The output is consumed by the React/TypeScript frontend codegen
(``npm run generate:types --prefix frontend``) so generated wire contracts stay
separate from handwritten UI-facing types.
so the TS types stay in sync with the Pydantic schemas.

This script does NOT run the lifespan startup (which would train the
surrogates). It only constructs the FastAPI app to extract the
schema, which is fast (<2 s).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cgem_ext.api.main import create_app  # noqa: E402


def main() -> int:
    output = REPO_ROOT / "docs" / "api" / "openapi.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    app = create_app()
    spec = app.openapi()
    output.write_text(json.dumps(spec, indent=2, sort_keys=True))
    print(f"Wrote {output} ({output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
