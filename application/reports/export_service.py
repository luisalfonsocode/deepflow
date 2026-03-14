"""
Caso de uso: exportación de actividades.
Obtiene datos del tablero y los transforma para Excel, CSV, etc.
"""

from typing import Any


class ExportService:
    """Obtiene actividades del tablero y las exporta (Excel, etc.)."""

    def __init__(self, board_data: dict[str, Any], columns: list[str], col_key_to_display):
        self._board_data = board_data
        self._columns = columns
        self._col_key_to_display = col_key_to_display

    def get_all_activities(self) -> list[dict[str, Any]]:
        """Todas las actividades (tareas) con columna actual y subtareas."""
        result = []
        for col in self._columns:
            for t in self._board_data.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    result.append({
                        "id": t.get("id", ""),
                        "ticket": t.get("ticket", ""),
                        "name": t.get("name", ""),
                        "tribe_and_squad": t.get("tribe_and_squad", ""),
                        "requester": t.get("requester", ""),
                        "reporting_channel": t.get("reporting_channel", ""),
                        "column": col,
                        "estado": self._col_key_to_display(col),
                        "column_display": self._col_key_to_display(col),
                        "subtasks": [
                            {
                                "text": s.get("text", s.get("name", "")),
                                "done": bool(s.get("done", s.get("estado") == "done")),
                            }
                            for s in t.get("subtasks", [])
                        ],
                        "created_at": t.get("created_at") or t.get("entered_at") or "",
                        "started_at": t.get("started_at") or "",
                        "finished_at": t.get("finished_at") or "",
                        "due_date": t.get("due_date") or "",
                    })
        return result

    def get_all_transitions(self) -> list[dict[str, Any]]:
        """Todas las transiciones de tareas entre columnas."""
        result = []
        for t in self._board_data.get("transitions", []):
            if isinstance(t, dict) and t.get("task_id"):
                from_col = t.get("from_column")
                to_col = t.get("to_column")
                result.append({
                    "task_id": t.get("task_id", ""),
                    "task_name": t.get("task_name", ""),
                    "from_column": from_col or "",
                    "from_display": self._col_key_to_display(from_col) if from_col else "-",
                    "to_column": to_col or "",
                    "to_display": self._col_key_to_display(to_col) if to_col else "-",
                    "timestamp": t.get("timestamp", ""),
                })
        return result

    def get_all_subtasks(self) -> list[dict[str, Any]]:
        """Todas las subtareas aplanadas con info de la tarea padre."""
        result = []
        for col in self._columns:
            for t in self._board_data.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    task_id = t.get("id", "")
                    task_name = t.get("name", "")
                    task_ticket = t.get("ticket", "")
                    for idx, s in enumerate(t.get("subtasks", [])):
                        result.append({
                            "task_id": task_id,
                            "subtask_index": idx,
                            "task_ticket": task_ticket,
                            "task_name": task_name,
                            "subtask_text": s.get("text", s.get("name", "")),
                            "done": bool(s.get("done", s.get("estado") == "done")),
                            "column_display": self._col_key_to_display(col),
                        })
        return result
