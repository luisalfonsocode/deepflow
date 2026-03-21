"""
Presentador del módulo Reports.
Separa la lógica de exportación y datos de la vista.
"""

from datetime import datetime

from domain.taskboard import TZ_APP
from pathlib import Path
from typing import Any

from application.reports import ExportService
from application.taskboard import BoardService
from domain.taskboard import parse_date_to_iso
from infrastructure.export import ExcelActivityExporter


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
            list(self._board.get_column_keys()),
            self._board.col_key_to_display,
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

    def load_subtasks_for_task(self, task_id: str) -> list[dict[str, Any]]:
        """Retorna las subtareas de una tarea concreta."""
        all_subs = self._get_export_service().get_all_subtasks()
        return [s for s in all_subs if s.get("task_id") == task_id]

    def export_to_excel(self, filepath: Path) -> bool:
        """Exporta los 3 reportes (Tareas, Subtareas, Transiciones) a Excel. Retorna True si tuvo éxito."""
        svc = self._get_export_service()
        activities = svc.get_all_activities()
        subtasks = svc.get_all_subtasks()
        transitions = svc.get_all_transitions()
        return self._exporter.export(activities, subtasks, transitions, filepath)

    def suggest_filename_excel(self) -> str:
        """Nombre sugerido para exportación Excel."""
        return f"actividades_{datetime.now(TZ_APP).strftime('%Y%m%d_%H%M')}.xlsx"

    def get_column_items(self) -> list[tuple[str, str]]:
        """Retorna [(label, key), ...] del maestro kanban_columns, ordenado por order."""
        self._board.load()
        cols = self._board.get_kanban_columns()
        return [(c.get("label", ""), c.get("key", "")) for c in sorted(cols, key=lambda x: x.get("order", 99))]

    def display_to_column_key(self, display: str) -> str | None:
        """Convierte label a column_key según maestro kanban_columns."""
        return self._board.display_to_column_key(display)

    # --- Edición (delega en BoardService) ---

    def update_task_ticket(self, task_id: str, value: str) -> bool:
        return self._board.update_task_ticket(task_id, value)

    def update_task_name(self, task_id: str, value: str) -> bool:
        return self._board.update_task_name(task_id, value)

    def update_task_state(self, task_id: str, display_value: str) -> bool:
        """Mueve la tarea a la columna indicada por display (desde maestro kanban_columns)."""
        col = self._board.display_to_column_key(display_value)
        if col is None:
            return False
        return self._board.move_task(task_id, col)

    def update_task_state_by_key(self, task_id: str, column_key: str) -> bool:
        """Mueve la tarea a la columna indicada por clave interna."""
        return self._board.move_task(task_id, column_key)

    def can_add_to(self, column_key: str) -> bool:
        return self._board.can_add_to(column_key)

    def create_task(self, name: str = "", column_key: str = "backlog") -> dict[str, Any] | None:
        if column_key == "backlog":
            return self._board.create_task(name)
        return self._board.create_task_in(name, column_key)

    def delete_task(self, task_id: str) -> bool:
        return self._board.delete_task(task_id)

    def update_subtask(
        self, task_id: str, subtask_index: int, text: str, done: bool
    ) -> bool:
        task = self._board.get_task(task_id)
        if not task:
            return False
        subs = list(task.get("subtasks", []))
        if subtask_index < 0 or subtask_index >= len(subs):
            return False
        s = dict(subs[subtask_index])
        s["text"] = text
        s["name"] = text
        s["done"] = done
        s["estado"] = "done" if done else "pending"
        subs[subtask_index] = s
        return self._board.update_task_subtasks(task_id, subs)

    def delete_subtask(self, task_id: str, subtask_index: int) -> bool:
        task = self._board.get_task(task_id)
        if not task:
            return False
        subs = list(task.get("subtasks", []))
        if subtask_index < 0 or subtask_index >= len(subs):
            return False
        subs.pop(subtask_index)
        return self._board.update_task_subtasks(task_id, subs)

    def update_task_created_at(self, task_id: str, iso_value: str) -> bool:
        return self._board.update_task_created_at(task_id, iso_value)

    def update_task_entered_at(self, task_id: str, iso_value: str) -> bool:
        return self._board.update_task_entered_at(task_id, iso_value)

    def update_task_started_at(self, task_id: str, iso_value: str) -> bool:
        return self._board.update_task_started_at(task_id, iso_value)

    def update_task_finished_at(self, task_id: str, iso_value: str) -> bool:
        return self._board.update_task_finished_at(task_id, iso_value)

    def update_task_due_date(self, task_id: str, iso_value: str) -> bool:
        return self._board.update_task_due_date(task_id, iso_value)

    def create_subtask(self, task_id: str, text: str = "") -> bool:
        task = self._board.get_task(task_id)
        if not task:
            return False
        subs = list(task.get("subtasks", []))
        subs.append({"text": text or "Nueva subtarea", "name": text or "Nueva subtarea", "done": False, "estado": "pending"})
        return self._board.update_task_subtasks(task_id, subs)
