from __future__ import annotations

import pandas as pd

__all__ = ["select_best_by_metric"]


def select_best_by_metric(
    df: pd.DataFrame,
    group_cols: list[str],
    metric_col: str,
    lower_is_better: bool = True,
) -> pd.DataFrame:
    if lower_is_better:
        idx = df.groupby(group_cols)[metric_col].idxmin()
    else:
        idx = df.groupby(group_cols)[metric_col].idxmax()
    return df.loc[idx].copy()
