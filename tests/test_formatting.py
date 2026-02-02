from __future__ import annotations

import pandas as pd

from dr_data.formatting import (
    FORMATTER_TYPES,
    format_coverage_table,
    format_table,
)


def test_formatter_types_scientific():
    assert FORMATTER_TYPES["scientific"](0.00123) == "1.23e-03"
    assert FORMATTER_TYPES["scientific"](None) == "None"


def test_formatter_types_decimal():
    assert FORMATTER_TYPES["decimal"](1.23456) == "1.235"
    assert FORMATTER_TYPES["decimal"](1.23456, precision=1) == "1.2"


def test_formatter_types_integer():
    assert FORMATTER_TYPES["integer"](1234567) == "1,234,567"


def test_formatter_types_truncate():
    long_text = "a" * 60
    result = FORMATTER_TYPES["truncate"](long_text)
    assert len(result) == 53
    assert result.endswith("...")


def test_format_table_list_of_dicts():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    result = format_table(data, output_format="markdown")
    assert isinstance(result, str)
    assert "a" in result
    assert "1" in result


def test_format_table_dataframe():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = format_table(df, output_format="plain")
    assert isinstance(result, str)


def test_format_table_with_config():
    data = [{"value": 0.123456}]
    config = {"value": {"header": "Value", "formatter": "decimal", "precision": 2}}
    result = format_table(data, output_format="markdown", column_config=config)
    assert "0.12" in result
    assert "Value" in result


def test_format_table_console_returns_rich_table():
    data = [{"a": 1}]
    result = format_table(data, output_format="console")
    assert hasattr(result, "add_row")


def test_format_coverage_table():
    df = pd.DataFrame({"a": [1, 2, None], "b": [1, None, None]})
    result = format_coverage_table(df, output_format="plain")
    assert "Column Coverage" in result
    assert "a" in result
    assert "b" in result


def test_format_coverage_table_empty():
    """Test that format_coverage_table handles empty DataFrame without raising ZeroDivisionError."""
    df = pd.DataFrame()
    result = format_coverage_table(df, output_format="plain")
    assert "Column Coverage" in result
    assert isinstance(result, str)
