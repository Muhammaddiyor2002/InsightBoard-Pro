"""Generate the bundled sample_sales.csv for first-run users.

Run via ``python data/samples/generate_sample.py`` from the project root.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd


def main(out_path: Path | None = None) -> Path:
    out = out_path or Path(__file__).parent / "sample_sales.csv"
    rng = np.random.default_rng(2026)
    n = 1500
    start = dt.datetime(2024, 1, 1)
    df = pd.DataFrame(
        {
            "order_date": [start + dt.timedelta(days=int(rng.integers(0, 720))) for _ in range(n)],
            "category": rng.choice(
                ["Books", "Electronics", "Clothing", "Toys", "Home", "Beauty"], size=n
            ),
            "region": rng.choice(["North", "South", "East", "West"], size=n),
            "channel": rng.choice(["Online", "Store", "Wholesale"], size=n, p=[0.6, 0.3, 0.1]),
            "units": rng.integers(1, 25, size=n),
            "unit_price": rng.uniform(8, 350, size=n).round(2),
        }
    )
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    df["cost"] = (df["revenue"] * rng.uniform(0.45, 0.75, size=n)).round(2)
    df["profit"] = (df["revenue"] - df["cost"]).round(2)
    df = df.sort_values("order_date").reset_index(drop=True)
    df.to_csv(out, index=False)
    return out


if __name__ == "__main__":
    p = main()
    print(f"sample written -> {p}")
