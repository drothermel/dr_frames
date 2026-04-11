from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

import pandas as pd

__all__ = ["maybe_pipe"]


def maybe_pipe(
    df: pd.DataFrame,
    condition: bool | Callable[[pd.DataFrame], bool] | Iterable | Mapping,
    func: Callable[..., pd.DataFrame],
    *args: Any,
    **kwargs: Any,
) -> pd.DataFrame:
    if callable(condition):
        should_apply = condition(df)
    elif isinstance(condition, (pd.Series, pd.DataFrame)):
        should_apply = not condition.empty
    elif hasattr(condition, "size"):
        should_apply = bool(getattr(condition, "size", 0)) and condition.size != 0
    else:
        should_apply = bool(condition)
    return df.pipe(func, *args, **kwargs) if should_apply else df
