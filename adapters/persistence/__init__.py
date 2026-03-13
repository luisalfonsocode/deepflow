"""Adaptadores de persistencia del tablero."""

from adapters.persistence.local_json_repository import (
    JsonFileBoardRepository,
    LocalJsonRepository,
)
from adapters.persistence.zodb_repository import ZODBBoardRepository

__all__ = [
    "JsonFileBoardRepository",
    "LocalJsonRepository",
    "ZODBBoardRepository",
]
