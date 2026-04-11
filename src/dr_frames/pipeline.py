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
    should_apply = condition(df) if callable(condition) else bool(condition)
    return df.pipe(func, *args, **kwargs) if should_apply else df
