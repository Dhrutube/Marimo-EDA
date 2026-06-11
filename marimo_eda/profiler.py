import pathlib

import pandas as pd

# Column kind detection and parsing

def _col_kind(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
        return "categorical"
    return "other"


def _try_parse_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Try to coerce object columns that look like dates into datetime.
    Only converts if the column name contains a date-like keyword
    AND pandas can parse it without errors.
    """
    date_keywords = {"date", "time", "dt", "timestamp", "year", "month", "day"}
    df = df.copy()
    for col in df.select_dtypes("object").columns:
        if any(kw in col.lower() for kw in date_keywords):
            try:
                converted = pd.to_datetime(df[col], infer_datetime_format=True)
                df[col] = converted
            except (ValueError, TypeError):
                pass
    return df

def profile_csv(path: pathlib.Path) -> dict:
    """
    Load a CSV and return pure Pandas

    Raises:
        ValueError: if the file is empty or has no columns.
        pd.errors.ParserError: if the file cannot be parsed as CSV.
    """
    # Load
    df = pd.read_csv(path)

    if df.empty:
        raise ValueError("The CSV file is empty.")
    if len(df.columns) == 0:
        raise ValueError("The CSV file has no columns.")

    # Try to detect datetime columns from object columns
    df = _try_parse_datetime(df)

    # Build per-column summaries
    columns: dict[str, dict] = {}
    for col in df.columns:
        series = df[col]
        kind = _col_kind(series)

        entry: dict = {
            "dtype":      str(series.dtype),
            "kind":       kind,
            "non_null":   int(series.notna().sum()),
            "null_count": int(series.isna().sum()),
            "null_pct":   round(series.isna().mean() * 100, 1),
            "unique":     int(series.nunique(dropna=True)),
            # numeric fields - filled below if applicable
            "mean":  _safe_float(series.mean()) if kind == "numeric" else None,
            "std":   _safe_float(series.std()) if kind == "numeric" else None,
            "min":   _safe_float(series.min()) if kind == "numeric" else None,
            "p25":   _safe_float(series.quantile(.25)) if kind == "numeric" else None,
            "p50":   _safe_float(series.quantile(.50)) if kind == "numeric" else None,
            "p75":   _safe_float(series.quantile(.75)) if kind == "numeric" else None,
            "max":   _safe_float(series.max()) if kind == "numeric" else None,
            # categorical fields - filled below if applicable
            "top_values": {str(k): int(v) for k, v in series.value_counts().head(10).items()} if kind == "categorical" else {},
        }
        columns[col] = entry

    numeric_cols     = [c for c, m in columns.items() if m["kind"] == "numeric"]
    categorical_cols = [c for c, m in columns.items() if m["kind"] == "categorical"]
    datetime_cols    = [c for c, m in columns.items() if m["kind"] == "datetime"]

    return {
        "df":               df,
        "shape":            df.shape,
        "duplicates":       int(df.duplicated().sum()),
        "columns":          columns,
        "numeric_cols":     numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols":    datetime_cols,
    }

def _safe_float(value: object) -> float | None:
    """Safety wrapper for converting ydata's stat values to floats, since DataFrame has 'object' type."""
    try:
        return round(float(value), 4)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    
# Print minimal summary in terminal

def print_summary(profile: dict) -> None:
    """
    Print a human-readable summary of the profile to stdout.
    """
    rows, cols = profile["shape"]
    dupes = profile["duplicates"]
    columns = profile["columns"]

    print(f"{rows:,} rows * {cols} columns   ({dupes:,} duplicate rows)\n")

    # Column summary table
    header = f"{'COLUMN':<30} {'TYPE':<12} {'KIND':<12} {'NON-NULL':>9} {'MISSING%':>9} {'UNIQUE':>8}"
    print(header)
    print("----" * len(header))

    for col, meta in columns.items():
        col_display = col if len(col) <= 28 else col[:27] + "..."
        print(
            f"{col_display:<30} "
            f"{meta['dtype']:<12} "
            f"{meta['kind']:<12} "
            f"{meta['non_null']:>9,} "
            f"{meta['null_pct']:>8.1f}% "
            f"{meta['unique']:>8,}"
        )

    # ── Numeric stats table ────────────────────────────────────────────────
    numeric_cols = profile["numeric_cols"]
    if numeric_cols:
        print("\nNUMERIC STATS")
        stat_keys = ["mean", "std", "min", "p25", "p50", "p75", "max"]
        col_w = 12

        # Header row
        print(f"{'':30}", end="")
        for col in numeric_cols:
            label = col if len(col) <= col_w - 1 else col[: col_w - 2] + "..."
            print(f"{label:>{col_w}}", end="")
        print()
        print("─" * (30 + col_w * len(numeric_cols)))

        for stat in stat_keys:
            print(f"{stat:<30}", end="")
            for col in numeric_cols:
                val = profile["columns"][col][stat]
                cell = f"{val:>{col_w}.2f}" if val is not None else f"{'-':>{col_w}}"
                print(cell, end="")
            print()

    # ── Datetime columns note ──────────────────────────────────────────────
    if profile["datetime_cols"]:
        print(f"\nDatetime columns detected: {', '.join(profile['datetime_cols'])}")
