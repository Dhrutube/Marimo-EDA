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
app = marimo.App(title="EDA — {title}", auto_download=True)

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

# Actual notebook builder
def build_notebook(
    csv_path: pathlib.Path,
    profile: dict,
    analyses: list[dict],
) -> str:
    """
    Assemble and return the full marimo notebook source as a string.

    Args:
        csv_path:  Path to the original CSV (embedded in the loader cell).
        profile:   The profile dict returned by profiler.profile_csv().
        analyses:  The list of analysis specs built by the CLI wizard.

    Returns:
        A string of valid Python that can be saved as a .py file and
        opened with `marimo edit`.
    """
    parts: list[str] = []

    # ── File header ────────────────────────────────────────────────────────
    parts.append(_FILE_HEADER.format(title=csv_path.name))

    # ── Fixed overview cells (always present) ──────────────────────────────
    parts.append(imports_cell())
    parts.append(loader_cell(csv_path=csv_path))
    parts.append(shape_cell(profile=profile))
    parts.append(dtypes_cell())
    parts.append(describe_cell())
    parts.append(missing_summary_cell())

    # ── User-selected analysis cells ───────────────────────────────────────
    for spec in analyses:
        parts.append(_render_cell(spec))

    # ── File footer ────────────────────────────────────────────────────────
    parts.append(_FILE_FOOTER)

    return "\n".join(parts)
