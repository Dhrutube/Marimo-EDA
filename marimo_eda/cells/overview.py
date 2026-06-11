"""
cells/overview.py — always-included notebook cells.
Every generated notebook starts with these cells regardless of what user picked.
"""

import pathlib
 
 
def imports_cell() -> str:
    return '''\
@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import altair as alt
    return mo, pd, alt
'''
 
 
def loader_cell(csv_path: pathlib.Path) -> str:
    # Use the absolute path so the notebook works when opened anywhere
    safe_path = str(csv_path.resolve()).replace("\\", "/")  # for windows cross-compatibility
    return f'''\
@app.cell
def __(pd):
    df = pd.read_csv("{safe_path}")
    return (df,)
'''
 
 
def shape_cell(profile: dict) -> str:
    rows, cols = profile["shape"]
    dupes = profile["duplicates"]
    return f'''\
@app.cell
def __(mo):
    mo.md("# EDA Report")
    return
 
 
@app.cell
def __(mo):
    mo.md("## Dataset Overview")
    return
 
 
@app.cell
def __(mo):
    overview = mo.stat(label="Rows", value="{rows:,}"), mo.stat(label="Columns", value="{cols}"), mo.stat(label="Duplicate Rows", value="{dupes:,}")
    mo.hstack(overview)
    return (overview,)
'''
 
 
def dtypes_cell() -> str:
    return '''\
@app.cell
def __(df, mo):
    mo.md("## Column Types")
    return
 
 
@app.cell
def __(df, mo):
    dtypes_df = df.dtypes.reset_index()
    dtypes_df.columns = ["column", "dtype"]
    dtypes_df["dtype"] = dtypes_df["dtype"].astype(str)
    mo.ui.table(dtypes_df)
    return (dtypes_df,)
'''
 
 
def describe_cell() -> str:
    return '''\
@app.cell
def __(df, mo):
    mo.md("## Descriptive Statistics")
    return
 
 
@app.cell
def __(df, mo):
    desc = df.describe(include="all").reset_index()
    desc = desc.rename(columns={"index": "stat"})
    mo.ui.table(desc)
    return (desc,)
'''
 
 
def missing_summary_cell() -> str:
    return '''\
@app.cell
def __(df, mo):
    mo.md("## Missing Values Summary")
    return
 
 
@app.cell
def __(df, mo):
    missing = pd.DataFrame({
        "column": df.columns,
        "null_count": df.isnull().sum().values,
        "null_pct": (df.isnull().mean() * 100).round(1).values,
    })
    missing = missing[missing["null_count"] > 0].reset_index(drop=True)
    if missing.empty:
        mo.callout(mo.md("No missing values found in this dataset."), kind="success")
    else:
        mo.ui.table(missing)
    return (missing,)
'''
