# Building executables

InsightBoard Pro can be packaged as a native desktop binary on Windows, macOS and Linux, plus published as a static web bundle. All three share the same `app/main.py` entry point.

## Prerequisites

- Python 3.11+
- The `requirements.txt` dependencies installed.
- Flet CLI (`pip install flet` already covers it).
- For Windows installers: [`Inno Setup`](https://jrsoftware.org/isinfo.php) or Flet's built-in MSIX option.
- For macOS notarisation: an Apple Developer ID (optional).

## Quick reference

```bash
# Desktop binary for the current OS
flet build app/main.py --name InsightBoardPro

# Windows installer
flet build app/main.py --build-version 1.0.0 --product "InsightBoard Pro" --target windows

# macOS app bundle
flet build app/main.py --target macos --copyright "© 2026 Cognition Labs"

# Linux AppImage
flet build app/main.py --target linux

# Static web bundle
flet publish app/main.py
# Output: ./dist (drop into S3 / GitHub Pages / Netlify)
```

## Configuration tips

- **Icon** — drop `app/assets/icon.png` (1024×1024). Flet picks it up automatically.
- **Splash** — provide `app/assets/splash.png` if you want a launch image.
- **Per-target excludes** — see `[tool.flet]` in `pyproject.toml` (extend as needed).
- **Bundling samples** — copy `data/samples/sample_sales.csv` next to the binary so first-run users can hit *Load bundled sample*.

## CI / CD

The `.github/workflows/ci.yml` workflow runs `ruff`, `mypy` and `pytest` on every push. To add release builds, fork it and add a job that runs `flet build` on the relevant runner OS, then uploads the artefact via `actions/upload-artifact`.

## Manual smoke test

After producing a binary:

1. Launch the binary on a clean machine (no Python installed).
2. Click **Upload Data → Load bundled sample**.
3. Verify the Dashboard, Charts and Reports pages render with no console errors.
4. Export a PDF and confirm it opens in your viewer.
