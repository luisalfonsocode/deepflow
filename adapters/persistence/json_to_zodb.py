"""
Migración única: JSON → ZODB.
Si existe monoflow_db.json y no existe monoflow_db.fs, migra los datos.
"""

from pathlib import Path

from adapters.persistence.json_file import load_board
from adapters.persistence.zodb_repository import ZODBBoardRepository
from core.modules.taskboard.constants import COLUMNS, DB_PATH, DB_ZODB_PATH


def migrate_json_to_zodb_if_needed(json_path: Path | None = None) -> bool:
    """
    Si existe JSON y no ZODB, migra. Retorna True si se realizó migración.
    """
    jpath = Path(json_path or DB_PATH)
    zpath = Path(DB_ZODB_PATH)

    if not jpath.exists() or zpath.exists():
        return False

    data = load_board(jpath)
    for col in COLUMNS:
        if col not in data or not isinstance(data[col], list):
            data[col] = []
    if "transitions" not in data or not isinstance(data["transitions"], list):
        data["transitions"] = []

    repo = ZODBBoardRepository(zpath)
    ok = repo.save_board_data(data)
    repo.close()
    return ok
