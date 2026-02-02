from __future__ import annotations

import pandas as pd

from dr_data.profiling import (
    DFColInfo,
    infer_col_name_contains_tags,
    infer_col_name_prefix_tags,
    infer_col_name_suffix_tags,
    infer_series_base_tag_type,
    looks_like_json,
    looks_like_path,
)


def test_looks_like_path():
    extensions = {".json", ".csv", ".parquet"}
    assert looks_like_path("/path/to/file.json", extensions) is True
    assert looks_like_path("file.csv", extensions) is True
    assert looks_like_path("C:\\Users\\file.parquet", extensions) is True
    assert looks_like_path("not_a_path", extensions) is False
    assert looks_like_path("", extensions) is False
    assert looks_like_path(None, extensions) is False


def test_looks_like_json():
    assert looks_like_json('{"key": "value"}') is True
    assert looks_like_json("[1, 2, 3]") is True
    assert looks_like_json("not json") is False
    assert looks_like_json("") is False
    assert looks_like_json(None) is False
    assert looks_like_json("{invalid}") is False


def test_infer_series_base_tag_type():
    type_map = [
        (pd.api.types.is_integer_dtype, ["int", "numeric"]),
        (pd.api.types.is_float_dtype, ["float", "numeric"]),
    ]
    default = ["str"]

    int_series = pd.Series([1, 2, 3])
    float_series = pd.Series([1.0, 2.0, 3.0])
    str_series = pd.Series(["a", "b", "c"])
    nullable_series = pd.Series([1.0, None, 3.0])

    int_tags = infer_series_base_tag_type(int_series, type_map, default)
    assert "int" in int_tags
    assert "numeric" in int_tags

    float_tags = infer_series_base_tag_type(float_series, type_map, default)
    assert "float" in float_tags
    assert "numeric" in float_tags

    str_tags = infer_series_base_tag_type(str_series, type_map, default)
    assert "str" in str_tags

    nullable_tags = infer_series_base_tag_type(nullable_series, type_map, default)
    assert "nullable" in nullable_tags


def test_infer_col_name_contains_tags():
    tag_map = {("config", "settings"): "config", ("metric",): "metric"}

    assert "config" in infer_col_name_contains_tags("my_config_col", tag_map)
    assert "config" in infer_col_name_contains_tags("settings_value", tag_map)
    assert "metric" in infer_col_name_contains_tags("metric_loss", tag_map)
    assert len(infer_col_name_contains_tags("other_col", tag_map)) == 0


def test_infer_col_name_suffix_tags():
    tag_map = {("_path", "_dir"): "path", ("_id",): "id"}

    assert "path" in infer_col_name_suffix_tags("file_path", tag_map)
    assert "path" in infer_col_name_suffix_tags("output_dir", tag_map)
    assert "id" in infer_col_name_suffix_tags("user_id", tag_map)
    assert len(infer_col_name_suffix_tags("other_col", tag_map)) == 0


def test_infer_col_name_prefix_tags():
    tag_map = {("is_", "has_"): "bool_like", ("metric_",): "metric"}

    assert "bool_like" in infer_col_name_prefix_tags("is_active", tag_map)
    assert "bool_like" in infer_col_name_prefix_tags("has_permission", tag_map)
    assert "metric" in infer_col_name_prefix_tags("metric_loss", tag_map)
    assert len(infer_col_name_prefix_tags("other_col", tag_map)) == 0


def test_df_col_info_update_from_df():
    df = pd.DataFrame(
        {
            "is_active": [True, False, True],
            "user_id": [1, 2, 3],
            "config_path": ["/a/b.json", "/c/d.json", "/e/f.json"],
        }
    )
    col_info = DFColInfo()
    col_info.update_from_df(df)

    assert "bool" in col_info.columns["is_active"].tags
    assert "bool_like" in col_info.columns["is_active"].tags
    assert "id" in col_info.columns["user_id"].tags
    assert "path" in col_info.columns["config_path"].tags


def test_df_col_info_names_with_tag():
    df = pd.DataFrame(
        {
            "is_active": [True, False],
            "has_permission": [True, True],
            "name": ["a", "b"],
        }
    )
    col_info = DFColInfo()
    col_info.update_from_df(df)

    bool_like_cols = col_info.names_with_tag("bool_like")
    assert "is_active" in bool_like_cols
    assert "has_permission" in bool_like_cols
    assert "name" not in bool_like_cols
