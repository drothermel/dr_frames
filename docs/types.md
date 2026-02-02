# types

Type coercion for numeric and string columns.

## Functions

### coerce_numeric_cols
```python
def coerce_numeric_cols(
    df: pd.DataFrame,
    columns: Sequence[str] | Iterable[str],
    dtype: type[float] | type[int] = float
) -> pd.DataFrame
```
Convert columns to numeric type. Invalid values become NaN.

For `dtype=int`:
- Asserts all non-null values are integers
- Uses nullable `Int64` dtype if nulls present

### coerce_string_cols
```python
def coerce_string_cols(
    df: pd.DataFrame,
    columns: Sequence[str] | Iterable[str]
) -> pd.DataFrame
```
Convert columns to pandas `string` dtype.

### is_string_series
```python
def is_string_series(
    series: pd.Series
) -> bool
```
Check if all non-null values in series are strings.

## Usage

```python
import pandas as pd
from dr_data import coerce_numeric_cols, coerce_string_cols

df = pd.DataFrame({
    "count": ["1", "2", "3"],
    "value": ["1.5", "2.5", "invalid"],
    "id": [1, 2, 3],
})

# Convert to float (invalid becomes NaN)
df = coerce_numeric_cols(df, ["value"])
# value: [1.5, 2.5, NaN]

# Convert to int (must be valid integers)
df = coerce_numeric_cols(df, ["count"], dtype=int)
# count: [1, 2, 3]

# Convert to string dtype
df = coerce_string_cols(df, ["id"])
# id: ["1", "2", "3"] with string dtype
```
