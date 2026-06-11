"""
cells/correlation.py — correlation heatmap cell.
"""

def correlation_cell(method: str) -> str:
    return f'''\
@app.cell
def __(mo):
    mo.md("## Correlation Heatmap")
    return


@app.cell
def __(df, mo, alt):
    corr = df.corr(numeric_only=True, method="{method}").stack().reset_index()
    corr.columns = ["col1", "col2", "r"]

    chart = alt.Chart(corr).mark_rect().encode(
        x=alt.X("col1:N", title=None),
        y=alt.Y("col2:N", title=None),
        color=alt.Color(
            "r:Q",
            scale=alt.Scale(scheme="redblue", domain=[-1, 1]),
            title="r",
        ),
        tooltip=[
            alt.Tooltip("col1:N", title="Column A"),
            alt.Tooltip("col2:N", title="Column B"),
            alt.Tooltip("r:Q", format=".3f", title="{method.capitalize()} r"),
        ],
    ).properties(
        title="{method.capitalize()} Correlation Matrix",
        width=400,
        height=400,
    )
    chart
    return (corr,)
'''