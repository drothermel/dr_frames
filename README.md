# dr_frames

Pandas/DataFrame utilities for data manipulation, filtering, aggregation, and schema management.

Common entry points:
- `maybe_pipe` for conditional `df.pipe(...)` steps
- `select_subset`, `filter_to_values`, and `filter_to_range` for filtering
- `coerce_numeric_cols` and `coerce_string_cols` for dtype cleanup
- `aggregate_over_seeds` and `aggregate_by_group` for grouped reductions
- `unique_non_null`, `unique_by_col`, and `unique_by_cols` for unique-value inspection
- `get_constant_cols` and `get_groupwise_constant_cols` for constant-value inspection
- `move_cols_to_beginning` and `strip_col_prefixes` for column cleanup

## Installation

```bash
pip install dr-frames
```

For table formatting features (console, markdown, latex):
```bash
pip install dr-frames[formatting]
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

## Module Overview

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **columns** | Column selection & reordering | `move_cols_to_beginning`, `get_cols_by_prefix`, `strip_col_prefixes` |
| **filtering** | Row filtering | `select_subset`, `filter_to_range`, `make_filter_fxn` |
| **cells** | Cell-level operations | `ensure_column`, `map_column_with_fallback`, `force_set_cell` |
| **types** | Type coercion | `coerce_numeric_cols`, `coerce_string_cols` |
| **aggregation** | GroupBy & reduction | `aggregate_over_seeds`, `aggregate_by_group` |
| **unique** | Unique-value inspection | `unique_non_null`, `unique_by_col`, `unique_by_cols` |
| **constant** | Constant-value inspection | `get_constant_cols`, `get_groupwise_constant_cols` |
| **pipeline** | Pipe-friendly orchestration | `maybe_pipe` |
| **parsing** | String list parsing | `parse_list_string` |
| **schema** | Data field metadata | `DataField`, `ComputedField`, `DataFormat` |
| **profiling** | Column auto-tagging | `DFColInfo`, `ColInfo`, `infer_tags_from_series_sample` |
| **formatting** | Table output | `format_table`, `format_coverage_table` |

## Documentation

- [Full API Reference](docs/api.md)
- Module guides: [columns](docs/columns.md) | [filtering](docs/filtering.md) | [cells](docs/cells.md) | [types](docs/types.md) | [aggregation](docs/aggregation.md) | [parsing](docs/parsing.md) | [schema](docs/schema.md) | [profiling](docs/profiling.md) | [formatting](docs/formatting.md)
- [Recipes & Patterns](docs/recipes.md)

### Auto-generated API Docs

```bash
# Serve interactive docs locally
uv run pdoc dr_frames

# Generate static HTML
uv run pdoc dr_frames -o docs/api_html
```

## Quick Reference

### Column Operations
```python
from dr_frames import (
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
from dr_frames import (
    select_subset,           # filter by exact column values
    filter_to_values,        # multi-value filter
    filter_to_range,         # numeric range filter
    filter_to_best_metric,   # keep best per group
    make_filter_fxn,         # compose filters
)
```

### Cell Operations
```python
from dr_frames import (
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
from dr_frames import (
    coerce_numeric_cols,     # convert to float/int
    coerce_string_cols,      # convert to string dtype
    is_string_series,        # check if series is strings
)
```

### Aggregation
```python
from dr_frames import (
    aggregate_over_seeds,    # mean/std/count by config
    aggregate_by_group,      # generic grouped aggregation
)
```

### Unique
```python
from dr_frames import (
    unique_non_null,         # unique values excluding null
    unique_by_col,           # unique values in column
    unique_by_cols,          # unique values across several columns
)
```

### Constants
```python
from dr_frames import (
    get_constant_cols,           # cols constant across the full dataframe
    get_groupwise_constant_cols, # cols constant within each group
)
```

### Pipeline
```python
from dr_frames import (
    maybe_pipe,              # conditional pipe step
)
```

### Parsing
```python
from dr_frames import (
    parse_list_string,       # "[1,2,3]" -> [1,2,3]
)
```

### Schema
```python
from dr_frames import (
    DataField,               # field with metadata
    ComputedField,           # derived field
    MetricDataField,         # metric with group info
    DataFormat,              # container for fields
)
```

### Profiling
```python
from dr_frames import (
    DFColInfo,               # catalog of column info
    ColInfo,                 # single column metadata
    infer_series_base_tag_type,  # infer dtype tags
    infer_tags_from_series_sample,  # sample-based path/json tags
)
```

### Formatting (requires `[formatting]` extra)
```python
from dr_frames import (
    format_table,            # render table in multiple formats
    format_coverage_table,   # show column coverage stats
    FORMATTER_TYPES,         # available formatters
    OUTPUT_FORMATS,          # available output formats
)
```

## License

MIT
