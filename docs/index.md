# dr_frames Documentation

Pandas/DataFrame utilities for data manipulation, filtering, aggregation, and schema management.

## Design Philosophy

- **Pipe-friendly**: All functions work with `df.pipe()` for readable chains
- **Non-mutating by default**: Functions return new DataFrames unless `inplace=True`
- **Fail fast**: Uses assertions for validation, not silent failures
- **Type-safe**: Comprehensive type hints on all public functions

## Modules

### Data Manipulation
- [columns](columns.md) - Column selection, reordering, and prefix operations
- [cells](cells.md) - Cell-level operations: ensure, update, map values
- [types](types.md) - Type coercion for numeric and string columns
- [filtering](filtering.md) - Row filtering with composable filter functions

### Data Reduction
- [aggregation](aggregation.md) - GroupBy operations, seed aggregation, unique values

### String Processing
- [parsing](parsing.md) - Parse string representations of lists

### Metadata & Schema
- [schema](schema.md) - Data field definitions with display metadata
- [profiling](profiling.md) - Automatic column tagging based on dtype and naming

### Output
- [formatting](formatting.md) - Multi-format table rendering (console, markdown, latex)

## Common Patterns

See [Recipes & Patterns](recipes.md) for common usage patterns.

## API Reference

See [Full API Reference](api.md) for auto-generated documentation from type hints.
