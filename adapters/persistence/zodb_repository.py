"""
Repositorio ZODB (Zope Object Database).
Base de datos embebida orientada a objetos con soporte para versionado futuro.
"""

import copy
from pathlib import Path
from typing import Any

import transaction
import ZODB
import ZODB.FileStorage

from adapters.persistence.schema_versions import CURRENT_SCHEMA_VERSION, migrate_to_latest
from core.modules.taskboard.constants import COLUMNS, DB_ZODB_PATH


def _get_default_data() -> dict[str, Any]:
    """Estructura por defecto del tablero."""
    data: dict[str, Any] = {col: [] for col in COLUMNS}
    data["transitions"] = []
    return data


def _ensure_schema(root: dict, default_data: dict[str, Any]) -> dict[str, Any]:
    """
    Asegura que el board tiene todas las columnas.
    Aplica migraciones si schema_version es anterior a la actual.
    """
    schema_version = root.get("schema_version", 1)
    board = root.get("board")

    if board is None:
        return copy.deepcopy(default_data)

    result = copy.deepcopy(board)
    for col in COLUMNS:
        if col not in result or not isinstance(result.get(col), list):
            result[col] = []
    if "transitions" not in result or not isinstance(result.get("transitions"), list):
        result["transitions"] = []

    if schema_version < CURRENT_SCHEMA_VERSION:
        result = migrate_to_latest(result, schema_version)
    return result


class ZODBBoardRepository:
    """
    Persistencia en ZODB. Implementa BoardRepository.
    Incluye schema_version en root para migraciones futuras.
    """

    def __init__(self, db_path: Path | str | None = None):
        self._path = Path(db_path or DB_ZODB_PATH)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        storage = ZODB.FileStorage.FileStorage(str(self._path))
        self._db = ZODB.DB(storage)

    def _open_connection(self):
        return self._db.open()

    def get_board_data(self) -> dict[str, Any]:
        conn = self._open_connection()
        try:
            root = conn.root()
            default = _get_default_data()
            return _ensure_schema(root, default)
        finally:
            conn.close()

    def save_board_data(self, data: dict[str, Any]) -> bool:
        conn = self._open_connection()
        try:
            root = conn.root()
            root["schema_version"] = CURRENT_SCHEMA_VERSION
            root["board"] = copy.deepcopy(data)
            transaction.commit()
            return True
        except Exception:
            transaction.abort()
            return False
        finally:
            conn.close()

    def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        self._db.close()
