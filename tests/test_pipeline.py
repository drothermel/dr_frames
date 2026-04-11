from __future__ import annotations

import pandas as pd

from dr_frames import maybe_pipe
from dr_frames.pipeline import maybe_pipe as maybe_pipe_from_module


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


def test_maybe_pipe_module_export_matches_top_level():
    assert maybe_pipe_from_module is maybe_pipe
