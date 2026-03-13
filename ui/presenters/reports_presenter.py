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

    def _get_export_service(self) -> ExportService:
        self._board.load()
        return ExportService(
            self._board.data,
            list(COLUMNS),
            col_key_to_display,
        )

    def load_activities(self) -> list[dict[str, Any]]:
        """Recarga el board y retorna tareas para la tabla."""
        return self._get_export_service().get_all_activities()

    def load_transitions(self) -> list[dict[str, Any]]:
        """Recarga el board y retorna transiciones."""
        return self._get_export_service().get_all_transitions()

    def load_subtasks(self) -> list[dict[str, Any]]:
        """Recarga el board y retorna subtareas aplanadas."""
        return self._get_export_service().get_all_subtasks()

    def export_to_excel(self, filepath: Path) -> bool:
        """Exporta los 3 reportes (Tareas, Subtareas, Transiciones) a Excel. Retorna True si tuvo éxito."""
        svc = self._get_export_service()
        activities = svc.get_all_activities()
        subtasks = svc.get_all_subtasks()
        transitions = svc.get_all_transitions()
        return self._exporter.export(activities, subtasks, transitions, filepath)

    def suggest_filename_excel(self) -> str:
        """Nombre sugerido para exportación Excel."""
        return f"actividades_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.xlsx"
