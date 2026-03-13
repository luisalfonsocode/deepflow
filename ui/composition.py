"""
Composición raíz (Composition Root).
Construye y conecta dependencias según el principio de Inversión de Dependencias.
"""

from typing import Any

from adapters.persistence import JsonFileBoardRepository
from core.modules.taskboard import BoardService
from core.modules.taskboard.constants import DB_PATH


def create_board_service(repository: Any = None) -> BoardService:
    """
    Crea BoardService con su repositorio inyectado.
    Punto único de construcción para facilitar testing y configuración.
    """
    repo = repository or JsonFileBoardRepository(DB_PATH)
    return BoardService(repo)
