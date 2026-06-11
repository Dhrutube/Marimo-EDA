# Marimo-EDA

A command-line tool that profiles a CSV file and generates an interactive [marimo](https://marimo.io) notebook for exploratory data analysis (EDA). Users can choose the columns and types of visualizations from the command-line itself, requiring no coding knowledge.

## Usage

Install directly from GitHub using uv:

    uv add "git+https://github.com/Dhrutube/Marimo-EDA.git"

Run it against any CSV file:

    marimo-eda path/to/your/data.csv

The tool will:
1. Print a summary of your dataset — column types, missing values, and descriptive statistics
2. Prompt you interactively to choose analyses — univariate charts, bivariate plots, missing value reports, correlation heatmaps, and time series plots
3. Write a marimo notebook (.py) to a location you choose

Open the generated report:

    marimo run path/to/output.py

Types of analyses available:
Univariate  - Histogram, Box Plot, Strip Plot, Bar Chart (counts), Pie Chart
Bivariate   - Scatter Plot, Grouped Bar Chart
Time Series - Line Plot (aggregated by X axis)
Missing     - Bar chart of % missing per column
Correlation - Heatmap with value labels (pearson / spearman / kendall)

### Example session

    $ marimo-eda sales_data.csv

    Loading sales_data.csv...

    ✔ 12,483 rows × 4 columns   (0 duplicate rows)

    COLUMN          TYPE       KIND          NON-NULL   MISSING%   UNIQUE
    revenue         float64    numeric         12,201       2.3%    8,847
    region          object     categorical     12,483       0.0%        4
    age             int64      numeric         12,483       0.0%       61
    date            datetime   datetime        12,483       0.0%      365

    ? What would you like to add to your notebook?
    ❯ Univariate Analysis
      Bivariate Analysis
      Time Series Analysis
      Missing Value Report
      Correlation Heatmap
      ──────────────
      Done — generate notebook

    ? Select a column: revenue
    ? Chart type for `revenue`: Histogram

    ✔ Added: Histogram of `revenue`

    ? What would you like to add to your notebook?
    ❯ Done — generate notebook

    ? Output filename: sales_data_eda.py
    ? Output directory: /Users/you/Downloads

    Notebook written to /Users/you/Downloads/sales_data_eda.py

    To open your notebook, run:
       marimo edit /Users/you/Downloads/sales_data_eda.py

    To open your report (without any code cells visible), run:
       marimo run /Users/you/Downloads/sales_data_eda.py