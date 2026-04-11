from __future__ import annotations

from .aggregation import (
    aggregate_over_seeds,
    aggregate_by_group,
)
from .cells import (
    fill_missing_values,
    masked_getter,
    masked_setter,
    rename_columns,
)
from .namespaced import group_namespaced_values
from .columns import (
    drop_all_null_cols,
    get_cols_by_contains,
    get_cols_by_prefix,
    move_cols_to_beginning,
    move_cols_with_prefix_to_end,
    move_numeric_cols_to_end,
    strip_col_prefixes,
    strip_col_prefixes_batch,
)
from .constant import get_constant_cols, get_groupwise_constant_cols
from .coerce import (
    coerce_numeric_cols,
    coerce_string_cols,
)
from .filtering import (
    filter_to_best_metric,
    filter_to_range,
    filter_to_values,
    make_filter_fxn,
    select_subset,
)
from .parsing import parse_list_string
from .pipeline import maybe_pipe
from .profiling import (
    ColInfo,
    DFColInfo,
    infer_series_base_tag_type,
    infer_tags_from_series_sample,
)
from .schema import (
    ComputedField,
    DataField,
    DataFormat,
    MetricDataField,
)
from .unique import unique_by_col, unique_by_cols, unique_non_null

try:
    from .formatting import (  # noqa: F401
        FORMATTER_TYPES,
        OUTPUT_FORMATS,
        format_coverage_table,
        format_table,
    )

    _HAS_FORMATTING = True
except ImportError:
    _HAS_FORMATTING = False

__all__ = [
    "aggregate_over_seeds",
    "aggregate_by_group",
    "coerce_numeric_cols",
    "coerce_string_cols",
    "ColInfo",
    "ComputedField",
    "DataField",
    "DataFormat",
    "DFColInfo",
    "drop_all_null_cols",
    "fill_missing_values",
    "filter_to_best_metric",
    "filter_to_range",
    "filter_to_values",
    "get_cols_by_contains",
    "get_cols_by_prefix",
    "get_constant_cols",
    "get_groupwise_constant_cols",
    "group_namespaced_values",
    "infer_series_base_tag_type",
    "infer_tags_from_series_sample",
    "make_filter_fxn",
    "masked_getter",
    "masked_setter",
    "maybe_pipe",
    "MetricDataField",
    "move_cols_to_beginning",
    "move_cols_with_prefix_to_end",
    "move_numeric_cols_to_end",
    "parse_list_string",
    "rename_columns",
    "select_subset",
    "strip_col_prefixes",
    "strip_col_prefixes_batch",
    "unique_by_col",
    "unique_by_cols",
    "unique_non_null",
]

if _HAS_FORMATTING:
    __all__.extend(
        [
            "format_table",
            "format_coverage_table",
            "FORMATTER_TYPES",
            "OUTPUT_FORMATS",
        ]
    )

__version__ = "0.1.0"
