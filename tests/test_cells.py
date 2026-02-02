from __future__ import annotations

import pandas as pd
import pytest

from dr_data.cells import (
    apply_column_converters,
    apply_if_column,
    ensure_column,
    fill_missing_values,
    force_set_cell,
    group_col_by_prefix,
    map_column_with_fallback,
    masked_getter,
    masked_setter,
    maybe_update_cell,
    rename_columns,
    require_row_index,
)


def test_ensure_column_new():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = ensure_column(df, "b", 0)
    assert "b" in result.columns
    assert list(result["b"]) == [0, 0, 0]


def test_ensure_column_existing_fillna():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = ensure_column(df, "a", 0)
    assert list(result["a"]) == [1.0, 0.0, 3.0]


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


def test_map_column_with_fallback():
    df = pd.DataFrame({"a": ["x", "y", "z"]})
    result = map_column_with_fallback(df, "a", {"x": "X", "y": "Y"})
    assert list(result["a"]) == ["X", "Y", "z"]


def test_map_column_with_fallback_missing_column():
    df = pd.DataFrame({"a": [1, 2]})
    result = map_column_with_fallback(df, "b", {"x": "X"})
    assert "a" in result.columns


def test_apply_column_converters():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    result = apply_column_converters(df, {"a": lambda x: x * 2, "b": str.upper})
    assert list(result["a"]) == [2, 4, 6]
    assert list(result["b"]) == ["X", "Y", "Z"]


def test_maybe_update_cell():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = maybe_update_cell(df, 1, "a", 999)
    assert result.loc[1, "a"] == 999
    result2 = maybe_update_cell(df, 0, "a", 888)
    assert result2.loc[0, "a"] == 1


def test_force_set_cell():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = force_set_cell(df, 1, "a", 999)
    assert result.loc[1, "a"] == 999


def test_force_set_cell_new_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = force_set_cell(df, 1, "b", 999, default=0)
    assert "b" in result.columns
    assert result.loc[1, "b"] == 999


def test_apply_if_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = apply_if_column(df, "a", lambda s: s * 2)
    assert list(result["a"]) == [2, 4, 6]


def test_apply_if_column_missing():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = apply_if_column(df, "b", lambda s: s * 2)
    assert "a" in result.columns
    assert "b" not in result.columns


def test_require_row_index():
    df = pd.DataFrame({"a": ["x", "y", "z"]})
    idx = require_row_index(df, "a", "y")
    assert idx == 1


def test_require_row_index_not_found():
    df = pd.DataFrame({"a": ["x", "y", "z"]})
    with pytest.raises(AssertionError):
        require_row_index(df, "a", "w")


def test_require_row_index_multiple():
    df = pd.DataFrame({"a": ["x", "x", "z"]})
    with pytest.raises(AssertionError):
        require_row_index(df, "a", "x")


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


def test_group_col_by_prefix():
    df = pd.DataFrame({"name": ["apple_1", "banana_2", "cherry_3", None]})
    prefix_map = {"apple": "fruit_a", "banana": "fruit_b"}
    result = group_col_by_prefix(df, "name", prefix_map, output_col="group")
    assert result.iloc[0] == "fruit_a"
    assert result.iloc[1] == "fruit_b"
    assert result.iloc[2] == "cherry_3"
    assert pd.isna(result.iloc[3])


def test_group_col_by_prefix_empty_map():
    df = pd.DataFrame({"name": ["apple", "banana"]})
    result = group_col_by_prefix(df, "name", None, output_col="group")
    assert list(result) == ["apple", "banana"]
