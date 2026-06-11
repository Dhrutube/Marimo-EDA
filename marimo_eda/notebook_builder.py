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
