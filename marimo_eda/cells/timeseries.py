"""
cells/timeseries.py — time series line plot cell.

NOT sampled — full sequence needed for accurate trends.
Sorts by X axis and drops nulls before plotting.
Handles datetime, numeric, and ordinal time axes.
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
def __(df, alt, pd):
    # Detect the correct Altair encoding type for the X axis
    if pd.api.types.is_datetime64_any_dtype(df["{x}"]):
        _x_type = "T"   # temporal
    elif pd.api.types.is_numeric_dtype(df["{x}"]):
        _x_type = "Q"   # quantitative
    else:
        _x_type = "O"   # ordinal (e.g. month names, quarters)
 
    # Sort by X and drop nulls — full dataset, no sampling
    _df_plot = df[["{x}", "{y}"]].dropna().sort_values("{x}")
 
    _chart = alt.Chart(_df_plot).mark_line(point=True).encode(
        alt.X(f"{x}:{{_x_type}}", title="{x}"),
        alt.Y("{y}:Q", title="{y}"),
        color={color_enc},
        tooltip=[
            alt.Tooltip(f"{x}:{{_x_type}}", title="{x}"),
            alt.Tooltip("{y}:Q", title="{y}"){color_tooltip},
        ],
    ).interactive().properties(title="{title}", width=600)
    _chart
    return
'''
