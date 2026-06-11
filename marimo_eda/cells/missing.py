"""
cells/missing.py — missing values cell.
"""


def missing_heatmap_cell() -> str:
    return '''\
@app.cell
def __(mo):
    mo.md("## Missing Value Heatmap")
    return


@app.cell
def __(df, mo, alt):
    import pandas as pd
    missing = df.isnull().mean().mul(100).reset_index()
    missing.columns = ["column", "pct_missing"]
    missing = missing[missing["pct_missing"] > 0].sort_values("pct_missing", ascending=False)

    if missing.empty:
        mo.callout(mo.md("No missing values found in this dataset."), kind="success")
    else:
        chart = alt.Chart(missing).mark_bar().encode(
            x=alt.X("pct_missing:Q", title="% Missing"),
            y=alt.Y("column:N", sort="-x", title="Column"),
            color=alt.condition(
                alt.datum.pct_missing > 5,
                alt.value("crimson"),
                alt.value("steelblue"),
            ),
            tooltip=["column", alt.Tooltip("pct_missing:Q", format=".1f", title="% Missing")],
        ).properties(title="Missing Values by Column", width=500)
        chart
    return (missing,)
'''
