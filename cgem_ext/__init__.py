"""CGEM extension layer.

This package wraps the validated FAA Civil Aerospace Medicine Institute
G-Effects Model (CGEM, AAM-631) with an ML augmentation layer:

- ``cgem_ext.data``         dataset generation + train/val/test splits
- ``cgem_ext.ood``          out-of-distribution detection (Mahalanobis + conformal)
- ``cgem_ext.surrogate``    fast ML emulator with Mondrian conformal CIs
- ``cgem_ext.sensitivity``  global sensitivity analysis (Sobol, Morris)
- ``cgem_ext.api``          FastAPI service exposing the above

The validated Fortran physiology core (``src/cgem.f``) and its subprocess
wrapper (``cgem_wrapper.py``) are *not* modified by this package. Anything
inside ``cgem_ext`` is additive; anything outside it is preserved as-is so
downstream consumers (notably ``pulse-sim``'s CGEM bridge) keep working
through the same import paths they already use.

The two upstream symbols that pulse-sim and other consumers depend on
are re-exported here so callers can use one stable import path:

    >>> from cgem_ext import run_cgem_for_profile, PilotConfig

These re-exports are covered by ``tests/test_contract.py`` and any change
to their shape will break CI.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

# Make sure the repository root (containing cgem_wrapper.py and the
# compiled cgem binary) is importable regardless of how the package is
# invoked. cgem_ext lives at <repo_root>/cgem_ext/ so the parent of this
# file is the repo root.
_REPO_ROOT = _Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

from cgem_wrapper import (  # noqa: E402  (path injected above)
    PilotConfig,
    run_cgem_for_profile,
)

__all__ = ["PilotConfig", "run_cgem_for_profile", "REPO_ROOT", "__version__"]

REPO_ROOT: _Path = _REPO_ROOT
__version__ = "0.1.0"
