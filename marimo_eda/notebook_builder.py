"""
notebook_builder.py — assembles a valid marimo .py notebook from an analyses list. Each analysis type delegates to a function in the cells/ package.
"""

import pathlib

from marimo_eda.cells.overview import (
    imports_cell,
    loader_cell,
    shape_cell,
    dtypes_cell,
    describe_cell,
    missing_summary_cell,
)
from marimo_eda.cells.univariate import univariate_cell
from marimo_eda.cells.bivariate import bivariate_cell
from marimo_eda.cells.missing import missing_heatmap_cell
from marimo_eda.cells.correlation import correlation_cell
from marimo_eda.cells.timeseries import timeseries_cell

# Marimo file wrapper

_FILE_HEADER = '''\
import marimo

__generated_with = "0.7.0"
app = marimo.App(title="EDA — {title}")

'''

_FILE_FOOTER = '''\

if __name__ == "__main__":
    app.run()
'''

# Cell builder

def _render_cell(spec: dict) -> str:
    """Route an analysis spec to the correct cell template function."""
    t = spec["type"]

    if t == "univariate":
        return univariate_cell(
            column=spec["column"],
            chart=spec["chart"],
        )
    if t == "bivariate":
        return bivariate_cell(
            x=spec["x"],
            y=spec["y"],
            color=spec["color"],
            chart=spec["chart"],
        )
    if t == "timeseries":
        return timeseries_cell(
            x=spec["x"],
            y=spec["y"],
            color=spec["color"],
        )
    if t == "missing":
        return missing_heatmap_cell()
    if t == "correlation":
        return correlation_cell(method=spec["method"])

    # Unknown spec type — emit a comment cell so the notebook still runs
    return f'''\
@app.cell
def __(mo):
    mo.md("> Unknown analysis type: `{t}` — skipped.")
'''
