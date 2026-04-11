from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

import pandas as pd

if TYPE_CHECKING:
    from rich.table import Table

JustifyMethod = Literal["default", "left", "center", "right", "full"]

__all__ = [
    "format_table",
    "format_coverage_table",
    "FORMATTER_TYPES",
    "OUTPUT_FORMATS",
]

OUTPUT_FORMATS = {
    "console": "grid",
    "markdown": "pipe",
    "latex": "latex",
    "plain": "plain",
    "csv": "simple",
}

FORMATTER_TYPES: dict[str, Callable] = {
    "scientific": lambda x, precision=2: f"{x:.{precision}e}"
    if x is not None
    else "None",
    "decimal": lambda x, precision=3: f"{x:.{precision}f}" if x is not None else "None",
    "integer": lambda x: f"{x:,.0f}" if x is not None else "None",
    "comma": lambda x: f"{x:,}" if x is not None else "None",
    "truncate": lambda x, max_length=50: (
        str(x)[:max_length] + "..."
        if x is not None and len(str(x)) > max_length
        else (str(x) if x is not None else "None")
    ),
    "string": lambda x: str(x) if x is not None else "None",
}

COVERAGE_TABLE_CONFIG = {
    "index": {"header": "#", "formatter": "integer"},
    "column": {"header": "Column", "formatter": "truncate", "max_length": 35},
    "coverage": {"header": "Coverage %", "formatter": "decimal", "precision": 1},
}


def format_table(
    data: list[dict] | pd.DataFrame | list[list],
    headers: list[str] | None = None,
    output_format: str = "console",
    column_config: dict[str, dict] | None = None,
    title: str | None = None,
    table_style: str = "lines",
    disable_numparse: bool = True,
) -> str | Table:
    processed_data, column_names = _normalize_table_data(data)
    config = column_config or {}
    formatted_data = _apply_column_formatting(processed_data, config, column_names)
    final_headers = _resolve_headers(headers, column_names, config)

    if output_format == "console":
        return _create_rich_table(
            formatted_data, final_headers, config, column_names, title, table_style
        )
    else:
        from tabulate import tabulate

        tablefmt = OUTPUT_FORMATS.get(output_format, "grid")
        return tabulate(
            formatted_data,
            headers=final_headers,
            tablefmt=tablefmt,
            disable_numparse=disable_numparse,
        )


def format_coverage_table(
    df: pd.DataFrame,
    title: str = "Column Coverage",
    output_format: str = "console",
    table_style: str = "lines",
    disable_numparse: bool = True,
) -> str:
    coverage_data = []
    row_count = len(df) or df.shape[0]
    for i, col in enumerate(df.columns):
        if row_count == 0:
            coverage = 0
        else:
            coverage = df[col].notna().sum() / row_count * 100
        coverage_data.append({"index": i + 1, "column": col, "coverage": coverage})
    result = f"{title} ({len(df.columns)} columns):\n"
    table_result = format_table(
        data=coverage_data,
        output_format=output_format,
        column_config=COVERAGE_TABLE_CONFIG,
        table_style=table_style,
        disable_numparse=disable_numparse,
    )
    result += str(table_result) if not isinstance(table_result, str) else table_result
    return result


def _stable_dict_keys(rows: list[dict]) -> list[str]:
    keys = list(rows[0].keys())
    keys_set = set(keys)
    for row in rows[1:]:
        for key in row.keys():
            if key not in keys_set:
                keys.append(key)
                keys_set.add(key)
    return keys


def _normalize_table_data(
    data: list[dict] | pd.DataFrame | list[list],
) -> tuple[list[list], list[str]]:
    if isinstance(data, pd.DataFrame):
        return data.to_numpy().tolist(), list(data.columns)
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            rows = data
            keys = _stable_dict_keys(rows)
            return [[row.get(key) for key in keys] for row in rows], keys
        return list(data), []
    return [], []


def _apply_column_formatting(
    processed_data: list[list],
    config: dict[str, dict],
    column_names: list[str] | None = None,
) -> list[list]:
    if not processed_data:
        return processed_data
    formatted_data = []
    for row in processed_data:
        formatted_row = []
        for col_idx, value in enumerate(row):
            col_name = (
                column_names[col_idx]
                if column_names and col_idx < len(column_names)
                else None
            )
            formatted_row.append(_format_value(value, col_name, config))
        formatted_data.append(formatted_row)
    return formatted_data


def _format_value(
    value: Any,
    col_name: str | None,
    config: dict[str, dict],
) -> str:
    if col_name and col_name in config:
        col_config = config[col_name]
        formatter_name = col_config.get("formatter", "string")
        formatter = FORMATTER_TYPES.get(formatter_name, FORMATTER_TYPES["string"])
        formatter_kwargs = {
            k: v for k, v in col_config.items() if k not in ["header", "formatter"]
        }
        try:
            return formatter(value, **formatter_kwargs)
        except (TypeError, ValueError):
            return str(value) if value is not None else "None"
    return str(value) if value is not None else "None"


def _resolve_headers(
    headers: list[str] | None, column_names: list[str], config: dict[str, dict]
) -> list[str]:
    if headers is not None:
        return headers
    if config and column_names:
        result_headers = []
        for col_name in column_names:
            if col_name in config:
                result_headers.append(config[col_name].get("header", col_name))
            else:
                result_headers.append(col_name)
        return result_headers
    if column_names:
        return column_names
    return []


def _create_rich_table(
    formatted_data: list[list],
    headers: list[str],
    config: dict[str, dict],
    column_names: list[str],
    title: str | None = None,
    table_style: str = "lines",
) -> Table:
    from rich.table import Table

    if table_style == "zebra":
        table = Table(
            title=title,
            show_header=True,
            header_style="bold magenta",
            row_styles=["", "dim"],
        )
    else:
        table = Table(
            title=title, show_header=True, header_style="bold magenta", show_lines=True
        )

    for i, header in enumerate(headers):
        col_name = _get_column_name_for_index(column_names, i)
        col_config = config.get(col_name, {})
        justify = _get_rich_justify(col_config)
        style = _get_rich_style(col_config)
        table.add_column(header, justify=justify, style=style)

    for row in formatted_data:
        table.add_row(*[str(cell) for cell in row])

    return table


def _get_column_name_for_index(column_names: list[str], index: int) -> str:
    return column_names[index] if index < len(column_names) else f"col_{index}"


def _get_rich_justify(col_config: dict) -> JustifyMethod:
    formatter = col_config.get("formatter", "string")
    if formatter in ["scientific", "decimal", "integer", "comma"]:
        return "right"
    return "left"


def _get_rich_style(col_config: dict) -> str | None:
    formatter = col_config.get("formatter", "string")
    style_map = {
        "scientific": "yellow",
        "decimal": "green",
        "integer": "cyan",
        "comma": "cyan",
        "truncate": "dim",
    }
    return style_map.get(formatter)
