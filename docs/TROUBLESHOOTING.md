# Troubleshooting

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `ModuleNotFoundError: flet` | Virtual env not activated, or deps not installed | `source .venv/bin/activate && pip install -r requirements.txt` |
| App opens but charts are blank PNGs | Kaleido binary not bundled in your environment | `pip install --upgrade kaleido==0.2.1` |
| `libwebkit2gtk-4.1.so.0: cannot open shared object file` (Linux) | Missing GTK / WebKit dependencies | `sudo apt-get install libwebkit2gtk-4.1-0 libgtk-3-0 libmpv2 libgl1` |
| `OSError: [Errno 24] Too many open files` | Pandas + DuckDB holding many descriptors | Restart the app or `ulimit -n 8192` |
| `UnicodeDecodeError` while reading CSV | Auto-detected encoding wrong for your file | Re-save as UTF-8, or set `INSIGHTBOARD_DEFAULT_ENCODING` (planned setting) |
| Large file ingest is slow | Fall back to DuckDB streaming | Set `INSIGHTBOARD_USE_DUCKDB=1` and re-run |
| PDF export is empty | ReportLab couldn't render data | Ensure dataframe has rows; check the log for `reportlab` warnings |
| App crashes on startup with a segfault | Conflicting older Flet binary | `pip install --force-reinstall "flet>=0.24"` |
| Tests fail with `AttributeError: module 'plotly' has no attribute …` | Plotly older than 5.20 | `pip install --upgrade plotly` |

## Logs

Logs are streamed to `stderr` under the `insightboard.*` namespace. To save to a file:

```bash
python -m app.main 2> insightboard.log
```

Forward the log along with steps-to-reproduce when filing an issue.

## Reset

Worst-case, wipe the SQLite cache and exports:

```bash
rm data/insightboard.sqlite
rm -rf exports/*
```

The next launch recreates the schema.
