from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

import pandas as pd

__all__ = [
    "ensure_column",
    "fill_missing_values",
    "rename_columns",
    "map_column_with_fallback",
    "apply_column_converters",
    "maybe_update_cell",
    "force_set_cell",
    "apply_if_column",
    "masked_getter",
    "masked_setter",
    "require_row_index",
]

MissingMarkers = Iterable[Any]


def ensure_column(
    df: pd.DataFrame,
    column: str,
    default: Any,
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    if column not in target.columns:
        target[column] = default
    elif default is None:
        pass
    else:
        target[column] = target[column].fillna(default)
    return target


def fill_missing_values(
    df: pd.DataFrame,
    defaults: Mapping[str, Any],
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    for column, default in defaults.items():
        if column in target.columns:
            target[column] = target[column].fillna(default)
    return target


def rename_columns(
    df: pd.DataFrame,
    mapping: Mapping[str, str],
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    existing_map = {old: new for old, new in mapping.items() if old in target.columns}
    if existing_map:
        target = target.rename(columns=existing_map)
    return target


def map_column_with_fallback(
    df: pd.DataFrame,
    column: str,
    mapping: Mapping[str, Any],
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    if column not in df.columns:
        return df if inplace else df.copy()

    target = df if inplace else df.copy()

    def _mapper(value: Any) -> Any:
        if pd.isna(value):
            return value
        return mapping.get(value, value)

    target[column] = target[column].map(_mapper)
    return target


def apply_column_converters(
    df: pd.DataFrame,
    converters: Mapping[str, Callable[[Any], Any]],
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    for column, converter in converters.items():
        if column in target.columns:
            target[column] = target[column].apply(converter)
    return target


def _matches_missing_marker(current: Any, marker: Any) -> bool:
    """Safely check if current value matches a missing marker.

    Handles NaN values via pd.isna comparisons and catches TypeError
    for unhashable types to ensure comparisons never raise.
    """
    try:
        # Handle NaN comparisons first
        if pd.isna(current) and pd.isna(marker):
            return True
        if pd.isna(current) or pd.isna(marker):
            return False
        # Safe equality check for hashable and unhashable types
        return current == marker
    except TypeError:
        # Unhashable types (e.g., lists, dicts) can't be compared with ==
        # in some contexts, so return False to be safe
        return False


def maybe_update_cell(
    df: pd.DataFrame,
    row_index: int,
    column: str,
    value: Any,
    *,
    missing_markers: MissingMarkers = (None, "N/A"),
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    if column not in target.columns or row_index not in target.index:
        return target

    current = target.loc[row_index, column]
    is_missing = pd.isna(current) or any(
        _matches_missing_marker(current, m) for m in missing_markers
    )
    if is_missing:
        target.loc[row_index, column] = value
    return target


def force_set_cell(
    df: pd.DataFrame,
    row_index: int,
    column: str,
    value: Any,
    *,
    default: Any = None,
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    target = ensure_column(target, column, default, inplace=True)
    target.loc[row_index, column] = value
    return target


def apply_if_column(
    df: pd.DataFrame,
    column: str,
    func: Callable[[pd.Series], pd.Series],
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    if column not in df.columns:
        return df if inplace else df.copy()

    target = df if inplace else df.copy()
    target[column] = func(target[column])
    return target


def require_row_index(
    df: pd.DataFrame,
    column: str,
    value: Any,
) -> int:
    matches = df.index[df[column] == value]
    if len(matches) == 0:
        raise ValueError(f"No rows found where {column} == {value!r}")
    if len(matches) > 1:
        raise ValueError(f"Multiple rows found where {column} == {value!r}")
    return int(matches[0])


def masked_getter(df: pd.DataFrame, mask: pd.Series, column: str) -> Any:
    if column not in df.columns:
        return None

    selection = df.loc[mask, column]
    if selection.empty:
        return None
    return selection.iloc[0]


def masked_setter(
    df: pd.DataFrame,
    mask: pd.Series,
    column: str,
    value: Any,
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    target = df if inplace else df.copy()
    target.loc[mask, column] = value
    return target
