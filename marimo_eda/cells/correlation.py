"""
cells/correlation.py — correlation heatmap cell with value labels.
"""

from __future__ import annotations


def correlation_cell(method: str, columns: list[str]) -> str:
    cols_repr = repr(columns)
    return f'''\
@app.cell
def __(mo):
    mo.md("## Correlation Heatmap")
    return


@app.cell
def __(df, alt):
    _cols = {cols_repr}
    corr = df[_cols].corr(numeric_only=True, method="{method}").stack().reset_index()
    corr.columns = ["col1", "col2", "r"]

    _base = alt.Chart(corr)

    _heatmap = _base.mark_rect().encode(
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
            alt.Tooltip("r:Q", format=".3f", title="{method} r"),
        ],
    )

    _text = _base.mark_text(fontSize=11).encode(
        x=alt.X("col1:N"),
        y=alt.Y("col2:N"),
        text=alt.Text("r:Q", format=".2f"),
        color=alt.condition(
            "datum.r > 0.5 || datum.r < -0.5",
            alt.value("white"),
            alt.value("black"),
        ),
    )

    (_heatmap + _text).properties(
        title="{method.capitalize()} Correlation Matrix",
        width=400,
        height=400,
    )
    return (corr,)
'''
