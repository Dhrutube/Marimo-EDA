import sys
import pathlib

import questionary
import pandas as pd

from marimo_eda.profiler import profile_csv, print_summary
from marimo_eda.notebook_builder import build_notebook

MAIN_MENU_CHOICES = [
    "Univariate Analysis",
    "Bivariate Analysis",
    "Time Series Analysis",
    "Missing Value Report",
    "Correlation Heatmap",
    questionary.Separator(),
    "Done — generate notebook",
]

UNIVARIATE_NUMERIC_CHARTS = ["Histogram", "Box Plot", "Strip Plot", "Line Plot (over index)"]
UNIVARIATE_CATEGORICAL_CHARTS = ["Bar Chart (counts)", "Pie Chart"]
BIVARIATE_CHARTS = ["Scatter Plot", "Grouped Bar Chart", "Line Plot"]
CORRELATION_METHODS = ["pearson", "spearman", "kendall"]

def _is_numeric(df: pd.DataFrame, col: str) -> bool:
    return pd.api.types.is_numeric_dtype(df[col])

def _pick_column(df: pd.DataFrame, label: str = "Select a column:") -> str | None:
    return questionary.select(
        label,
        choices=list(df.columns),
    ).ask()

def _prompt_univariate(df: pd.DataFrame) -> dict | None:
    """Prompt for a column and chart type."""
    col = _pick_column(df)
    if col is None:
        return None

    if _is_numeric(df, col):
        chart_choices = UNIVARIATE_NUMERIC_CHARTS
    else:
        chart_choices = UNIVARIATE_CATEGORICAL_CHARTS

    chart = questionary.select(
        f"Chart type for `{col}`:",
        choices=chart_choices,
    ).ask()
    if chart is None:
        return None

    return {
        "type": "univariate", 
        "chart": chart, 
        "column": col
    }


def _prompt_bivariate(df: pd.DataFrame) -> dict | None:
    """Prompt for X, Y, and optional color column."""
    numeric_cols = df.select_dtypes("number").columns.tolist()
    cat_cols = df.select_dtypes("object").columns.tolist()

    if len(numeric_cols) < 1:
        questionary.print("No numeric columns available for bivariate analysis.", style="fg:yellow")
        return None

    x_col = _pick_column(df, "X axis column:")
    if x_col is None:
        return None

    y_col = questionary.select(
        "Y axis column (numeric):",
        choices=numeric_cols,
    ).ask()
    if y_col is None:
        return None

    color_col = questionary.select(
        "Color by (optional):",
        choices=["None"] + cat_cols,
    ).ask()
    if color_col is None:
        return None

    chart = questionary.select(
        "Chart type:",
        choices=BIVARIATE_CHARTS,
    ).ask()
    if chart is None:
        return None

    return {
        "type": "bivariate",
        "chart": chart,
        "x": x_col,
        "y": y_col,
        "color": color_col,
    }