# parsing

Parse string representations of lists (common in CSV exports).

## Functions

### parse_list_string
```python
def parse_list_string(
    val: Any
) -> list | None
```
Parse a string list representation into an actual list.
- `"[1, 2, 3]"` → `[1, 2, 3]`
- `"42"` → `[42]`
- Invalid/null → `None`

## Usage

```python
import pandas as pd
from dr_frames import parse_list_string

df = pd.DataFrame({
    "expert_sizes": ["[0.5, 0.25]", "[0.125, 0.125]", "[1, 2, 4]"],
    "num_experts": ["[8, 16]", "[32, 32]", "[4, 8, 16]"],
})

# Parse once, then derive what you need in plain Python
df["parsed_sizes"] = df["expert_sizes"].apply(parse_list_string)
df["granularity"] = df["parsed_sizes"].apply(
    lambda values: float(values[0]) if values else float("nan")
)

df["parsed_counts"] = df["num_experts"].apply(parse_list_string)
df["total_experts"] = df["parsed_counts"].apply(
    lambda values: float(sum(float(item) for item in values)) if values else float("nan")
)

df["is_uniform"] = df["parsed_sizes"].apply(
    lambda values: bool(values) and len(set(values)) == 1
)
```
