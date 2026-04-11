from __future__ import annotations

import pandas as pd
import pytest

from dr_frames import get_constant_cols, get_groupwise_constant_cols


def test_get_constant_cols():
    df = pd.DataFrame({"a": [1, 1, 1], "b": [1, 2, 3], "c": ["x", "x", "x"]})
    result = get_constant_cols(df)
    assert result == {"a": 1, "c": "x"}


def test_get_constant_cols_empty_df():
    df = pd.DataFrame()
    result = get_constant_cols(df)
    assert result == {}


def test_get_constant_cols_single_row():
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = get_constant_cols(df)
    assert result == {}


def test_get_groupwise_constant_cols():
    df = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "dataset": ["c4", "c4", "pile", "pile"],
            "label": ["x", "y", "x", "y"],
            "seed": [1, 2, 1, 2],
        }
    )
    result = get_groupwise_constant_cols(df, ["group"], ["dataset", "label", "seed"])
    assert result == ["dataset"]


def test_get_groupwise_constant_cols_skips_missing_candidates():
    df = pd.DataFrame({"group": ["a", "a"], "dataset": ["c4", "c4"]})
    result = get_groupwise_constant_cols(df, ["group"], ["dataset", "missing"])
    assert result == ["dataset"]


def test_get_groupwise_constant_cols_raises_without_valid_group_cols():
    df = pd.DataFrame({"dataset": ["c4", "c4"]})
    with pytest.raises(
        ValueError,
        match="At least one grouping column must be present in the dataframe",
    ):
        get_groupwise_constant_cols(df, ["group"], ["dataset"])
