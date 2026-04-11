from __future__ import annotations

from typing import Any

import pandas as pd

__all__ = ["masked_getter", "masked_setter"]


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
