"""Export the FastAPI OpenAPI spec to ``docs/api/openapi.json``.

Usage:
    python -m scripts.export_openapi

The output is consumed by the React/TypeScript frontend codegen
(``npx openapi-typescript docs/api/openapi.json -o frontend/src/services/types.ts``)
so the TS types stay in sync with the Pydantic schemas.

This script does NOT run the lifespan startup (which would train the
surrogates). It only constructs the FastAPI app to extract the
schema, which is fast (<2 s).
"""

from __future__ import annotations

import json
from pathlib import Path

from cgem_ext.api.main import create_app


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    output = repo_root / "docs" / "api" / "openapi.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    app = create_app()
    spec = app.openapi()
    output.write_text(json.dumps(spec, indent=2, sort_keys=True))
    print(f"Wrote {output} ({output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
