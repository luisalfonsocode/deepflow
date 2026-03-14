"""Fixtures compartidas para los tests."""

from copy import deepcopy
from typing import Any

import pytest

from domain.taskboard.constants import COLUMNS
from domain.taskboard.masters import KANBAN_COLUMNS


def _default_data() -> dict[str, Any]:
    """Estructura v4: columns + transitions. Maestros en domain."""
    columns = {kc["key"]: [] for kc in KANBAN_COLUMNS}
    return {"columns": columns, "transitions": []}


def _normalize_to_v4(data: dict) -> dict:
    """Convierte datos planos a v4 si hace falta. Solo columns + transitions."""
    if "columns" in data and isinstance(data["columns"], dict):
        cols = dict(data["columns"])
    else:
        cols = {col: list(data.get(col, []) or []) for col in COLUMNS}
    for kc in KANBAN_COLUMNS:
        if kc["key"] not in cols:
            cols[kc["key"]] = []
    return {
        "columns": cols,
        "transitions": data.get("transitions") if isinstance(data.get("transitions"), list) else [],
    }


class InMemoryBoardRepository:
    """Repositorio en memoria para tests. No persiste a disco."""

    def __init__(self, initial_data: dict | None = None):
        raw = deepcopy(initial_data or _default_data())
        self._data = _normalize_to_v4(raw)

    def get_board_data(self) -> dict:
        return deepcopy(self._data)

    def save_board_data(self, data: dict) -> bool:
        self._data = deepcopy(data)
        return True

    def close(self) -> None:
        """No-op para tests en memoria."""
        pass


@pytest.fixture
def empty_repo():
    """Repositorio vacío."""
    return InMemoryBoardRepository()


@pytest.fixture
def board_service(empty_repo):
    """BoardService con repositorio en memoria."""
    from application.taskboard import BoardService

    return BoardService(empty_repo)
