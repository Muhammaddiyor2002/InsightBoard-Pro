"""Shared pytest fixtures."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.config import AppConfig
from app.database import Database


@pytest.fixture
def sample_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 200
    start = dt.datetime(2024, 1, 1)
    df = pd.DataFrame(
        {
            "date": [start + dt.timedelta(days=i) for i in range(n)],
            "category": rng.choice(["Books", "Electronics", "Clothing", "Toys"], size=n),
            "region": rng.choice(["North", "South", "East", "West"], size=n),
            "units": rng.integers(1, 50, size=n),
            "price": rng.uniform(10, 250, size=n).round(2),
        }
    )
    df["revenue"] = (df["units"] * df["price"]).round(2)
    # Sprinkle a few NaNs
    df.loc[df.sample(8, random_state=1).index, "price"] = np.nan
    df.loc[df.sample(5, random_state=2).index, "category"] = np.nan
    return df


@pytest.fixture
def sample_csv(tmp_path: Path, sample_df: pd.DataFrame) -> Path:
    p = tmp_path / "sample.csv"
    sample_df.to_csv(p, index=False)
    return p


@pytest.fixture
def sample_xlsx(tmp_path: Path, sample_df: pd.DataFrame) -> Path:
    p = tmp_path / "sample.xlsx"
    sample_df.to_excel(p, index=False)
    return p


@pytest.fixture
def in_memory_db() -> Database:
    db = Database(":memory:")
    yield db
    db.close()


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        samples_dir=tmp_path / "data" / "samples",
        exports_dir=tmp_path / "exports",
        db_path=tmp_path / "data" / "test.sqlite",
    )
