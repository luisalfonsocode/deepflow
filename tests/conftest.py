"""Fixtures compartidas para los tests."""

from copy import deepcopy
from typing import Any

import pytest

from core.modules.taskboard.constants import COLUMNS


def _default_data() -> dict[str, Any]:
    return {
        "backlog": [],
        "todo": [],
        "in_progress": [],
        "done": [],
        "detenido": [],
    }


class InMemoryBoardRepository:
    """Repositorio en memoria para tests. No persiste a disco."""

    def __init__(self, initial_data: dict | None = None):
        self._data = deepcopy(initial_data or _default_data())
        for col in COLUMNS:
            if col not in self._data or not isinstance(self._data[col], list):
                self._data[col] = []

    def get_board_data(self) -> dict:
        return deepcopy(self._data)

    def save_board_data(self, data: dict) -> bool:
        self._data = deepcopy(data)
        return True


@pytest.fixture
def empty_repo():
    """Repositorio vacío."""
    return InMemoryBoardRepository()


@pytest.fixture
def board_service(empty_repo):
    """BoardService con repositorio en memoria."""
    from core.modules.taskboard.services import BoardService

    return BoardService(empty_repo)
