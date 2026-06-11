"""
cells/bivariate.py — two-column chart cells.

Supported chart types:
  Scatter Plot      — sampled, density patterns preserved
  Grouped Bar Chart — NOT sampled, aggregates on full df
  sampling because output is too large for marimo
"""

def bivariate_cell(x: str, y: str, color: str, chart: str) -> str:
    dispatch = {
        "Scatter Plot":      _scatter,
        "Grouped Bar Chart": _grouped_bar,
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
def __(df, alt, pd):
    _df_plot = df.sample(min(5000, len(df)), random_state=42) if len(df) > 5000 else df

    # Detect X axis type
    if pd.api.types.is_numeric_dtype(df["{x}"]):
        _x_enc = alt.X("{x}:Q", title="{x}")
    elif pd.api.types.is_datetime64_any_dtype(df["{x}"]):
        _x_enc = alt.X("{x}:T", title="{x}")
    else:
        _x_enc = alt.X("{x}:N", title="{x}")

    _chart = alt.Chart(_df_plot).mark_point(opacity=0.6).encode(
        _x_enc,
        alt.Y("{y}:Q", title="{y}"),
        color={color_enc},
        tooltip=[alt.Tooltip("{x}"), alt.Tooltip("{y}:Q"){color_tooltip}],
    ).interactive().properties(title="{title}", width=500)
    _chart
    return
'''


def _grouped_bar(x: str, y: str, color: str) -> str:
    color_enc = f'alt.Color("{color}:N", legend=alt.Legend(title="{color}"))' if color != "None" else 'alt.value("steelblue")'
    x_offset = f'xOffset="{color}:N",' if color != "None" else ""
    groupby_cols = f'["{x}", "{color}"]' if color != "None" else f'"{x}"'
    title = f"Mean {y} by {x}" + (f" grouped by {color}" if color != "None" else "")

    return f'''\
@app.cell
def __(mo):
    mo.md("## Grouped Bar Chart — `{y}` by `{x}`")
    return


@app.cell
def __(df, alt):
    _agg = df.groupby({groupby_cols})["{y}"].mean().reset_index()
    _agg = _agg.nlargest(50, "{y}")

    _chart = alt.Chart(_agg).mark_bar().encode(
        alt.X("{x}:N", sort="-y", title="{x}"),
        alt.Y("{y}:Q", title="Mean {y}"),
        {x_offset}
        color={color_enc},
        tooltip=[alt.Tooltip("{x}:N"), alt.Tooltip("{y}:Q", format=".2f", title="Mean {y}")],
    ).properties(title="{title} (top 50)", width=500)
    _chart
    return
'''


# Fallback

def _unknown(x: str, y: str, color: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.callout(mo.md("Unknown bivariate chart type for `{x}` vs `{y}` — skipped."), kind="warn")
    return
'''
