from __future__ import annotations

import ast

import pandas as pd

__all__ = [
    "parse_first_element",
    "sum_list_elements",
    "is_homogeneous",
    "parse_list_string",
]


def parse_list_string(val: str) -> list | None:
    if pd.isna(val):
        return None
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return parsed
        return [parsed]
    except (ValueError, SyntaxError):
        return None


def parse_first_element(val: str) -> float:
    if pd.isna(val):
        return float("nan")
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            if len(parsed) > 0:
                return float(parsed[0])
            return float("nan")
        return float(parsed)
    except (ValueError, SyntaxError):
        return float("nan")


def sum_list_elements(val: str) -> float:
    if pd.isna(val):
        return float("nan")
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            if len(parsed) > 0:
                try:
                    return float(sum(float(item) for item in parsed))
                except (ValueError, TypeError):
                    return float("nan")
            return float("nan")
        return float(parsed)
    except (ValueError, SyntaxError):
        return float("nan")


def is_homogeneous(val: str) -> bool:
    if pd.isna(val):
        return False
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            if len(parsed) > 0:
                return len(set(parsed)) == 1
            return False
        return True
    except (ValueError, SyntaxError, TypeError):
        return False
