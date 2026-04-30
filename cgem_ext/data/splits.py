"""Train / val / test splits for the synthetic CGEM dataset.

Two splitters are exposed:

* ``stratified_split`` — single 70/15/15 split stratified by maneuver
  category (championship, military_acm, extreme_post_stall, training,
  conceptual). Used for the headline emulator metrics. The split is
  deterministic given a seed and is committed to the OSF
  pre-registration before any test-set evaluation.
* ``leave_one_group_out`` — yields disjoint train/test pairs that hold
  out one full maneuver category at a time. Used for OOD-style
  validation: how well does the surrogate generalise to a category it
  has never seen? This is the basis of the "leave-one-group-out R^2"
  number reported in the paper.

Both splitters operate row-wise; the input is the parquet emitted by
``cgem_ext.data.generate_dataset.generate``.

The category column is read directly from the parquet
(``maneuver_category``) which the generator merges in via
``maneuvers_catalog`` at write time. We re-derive the category from the
maneuver string only as a fallback if the column is missing.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
import pandas as pd

import cgem_ext  # noqa: F401  side-effect: injects repo root onto sys.path

try:
    from maneuvers_catalog import get as _get_maneuver_meta
except ImportError:  # pragma: no cover
    _get_maneuver_meta = None  # type: ignore[assignment]


@dataclass(frozen=True)
class Split:
    """A single train/val/test split as integer index arrays."""

    train_idx: np.ndarray
    val_idx: np.ndarray
    test_idx: np.ndarray
    seed: int
    train_frac: float
    val_frac: float
    test_frac: float

    def apply(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Slice the DataFrame into ``(train, val, test)`` views."""
        return (
            df.iloc[self.train_idx].reset_index(drop=True),
            df.iloc[self.val_idx].reset_index(drop=True),
            df.iloc[self.test_idx].reset_index(drop=True),
        )

    def __repr__(self) -> str:
        return (
            f"Split(train={len(self.train_idx)}, val={len(self.val_idx)}, "
            f"test={len(self.test_idx)}, seed={self.seed})"
        )


