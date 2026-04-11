from __future__ import annotations

from .data_field import DataField


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
