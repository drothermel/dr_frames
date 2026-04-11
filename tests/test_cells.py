from __future__ import annotations

import pandas as pd

from dr_frames.primitives.columns import rename_columns
from dr_frames.primitives.masked import (
    masked_getter,
    masked_setter,
)
from dr_frames.primitives.missing import fill_missing_values


def test_fill_missing_values():
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, 2, None]})
    result = fill_missing_values(df, {"a": 0, "b": -1})
    assert list(result["a"]) == [1.0, 0.0, 3.0]
    assert list(result["b"]) == [-1.0, 2.0, -1.0]


def test_rename_columns():
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = rename_columns(df, {"a": "x", "c": "y"})
    assert "x" in result.columns
    assert "a" not in result.columns
    assert "b" in result.columns


def test_masked_getter():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    mask = df["a"] == 2
    result = masked_getter(df, mask, "b")
    assert result == "y"


def test_masked_getter_empty():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    mask = df["a"] == 999
    result = masked_getter(df, mask, "b")
    assert result is None


def test_masked_setter():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    original_b = df["b"].copy()
    mask = df["a"] == 2
    result = masked_setter(df, mask, "b", "NEW")
    assert result.loc[1, "b"] == "NEW"
    # Verify original DataFrame is not mutated (default inplace=False)
    assert list(df["b"]) == list(original_b)


def test_masked_setter_inplace():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    mask = df["a"] == 2
    result = masked_setter(df, mask, "b", "NEW", inplace=True)
    assert result.loc[1, "b"] == "NEW"
    # Verify original DataFrame is mutated when inplace=True
    assert df.loc[1, "b"] == "NEW"
    assert result is df
