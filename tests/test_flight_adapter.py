"""Native CGEM clock, flags and ramp reconstruction regression coverage."""

import numpy as np
import pytest


def row(t, flags=(0, 0, 0)):
    return f"{t} 2 1.9 7.1 41 31 21 5.04 120 {flags[0]} {flags[1]} {flags[2]}"


def test_continuous_ramps_preserve_exact_duration_and_values():
    from cgem_ext.flight.adapter import trace_to_ramps

    ramps = trace_to_ramps([0.0, 0.01, 0.03, 1.0], [1.0, 1.1, 0.9, -1.0])
    assert sum(ms for _, ms in ramps) == 1000
    assert [ms for _, ms in ramps] == [10, 20, 970]
    reconstructed = 1 + np.cumsum([rate * ms / 1000 for rate, ms in ramps])
    np.testing.assert_allclose(reconstructed, [1.1, 0.9, -1.0], atol=1e-12)


@pytest.mark.parametrize(
    "t,g", [([0, 0.0015], [1, 2]), ([0, 0.01], [0, 1]), ([0, 0], [1, 1]), ([0, 121], [1, 1])]
)
def test_invalid_trace_rejected(t, g):
    from cgem_ext.flight.adapter import trace_to_ramps

    with pytest.raises(ValueError):
        trace_to_ramps(t, g)


def test_mixed_timestamp_cadence_early_event_and_recovery(tmp_path):
    from cgem_ext.flight.adapter import parse_output

    path = tmp_path / "out"
    path.write_text(
        "\n".join([row(5, (0, 1, 0)), row(1, (0, 1, 0)), row(1000, (0, 2, 0)), row(2, (0, 2, 0))])
    )
    result = parse_output(path, "test", "custom", 2.0)
    assert result.data.Time_s == [0.005, 0.999, 1.0, 1.999]
    assert result.time_to_greyout_s == 0.005
    assert result.data.Greyout == [1, 1, 2, 2]
    assert result.data.F_vis_dl_per_min == [31] * 4
    assert result.data.F_bo_dl_per_min == [21] * 4


def test_periodic_rows_after_100_seconds_are_seconds(tmp_path):
    from cgem_ext.flight.adapter import parse_output

    path = tmp_path / "out"
    path.write_text("\n".join(row(i) for i in range(1, 121)))
    result = parse_output(path, "long", "custom", 120.0)
    assert result.data.Time_s[-1] == 119.999
    assert result.time_to_gloc_s is None


def test_later_transition_replaces_duplicate_time(tmp_path):
    from cgem_ext.flight.adapter import parse_output

    path = tmp_path / "out"
    path.write_text("\n".join([row(999, (1, 0, 0)), row(1, (1, 0, 0)), row(999, (1, 1, 0))]))
    result = parse_output(path, "test", "custom", 1.0)
    assert result.data.Time_s == [0.999]
    assert result.data.Greyout == [1]
    assert result.time_to_gloc_s == 0.999
    assert result.time_to_greyout_s == 0.999


def test_malformed_physiology_is_not_zero_filled(tmp_path):
    from cgem_ext.flight.adapter import parse_output

    path = tmp_path / "out"
    path.write_text("CGEM header only")
    with pytest.raises(ValueError):
        parse_output(path, "test", "custom", 1.0)


@pytest.mark.needs_cgem_binary
def test_real_binary_generated_ramps_and_native_clock(cgem_binary_available):
    if not cgem_binary_available:
        pytest.skip("CGEM binary unavailable")
    from cgem_ext.api.schemas import PilotConfigRequest
    from cgem_ext.flight.adapter import run_trace

    result = run_trace([0, 2, 10, 12, 20], [1, 6, 6, 1, 1], PilotConfigRequest(), "test")
    assert result.status == "available", result.reason
    assert result.binary_sha256 and len(result.binary_sha256) == 64
    data = result.result.data
    assert data.Time_s[0] > 0
    expected = np.interp(data.Time_s, [0, 2, 10, 12, 20], [1, 6, 6, 1, 1])
    np.testing.assert_allclose(data.G, expected, atol=0.003)
    assert result.result.time_to_greyout_s is not None


def test_truncated_native_cadence_is_unavailable(tmp_path):
    from cgem_ext.flight.adapter import parse_output

    path = tmp_path / "out"
    path.write_text(row(1))
    with pytest.raises(ValueError, match="periodic"):
        parse_output(path, "test", "custom", 2.0)


def test_subprocess_failure_cleans_run_directory(monkeypatch, tmp_path):
    import subprocess
    from pathlib import Path

    from cgem_ext.api.schemas import PilotConfigRequest
    from cgem_ext.flight.adapter import run_trace

    paths = []

    def timeout(*args, **kwargs):
        root = Path(kwargs["cwd"])
        paths.append(root)
        assert (root / "gloc_inp.dat").is_file()
        assert (root / "flight.egp").is_file()
        assert kwargs["timeout"] <= 20
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timeout)
    result = run_trace([0, 1], [1, 2], PilotConfigRequest(), "test")
    assert result.status == "unavailable"
    assert "TimeoutExpired" in result.reason
    assert len(paths) == 1 and not paths[0].exists()


@pytest.mark.needs_cgem_binary
def test_who_preset_honors_agsm_in_native_generated_trace(cgem_binary_available):
    if not cgem_binary_available:
        pytest.skip("CGEM binary unavailable")
    from cgem_ext.api.schemas import PilotConfigRequest
    from cgem_ext.flight.adapter import run_trace

    times, gz = [0.0, 2.0, 10.0, 12.0, 20.0], [1.0, 6.0, 6.0, 1.0, 1.0]
    baseline = run_trace(
        times, gz, PilotConfigRequest(who_profile=2, agsm_effectiveness=0.0), "test"
    )
    protected = run_trace(
        times, gz, PilotConfigRequest(who_profile=2, agsm_effectiveness=0.5), "test"
    )
    assert baseline.status == protected.status == "available"
    assert baseline.result is not None and protected.result is not None
    base_data, protected_data = baseline.result.data, protected.result.data
    # Compare the native periodic sample during the same six-G plateau.
    bi = base_data.Time_s.index(7.999)
    pi = protected_data.Time_s.index(7.999)
    assert protected_data.G[pi] == base_data.G[bi]
    assert protected_data.HLAP_mmHg[pi] > base_data.HLAP_mmHg[bi] + 10
    assert protected_data.F_con_dl_per_min[pi] > base_data.F_con_dl_per_min[bi]
