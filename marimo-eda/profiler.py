import pathlib

import pandas as pd
from ydata_profiling import ProfileReport


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
    Load a CSV and return yprofile-data

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

    # Run ydata
    report = ProfileReport(df, minimal=True, progress_bar=False)
    description = report.get_description()
    ydata_vars = description.variables  # dict[col_name, dict of stats]

    # Build per-column summaries
    columns: dict[str, dict] = {}
    for col in df.columns:
        series = df[col]
        kind = _col_kind(series)
        yv = ydata_vars.get(col, {})

        entry: dict = {
            "dtype":      str(series.dtype),
            "kind":       kind,
            "non_null":   int(series.notna().sum()),
            "null_count": int(series.isna().sum()),
            "null_pct":   round(series.isna().mean() * 100, 1),
            "unique":     int(series.nunique(dropna=True)),
            # numeric fields — filled below if applicable
            "mean":       None,
            "std":        None,
            "min":        None,
            "p25":        None,
            "p50":        None,
            "p75":        None,
            "max":        None,
            # categorical fields — filled below if applicable
            "top_values": {},
        }

        if kind == "numeric":
            entry["mean"] = _safe_float(yv.get("mean"))
            entry["std"]  = _safe_float(yv.get("std"))
            entry["min"]  = _safe_float(yv.get("min"))
            entry["p25"]  = _safe_float(yv.get("p25"))
            entry["p50"]  = _safe_float(yv.get("p50"))
            entry["p75"]  = _safe_float(yv.get("p75"))
            entry["max"]  = _safe_float(yv.get("max"))

        if kind == "categorical":
            top = series.dropna().value_counts().head(10)
            entry["top_values"] = {str(k): int(v) for k, v in top.items()}

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