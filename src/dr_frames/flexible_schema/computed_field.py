from __future__ import annotations

from collections.abc import Callable

import pandas as pd
from pydantic import Field

from .data_field import DataField


class ComputedField(DataField):
    source_columns: list[str] = Field(default_factory=list)
    compute: Callable[[pd.DataFrame], pd.Series] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return self.compute(df)
