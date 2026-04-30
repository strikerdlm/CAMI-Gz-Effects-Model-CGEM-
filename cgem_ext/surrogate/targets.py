"""Target catalogue for the surrogate emulator.

Five targets, two flavours:

* **Censored time targets** — ``time_to_greyout_s``, ``time_to_blackout_s``,
  ``time_to_gloc_s``. Right-censored: rows where the event did not
  occur during the maneuver carry ``None`` in the time column and ``0``
  in the matching ``event_*`` flag. Handled via a two-stage classifier-
  then-regressor pattern (see :class:`cgem_ext.surrogate.xgb.TwoStageXGBSurrogate`).
* **Continuous targets** — ``hlap_min``, ``c_bank_min``. Always present;
  fit by a single regressor.

This module is the single source of truth for: (a) the target list,
(b) which targets are censored, (c) the matching ``event_*`` column
when censored, and (d) per-target monotonicity hints for XGBoost.

Monotonicity priors are physiologically-grounded:

- Higher peak |G| should *shorten* time-to-greyout / -blackout / -G-LOC
  (sign = -1 on ``g_peak_abs``).
- Higher onset rate (``dgdt_max_g_per_s``) should *shorten* time-to-event
  (sign = -1).
- Higher countermeasures (``cm_ordinal``) and higher countermeasure
  components (``agsm_effectiveness``, ``gsuit_max_psi``) should *lengthen*
  time-to-event (sign = +1).
- Higher dehydration should reduce HLAP_min and shorten c_bank_min
  (sign = -1 on ``hlap_min`` / ``c_bank_min`` for ``dehydration_level``).

We deliberately keep the constraint set sparse — only constraints with
a clear physiological prior are encoded. Unconstrained features (all
``who_*`` one-hots, profile_duration_s, gsuit_coverage, pbg_max_mmhg,
g_tolerance_multiplier) are left at 0.
"""

from __future__ import annotations

from dataclasses import dataclass

from cgem_ext.surrogate.features import FEATURE_COLUMNS, feature_index


@dataclass(frozen=True)
class TargetSpec:
    """Specification for one surrogate target."""

    name: str
    censored: bool
    event_column: str | None  # set iff censored
    description: str
    units: str
    monotonicity: tuple[int, ...]


def _monotonicity(positive: tuple[str, ...] = (), negative: tuple[str, ...] = ()) -> tuple[int, ...]:
    """Build a length-len(FEATURE_COLUMNS) monotonicity vector."""
    vec = [0] * len(FEATURE_COLUMNS)
    for name in positive:
        vec[feature_index(name)] = 1
    for name in negative:
        vec[feature_index(name)] = -1
    return tuple(vec)


# Common monotonicity for time-to-event targets: higher G stress shortens
# time-to-event; better countermeasures and pilot tolerance lengthen it.
_TIME_NEGATIVES = ("g_peak_abs", "dgdt_max_g_per_s", "dehydration_level")
_TIME_POSITIVES = ("g_tolerance_multiplier", "agsm_effectiveness", "gsuit_max_psi", "cm_ordinal")


TARGETS: tuple[TargetSpec, ...] = (
    TargetSpec(
        name="time_to_greyout_s",
        censored=True,
        event_column="event_greyout",
        description="Time from t=0 of the maneuver to first greyout flag.",
        units="seconds",
        monotonicity=_monotonicity(positive=_TIME_POSITIVES, negative=_TIME_NEGATIVES),
    ),
    TargetSpec(
        name="time_to_blackout_s",
        censored=True,
        event_column="event_blackout",
        description="Time from t=0 to first blackout flag.",
        units="seconds",
        monotonicity=_monotonicity(positive=_TIME_POSITIVES, negative=_TIME_NEGATIVES),
    ),
    TargetSpec(
        name="time_to_gloc_s",
        censored=True,
        event_column="event_gloc",
        description="Time from t=0 to G-induced loss of consciousness.",
        units="seconds",
        monotonicity=_monotonicity(positive=_TIME_POSITIVES, negative=_TIME_NEGATIVES),
    ),
    TargetSpec(
        name="hlap_min",
        censored=False,
        event_column=None,
        description="Minimum heart-level mean arterial pressure during the maneuver.",
        units="mmHg",
        monotonicity=_monotonicity(
            positive=("g_tolerance_multiplier", "gsuit_max_psi", "agsm_effectiveness", "cm_ordinal"),
            negative=("g_peak_abs", "dehydration_level"),
        ),
    ),
    TargetSpec(
        name="c_bank_min",
        censored=False,
        event_column=None,
        description="Minimum consciousness reserve bank during the maneuver.",
        units="seconds",
        monotonicity=_monotonicity(
            positive=("g_tolerance_multiplier", "gsuit_max_psi", "agsm_effectiveness", "cm_ordinal"),
            negative=("g_peak_abs", "dgdt_max_g_per_s", "dehydration_level"),
        ),
    ),
)


def get_target(name: str) -> TargetSpec:
    for t in TARGETS:
        if t.name == name:
            return t
    raise KeyError(f"Unknown target {name!r}; available: {[t.name for t in TARGETS]}")


def censored_targets() -> tuple[TargetSpec, ...]:
    return tuple(t for t in TARGETS if t.censored)


def continuous_targets() -> tuple[TargetSpec, ...]:
    return tuple(t for t in TARGETS if not t.censored)


__all__ = [
    "TARGETS",
    "TargetSpec",
    "censored_targets",
    "continuous_targets",
    "get_target",
]
