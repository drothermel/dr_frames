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
