from __future__ import annotations

import pandas as pd
import pytest

from dr_frames.coerce import coerce_numeric_cols, coerce_string_cols


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


def test_coerce_numeric_cols_nullable_integer_dtype_string():
    df = pd.DataFrame({"a": ["1", None, "3"]})
    result = coerce_numeric_cols(df, ["a"], dtype="Int64")
    assert result["a"].dtype == "Int64"


def test_coerce_numeric_cols_non_nullable_integer_dtype_string_with_nulls():
    df = pd.DataFrame({"a": ["1", None, "3"]})
    with pytest.raises(ValueError, match="nullable integer dtype"):
        coerce_numeric_cols(df, ["a"], dtype="int64")


def test_coerce_numeric_cols_invalid_int():
    df = pd.DataFrame({"a": ["1.5", "2.5", "3.5"]})
    with pytest.raises(ValueError):
        coerce_numeric_cols(df, ["a"], dtype=int)


def test_coerce_numeric_cols_float_dtype_string():
    df = pd.DataFrame({"a": ["1.0", "2.5", None]})
    result = coerce_numeric_cols(df, ["a"], dtype="Float64")
    assert result["a"].dtype == "Float64"


def test_coerce_numeric_cols_raise_errors():
    df = pd.DataFrame({"a": ["1", "not-a-number", "3"]})
    with pytest.raises(ValueError):
        coerce_numeric_cols(df, ["a"], errors="raise")


def test_coerce_numeric_cols_downcast_float():
    df = pd.DataFrame({"a": ["1.0", "2.0", "3.0"]})
    result = coerce_numeric_cols(df, ["a"], downcast="float")
    assert result["a"].dtype == "float32"


def test_coerce_numeric_cols_downcast_integer():
    df = pd.DataFrame({"a": ["1", "2", "3"]})
    result = coerce_numeric_cols(df, ["a"], dtype=int, downcast="integer")
    assert str(result["a"].dtype).startswith("int")


def test_coerce_numeric_cols_missing_column():
    df = pd.DataFrame({"a": ["1", "2", "3"]})
    result = coerce_numeric_cols(df, ["b"])
    assert "a" in result.columns


def test_coerce_string_cols():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [1.0, 2.0, 3.0], "c": [None, "x", None]})
    result = coerce_string_cols(df, ["a", "b"])
    assert result["a"].dtype == "string"
    assert result["b"].dtype == "string"
    assert pd.isna(result.loc[0, "c"])


def test_coerce_string_cols_with_null_fill():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = coerce_string_cols(df, ["a"], null_value="")
    assert result["a"].dtype == "string"
    assert result["a"].tolist() == ["1.0", "", "3.0"]


def test_coerce_string_cols_missing_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = coerce_string_cols(df, ["b"])
    assert result["a"].dtype == df["a"].dtype
