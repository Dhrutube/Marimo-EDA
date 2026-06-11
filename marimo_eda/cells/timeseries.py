"""
cells/timeseries.py — time series line plot cell.

Handles both proper datetime columns and ordinal/numeric
time axes (e.g. year, month, sequence number).
"""

def timeseries_cell(x: str, y: str, color: str) -> str:
    color_enc = (
        f'alt.Color("{color}:N", legend=alt.Legend(title="{color}"))'
        if color != "None"
        else 'alt.value("steelblue")'
    )
    color_tooltip = f', alt.Tooltip("{color}:N")' if color != "None" else ""
    title = f"{y} over {x}" + (f" by {color}" if color != "None" else "")

    return f'''\

@app.cell
def __(mo):
    mo.md("## Time Series — `{y}` over `{x}`")
    return


@app.cell
def __(df, alt):
    import pandas as pd

    # Detect the correct Altair encoding type for the X axis
    _x_series = df["{x}"]
    if pd.api.types.is_datetime64_any_dtype(_x_series):
        _x_type = "T"   # temporal
    elif pd.api.types.is_numeric_dtype(_x_series):
        _x_type = "Q"   # quantitative
    else:
        _x_type = "O"   # ordinal (e.g. month names, quarters)

    chart = alt.Chart(df).mark_line(point=True).encode(
        alt.X(f"{x}:{{_x_type}}", title="{x}"),
        alt.Y("{y}:Q", title="{y}"),
        color={color_enc},
        tooltip=[
            alt.Tooltip(f"{x}:{{_x_type}}", title="{x}"),
            alt.Tooltip("{y}:Q", title="{y}"){color_tooltip},
        ],
    ).interactive().properties(title="{title}", width=600)
    chart
    return (chart,)
'''