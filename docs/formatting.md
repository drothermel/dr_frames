# formatting

Multi-format table rendering (console, markdown, latex, csv).

**Note:** Requires the `[formatting]` extra: `pip install dr-data[formatting]`

## Functions

### format_table
```python
def format_table(
    data: list[dict] | pd.DataFrame | list[list],
    headers: list[str] | None = None,
    output_format: str = "console",
    column_config: dict[str, dict] | None = None,
    title: str | None = None,
    table_style: str = "lines",
    disable_numparse: bool = True
) -> str | Table
```

**Parameters:**
- `data`: Input data (DataFrame, list of dicts, or list of lists)
- `headers`: Column headers (auto-detected if None)
- `output_format`: One of `"console"`, `"markdown"`, `"latex"`, `"plain"`, `"csv"`
- `column_config`: Per-column formatting config (see below)
- `title`: Table title (console only)
- `table_style`: `"lines"` or `"zebra"` (console only)

**Returns:** String for text formats, `rich.Table` for console format.

### format_coverage_table
```python
def format_coverage_table(
    df: pd.DataFrame,
    title: str = "Column Coverage",
    output_format: str = "console",
    table_style: str = "lines",
    disable_numparse: bool = True
) -> str
```
Generate a table showing non-null percentage for each column.

## Column Config

Per-column formatting via `column_config` dict:

```python
column_config = {
    "column_name": {
        "header": "Display Header",    # Override column header
        "formatter": "decimal",        # Formatter type
        "precision": 2,                # Formatter-specific options
    }
}
```

## Formatter Types

| Name | Description | Options |
|------|-------------|---------|
| `scientific` | Scientific notation | `precision` (default: 2) |
| `decimal` | Fixed decimal places | `precision` (default: 3) |
| `integer` | Integer with commas | - |
| `comma` | Number with commas | - |
| `truncate` | Truncate long strings | `max_length` (default: 50) |
| `string` | Plain string (default) | - |

## Output Formats

| Format | Description | Library |
|--------|-------------|---------|
| `console` | Rich table with colors | `rich` |
| `markdown` | GitHub-flavored markdown | `tabulate` |
| `latex` | LaTeX table | `tabulate` |
| `plain` | Plain text | `tabulate` |
| `csv` | Simple CSV-like | `tabulate` |

## Usage

```python
import pandas as pd
from dr_data import format_coverage_table, format_table

df = pd.DataFrame({
    "model": ["A", "B", "C"],
    "loss": [0.00123, 0.00456, 0.00789],
    "accuracy": [0.9234, 0.8765, 0.8432],
    "params": [1000000, 2000000, 5000000],
})

# Basic markdown table
print(format_table(df, output_format="markdown"))

# Formatted table with config
config = {
    "loss": {"header": "Loss", "formatter": "scientific", "precision": 2},
    "accuracy": {"header": "Acc %", "formatter": "decimal", "precision": 1},
    "params": {"header": "Parameters", "formatter": "comma"},
}
print(format_table(df, output_format="markdown", column_config=config))

# Output:
# | model   | Loss     | Acc % | Parameters   |
# |---------|----------|-------|--------------|
# | A       | 1.23e-03 | 92.3  | 1,000,000    |
# | B       | 4.56e-03 | 87.7  | 2,000,000    |
# | C       | 7.89e-03 | 84.3  | 5,000,000    |

# Coverage table
print(format_coverage_table(df, output_format="plain"))
```
