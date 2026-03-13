"""
Versionado de schema para ZODB.
Al incrementar schema_version, añadir lógica de migración aquí.

  - schema_version 1: columnas + transitions
  - schema_version 2: campo ticket en tareas + next_ticket
"""

from typing import Any

from core.modules.taskboard.constants import COLUMNS


def migrate_to_latest(data: dict[str, Any], from_version: int) -> dict[str, Any]:
    """
    Migra datos desde from_version a la última versión.
    Retorna el dict migrado.
    """
    result = data
    if from_version < 2:
        result = _migrate_v1_to_v2(result)
    return result


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Añade campo ticket (código de solicitud externa) vacío a tareas que no lo tienen."""
    for col in COLUMNS:
        for task in data.get(col, []):
            if isinstance(task, dict) and "ticket" not in task:
                task["ticket"] = ""
    return data


CURRENT_SCHEMA_VERSION = 2
