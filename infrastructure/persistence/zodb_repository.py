"""Repositorio ZODB. Implementa BoardRepository (puerto de aplicación)."""

import copy
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)
from typing import Any

import transaction
import ZODB
import ZODB.FileStorage

from domain.taskboard.constants import COLUMNS
from domain.taskboard.masters import KANBAN_COLUMNS
from infrastructure.persistence.config import get_zodb_path
from infrastructure.persistence.schema_versions import CURRENT_SCHEMA_VERSION, migrate_to_latest

# Maestros solo en código (domain). BD guarda solo columns + transitions.


def _default_deepflow() -> dict[str, Any]:
    columns = {kc["key"]: [] for kc in KANBAN_COLUMNS}
    return {"columns": columns, "transitions": []}


def _legacy_to_v4(raw: dict[str, Any]) -> dict[str, Any]:
    columns = {}
    for col in COLUMNS:
        columns[col] = list(raw.get(col, []) if isinstance(raw.get(col), list) else [])
    transitions = raw.get("transitions", []) if isinstance(raw.get("transitions"), list) else []
    return {"columns": columns, "transitions": transitions}


def _ensure_deepflow(root: Any) -> dict[str, Any]:
    schema_version = root.get("schema_version", 1)
    container = root.get("deepflow") or root.get("task") or root.get("board")

    if container is None:
        return _default_deepflow()

    if "columns" not in container and any(
        k in container for k in ("backlog", "todo", "in_progress")
    ):
        container = _legacy_to_v4(dict(container))
    elif "columns" not in container:
        container = dict(container)
        container["columns"] = {kc["key"]: [] for kc in KANBAN_COLUMNS}
        for col in COLUMNS:
            if col in container and isinstance(container[col], list):
                container["columns"][col] = container[col]

    result = copy.deepcopy(container)
    if schema_version < CURRENT_SCHEMA_VERSION:
        result = migrate_to_latest(result, schema_version)

    if "columns" not in result or not isinstance(result["columns"], dict):
        result["columns"] = {kc["key"]: [] for kc in KANBAN_COLUMNS}
    if "transitions" not in result or not isinstance(result["transitions"], list):
        result["transitions"] = []

    for kc in KANBAN_COLUMNS:
        key = kc.get("key")
        if key and key not in result["columns"]:
            result["columns"][key] = []

    # Maestros v5: asegurar que existan
    from domain.taskboard.masters import ORIGEN_OPTIONS, SOLICITANTE_OPTIONS, TRIBU_SQUAD_OPTIONS
    if "tribu_squad" not in result or not isinstance(result.get("tribu_squad"), list):
        result["tribu_squad"] = [dict(o) for o in TRIBU_SQUAD_OPTIONS]
    if "solicitante" not in result or not isinstance(result.get("solicitante"), list):
        result["solicitante"] = [dict(o) for o in SOLICITANTE_OPTIONS]
    if "canal_reporte" not in result or not isinstance(result.get("canal_reporte"), list):
        result["canal_reporte"] = [dict(o) for o in ORIGEN_OPTIONS]

    return result


class ZODBBoardRepository:
    """Implementa BoardRepository usando ZODB."""

    def __init__(self, db_path: Path | str | None = None):
        self._path = Path(db_path or get_zodb_path())
        self._path.parent.mkdir(parents=True, exist_ok=True)
        LOG.info("Abriendo ZODB: %s", self._path)
        storage = ZODB.FileStorage.FileStorage(str(self._path))
        self._db = ZODB.DB(storage)

    def _open_connection(self):
        return self._db.open()

    def get_board_data(self) -> dict[str, Any]:
        conn = self._open_connection()
        try:
            return _ensure_deepflow(conn.root())
        finally:
            conn.close()

    def save_board_data(self, data: dict[str, Any]) -> bool:
        conn = self._open_connection()
        try:
            root = conn.root()
            root["schema_version"] = CURRENT_SCHEMA_VERSION
            to_save = {
                "columns": copy.deepcopy(data.get("columns", {})),
                "transitions": copy.deepcopy(data.get("transitions", [])),
                "tribu_squad": copy.deepcopy(data.get("tribu_squad", [])),
                "solicitante": copy.deepcopy(data.get("solicitante", [])),
                "canal_reporte": copy.deepcopy(data.get("canal_reporte", [])),
            }
            root["deepflow"] = to_save
            transaction.commit()
            LOG.debug("Datos guardados en ZODB")
            return True
        except Exception as e:
            transaction.abort()
            LOG.error("Error al guardar en ZODB: %s", e, exc_info=True)
            return False
        finally:
            conn.close()

    def close(self) -> None:
        LOG.debug("Cerrando ZODB")
        self._db.close()
