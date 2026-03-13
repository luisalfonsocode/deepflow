"""
Contrato de persistencia del tablero Kanban.
Cualquier implementación (archivo JSON, API REST, etc.) debe cumplir esta interfaz.
"""

from typing import Any, Protocol


class BoardRepository(Protocol):
    """Repositorio del estado completo del tablero (columnas + transiciones)."""

    def get_board_data(self) -> dict[str, Any]:
        """
        Obtiene el estado completo del tablero.
        Estructura: { "backlog": [...], "todo": [...], ..., "transitions": [...] }
        """
        ...

    def save_board_data(self, data: dict[str, Any]) -> bool:
        """
        Persiste el estado del tablero.
        Retorna True si tuvo éxito.
        """
        ...
