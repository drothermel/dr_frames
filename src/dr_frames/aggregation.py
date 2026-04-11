from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from .columns import move_cols_to_beginning, move_cols_with_prefix_to_end
from .constant import get_groupwise_constant_cols

__all__ = [
    "aggregate_by_group",
    "aggregate_over_seeds",
]


def _validate_group_columns(df: pd.DataFrame, group_cols: Sequence[str]) -> list[str]:
    valid_group_cols = [column for column in group_cols if column in df.columns]
    if not valid_group_cols:
        raise ValueError("At least one grouping column must be present in the dataframe.")
    return valid_group_cols


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
    first_agg_cols = get_groupwise_constant_cols(df, [group_col], first_agg_candidates)
    varying_first_cols = sorted(set(first_agg_candidates) - set(first_agg_cols))
    if varying_first_cols:
        raise ValueError(
            "Non-numeric columns must be constant within each group: "
            + ", ".join(varying_first_cols)
        )

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
    passthrough_cols = get_groupwise_constant_cols(
        df,
        valid_config_cols,
        passthrough_candidates,
    )
    varying_passthrough_cols = sorted(set(passthrough_candidates) - set(passthrough_cols))
    if varying_passthrough_cols:
        raise ValueError(
            "Non-numeric columns must be constant within each group: "
            + ", ".join(varying_passthrough_cols)
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
