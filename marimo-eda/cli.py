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

def _prompt_correlation(df: pd.DataFrame) -> dict | None:
    """Prompt for correlation."""
    numeric_cols = df.select_dtypes("number").columns.tolist()
    if len(numeric_cols) < 2:
        questionary.print("Need at least 2 numeric columns for a correlation heatmap.", style="fg:yellow")
        return None

    method = questionary.select(
        "Correlation method:",
        choices=CORRELATION_METHODS,
    ).ask()
    if method is None:
        return None

    return {"type": "correlation", "method": method}

def _prompt_timeseries(df: pd.DataFrame) -> dict | None:
    """
    Prompt for a datetime X axis and one or more numeric Y columns.
    If no datetime columns exist, fall back to letting the user pick any column
    as X.
    """
    datetime_cols = df.select_dtypes("datetime").columns.tolist()
    numeric_cols = df.select_dtypes("number").columns.tolist()

    if not numeric_cols:
        questionary.print("No numeric columns available for a time series plot.", style="fg:yellow")
        return None

    # X axis — prefer datetime columns but allow any column
    if datetime_cols:
        x_choices = datetime_cols + questionary.Separator() + [c for c in df.columns if c not in datetime_cols]
    else:
        questionary.print(
            "No datetime columns detected. You can still pick any column as the time axis "
            "(e.g. a year, month, or sequence column).",
            style="fg:cyan",
        )
        x_choices = list(df.columns)

    x_col = questionary.select("Time (X) axis column:", choices=x_choices).ask()
    if x_col is None:
        return None

    y_col = questionary.select(
        "Value (Y) axis column (numeric):",
        choices=numeric_cols,
    ).ask()
    if y_col is None:
        return None

    # Optional color grouping
    cat_cols = [c for c in df.select_dtypes("object").columns if c != x_col]
    color_col = questionary.select(
        "Color / group by (optional):",
        choices=["None"] + cat_cols,
    ).ask()
    if color_col is None:
        return None

    return {
        "type": "timeseries",
        "x": x_col,
        "y": y_col,
        "color": color_col,
    }

def _prompt_run(df: pd.DataFrame) -> list[dict]:
    """
    Main loop. Returns a list of analysis spec dicts, e.g.:
      [
        {"type": "univariate", "chart": "Histogram", "column": "revenue"},
        {"type": "correlation", "method": "pearson"},
      ]
    """
    analyses: list[dict] = []

    while True:
        choice = questionary.select(
            "What would you like to add to your notebook?",
            choices=MAIN_MENU_CHOICES,
        ).ask()

        if choice is None or choice == "Done — generate notebook":
            break

        spec: dict | None = None

        if choice == "Univariate Analysis":
            spec = _prompt_univariate(df)
        elif choice == "Bivariate Analysis":
            spec = _prompt_bivariate(df)
        elif choice == "Time Series Analysis":
            spec = _prompt_timeseries(df)
        elif choice == "Missing Value Report":
            spec = {"type": "missing"}
        elif choice == "Correlation Heatmap":
            spec = _prompt_correlation(df)

        if spec is not None:
            analyses.append(spec)
        print()

    return analyses

def main() -> None:
    # Parse argument
    if len(sys.argv) < 2:
        print("Usage: marimo-eda <path-to-csv>")
        sys.exit(1)

    csv_path = pathlib.Path(sys.argv[1])

    if not csv_path.exists():
        print(f"Error: file not found — {csv_path}")
        sys.exit(1)

    if csv_path.suffix.lower() != ".csv":
        print(f"Error: expected a .csv file, got `{csv_path.suffix}`")
        sys.exit(1)

    # Load profile
    print(f"\nLoading {csv_path.name}...\n")
    try:
        profile = profile_csv(csv_path)
    except Exception as exc:
        print(f"Error reading CSV: {exc}")
        sys.exit(1)

    print_summary(profile)
    print()

    # Run Main Menu
    df: pd.DataFrame = profile["df"]

    analyses = _prompt_run(df)

    if not analyses:
        print("No analyses selected — nothing to write. Exiting.")
        sys.exit(0)

    print()
    output_path = '~/Downloads'

    # Build and export Marimo notebook
    output_path.parent.mkdir(parents=True, exist_ok=True)
    notebook_code = build_notebook(
        csv_path=csv_path,
        profile=profile,
        analyses=analyses,
    )
    output_path.write_text(notebook_code, encoding="utf-8")

    print(f"\nNotebook written to {output_path}")
    print("\nTo open your notebook run:")
    print(f"   marimo edit {output_path}\n")
    print("Dependencies needed in that environment:")
    print("   pip install marimo pandas altair ydata-profiling\n")