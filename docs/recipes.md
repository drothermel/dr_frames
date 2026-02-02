# Recipes & Patterns

Common usage patterns combining multiple dr_frames functions.

## Data Loading Pipeline

Clean and standardize data after loading from CSV/parquet:

```python
import pandas as pd
from dr_frames import (
    coerce_numeric_cols,
    drop_all_null_cols,
    move_cols_to_beginning,
    strip_col_prefixes,
)

def load_and_clean(path: str, id_cols: list[str]) -> pd.DataFrame:
    return (
        pd.read_csv(path)
        .pipe(drop_all_null_cols)
        .pipe(strip_col_prefixes, "config.")
        .pipe(strip_col_prefixes, "summary.")
        .pipe(coerce_numeric_cols, ["lr", "batch_size", "epochs"])
        .pipe(move_cols_to_beginning, id_cols)
    )
```

## Experiment Filtering

Filter experiments to specific configurations:

```python
from dr_frames import filter_to_range, filter_to_value, make_filter_fxn

# Define reusable filter
best_settings = make_filter_fxn([
    (filter_to_value, "optimizer", "adamw"),
    (filter_to_range, "lr", 0.0001, 0.01),
    (filter_to_value, "scheduler", "cosine"),
])

# Apply to any dataframe
filtered = best_settings(df)
```

## Seed Aggregation Workflow

Aggregate metrics across random seeds:

```python
from dr_frames import aggregate_over_seeds, get_constant_cols

# Find which columns vary vs are constant
constants = get_constant_cols(df, skip=["seed", "run_id"])
config_cols = [c for c in df.columns if c not in constants and c != "seed"]

# Aggregate
agg = aggregate_over_seeds(
    df,
    config_cols=config_cols,
    metric_cols=["eval/loss", "eval/accuracy"],
    agg_funcs=["mean", "std", "min", "max"],
)
```

## Schema-Driven Analysis

Define data schema once, use everywhere:

```python
from dr_frames import ComputedField, DataField, DataFormat

class MyExperimentFormat(DataFormat):
    fields = [
        DataField(id_string="model_size", is_config=True),
        DataField(id_string="learning_rate", is_config=True),
        DataField(id_string="seed", is_config=False),
    ]

    computed_fields = [
        ComputedField(
            id_string="size_bucket",
            source_columns=["model_size"],
            compute=lambda df: pd.cut(
                df["model_size"],
                bins=[0, 100, 1000, float("inf")],
                labels=["small", "medium", "large"]
            ),
        ),
    ]

# Use schema
fmt = MyExperimentFormat.from_df(df)
config_cols = fmt.get_config_columns()
plot_df = fmt.prepare_for_plotting(df)
```

## Column Profiling for Unknown Data

Explore unfamiliar datasets:

```python
from dr_frames import DFColInfo, format_coverage_table

# Profile columns
info = DFColInfo()
info.update_from_df(df)

# Find columns by type
numeric_cols = info.names_with_tag("numeric")
config_cols = info.names_with_tag("config")
path_cols = info.names_with_tag("path")
nullable_cols = info.names_with_tag("nullable")

# Show coverage
print(format_coverage_table(df))
```

## Conditional Pipeline Steps

Apply transformations conditionally:

```python
from dr_frames import maybe_pipe, drop_all_null_cols, coerce_numeric_cols

result = (
    df
    # Only drop nulls if there are any
    .pipe(maybe_pipe, df.isna().any().any(), drop_all_null_cols)
    # Only coerce if column exists
    .pipe(maybe_pipe, "value" in df.columns, coerce_numeric_cols, ["value"])
    # Condition can be a callable
    .pipe(maybe_pipe, lambda x: len(x) > 100, lambda x: x.sample(100))
)
```

## Safe Column Operations

Work with columns that may or may not exist:

```python
from dr_frames import (
    apply_if_column,
    contained_cols,
    ensure_column,
    rename_columns,
)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Rename columns that exist (skip missing)
    df = rename_columns(df, {
        "old_name": "new_name",
        "might_not_exist": "normalized",
    })

    # Ensure required columns exist
    df = ensure_column(df, "status", default="unknown")

    # Transform only if column exists
    df = apply_if_column(df, "score", lambda s: s / 100)

    # Get subset of columns that exist
    keep = contained_cols(df, ["id", "name", "score", "status"])
    return df[keep]
```

## Best Metric Selection

Select best run per configuration:

```python
from dr_frames import filter_to_best_metric, select_subset

# Get best loss per model size
best_by_size = filter_to_best_metric(
    df,
    group_cols=["model_size"],
    metric_col="eval/loss",
    lower_is_better=True,
)

# Get best accuracy for specific config
subset = select_subset(df, {"optimizer": "adamw", "scheduler": "cosine"})
best = filter_to_best_metric(
    subset,
    group_cols=["model_size", "lr"],
    metric_col="eval/accuracy",
    lower_is_better=False,
)
```

## Parsing Nested Config Strings

Handle stringified lists from CSV exports:

```python
from dr_frames import is_homogeneous, parse_first_element, sum_list_elements

# Add computed columns from string lists
df["granularity"] = df["expert_sizes"].apply(parse_first_element)
df["total_experts"] = df["num_experts"].apply(sum_list_elements)
df["is_uniform"] = df["expert_sizes"].apply(is_homogeneous)

# Filter to uniform configurations only
uniform_df = df[df["is_uniform"]]
```
