"""FastAPI service tests using FastAPI's TestClient.

Non-binary endpoints use deterministic injected state and do not train
models. Only tests that execute the actual Fortran binary are gated by
``needs_cgem_binary``.

The test client also enforces the wire contract that pulse-sim
depends on: ``test_run_cgem_response_matches_pulse_sim_schema`` checks
that the v2.2.0 ``CGEMRun`` JSON keys are present and well-typed.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from cgem_ext.api.state import AppState
from cgem_ext.ood import ConformalAbstention, MahalanobisOOD
from cgem_ext.surrogate import (
    TARGETS,
    MondrianSplitConformal,
    TwoStageXGBSurrogate,
    XGBSurrogate,
)
from cgem_wrapper import CGEMResult


class _FakeModel:
    def predict(self, df):
        return np.full(len(df), 4.0)

    def predict_event_probability(self, df):
        return np.full(len(df), 0.25)


class _FakeConformal:
    def predict_interval(self, *, test_predictions, test_strata):
        return test_predictions - 1.0, test_predictions + 1.0


class _FakeOOD:
    def score(self, df):
        return np.full(len(df), 0.5)


class _FakeAbstainer:
    def is_in_envelope(self, scores):
        return np.ones(len(scores), dtype=bool)


def _fake_state() -> AppState:
    features = [
        "g_peak_abs",
        "dgdt_max_g_per_s",
        "profile_duration_s",
        "dehydration_level",
        "g_tolerance_multiplier",
        "gsuit_max_psi",
        "gsuit_coverage_fraction",
        "agsm_effectiveness",
        "pbg_max_mmhg",
    ]
    sensitivity = pd.DataFrame(
        {
            "target": ["hlap_min"] * len(features),
            "censored": [False] * len(features),
            "feature": features,
            "S1": np.linspace(0.1, 0.9, len(features)),
            "S1_conf": [0.01] * len(features),
            "ST": [0.1, 0.2, 0.3, 1.0, 0.4, 0.5, 0.6, 0.7, 0.8],
            "ST_conf": [0.02] * len(features),
        }
    )
    state = AppState(
        package_version="test-version",
        dataset_path=Path("fixture.parquet"),
        cgem_binary_sha256="abc123",
        master_seed=42,
        surrogates=cast(
            dict[str, XGBSurrogate | TwoStageXGBSurrogate],
            {spec.name: _FakeModel() for spec in TARGETS},
        ),
        conformals=cast(
            dict[str, MondrianSplitConformal],
            {spec.name: _FakeConformal() for spec in TARGETS},
        ),
        ood_detector=cast(MahalanobisOOD, _FakeOOD()),
        ood_abstainer=cast(ConformalAbstention, _FakeAbstainer()),
        sensitivity_df=sensitivity,
    )
    return state


def test_non_binary_endpoints_use_injected_state(monkeypatch) -> None:
    from cgem_ext.api.main import create_app

    def fail_build():
        raise AssertionError("AppState.build must not run")

    monkeypatch.setattr(AppState, "build", fail_build)
    with TestClient(create_app(state_factory=_fake_state)) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/version").status_code == 200
        body = {"maneuver": {"maneuver": "high_g_turn"}}
        assert client.post("/predict", json=body).status_code == 200
        assert client.post("/sweep", json={"inputs": [body]}).status_code == 200
        assert client.get("/sensitivity/hlap_min").status_code == 200

# ──────────────────────────────────────────────────────────────────────
# Session-wide TestClient
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def api_client(repo_root) -> Iterator[TestClient]:
    """Use deterministic inference doubles; no binary or training required."""
    from cgem_ext.api.main import create_app

    app = create_app(state_factory=_fake_state)
    with TestClient(app) as client:
        yield client


# ──────────────────────────────────────────────────────────────────────
# Liveness + meta
# ──────────────────────────────────────────────────────────────────────


def test_root(api_client):
    r = api_client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"].startswith("CGEM")
    assert body["docs"] == "/docs"


def test_healthz(api_client):
    r = api_client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_version(api_client):
    r = api_client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert body["package_version"]
    assert len(body["targets"]) == 5
    assert body["dataset_master_seed"] == 42


# ──────────────────────────────────────────────────────────────────────
# /predict
# ──────────────────────────────────────────────────────────────────────


def test_predict_with_named_maneuver(api_client):
    body = {
        "maneuver": {"maneuver": "high_g_turn"},
        "pilot": {"who_profile": 2, "countermeasures_label": "agsm", "agsm_effectiveness": 0.6},
    }
    r = api_client.post("/predict", json=body)
    assert r.status_code == 200, r.text
    d = r.json()
    assert {t["target"] for t in d["targets"]} == {
        "time_to_greyout_s",
        "time_to_blackout_s",
        "time_to_gloc_s",
        "hlap_min",
        "c_bank_min",
    }
    # Shape contract on every target output
    for t in d["targets"]:
        assert isinstance(t["point"], float)
        if t["censored"]:
            assert 0.0 <= t["event_probability"] <= 1.0
            assert isinstance(t["expected_time_s"], float)
        # Conformal interval is on the same scale as `point`
        if t["lo"] is not None and t["hi"] is not None:
            assert t["lo"] <= t["hi"]
    # OOD reporting present
    assert "ood" in d
    assert "ood_score" in d
    assert d["source"] == "surrogate"
    assert d["resolved_maneuver"] == "high_g_turn"
    assert d["maneuver_category"] != "unregistered"
    assert d["calibration_scope"] == "category"


def test_predict_with_inline_descriptors(api_client):
    body = {
        "maneuver": {
            "g_peak_abs": 7.0,
            "dgdt_max_g_per_s": 5.0,
            "profile_duration_s": 12.0,
        },
        "pilot": {"who_profile": 4, "countermeasures_label": "suit_agsm",
                  "gsuit_max_psi": 10.0, "agsm_effectiveness": 0.8, "pbg_max_mmhg": 15.0},
    }
    r = api_client.post("/predict", json=body)
    assert r.status_code == 200


def test_predict_rejects_underspecified_descriptors(api_client):
    body = {
        "maneuver": {"g_peak_abs": 7.0},  # missing dgdt + duration
        "pilot": {"who_profile": 2},
    }
    r = api_client.post("/predict", json=body)
    assert r.status_code == 422


# ──────────────────────────────────────────────────────────────────────
# /sweep
# ──────────────────────────────────────────────────────────────────────


def test_sweep_batched(api_client):
    body = {
        "inputs": [
            {"maneuver": {"maneuver": "high_g_turn"}, "pilot": {"who_profile": 2}},
            {"maneuver": {"maneuver": "hammerhead"}, "pilot": {"who_profile": 4}},
            {"maneuver": {"maneuver": "outside_360"}, "pilot": {"who_profile": 6}},
        ]
    }
    r = api_client.post("/sweep", json=body)
    assert r.status_code == 200, r.text
    d = r.json()
    assert len(d["results"]) == 3
    for res in d["results"]:
        assert len(res["targets"]) == 5


# ──────────────────────────────────────────────────────────────────────
# /sensitivity
# ──────────────────────────────────────────────────────────────────────


def test_sensitivity_returns_per_target_indices(api_client):
    r = api_client.get("/sensitivity/hlap_min")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["target"] == "hlap_min"
    assert len(d["indices"]) == 9  # 9 continuous features
    # Top-ST driver should be dehydration_level on hlap_min
    top = max(d["indices"], key=lambda x: x["ST"])
    assert top["feature"] == "dehydration_level"


def test_sensitivity_unknown_target_returns_404(api_client):
    r = api_client.get("/sensitivity/no_such_target")
    assert r.status_code == 404


def _fake_cgem_result() -> CGEMResult:
    return CGEMResult(
        time_to_greyout_s=None,
        time_to_blackout_s=None,
        time_to_gloc_s=None,
        times_s=[0.0, 1.0],
        g_values=[1.0, 2.0],
        geff_values=[1.0, 1.8],
    )


def test_run_cgem_cleanup(api_client, monkeypatch, tmp_path) -> None:
    import cgem_wrapper

    run_dir = tmp_path / "authoritative-run"
    run_dir.mkdir()
    (run_dir / "sentinel").write_text("temporary")
    monkeypatch.setattr(
        cgem_wrapper,
        "run_cgem_for_profile",
        lambda maneuver, config: (_fake_cgem_result(), run_dir),
    )

    response = api_client.post(
        "/run-cgem",
        json={"maneuver": "high_g_turn", "pilot": {"who_profile": 2}},
    )

    assert response.status_code == 200, response.text
    assert set(response.json()) == {
        "maneuver",
        "pilot_profile",
        "duration_s",
        "time_to_greyout_s",
        "time_to_blackout_s",
        "time_to_gloc_s",
        "data",
    }
    assert not run_dir.exists()


def test_run_cgem_uses_threadpool(api_client, monkeypatch, tmp_path) -> None:
    import cgem_ext.api.main as api_main
    import cgem_wrapper

    called = False
    run_dir = tmp_path / "threaded-run"
    run_dir.mkdir()

    async def fake_threadpool(function, *args, **kwargs):
        nonlocal called
        called = True
        return function(*args, **kwargs)

    monkeypatch.setattr(api_main, "run_in_threadpool", fake_threadpool, raising=False)
    monkeypatch.setattr(
        cgem_wrapper,
        "run_cgem_for_profile",
        lambda maneuver, config: (_fake_cgem_result(), run_dir),
    )

    response = api_client.post(
        "/run-cgem",
        json={"maneuver": "high_g_turn", "pilot": {"who_profile": 2}},
    )

    assert response.status_code == 200, response.text
    assert called


def test_run_cgem_timeout_has_stable_504(api_client, monkeypatch) -> None:
    import cgem_wrapper

    def time_out(maneuver, config):
        raise subprocess.TimeoutExpired(cmd="cgem", timeout=30)

    monkeypatch.setattr(cgem_wrapper, "run_cgem_for_profile", time_out)
    response = api_client.post(
        "/run-cgem",
        json={"maneuver": "high_g_turn", "pilot": {"who_profile": 2}},
    )

    assert response.status_code == 504
    assert response.json() == {"detail": "cgem execution timed out"}


def test_run_cgem_failure_hides_internal_details(api_client, monkeypatch) -> None:
    import cgem_wrapper

    def fail(maneuver, config):
        raise RuntimeError("sensitive path: /tmp/cgem_run_secret")

    monkeypatch.setattr(cgem_wrapper, "run_cgem_for_profile", fail)
    response = api_client.post(
        "/run-cgem",
        json={"maneuver": "high_g_turn", "pilot": {"who_profile": 2}},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "cgem execution failed"}


# ──────────────────────────────────────────────────────────────────────
# /run-cgem — pulse-sim contract
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.needs_cgem_binary
def test_run_cgem_executes(api_client):
    r = api_client.post(
        "/run-cgem",
        json={"maneuver": "high_g_turn", "pilot": {"who_profile": 2}},
    )
    assert r.status_code == 200, r.text


@pytest.mark.needs_cgem_binary
def test_run_cgem_response_matches_pulse_sim_schema(api_client):
    """The wire contract pulse-sim's `cgem_bridge.load_cgem_json` reads.

    Failing this breaks the downstream consumer; CI must keep it green.
    """
    r = api_client.post(
        "/run-cgem",
        json={"maneuver": "high_g_turn", "pilot": {"who_profile": 2}},
    )
    assert r.status_code == 200, r.text
    body = r.json()

    # Top-level keys
    for key in ("maneuver", "pilot_profile", "duration_s",
                "time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s",
                "data"):
        assert key in body, f"missing top-level key {key!r}"

    # data sub-object: every column the bridge maps into a DataFrame
    data = body["data"]
    for col in ("Time(s)", "G", "G_eff", "HLAP(mmHg)",
                "F_con(dl/min)", "F_vis(dl/min)", "F_bo(dl/min)",
                "c_bank(s)", "bo_bank(s)",
                "Conscious", "Greyout", "Blackout"):
        assert col in data, f"missing data column {col!r}"
        assert isinstance(data[col], list), f"{col!r} should be a list"

    # All time-series columns aligned on length
    n = len(data["Time(s)"])
    for col, values in data.items():
        assert len(values) == n, f"{col!r} length {len(values)} != Time(s) length {n}"
