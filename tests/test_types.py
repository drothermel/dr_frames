from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dr_frames.types import coerce_numeric_cols, coerce_string_cols, is_string_series


def test_is_string_series():
    assert is_string_series(pd.Series(["a", "b", "c"]))
    assert is_string_series(pd.Series(["a", None, "c"]))
    assert not is_string_series(pd.Series([1, 2, 3]))
    # Edge case: empty Series
    assert not is_string_series(pd.Series([]))
    assert not is_string_series(pd.Series(dtype=object))
    # Edge case: all-null Series
    assert not is_string_series(pd.Series([None, None]))
    assert not is_string_series(pd.Series([np.nan, np.nan]))


def test_coerce_numeric_cols():
    df = pd.DataFrame({"a": ["1.0", "2.0", "3.0"], "b": ["x", "y", "z"]})
    result = coerce_numeric_cols(df, ["a"])
    assert result["a"].dtype == float
    assert list(result["a"]) == [1.0, 2.0, 3.0]


def test_coerce_numeric_cols_int():
    df = pd.DataFrame({"a": ["1", "2", "3"]})
    result = coerce_numeric_cols(df, ["a"], dtype=int)
    assert result["a"].dtype == int


def test_coerce_numeric_cols_int_with_nulls():
    df = pd.DataFrame({"a": ["1", None, "3"]})
    result = coerce_numeric_cols(df, ["a"], dtype=int)
    assert result["a"].dtype == "Int64"


def test_coerce_numeric_cols_invalid_int():
    df = pd.DataFrame({"a": ["1.5", "2.5", "3.5"]})
    with pytest.raises(ValueError):
        coerce_numeric_cols(df, ["a"], dtype=int)


def test_coerce_numeric_cols_missing_column():
    df = pd.DataFrame({"a": ["1", "2", "3"]})
    result = coerce_numeric_cols(df, ["b"])
    assert "a" in result.columns


def test_coerce_string_cols():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [1.0, 2.0, 3.0]})
    result = coerce_string_cols(df, ["a", "b"])
    assert result["a"].dtype == "string"
    assert result["b"].dtype == "string"


def test_coerce_string_cols_missing_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = coerce_string_cols(df, ["b"])
    assert result["a"].dtype == df["a"].dtype
