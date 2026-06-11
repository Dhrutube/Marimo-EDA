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
def __(df, mo, pd):
    _missing = pd.DataFrame({
    "column": df.columns,
    "null_count": df.isnull().sum().values,
    "null_pct": (df.isnull().mean() * 100).round(1).values,
    })
    _missing = _missing[_missing["null_count"] > 0].reset_index(drop=True)

    mo.stop(_missing.empty, mo.callout(mo.md("✅ No missing values found in this dataset."), kind="success"))
    _missing
'''
