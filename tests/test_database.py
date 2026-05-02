"""Database / repositories tests."""

from __future__ import annotations

from app.database import Database
from app.database.models import (
    DashboardTemplate,  # noqa: F401  (imported for side-effects in __init__)
    ReportHistory,
    UploadedFile,
)
from app.database.repositories import (
    DashboardTemplateRepo,
    ExportLogRepo,
    ReportHistoryRepo,
    SavedFilterRepo,
    SettingsRepo,
    UploadedFileRepo,
)


def test_uploaded_file_crud(in_memory_db: Database) -> None:
    repo = UploadedFileRepo(in_memory_db)
    uid = repo.add(
        UploadedFile(
            id=None,
            filename="x.csv",
            path="/tmp/x.csv",
            size_bytes=10,
            rows=5,
            cols=2,
            delimiter=",",
            encoding="utf-8",
        )
    )
    assert uid > 0
    rows = repo.list()
    assert len(rows) == 1 and rows[0].filename == "x.csv"
    assert repo.get(uid) is not None
    repo.delete(uid)
    assert repo.list() == []


def test_report_history(in_memory_db: Database) -> None:
    repo = ReportHistoryRepo(in_memory_db)
    rid = repo.add(ReportHistory(id=None, file_id=None, title="a", kind="csv", path="x"))
    assert rid > 0
    assert len(repo.list()) == 1


def test_saved_filters_upsert(in_memory_db: Database) -> None:
    repo = SavedFilterRepo(in_memory_db)
    fid = repo.upsert("by_region", {"region": "North"})
    assert fid > 0
    payload = repo.get("by_region")
    assert payload == {"region": "North"}
    repo.upsert("by_region", {"region": "South"})
    assert repo.get("by_region") == {"region": "South"}
    assert len(repo.list()) == 1


def test_dashboard_templates(in_memory_db: Database) -> None:
    repo = DashboardTemplateRepo(in_memory_db)
    repo.upsert("default", {"layout": [1, 2]})
    assert len(repo.list()) == 1


def test_settings(in_memory_db: Database) -> None:
    repo = SettingsRepo(in_memory_db)
    repo.set("theme", "dark")
    assert repo.get("theme") == "dark"
    repo.set("theme", "light")
    assert repo.get("theme") == "light"
    assert repo.get("missing", "fallback") == "fallback"
    keys = [s.key for s in repo.all()]
    assert "theme" in keys


def test_export_logs(in_memory_db: Database) -> None:
    repo = ExportLogRepo(in_memory_db)
    repo.add("csv", "/tmp/a.csv", 100)
    repo.add("pdf", "/tmp/a.pdf", 1000)
    assert len(repo.list()) == 2
