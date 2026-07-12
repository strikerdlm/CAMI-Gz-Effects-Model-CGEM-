"""FastAPI service exposing the CGEM ML extension layer.

Endpoints
---------

GET  /              — landing payload pointing at /docs
GET  /healthz       — liveness probe
GET  /version       — package version, binary SHA, dataset metadata
GET  /sensitivity/{target}
                    — precomputed Sobol indices loaded from
                      data/results/sensitivity/sobol_first_total.csv
POST /predict       — one-row prediction with conformal interval + OOD flag
POST /sweep         — batched predictions (same surrogate path)
POST /run-cgem      — authoritative path: invokes the Fortran binary
                      and returns the v2.2.0 CGEMRun JSON shape

The CORS layer is wide-open by default for local frontend
development; production deployments should narrow ``allow_origins``.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from cgem_ext.api.inference import build_inference_row
from cgem_ext.api.schemas import (
    CGEMRunData,
    CGEMRunResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    RunCGEMRequest,
    SensitivityResponse,
    SobolFeatureIndex,
    SweepRequest,
    SweepResponse,
    TargetPrediction,
    VersionResponse,
)
from cgem_ext.api.state import AppState
from cgem_ext.surrogate import TARGETS

# ── Lifespan: build app state once on startup ────────────────────────


def _lifespan(state_factory: Callable[[], AppState]):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.cgem = state_factory()
        yield

    return lifespan


def create_app(state_factory: Callable[[], AppState] = AppState.build) -> FastAPI:
    app = FastAPI(
        title="CGEM ML Extension API",
        version="0.1.0",
        description=(
            "ML-augmented framework for CAMI G-Effects Model: surrogate "
            "emulator, OOD detection, conformal prediction intervals, "
            "global sensitivity analysis, and authoritative subprocess "
            "path. The Fortran physiology core is unchanged; this API "
            "is additive."
        ),
        lifespan=_lifespan(state_factory),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    try:
        max_runs = int(os.getenv("CGEM_MAX_CONCURRENT_RUNS", "2"))
    except ValueError:
        max_runs = 2
    app.state.cgem_run_semaphore = asyncio.Semaphore(max(1, max_runs))
    _register_routes(app)
    return app


# ── Helpers ──────────────────────────────────────────────────────────


def _state(request: Request) -> AppState:
    state: AppState = request.app.state.cgem
    return state


def _predict_one(state: AppState, req: PredictionRequest) -> PredictionResponse:
    df, resolved = build_inference_row(req)
    target_outputs: list[TargetPrediction] = []

    for spec in TARGETS:
        model = state.surrogates[spec.name]
        cp = state.conformals.get(spec.name)
        if spec.censored:
            event_p = float(model.predict_event_probability(df)[0])  # type: ignore[union-attr]
            cond_t = float(model.predict(df)[0])
            # `point` is the conditional time so lo/hi are on the same scale.
            # The frontend composes `expected_time_s` = event_p * cond_t.
            lo = hi = None
            if cp is not None:
                lo_arr, hi_arr = cp.predict_interval(
                    test_predictions=np.array([cond_t]),
                    test_strata=np.array([df["maneuver_category"].iloc[0]]),
                )
                lo, hi = float(lo_arr[0]), float(hi_arr[0])
            target_outputs.append(
                TargetPrediction(
                    target=spec.name,
                    censored=True,
                    point=cond_t,
                    lo=lo,
                    hi=hi,
                    event_probability=event_p,
                    expected_time_s=float(event_p * cond_t),
                )
            )
        else:
            point = float(model.predict(df)[0])
            lo = hi = None
            if cp is not None:
                lo_arr, hi_arr = cp.predict_interval(
                    test_predictions=np.array([point]),
                    test_strata=np.array([df["maneuver_category"].iloc[0]]),
                )
                lo, hi = float(lo_arr[0]), float(hi_arr[0])
            target_outputs.append(
                TargetPrediction(
                    target=spec.name,
                    censored=False,
                    point=point,
                    lo=lo,
                    hi=hi,
                )
            )

    ood_score = float(state.ood_detector.score(df)[0]) if state.ood_detector is not None else 0.0
    in_envelope = (
        bool(state.ood_abstainer.is_in_envelope(np.array([ood_score]))[0])
        if state.ood_abstainer is not None
        else True
    )

    return PredictionResponse(
        targets=target_outputs,
        ood=not in_envelope,
        ood_score=ood_score,
        in_envelope=in_envelope,
        model_version=state.package_version,
        cgem_binary_sha256=state.cgem_binary_sha256,
        resolved_maneuver=resolved.maneuver_id,
        maneuver_category=resolved.category,
        calibration_scope=resolved.calibration_scope,
        source="surrogate",
    )


# ── Route registration ──────────────────────────────────────────────


def _register_routes(app: FastAPI) -> None:

    @app.get("/", include_in_schema=False)
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "service": "CGEM ML Extension API",
                "docs": "/docs",
                "openapi": "/openapi.json",
                "health": "/healthz",
            }
        )

    @app.get("/healthz", response_model=HealthResponse, tags=["meta"])
    async def healthz(request: Request) -> HealthResponse:
        try:
            _ = _state(request)
            return HealthResponse(status="ok")
        except Exception as exc:
            return HealthResponse(status="degraded", detail=str(exc))

    @app.get("/version", response_model=VersionResponse, tags=["meta"])
    async def version(request: Request) -> VersionResponse:
        state = _state(request)
        return VersionResponse(
            package_version=state.package_version,
            cgem_binary_sha256=state.cgem_binary_sha256,
            dataset_name=state.dataset_path.name,
            dataset_master_seed=state.master_seed,
            targets=[t.name for t in TARGETS],
        )

    @app.get(
        "/sensitivity/{target}",
        response_model=SensitivityResponse,
        tags=["analysis"],
    )
    async def sensitivity(target: str, request: Request) -> SensitivityResponse:
        state = _state(request)
        if state.sensitivity_df is None:
            raise HTTPException(
                status_code=404,
                detail="sensitivity CSV not present; run scripts/run_sensitivity.py",
            )
        spec = next((t for t in TARGETS if t.name == target), None)
        if spec is None:
            raise HTTPException(status_code=404, detail=f"unknown target {target!r}")
        sub = state.sensitivity_df[state.sensitivity_df["target"] == target]
        if sub.empty:
            raise HTTPException(status_code=404, detail=f"no rows for {target!r}")
        manifest = state.sensitivity_manifest or {}
        return SensitivityResponse(
            target=target,
            censored=spec.censored,
            fixed_who_profile=str(manifest.get("fixed_who_profile", "custom")),
            sobol_n_base=int(manifest.get("sobol_n_base", 0)),
            indices=[
                SobolFeatureIndex(
                    feature=str(r.feature),
                    S1=float(r.S1),
                    S1_conf=float(r.S1_conf),
                    ST=float(r.ST),
                    ST_conf=float(r.ST_conf),
                )
                for r in sub.itertuples(index=False)
            ],
        )

    @app.post("/predict", response_model=PredictionResponse, tags=["inference"])
    async def predict(req: PredictionRequest, request: Request) -> PredictionResponse:
        state = _state(request)
        return _predict_one(state, req)

    @app.post("/sweep", response_model=SweepResponse, tags=["inference"])
    async def sweep(req: SweepRequest, request: Request) -> SweepResponse:
        state = _state(request)
        results = [_predict_one(state, r) for r in req.inputs]
        return SweepResponse(results=results)

    @app.post("/run-cgem", response_model=CGEMRunResponse, tags=["inference"])
    async def run_cgem(req: RunCGEMRequest, request: Request) -> CGEMRunResponse:
        # Defer the import so the endpoint module loads cleanly even
        # without a Fortran binary present (e.g. in CI).
        from cgem_wrapper import PilotConfig, run_cgem_for_profile

        cfg_kwargs: dict = {
            "who_profile": req.pilot.who_profile,
            "dehydration_level": req.pilot.dehydration_level,
            "gsuit_max_psi": req.pilot.gsuit_max_psi,
            "gsuit_coverage_fraction": req.pilot.gsuit_coverage_fraction,
            "agsm_effectiveness": req.pilot.agsm_effectiveness,
            "pbg_max_mmhg": req.pilot.pbg_max_mmhg,
        }
        if req.pilot.who_profile is None:
            cfg_kwargs["g_tolerance_multiplier"] = req.pilot.g_tolerance_multiplier
        run_dir = None
        try:
            cfg = PilotConfig(**cfg_kwargs)
            async with request.app.state.cgem_run_semaphore:
                result, run_dir = await run_in_threadpool(
                    run_cgem_for_profile, req.maneuver, cfg
                )
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail="cgem execution timed out") from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail="cgem execution failed") from exc

        try:
            # Build the protected v2.2.0 CGEMRun JSON shape.
            n = len(result.times_s) if result.times_s else 0

            def _ts(values: list[float] | None) -> list[float]:
                return [float(v) for v in (values or [0.0] * n)][:n] if n else []

            def _flag(values: list[int] | None) -> list[int]:
                return [int(v) for v in (values or [0] * n)][:n] if n else []

            data = CGEMRunData(
                **{  # type: ignore[arg-type]
                    "Time(s)": _ts(result.times_s),
                    "G": _ts(result.g_values),
                    "G_eff": _ts(result.geff_values),
                    "HLAP(mmHg)": _ts(result.hlap_values),
                    "F_con(dl/min)": _ts(result.f_con_values),
                    "F_vis(dl/min)": _ts(result.f_vis_values),
                    "F_bo(dl/min)": _ts(result.f_bo_values),
                    "c_bank(s)": _ts(result.c_bank_values),
                    "bo_bank(s)": _ts(result.bo_bank_values),
                    "Conscious": _flag(result.flags_n2),
                    "Greyout": _flag(result.flags_ne2),
                    "Blackout": _flag(result.flags_non2),
                }
            )
            duration = (
                float(max(result.times_s))
                if (result.times_s and len(result.times_s))
                else 0.0
            )
            return CGEMRunResponse(
                maneuver=req.maneuver,
                pilot_profile=(
                    f"who_profile={req.pilot.who_profile}"
                    if req.pilot.who_profile is not None
                    else "custom"
                ),
                duration_s=duration,
                time_to_greyout_s=result.time_to_greyout_s,
                time_to_blackout_s=result.time_to_blackout_s,
                time_to_gloc_s=result.time_to_gloc_s,
                data=data,
            )
        finally:
            if run_dir is not None:
                shutil.rmtree(run_dir, ignore_errors=True)


# Module-level app for `uvicorn cgem_ext.api.main:app`
app = create_app()


__all__ = ["app", "create_app"]
