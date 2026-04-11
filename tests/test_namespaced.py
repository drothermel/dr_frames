from __future__ import annotations

from typing import Any, cast

import pandas as pd

from dr_frames import group_namespaced_values
from dr_frames.primitives.namespaced import (
    group_namespaced_values as group_namespaced_values_from_module,
)


def test_group_namespaced_values():
    df = pd.DataFrame({"name": ["apple_1", "banana_2", "cherry_3", None]})
    prefix_map = {"apple": "fruit_a", "banana": "fruit_b"}
    result = group_namespaced_values(df, "name", prefix_map, output_col="group")
    assert result.iloc[0] == "fruit_a"
    assert result.iloc[1] == "fruit_b"
    assert result.iloc[2] == "cherry_3"
    assert pd.isna(result.iloc[3])


def test_group_namespaced_values_empty_map():
    df = pd.DataFrame({"name": ["apple", "banana"]})
    result = group_namespaced_values(df, "name", None, output_col="group")
    assert list(result) == ["apple", "banana"]


def test_group_namespaced_values_prefers_longest_prefix_and_tuple_input():
    df = pd.DataFrame({"name": ["model/base/run", "model/run"]})
    result = group_namespaced_values(
        df,
        "name",
        [("model/", "generic"), ("model/base/", "base")],
        output_col="group",
    )
    assert list(result) == ["base", "generic"]


def test_group_namespaced_values_raises_for_invalid_prefix_items():
    df = pd.DataFrame({"name": ["apple"]})
    try:
        group_namespaced_values(
            df,
            "name",
            cast(Any, [(1, "fruit")]),
            output_col="group",
        )
    except AssertionError as exc:
        assert "Prefix keys must be strings" in str(exc)
    else:
        raise AssertionError("Expected AssertionError")


def test_group_namespaced_values_module_export_matches_top_level():
    assert group_namespaced_values_from_module is group_namespaced_values
