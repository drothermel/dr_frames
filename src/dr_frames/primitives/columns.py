from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Literal

import pandas as pd

from .constant import get_constant_cols

__all__ = [
    "get_cols_by_prefix",
    "get_cols_by_contains",
    "rename_columns",
    "strip_col_prefixes",
    "move_cols_to_beginning",
    "move_numeric_cols_to_end",
    "move_cols_with_prefix_to_end",
    "drop_all_null_cols",
    "drop_all_constant_cols",
]


def _skip_columns(
    columns: Sequence[str] | pd.Index, skip: Iterable[str] = ()
) -> list[str]:
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
        columns={
            c: c.removeprefix(prefix) for c in get_cols_by_prefix(df, prefix, skip)
        }
    )


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


def _all_non_null_values_are_strings(series: pd.Series) -> bool:
    non_null = series.dropna()
    return (
        not non_null.empty and non_null.map(lambda value: isinstance(value, str)).all()
    )


def _contains_any_strings(series: pd.Series) -> bool:
    non_null = series.dropna()
    return (
        not non_null.empty and non_null.map(lambda value: isinstance(value, str)).any()
    )


def drop_all_null_cols(
    df: pd.DataFrame,
    *,
    treat_blank_strings_as_null: bool = True,
    blank_string_mode: Literal["string_only", "string_like"] = "string_only",
    allow_mixed_object_string_cleanup: bool = False,
) -> pd.DataFrame:
    """Drop columns that are empty after optional blank-string normalization.

    By default, the function first treats blank or whitespace-only strings as
    missing values, but only for `object` and pandas `string` columns whose
    non-null values are all strings. It then drops any columns that are entirely
    missing.

    `blank_string_mode` controls which columns are eligible for blank-string
    normalization:
    - `"string_only"`: only inspect `object` and pandas `string` columns.
    - `"string_like"`: inspect any column whose non-null values are all strings,
      including string-valued categoricals.

    `allow_mixed_object_string_cleanup` widens the `"string_only"` behavior for
    `object` columns. When enabled, blank strings inside mixed-type `object`
    columns are also converted to missing values before all-null columns are
    dropped.
    """
    working = df.copy()
    if treat_blank_strings_as_null:
        if blank_string_mode == "string_only":
            candidate_cols = working.select_dtypes(include=["object", "string"]).columns
        else:
            candidate_cols = working.columns

        cols_to_clean: list[str] = []
        for column in candidate_cols:
            series = working[column]
            if _all_non_null_values_are_strings(series):
                cols_to_clean.append(column)
                continue
            if (
                allow_mixed_object_string_cleanup
                and series.dtype == object
                and _contains_any_strings(series)
            ):
                cols_to_clean.append(column)

        for column in cols_to_clean:
            working[column] = working[column].mask(
                working[column].map(
                    lambda value: isinstance(value, str) and value.strip() == ""
                ),
                other=pd.NA,
            )
    return working.dropna(axis=1, how="all")


def drop_all_constant_cols(
    df: pd.DataFrame,
    skip: Iterable[str] = (),
) -> pd.DataFrame:
    constant_cols = list(get_constant_cols(df, skip=skip).keys())
    return df.drop(columns=constant_cols)
