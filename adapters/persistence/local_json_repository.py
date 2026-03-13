"""
Repositorio que persiste el tablero en archivo JSON local.
Implementa el contrato BoardRepository.
"""

from pathlib import Path
from typing import Any

from adapters.persistence.json_file import load_board, save_board
from core.modules.taskboard.constants import DB_PATH


class JsonFileBoardRepository:
    """Persistencia del tablero en monoflow_db.json."""

    def __init__(self, file_path: Path | str | None = None):
        self._path = Path(file_path or DB_PATH)

    def get_board_data(self) -> dict[str, Any]:
        return load_board(self._path)

    def save_board_data(self, data: dict[str, Any]) -> bool:
        return save_board(data, self._path)


# Alias para compatibilidad
LocalJsonRepository = JsonFileBoardRepository
