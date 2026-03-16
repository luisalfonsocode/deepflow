"""
Presentador del módulo Maestros.
CRUD de maestros: tribu_squad, solicitante, canal_reporte.
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

    def get_master_label(self, master_key: str) -> str:
        """Etiqueta visible del maestro."""
        return MASTER_KEYS.get(master_key, master_key)
