"""Constantes del módulo TaskBoard."""

from pathlib import Path

COLUMNS = ("backlog", "todo", "in_progress", "done", "detenido")
WIP_LIMIT_PER_COLUMN = 3
DB_PATH = Path(__file__).parent.parent.parent.parent / "monoflow_db.json"
