"""Low-fidelity analytical G-tolerance models.

These models are µs-cost analytical approximations of the time-to-LOC
relationship under +Gz acceleration. They are *low-fidelity* relative
to the FAA CGEM core: they encode less physiology (no compartmental
hemodynamics, no pilot-configuration parameters beyond a single
G-tolerance multiplier) but evaluate orders of magnitude faster and
have published validity envelopes against archival centrifuge data.

Their purpose in this package is twofold:

1. **Manuscript baseline.** The CQR / Mondrian conformal layer in
   :mod:`cgem_ext.surrogate.cqr` is an ML wrapper around CGEM. The
   low-fidelity models below provide a non-ML, non-CGEM baseline against
   which the surrogate's calibrated bracket can be compared at a
   single-row level.

2. **Multi-fidelity coupling (deferred to Week 6).** A Kennedy & O'Hagan
   or NARGP scheme treating the low-fidelity model as the cheap source
   and CGEM as the high-fidelity source can achieve calibrated coverage
   at lower CGEM-call budgets than a single-fidelity surrogate.
   :mod:`cgem_ext.surrogate.multifidelity` is the planned home for the
   coupling code; this subpackage supplies the low-fidelity functions
   it consumes.

Models implemented:

* :class:`StollGTolerance` — Stoll-1956 sustained-G tolerance curve.
  An exponential / sigmoid relationship between sustained +Gz level
  and time-to-tolerance. Domain of original validity is rapid-onset,
  unprotected exposures.
* :class:`WhinneryForsterGLOC` — Whinnery & Forster 2013 piecewise
  curve. Three-segment analytical fit to the 888-episode centrifuge
  cohort: ≤ 0.2 G/s gradual regime, transitional 0.2 – 1.0 G/s, and
  ≥ 1.0 G/s rapid regime where time-to-LOC saturates near 9.10 s.

Both models expose a uniform API::

    model.predict_time_to_loc_s(g_peak_abs, dgdt_max_g_per_s) -> float
    model.predict_array(X) -> np.ndarray  # vectorised; X has columns
                                           # (g_peak_abs, dgdt_max_g_per_s)

Models report :attr:`validity_envelope` describing the input range
within which their published validation evidence applies, and a
sentinel value (``np.nan``) outside it. Callers must check the
returned value before using the prediction operationally; the
multi-fidelity layer downstream uses the sentinel to fall back to
high-fidelity CGEM evaluations in regions where the low-fidelity
model is out-of-envelope.
"""

from cgem_ext.surrogate.lowfi.stoll import StollGTolerance
from cgem_ext.surrogate.lowfi.whinnery_forster import WhinneryForsterGLOC

__all__ = ["StollGTolerance", "WhinneryForsterGLOC"]
