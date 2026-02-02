from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any, cast

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
    "group_col_by_prefix",
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
    is_missing = pd.isna(current) or current in missing_markers
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
    assert len(matches) > 0, f"No rows found where {column} == {value!r}"
    assert len(matches) <= 1, f"Multiple rows found where {column} == {value!r}"
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


def _normalize_prefix_items(
    prefix_map: Mapping[str, str] | Iterable[tuple[str, str]] | None,
) -> list[tuple[str, str]]:
    if prefix_map is None:
        return []
    items = list(prefix_map.items() if isinstance(prefix_map, Mapping) else prefix_map)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in items), (
        f"Prefix map must be a mapping or iterable of tuples, received {type(prefix_map)!r}."
    )

    normalized: list[tuple[str, str]] = []
    for prefix, group in items:
        assert isinstance(prefix, str), (
            f"Prefix keys must be strings, received {type(prefix)!r}."
        )
        assert isinstance(group, str), (
            f"Group names must be strings, received {type(group)!r}."
        )
        lowered = prefix.strip().lower()
        assert lowered, "Prefix keys must be non-empty after stripping whitespace."
        normalized.append((lowered, group))
    normalized.sort(key=lambda item: (-len(item[0]), item[0]))
    return normalized


def group_col_by_prefix(
    df: pd.DataFrame,
    column: str,
    prefix_map: Mapping[str, str] | Iterable[tuple[str, str]] | None,
    *,
    output_col: str,
) -> pd.Series:
    assert column in df.columns, f"Column '{column}' not present in DataFrame."

    series = cast(pd.Series, df[column])
    normalized_prefixes = _normalize_prefix_items(prefix_map)

    if not normalized_prefixes:
        return series.copy().rename(output_col)

    def resolve(value: object) -> object:
        if bool(pd.isna(value)):
            return value
        if isinstance(value, str):
            lowered = value.lower()
            for prefix, group in normalized_prefixes:
                if lowered.startswith(prefix):
                    return group
            return value
        return value

    return series.map(resolve).rename(output_col)
