# Installation

InsightBoard Pro runs on Python 3.11+ and ships with everything needed for local development. Native binaries can be produced with `flet build` (see [`BUILD.md`](BUILD.md)).

## 1 — Get the source

```bash
git clone https://github.com/Muhammaddiyor2002/InsightBoard-Pro.git
cd InsightBoard-Pro
```

## 2 — Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

## 3 — Install dependencies

For end users:

```bash
pip install -r requirements.txt
```

For contributors (adds pytest, ruff, mypy):

```bash
pip install -r requirements-dev.txt
```

## 4 — Generate the bundled sample (optional)

The repository already contains `data/samples/sample_sales.csv`; if you remove it you can regenerate it with:

```bash
python data/samples/generate_sample.py
```

## 5 — Run the app

```bash
python -m app.main             # opens a desktop window
flet run app/main.py           # via Flet CLI
flet run --web app/main.py     # browser at http://localhost:8550
```

## Platform notes

### Linux

The Flet runtime depends on GTK/WebKit. On Ubuntu/Debian:

```bash
sudo apt-get install -y libwebkit2gtk-4.1-0 libgtk-3-0 libmpv2 libgl1
```

Headless / CI environments should use the `--web` runner instead, since no X server is available.

### macOS

No extra dependencies. Use `python3 -m app.main` or `flet run app/main.py`.

### Windows

Install [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) if it's not already on the machine.

## Troubleshooting

See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
