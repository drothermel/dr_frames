from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd

from .columns import move_cols_to_beginning, move_cols_with_prefix_to_end

__all__ = [
    "aggregate_by_group",
    "aggregate_over_seeds",
    "unique_non_null",
    "unique_by_col",
    "unique_by_cols",
    "get_constant_cols",
]


def unique_non_null(values: pd.Series | Iterable[Any]) -> list[Any]:
    series = values if isinstance(values, pd.Series) else pd.Series(list(values))
    return series.dropna().unique().tolist()


def unique_by_col(df: pd.DataFrame, col: str) -> list[Any]:
    return df[col].unique().tolist()


def unique_by_cols(df: pd.DataFrame, cols: Sequence[str]) -> dict[str, Any]:
    contained = [col for col in cols if col in df.columns]
    return {col: unique_by_col(df, col) for col in contained}


def get_constant_cols(df: pd.DataFrame, skip: Iterable[str] = ()) -> dict[str, Any]:
    if df.empty or len(df) <= 1:
        return {}
    skip_set = set(skip)
    return {
        c: df[c].iloc[0]
        for c in df.columns
        if c not in skip_set
        if df[c].nunique(dropna=False) <= 1
    }


def _validate_group_columns(df: pd.DataFrame, group_cols: Sequence[str]) -> list[str]:
    valid_group_cols = [column for column in group_cols if column in df.columns]
    if not valid_group_cols:
        raise ValueError("At least one grouping column must be present in the dataframe.")
    return valid_group_cols


def _constant_value_columns(
    df: pd.DataFrame,
    group_cols: Sequence[str],
    candidate_cols: Sequence[str],
) -> list[str]:
    if not candidate_cols:
        return []

    varying_cols = [
        column
        for column in candidate_cols
        if df.groupby(list(group_cols), dropna=False)[column].nunique(dropna=False).gt(1).any()
    ]
    if varying_cols:
        raise ValueError(
            "Non-numeric columns must be constant within each group: "
            + ", ".join(sorted(varying_cols))
        )
    return list(candidate_cols)


def aggregate_by_group(
    df: pd.DataFrame,
    group_col: str,
    exclude_cols: Sequence[str] | None = None,
    start_cols: Sequence[str] | None = None,
    sort_cols: Sequence[str] | None = None,
    end_prefix: str = "metrics_",
) -> pd.DataFrame:
    if df.empty:
        return df
    if group_col not in df.columns:
        raise ValueError(f"Group column '{group_col}' not found in dataframe.")
    if group_col in (exclude_cols or []):
        raise ValueError(f"Group column '{group_col}' cannot be in exclude_cols.")

    cols_to_drop = set(exclude_cols or [])
    numeric_cols = set(df.select_dtypes(include=["number"]).columns.tolist())
    cols_to_use = set(df.columns) - cols_to_drop - {group_col}
    mean_agg_cols = numeric_cols & cols_to_use
    first_agg_candidates = [
        column for column in df.columns if column in cols_to_use - mean_agg_cols
    ]
    first_agg_cols = _constant_value_columns(df, [group_col], first_agg_candidates)

    df = df.copy()
    df = df.drop(columns=list(cols_to_drop))
    if not mean_agg_cols and not first_agg_cols:
        result = df[[group_col]].drop_duplicates().reset_index(drop=True)
        if sort_cols:
            result = result.sort_values(list(sort_cols))
        return result
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
    seed_col: str = "seed",
    metric_cols: list[str] | None = None,
    agg_funcs: list[str] | None = None,
) -> pd.DataFrame:
    if not config_cols:
        raise ValueError("config_cols must be provided")
    if seed_col not in df.columns:
        raise ValueError(f"Seed column '{seed_col}' not found in dataframe.")
    if seed_col in config_cols:
        raise ValueError(f"Seed column '{seed_col}' cannot be included in config_cols.")

    if agg_funcs is None:
        agg_funcs = ["mean", "std", "count"]

    if metric_cols is None:
        metric_cols = [col for col in df.columns if col.startswith("eval/")]

    valid_config_cols = _validate_group_columns(df, config_cols)
    valid_metric_cols = [metric for metric in metric_cols if metric in df.columns]
    if not valid_metric_cols:
        raise ValueError("No metric columns found for aggregation.")

    duplicate_seed_counts = (
        df.groupby([*valid_config_cols, seed_col], dropna=False)
        .size()
        .gt(1)
    )
    if duplicate_seed_counts.any():
        raise ValueError(
            "Each seed must appear at most once within a configuration group."
        )

    passthrough_candidates = [
        column
        for column in df.columns
        if column not in {*valid_config_cols, seed_col, *valid_metric_cols}
    ]
    passthrough_cols = _constant_value_columns(
        df,
        valid_config_cols,
        passthrough_candidates,
    )

    agg_dict: dict[str, str | list[str]] = {
        **{metric: agg_funcs for metric in valid_metric_cols},
        **{column: "first" for column in passthrough_cols},
    }

    aggregated = df.groupby(valid_config_cols, dropna=False).agg(agg_dict)
    aggregated.columns = [
        column if agg == "first" and column in passthrough_cols else f"{column}_{agg}"
        for column, agg in aggregated.columns
    ]

    aggregated = aggregated.reset_index()
    metric_output_cols = [
        f"{metric}_{agg}" for metric in valid_metric_cols for agg in agg_funcs
    ]
    ordered_cols = [*valid_config_cols, *passthrough_cols, *metric_output_cols]
    return aggregated.loc[:, ordered_cols]
