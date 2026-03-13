"""Módulos de MonoFlow: Widget, TaskBoard, Reports, Alerts."""

from core.modules.taskboard import (
    BoardRepository,
    BoardService,
    COLUMNS,
    WIP_LIMIT_PER_COLUMN,
    col_key_to_display,
)
from core.modules.widget import MODULES, get_module_index

__all__ = [
    "BoardRepository",
    "BoardService",
    "COLUMNS",
    "WIP_LIMIT_PER_COLUMN",
    "col_key_to_display",
    "MODULES",
    "get_module_index",
]
