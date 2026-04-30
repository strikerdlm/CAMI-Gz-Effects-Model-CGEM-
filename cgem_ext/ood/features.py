"""Feature encoding for the CGEM OOD detector.

The OOD detector operates over a fixed feature vector derived from the
``RowSpec`` columns of the synthetic dataset. Encoding choices are
documented in ``docs/publication/osf_preregistration.md`` and locked
before any test-set evaluation.

Numeric features (passed through):
    g_peak_abs                — max abs Nz from the maneuver profile
    dgdt_max_g_per_s          — max |dG/dt| from the maneuver profile
    profile_duration_s        — total maneuver duration
    dehydration_level         — 0.0 / 0.3 / 0.7
    g_tolerance_multiplier    — 0.85 / 1.00 / 1.15 (or 1.0 in standard arm)
    gsuit_max_psi             — countermeasure component
    gsuit_coverage_fraction   — countermeasure component
    agsm_effectiveness        — countermeasure component
    pbg_max_mmhg              — countermeasure component

Categorical features (one-hot, 7 indicator columns):
    who_profile               — {1, 2, 3, 4, 5, 6, custom}

Ordinal feature:
    cm_ordinal                — none=0, agsm=1, suit_agsm=2
                                kept alongside the numeric components so the
                                detector has a single scalar capturing
                                "countermeasure intensity"

The output is a ``pd.DataFrame`` with stable column ordering driven by
``FEATURE_COLUMNS``; this is what every consumer (Mahalanobis,
IsolationForest baseline, future surrogate) reads from.
"""

from __future__ import annotations

import pandas as pd


# ── Stable column ordering ─────────────────────────────────────────────

NUMERIC_FEATURES: tuple[str, ...] = (
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

WHO_LEVELS: tuple[str, ...] = (
    "who_1", "who_2", "who_3", "who_4", "who_5", "who_6", "who_custom",
)

ORDINAL_FEATURES: tuple[str, ...] = ("cm_ordinal",)

FEATURE_COLUMNS: tuple[str, ...] = NUMERIC_FEATURES + WHO_LEVELS + ORDINAL_FEATURES


# ── Encoding helpers ──────────────────────────────────────────────────

_CM_ORDER = {"none": 0, "agsm": 1, "suit_agsm": 2}


def _encode_who(who: object) -> dict[str, float]:
    """One-hot encode ``who_profile`` into the 7-column WHO_LEVELS layout.

    ``None`` (custom subject) maps to ``who_custom = 1`` and the standard
    presets map to their ordinal slot.
    """
    out = {col: 0.0 for col in WHO_LEVELS}
    if who is None or (isinstance(who, float) and pd.isna(who)):
        out["who_custom"] = 1.0
        return out
    try:
        i = int(who)
    except (TypeError, ValueError):
        out["who_custom"] = 1.0
        return out
    if 1 <= i <= 6:
        out[f"who_{i}"] = 1.0
    else:
        out["who_custom"] = 1.0
    return out


def _encode_cm(label: object) -> float:
    if isinstance(label, str) and label in _CM_ORDER:
        return float(_CM_ORDER[label])
    raise ValueError(
        f"Unknown countermeasures_label {label!r}; expected one of "
        f"{sorted(_CM_ORDER)}"
    )


# ── Public API ────────────────────────────────────────────────────────

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a feature DataFrame with the columns in ``FEATURE_COLUMNS``.

    Input ``df`` must be a slice of the synthetic dataset produced by
    :func:`cgem_ext.data.generate_dataset.generate` (any subset of rows
    is fine; column dtypes follow the parquet).
    """
    required = {
        "g_peak_abs", "dgdt_max_g_per_s", "profile_duration_s",
        "dehydration_level", "g_tolerance_multiplier",
        "gsuit_max_psi", "gsuit_coverage_fraction",
        "agsm_effectiveness", "pbg_max_mmhg",
        "who_profile", "countermeasures_label",
    }
    missing = required - set(df.columns)
    if missing:
        raise KeyError(
            f"extract_features: input DataFrame is missing required columns: "
            f"{sorted(missing)}"
        )

    out = pd.DataFrame(index=df.index)
    for col in NUMERIC_FEATURES:
        out[col] = df[col].astype(float)

    who_records = [_encode_who(v) for v in df["who_profile"].tolist()]
    who_df = pd.DataFrame(who_records, index=df.index)
    for col in WHO_LEVELS:
        out[col] = who_df[col].astype(float).values

    out["cm_ordinal"] = df["countermeasures_label"].map(_encode_cm).astype(float).values

    # Stable column ordering
    return out[list(FEATURE_COLUMNS)]


__all__ = [
    "FEATURE_COLUMNS",
    "NUMERIC_FEATURES",
    "ORDINAL_FEATURES",
    "WHO_LEVELS",
    "extract_features",
]
