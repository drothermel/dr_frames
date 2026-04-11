from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, Field, computed_field

from .computed_field import ComputedField
from .data_field import DataField
from .metric_data_field import MetricDataField


class DataFormat(BaseModel):
    fields: list[DataField] = Field(default_factory=list)
    computed_fields: list[ComputedField] = Field(default_factory=list)
    metrics: list[MetricDataField] = Field(default_factory=list)
    column_overrides: dict[str, str] = Field(default_factory=dict)
    metric_prefix: str = "eval/"

    @staticmethod
    def _validated_column_overrides(
        df: pd.DataFrame,
        column_overrides: dict[str, str] | None,
    ) -> dict[str, str]:
        if column_overrides is None:
            return {}
        return {
            field_id: column_name
            for field_id, column_name in column_overrides.items()
            if column_name in df.columns
        }

    @staticmethod
    def _resolve_field_column_name(
        field_id: str,
        df: pd.DataFrame,
        overrides: dict[str, str],
    ) -> str | None:
        if field_id in overrides:
            return overrides[field_id]
        if field_id in df.columns:
            return field_id
        return None

    @classmethod
    def from_dict(
        cls,
        field_descriptions: dict[str, str],
        df: pd.DataFrame,
        column_overrides: dict[str, str] | None = None,
    ) -> "DataFormat":
        overrides = cls._validated_column_overrides(df, column_overrides)
        fields = [
            DataField(
                id_string=key,
                description=value,
                column_name=cls._resolve_field_column_name(key, df, overrides),
            )
            for key, value in field_descriptions.items()
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
    ) -> "DataFormat":
        overrides = cls._validated_column_overrides(df, column_overrides)
        defaults = cls()

        if field_descriptions is not None:
            fields = [
                DataField(
                    id_string=key,
                    description=value,
                    column_name=cls._resolve_field_column_name(key, df, overrides),
                )
                for key, value in field_descriptions.items()
            ]
        else:
            fields = [
                field.model_copy(
                    update={
                        "column_name": cls._resolve_field_column_name(
                            field.id_string,
                            df,
                            overrides,
                        )
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
            metric_prefix=metric_prefix,
        )

    @property
    def unresolved_fields(self) -> list[DataField]:
        return [field for field in self.fields if not field.is_resolved]

    @computed_field
    @property
    def is_fully_resolved(self) -> bool:
        return all(field.is_resolved for field in self.fields)

    def prepare_for_plotting(
        self, df: pd.DataFrame, drop_unknown: bool = True
    ) -> pd.DataFrame:
        result = df.copy()
        for field in self.computed_fields:
            col_name = field.column_name or field.id_string
            result[col_name] = field.apply(result)

        if drop_unknown:
            known_cols: set[str] = set()
            for field in self.fields:
                known_cols.add(field.column_name or field.id_string)
            for computed in self.computed_fields:
                known_cols.add(computed.column_name or computed.id_string)
            for metric in self.metrics:
                if metric.column_name:
                    known_cols.add(metric.column_name)
            keep_cols = [column for column in result.columns if column in known_cols]
            result = result[keep_cols]

        return result

    def get_metric(self, pattern: str) -> MetricDataField | None:
        for metric in self.metrics:
            if pattern in (metric.column_name or "") or pattern in (
                metric.display_name or ""
            ):
                return metric
        return None

    def metric_col(self, pattern: str) -> str:
        metric = self.get_metric(pattern)
        if metric is None:
            raise ValueError(f"No metric found matching '{pattern}'")
        if metric.column_name is None:
            raise ValueError(
                f"Metric matching '{pattern}' exists but has no column_name"
            )
        return metric.column_name

    def get_metrics(self, df: pd.DataFrame) -> list[str]:
        return [col for col in df.columns if col.startswith(self.metric_prefix)]

    def get_config_columns(self, use_computed: bool = True) -> list[str]:
        if use_computed:
            config_cols = [
                computed.id_string
                for computed in self.computed_fields
                if computed.is_config
            ]

            computed_sources: set[str] = set()
            for computed in self.computed_fields:
                if computed.is_config:
                    computed_sources.update(computed.source_columns)

            for field in self.fields:
                if field.is_config and field.id_string not in computed_sources:
                    config_cols.append(field.id_string)

            return config_cols
        return [field.id_string for field in self.fields if field.is_config]
