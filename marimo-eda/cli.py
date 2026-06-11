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