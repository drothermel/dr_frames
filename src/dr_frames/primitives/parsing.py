from __future__ import annotations

import ast
from typing import Any

import pandas as pd

__all__ = ["parse_list_string"]


def _parse_literal_list(val: Any) -> list[Any] | None:
    if pd.api.types.is_scalar(val) and pd.isna(val):
        return None
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return parsed
        return [parsed]
    except (TypeError, ValueError, SyntaxError):
        return None


def parse_list_string(val: Any) -> list[Any] | None:
    return _parse_literal_list(val)
