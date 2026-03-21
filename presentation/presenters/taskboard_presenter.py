"""
Presentador del módulo TaskBoard.
Orquesta lógica de tareas; la vista solo renderiza.
"""

from typing import Any

from application.taskboard import BoardService


class TaskboardPresenter:
    """Presentador: CRUD de tareas, datos para la vista Kanban."""

    def __init__(self, board: BoardService):
        self._board = board

    def get_tasks_by_column(self, column_key: str) -> list[dict[str, Any]]:
        """Tareas de una columna."""
        self._board.load()
        return list(self._board.data.get(column_key, []))

    def get_all_columns_data(self) -> dict[str, list]:
        """Todas las columnas con sus tareas (desde maestro kanban_columns)."""
        self._board.load()
        return {col: self.get_tasks_by_column(col) for col in self._board.get_column_keys()}

    def create_task(self, name: str) -> dict[str, Any] | None:
        """Crea tarea en Backlog."""
        return self._board.create_task(name)

    def create_task_in(self, name: str, column_key: str) -> dict[str, Any] | None:
        """Crea tarea directamente en columna."""
        return self._board.create_task_in(name, column_key)

    def move_task(self, task_id: str, target_column: str) -> bool:
        """Mueve tarea a otra columna."""
        return self._board.move_task(task_id, target_column)

    def can_add_to(self, column_key: str) -> bool:
        """Indica si la columna admite más tareas."""
        return self._board.can_add_to(column_key)

    def is_overcapacity(self, column_key: str) -> bool:
        """Indica si la columna supera WIP."""
        return self._board.is_overcapacity(column_key)

    def col_display(self, column_key: str) -> str:
        """Nombre visible de columna (desde maestro kanban_columns)."""
        return self._board.col_key_to_display(column_key)
