"""
Re-export para compatibilidad.
Preferir: from core.modules.taskboard import BoardService
"""

from core.modules.taskboard import BoardService, col_key_to_display

Board = BoardService

__all__ = ["Board", "BoardService", "col_key_to_display"]
