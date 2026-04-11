from __future__ import annotations

from typing import Literal, Self

import pandas as pd
from pydantic import BaseModel, computed_field, model_validator


class DataField(BaseModel):
    id_string: str
    description: str | None = None
    column_name: str | None = None
    display_name: str | None = None
    altair_type: Literal["Q", "N", "O", "T"] | None = None
    scale_hint: Literal["linear", "log"] | None = None
    is_config: bool = True

    @model_validator(mode="after")
    def derive_display_name(self) -> Self:
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
        if self.id_string in df.columns:
            return self.id_string
        raise ValueError(
            f"Cannot resolve column for field with id_string='{self.id_string}'. "
            f"Neither column_name nor id_string '{self.id_string}' found in DataFrame columns. "
            f"Available columns: {list(df.columns)}"
        )

    def infer_altair_type(self, df: pd.DataFrame) -> str:
        if self.altair_type:
            return self.altair_type
        try:
            col = self.resolve_column(df)
        except ValueError:
            return "N"
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            return "Q"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "T"
        return "N"
