"""Re-export para compatibilidad. Preferir core.modules.taskboard.constants."""

from core.modules.taskboard.constants import COLUMNS, DB_PATH, WIP_LIMIT_PER_COLUMN

__all__ = ["COLUMNS", "DB_PATH", "WIP_LIMIT_PER_COLUMN"]
