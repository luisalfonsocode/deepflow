"""
Caso de uso: gestión del tablero Kanban.
Orquesta dominio e infraestructura (repositorio).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from domain.taskboard.constants import TZ_APP
from typing import TYPE_CHECKING, Any

from domain.taskboard.constants import COLUMNS
from domain.taskboard.masters import KANBAN_COLUMNS, get_column_keys, get_wip_limit

if TYPE_CHECKING:
    from application.ports.board_repository import BoardRepository

# Maestros solo en código (domain), no en BD
_COLUMN_KEYS = get_column_keys(KANBAN_COLUMNS)


def _columns(data: dict) -> dict[str, list]:
    """Acceso a columns; soporta estructura v4 y legacy."""
    if "columns" in data and isinstance(data["columns"], dict):
        return data["columns"]
    return {col: data.get(col, []) for col in COLUMNS}


def _column_keys(_data: dict) -> tuple[str, ...]:
    """Claves de columnas desde domain (código), no desde BD."""
    return _COLUMN_KEYS


class BoardService:
    """Caso de uso: gestiona el tablero. Usa BoardRepository (puerto) para persistencia."""

    def __init__(self, repository: "BoardRepository"):
        self._repo = repository
        self._data = self._repo.get_board_data()

    @property
    def data(self) -> dict[str, Any]:
        """Datos con compat: columnas también en top level (data['backlog'], etc.)."""
        d = dict(self._data)
        cols = self._cols()
        for col in self._col_keys():
            d[col] = cols.get(col, [])
        return d

    def _cols(self) -> dict[str, list]:
        return _columns(self._data)

    def _col_keys(self) -> tuple[str, ...]:
        return _column_keys(self._data)

    def load(self) -> None:
        """Recarga desde el repositorio."""
        self._data = self._repo.get_board_data()

    def persist(self) -> bool:
        """Persiste mediante el repositorio."""
        return self._repo.save_board_data(self._data)

    def shutdown(self) -> None:
        """Cierra recursos del repositorio (ej. ZODB). Llamar al salir de la app."""
        self._repo.close()

    # --- Maestros (v5) ---
    def get_master_list(self, master_key: str) -> list[dict[str, str]]:
        """Obtiene la lista de un maestro: tribu_squad, solicitante, canal_reporte."""
        items = self._data.get(master_key, [])
        if not isinstance(items, list):
            return []
        return [dict(item) for item in items if isinstance(item, dict) and item.get("label")]

    def save_master_list(self, master_key: str, items: list[dict[str, str]]) -> bool:
        """Persiste la lista de un maestro."""
        valid = [
            {"key": (x.get("key") or str(x.get("label", "")).lower().replace(" ", "_")), "label": str(x.get("label", ""))}
            for x in items
            if isinstance(x, dict) and x.get("label")
        ]
        self._data[master_key] = valid
        return self.persist()

    # --- Creación ---
    def _new_task(self, name: str, column_key: str) -> dict[str, Any]:
        """Crea dict Task con campos v4."""
        now = datetime.now(TZ_APP).isoformat()
        task = {
            "id": str(uuid.uuid4()),
            "ticket": "",
            "name": name.strip() or "Nueva tarea",
            "created_at": now,
            "entered_at": now,
            "subtasks": [],
            "tribe_and_squad": "",
            "solicitante": "",
            "origen": "",
            "categoria": "",
            "prioridad": False,
            "detalle": "",
            "due_date": "",
            "requester": "",
            "reporting_channel": "",
        }
        if column_key == "in_progress":
            task["started_at"] = now
        if column_key == "done":
            task["finished_at"] = now
        return task

    def create_task(self, name: str = "") -> dict[str, Any] | None:
        """Crea tarea en Backlog. Retorna None si Backlog está lleno."""
        if not self._can_add_to("backlog"):
            return None
        task = self._new_task(name, "backlog")
        self._cols()["backlog"].append(task)
        self._record_transition(task["id"], task["name"], None, "backlog")
        self.persist()
        return task

    def create_task_from_clipboard(self, text: str) -> dict[str, Any] | None:
        """Crea tarea desde texto (ej. portapapeles)."""
        return self.create_task(text)

    def create_task_in(self, name: str, column_key: str) -> dict[str, Any] | None:
        """Crea tarea directamente en la columna indicada. Retorna None si está llena."""
        if not self._can_add_to(column_key):
            return None
        task = self._new_task(name, column_key)
        self._cols()[column_key].append(task)
        self._record_transition(task["id"], task["name"], None, column_key)
        self.persist()
        return task

    # --- Modificación ---
    def update_task_name(self, task_id: str, new_name: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["name"] = new_name.strip() or task.get("name", "Nueva tarea")
        self.persist()
        return True

    def update_task_ticket(self, task_id: str, ticket: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["ticket"] = ticket.strip()
        self.persist()
        return True

    def update_task_tribe_and_squad(self, task_id: str, value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["tribe_and_squad"] = value.strip()
        self.persist()
        return True

    def update_task_requester(self, task_id: str, value: str) -> bool:
        return self.update_task_solicitante(task_id, value)

    def update_task_solicitante(self, task_id: str, value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        v = value.strip()
        task["solicitante"] = v
        task["requester"] = v
        self.persist()
        return True

    def update_task_reporting_channel(self, task_id: str, value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        v = value.strip()
        task["origen"] = v
        task["reporting_channel"] = v
        self.persist()
        return True

    def update_task_prioridad(self, task_id: str, value: bool) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["prioridad"] = bool(value)
        self.persist()
        return True

    def update_task_categoria(self, task_id: str, value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["categoria"] = value.strip()
        self.persist()
        return True

    def update_task_detalle(self, task_id: str, value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["detalle"] = value.strip()
        self.persist()
        return True

    def update_task_due_date(self, task_id: str, value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["due_date"] = value.strip()
        self.persist()
        return True

    def update_task_created_at(self, task_id: str, iso_value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["created_at"] = iso_value
        self.persist()
        return True

    def update_task_entered_at(self, task_id: str, iso_value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["entered_at"] = iso_value
        self.persist()
        return True

    def update_task_started_at(self, task_id: str, iso_value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["started_at"] = iso_value
        self.persist()
        return True

    def update_task_finished_at(self, task_id: str, iso_value: str) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        task["finished_at"] = iso_value
        self.persist()
        return True

    def update_task_subtasks(self, task_id: str, subtasks: list[dict[str, Any]]) -> bool:
        task = self._find_task(task_id)
        if not task:
            return False
        normalized = []
        for i, s in enumerate(subtasks):
            if isinstance(s, dict):
                item = dict(s)
                if "name" not in item and "text" in item:
                    item["name"] = item["text"]
                if "estado" not in item:
                    item["estado"] = "done" if item.get("done") else "pending"
                if "order" not in item:
                    item["order"] = i
                normalized.append(item)
        task["subtasks"] = normalized
        self.persist()
        return True

    def move_task(self, task_id: str, target_column: str) -> bool:
        if not self._can_add_to(target_column):
            return False
        result = self._pop_task(task_id)
        if not result:
            return False
        task, from_column = result
        now = datetime.now(TZ_APP).isoformat()
        task["entered_at"] = now
        if "created_at" not in task:
            task["created_at"] = task.get("entered_at", now)
        if target_column == "in_progress" and not task.get("started_at"):
            task["started_at"] = now
        if target_column == "done":
            task["finished_at"] = now
        self._cols()[target_column].append(task)
        self._record_transition(
            task["id"], task.get("name", ""), from_column, target_column
        )
        self.persist()
        return True

    def delete_task(self, task_id: str) -> bool:
        cols = self._cols()
        for col in self._col_keys():
            for i, t in enumerate(cols.get(col, [])):
                if t.get("id") == task_id:
                    cols[col].pop(i)
                    self.persist()
                    return True
        return False

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self._find_task(task_id)

    def get_task_column(self, task_id: str) -> str | None:
        cols = self._cols()
        for col in self._col_keys():
            for t in cols.get(col, []):
                if t.get("id") == task_id:
                    return col
        return None

    def get_tasks_with_timestamps(self) -> list[dict[str, Any]]:
        result = []
        cols = self._cols()
        for col in self._col_keys():
            for t in cols.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    result.append({
                        "task_id": t["id"],
                        "ticket": t.get("ticket", ""),
                        "task_name": t.get("name", ""),
                        "tribe_and_squad": t.get("tribe_and_squad", ""),
                        "requester": t.get("requester") or t.get("solicitante", ""),
                        "reporting_channel": t.get("reporting_channel") or t.get("origen", ""),
                        "started_at": t.get("started_at") or "",
                        "finished_at": t.get("finished_at") or "",
                    })
        return result

    def can_add_to(self, column_key: str) -> bool:
        limit = get_wip_limit(KANBAN_COLUMNS, column_key)
        if limit is None:
            return True
        return len(self._cols().get(column_key, [])) < limit

    def count(self, column_key: str) -> int:
        return len(self._cols().get(column_key, []))

    def is_overcapacity(self, column_key: str) -> bool:
        limit = get_wip_limit(KANBAN_COLUMNS, column_key)
        if limit is None:
            return False
        return len(self._cols().get(column_key, [])) > limit

    def _find_task(self, task_id: str) -> dict[str, Any] | None:
        cols = self._cols()
        for col in self._col_keys():
            for t in cols.get(col, []):
                if t.get("id") == task_id:
                    return t
        return None

    def _pop_task(self, task_id: str) -> tuple[dict[str, Any], str] | None:
        cols = self._cols()
        for col in self._col_keys():
            for i, t in enumerate(cols.get(col, [])):
                if t.get("id") == task_id:
                    return (cols[col].pop(i), col)
        return None

    def _can_add_to(self, column_key: str) -> bool:
        return self.can_add_to(column_key)

    def _record_transition(
        self,
        task_id: str,
        task_name: str,
        from_column: str | None,
        to_column: str,
    ) -> None:
        transitions = self._data.get("transitions")
        if not isinstance(transitions, list):
            self._data["transitions"] = []
            transitions = self._data["transitions"]
        transitions.append({
            "task_id": task_id,
            "task_name": task_name,
            "from_column": from_column,
            "to_column": to_column,
            "timestamp": datetime.now(TZ_APP).isoformat(),
        })
