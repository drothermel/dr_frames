from __future__ import annotations

from .aggregation import (
    aggregate_over_seeds,
    apply_aggregations,
    fillna_with_defaults,
    get_constant_cols,
    maybe_pipe,
    unique_by_col,
    unique_by_cols,
    unique_non_null,
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
    apply_skip,
    contained_cols,
    drop_all_null_cols,
    get_cols_by_contains,
    get_cols_by_prefix,
    move_cols_to_beginning,
    move_cols_with_prefix_to_end,
    move_numeric_cols_to_end,
    remaining_cols,
    strip_col_prefixes,
    strip_col_prefixes_batch,
)
from .filtering import (
    apply_filters_to_df,
    filter_to_best_metric,
    filter_to_range,
    filter_to_value,
    filter_to_values,
    make_filter_fxn,
    select_subset,
)
from .parsing import (
    is_homogeneous,
    parse_first_element,
    parse_list_string,
    sum_list_elements,
)
from .profiling import (
    ColInfo,
    DFColInfo,
    infer_col_name_contains_tags,
    infer_col_name_prefix_tags,
    infer_col_name_suffix_tags,
    infer_series_base_tag_type,
    infer_tags_from_series_sample,
    looks_like_json,
    looks_like_path,
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
    "apply_aggregations",
    "apply_column_converters",
    "apply_filters_to_df",
    "apply_if_column",
    "apply_skip",
    "coerce_numeric_cols",
    "coerce_string_cols",
    "ColInfo",
    "ComputedField",
    "contained_cols",
    "DataField",
    "DataFormat",
    "DFColInfo",
    "drop_all_null_cols",
    "ensure_column",
    "fill_missing_values",
    "fillna_with_defaults",
    "filter_to_best_metric",
    "filter_to_range",
    "filter_to_value",
    "filter_to_values",
    "force_set_cell",
    "get_cols_by_contains",
    "get_cols_by_prefix",
    "get_constant_cols",
    "group_col_by_prefix",
    "infer_col_name_contains_tags",
    "infer_col_name_prefix_tags",
    "infer_col_name_suffix_tags",
    "infer_series_base_tag_type",
    "infer_tags_from_series_sample",
    "is_homogeneous",
    "is_string_series",
    "looks_like_json",
    "looks_like_path",
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
    "parse_first_element",
    "parse_list_string",
    "remaining_cols",
    "rename_columns",
    "require_row_index",
    "select_subset",
    "strip_col_prefixes",
    "strip_col_prefixes_batch",
    "sum_list_elements",
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
