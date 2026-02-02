from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import PurePath
from typing import TYPE_CHECKING, Any

import pandas as pd
from pydantic import BaseModel, Field

from .aggregation import unique_non_null

if TYPE_CHECKING:
    pass

__all__ = [
    "ColInfo",
    "DFColInfo",
    "looks_like_json",
    "looks_like_path",
    "infer_series_base_tag_type",
    "infer_tags_from_series_sample",
    "infer_col_name_contains_tags",
    "infer_col_name_suffix_tags",
    "infer_col_name_prefix_tags",
]


class ColInfo(BaseModel):
    catalog: DFColInfo
    name: str
    dtype: str | None = None
    tags: set[str] = Field(default_factory=set)

    model_config = {"arbitrary_types_allowed": True}

    def update_tags(self, series: pd.Series) -> None:
        self.tags.update(
            infer_series_base_tag_type(
                series,
                self.catalog.pd_type_to_tags,
                self.catalog.pd_default_type,
            )
        )
        self.tags.update(
            infer_col_name_contains_tags(
                self.name,
                self.catalog.col_name_contains_map,
            )
        )
        self.tags.update(
            infer_col_name_suffix_tags(
                self.name,
                self.catalog.col_name_suffix_map,
            )
        )
        self.tags.update(
            infer_col_name_prefix_tags(
                self.name,
                self.catalog.col_name_prefix_map,
            )
        )
        self.tags.update(
            infer_tags_from_series_sample(
                series,
                self.catalog.path_like_extensions,
            )
        )

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def add_tags(self, extra: list[str]) -> None:
        self.tags.update(extra)


class DFColInfo(BaseModel):
    columns: dict[str, ColInfo] = Field(default_factory=dict)
    pd_type_to_tags: list[tuple[Callable, list[str]]] = Field(
        default_factory=lambda: [
            (pd.api.types.is_bool_dtype, ["bool"]),
            (pd.api.types.is_integer_dtype, ["int", "numeric"]),
            (pd.api.types.is_float_dtype, ["float", "numeric"]),
            (pd.api.types.is_datetime64_any_dtype, ["datetime"]),
            (pd.api.types.is_timedelta64_dtype, ["timedelta"]),
            (lambda dt: isinstance(dt, pd.CategoricalDtype), ["categorical"]),
        ]
    )
    pd_default_type: list[str] = Field(default_factory=lambda: ["str"])

    col_name_contains_map: dict[tuple[str, ...], str] = Field(
        default_factory=lambda: {
            ("config", "kwargs", "settings", "params"): "config",
        }
    )
    col_name_suffix_map: dict[tuple[str, ...], str] = Field(
        default_factory=lambda: {
            ("_path", "_dir"): "path",
            ("_id",): "id",
            ("_tag", "_tags"): "categorical",
        }
    )
    col_name_prefix_map: dict[tuple[str, ...], str] = Field(
        default_factory=lambda: {
            ("is_", "has_"): "bool_like",
            ("metric_",): "metric",
        }
    )

    path_like_extensions: set[str] = Field(
        default_factory=lambda: {
            ".json",
            ".jsonl",
            ".csv",
            ".tsv",
            ".parquet",
            ".txt",
            ".yaml",
            ".yml",
            ".log",
        }
    )

    def update_from_df(self, df: pd.DataFrame) -> None:
        for column in df.columns:
            info = ColInfo(catalog=self, name=column)
            info.update_tags(df[column])
            self.columns[column] = info

    def get(self, name: str) -> ColInfo | None:
        return self.columns.get(name)

    def names_with_tag(self, tag: str) -> list[str]:
        return [name for name, info in self.columns.items() if info.has_tag(tag)]


def infer_tags_from_series_sample(
    series: pd.Series,
    path_like_extensions: set[str],
) -> set[str]:
    tags: set[str] = set()
    unique_vals = unique_non_null(series)
    if len(unique_vals) == 0:
        return tags

    sample_point = unique_vals[0]
    if looks_like_path(sample_point, path_like_extensions):
        tags.add("path")
    if looks_like_json(sample_point):
        tags.add("json")
    return tags


def infer_col_name_contains_tags(
    name: str,
    col_name_contains_map: dict[tuple[str, ...], str],
) -> set[str]:
    lower_name = name.lower()
    tags: set[str] = set()
    for contains_tuple, tag in col_name_contains_map.items():
        for contains in contains_tuple:
            if contains.lower() in lower_name:
                tags.add(tag)
    return tags


def infer_col_name_suffix_tags(
    name: str,
    col_name_suffix_map: dict[tuple[str, ...], str],
) -> set[str]:
    lower_name = name.lower()
    tags: set[str] = set()
    for suffix_tuple, tag in col_name_suffix_map.items():
        for suffix in suffix_tuple:
            if lower_name.endswith(suffix.lower()):
                tags.add(tag)
                break
    return tags


def infer_col_name_prefix_tags(
    name: str,
    col_name_prefix_map: dict[tuple[str, ...], str],
) -> set[str]:
    lower_name = name.lower()
    tags: set[str] = set()
    for prefix_tuple, tag in col_name_prefix_map.items():
        for prefix in prefix_tuple:
            if lower_name.startswith(prefix.lower()):
                tags.add(tag)
                break
    return tags


def infer_series_base_tag_type(
    series: pd.Series,
    pd_type_to_tags: list[tuple[Callable, list[str]]],
    pd_default_type: list[str],
) -> set[str]:
    dtype = series.dtype
    tags: set[str] = set()
    for type_fxn, tag_list in pd_type_to_tags:
        tags.update(tag_list if type_fxn(dtype) else [])
    if len(tags) == 0:
        tags.update(pd_default_type)
    if series.isna().any():
        tags.add("nullable")
    return tags


def looks_like_path(value: Any, path_extensions: set[str]) -> bool:
    if not value or not isinstance(value, str) or value.isspace():
        return False
    normalized = value.strip()
    if any(sep in normalized for sep in ("/", "\\")):
        return True
    try:
        suffix = PurePath(normalized).suffix.lower()
    except (TypeError, ValueError):
        return False
    return suffix in path_extensions


def looks_like_json(value: Any) -> bool:
    if not value or not isinstance(value, str):
        return False
    trimmed = value.strip()
    if not trimmed:
        return False
    if not (trimmed.startswith("{") or trimmed.startswith("[")):
        return False
    try:
        parsed = json.loads(trimmed)
    except Exception:
        return False
    return isinstance(parsed, (dict, list))
