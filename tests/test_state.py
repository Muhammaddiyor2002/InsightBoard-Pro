"""AppState integration tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import AppConfig
from app.database import Database
from app.state import AppState


def test_state_ingest_file(sample_csv: Path, tmp_path: Path) -> None:
    config = AppConfig(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        samples_dir=tmp_path / "data" / "samples",
        exports_dir=tmp_path / "exports",
        db_path=tmp_path / "data" / "test.sqlite",
    )
    config.ensure_dirs()
    db = Database(config.db_path)
    state = AppState(config=config, db=db)
    loaded, report = state.ingest_file(str(sample_csv))
    assert state.has_data()
    assert loaded.rows > 0
    assert report.rows_after > 0
    assert isinstance(state.df, pd.DataFrame)
    db.close()


def test_state_subscribe_fires(in_memory_db: Database, app_config: AppConfig) -> None:
    state = AppState(config=app_config, db=in_memory_db)
    flag = {"called": False}
    state.subscribe(lambda: flag.update(called=True))
    state.notify()
    assert flag["called"]
