# API Reference

This page provides auto-generated API documentation from type hints.

## Generating API Docs

To generate HTML API documentation locally:

```bash
# Install pdoc
uv add --dev pdoc

# Generate HTML docs
uv run pdoc dr_data -o docs/api_html

# Or serve locally with live reload
uv run pdoc dr_data
```

This opens a browser at `http://localhost:8080` with full API documentation extracted from type hints.

## Module Index

- `dr_data.columns` - Column selection and reordering
- `dr_data.filtering` - Row filtering
- `dr_data.cells` - Cell-level operations
- `dr_data.types` - Type coercion
- `dr_data.aggregation` - GroupBy and reduction
- `dr_data.parsing` - String list parsing
- `dr_data.schema` - Data field metadata
- `dr_data.profiling` - Column auto-tagging
- `dr_data.formatting` - Table output formatting

## Quick Type Reference

### Common Parameter Types

| Type | Description |
|------|-------------|
| `pd.DataFrame` | Pandas DataFrame |
| `pd.Series` | Pandas Series |
| `Sequence[str]` | List or tuple of strings |
| `Iterable[str]` | Any iterable of strings |
| `Mapping[str, Any]` | Dict-like mapping |
| `Callable[[pd.DataFrame], pd.Series]` | Function taking df, returning series |

### Common Return Types

| Type | Description |
|------|-------------|
| `pd.DataFrame` | New DataFrame (original unchanged unless `inplace=True`) |
| `list[str]` | List of column names |
| `dict[str, Any]` | Dictionary with string keys |
| `bool` | Boolean result |
| `float` | Numeric result (may be NaN) |
