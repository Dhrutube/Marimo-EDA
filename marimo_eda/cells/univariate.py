"""
cells/univariate.py — single-column chart cells.

Supported chart types:
  Histogram              (numeric)
  Box Plot               (numeric)
  Strip Plot             (numeric)
  Line Plot (over index) (numeric)
  Bar Chart (counts)     (categorical)
  Pie Chart              (categorical)
"""

def univariate_cell(column: str, chart: str) -> str:
    dispatch = {
        "Histogram":              _histogram,
        "Box Plot":               _box_plot,
        "Strip Plot":             _strip_plot,
        "Line Plot (over index)": _line_plot_index,
        "Bar Chart (counts)":     _bar_chart,
        "Pie Chart":              _pie_chart,
    }
    fn = dispatch.get(chart, _unknown)
    return fn(column)


# Numeric charts

def _histogram(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Histogram — `{column}`")
    return


@app.cell
def __(mo):
    bin_count_{_safe(column)} = mo.ui.slider(5, 100, value=30, label="Bin count")
    bin_count_{_safe(column)}
    return (bin_count_{_safe(column)},)


@app.cell
def __(df, alt, bin_count_{_safe(column)}):
    chart = alt.Chart(df).mark_bar().encode(
        alt.X("{column}:Q", bin=alt.Bin(maxbins=bin_count_{_safe(column)}.value), title="{column}"),
        alt.Y("count()", title="Count"),
        tooltip=[alt.Tooltip("{column}:Q"), alt.Tooltip("count()", title="Count")],
    ).properties(title="Histogram of {column}", width=500)
    chart
    return (chart,)
'''


def _box_plot(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Box Plot — `{column}`")
    return


@app.cell
def __(df, alt):
    chart = alt.Chart(df).mark_boxplot(extent="min-max").encode(
        alt.Y("{column}:Q", title="{column}"),
        tooltip=[alt.Tooltip("{column}:Q")],
    ).properties(title="Box Plot of {column}", width=200)
    chart
    return (chart,)
'''


def _strip_plot(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Strip Plot — `{column}`")
    return


@app.cell
def __(df, alt):
    chart = alt.Chart(df).mark_tick().encode(
        alt.X("{column}:Q", title="{column}"),
        tooltip=[alt.Tooltip("{column}:Q")],
    ).properties(title="Strip Plot of {column}", width=500)
    chart
    return (chart,)
'''


def _line_plot_index(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Line Plot — `{column}` over index")
    return


@app.cell
def __(df, alt):
    _df = df[["{column}"]].reset_index().rename(columns={{"index": "row"}})
    chart = alt.Chart(_df).mark_line().encode(
        alt.X("row:Q", title="Row index"),
        alt.Y("{column}:Q", title="{column}"),
        tooltip=[alt.Tooltip("row:Q", title="Index"), alt.Tooltip("{column}:Q")],
    ).properties(title="{column} over row index", width=500)
    chart
    return (chart,)
'''


# Categorical charts

def _bar_chart(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Bar Chart — `{column}`")
    return


@app.cell
def __(df, alt):
    counts = df["{column}"].value_counts().reset_index()
    counts.columns = ["{column}", "count"]
    chart = alt.Chart(counts).mark_bar().encode(
        alt.X("{column}:N", sort="-y", title="{column}"),
        alt.Y("count:Q", title="Count"),
        tooltip=[alt.Tooltip("{column}:N"), alt.Tooltip("count:Q", title="Count")],
    ).properties(title="Value Counts: {column}", width=500)
    chart
    return (chart,)
'''


def _pie_chart(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Pie Chart — `{column}`")
    return


@app.cell
def __(df, alt):
    counts = df["{column}"].value_counts().reset_index()
    counts.columns = ["{column}", "count"]
    chart = alt.Chart(counts).mark_arc().encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color("{column}:N", legend=alt.Legend(title="{column}")),
        tooltip=[alt.Tooltip("{column}:N"), alt.Tooltip("count:Q", title="Count")],
    ).properties(title="Pie Chart: {column}", width=350, height=350)
    chart
    return (chart,)
'''


# Fallback

def _unknown(column: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.callout(mo.md("Unknown chart type for column `{column}` — skipped."), kind="warn")
    return
'''


# Python variable name safe-checker

def _safe(name: str) -> str:
    """Convert a column name to a safe Python identifier for variable names."""
    return name.replace(" ", "_").replace("-", "_").replace(".", "_").lower()
