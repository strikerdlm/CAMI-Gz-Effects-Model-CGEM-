"""Unit tests for the low-fidelity G-tolerance models.

Two models are exercised:

* :class:`cgem_ext.surrogate.lowfi.stoll.StollGTolerance` — Stoll
  1956-style sustained-G tolerance curve (anchored on WF2013).
* :class:`cgem_ext.surrogate.lowfi.whinnery_forster.WhinneryForsterGLOC`
  — three-segment piecewise WF2013 G-LOC time curve.

Tests are pure-Python (no compiled CGEM binary required) and run in
CI under the ``not needs_cgem_binary`` filter.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# ──────────────────────────────────────────────────────────────────────
# Stoll 1956 — anchor reproduction and envelope behaviour
# ──────────────────────────────────────────────────────────────────────


def test_stoll_anchor_reproduction():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    # Fitted to pass through (G=7, t=9.65) and (G=9.4, t=5.0).
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(7.0, 5.0), 9.65, rtol=1e-6
    )
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(9.4, 5.0), 5.0, rtol=1e-6
    )


def test_stoll_monotonically_decreasing_in_g_peak():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    g_peaks = np.linspace(5.0, 11.5, 30)
    times = np.array(
        [model.predict_time_to_loc_s(g, 5.0) for g in g_peaks]
    )
    diffs = np.diff(times)
    assert (diffs <= 0).all(), (
        "Stoll curve must be monotonically decreasing in g_peak"
    )


def test_stoll_returns_nan_below_threshold():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    # Below g_threshold (4.7 Gz).
    assert np.isnan(model.predict_time_to_loc_s(4.0, 5.0))
    # Above the validity-envelope max (12 Gz).
    assert np.isnan(model.predict_time_to_loc_s(13.0, 5.0))


def test_stoll_returns_nan_below_onset_rate():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    # Stoll is rapid-onset only; gradual onset out of envelope.
    assert np.isnan(model.predict_time_to_loc_s(7.0, 0.1))
    # At the cutoff, in envelope.
    assert not np.isnan(model.predict_time_to_loc_s(7.0, 1.0))


def test_stoll_predict_array_matches_scalar():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    rows = np.array(
        [
            [7.0, 5.0],
            [8.0, 5.0],
            [9.4, 5.0],
            [4.0, 5.0],  # below threshold
            [10.0, 0.5],  # below onset cutoff
        ],
        dtype=float,
    )
    arr_pred = model.predict_array(rows)
    scalar_pred = np.array(
        [model.predict_time_to_loc_s(g, r) for g, r in rows]
    )
    # NaNs must occur in the same rows.
    np.testing.assert_array_equal(np.isnan(arr_pred), np.isnan(scalar_pred))
    # Finite predictions must match.
    finite = ~np.isnan(arr_pred)
    np.testing.assert_allclose(arr_pred[finite], scalar_pred[finite])


def test_stoll_predict_array_accepts_dataframe():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    df = pd.DataFrame(
        {
            "g_peak_abs": [7.0, 8.0, 9.4],
            "dgdt_max_g_per_s": [5.0, 5.0, 5.0],
        }
    )
    pred = model.predict_array(df)
    assert pred.shape == (3,)
    assert (pred > 0).all()


def test_stoll_predict_array_rejects_bad_shape():
    from cgem_ext.surrogate import StollGTolerance

    model = StollGTolerance()
    with pytest.raises(ValueError, match="shape"):
        model.predict_array(np.array([1.0, 2.0, 3.0]))


# ──────────────────────────────────────────────────────────────────────
# Whinnery & Forster 2013 — anchor reproduction
# ──────────────────────────────────────────────────────────────────────


def test_whinnery_forster_rapid_anchor():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(9.0, 1.0), 9.10, rtol=1e-6
    )
    # Independent of onset rate above 1.0 G/s.
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(9.0, 5.0), 9.10, rtol=1e-6
    )
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(9.0, 10.0), 9.10, rtol=1e-6
    )


def test_whinnery_forster_gradual_anchor():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(7.0, 0.2), 74.41, rtol=1e-6
    )
    np.testing.assert_allclose(
        model.predict_time_to_loc_s(7.0, 0.05), 74.41, rtol=1e-6
    )


def test_whinnery_forster_transitional_interpolation():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    # In the transitional regime, t_loc must lie strictly between the
    # two anchor values.
    t_mid = model.predict_time_to_loc_s(7.0, 0.5)
    assert 9.10 < t_mid < 74.41


def test_whinnery_forster_below_threshold_returns_inf():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    # G-LOC does not occur below +4.7 Gz.
    assert np.isinf(model.predict_time_to_loc_s(4.0, 5.0))


def test_whinnery_forster_locindti_floor():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    # Even at maximum onset rate, t_loc must be ≥ 5 s (LOCINDTI floor).
    assert model.predict_time_to_loc_s(11.0, 10.0) >= 5.0


def test_whinnery_forster_predict_array_matches_scalar():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    rows = np.array(
        [
            [7.0, 1.0],   # rapid → 9.10
            [7.0, 0.2],   # gradual → 74.41
            [7.0, 0.5],   # transitional → between anchors
            [4.0, 5.0],   # below threshold → inf
            [13.0, 5.0],  # above g_peak max → nan
        ],
        dtype=float,
    )
    arr_pred = model.predict_array(rows)
    scalar_pred = np.array(
        [model.predict_time_to_loc_s(g, r) for g, r in rows]
    )
    # NaN, inf, and finite patterns must agree.
    nan_arr = np.isnan(arr_pred)
    nan_scalar = np.isnan(scalar_pred)
    np.testing.assert_array_equal(nan_arr, nan_scalar)
    inf_arr = np.isinf(arr_pred)
    inf_scalar = np.isinf(scalar_pred)
    np.testing.assert_array_equal(inf_arr, inf_scalar)
    finite = ~nan_arr & ~inf_arr
    np.testing.assert_allclose(arr_pred[finite], scalar_pred[finite])


def test_whinnery_forster_dataframe_input():
    from cgem_ext.surrogate import WhinneryForsterGLOC

    model = WhinneryForsterGLOC()
    df = pd.DataFrame(
        {
            "g_peak_abs": [7.0, 8.0, 9.0, 10.0],
            "dgdt_max_g_per_s": [1.0, 2.0, 5.0, 10.0],
        }
    )
    pred = model.predict_array(df)
    # All within rapid-onset regime → all 9.10 s.
    np.testing.assert_allclose(pred, 9.10, rtol=1e-6)


# ──────────────────────────────────────────────────────────────────────
# Cross-comparison against the H6 archival cohort anchors
# ──────────────────────────────────────────────────────────────────────


def test_lowfi_models_recover_h6_anchor_pattern():
    """Both low-fidelity models should reproduce the empirical pattern
    seen in the H6 evaluation: short t_loc at rapid onsets, long t_loc
    at slow onsets."""
    from cgem_ext.surrogate import StollGTolerance, WhinneryForsterGLOC

    stoll = StollGTolerance()
    wf = WhinneryForsterGLOC()

    # Rapid onset (5 G/s, 9.0 G plateau): both models should report
    # short t_loc.
    rapid = (9.0, 5.0)
    t_stoll_rapid = stoll.predict_time_to_loc_s(*rapid)
    t_wf_rapid = wf.predict_time_to_loc_s(*rapid)
    assert t_stoll_rapid < 12.0
    assert t_wf_rapid < 12.0

    # Slow onset (0.05 G/s, 6 G plateau): WF must report a long t_loc;
    # Stoll has no onset-rate dependence (rapid-onset only) and is out
    # of envelope here, so it returns NaN.
    slow = (6.0, 0.05)
    t_wf_slow = wf.predict_time_to_loc_s(*slow)
    t_stoll_slow = stoll.predict_time_to_loc_s(*slow)
    assert t_wf_slow > 50.0  # gradual regime → 74.41 s
    assert np.isnan(t_stoll_slow)
