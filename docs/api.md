# API Reference

This page provides auto-generated API documentation from type hints.

## Generating API Docs

To generate HTML API documentation locally:

```bash
# Install pdoc
uv add --dev pdoc

# Generate HTML docs
uv run pdoc dr_frames -o docs/api_html

# Or serve locally with live reload
uv run pdoc dr_frames
```

This opens a browser at `http://localhost:8080` with full API documentation extracted from type hints.

## Module Index

- `dr_frames.columns` - Column selection and reordering
- `dr_frames.filtering` - Row filtering
- `dr_frames.cells` - Cell-level operations
- `dr_frames.types` - Type coercion
- `dr_frames.aggregation` - GroupBy and reduction
- `dr_frames.parsing` - String list parsing
- `dr_frames.schema` - Data field metadata
- `dr_frames.profiling` - Column auto-tagging
- `dr_frames.formatting` - Table output formatting

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
