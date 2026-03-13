"""
Presentador del TaskBoard.
Separa la lógica de la vista: validaciones, orquestación, mensajes.
"""

from typing import Callable

from core.modules.taskboard import BoardService, COLUMNS, col_key_to_display


class TaskBoardPresenter:
    """Presentador: expone datos y acciones para TaskBoardView."""

    def __init__(self, board: BoardService):
        self._board = board

    @property
    def board(self) -> BoardService:
        return self._board

    @property
    def columns(self) -> list[str]:
        return list(COLUMNS)

    def col_display(self, key: str) -> str:
        return col_key_to_display(key)

    def can_add_to_backlog(self) -> bool:
        return self._board.can_add_to("backlog")

    def can_add_to(self, column_key: str) -> bool:
        return self._board.can_add_to(column_key)

    def create_task(self, name: str):
        return self._board.create_task(name)

    def create_task_in(self, name: str, column_key: str):
        return self._board.create_task_in(name, column_key)

    def move_task(self, task_id: str, target_column: str) -> bool:
        return self._board.move_task(task_id, target_column)

    def get_tasks_by_column(self) -> dict[str, list]:
        return self._board.data

    def is_overcapacity(self, column_key: str) -> bool:
        return self._board.is_overcapacity(column_key)

    def is_any_overcapacity(self) -> bool:
        return any(self._board.is_overcapacity(c) for c in COLUMNS)
