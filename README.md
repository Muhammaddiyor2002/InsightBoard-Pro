# InsightBoard Pro

> Premium desktop & web data-analytics dashboard built with Python Flet, Pandas and Plotly.

InsightBoard Pro lets analysts drop in a CSV/Excel file and get a polished, interactive
business-intelligence experience in seconds — KPI cards, smart cleaning, ten chart types,
multi-column filters, pivot analytics, auto-insights, forecasting and exportable reports.

![Architecture](docs/architecture.svg)

---

## Highlights

- **Drag & drop ingest** — CSV, XLSX, XLS with automatic delimiter, encoding and dtype detection.
- **Smart cleaning** — one-click missing-value handling, duplicate removal, outlier flagging, date parsing.
- **Live dashboard** — eight KPI cards plus an Auto-Insights engine that flags trends, spikes and anomalies.
- **Ten interactive Plotly charts** — bar, line, pie, histogram, scatter, box, heatmap, area, correlation, time-series.
- **Advanced filtering** — date range, category, numeric range, full-text search, multi-column compose.
- **Pivot analytics** — group-by with sum / mean / median / count / min / max.
- **Reports & exports** — cleaned CSV, multi-sheet Excel, PDF dashboard snapshot, individual chart PNGs, plain-text summary.
- **Forecasting** — naive linear / seasonal-naive forecast for any time-series column.
- **Smart recommendations** — chart suggestions based on column profiles.
- **Saved templates** — dashboard layouts, filters and history persisted in SQLite.
- **Premium UI** — sidebar navigation, dark mode, smooth transitions, responsive layout.
- **Production-ready** — typed, modular, 85 %+ test coverage target, ruff + mypy clean.

---

## Quick start

```bash
git clone https://github.com/Muhammaddiyor2002/InsightBoard-Pro.git
cd InsightBoard-Pro

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m app.main                 # desktop window
# or
flet run app/main.py               # via Flet CLI
# or
flet run --web app/main.py         # browser
```

A fresh launch ships with a `data/samples/sample_sales.csv` you can load via **Upload Data → Load sample**.

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for OS-specific setup, [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for a screen-by-screen walkthrough, [`docs/BUILD.md`](docs/BUILD.md) for native binaries, and [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for common errors.

---

## Architecture

```
app/
├── main.py              # Flet entry point + DI wiring
├── config.py            # AppConfig (paths, limits, theme defaults)
├── ui/                  # theme, top-level layout, router
├── components/          # Sidebar, KPI card, chart card, data table, filter panel, …
├── pages/               # Home, Upload, Preview, Dashboard, Charts, Filters, Reports, Settings, History
├── charts/              # Plotly chart factories (10 chart types)
├── services/            # File loader, cleaner, exporter, insights, pivot, filters, AI query
├── analytics/           # stats, forecast, outliers, chart recommender
├── database/            # SQLite engine, models, repositories
├── utils/               # logger, validators, formatters, encoding helpers
└── assets/              # icons, fonts
```

Data flow:

```
File → FileLoader → DataFrame → DataCleaner → AppState (Pandas + DuckDB)
                                              │
              ┌───────────────────────────────┼──────────────────────────────┐
              ▼                               ▼                              ▼
         FilterPanel                    ChartFactory                   InsightsEngine
              │                               │                              │
              └────────────► Live UI re-render (Flet) ◄──────────────────────┘
```

---

## Development

```bash
pip install -r requirements-dev.txt

ruff check .                 # lint
ruff format --check .        # formatter
mypy app                     # types
pytest --cov=app --cov-report=term-missing
```

Continuous Integration runs `ruff`, `mypy`, `pytest` and a coverage gate on every push.

---

## Roadmap

- [ ] Real LLM-backed “Ask Your Data” natural-language queries
- [ ] Prophet / ARIMA forecasting backend
- [ ] Cloud sync of dashboard templates
- [ ] Per-user authentication for hosted web build

---

## License

MIT — see [`LICENSE`](LICENSE).
