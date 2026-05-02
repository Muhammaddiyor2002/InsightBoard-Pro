# User Guide

This walkthrough mirrors the order of items in the sidebar.

## Home

A landing page with quick links to the four most-used screens — Upload, Dashboard, Charts and Reports.

## Upload Data

- Drag a CSV / Excel file onto the dotted card or click **Browse files**.
- Click **Load bundled sample** to immediately try the app with `data/samples/sample_sales.csv` (1 500 synthetic sales rows).
- The bottom of the page shows the most-recent upload's rows × columns and the cleaning summary.

Supported formats: `.csv`, `.tsv`, `.xlsx`, `.xls`. Default size cap is 250 MB; configurable via `INSIGHTBOARD_MAX_FILE_MB`.

## Data Preview

Two tabs:

- **Sample rows** — paginated DataTable of the first 5 000 cleaned rows.
- **Column profile** — per-column dtype, non-null count, null %, unique values, sample value.

## Dashboard

- Eight KPI cards (rows, columns, missing values, duplicate rows, numeric / categorical / date column counts, last update).
- Auto-Insights panel — ranked observations covering trends, top categories, statistical extremes and IQR-based anomalies.

## Charts

Pick a chart type and X / Y columns; the chart re-renders live. Ten chart types are supported:

| Chart | Best for |
| --- | --- |
| Bar | Comparing a metric across categorical values |
| Line | Continuous changes |
| Pie | Share-of-total when cardinality ≤ 6 |
| Histogram | Distribution of a numeric column |
| Scatter | Relationship between two numeric columns |
| Box | Outliers, spread |
| Heatmap | Pairwise correlations |
| Area | Cumulative volume over time |
| Correlation | Quick numeric correlation matrix |
| Time-series | Seasonal / trend behaviour with auto-resample |

A toolbar above each chart lets you export a static PNG to the `exports/` folder.

## Filters

A multi-column panel with:

- Free-text search (across object columns)
- Up to five categorical dropdowns
- Up to four numeric range inputs
- Date range picker

The dataframe shown on the right and the dataframe used by other pages re-render as you change filters.

## Reports

Four export tiles:

- **Cleaned CSV** — current (filtered) dataframe.
- **Excel report** — multi-sheet workbook (`data`, `kpis`).
- **PDF dashboard** — KPIs + auto-insights + first 10 rows.
- **Text summary** — plain-text overview for chat / docs.

A *Recent exports* list shows the last 10 artefacts generated this session.

## History

A read-only audit log of:

- Uploaded files
- Saved filters
- Dashboard templates
- Recent exports

Backed by SQLite at `data/insightboard.sqlite`.

## Settings

Toggle dark / light mode, view configuration paths and limits, inspect feature toggles. Most settings can also be overridden via environment variables — see `app/config.py`.
