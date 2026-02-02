# parsing

Parse string representations of lists (common in CSV exports).

## Functions

### parse_list_string
```python
def parse_list_string(
    val: str
) -> list | None
```
Parse a string list representation into an actual list.
- `"[1, 2, 3]"` → `[1, 2, 3]`
- `"42"` → `[42]`
- Invalid/null → `None`

### parse_first_element
```python
def parse_first_element(
    val: str
) -> float
```
Parse and return the first element as float.
- `"[0.5, 0.25]"` → `0.5`
- `"42"` → `42.0`
- Invalid/empty → `NaN`

### sum_list_elements
```python
def sum_list_elements(
    val: str
) -> float
```
Parse and return the sum of all elements.
- `"[1, 2, 3]"` → `6.0`
- `"[4, 8]"` → `12.0`
- Invalid/empty → `NaN`

### is_homogeneous
```python
def is_homogeneous(
    val: str
) -> bool
```
Check if all elements in the list are equal.
- `"[0.125, 0.125, 0.125]"` → `True`
- `"[0.5, 0.25]"` → `False`
- Empty/null → `False`

## Usage

```python
import pandas as pd
from dr_data import is_homogeneous, parse_first_element, sum_list_elements

df = pd.DataFrame({
    "expert_sizes": ["[0.5, 0.25]", "[0.125, 0.125]", "[1, 2, 4]"],
    "num_experts": ["[8, 16]", "[32, 32]", "[4, 8, 16]"],
})

# Extract first element (granularity)
df["granularity"] = df["expert_sizes"].apply(parse_first_element)
# [0.5, 0.125, 1.0]

# Sum elements (total experts)
df["total_experts"] = df["num_experts"].apply(sum_list_elements)
# [24.0, 64.0, 28.0]

# Check homogeneity
df["is_uniform"] = df["expert_sizes"].apply(is_homogeneous)
# [False, True, False]
```
