from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

import pandas as pd

from dr_frames.types import is_string_series

__all__ = [
    "get_cols_by_prefix",
    "get_cols_by_contains",
    "strip_col_prefixes",
    "strip_col_prefixes_batch",
    "move_cols_to_beginning",
    "move_numeric_cols_to_end",
    "move_cols_with_prefix_to_end",
    "drop_all_null_cols",
]


def _skip_columns(columns: Sequence[str] | pd.Index, skip: Iterable[str] = ()) -> list[str]:
    skip_set = set(skip)
    return [column for column in columns if column not in skip_set]


def _contained_columns(df: pd.DataFrame, columns: Sequence[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def _remaining_columns(df: pd.DataFrame, cols: Iterable[str]) -> list[str]:
    skip_set = set(cols)
    return [column for column in df.columns if column not in skip_set]


def get_cols_by_prefix(
    df: pd.DataFrame, prefix: str, skip: Iterable[str] = ()
) -> list[str]:
    return [c for c in _skip_columns(df.columns, skip) if c.startswith(prefix)]


def get_cols_by_contains(
    df: pd.DataFrame, substr: str, skip: Iterable[str] = ()
) -> list[str]:
    return [c for c in _skip_columns(df.columns, skip) if substr in c]


def strip_col_prefixes(
    df: pd.DataFrame, prefix: str, skip: Iterable[str] = ()
) -> pd.DataFrame:
    return df.rename(
        columns={c: c.removeprefix(prefix) for c in get_cols_by_prefix(df, prefix, skip)}
    )


def strip_col_prefixes_batch(
    df: pd.DataFrame,
    prefix_map: Mapping[str, Iterable[str]] | None = None,
) -> pd.DataFrame:
    if not prefix_map:
        return df

    sorted_items = sorted(prefix_map.items(), key=lambda x: len(x[0]), reverse=True)

    working = df
    for prefix, skip in sorted_items:
        working = strip_col_prefixes(working, prefix, skip)
    return working


def move_cols_to_beginning(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df.loc[:, [*_contained_columns(df, cols), *_remaining_columns(df, cols)]]


def move_numeric_cols_to_end(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    return df.loc[:, [*_remaining_columns(df, numeric_columns), *numeric_columns]]


def move_cols_with_prefix_to_end(
    df: pd.DataFrame, prefix: str, skip: Iterable[str] = ()
) -> pd.DataFrame:
    target_columns = get_cols_by_prefix(df, prefix, skip)
    return df.loc[:, [*_remaining_columns(df, target_columns), *target_columns]]


def drop_all_null_cols(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    object_cols = working.select_dtypes(include=["object", "string"])
    blank_mask = pd.DataFrame(False, index=working.index, columns=working.columns)
    if not object_cols.empty:
        string_cols = [c for c, col in object_cols.items() if is_string_series(col)]
        if string_cols:
            blank_mask[string_cols] = object_cols[string_cols].apply(
                lambda col: col.str.strip() == ""
            )
    working = working.mask(blank_mask, other=pd.NA)
    return working.dropna(axis=1, how="all")
