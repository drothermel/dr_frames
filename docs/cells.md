# cells

Cell-level operations for DataFrame manipulation.

## Functions

### ensure_column
```python
def ensure_column(
    df: pd.DataFrame,
    column: str,
    default: Any,
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Add column with default value if missing. If column exists, fill nulls with default.

### fill_missing_values
```python
def fill_missing_values(
    df: pd.DataFrame,
    defaults: Mapping[str, Any],
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Fill nulls in specified columns with their default values.

### rename_columns
```python
def rename_columns(
    df: pd.DataFrame,
    mapping: Mapping[str, str],
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Rename columns. Silently skips columns not present in dataframe.

### map_column_with_fallback
```python
def map_column_with_fallback(
    df: pd.DataFrame,
    column: str,
    mapping: Mapping[str, Any],
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Map column values using mapping dict. Values not in mapping are kept unchanged.

### apply_column_converters
```python
def apply_column_converters(
    df: pd.DataFrame,
    converters: Mapping[str, Callable[[Any], Any]],
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Apply converter functions to specified columns.

### maybe_update_cell
```python
def maybe_update_cell(
    df: pd.DataFrame,
    row_index: int,
    column: str,
    value: Any,
    *,
    missing_markers: Iterable[Any] = (None, "N/A"),
    inplace: bool = False
) -> pd.DataFrame
```
Update cell only if current value is null or in missing_markers.

### force_set_cell
```python
def force_set_cell(
    df: pd.DataFrame,
    row_index: int,
    column: str,
    value: Any,
    *,
    default: Any = None,
    inplace: bool = False
) -> pd.DataFrame
```
Set cell value unconditionally. Creates column if missing.

### apply_if_column
```python
def apply_if_column(
    df: pd.DataFrame,
    column: str,
    func: Callable[[pd.Series], pd.Series],
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Apply function to column if it exists. No-op if column missing.

### require_row_index
```python
def require_row_index(
    df: pd.DataFrame,
    column: str,
    value: Any
) -> int
```
Find the single row index where column equals value. Asserts exactly one match.

### masked_getter
```python
def masked_getter(
    df: pd.DataFrame,
    mask: pd.Series,
    column: str
) -> Any
```
Get first value from column where mask is True. Returns None if no matches.

### masked_setter
```python
def masked_setter(
    df: pd.DataFrame,
    mask: pd.Series,
    column: str,
    value: Any,
    *,
    inplace: bool = False
) -> pd.DataFrame
```
Set column value where mask is True.

### group_col_by_prefix
```python
def group_col_by_prefix(
    df: pd.DataFrame,
    column: str,
    prefix_map: Mapping[str, str] | Iterable[tuple[str, str]] | None,
    *,
    output_col: str
) -> pd.Series
```
Group values by longest matching prefix. Unmatched values returned unchanged.

## Usage

```python
import pandas as pd
from dr_data import (
    ensure_column,
    map_column_with_fallback,
    maybe_update_cell,
)

df = pd.DataFrame({
    "id": [1, 2, 3],
    "status": ["done", None, "pending"],
})

# Ensure column exists with default
df = ensure_column(df, "notes", default="")

# Map values with fallback
df = map_column_with_fallback(df, "status", {
    "done": "completed",
    "pending": "in_progress",
})
# None stays None, unmapped values stay unchanged

# Update only if null
df = maybe_update_cell(df, 1, "status", "unknown")
```
