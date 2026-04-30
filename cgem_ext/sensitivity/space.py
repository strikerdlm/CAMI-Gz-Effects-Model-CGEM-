"""Sensitivity-analysis input space.

Sobol and Morris methods need every input dimension specified as a
continuous range with explicit bounds. The full :mod:`cgem_ext.ood.features`
feature space is 17-dimensional (9 numeric + 7 one-hot WHO + 1 ordinal
cm), but the categorical / one-hot dimensions are not Sobol-friendly:
SALib treats them as continuous, generates fractional values, and the
surrogate happily accepts them — but the indices that come back are
hard to interpret physically.

This module restricts the sensitivity sweep to the 9 continuous
features and holds the categorical / one-hot dims fixed at canonical
defaults. Reviewers can read the sensitivity rankings as "given a
typical pilot (who_profile=2) running countermeasures=none, which of
the continuous knobs drives the output most?".

We expose two helpers:

* :data:`SOBOL_PROBLEM` — the SALib problem dict (``num_vars``, ``names``,
  ``bounds``).
* :func:`fixed_feature_template` — returns a 1-D ``np.ndarray`` aligned
  to ``cgem_ext.ood.features.FEATURE_COLUMNS`` with the categorical/
  one-hot defaults set; the Sobol sweep overwrites the 9 continuous
  slots with the Saltelli sample.

The bounds below are sourced from the empirical extents in
``cgem_synthetic_v1`` rounded outward slightly so the Saltelli sample
covers the in-distribution envelope. Anything outside these bounds is
explicitly out-of-distribution and would be flagged by
:mod:`cgem_ext.ood`.
"""

from __future__ import annotations

import numpy as np

from cgem_ext.ood.features import FEATURE_COLUMNS

# ── Continuous-feature names + bounds (must align with FEATURE_COLUMNS) ─
SENSITIVITY_FEATURES: tuple[str, ...] = (
    "g_peak_abs",
    "dgdt_max_g_per_s",
    "profile_duration_s",
    "dehydration_level",
    "g_tolerance_multiplier",
    "gsuit_max_psi",
    "gsuit_coverage_fraction",
    "agsm_effectiveness",
    "pbg_max_mmhg",
)

# Empirical extents in cgem_synthetic_v1 (rounded outward by ~10%)
SENSITIVITY_BOUNDS: tuple[tuple[float, float], ...] = (
    (1.0, 10.0),     # g_peak_abs (G)
    (0.5, 45.0),     # dgdt_max_g_per_s
    (4.0, 45.0),     # profile_duration_s
    (0.0, 0.7),      # dehydration_level
    (0.85, 1.15),    # g_tolerance_multiplier
    (0.0, 10.0),     # gsuit_max_psi
    (0.0, 0.7),      # gsuit_coverage_fraction
    (0.0, 0.8),      # agsm_effectiveness
    (0.0, 15.0),     # pbg_max_mmhg
)

# SALib problem dict (consumed by saltelli + sobol_analyze + morris)
SOBOL_PROBLEM: dict = {
    "num_vars": len(SENSITIVITY_FEATURES),
    "names": list(SENSITIVITY_FEATURES),
    "bounds": [list(b) for b in SENSITIVITY_BOUNDS],
}


# ── Held-fixed defaults for categorical / one-hot dimensions ─────────


def fixed_feature_template(
    *,
    who_profile: int | str | None = "custom",
    cm_ordinal: float = 0.0,
) -> np.ndarray:
    """Build a length-len(FEATURE_COLUMNS) row aligned to FEATURE_COLUMNS.

    Continuous slots are zero-initialised; the caller (Sobol / Morris
    runner) overwrites them with the Saltelli sample. Categorical /
    one-hot slots are set to canonical defaults:

    - ``who_profile`` — one of ``1..6`` (FAA standard subject one-hot)
      or ``"custom"`` / ``None`` (sets ``who_custom = 1`` so the
      Saltelli sample for ``g_tolerance_multiplier`` and
      ``dehydration_level`` is *in-distribution* against the custom
      arm of ``cgem_synthetic_v1``). Default ``"custom"``.
    - ``cm_ordinal=0`` (countermeasures = none).

    Why default to custom: in the dataset's standard arm
    ``dehydration_level`` and ``g_tolerance_multiplier`` are fixed at
    canonical values (the Fortran model overrides subject physiology
    when ``who_profile`` is set). Running Sobol against a fixed FAA
    preset therefore queries the surrogate at OOD points whenever the
    Saltelli sample picks a non-zero dehydration. The surrogate happily
    extrapolates, but the resulting indices reflect *the surrogate's
    learned coupling*, not CGEM's actual behaviour. The custom arm
    exercises all nine continuous features in-distribution.

    Both arms are reported in the per-target Sobol CSVs: the
    custom-arm result is the headline rank; the standard-arm result is
    reported alongside as an "in this preset, with dehydration held at
    the value the FAA model would actually use, what drives the output?"
    sanity check.

    Whatever is fixed here is documented in the per-target Sobol CSV
    header and the model card.
    """
    template = np.zeros(len(FEATURE_COLUMNS), dtype=float)
    if who_profile in (None, "custom"):
        idx = FEATURE_COLUMNS.index("who_custom")
    elif isinstance(who_profile, int) and 1 <= who_profile <= 6:
        idx = FEATURE_COLUMNS.index(f"who_{who_profile}")
    else:
        raise ValueError(
            f"who_profile must be 1..6, 'custom', or None; got {who_profile!r}"
        )
    template[idx] = 1.0
    cm_idx = FEATURE_COLUMNS.index("cm_ordinal")
    template[cm_idx] = float(cm_ordinal)
    return template


def continuous_indices() -> tuple[int, ...]:
    """Return the FEATURE_COLUMNS indices of the 9 continuous features."""
    return tuple(FEATURE_COLUMNS.index(name) for name in SENSITIVITY_FEATURES)


__all__ = [
    "SENSITIVITY_BOUNDS",
    "SENSITIVITY_FEATURES",
    "SOBOL_PROBLEM",
    "continuous_indices",
    "fixed_feature_template",
]
