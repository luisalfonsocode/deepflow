"""Adaptadores de persistencia del tablero."""

from adapters.persistence.local_json_repository import (
    JsonFileBoardRepository,
    LocalJsonRepository,
)

__all__ = ["JsonFileBoardRepository", "LocalJsonRepository"]
