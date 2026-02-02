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

## Features

- **columns**: Column selection, manipulation, and reordering
- **filtering**: Row filtering with value matching, ranges, and composable filters
- **types**: Type coercion for numeric and string columns
- **aggregation**: GroupBy operations and seed aggregation
- **schema**: Data field definitions with metadata for display and type inference
- **profiling**: Column profiling and automatic tagging based on dtype and naming patterns
- **parsing**: String parsing utilities for list-like values
- **formatting**: Multi-format table output (console, markdown, latex, csv)
- **cells**: Cell-level operations for DataFrame manipulation

## Quick Start

```python
from dr_data import (
    select_subset,
    filter_to_range,
    coerce_numeric_cols,
    move_cols_to_beginning,
)

import pandas as pd

df = pd.DataFrame({
    "name": ["a", "b", "c"],
    "value": ["1.0", "2.0", "3.0"],
    "category": ["x", "y", "x"],
})

# Filter and transform
result = (
    df.pipe(coerce_numeric_cols, ["value"])
    .pipe(select_subset, {"category": "x"})
    .pipe(filter_to_range, "value", 0.5, 2.5)
)
```

## License

MIT
