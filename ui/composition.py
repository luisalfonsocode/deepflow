"""
Composición raíz (Composition Root).
Construye y conecta dependencias según el principio de Inversión de Dependencias.
"""

from typing import Any

from adapters.persistence import ZODBBoardRepository
from adapters.persistence.json_to_zodb import migrate_json_to_zodb_if_needed
from core.modules.taskboard import BoardService
from core.modules.taskboard.constants import DB_PATH, DB_ZODB_PATH


def create_board_service(repository: Any = None) -> BoardService:
    """
    Crea BoardService con su repositorio inyectado.
    Usa ZODB por defecto (monoflow_db.fs). Migra desde JSON si existe.
    """
    if repository is not None:
        return BoardService(repository)
    migrate_json_to_zodb_if_needed(DB_PATH)
    repo = ZODBBoardRepository(DB_ZODB_PATH)
    return BoardService(repo)
