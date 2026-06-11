"""
cells/timeseries.py — time series line plot cell.

Aggregates by X axis (mean of Y per X value) to reduce data size
while keeping the trend accurate.
"""


def timeseries_cell(x: str, y: str, color: str) -> str:
    color_enc = (
        f'alt.Color("{color}:N", legend=alt.Legend(title="{color}"))'
        if color != "None"
        else 'alt.value("steelblue")'
    )
    color_tooltip = f', alt.Tooltip("{color}:N")' if color != "None" else ""
    title = f"{y} over {x}" + (f" by {color}" if color != "None" else "")

    # Build groupby columns depending on whether color is set
    if color != "None":
        groupby_cols = f'["{x}", "{color}"]'
    else:
        groupby_cols = f'"{x}"'

    return f'''\
@app.cell
def __(mo):
    mo.md("## Time Series — `{y}` over `{x}`")
    return


@app.cell
def __(df, alt, pd):
    # Detect the correct Altair encoding type for the X axis
    if pd.api.types.is_datetime64_any_dtype(df["{x}"]):
        _x_type = "T"
    elif pd.api.types.is_numeric_dtype(df["{x}"]):
        _x_type = "Q"
    else:
        _x_type = "O"

    # Aggregate by X (and color if set) — mean of Y per group
    # This keeps the trend accurate while drastically reducing data size
    _df_plot = (
        df.groupby({groupby_cols})["{y}"]
        .mean()
        .reset_index()
        .sort_values("{x}")
    )

    _chart = alt.Chart(_df_plot).mark_line(point=True).encode(
        alt.X(f"{x}:{{_x_type}}", title="{x}"),
        alt.Y("{y}:Q", title="Mean {y}"),
        color={color_enc},
        tooltip=[
            alt.Tooltip(f"{x}:{{_x_type}}", title="{x}"),
            alt.Tooltip("{y}:Q", format=".2f", title="Mean {y}"){color_tooltip},
        ],
    ).interactive().properties(title="{title}", width=600)
    _chart
    return
'''
