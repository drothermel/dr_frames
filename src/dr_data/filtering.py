from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, cast

import pandas as pd

__all__ = [
    "select_subset",
    "apply_filters_to_df",
    "filter_to_value",
    "filter_to_values",
    "filter_to_range",
    "filter_to_best_metric",
    "make_filter_fxn",
]


def select_subset(
    df: pd.DataFrame,
    filters: Mapping[str, Any] | list[tuple[str, Any]] | None = None,
) -> pd.DataFrame:
    if filters is None:
        filters = []
    items = filters.items() if isinstance(filters, Mapping) else filters
    mask = pd.Series(True, index=df.index)
    for column, value in items:
        assert column in df.columns, f"Column '{column}' not present in DataFrame."
        if value is None or (isinstance(value, float) and pd.isna(value)):
            mask &= df[column].isna()
        else:
            mask &= df[column] == value
    return df.loc[mask]


def apply_filters_to_df(
    df: pd.DataFrame, filters: dict[str, Sequence[Any]]
) -> pd.DataFrame:
    df = df.copy()
    avail_cols = set(df.columns.tolist())
    for k, v in filters.items():
        if k not in avail_cols:
            continue
        df = cast(pd.DataFrame, df[df[k].isin(v)])
    return df.reset_index(drop=True)


def filter_to_value(df: pd.DataFrame, column: str, value: float | str) -> pd.DataFrame:
    if value == "none":
        return df[df[column].isna()].copy()
    return df[df[column] == value].copy()


def filter_to_values(
    df: pd.DataFrame, column: str, values: list[float | str]
) -> pd.DataFrame:
    if "none" in values:
        other_values = [v for v in values if v != "none"]
        mask = df[column].isna() | df[column].isin(other_values)
    else:
        mask = df[column].isin(values)
    return df[mask].copy()


def filter_to_range(
    df: pd.DataFrame, column: str, min_val: float, max_val: float
) -> pd.DataFrame:
    return df[(df[column] >= min_val) & (df[column] <= max_val)].copy()


def filter_to_best_metric(
    df: pd.DataFrame,
    group_cols: list[str],
    metric_col: str,
    lower_is_better: bool = True,
) -> pd.DataFrame:
    if lower_is_better:
        idx = df.groupby(group_cols)[metric_col].idxmin()
    else:
        idx = df.groupby(group_cols)[metric_col].idxmax()
    return df.loc[idx].copy()


def make_filter_fxn(
    filters: list[tuple[Callable, ...]],
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    def apply(df: pd.DataFrame) -> pd.DataFrame:
        for fn, *args in filters:
            df = fn(df, *args)
        return df

    return apply