@dataclass(frozen=True)
class GroupSplit:
    """Hold-out-by-group split: train = all categories except ``held_out``."""

    train_idx: np.ndarray
    test_idx: np.ndarray
    held_out: str

    def apply(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        return (
            df.iloc[self.train_idx].reset_index(drop=True),
            df.iloc[self.test_idx].reset_index(drop=True),
        )

    def __repr__(self) -> str:
        return (
            f"GroupSplit(held_out={self.held_out!r}, "
            f"train={len(self.train_idx)}, test={len(self.test_idx)})"
        )


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def _ensure_category_column(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a ``maneuver_category`` column populated.

    If the column is already present, leaves df alone (returns the same
    object). Otherwise re-derives from ``maneuver`` via
    ``maneuvers_catalog``; rows without a registered category are tagged
    ``"unregistered"``.
    """
    if "maneuver_category" in df.columns:
        return df
    if "maneuver" not in df.columns:
        raise KeyError(
            "DataFrame is missing both 'maneuver_category' and 'maneuver'; "
            "cannot determine maneuver category for splitting."
        )
    if _get_maneuver_meta is None:
        out = df.copy()
        out["maneuver_category"] = "unregistered"
        return out
    cats = []
    for m in df["maneuver"]:
        try:
            cats.append(_get_maneuver_meta(m).category.value)
        except KeyError:
            cats.append("unregistered")
    out = df.copy()
    out["maneuver_category"] = cats
    return out


def _check_fractions(train: float, val: float, test: float) -> None:
    total = train + val + test
    if not 0.999 <= total <= 1.001:
        raise ValueError(f"Split fractions must sum to 1.0; got {total}")
    if min(train, val, test) <= 0:
        raise ValueError("All split fractions must be > 0")


# ──────────────────────────────────────────────────────────────────────
# Stratified 70/15/15 split
# ──────────────────────────────────────────────────────────────────────


def stratified_split(
    df: pd.DataFrame,
    *,
    seed: int = 42,
    train_frac: float = 0.70,
    val_frac: float = 0.15,
    test_frac: float = 0.15,
    drop_status_error: bool = True,
) -> Split:
    """Stratified train/val/test split keyed on ``maneuver_category``.

    Within each category we shuffle row indices deterministically (seed)
    and slice into the requested fractions. Categories with fewer than
    three rows still receive at least one row in train (and val/test
    only if rows remain). This avoids the edge case where a tiny
    category vanishes from train.

    Parameters
    ----------
    df
        The dataset DataFrame as produced by
        :func:`cgem_ext.data.generate_dataset.generate`.
    seed
        Master seed for the per-category shuffle.
    train_frac, val_frac, test_frac
        Must sum to 1.0.
    drop_status_error
        If True (default), rows with ``status != "ok"`` are excluded
        before splitting. They are not part of the regression target
        space and would just inject NaNs.

    Returns
    -------
    Split
        Integer index arrays into the *original* df (or the
        status-filtered view if ``drop_status_error=True`` — in which
        case the indices are into the filtered df with indices reset).
    """
    _check_fractions(train_frac, val_frac, test_frac)

    df = _ensure_category_column(df)
    if drop_status_error and "status" in df.columns:
        df = df[df["status"] == "ok"].reset_index(drop=True)

    rng = np.random.default_rng(seed)
    train_parts: list[np.ndarray] = []
    val_parts: list[np.ndarray] = []
    test_parts: list[np.ndarray] = []

    for _category, sub in df.groupby("maneuver_category", sort=True):
        idx = sub.index.to_numpy()
        rng.shuffle(idx)
        n = len(idx)
        if n == 0:
            continue
        n_train = max(1, int(round(n * train_frac))) if n >= 1 else 0
        # Distribute the remainder between val/test proportionally.
        remainder = n - n_train
        if remainder > 0:
            n_val = max(1, int(round(remainder * val_frac / (val_frac + test_frac))))
            n_val = min(n_val, remainder)
            n_test = remainder - n_val
        else:
            n_val = n_test = 0

        train_parts.append(idx[:n_train])
        val_parts.append(idx[n_train : n_train + n_val])
        test_parts.append(idx[n_train + n_val :])

    train_idx = np.concatenate(train_parts) if train_parts else np.array([], dtype=int)
    val_idx = np.concatenate(val_parts) if val_parts else np.array([], dtype=int)
    test_idx = np.concatenate(test_parts) if test_parts else np.array([], dtype=int)

    # Sort within each split for stable downstream behaviour.
    train_idx.sort()
    val_idx.sort()
    test_idx.sort()

    return Split(
        train_idx=train_idx,
        val_idx=val_idx,
        test_idx=test_idx,
        seed=seed,
        train_frac=train_frac,
        val_frac=val_frac,
        test_frac=test_frac,
    )


# ──────────────────────────────────────────────────────────────────────
# Leave-one-group-out
# ──────────────────────────────────────────────────────────────────────


def leave_one_group_out(
    df: pd.DataFrame,
    *,
    group_column: str = "maneuver_category",
    drop_status_error: bool = True,
) -> Iterator[GroupSplit]:
    """Yield ``GroupSplit``s holding out one category at a time.

    For OOD-style validation: train on every category except one,
    test on the held-out category. The OOD detector and the surrogate
    are both expected to behave gracefully on these splits — see
    ``tests/test_ood.py`` and ``tests/test_surrogate.py`` once
    Phases 2 and 3 land.

    Categories yielded in alphabetical order so iteration is
    deterministic across runs.
    """
    df = _ensure_category_column(df)
    if drop_status_error and "status" in df.columns:
        df = df[df["status"] == "ok"].reset_index(drop=True)
    if group_column not in df.columns:
        raise KeyError(f"DataFrame missing column {group_column!r} for leave-one-group-out")

    groups = sorted(df[group_column].unique().tolist())
    for held_out in groups:
        held_mask = df[group_column].to_numpy() == held_out
        train_idx = np.where(~held_mask)[0]
        test_idx = np.where(held_mask)[0]
        yield GroupSplit(train_idx=train_idx, test_idx=test_idx, held_out=str(held_out))


__all__ = [
    "GroupSplit",
    "Split",
    "leave_one_group_out",
    "stratified_split",
]
