# dr_frames

Pandas/DataFrame utilities for data manipulation, filtering, aggregation, and schema management.

Primitive quick reference for agents:
- `primitives.columns`: `rename_columns`, `move_cols_to_beginning`, `strip_col_prefixes`, `drop_all_null_cols`, `drop_all_constant_cols`, `get_cols_by_prefix`, `get_cols_by_contains`, `move_cols_with_prefix_to_end`, `move_numeric_cols_to_end`
- `primitives.filtering`: `select_subset`, `filter_to_values`, `filter_to_range`, `make_filter_fxn`
- `primitives.ranking`: `select_best_by_metric`
- `primitives.coerce`: `coerce_numeric_cols`, `coerce_string_cols`
- `primitives.aggregation`: `aggregate_over_seeds`, `aggregate_by_group`
- `primitives.missing`: `fill_missing_values`
- `primitives.masked`: `masked_getter`, `masked_setter`
- `primitives.constant`: `get_constant_cols`, `get_groupwise_constant_cols`
- `primitives.unique`: `unique_non_null`, `unique_by_col`, `unique_by_cols`
- `primitives.namespaced`: `group_namespaced_values`
- `primitives.pipeline`: `maybe_pipe`
- `primitives.parsing`: `parse_list_string`

## Installation

```bash
uv add dr-frames
```

## Quick Start

```python
import pandas as pd
from dr_frames import (
    coerce_numeric_cols,
    filter_to_range,
    move_cols_to_beginning,
    select_subset,
)

df = pd.DataFrame({
    "name": ["alice", "bob", "charlie"],
    "value": ["1.0", "2.0", "3.0"],
    "category": ["x", "y", "x"],
})

result = (
    df.pipe(coerce_numeric_cols, ["value"])
    .pipe(select_subset, {"category": "x"})
    .pipe(filter_to_range, "value", 0.5, 2.5)
)
```

## Flexible Schema

`flexible_schema` is the higher-level part of the library for working with
dataframes whose columns you did not design yourself.

- `DataField` describes a logical field and can resolve which dataframe column
  it maps to.
- `ComputedField` describes a derived field that should be added from existing
  columns before downstream use.
- `MetricDataField` describes metric columns, especially prefixed metric names
  such as `eval/...`.
- `DataFormat` is the container that ties those pieces together and gives you a
  reusable view of a dataframe schema.

Typical usage:
- build a `DataFormat` from a dataframe with `DataFormat.from_df(...)` or from
  a field-description mapping with `DataFormat.from_dict(...)`
- inspect unresolved fields and discovered metrics
- add computed fields for columns you want to derive once and reuse
- call `prepare_for_plotting(...)` to produce a dataframe restricted to the
  known fields, computed fields, and metrics
- use `metric_col(...)`, `get_metric(...)`, and `get_config_columns(...)` to
  drive plotting or grouped analysis code without hardcoding raw column names

Minimal example:

```python
from dr_frames import ComputedField, DataField, DataFormat

fmt = DataFormat(
    fields=[
        DataField(id_string="model", column_name="model_name"),
        DataField(id_string="dataset"),
    ],
    computed_fields=[
        ComputedField(
            id_string="is_large",
            source_columns=["params_millions"],
            compute=lambda df: df["params_millions"] > 1000,
        )
    ],
)

plot_df = fmt.prepare_for_plotting(df)
config_cols = fmt.get_config_columns()
```

## License

MIT
