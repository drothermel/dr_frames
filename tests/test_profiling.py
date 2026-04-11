from __future__ import annotations

import pandas as pd

from dr_frames.profiling import (
    DFColInfo,
    infer_series_base_tag_type,
    infer_tags_from_series_sample,
)


def test_infer_tags_from_series_sample_path():
    extensions = {".json", ".csv", ".parquet"}
    series = pd.Series(["/path/to/file.json", "file.csv", "C:\\Users\\file.parquet"])
    assert "path" in infer_tags_from_series_sample(series, extensions)


def test_infer_tags_from_series_sample_json():
    series = pd.Series(['{"key": "value"}', "[1, 2, 3]", "not json"])
    assert "json" in infer_tags_from_series_sample(series, {".json"})


def test_infer_tags_from_series_sample_empty():
    assert infer_tags_from_series_sample(pd.Series([None, pd.NA]), {".json"}) == set()


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
