from __future__ import annotations

import pandas as pd

from dr_frames.primitives.columns import (
    drop_all_constant_cols,
    drop_all_null_cols,
    get_cols_by_contains,
    get_cols_by_prefix,
    move_cols_to_beginning,
    move_cols_with_prefix_to_end,
    move_numeric_cols_to_end,
    strip_col_prefixes,
)


def test_get_cols_by_prefix(sample_df: pd.DataFrame):
    result = get_cols_by_prefix(sample_df, "prefix_")
    assert result == ["prefix_col1", "prefix_col2"]


def test_get_cols_by_prefix_with_skip(sample_df: pd.DataFrame):
    result = get_cols_by_prefix(sample_df, "prefix_", skip=["prefix_col1"])
    assert result == ["prefix_col2"]


def test_get_cols_by_contains(sample_df: pd.DataFrame):
    result = get_cols_by_contains(sample_df, "col")
    assert "prefix_col1" in result
    assert "prefix_col2" in result


def test_strip_col_prefixes(sample_df: pd.DataFrame):
    result = strip_col_prefixes(sample_df, "prefix_")
    assert "col1" in result.columns
    assert "col2" in result.columns
    assert "prefix_col1" not in result.columns


def test_move_cols_to_beginning(sample_df: pd.DataFrame):
    result = move_cols_to_beginning(sample_df, ["other", "category"])
    assert list(result.columns)[:2] == ["other", "category"]


def test_move_numeric_cols_to_end(sample_df: pd.DataFrame):
    result = move_numeric_cols_to_end(sample_df)
    numeric_cols = result.select_dtypes(include=["number"]).columns.tolist()
    assert list(result.columns)[-len(numeric_cols) :] == numeric_cols


def test_move_cols_with_prefix_to_end(sample_df: pd.DataFrame):
    result = move_cols_with_prefix_to_end(sample_df, "prefix_")
    assert list(result.columns)[-2:] == ["prefix_col1", "prefix_col2"]


def test_drop_all_null_cols(df_with_nulls: pd.DataFrame):
    result = drop_all_null_cols(df_with_nulls)
    assert "c" not in result.columns
    assert "a" in result.columns
    assert "b" in result.columns


def test_drop_all_null_cols_with_blank_strings():
    df = pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["", "  ", ""],
            "c": ["x", "y", "z"],
        }
    )
    result = drop_all_null_cols(df)
    assert "b" not in result.columns
    assert "a" in result.columns
    assert "c" in result.columns


def test_drop_all_null_cols_can_preserve_blank_only_string_columns():
    df = pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["", "  ", ""],
        }
    )
    result = drop_all_null_cols(df, treat_blank_strings_as_null=False)
    assert "a" in result.columns
    assert "b" in result.columns


def test_drop_all_null_cols_string_like_mode_handles_categorical_strings():
    df = pd.DataFrame(
        {
            "a": pd.Series(["", "   ", ""], dtype="category"),
            "b": [1, 2, 3],
        }
    )
    result = drop_all_null_cols(df, blank_string_mode="string_like")
    assert "a" not in result.columns
    assert "b" in result.columns


def test_drop_all_null_cols_can_clean_blank_strings_in_mixed_object_columns():
    df = pd.DataFrame(
        {
            "a": ["", 1, None],
            "b": [1, 2, 3],
        }
    )
    result = drop_all_null_cols(df, allow_mixed_object_string_cleanup=True)
    assert pd.isna(result.loc[0, "a"])
    assert result.loc[1, "a"] == 1


def test_drop_all_constant_cols():
    df = pd.DataFrame(
        {
            "constant": [1, 1, 1],
            "varying": [1, 2, 3],
            "all_null": [None, None, None],
        }
    )
    result = drop_all_constant_cols(df)
    assert "constant" not in result.columns
    assert "all_null" not in result.columns
    assert "varying" in result.columns


def test_drop_all_constant_cols_with_skip():
    df = pd.DataFrame(
        {
            "constant": [1, 1, 1],
            "varying": [1, 2, 3],
        }
    )
    result = drop_all_constant_cols(df, skip=["constant"])
    assert "constant" in result.columns
    assert "varying" in result.columns
