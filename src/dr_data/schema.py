from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, computed_field, model_validator

__all__ = [
    "DataField",
    "ComputedField",
    "MetricDataField",
    "DataFormat",
]


class DataField(BaseModel):
    id_string: str
    description: str | None = None
    column_name: str | None = None
    display_name: str | None = None
    altair_type: Literal["Q", "N", "O", "T"] | None = None
    scale_hint: Literal["linear", "log"] | None = None
    is_config: bool = True

    @model_validator(mode="after")
    def derive_display_name(self) -> DataField:
        if self.display_name is None:
            object.__setattr__(
                self,
                "display_name",
                self.id_string.replace("_", " ").replace(".", " ").title(),
            )
        return self

    @computed_field
    @property
    def is_resolved(self) -> bool:
        return self.column_name is not None

    def resolve_column(self, df: pd.DataFrame) -> str:
        if self.column_name:
            return self.column_name
        return self.id_string if self.id_string in df.columns else "Unknown"

    def infer_altair_type(self, df: pd.DataFrame) -> str:
        if self.altair_type:
            return self.altair_type
        col = self.resolve_column(df)
        if col not in df.columns:
            return "N"
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            return "Q"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "T"
        return "N"


class ComputedField(DataField):
    source_columns: list[str] = Field(default_factory=list)
    compute: Callable[[pd.DataFrame], pd.Series] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return self.compute(df)


class MetricDataField(DataField):
    group: str = ""
    metric_type: str = ""

    @classmethod
    def from_column_name(cls, col: str) -> MetricDataField:
        parts = col.split("/")
        if len(parts) >= 4:
            group = parts[1]
            metric_type = parts[-1]
            display = " ".join(parts[2:]).replace("(", "").replace(")", "")
        else:
            group = "unknown"
            metric_type = col
            display = col
        return cls(
            id_string=col,
            column_name=col,
            display_name=display,
            group=group,
            metric_type=metric_type,
            altair_type="Q",
        )


class DataFormat(BaseModel):
    fields: list[DataField] = Field(default_factory=list)
    computed_fields: list[ComputedField] = Field(default_factory=list)
    metrics: list[MetricDataField] = Field(default_factory=list)
    column_overrides: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_dict(
        cls,
        field_descriptions: dict[str, str],
        df: pd.DataFrame,
        column_overrides: dict[str, str] | None = None,
    ) -> DataFormat:
        overrides = column_overrides or {}
        fields = [
            DataField(
                id_string=k,
                description=v,
                column_name=overrides.get(k) or (k if k in df.columns else None),
            )
            for k, v in field_descriptions.items()
        ]
        return cls(fields=fields, column_overrides=overrides)

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        field_descriptions: dict[str, str] | None = None,
        computed_fields: list[ComputedField] | None = None,
        column_overrides: dict[str, str] | None = None,
        metric_prefix: str = "eval/",
    ) -> DataFormat:
        overrides = column_overrides or {}
        defaults = cls()

        if field_descriptions is not None:
            fields = [
                DataField(
                    id_string=k,
                    description=v,
                    column_name=overrides.get(k) or (k if k in df.columns else None),
                )
                for k, v in field_descriptions.items()
            ]
        else:
            fields = [
                field.model_copy(
                    update={
                        "column_name": overrides.get(field.id_string)
                        or (field.id_string if field.id_string in df.columns else None)
                    }
                )
                if field.column_name is None
                else field
                for field in defaults.fields
            ]

        cf_list = (
            computed_fields if computed_fields is not None else defaults.computed_fields
        )

        metrics = [
            MetricDataField.from_column_name(col)
            for col in df.columns
            if col.startswith(metric_prefix)
        ]

        return cls(
            fields=fields,
            computed_fields=cf_list,
            metrics=metrics,
            column_overrides=overrides,
        )

    @property
    def unresolved_fields(self) -> list[DataField]:
        return [f for f in self.fields if not f.is_resolved]

    @computed_field
    @property
    def is_fully_resolved(self) -> bool:
        return all(f.is_resolved for f in self.fields)

    def prepare_for_plotting(
        self, df: pd.DataFrame, drop_unknown: bool = True
    ) -> pd.DataFrame:
        result = df.copy()
        for cf in self.computed_fields:
            col_name = cf.column_name or cf.id_string
            result[col_name] = cf.apply(result)

        if drop_unknown:
            known_cols = set()
            for f in self.fields:
                known_cols.add(f.column_name or f.id_string)
            for cf in self.computed_fields:
                known_cols.add(cf.column_name or cf.id_string)
            for m in self.metrics:
                if m.column_name:
                    known_cols.add(m.column_name)
            keep_cols = [c for c in result.columns if c in known_cols]
            result = result[keep_cols]

        return result

    def get_metric(self, pattern: str) -> MetricDataField | None:
        for m in self.metrics:
            if pattern in (m.column_name or "") or pattern in (m.display_name or ""):
                return m
        return None

    def metric_col(self, pattern: str) -> str:
        metric = self.get_metric(pattern)
        assert metric is not None and metric.column_name is not None, (
            f"No metric found matching '{pattern}'"
        )
        return metric.column_name

    def get_metrics(self, df: pd.DataFrame) -> list[str]:
        return [col for col in df.columns if col.startswith("eval/")]

    def get_config_columns(self, use_computed: bool = True) -> list[str]:
        if use_computed:
            config_cols = [cf.id_string for cf in self.computed_fields if cf.is_config]

            computed_sources = set()
            for cf in self.computed_fields:
                if cf.is_config:
                    computed_sources.update(cf.source_columns)

            for f in self.fields:
                if f.is_config and f.id_string not in computed_sources:
                    config_cols.append(f.id_string)

            return config_cols
        else:
            return [f.id_string for f in self.fields if f.is_config]
