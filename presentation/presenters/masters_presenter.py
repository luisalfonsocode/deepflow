"""
Presentador del módulo Maestros.
CRUD de maestros: tribu_squad, solicitante, canal_reporte, categoria, kanban_columns.
"""

from typing import Any

from application.taskboard import BoardService


MASTER_KEYS = {
    "tribu_squad": "Tribu y Squad",
    "solicitante": "Solicitante",
    "canal_reporte": "Canal de reporte",
    "categoria": "Categoría",
}


class MastersPresenter:
    """Presentador: obtiene y persiste maestros."""

    def __init__(self, board: BoardService):
        self._board = board

    def load_master(self, master_key: str) -> list[dict[str, str]]:
        """Recarga el board y retorna la lista del maestro."""
        self._board.load()
        return self._board.get_master_list(master_key)

    def save_master(self, master_key: str, items: list[dict[str, str]]) -> bool:
        """Persiste la lista del maestro."""
        return self._board.save_master_list(master_key, items)

    def load_kanban_columns(self) -> list[dict[str, Any]]:
        """Recarga el board y retorna kanban_columns (key, label, order, wip_limit)."""
        self._board.load()
        return self._board.get_kanban_columns()

    def save_kanban_columns(self, columns: list[dict[str, Any]]) -> bool:
        """Persiste el maestro kanban_columns."""
        return self._board.save_kanban_columns(columns)

    def get_master_label(self, master_key: str) -> str:
        """Etiqueta visible del maestro."""
        return MASTER_KEYS.get(master_key, master_key)
