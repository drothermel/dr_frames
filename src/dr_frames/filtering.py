from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

import pandas as pd

__all__ = [
    "select_subset",
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
    return df.loc[mask].copy()


def filter_to_values(
    df: pd.DataFrame, column: str, values: Sequence[float | str | None]
) -> pd.DataFrame:
    """Filter to rows matching any value in list. Use None in list to include NaN."""
    if None in values:
        other_values = [v for v in values if v is not None]
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
