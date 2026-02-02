# profiling

Automatic column tagging based on dtype and naming patterns.

## Classes

### DFColInfo
```python
class DFColInfo(BaseModel):
    columns: dict[str, ColInfo] = {}

    # Type inference config
    pd_type_to_tags: list[tuple[Callable, list[str]]]  # dtype -> tags
    pd_default_type: list[str] = ["str"]               # fallback tags

    # Name pattern config
    col_name_contains_map: dict[tuple[str, ...], str]  # substrings -> tag
    col_name_suffix_map: dict[tuple[str, ...], str]    # suffixes -> tag
    col_name_prefix_map: dict[tuple[str, ...], str]    # prefixes -> tag

    # Content detection config
    path_like_extensions: set[str]  # file extensions for path detection
```

**Methods:**
- `update_from_df(df)` - Profile all columns in DataFrame
- `get(name) -> ColInfo | None` - Get info for a column
- `names_with_tag(tag) -> list[str]` - Get all column names with a tag

### ColInfo
```python
class ColInfo(BaseModel):
    catalog: DFColInfo      # Parent catalog
    name: str               # Column name
    dtype: str | None       # pandas dtype
    tags: set[str] = set()  # Inferred tags
```

**Methods:**
- `update_tags(series)` - Infer and add tags from series
- `has_tag(tag) -> bool` - Check if tag present
- `add_tags(extra)` - Manually add tags

## Functions

### looks_like_json
```python
def looks_like_json(value: Any) -> bool
```
Check if value looks like a JSON string (starts with `{` or `[` and parses).

### looks_like_path
```python
def looks_like_path(value: Any, path_extensions: set[str]) -> bool
```
Check if value looks like a file path (contains `/` or `\`, or has known extension).

### infer_series_base_tag_type
```python
def infer_series_base_tag_type(
    series: pd.Series,
    pd_type_to_tags: list[tuple[Callable, list[str]]],
    pd_default_type: list[str]
) -> set[str]
```
Infer tags from series dtype. Adds `"nullable"` if series contains nulls.

### infer_col_name_contains_tags / suffix_tags / prefix_tags
```python
def infer_col_name_contains_tags(name: str, mapping: dict) -> set[str]
def infer_col_name_suffix_tags(name: str, mapping: dict) -> set[str]
def infer_col_name_prefix_tags(name: str, mapping: dict) -> set[str]
```
Infer tags from column name patterns.

### infer_tags_from_series_sample
```python
def infer_tags_from_series_sample(
    series: pd.Series,
    path_like_extensions: set[str]
) -> set[str]
```
Infer tags by sampling first non-null value (detects paths, JSON).

## Default Tags

**From dtype:**
- `bool` - boolean columns
- `int`, `numeric` - integer columns
- `float`, `numeric` - float columns
- `datetime` - datetime columns
- `categorical` - categorical dtype
- `str` - fallback for object dtype
- `nullable` - if column has any nulls

**From column name:**
- `config` - name contains "config", "kwargs", "settings", "params"
- `path` - name ends with "_path", "_dir"
- `id` - name ends with "_id"
- `categorical` - name ends with "_tag", "_tags"
- `bool_like` - name starts with "is_", "has_"
- `metric` - name starts with "metric_"

**From content:**
- `path` - values look like file paths
- `json` - values look like JSON strings

## Usage

```python
import pandas as pd
from dr_frames import DFColInfo

df = pd.DataFrame({
    "user_id": [1, 2, 3],
    "is_active": [True, False, True],
    "config_path": ["/a/b.json", "/c/d.json", "/e/f.json"],
    "settings": ['{"lr": 0.01}', '{"lr": 0.02}', '{"lr": 0.03}'],
    "score": [0.9, None, 0.7],
})

# Profile DataFrame
col_info = DFColInfo()
col_info.update_from_df(df)

# Query tags
col_info.columns["user_id"].tags
# {'int', 'numeric', 'id'}

col_info.columns["is_active"].tags
# {'bool', 'bool_like'}

col_info.columns["config_path"].tags
# {'str', 'path'}

col_info.columns["settings"].tags
# {'str', 'config', 'json'}

col_info.columns["score"].tags
# {'float', 'numeric', 'nullable'}

# Find columns by tag
col_info.names_with_tag("numeric")
# ['user_id', 'score']

col_info.names_with_tag("config")
# ['config_path', 'settings']
```
