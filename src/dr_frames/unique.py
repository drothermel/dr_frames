from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd

__all__ = ["unique_non_null", "unique_by_col", "unique_by_cols"]


def unique_non_null(values: pd.Series | Iterable[Any]) -> list[Any]:
    series = values if isinstance(values, pd.Series) else pd.Series(list(values))
    return series.dropna().unique().tolist()


def unique_by_col(df: pd.DataFrame, col: str) -> list[Any]:
    return df[col].unique().tolist()


def unique_by_cols(df: pd.DataFrame, cols: Sequence[str]) -> dict[str, Any]:
    contained = [col for col in cols if col in df.columns]
    return {col: unique_by_col(df, col) for col in contained}
