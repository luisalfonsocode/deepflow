"""
Servicio del tablero Kanban.
CRUD: creación, modificación de nombre, eliminación, consulta.
Almacena por tarea: started_at (primera vez en In Progress), finished_at (última vez en Done).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.modules.taskboard.constants import COLUMNS, DB_PATH, WIP_LIMIT_PER_COLUMN

if TYPE_CHECKING:
    from core.modules.taskboard.ports.board_repository import BoardRepository


class BoardService:
    """Gestiona el tablero. Usa BoardRepository para persistencia (DIP)."""

    def __init__(self, repository: "BoardRepository"):
        """
        Args:
            repository: Implementación de BoardRepository (inyección de dependencias).
        """
        self._repo = repository
        self._data = self._repo.get_board_data()

    @property
    def data(self) -> dict[str, list[dict[str, Any]]]:
        return self._data

    def load(self) -> None:
        """Recarga desde el repositorio."""
        self._data = self._repo.get_board_data()

    def persist(self) -> bool:
        """Persiste mediante el repositorio."""
        return self._repo.save_board_data(self._data)

    # --- Creación ---
    def create_task(self, name: str = "") -> dict[str, Any] | None:
        """Crea tarea en Backlog. Retorna None si Backlog está lleno."""
        if not self._can_add_to("backlog"):
            return None
        now = datetime.now(timezone.utc).isoformat()
        task = {
            "id": str(uuid.uuid4()),
            "name": name.strip() or "Nueva tarea",
            "entered_at": now,
            "subtasks": [],
        }
        self._data["backlog"].append(task)
        self.persist()
        return task

    def create_task_from_clipboard(self, text: str) -> dict[str, Any] | None:
        """Crea tarea desde texto (ej. portapapeles)."""
        return self.create_task(text)

    def create_task_in(self, name: str, column_key: str) -> dict[str, Any] | None:
        """Crea tarea directamente en la columna indicada. Retorna None si está llena."""
        if not self._can_add_to(column_key):
            return None
        now = datetime.now(timezone.utc).isoformat()
        task = {
            "id": str(uuid.uuid4()),
            "name": name.strip() or "Nueva tarea",
            "entered_at": now,
            "subtasks": [],
        }
        if column_key == "in_progress":
            task["started_at"] = now
        if column_key == "done":
            task["finished_at"] = now
        self._data[column_key].append(task)
        self.persist()
        return task

    # --- Modificación ---
    def update_task_name(self, task_id: str, new_name: str) -> bool:
        """Modifica el nombre de una tarea. Retorna False si no existe."""
        task = self._find_task(task_id)
        if not task:
            return False
        task["name"] = new_name.strip() or task.get("name", "Nueva tarea")
        self.persist()
        return True

    def update_task_subtasks(self, task_id: str, subtasks: list[dict[str, Any]]) -> bool:
        """Actualiza la lista de subtareas. Cada item: {"text": str, "done": bool}."""
        task = self._find_task(task_id)
        if not task:
            return False
        task["subtasks"] = subtasks
        self.persist()
        return True

    def move_task(self, task_id: str, target_column: str) -> bool:
        """Mueve tarea a columna destino. Retorna False si destino está lleno."""
        if not self._can_add_to(target_column):
            return False
        result = self._pop_task(task_id)
        if not result:
            return False
        task, from_column = result
        now = datetime.now(timezone.utc).isoformat()
        task["entered_at"] = now
        if target_column == "in_progress" and not task.get("started_at"):
            task["started_at"] = now
        if target_column == "done":
            task["finished_at"] = now
        self._data[target_column].append(task)
        self.persist()
        return True

    # --- Eliminación ---
    def delete_task(self, task_id: str) -> bool:
        """Elimina una tarea del tablero. Retorna False si no existe."""
        for col in COLUMNS:
            for i, t in enumerate(self._data[col]):
                if t.get("id") == task_id:
                    self._data[col].pop(i)
                    self.persist()
                    return True
        return False

    # --- Consulta ---
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Obtiene una tarea por id. Retorna None si no existe."""
        return self._find_task(task_id)

    def get_tasks_with_timestamps(self) -> list[dict[str, Any]]:
        """Todas las tareas con started_at y finished_at para exportación."""
        result = []
        for col in COLUMNS:
            for t in self._data.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    result.append({
                        "task_id": t["id"],
                        "task_name": t.get("name", ""),
                        "started_at": t.get("started_at") or "",
                        "finished_at": t.get("finished_at") or "",
                    })
        return result

    def can_add_to(self, column_key: str) -> bool:
        """True si la columna admite más tareas (límite WIP)."""
        return len(self._data.get(column_key, [])) < WIP_LIMIT_PER_COLUMN

    def count(self, column_key: str) -> int:
        """Número de tareas en la columna."""
        return len(self._data.get(column_key, []))

    def is_overcapacity(self, column_key: str) -> bool:
        """True si la columna supera el límite WIP."""
        return self.count(column_key) > WIP_LIMIT_PER_COLUMN

    # --- Privados ---
    def _find_task(self, task_id: str) -> dict[str, Any] | None:
        for col in COLUMNS:
            for t in self._data[col]:
                if t.get("id") == task_id:
                    return t
        return None

    def _pop_task(self, task_id: str) -> tuple[dict[str, Any], str] | None:
        for col in COLUMNS:
            for i, t in enumerate(self._data[col]):
                if t.get("id") == task_id:
                    return (self._data[col].pop(i), col)
        return None

    def _can_add_to(self, column_key: str) -> bool:
        return self.can_add_to(column_key)
