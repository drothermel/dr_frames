from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import cast

import pandas as pd

__all__ = ["group_namespaced_values"]


def _normalize_prefix_items(
    prefix_map: Mapping[str, str] | Iterable[tuple[str, str]] | None,
) -> list[tuple[str, str]]:
    if prefix_map is None:
        return []
    items = list(prefix_map.items() if isinstance(prefix_map, Mapping) else prefix_map)
    if not all(isinstance(item, tuple) and len(item) == 2 for item in items):
        raise TypeError(
            "Prefix map must be a mapping or iterable of tuples, "
            f"received {type(prefix_map)!r}."
        )

    normalized: list[tuple[str, str]] = []
    for prefix, group in items:
        if not isinstance(prefix, str):
            raise TypeError(f"Prefix keys must be strings, received {type(prefix)!r}.")
        if not isinstance(group, str):
            raise TypeError(f"Group names must be strings, received {type(group)!r}.")
        lowered = prefix.strip().lower()
        if not lowered:
            raise ValueError(
                "Prefix keys must be non-empty after stripping whitespace."
            )
        normalized.append((lowered, group))
    normalized.sort(key=lambda item: (-len(item[0]), item[0]))
    return normalized


def group_namespaced_values(
    df: pd.DataFrame,
    column: str,
    prefix_map: Mapping[str, str] | Iterable[tuple[str, str]] | None,
    *,
    output_col: str,
) -> pd.Series:
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not present in DataFrame.")

    series = cast(pd.Series, df[column])
    normalized_prefixes = _normalize_prefix_items(prefix_map)

    if not normalized_prefixes:
        return series.copy().rename(output_col)

    def resolve(value: object) -> object:
        if pd.api.types.is_scalar(value) and bool(pd.isna(value)):
            return value
        if isinstance(value, str):
            lowered = value.lower()
            for prefix, group in normalized_prefixes:
                if lowered.startswith(prefix):
                    return group
            return value
        return value

    return series.map(resolve).rename(output_col)
