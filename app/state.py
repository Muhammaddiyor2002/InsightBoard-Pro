"""Central application state — single source of truth for the loaded dataset."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import pandas as pd

from app.config import AppConfig
from app.database import (
    DashboardTemplateRepo,
    Database,
    ExportLogRepo,
    ReportHistoryRepo,
    SavedFilterRepo,
    SettingsRepo,
    UploadedFileRepo,
)
from app.services import (
    Aggregator,
    AIQueryService,
    DataCleaner,
    Exporter,
    FileLoader,
    FilterEngine,
    InsightsEngine,
    LoadedDataset,
)
from app.services.data_cleaner import CleaningReport
from app.utils.logger import get_logger

log = get_logger("state")

Listener = Callable[[], None]


@dataclass
class AppState:
    """Shared mutable state with a tiny pub/sub mechanism."""

    config: AppConfig
    db: Database

    # Services
    file_loader: FileLoader = field(init=False)
    cleaner: DataCleaner = field(init=False)
    aggregator: Aggregator = field(init=False)
    exporter: Exporter = field(init=False)
    insights_engine: InsightsEngine = field(init=False)
    filter_engine: FilterEngine = field(init=False)
    ai: AIQueryService = field(init=False)

    # Repositories
    files_repo: UploadedFileRepo = field(init=False)
    reports_repo: ReportHistoryRepo = field(init=False)
    filters_repo: SavedFilterRepo = field(init=False)
    templates_repo: DashboardTemplateRepo = field(init=False)
    settings_repo: SettingsRepo = field(init=False)
    export_log_repo: ExportLogRepo = field(init=False)

    # Data
    loaded: LoadedDataset | None = None
    cleaned: pd.DataFrame | None = None
    cleaning_report: CleaningReport | None = None
    filtered: pd.DataFrame | None = None

    _listeners: list[Listener] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        self.file_loader = FileLoader(
            max_size_mb=self.config.max_file_size_mb,
            allowed_extensions=self.config.allowed_extensions,
        )
        self.cleaner = DataCleaner()
        self.aggregator = Aggregator()
        self.exporter = Exporter(self.config.exports_dir)
        self.insights_engine = InsightsEngine()
        self.filter_engine = FilterEngine()
        self.ai = AIQueryService()

        self.files_repo = UploadedFileRepo(self.db)
        self.reports_repo = ReportHistoryRepo(self.db)
        self.filters_repo = SavedFilterRepo(self.db)
        self.templates_repo = DashboardTemplateRepo(self.db)
        self.settings_repo = SettingsRepo(self.db)
        self.export_log_repo = ExportLogRepo(self.db)

    # ------------------------------------------------------------------ #
    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def notify(self) -> None:
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:  # pragma: no cover  - never let a UI cb break state
                log.exception("listener failed")

    # ------------------------------------------------------------------ #
    def has_data(self) -> bool:
        return self.cleaned is not None and not self.cleaned.empty

    @property
    def df(self) -> pd.DataFrame:
        """The dataframe to use for charts / KPIs (filtered ?? cleaned)."""
        if self.filtered is not None:
            return self.filtered
        if self.cleaned is not None:
            return self.cleaned
        return pd.DataFrame()

    # ------------------------------------------------------------------ #
    def ingest_file(self, path: str) -> tuple[LoadedDataset, CleaningReport]:
        """Load + clean a file; persist a row in uploaded_files."""
        loaded = self.file_loader.load(path)
        cleaned, report = self.cleaner.clean(loaded.df)
        self.loaded = loaded
        self.cleaned = cleaned
        self.cleaning_report = report
        self.filtered = None
        from app.database.models import UploadedFile

        self.files_repo.add(
            UploadedFile(
                id=None,
                filename=loaded.source_path.name,
                path=str(loaded.source_path),
                size_bytes=loaded.size_bytes,
                rows=loaded.rows,
                cols=loaded.cols,
                delimiter=loaded.delimiter,
                encoding=loaded.encoding,
            )
        )
        self.notify()
        return loaded, report
