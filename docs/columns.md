# columns

Column selection, reordering, and prefix operations.

## Functions

### apply_skip
```python
def apply_skip(
    columns: Sequence[str] | pd.Index,
    skip: Iterable[str] = ()
) -> list[str]
```
Return `columns` excluding any names present in `skip`.

### contained_cols
```python
def contained_cols(
    df: pd.DataFrame,
    columns: Sequence[str]
) -> list[str]
```
Return the subset of `columns` that exist in the dataframe.

### remaining_cols
```python
def remaining_cols(
    df: pd.DataFrame,
    cols: Iterable[str]
) -> list[str]
```
Return dataframe columns that are NOT listed in `cols`.

### get_cols_by_prefix
```python
def get_cols_by_prefix(
    df: pd.DataFrame,
    prefix: str,
    skip: Iterable[str] = ()
) -> list[str]
```
Return dataframe columns that start with the given prefix.

### get_cols_by_contains
```python
def get_cols_by_contains(
    df: pd.DataFrame,
    substr: str,
    skip: Iterable[str] = ()
) -> list[str]
```
Return dataframe columns that contain the given substring.

### strip_col_prefixes
```python
def strip_col_prefixes(
    df: pd.DataFrame,
    prefix: str,
    skip: Iterable[str] = ()
) -> pd.DataFrame
```
Strip a prefix from column names. Columns not starting with the prefix are unchanged.

### strip_col_prefixes_batch
```python
def strip_col_prefixes_batch(
    df: pd.DataFrame,
    prefix_map: Mapping[str, Iterable[str]] | None = None
) -> pd.DataFrame
```
Apply multiple prefix-stripping rules. Prefixes are sorted by length (longest first) to handle nested prefixes correctly.

### move_cols_to_beginning
```python
def move_cols_to_beginning(
    df: pd.DataFrame,
    cols: list[str]
) -> pd.DataFrame
```
Reorder columns so `cols` appear first, followed by remaining columns.

### move_numeric_cols_to_end
```python
def move_numeric_cols_to_end(
    df: pd.DataFrame
) -> pd.DataFrame
```
Move all numeric columns to the end of the dataframe.

### move_cols_with_prefix_to_end
```python
def move_cols_with_prefix_to_end(
    df: pd.DataFrame,
    prefix: str,
    skip: Iterable[str] = ()
) -> pd.DataFrame
```
Move columns with the given prefix to the end.

### drop_all_null_cols
```python
def drop_all_null_cols(
    df: pd.DataFrame
) -> pd.DataFrame
```
Drop columns consisting entirely of null-like or blank-string values.

## Usage

```python
import pandas as pd
from dr_frames import (
    get_cols_by_prefix,
    move_cols_to_beginning,
    strip_col_prefixes,
)

df = pd.DataFrame({
    "id": [1, 2],
    "config_lr": [0.01, 0.02],
    "config_batch": [32, 64],
    "metric_loss": [0.5, 0.6],
})

# Find config columns
config_cols = get_cols_by_prefix(df, "config_")
# ['config_lr', 'config_batch']

# Strip prefix and move to beginning
result = (
    df.pipe(strip_col_prefixes, "config_")
    .pipe(move_cols_to_beginning, ["id", "lr", "batch"])
)
```
