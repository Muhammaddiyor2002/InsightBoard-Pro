"""Export pipeline — CSV, Excel, PDF snapshot, chart images, text summary."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.insights import Insight
from app.utils.logger import get_logger

log = get_logger("exporter")


class Exporter:
    """Produce export artefacts for a dataset."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # CSV / Excel                                                         #
    # ------------------------------------------------------------------ #
    def export_csv(self, df: pd.DataFrame, name: str = "cleaned") -> Path:
        path = self.output_dir / self._timestamped(f"{name}.csv")
        df.to_csv(path, index=False)
        log.info("exported csv -> %s", path)
        return path

    def export_excel(
        self,
        df: pd.DataFrame,
        *,
        name: str = "report",
        extra_sheets: dict[str, pd.DataFrame] | None = None,
    ) -> Path:
        path = self.output_dir / self._timestamped(f"{name}.xlsx")
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="data", index=False)
            for sheet, content in (extra_sheets or {}).items():
                content.to_excel(writer, sheet_name=sheet[:31], index=False)
        log.info("exported excel -> %s", path)
        return path

    # ------------------------------------------------------------------ #
    # Chart images                                                        #
    # ------------------------------------------------------------------ #
    def export_chart_png(
        self, figure: object, name: str, *, width: int = 1200, height: int = 700
    ) -> Path:
        """Save a Plotly figure as a PNG image (requires kaleido)."""
        path = self.output_dir / self._timestamped(f"{name}.png")
        # Imported lazily to avoid hard dependency at startup.
        try:
            png_bytes = figure.to_image(  # type: ignore[attr-defined]
                format="png", width=width, height=height, engine="kaleido"
            )
        except (ValueError, RuntimeError) as exc:  # pragma: no cover - kaleido env issues
            log.warning("plotly-to-image failed: %s; writing fallback text", exc)
            path = path.with_suffix(".txt")
            path.write_text("Chart export unavailable (kaleido missing)\n")
            return path
        path.write_bytes(png_bytes)
        log.info("exported chart png -> %s", path)
        return path

    # ------------------------------------------------------------------ #
    # Text summary                                                        #
    # ------------------------------------------------------------------ #
    def export_text_summary(
        self,
        df: pd.DataFrame,
        *,
        insights: Iterable[Insight] = (),
        name: str = "summary",
    ) -> Path:
        path = self.output_dir / self._timestamped(f"{name}.txt")
        lines: list[str] = []
        lines.append("InsightBoard Pro — Summary Report")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
        lines.append(f"Rows × Columns: {len(df):,} × {df.shape[1]}")
        lines.append("")
        lines.append("Columns:")
        for col, dtype in df.dtypes.items():
            lines.append(f"  - {col} :: {dtype}")
        lines.append("")
        if any(True for _ in insights):
            pass
        ins_list = list(insights)
        if ins_list:
            lines.append("Auto-Insights:")
            for ins in ins_list:
                lines.append(f"  • [{ins.kind.upper()}] {ins.title}")
                lines.append(f"      {ins.detail}")
        path.write_text("\n".join(lines), encoding="utf-8")
        log.info("exported text summary -> %s", path)
        return path

    # ------------------------------------------------------------------ #
    # PDF dashboard                                                       #
    # ------------------------------------------------------------------ #
    def export_pdf_dashboard(
        self,
        df: pd.DataFrame,
        *,
        kpis: dict[str, str] | None = None,
        insights: Iterable[Insight] = (),
        name: str = "dashboard",
    ) -> Path:
        path = self.output_dir / self._timestamped(f"{name}.pdf")
        doc = SimpleDocTemplate(str(path), pagesize=A4, title="InsightBoard Pro")
        styles = getSampleStyleSheet()
        flow: list = []
        flow.append(Paragraph("InsightBoard Pro — Dashboard Snapshot", styles["Title"]))
        flow.append(Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles["Italic"]))
        flow.append(Spacer(1, 12))

        if kpis:
            kpi_rows = [["Metric", "Value"]] + list(kpis.items())
            kpi_table = Table(kpi_rows, hAlign="LEFT", colWidths=[160, 200])
            kpi_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222b3a")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ]
                )
            )
            flow.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
            flow.append(kpi_table)
            flow.append(Spacer(1, 12))

        ins_list = list(insights)
        if ins_list:
            flow.append(Paragraph("Auto-Insights", styles["Heading2"]))
            for ins in ins_list:
                flow.append(Paragraph(f"<b>{ins.title}</b>", styles["Normal"]))
                flow.append(Paragraph(ins.detail, styles["BodyText"]))
                flow.append(Spacer(1, 6))

        flow.append(Spacer(1, 12))
        flow.append(Paragraph("Sample data (first 10 rows)", styles["Heading2"]))
        head = df.head(10).fillna("").astype(str)
        if not head.empty:
            data = [list(head.columns)] + head.values.tolist()
            tbl = Table(data, hAlign="LEFT")
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ]
                )
            )
            flow.append(tbl)

        doc.build(flow)
        log.info("exported pdf dashboard -> %s", path)
        return path

    # ------------------------------------------------------------------ #
    @staticmethod
    def _timestamped(name: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem, _, ext = name.rpartition(".")
        return f"{stem}_{ts}.{ext}"
