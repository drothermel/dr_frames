# aggregation

GroupBy operations, seed aggregation, and unique value utilities.

## Functions

### aggregate_over_seeds
```python
def aggregate_over_seeds(
    df: pd.DataFrame,
    config_cols: list[str],
    metric_cols: list[str] | None = None,
    agg_funcs: list[str] | None = None
) -> pd.DataFrame
```
Aggregate metrics over duplicate configurations (treating duplicates as seeds).

- `config_cols`: Columns defining unique configurations
- `metric_cols`: Columns to aggregate (default: columns starting with `eval/`)
- `agg_funcs`: Aggregation functions (default: `["mean", "std", "count"]`)

Output columns: `{metric_col}_{agg_func}` (e.g., `eval/loss_mean`)

### apply_aggregations
```python
def apply_aggregations(
    df: pd.DataFrame,
    group_col: str,
    agg_over_cols: Sequence[str],
    drop_cols: Sequence[str] | None = None,
    start_cols: Sequence[str] | None = None,
    sort_cols: Sequence[str] | None = None,
    end_prefix: str = "metrics_"
) -> pd.DataFrame
```
Flexible groupby with automatic aggregation:
- Numeric columns: `mean`
- Non-numeric columns: `first`

### unique_non_null
```python
def unique_non_null(
    values: pd.Series | Iterable[Any]
) -> list[Any]
```
Return unique, non-null values.

### unique_by_col
```python
def unique_by_col(
    df: pd.DataFrame,
    col: str
) -> list[Any]
```
Return unique values from a column (including nulls).

### unique_by_cols
```python
def unique_by_cols(
    df: pd.DataFrame,
    cols: Sequence[str]
) -> dict[str, Any]
```
Return unique values for multiple columns as a dict.

### get_constant_cols
```python
def get_constant_cols(
    df: pd.DataFrame,
    skip: Iterable[str] = ()
) -> dict[str, Any]
```
Return `{column: value}` for columns with a single unique value.

### maybe_pipe
```python
def maybe_pipe(
    df: pd.DataFrame,
    condition: bool | Callable[[pd.DataFrame], bool] | Iterable | Mapping,
    func: Callable[..., pd.DataFrame],
    *args: Any,
    **kwargs: Any
) -> pd.DataFrame
```
Conditionally apply function in a pipe. Condition can be bool or callable.

## Usage

```python
import pandas as pd
from dr_frames import aggregate_over_seeds, get_constant_cols, maybe_pipe

df = pd.DataFrame({
    "model": ["A", "A", "A", "B", "B", "B"],
    "seed": [1, 2, 3, 1, 2, 3],
    "lr": [0.01] * 6,
    "eval/loss": [0.5, 0.52, 0.48, 0.6, 0.62, 0.58],
})

# Aggregate over seeds
agg = aggregate_over_seeds(df, config_cols=["model", "lr"])
# model  lr    eval/loss_mean  eval/loss_std  eval/loss_count
# A      0.01  0.50            0.02           3
# B      0.01  0.60            0.02           3

# Find constant columns
constants = get_constant_cols(df)
# {"lr": 0.01}

# Conditional pipe
result = df.pipe(
    maybe_pipe,
    len(df) > 5,  # only apply if condition true
    lambda x: x.head(3)
)
```
