from __future__ import annotations

import pandas as pd
import pytest

from dr_frames.schema import ComputedField, DataField, DataFormat, MetricDataField


def test_data_field_display_name_derived():
    field = DataField(id_string="my_field_name")
    assert field.display_name == "My Field Name"


def test_data_field_explicit_display_name():
    field = DataField(id_string="my_field_name", display_name="Custom Name")
    assert field.display_name == "Custom Name"


def test_data_field_is_resolved():
    field1 = DataField(id_string="a", column_name="col_a")
    field2 = DataField(id_string="b")
    assert field1.is_resolved is True
    assert field2.is_resolved is False


def test_data_field_resolve_column():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    field1 = DataField(id_string="a")
    field2 = DataField(id_string="c")
    assert field1.resolve_column(df) == "a"
    with pytest.raises(ValueError, match="Cannot resolve column"):
        field2.resolve_column(df)


def test_data_field_infer_altair_type():
    df = pd.DataFrame(
        {
            "numeric": [1, 2, 3],
            "string": ["a", "b", "c"],
            "datetime": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
        }
    )
    field_num = DataField(id_string="numeric")
    field_str = DataField(id_string="string")
    field_dt = DataField(id_string="datetime")

    assert field_num.infer_altair_type(df) == "Q"
    assert field_str.infer_altair_type(df) == "N"
    assert field_dt.infer_altair_type(df) == "T"


def test_computed_field_apply():
    df = pd.DataFrame({"a": [1, 2, 3]})
    field = ComputedField(
        id_string="doubled", source_columns=["a"], compute=lambda df: df["a"] * 2
    )
    result = field.apply(df)
    assert list(result) == [2, 4, 6]


def test_metric_data_field_from_column_name():
    metric = MetricDataField.from_column_name("eval/lm/c4_en-validation/CE loss")
    assert metric.group == "lm"
    assert metric.metric_type == "CE loss"
    assert metric.altair_type == "Q"


def test_metric_data_field_from_short_column():
    metric = MetricDataField.from_column_name("eval/loss")
    assert metric.group == "unknown"
    assert metric.metric_type == "eval/loss"


def test_data_format_from_dict():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    fmt = DataFormat.from_dict(
        {"a": "Column A description", "c": "Column C (missing)"},
        df,
    )
    assert len(fmt.fields) == 2
    a_field = next(f for f in fmt.fields if f.id_string == "a")
    c_field = next(f for f in fmt.fields if f.id_string == "c")
    assert a_field.column_name == "a"
    assert c_field.column_name is None


def test_data_format_from_df_with_metrics():
    df = pd.DataFrame(
        {
            "config": ["a", "b"],
            "eval/loss": [0.5, 0.6],
            "eval/acc": [0.9, 0.85],
        }
    )
    fmt = DataFormat.from_df(df)
    assert len(fmt.metrics) == 2


def test_data_format_is_fully_resolved():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    fmt1 = DataFormat.from_dict({"a": "desc", "b": "desc"}, df)
    fmt2 = DataFormat.from_dict({"a": "desc", "c": "missing"}, df)
    assert fmt1.is_fully_resolved is True
    assert fmt2.is_fully_resolved is False


def test_data_format_prepare_for_plotting():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    computed = ComputedField(
        id_string="c", source_columns=["a"], compute=lambda df: df["a"] * 10
    )
    fmt = DataFormat(
        fields=[DataField(id_string="a", column_name="a")],
        computed_fields=[computed],
    )
    result = fmt.prepare_for_plotting(df, drop_unknown=True)
    assert "c" in result.columns
    assert "b" not in result.columns


def test_data_format_get_metric():
    df = pd.DataFrame({"eval/lm/loss": [0.5], "eval/lm/acc": [0.9]})
    fmt = DataFormat.from_df(df)
    metric = fmt.get_metric("loss")
    assert metric is not None
    assert "loss" in metric.column_name


def test_data_format_metric_col():
    df = pd.DataFrame({"eval/lm/loss": [0.5]})
    fmt = DataFormat.from_df(df)
    col = fmt.metric_col("loss")
    assert col == "eval/lm/loss"
