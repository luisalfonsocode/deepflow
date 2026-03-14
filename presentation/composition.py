"""
Composición raíz (Composition Root).
Construye y conecta dependencias según el principio de Inversión de Dependencias.
"""

from typing import Any

from application.taskboard import BoardService
from infrastructure.persistence import ZODBBoardRepository
from infrastructure.persistence.config import get_zodb_path
from infrastructure.persistence.json_to_zodb import (
    migrate_json_to_zodb_if_needed,
    migrate_monoflow_zodb_to_deepflow_if_needed,
)


def create_clipboard_provider():
    """Crea el proveedor de portapapeles (inyectable en tests)."""
    from infrastructure.ui import QtClipboardProvider
    return QtClipboardProvider()


def create_board_service(repository: Any = None) -> BoardService:
    """
    Crea BoardService con su repositorio inyectado.
    Usa ZODB por defecto (data/db/deepflow_db.fs). Migra desde JSON si existe.
    """
    if repository is not None:
        return BoardService(repository)
    migrate_monoflow_zodb_to_deepflow_if_needed()
    migrate_json_to_zodb_if_needed()
    repo = ZODBBoardRepository(get_zodb_path())
    return BoardService(repo)
