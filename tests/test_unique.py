from __future__ import annotations

import pandas as pd

from dr_frames import unique_by_col, unique_by_cols, unique_non_null


def test_unique_non_null():
    series = pd.Series([1, None, 2, None, 1])
    result = unique_non_null(series)
    assert set(result) == {1, 2}


def test_unique_non_null_with_list():
    result = unique_non_null([1, None, 2, None, 1])
    assert set(result) == {1, 2}


def test_unique_by_col(sample_df: pd.DataFrame):
    result = unique_by_col(sample_df, "category")
    assert set(result) == {"x", "y"}


def test_unique_by_cols(sample_df: pd.DataFrame):
    result = unique_by_cols(sample_df, ["category", "name"])
    assert set(result["category"]) == {"x", "y"}
    assert set(result["name"]) == {"alice", "bob", "charlie"}


def test_unique_by_cols_skips_missing_columns(sample_df: pd.DataFrame):
    result = unique_by_cols(sample_df, ["category", "missing"])
    assert list(result.keys()) == ["category"]
