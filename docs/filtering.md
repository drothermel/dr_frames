# filtering

Row filtering with composable filter functions.

## Functions

### select_subset
```python
def select_subset(
    df: pd.DataFrame,
    filters: Mapping[str, Any] | list[tuple[str, Any]] | None = None
) -> pd.DataFrame
```
Return rows matching the column/value pairs. Use `None` to match null values.

### filter_to_values
```python
def filter_to_values(
    df: pd.DataFrame,
    column: str,
    values: Sequence[float | str | None]
) -> pd.DataFrame
```
Filter to rows matching any value in the sequence. Use a one-item sequence for exact matches and include `None` to match nulls.

### filter_to_range
```python
def filter_to_range(
    df: pd.DataFrame,
    column: str,
    min_val: float,
    max_val: float
) -> pd.DataFrame
```
Filter to rows where column value is within [min_val, max_val] inclusive.

### filter_to_best_metric
```python
def filter_to_best_metric(
    df: pd.DataFrame,
    group_cols: list[str],
    metric_col: str,
    lower_is_better: bool = True
) -> pd.DataFrame
```
Keep only the row with best metric value for each group.

### make_filter_fxn
```python
def make_filter_fxn(
    filters: list[tuple[Callable, ...]]
) -> Callable[[pd.DataFrame], pd.DataFrame]
```
Create a composed filter function from a list of `(fn, *args)` tuples.

## Usage

```python
import pandas as pd
from dr_frames import (
    filter_to_range,
    filter_to_values,
    make_filter_fxn,
    select_subset,
)

df = pd.DataFrame({
    "model": ["A", "A", "B", "B"],
    "lr": [0.01, 0.001, 0.01, 0.001],
    "loss": [0.5, 0.4, 0.6, 0.3],
})

# Simple exact match
subset = select_subset(df, {"model": "A"})

# Range filter
in_range = filter_to_range(df, "lr", 0.001, 0.01)

# Compose multiple filters
my_filter = make_filter_fxn([
    (filter_to_values, "model", ["A"]),
    (filter_to_range, "lr", 0.001, 0.01),
])
result = my_filter(df)
```
