"""
Presentador del módulo Reports.
Separa la lógica de exportación y datos de la vista.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.export import ExcelActivityExporter
from core.modules.reports.services import ExportService
from core.modules.taskboard import BoardService, COLUMNS, col_key_to_display


class ReportsPresenter:
    """Presentador: obtiene datos y orquesta exportación."""

    def __init__(
        self,
        board: BoardService,
        exporter: ExcelActivityExporter | None = None,
    ):
        self._board = board
        self._exporter = exporter or ExcelActivityExporter()

    def load_activities(self) -> list[dict[str, Any]]:
        """Recarga el board y retorna actividades para la tabla (con subtareas)."""
        self._board.load()
        svc = ExportService(
            self._board.data,
            list(COLUMNS),
            col_key_to_display,
        )
        return svc.get_all_activities()

    def export_to_excel(self, activities: list[dict[str, Any]], filepath: Path) -> bool:
        """Exporta actividades a Excel. Retorna True si tuvo éxito."""
        return self._exporter.export(activities, filepath)

    def suggest_filename_excel(self) -> str:
        """Nombre sugerido para exportación Excel."""
        return f"actividades_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.xlsx"
