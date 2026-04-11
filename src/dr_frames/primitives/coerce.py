from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Literal, cast

import numpy as np
import pandas as pd

__all__ = [
    "coerce_numeric_cols",
    "coerce_string_cols",
]


def _resolve_numeric_dtype(
    dtype: str | type[int] | type[float],
) -> tuple[object | None, bool]:
    if dtype is int:
        return None, True
    if dtype is float:
        return float, False
    if isinstance(dtype, str):
        normalized = dtype.strip()
        lowered = normalized.lower()
        if lowered == "int":
            return None, True
        if lowered == "float":
            return float, False
        if lowered.startswith(("int", "uint")):
            return normalized, True
        if lowered.startswith("float"):
            return normalized, False
    raise TypeError(
        "dtype must be int, float, or a numeric dtype string such as "
        "'Int64', 'int64', 'Float64', or 'float64'."
    )


def coerce_numeric_cols(
    df: pd.DataFrame,
    columns: Sequence[str] | Iterable[str],
    dtype: str | type[float] | type[int] = float,
    *,
    errors: Literal["coerce", "raise"] = "coerce",
    downcast: Literal["integer", "float"] | None = None,
) -> pd.DataFrame:
    resolved_dtype, requires_integral_values = _resolve_numeric_dtype(dtype)
    columns_list = list(columns)
    working = df.copy()
    if not columns_list:
        return working
    for c in columns_list:
        if c not in working.columns:
            continue
        coerced = cast(
            pd.Series,
            pd.to_numeric(working[c], errors=errors, downcast=downcast),
        )
        if requires_integral_values:
            non_null = coerced.dropna()
            if not np.isclose(non_null, non_null.astype(int)).all():
                raise ValueError(
                    f"Column '{c}' contains non-integer values after coercion."
                )
            if resolved_dtype is None:
                if coerced.isna().any():
                    target_dtype: object = "Int64"
                elif downcast == "integer" and pd.api.types.is_integer_dtype(
                    coerced.dtype
                ):
                    target_dtype = coerced.dtype
                else:
                    target_dtype = int
            else:
                target_dtype = resolved_dtype
                if (
                    coerced.isna().any()
                    and isinstance(target_dtype, str)
                    and target_dtype.lower().startswith(("int", "uint"))
                    and not target_dtype.startswith("I")
                ):
                    raise ValueError(
                        f"Column '{c}' contains nulls after coercion; "
                        f"use a nullable integer dtype such as 'Int64'."
                    )
        else:
            if (
                downcast == "float"
                and resolved_dtype is float
                and pd.api.types.is_float_dtype(coerced.dtype)
            ):
                target_dtype = coerced.dtype
            else:
                target_dtype = resolved_dtype
        working[c] = coerced.astype(target_dtype)
    return working


def coerce_string_cols(
    df: pd.DataFrame,
    columns: Sequence[str] | Iterable[str],
    *,
    null_value: str | None = None,
) -> pd.DataFrame:
    columns_list = list(columns)
    if not columns_list:
        return df.copy()
    working = df.copy()
    for c in columns_list:
        if c not in working.columns:
            continue
        working[c] = working[c].astype("string")
        if null_value is not None:
            working[c] = working[c].fillna(null_value)
    return working
