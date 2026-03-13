"""Constantes del módulo TaskBoard."""

from pathlib import Path

COLUMNS = ("backlog", "todo", "in_progress", "done", "detenido")
WIP_LIMIT_PER_COLUMN = 3
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = _PROJECT_ROOT / "monoflow_db.json"
DB_ZODB_PATH = _PROJECT_ROOT / "monoflow_db.fs"
