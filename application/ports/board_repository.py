"""
Puerto de persistencia del tablero Kanban.
La capa de aplicación define qué necesita; la infraestructura implementa.
"""

from typing import Any, Protocol


class BoardRepository(Protocol):
    """Repositorio del estado completo del tablero (columnas + transiciones)."""

    def get_board_data(self) -> dict[str, Any]:
        """
        Obtiene el estado completo del tablero.
        Estructura: { "columns": {...}, "transitions": [...], maestros }
        """
        ...

    def save_board_data(self, data: dict[str, Any]) -> bool:
        """
        Persiste el estado del tablero.
        Retorna True si tuvo éxito.
        """
        ...

    def close(self) -> None:
        """Cierra conexiones/recursos. No-op para implementaciones en memoria."""
        ...
