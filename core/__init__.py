"""MonoFlow - Lógica de negocio."""

from core.modules.taskboard import (
    BoardRepository,
    BoardService,
    COLUMNS,
    col_key_to_display,
    WIP_LIMIT_PER_COLUMN,
)

# Alias para compatibilidad
Board = BoardService

__all__ = [
    "Board",
    "BoardRepository",
    "BoardService",
    "COLUMNS",
    "col_key_to_display",
    "WIP_LIMIT_PER_COLUMN",
]
