import pathlib

import pandas as pd
from ydata_profiling import ProfileReport


# ── Column kind detection ─────────────────────────────────────────────────────

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