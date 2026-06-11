"""
cells/missing.py — missing values cell.
"""


def missing_heatmap_cell() -> str:
    return '''\
@app.cell
def __(mo):
    mo.md("## Missing Values")
    return


@app.cell
def __(df, alt, mo, pd):
    _missing = pd.DataFrame({
        "column": df.columns,
        "null_count": df.isnull().sum().values,
        "null_pct": (df.isnull().mean() * 100).round(1).values,
    })
    _missing = _missing[_missing["null_count"] > 0].sort_values("null_pct", ascending=False).reset_index(drop=True)

    mo.stop(_missing.empty, mo.callout(mo.md("No missing values found in this dataset."), kind="success"))

    _chart = alt.Chart(_missing).mark_bar().encode(
        x=alt.X("null_pct:Q", title="% Missing"),
        y=alt.Y("column:N", sort="-x", title="Column"),
        color=alt.condition(
            alt.datum.null_pct > 5,
            alt.value("crimson"),
            alt.value("steelblue"),
        ),
        tooltip=["column", alt.Tooltip("null_pct:Q", format=".1f", title="% Missing")],
    ).properties(title="Missing Values by Column", width=500)
    _chart
'''
