"""Tests for the Kennedy-O'Hagan / NARGP multi-fidelity coupling.

Exercises :class:`cgem_ext.surrogate.multifidelity.MultiFidelityNARGP`
against the WF2013 low-fidelity model and a small synthetic high-
fidelity training set.

Tests are pure-Python (no compiled CGEM binary required) and run in
CI under the ``not needs_cgem_binary`` filter.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _synthetic_high_fidelity(rng_seed: int = 0, n: int = 50):
    """Build a small synthetic 'high-fidelity' training set whose
    relationship with the low-fidelity model is::

        y_high = ρ · y_low + δ(g_peak, onset_rate) + noise

    with ρ=1, δ a smooth correction, and small Gaussian noise.
    """
    rng = np.random.default_rng(rng_seed)
    g_peak = rng.uniform(5.5, 11.0, n)
    onset = np.exp(rng.uniform(np.log(0.1), np.log(8.0), n))
    X = np.column_stack([g_peak, onset])

    # Low-fidelity prediction.
    from cgem_ext.surrogate import WhinneryForsterGLOC

    wf = WhinneryForsterGLOC()
    z_low = wf.predict_array(X)
    # Smooth correction term: a quadratic in (g_peak − 7) plus a
    # log-onset term. Tunable so the synthetic discrepancy is non-zero.
    delta = 0.5 * (g_peak - 7.0) ** 2 + 1.5 * np.log(onset)
    noise = rng.normal(0.0, 0.5, n)
    y_high = z_low + delta + noise
    return X, y_high


def test_multifidelity_fit_predict_shapes():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=40)
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(X, y)

    pred = mf.predict(X)
    assert pred.shape == (len(X),)

    mean, std = mf.predict(X, return_std=True)
    assert mean.shape == (len(X),)
    assert std.shape == (len(X),)
    assert (std > 0).all()


def test_multifidelity_predict_interval_brackets_truth_in_distribution():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=80)
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(X, y)

    lo, hi = mf.predict_interval(X, alpha=0.10)
    finite = ~np.isnan(lo) & ~np.isnan(hi)
    coverage = ((y[finite] >= lo[finite]) & (y[finite] <= hi[finite])).mean()
    # Training-set coverage should be high (the GP nearly interpolates).
    assert coverage >= 0.85


def test_multifidelity_handles_out_of_envelope_low_fidelity():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=40)
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(X, y)

    # Query a row above the WF2013 g_peak ceiling — low-fidelity
    # returns NaN, so the multi-fidelity prediction should also be NaN.
    X_bad = np.array([[15.0, 5.0]])
    pred = mf.predict(X_bad)
    assert np.isnan(pred).all()


def test_multifidelity_handles_below_threshold_low_fidelity():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=40)
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(X, y)

    # Below +Gz threshold — low-fidelity returns inf which is clipped
    # before passing into the GP. The multi-fidelity prediction should
    # be a finite number (not NaN, not inf).
    X_below = np.array([[3.0, 5.0]])
    pred = mf.predict(X_below)
    assert np.isfinite(pred).all()


def test_multifidelity_unfitted_raises():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC())
    with pytest.raises(RuntimeError, match="not fitted"):
        _ = mf.fit_info
    with pytest.raises(RuntimeError, match="not fitted"):
        mf.predict(np.array([[7.0, 5.0]]))


def test_multifidelity_alpha_validation():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=20)
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(X, y)
    with pytest.raises(ValueError, match="alpha"):
        mf.predict_interval(X, alpha=0.0)
    with pytest.raises(ValueError, match="alpha"):
        mf.predict_interval(X, alpha=1.0)


def test_multifidelity_dataframe_input():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=30)
    df = pd.DataFrame(X, columns=["g_peak_abs", "dgdt_max_g_per_s"])
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(df, y)
    pred = mf.predict(df)
    assert pred.shape == (len(df),)


def test_multifidelity_fit_info_records_kernel_and_n():
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=25)
    mf = MultiFidelityNARGP(low_fidelity=WhinneryForsterGLOC()).fit(X, y)

    info = mf.fit_info
    assert info.n_high_fidelity_points <= len(X)
    assert info.rho == 1.0
    assert "Matern" in info.discrepancy_kernel or "matern" in info.discrepancy_kernel.lower()
    assert np.isfinite(info.log_marginal_likelihood)


def test_multifidelity_data_efficiency_vs_pure_low_fidelity():
    """At small high-fidelity budgets, MultiFidelityNARGP should
    out-perform a pure-low-fidelity baseline on synthetic-discrepancy
    data because the discrepancy GP corrects for the systematic bias."""
    from cgem_ext.surrogate import MultiFidelityNARGP, WhinneryForsterGLOC

    X, y = _synthetic_high_fidelity(n=80)
    train_X, train_y = X[:20], y[:20]
    test_X, test_y = X[20:], y[20:]

    wf = WhinneryForsterGLOC()
    mf = MultiFidelityNARGP(low_fidelity=wf).fit(train_X, train_y)

    pred_mf = mf.predict(test_X)
    pred_lo = wf.predict_array(test_X)

    finite = (
        ~np.isnan(pred_mf) & ~np.isnan(pred_lo) & ~np.isinf(pred_lo)
    )
    rmse_mf = np.sqrt(((pred_mf[finite] - test_y[finite]) ** 2).mean())
    rmse_lo = np.sqrt(((pred_lo[finite] - test_y[finite]) ** 2).mean())
    # Multi-fidelity must beat the raw low-fidelity baseline by a
    # nontrivial margin on this synthetic discrepancy structure.
    assert rmse_mf < rmse_lo - 0.5
