from __future__ import annotations

import pandas as pd

from dr_frames import maybe_pipe
from dr_frames.primitives.pipeline import maybe_pipe as maybe_pipe_from_module


def test_maybe_pipe_true():
    df = pd.DataFrame({"a": [1, 2, 3]})
    should_pipe = True
    result = maybe_pipe(df, should_pipe, lambda x: x.assign(b=x["a"] * 2))
    assert "b" in result.columns


def test_maybe_pipe_false():
    df = pd.DataFrame({"a": [1, 2, 3]})
    should_pipe = False
    result = maybe_pipe(df, should_pipe, lambda x: x.assign(b=x["a"] * 2))
    assert "b" not in result.columns


def test_maybe_pipe_callable():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = maybe_pipe(df, lambda x: len(x) > 2, lambda x: x.assign(b=x["a"] * 2))
    assert "b" in result.columns


def test_maybe_pipe_iterable_truthiness():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = maybe_pipe(df, [1], lambda x: x.assign(b=x["a"] * 2))
    assert "b" in result.columns
    result = maybe_pipe(df, [], lambda x: x.assign(b=x["a"] * 2))
    assert "b" not in result.columns


def test_maybe_pipe_handles_pandas_objects():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = maybe_pipe(
        df,
        df["a"] > 0,
        lambda x: x.assign(b=x["a"] * 2),
    )
    assert "b" in result.columns

    result = maybe_pipe(
        df,
        pd.Series(dtype=bool),
        lambda x: x.assign(b=x["a"] * 2),
    )
    assert "b" not in result.columns

    result = maybe_pipe(
        df,
        pd.DataFrame({"a": []}),
        lambda x: x.assign(b=x["a"] * 2),
    )
    assert "b" not in result.columns


def test_maybe_pipe_module_export_matches_top_level():
    assert maybe_pipe_from_module is maybe_pipe
