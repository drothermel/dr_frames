from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["alice", "bob", "charlie"],
            "value": [1.0, 2.0, 3.0],
            "category": ["x", "y", "x"],
            "prefix_col1": [10, 20, 30],
            "prefix_col2": [100, 200, 300],
            "other": ["a", "b", "c"],
        }
    )


@pytest.fixture
def df_with_nulls() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a": [1, None, 3],
            "b": ["x", "y", None],
            "c": [None, None, None],
        }
    )


@pytest.fixture
def metrics_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "config_a": ["a", "a", "b", "b"],
            "config_b": [1, 1, 2, 2],
            "eval/loss": [0.5, 0.6, 0.7, 0.8],
            "eval/accuracy": [0.9, 0.85, 0.8, 0.75],
        }
    )
