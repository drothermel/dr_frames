from __future__ import annotations

import pandas as pd

from dr_data.filtering import (
    apply_filters_to_df,
    filter_to_best_metric,
    filter_to_range,
    filter_to_value,
    filter_to_values,
    make_filter_fxn,
    select_subset,
)


def test_select_subset(sample_df: pd.DataFrame):
    result = select_subset(sample_df, {"category": "x"})
    assert len(result) == 2
    assert all(result["category"] == "x")


def test_select_subset_with_list_of_tuples(sample_df: pd.DataFrame):
    result = select_subset(sample_df, [("category", "x"), ("name", "alice")])
    assert len(result) == 1
    assert result.iloc[0]["name"] == "alice"


def test_select_subset_with_null():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]})
    result = select_subset(df, {"a": None})
    assert len(result) == 1
    assert result.iloc[0]["b"] == "y"


def test_apply_filters_to_df(sample_df: pd.DataFrame):
    result = apply_filters_to_df(sample_df, {"category": ["x"]})
    assert len(result) == 2


def test_apply_filters_to_df_multiple_values(sample_df: pd.DataFrame):
    result = apply_filters_to_df(sample_df, {"name": ["alice", "bob"]})
    assert len(result) == 2


def test_filter_to_value(sample_df: pd.DataFrame):
    result = filter_to_value(sample_df, "category", "x")
    assert len(result) == 2


def test_filter_to_value_none():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = filter_to_value(df, "a", "none")
    assert len(result) == 1


def test_filter_to_values(sample_df: pd.DataFrame):
    result = filter_to_values(sample_df, "name", ["alice", "bob"])
    assert len(result) == 2


def test_filter_to_values_with_none():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = filter_to_values(df, "a", [1, "none"])
    assert len(result) == 2


def test_filter_to_range(sample_df: pd.DataFrame):
    result = filter_to_range(sample_df, "value", 1.5, 2.5)
    assert len(result) == 1
    assert result.iloc[0]["value"] == 2.0


def test_filter_to_best_metric(metrics_df: pd.DataFrame):
    result = filter_to_best_metric(
        metrics_df,
        group_cols=["config_a"],
        metric_col="eval/loss",
        lower_is_better=True,
    )
    assert len(result) == 2
    assert result[result["config_a"] == "a"]["eval/loss"].iloc[0] == 0.5


def test_filter_to_best_metric_higher_is_better(metrics_df: pd.DataFrame):
    result = filter_to_best_metric(
        metrics_df,
        group_cols=["config_a"],
        metric_col="eval/accuracy",
        lower_is_better=False,
    )
    assert len(result) == 2
    assert result[result["config_a"] == "a"]["eval/accuracy"].iloc[0] == 0.9


def test_make_filter_fxn(sample_df: pd.DataFrame):
    filter_fn = make_filter_fxn(
        [
            (filter_to_value, "category", "x"),
            (filter_to_range, "value", 0.5, 1.5),
        ]
    )
    result = filter_fn(sample_df)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "alice"
