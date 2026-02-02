# dr_data

Pandas/DataFrame utilities for data manipulation, filtering, aggregation, and schema management.

## Installation

```bash
pip install dr-data
```

For table formatting features (console, markdown, latex):
```bash
pip install dr-data[formatting]
```

## Quick Start

```python
import pandas as pd
from dr_data import (
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

## Module Overview

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **columns** | Column selection & reordering | `move_cols_to_beginning`, `get_cols_by_prefix`, `strip_col_prefixes` |
| **filtering** | Row filtering | `select_subset`, `filter_to_range`, `make_filter_fxn` |
| **cells** | Cell-level operations | `ensure_column`, `map_column_with_fallback`, `force_set_cell` |
| **types** | Type coercion | `coerce_numeric_cols`, `coerce_string_cols` |
| **aggregation** | GroupBy & reduction | `aggregate_over_seeds`, `apply_aggregations`, `unique_non_null` |
| **parsing** | String list parsing | `parse_first_element`, `sum_list_elements`, `is_homogeneous` |
| **schema** | Data field metadata | `DataField`, `ComputedField`, `DataFormat` |
| **profiling** | Column auto-tagging | `DFColInfo`, `ColInfo`, `looks_like_json` |
| **formatting** | Table output | `format_table`, `format_coverage_table` |

## Documentation

- [Full API Reference](docs/api.md)
- Module guides: [columns](docs/columns.md) | [filtering](docs/filtering.md) | [cells](docs/cells.md) | [types](docs/types.md) | [aggregation](docs/aggregation.md) | [parsing](docs/parsing.md) | [schema](docs/schema.md) | [profiling](docs/profiling.md) | [formatting](docs/formatting.md)
- [Recipes & Patterns](docs/recipes.md)

### Auto-generated API Docs

```bash
# Serve interactive docs locally
uv run pdoc dr_data

# Generate static HTML
uv run pdoc dr_data -o docs/api_html
```

## Quick Reference

### Column Operations
```python
from dr_data import (
    contained_cols,          # cols that exist in df
    remaining_cols,          # cols NOT in a list
    get_cols_by_prefix,      # cols starting with prefix
    get_cols_by_contains,    # cols containing substring
    move_cols_to_beginning,  # reorder cols
    move_cols_with_prefix_to_end,
    strip_col_prefixes,      # rename by removing prefix
    drop_all_null_cols,      # remove empty columns
)
```

### Filtering
```python
from dr_data import (
    select_subset,           # filter by exact column values
    apply_filters_to_df,     # filter by value lists
    filter_to_value,         # single value filter
    filter_to_values,        # multi-value filter
    filter_to_range,         # numeric range filter
    filter_to_best_metric,   # keep best per group
    make_filter_fxn,         # compose filters
)
```

### Cell Operations
```python
from dr_data import (
    ensure_column,           # add column if missing
    fill_missing_values,     # fillna with defaults dict
    rename_columns,          # safe rename (skips missing)
    map_column_with_fallback,# map values, keep unmapped
    apply_column_converters, # apply functions to columns
    maybe_update_cell,       # update if currently null
    force_set_cell,          # always update
    masked_getter,           # get value where mask is true
    masked_setter,           # set value where mask is true
)
```

### Type Coercion
```python
from dr_data import (
    coerce_numeric_cols,     # convert to float/int
    coerce_string_cols,      # convert to string dtype
    is_string_series,        # check if series is strings
)
```

### Aggregation
```python
from dr_data import (
    aggregate_over_seeds,    # mean/std/count by config
    apply_aggregations,      # flexible groupby
    unique_non_null,         # unique values excluding null
    unique_by_col,           # unique values in column
    get_constant_cols,       # cols with single value
    fillna_with_defaults,    # fill nulls from dict
    maybe_pipe,              # conditional pipe
)
```

### Parsing
```python
from dr_data import (
    parse_list_string,       # "[1,2,3]" -> [1,2,3]
    parse_first_element,     # "[1,2,3]" -> 1.0
    sum_list_elements,       # "[1,2,3]" -> 6.0
    is_homogeneous,          # "[1,1,1]" -> True
)
```

### Schema
```python
from dr_data import (
    DataField,               # field with metadata
    ComputedField,           # derived field
    MetricDataField,         # metric with group info
    DataFormat,              # container for fields
)
```

### Profiling
```python
from dr_data import (
    DFColInfo,               # catalog of column info
    ColInfo,                 # single column metadata
    looks_like_json,         # detect JSON strings
    looks_like_path,         # detect file paths
    infer_series_base_tag_type,  # infer dtype tags
)
```

### Formatting (requires `[formatting]` extra)
```python
from dr_data import (
    format_table,            # render table in multiple formats
    format_coverage_table,   # show column coverage stats
    FORMATTER_TYPES,         # available formatters
    OUTPUT_FORMATS,          # available output formats
)
```

## License

MIT
