"""
cells/missing.py — missing values cell.
"""


def missing_summary_cell() -> str:
    return '''\
@app.cell
def __(mo):
    mo.md("## Missing Value Summary")
    return


@app.cell
def __(df, mo):
    _missing = pd.DataFrame({
        "column": df.columns,
        "null_count": df.isnull().sum().values,
        "null_pct": (df.isnull().mean() * 100).round(1).values,
    })
    _missing_filtered = _missing[_missing["null_count"] > 0].reset_index(drop=True)
    if _missing_filtered.empty:
        mo.callout(mo.md("✅ No missing values found in this dataset."), kind="success")
    else:
        mo.vstack([
            mo.md(f"**{len(_missing_filtered)} column(s) have missing values:**"),
            _missing_filtered,
        ])
    return
'''
