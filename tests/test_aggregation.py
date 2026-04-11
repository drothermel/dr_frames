from __future__ import annotations

import pandas as pd
import pytest

from dr_frames.primitives.aggregation import (
    aggregate_over_seeds,
    aggregate_by_group,
)


def test_aggregate_by_group():
    df = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "seed": [1, 2, 1, 2],
            "metrics_loss": [0.5, 0.6, 0.7, 0.8],
            "label": ["x", "x", "y", "y"],
        }
    )
    result = aggregate_by_group(
        df, group_col="group", exclude_cols=["seed"], end_prefix="metrics_"
    )
    assert len(result) == 2
    assert "seed" not in result.columns
    assert "metrics_loss" in result.columns
    assert "label" in result.columns
    assert set(result["label"]) == {"x", "y"}


def test_aggregate_by_group_raises_for_varying_non_numeric_values():
    df = pd.DataFrame(
        {
            "group": ["a", "a"],
            "metrics_loss": [0.5, 0.6],
            "label": ["x", "y"],
        }
    )
    with pytest.raises(ValueError, match="Non-numeric columns must be constant"):
        aggregate_by_group(df, group_col="group")


def test_aggregate_by_group_returns_unique_groups_when_all_other_columns_are_excluded():
    df = pd.DataFrame({"group": ["a", "a", "b"], "seed": [1, 2, 1]})
    result = aggregate_by_group(df, group_col="group", exclude_cols=["seed"])
    assert result.to_dict(orient="list") == {"group": ["a", "b"]}


def test_aggregate_by_group_empty_df_returns_empty_df():
    df = pd.DataFrame(columns=["group", "value"])
    result = aggregate_by_group(df, group_col="group")
    assert result.empty
    assert list(result.columns) == ["group", "value"]


def test_aggregate_by_group_raises_for_missing_group_col():
    df = pd.DataFrame({"value": [1, 2]})
    with pytest.raises(ValueError, match="Group column 'group' not found"):
        aggregate_by_group(df, group_col="group")


def test_aggregate_by_group_raises_when_group_col_is_excluded():
    df = pd.DataFrame({"group": ["a", "b"], "value": [1, 2]})
    with pytest.raises(ValueError, match="cannot be in exclude_cols"):
        aggregate_by_group(df, group_col="group", exclude_cols=["group"])


def test_aggregate_by_group_applies_start_and_sort_cols():
    df = pd.DataFrame(
        {
            "group": ["b", "b", "a", "a"],
            "priority": [2, 2, 1, 1],
            "metrics_loss": [0.8, 0.6, 0.4, 0.2],
            "label": ["beta", "beta", "alpha", "alpha"],
        }
    )
    result = aggregate_by_group(
        df,
        group_col="group",
        start_cols=["priority"],
        sort_cols=["priority"],
        end_prefix="metrics_",
    )
    assert list(result.columns[:2]) == ["group", "priority"]
    assert list(result["group"]) == ["a", "b"]


def test_aggregate_over_seeds(metrics_df: pd.DataFrame):
    result = aggregate_over_seeds(
        metrics_df,
        config_cols=["config_a", "config_b"],
        metric_cols=["eval/loss", "eval/accuracy"],
    )
    assert len(result) == 2
    assert "dataset" in result.columns
    assert "eval/loss_mean" in result.columns
    assert "eval/loss_std" in result.columns
    assert "eval/loss_count" in result.columns


def test_aggregate_over_seeds_raises_without_seed_column():
    df = pd.DataFrame({"config": ["a"], "eval/loss": [0.5]})
    with pytest.raises(ValueError, match="Seed column 'seed' not found"):
        aggregate_over_seeds(df, config_cols=["config"])


def test_aggregate_over_seeds_raises_without_config_cols(metrics_df: pd.DataFrame):
    with pytest.raises(ValueError, match="config_cols must be provided"):
        aggregate_over_seeds(metrics_df, config_cols=[])


def test_aggregate_over_seeds_raises_if_seed_is_in_config_cols(metrics_df: pd.DataFrame):
    with pytest.raises(ValueError, match="cannot be included in config_cols"):
        aggregate_over_seeds(metrics_df, config_cols=["config_a", "seed"])


def test_aggregate_over_seeds_raises_for_duplicate_seed_within_config():
    df = pd.DataFrame(
        {
            "config": ["a", "a"],
            "seed": [1, 1],
            "eval/loss": [0.5, 0.6],
        }
    )
    with pytest.raises(ValueError, match="Each seed must appear at most once"):
        aggregate_over_seeds(df, config_cols=["config"])


def test_aggregate_over_seeds_raises_for_varying_passthrough_columns():
    df = pd.DataFrame(
        {
            "config": ["a", "a"],
            "seed": [1, 2],
            "dataset": ["c4", "pile"],
            "eval/loss": [0.5, 0.6],
        }
    )
    with pytest.raises(ValueError, match="Non-numeric columns must be constant"):
        aggregate_over_seeds(df, config_cols=["config"])


def test_aggregate_over_seeds_raises_without_metric_columns():
    df = pd.DataFrame({"config": ["a"], "seed": [1], "label": ["x"]})
    with pytest.raises(ValueError, match="No metric columns found"):
        aggregate_over_seeds(df, config_cols=["config"])


def test_aggregate_over_seeds_discovers_default_eval_metrics():
    df = pd.DataFrame(
        {
            "config": ["a", "a", "b", "b"],
            "seed": [1, 2, 1, 2],
            "dataset": ["c4", "c4", "pile", "pile"],
            "eval/loss": [0.5, 0.7, 0.4, 0.6],
            "eval/acc": [0.9, 0.8, 0.85, 0.88],
            "notes": ["run-a", "run-a", "run-b", "run-b"],
        }
    )
    result = aggregate_over_seeds(df, config_cols=["config"])
    assert "eval/loss_mean" in result.columns
    assert "eval/acc_mean" in result.columns
    assert "notes" in result.columns


def test_aggregate_over_seeds_supports_custom_agg_funcs():
    df = pd.DataFrame(
        {
            "config": ["a", "a"],
            "seed": [1, 2],
            "eval/loss": [0.5, 0.7],
        }
    )
    result = aggregate_over_seeds(
        df,
        config_cols=["config"],
        metric_cols=["eval/loss"],
        agg_funcs=["mean", "count"],
    )
    assert list(result.columns) == ["config", "eval/loss_mean", "eval/loss_count"]
