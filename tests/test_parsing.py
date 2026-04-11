from __future__ import annotations

import pandas as pd

from dr_frames.primitives.parsing import parse_list_string


def test_parse_list_string():
    assert parse_list_string("[1, 2, 3]") == [1, 2, 3]
    assert parse_list_string("[0.5, 0.25]") == [0.5, 0.25]
    assert parse_list_string("['a', 'b']") == ["a", "b"]


def test_parse_list_string_single_value():
    assert parse_list_string("42") == [42]


def test_parse_list_string_invalid():
    assert parse_list_string("invalid") is None


def test_parse_list_string_null():
    assert parse_list_string(pd.NA) is None


def test_parse_list_string_non_scalar_input():
    assert parse_list_string([1, 2, 3]) is None


def test_parse_list_string_empty_list():
    assert parse_list_string("[]") == []


def test_parse_list_string_supports_consumer_projections():
    values = parse_list_string("[1, 2, 3]")
    assert values is not None
    assert float(values[0]) == 1.0
    assert float(sum(float(item) for item in values)) == 6.0
    assert len(set(values)) == 3


def test_parse_list_string_supports_consumer_homogeneity_check():
    values = parse_list_string("[0.125, 0.125, 0.125]")
    assert values is not None
    assert len(set(values)) == 1
