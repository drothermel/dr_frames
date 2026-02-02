# schema

Data field definitions with metadata for display and type inference.

## Classes

### DataField
```python
class DataField(BaseModel):
    id_string: str                              # Unique identifier
    description: str | None = None              # Human-readable description
    column_name: str | None = None              # Actual column in DataFrame
    display_name: str | None = None             # Display label (auto-derived if None)
    altair_type: Literal["Q", "N", "O", "T"] | None = None  # Vega-Altair type hint
    scale_hint: Literal["linear", "log"] | None = None      # Scale suggestion
    is_config: bool = True                      # Whether field defines unique config
```

**Properties:**
- `is_resolved: bool` - True if column_name is set

**Methods:**
- `resolve_column(df) -> str` - Returns column_name or id_string if in df
- `infer_altair_type(df) -> str` - Infer Q/N/O/T from dtype

### ComputedField
```python
class ComputedField(DataField):
    source_columns: list[str] = []              # Columns used in computation
    compute: Callable[[pd.DataFrame], pd.Series]  # Computation function
```

**Methods:**
- `apply(df) -> pd.Series` - Run the compute function

### MetricDataField
```python
class MetricDataField(DataField):
    group: str = ""                             # Metric group (e.g., "lm")
    metric_type: str = ""                       # Metric type (e.g., "CE loss")
```

**Class Methods:**
- `from_column_name(col) -> MetricDataField` - Parse `eval/lm/dataset/metric` format

### DataFormat
```python
class DataFormat(BaseModel):
    fields: list[DataField] = []
    computed_fields: list[ComputedField] = []
    metrics: list[MetricDataField] = []
    column_overrides: dict[str, str] = {}
```

**Class Methods:**
- `from_dict(field_descriptions, df, column_overrides=None)` - Build from description dict
- `from_df(df, field_descriptions=None, computed_fields=None, column_overrides=None, metric_prefix="eval/")` - Build with auto-discovered metrics

**Properties:**
- `unresolved_fields: list[DataField]` - Fields without column_name
- `is_fully_resolved: bool` - All fields have column_name

**Methods:**
- `prepare_for_plotting(df, drop_unknown=True) -> pd.DataFrame` - Apply computed fields
- `get_metric(pattern) -> MetricDataField | None` - Find metric by substring
- `metric_col(pattern) -> str` - Get metric column name (asserts if not found)
- `get_metrics(df) -> list[str]` - Auto-discover metric columns
- `get_config_columns(use_computed=True) -> list[str]` - Get config-defining columns

## Usage

```python
import pandas as pd
from dr_frames import ComputedField, DataField, DataFormat

df = pd.DataFrame({
    "model_size": ["10M", "20M", "50M"],
    "learning_rate": [0.01, 0.01, 0.001],
    "eval/loss": [0.5, 0.4, 0.3],
})

# Define schema
fmt = DataFormat(
    fields=[
        DataField(id_string="model_size", description="Model parameter count"),
        DataField(id_string="learning_rate", description="Training LR"),
    ],
    computed_fields=[
        ComputedField(
            id_string="size_order",
            source_columns=["model_size"],
            compute=lambda df: df["model_size"].map(
                {"10M": 1, "20M": 2, "50M": 3}
            ),
            is_config=False,
        ),
    ],
)

# Or build from DataFrame
fmt = DataFormat.from_df(df, metric_prefix="eval/")

# Prepare for plotting
plot_df = fmt.prepare_for_plotting(df)

# Find metric
loss_col = fmt.metric_col("loss")  # "eval/loss"
```
