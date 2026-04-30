"""Shared fixtures and import-path setup for the test suite.

Adds the repo root to ``sys.path`` so tests can import ``cgem_wrapper``,
``aerobatic_profiles``, and the new ``cgem_ext`` package without depending
on the package being installed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def cgem_binary_available(repo_root: Path) -> bool:
    """True when the compiled CGEM binary is present and executable.

    Tests that need to actually run a simulation should depend on this and
    skip when False so CI on machines without the binary still passes the
    rest of the suite.
    """
    candidates = ["cgem", "cgem.exe"]
    for name in candidates:
        path = repo_root / name
        if path.is_file() and (os.access(path, os.X_OK) or name.endswith(".exe")):
            return True
    return False
