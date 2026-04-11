from __future__ import annotations

import pandas as pd

__all__ = ["select_best_by_metric"]


def select_best_by_metric(
    df: pd.DataFrame,
    group_cols: list[str],
    metric_col: str,
    lower_is_better: bool = True,
) -> pd.DataFrame:
    valid_rows = df[df[metric_col].notna()]
    if valid_rows.empty:
        return valid_rows.copy()

    if lower_is_better:
        idx = valid_rows.groupby(group_cols)[metric_col].idxmin()
    else:
        idx = valid_rows.groupby(group_cols)[metric_col].idxmax()
    valid_idx = idx.dropna().astype(int)
    return df.loc[valid_idx].copy()
