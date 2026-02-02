from __future__ import annotations

import math

import pandas as pd

from dr_frames.parsing import (
    is_homogeneous,
    parse_first_element,
    parse_list_string,
    sum_list_elements,
)


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


def test_parse_first_element():
    assert parse_first_element("[0.5, 0.25]") == 0.5
    assert parse_first_element("[1, 2, 3]") == 1.0


def test_parse_first_element_single():
    assert parse_first_element("42") == 42.0


def test_parse_first_element_empty_list():
    assert math.isnan(parse_first_element("[]"))


def test_parse_first_element_null():
    assert math.isnan(parse_first_element(pd.NA))


def test_parse_first_element_invalid():
    assert math.isnan(parse_first_element("invalid"))


def test_sum_list_elements():
    assert sum_list_elements("[1, 2, 3]") == 6.0
    assert sum_list_elements("[4, 8]") == 12.0


def test_sum_list_elements_single():
    assert sum_list_elements("10") == 10.0


def test_sum_list_elements_empty():
    assert math.isnan(sum_list_elements("[]"))


def test_sum_list_elements_null():
    assert math.isnan(sum_list_elements(pd.NA))


def test_is_homogeneous():
    assert is_homogeneous("[0.125, 0.125, 0.125]") is True
    assert is_homogeneous("[1, 1, 1]") is True


def test_is_homogeneous_heterogeneous():
    assert is_homogeneous("[0.5, 0.25]") is False
    assert is_homogeneous("[1, 2, 3]") is False


def test_is_homogeneous_single():
    assert is_homogeneous("42") is True


def test_is_homogeneous_empty():
    assert is_homogeneous("[]") is False


def test_is_homogeneous_null():
    assert is_homogeneous(pd.NA) is False
