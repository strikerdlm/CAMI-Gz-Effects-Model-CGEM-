"""Additive API must keep flight inspectable if native physiology fails."""

from fastapi.testclient import TestClient

from cgem_ext.api.main import create_app


def test_flight_api_unavailable_is_explicit_and_flight_remains_usable(monkeypatch):
    import cgem_wrapper

    def missing():
        raise FileNotFoundError("test binary unavailable")

    monkeypatch.setattr(cgem_wrapper, "_resolve_cgem_executable", missing)
    client = TestClient(create_app())
    response = client.post("/simulate-flight", json={"scenario": "aileron_roll"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert len(data["frames"]) > 500
    assert data["physiology"]["status"] == "unavailable"
    assert "test binary unavailable" in data["physiology"]["reason"]
    assert data["physiology"]["result"] is None
    assert len(data["provenance"]["trace_sha256"]) == 64


def test_flight_invalid_initial_setup_returns_422():
    client = TestClient(create_app())
    for fields in [
        {"entry_ias_kts": 40},
        {"loading": "dual", "intensity_g": 9},
        {"scenario": "fake"},
        {"altitude_ft": -5},
        {"entry_ias_kts": 200},
    ]:
        response = client.post("/simulate-flight", json={"scenario": "aileron_roll", **fields})
        assert response.status_code == 422, response.text


def test_flight_schema_imports_before_api_main():
    # A fresh interpreter catches the package initialization cycle hidden when
    # earlier tests happen to import api.main first.
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from cgem_ext.flight.schemas import FlightRequest; "
            "from cgem_ext.api import app, create_app; "
            'assert FlightRequest(scenario="loop").intensity_g == 4; '
            "assert app.title == create_app().title",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
