from __future__ import annotations

import pandas as pd

from dr_data.aggregation import (
    aggregate_over_seeds,
    apply_aggregations,
    fillna_with_defaults,
    get_constant_cols,
    maybe_pipe,
    unique_by_col,
    unique_by_cols,
    unique_non_null,
)


def test_unique_non_null():
    series = pd.Series([1, None, 2, None, 1])
    result = unique_non_null(series)
    assert set(result) == {1, 2}


def test_unique_non_null_with_list():
    result = unique_non_null([1, None, 2, None, 1])
    assert set(result) == {1, 2}


def test_unique_by_col(sample_df: pd.DataFrame):
    result = unique_by_col(sample_df, "category")
    assert set(result) == {"x", "y"}


def test_unique_by_cols(sample_df: pd.DataFrame):
    result = unique_by_cols(sample_df, ["category", "name"])
    assert set(result["category"]) == {"x", "y"}
    assert set(result["name"]) == {"alice", "bob", "charlie"}


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


def test_fillna_with_defaults():
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, "y", None]})
    result = fillna_with_defaults(df, {"a": 0, "b": "default"})
    assert result["a"].tolist() == [1.0, 0.0, 3.0]
    assert result["b"].tolist() == ["default", "y", "default"]


def test_maybe_pipe_true():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = maybe_pipe(df, True, lambda x: x.assign(b=x["a"] * 2))
    assert "b" in result.columns


def test_maybe_pipe_false():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = maybe_pipe(df, False, lambda x: x.assign(b=x["a"] * 2))
    assert "b" not in result.columns


def test_maybe_pipe_callable():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = maybe_pipe(df, lambda x: len(x) > 2, lambda x: x.assign(b=x["a"] * 2))
    assert "b" in result.columns


def test_apply_aggregations():
    df = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "seed": [1, 2, 1, 2],
            "metrics_loss": [0.5, 0.6, 0.7, 0.8],
            "label": ["x", "x", "y", "y"],
        }
    )
    result = apply_aggregations(
        df, group_col="group", agg_over_cols=["seed"], end_prefix="metrics_"
    )
    assert len(result) == 2
    assert "seed" not in result.columns
    assert "metrics_loss" in result.columns


def test_aggregate_over_seeds(metrics_df: pd.DataFrame):
    result = aggregate_over_seeds(
        metrics_df,
        config_cols=["config_a", "config_b"],
        metric_cols=["eval/loss", "eval/accuracy"],
    )
    assert len(result) == 2
    assert "eval/loss_mean" in result.columns
    assert "eval/loss_std" in result.columns
    assert "eval/loss_count" in result.columns
