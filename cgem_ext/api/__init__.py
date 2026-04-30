"""FastAPI service exposing the CGEM ML extension layer (Phase 5).

Public entry points:

    from cgem_ext.api.main import app, create_app

Or, for a uvicorn server:

    uvicorn cgem_ext.api.main:app

Endpoints (full schema in ``docs/api/openapi.json``):

    GET  /                       landing payload
    GET  /healthz                liveness
    GET  /version                package + binary SHA + dataset metadata
    GET  /sensitivity/{target}   precomputed Sobol indices
    POST /predict                surrogate prediction + conformal CI + OOD flag
    POST /sweep                  batched predictions
    POST /run-cgem               authoritative Fortran subprocess; mirrors
                                 pulse-sim CGEMRun JSON shape

See ``cgem_ext.api.schemas`` for the wire contract and
``cgem_ext.api.state`` for the lifespan-managed model store.
"""

from cgem_ext.api.main import app, create_app
from cgem_ext.api.schemas import (
    CGEMRunResponse,
    PredictionRequest,
    PredictionResponse,
    RunCGEMRequest,
    SweepRequest,
    SweepResponse,
)
from cgem_ext.api.state import AppState

__all__ = [
    "AppState",
    "CGEMRunResponse",
    "PredictionRequest",
    "PredictionResponse",
    "RunCGEMRequest",
    "SweepRequest",
    "SweepResponse",
    "app",
    "create_app",
]
