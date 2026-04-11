from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

__all__ = [
    "fill_missing_values",
    "rename_columns",
    "masked_getter",
    "masked_setter",
]


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
