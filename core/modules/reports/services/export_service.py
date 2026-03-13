"""
Servicio de exportación de actividades.
Separa la lógica de negocio/exportación de la UI.
"""

from pathlib import Path
from typing import Any


class ExportService:
    """Obtiene actividades del tablero y las exporta (Excel, etc.)."""

    def __init__(self, board_data: dict[str, Any], columns: list[str], col_key_to_display):
        """
        Args:
            board_data: self.board.data del BoardService
            columns: COLUMNS del taskboard
            col_key_to_display: función para mostrar nombre de columna
        """
        self._board_data = board_data
        self._columns = columns
        self._col_key_to_display = col_key_to_display

    def get_all_activities(self) -> list[dict[str, Any]]:
        """Todas las actividades con columna actual y subtareas, listas para tabla o exportación."""
        result = []
        for col in self._columns:
            for t in self._board_data.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    result.append({
                        "id": t.get("id", ""),
                        "name": t.get("name", ""),
                        "column": col,
                        "estado": self._col_key_to_display(col),
                        "column_display": self._col_key_to_display(col),
                        "subtasks": [
                            {"text": s.get("text", ""), "done": bool(s.get("done", False))}
                            for s in t.get("subtasks", [])
                        ],
                        "entered_at": t.get("entered_at") or "",
                        "started_at": t.get("started_at") or "",
                        "finished_at": t.get("finished_at") or "",
                    })
        return result
