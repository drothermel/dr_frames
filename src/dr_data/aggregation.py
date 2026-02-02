from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

import pandas as pd

from .columns import (
    apply_skip,
    contained_cols,
    move_cols_to_beginning,
    move_cols_with_prefix_to_end,
)

__all__ = [
    "apply_aggregations",
    "aggregate_over_seeds",
    "unique_non_null",
    "unique_by_col",
    "unique_by_cols",
    "get_constant_cols",
    "fillna_with_defaults",
    "maybe_pipe",
]


def unique_non_null(values: pd.Series | Iterable[Any]) -> list[Any]:
    series = values if isinstance(values, pd.Series) else pd.Series(list(values))
    return series.dropna().unique().tolist()


def unique_by_col(df: pd.DataFrame, col: str) -> list[Any]:
    return df[col].unique().tolist()


def unique_by_cols(df: pd.DataFrame, cols: Sequence[str]) -> dict[str, Any]:
    contained = contained_cols(df, cols)
    return {col: unique_by_col(df, col) for col in contained}


def get_constant_cols(df: pd.DataFrame, skip: Iterable[str] = ()) -> dict[str, Any]:
    if df.empty or len(df) <= 1:
        return {}
    return {
        c: df[c].iloc[0]
        for c in apply_skip(df.columns, skip)
        if df[c].nunique(dropna=False) <= 1
    }


def fillna_with_defaults(
    df: pd.DataFrame,
    defaults: Mapping[str, object] | Iterable[tuple[str, object]],
) -> pd.DataFrame:
    defaults_dict = dict(defaults)
    if not defaults_dict:
        return df
    present = {c: value for c, value in defaults_dict.items() if c in df.columns}
    return df.fillna(value=present) if present else df


def maybe_pipe(
    df: pd.DataFrame,
    condition: bool | Callable[[pd.DataFrame], bool] | Iterable | Mapping,
    func: Callable[..., pd.DataFrame],
    *args: Any,
    **kwargs: Any,
) -> pd.DataFrame:
    should_apply = condition(df) if callable(condition) else bool(condition)
    return df.pipe(func, *args, **kwargs) if should_apply else df


def apply_aggregations(
    df: pd.DataFrame,
    group_col: str,
    agg_over_cols: Sequence[str],
    drop_cols: Sequence[str] | None = None,
    start_cols: Sequence[str] | None = None,
    sort_cols: Sequence[str] | None = None,
    end_prefix: str = "metrics_",
) -> pd.DataFrame:
    if df.empty:
        return df
    if group_col not in df.columns:
        raise ValueError(f"Group column '{group_col}' not found in dataframe.")
    if group_col in (drop_cols or []):
        raise ValueError(f"Group column '{group_col}' cannot be in drop_cols.")

    cols_to_drop = {*(drop_cols or []), *agg_over_cols}
    numeric_cols = set(df.select_dtypes(include=["number"]).columns.tolist())
    cols_to_use = set(df.columns) - cols_to_drop - {group_col}
    mean_agg_cols = numeric_cols & cols_to_use
    first_agg_cols = cols_to_use - mean_agg_cols

    df = df.copy()
    df = df.drop(columns=list(cols_to_drop))
    df = (
        df.groupby(group_col)
        .agg(
            {
                **dict.fromkeys(first_agg_cols, "first"),
                **dict.fromkeys(mean_agg_cols, "mean"),
            }
        )
        .reset_index()
    )
    df = move_cols_with_prefix_to_end(df, prefix=end_prefix)
    df = move_cols_to_beginning(df, [group_col, *(start_cols or [])])
    if sort_cols:
        df = df.sort_values(list(sort_cols))
    return df


def aggregate_over_seeds(
    df: pd.DataFrame,
    config_cols: list[str],
    metric_cols: list[str] | None = None,
    agg_funcs: list[str] | None = None,
) -> pd.DataFrame:
    assert config_cols, "config_cols must be provided"

    if agg_funcs is None:
        agg_funcs = ["mean", "std", "count"]

    if metric_cols is None:
        metric_cols = [col for col in df.columns if col.startswith("eval/")]

    valid_config_cols = [c for c in config_cols if c in df.columns]

    agg_dict = {metric: agg_funcs for metric in metric_cols if metric in df.columns}

    if not agg_dict:
        return df.groupby(valid_config_cols, dropna=False).first().reset_index()

    aggregated = df.groupby(valid_config_cols, dropna=False).agg(agg_dict)
    aggregated.columns = [f"{col}_{agg}" for col, agg in aggregated.columns]

    return aggregated.reset_index()
