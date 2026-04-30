"""FastAPI service tests using FastAPI's TestClient.

The lifespan context trains five surrogates + an OOD detector + per-
target conformal layers at app startup, so each test session pays a
single ~30-second warm-up cost (amortised across all tests in this
file). Tests that need the actual Fortran binary (``/run-cgem``) are
gated by ``needs_cgem_binary``.

The test client also enforces the wire contract that pulse-sim
depends on: ``test_run_cgem_response_matches_pulse_sim_schema`` checks
that the v2.2.0 ``CGEMRun`` JSON keys are present and well-typed.
"""

from __future__ import annotations

import warnings
from typing import Iterator

import pytest
from fastapi.testclient import TestClient


# ──────────────────────────────────────────────────────────────────────
# Session-wide TestClient
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def api_client(repo_root) -> Iterator[TestClient]:
    """Train models once, yield a TestClient for the whole module."""
    parquet = repo_root / "data" / "datasets" / "cgem_synthetic_v1.parquet"
    if not parquet.is_file():
        pytest.skip("cgem_synthetic_v1.parquet not present")

    warnings.filterwarnings("ignore")
    from cgem_ext.api.main import create_app

    app = create_app()
    with TestClient(app) as client:
        yield client


# ──────────────────────────────────────────────────────────────────────
# Liveness + meta
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.needs_cgem_binary
def test_root(api_client):
    r = api_client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"].startswith("CGEM")
    assert body["docs"] == "/docs"


@pytest.mark.needs_cgem_binary
def test_healthz(api_client):
    r = api_client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.needs_cgem_binary
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


@pytest.mark.needs_cgem_binary
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


@pytest.mark.needs_cgem_binary
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


@pytest.mark.needs_cgem_binary
def test_predict_rejects_underspecified_descriptors(api_client):
    body = {
        "maneuver": {"g_peak_abs": 7.0},  # missing dgdt + duration
        "pilot": {"who_profile": 2},
    }
    r = api_client.post("/predict", json=body)
    assert r.status_code == 400


# ──────────────────────────────────────────────────────────────────────
# /sweep
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.needs_cgem_binary
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


@pytest.mark.needs_cgem_binary
def test_sensitivity_returns_per_target_indices(api_client):
    r = api_client.get("/sensitivity/hlap_min")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["target"] == "hlap_min"
    assert len(d["indices"]) == 9  # 9 continuous features
    # Top-ST driver should be dehydration_level on hlap_min
    top = max(d["indices"], key=lambda x: x["ST"])
    assert top["feature"] == "dehydration_level"


@pytest.mark.needs_cgem_binary
def test_sensitivity_unknown_target_returns_404(api_client):
    r = api_client.get("/sensitivity/no_such_target")
    assert r.status_code == 404


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
