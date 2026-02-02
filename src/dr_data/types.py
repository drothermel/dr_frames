from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import cast

import numpy as np
import pandas as pd

__all__ = [
    "coerce_numeric_cols",
    "coerce_string_cols",
    "is_string_series",
]


def is_string_series(series: pd.Series) -> bool:
    return bool(series.dropna().map(lambda x: isinstance(x, str)).all())


def coerce_numeric_cols(
    df: pd.DataFrame,
    columns: Sequence[str] | Iterable[str],
    dtype: type[float] | type[int] = float,
) -> pd.DataFrame:
    columns_list = list(columns)
    if not columns_list:
        return df
    working = df.copy()
    for c in columns_list:
        if c not in working.columns:
            continue
        coerced = cast(pd.Series, pd.to_numeric(working[c], errors="coerce"))
        if dtype is int:
            non_null = coerced.dropna()
            assert np.isclose(non_null, non_null.astype(int)).all(), (
                f"Column '{c}' contains non-integer values after coercion."
            )
            target_dtype: object = "Int64" if coerced.isna().any() else int
        else:
            target_dtype = dtype
        working[c] = coerced.astype(target_dtype)
    return working


def coerce_string_cols(
    df: pd.DataFrame,
    columns: Sequence[str] | Iterable[str],
) -> pd.DataFrame:
    columns_list = list(columns)
    if not columns_list:
        return df
    working = df.copy()
    for c in columns_list:
        if c not in working.columns:
            continue
        working[c] = working[c].astype("string")
    return working
