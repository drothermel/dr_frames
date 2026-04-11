from __future__ import annotations

from .aggregation import (
    aggregate_over_seeds,
    aggregate_by_group,
)
from .cells import (
    apply_column_converters,
    apply_if_column,
    ensure_column,
    fill_missing_values,
    force_set_cell,
    group_col_by_prefix,
    map_column_with_fallback,
    masked_getter,
    masked_setter,
    maybe_update_cell,
    rename_columns,
    require_row_index,
)
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
from .types import (
    coerce_numeric_cols,
    coerce_string_cols,
    is_string_series,
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
    "apply_column_converters",
    "apply_if_column",
    "coerce_numeric_cols",
    "coerce_string_cols",
    "ColInfo",
    "ComputedField",
    "DataField",
    "DataFormat",
    "DFColInfo",
    "drop_all_null_cols",
    "ensure_column",
    "fill_missing_values",
    "filter_to_best_metric",
    "filter_to_range",
    "filter_to_values",
    "force_set_cell",
    "get_cols_by_contains",
    "get_cols_by_prefix",
    "get_constant_cols",
    "get_groupwise_constant_cols",
    "group_col_by_prefix",
    "infer_series_base_tag_type",
    "infer_tags_from_series_sample",
    "is_string_series",
    "make_filter_fxn",
    "map_column_with_fallback",
    "masked_getter",
    "masked_setter",
    "maybe_pipe",
    "maybe_update_cell",
    "MetricDataField",
    "move_cols_to_beginning",
    "move_cols_with_prefix_to_end",
    "move_numeric_cols_to_end",
    "parse_list_string",
    "rename_columns",
    "require_row_index",
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
