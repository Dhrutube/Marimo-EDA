"""
cells/bivariate.py — two-column chart cells.

Supported chart types:
  Scatter Plot
  Grouped Bar Chart
  Line Plot
"""

def bivariate_cell(x: str, y: str, color: str, chart: str) -> str:
    dispatch = {
        "Scatter Plot":      _scatter,
        "Grouped Bar Chart": _grouped_bar,
        "Line Plot":         _line_plot,
    }
    fn = dispatch.get(chart, _unknown)
    return fn(x, y, color)


# Chart templates

def _scatter(x: str, y: str, color: str) -> str:
    color_enc = f'alt.Color("{color}:N")' if color != "None" else 'alt.value("steelblue")'
    color_tooltip = f', alt.Tooltip("{color}:N")' if color != "None" else ""
    title = f"{x} vs {y}" + (f" by {color}" if color != "None" else "")

    return f'''\
@app.cell
def __(mo):
    mo.md("## Scatter Plot — `{x}` vs `{y}`")
    return


@app.cell
def __(df, alt):
    chart = alt.Chart(df).mark_point(opacity=0.6).encode(
        alt.X("{x}:Q", title="{x}"),
        alt.Y("{y}:Q", title="{y}"),
        color={color_enc},
        tooltip=[alt.Tooltip("{x}:Q"), alt.Tooltip("{y}:Q"){color_tooltip}],
    ).interactive().properties(title="{title}", width=500)
    chart
    return (chart,)
'''


def _grouped_bar(x: str, y: str, color: str) -> str:
    color_enc = f'alt.Color("{color}:N", legend=alt.Legend(title="{color}"))' if color != "None" else 'alt.value("steelblue")'
    x_offset = f'xOffset="{color}:N",' if color != "None" else ""
    title = f"{y} by {x}" + (f" grouped by {color}" if color != "None" else "")

    return f'''\
@app.cell
def __(mo):
    mo.md("## Grouped Bar Chart — `{y}` by `{x}`")
    return


@app.cell
def __(df, alt):
    chart = alt.Chart(df).mark_bar().encode(
        alt.X("{x}:N", title="{x}"),
        alt.Y("{y}:Q", title="{y}"),
        {x_offset}
        color={color_enc},
        tooltip=[alt.Tooltip("{x}:N"), alt.Tooltip("{y}:Q")],
    ).properties(title="{title}", width=500)
    chart
    return (chart,)
'''


def _line_plot(x: str, y: str, color: str) -> str:
    color_enc = f'alt.Color("{color}:N", legend=alt.Legend(title="{color}"))' if color != "None" else 'alt.value("steelblue")'
    color_tooltip = f', alt.Tooltip("{color}:N")' if color != "None" else ""
    title = f"{y} over {x}" + (f" by {color}" if color != "None" else "")
    x_type = "Q"  # bivariate line plots treat X as quantitative

    return f'''\
@app.cell
def __(mo):
    mo.md("## Line Plot — `{y}` over `{x}`")
    return


@app.cell
def __(df, alt):
    chart = alt.Chart(df).mark_line().encode(
        alt.X("{x}:{x_type}", title="{x}"),
        alt.Y("{y}:Q", title="{y}"),
        color={color_enc},
        tooltip=[alt.Tooltip("{x}:{x_type}"), alt.Tooltip("{y}:Q"){color_tooltip}],
    ).interactive().properties(title="{title}", width=500)
    chart
    return (chart,)
'''


# Fallback

def _unknown(x: str, y: str, color: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.callout(mo.md("Unknown bivariate chart type for `{x}` vs `{y}` — skipped."), kind="warn")
    return
'''