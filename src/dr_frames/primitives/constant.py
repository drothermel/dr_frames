from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd

__all__ = ["get_constant_cols", "get_groupwise_constant_cols"]


def get_constant_cols(df: pd.DataFrame, skip: Iterable[str] = ()) -> dict[str, Any]:
    if df.empty or len(df) <= 1:
        return {}
    skip_set = set(skip)
    return {
        column: df[column].iloc[0]
        for column in df.columns
        if column not in skip_set
        if df[column].nunique(dropna=False) <= 1
    }


def get_groupwise_constant_cols(
    df: pd.DataFrame,
    group_cols: Sequence[str],
    candidate_cols: Sequence[str],
) -> list[str]:
    if not candidate_cols:
        return []

    valid_group_cols = [column for column in group_cols if column in df.columns]
    if not valid_group_cols:
        raise ValueError(
            "At least one grouping column must be present in the dataframe."
        )

    valid_candidate_cols = [
        column
        for column in candidate_cols
        if column in df.columns and column not in valid_group_cols
    ]
    if not valid_candidate_cols:
        return []

    return [
        column
        for column in valid_candidate_cols
        if not df.groupby(valid_group_cols, dropna=False)[column]
        .nunique(dropna=False)
        .gt(1)
        .any()
    ]
