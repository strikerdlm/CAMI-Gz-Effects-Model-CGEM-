"""Regression test enforcing the consumer contract `pulse-sim` depends on.

`pulse-sim/integrations/cgem_bridge.py` (v2.2.0) imports two symbols from
the CGEM repo and reads a documented set of attributes off the result:

    >>> from cgem_wrapper import run_cgem_for_profile, PilotConfig
    >>> result, run_dir = run_cgem_for_profile("high_g_turn", PilotConfig(who_profile=2))
    >>> result.times_s, result.g_values, result.hlap_values, ...

This file fails CI if any of those imports stops resolving, the result
dataclass loses a documented field, or the new ``cgem_ext`` re-export
diverges from the upstream wrapper.

Tests that actually execute the Fortran binary are guarded by the
``cgem_binary_available`` fixture and skip cleanly on environments
without it (e.g. minimal CI).
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

# ──────────────────────────────────────────────────────────────────────
# Static (no-binary) checks — always run in CI
# ──────────────────────────────────────────────────────────────────────


def test_upstream_imports_resolve() -> None:
    """The import path pulse-sim uses must keep working."""
    from cgem_wrapper import PilotConfig, run_cgem_for_profile  # noqa: F401


def test_cgem_ext_reexports_match_upstream() -> None:
    """`cgem_ext.run_cgem_for_profile` must be the same function pulse-sim
    would obtain via the upstream import path."""
    import cgem_ext
    import cgem_wrapper

    assert cgem_ext.run_cgem_for_profile is cgem_wrapper.run_cgem_for_profile
    assert cgem_ext.PilotConfig is cgem_wrapper.PilotConfig


def test_run_cgem_for_profile_signature() -> None:
    """The function signature pulse-sim's bridge calls."""
    from cgem_wrapper import run_cgem_for_profile

    sig = inspect.signature(run_cgem_for_profile)
    params = list(sig.parameters)
    # Bridge calls: run_cgem_for_profile(maneuver, cfg)
    assert params[:2] == ["profile_id", "config"], (
        "pulse-sim invokes run_cgem_for_profile(profile_id, config); "
        f"current signature exposes {params}"
    )


def test_pilot_config_accepts_who_profile() -> None:
    """pulse-sim instantiates PilotConfig(who_profile=int).
    The dataclass must accept that keyword without error."""
    from cgem_wrapper import PilotConfig

    cfg = PilotConfig(who_profile=2)
    # Dataclasses become hashable when frozen; this just probes the object.
    assert getattr(cfg, "who_profile", None) == 2


def test_cgem_result_has_documented_fields() -> None:
    """Every attribute pulse-sim's bridge reads must remain on CGEMResult.

    See pulse-sim/integrations/cgem_bridge.py:_result_to_dataframe for the
    consumer-side reads (Time(s), G, G_eff, HLAP(mmHg), F_con, F_vis, F_bo,
    c_bank, bo_bank, plus event-time scalars).
    """
    from cgem_wrapper import CGEMResult

    fields_required: tuple[str, ...] = (
        # Event-time scalars (read directly into the joint report)
        "time_to_greyout_s",
        "time_to_blackout_s",
        "time_to_gloc_s",
        # Time-series (mapped 1:1 to DataFrame columns by the bridge)
        "times_s",
        "g_values",
        "geff_values",
        "hlap_values",
        "f_con_values",
        "f_vis_values",
        "f_bo_values",
        "c_bank_values",
        "bo_bank_values",
    )
    annotations = getattr(CGEMResult, "__annotations__", {})
    missing = [f for f in fields_required if f not in annotations]
    assert not missing, (
        f"pulse-sim's CGEM bridge reads these fields off CGEMResult; "
        f"the following are missing or renamed: {missing}"
    )


# ──────────────────────────────────────────────────────────────────────
# Live (binary-required) checks — skipped when `cgem` is absent
# ──────────────────────────────────────────────────────────────────────


@pytest.mark.needs_cgem_binary
def test_run_cgem_for_profile_executes(cgem_binary_available: bool) -> None:
    """End-to-end smoke test mirroring pulse-sim's call shape."""
    if not cgem_binary_available:
        pytest.skip("cgem binary not present in repo root")

    from cgem_wrapper import PilotConfig, run_cgem_for_profile

    cfg = PilotConfig(who_profile=2)
    result, run_dir = run_cgem_for_profile("high_g_turn", cfg)

    assert run_dir.exists()
    assert isinstance(result.times_s, list) and len(result.times_s) > 0
    assert isinstance(result.g_values, list) and len(result.g_values) == len(result.times_s)
    # Event-time fields are Optional[float] by contract; they can be None
    # when no event occurred during the maneuver. Just probe the type.
    for attr in ("time_to_greyout_s", "time_to_blackout_s", "time_to_gloc_s"):
        v: Any = getattr(result, attr)
        assert v is None or isinstance(v, (int, float))
