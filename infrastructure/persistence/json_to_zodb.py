"""Migración JSON → ZODB."""

import logging
import shutil
from pathlib import Path

LOG = logging.getLogger(__name__)

from domain.taskboard.masters import KANBAN_COLUMNS
from infrastructure.persistence.config import (
    DATA_DIR,
    DB_PATH,
    DB_ZODB_PATH,
    LEGACY_MONOFLOW_FS,
    LEGACY_JSON_PATH,
    LEGACY_MONOFLOW_JSON,
    LEGACY_MONOFLOW_JSON_DATA,
    get_zodb_path,
)
from infrastructure.persistence.json_file import load_board
from infrastructure.persistence.schema_versions import migrate_to_latest
from infrastructure.persistence.zodb_repository import ZODBBoardRepository


def migrate_monoflow_zodb_to_deepflow_if_needed() -> bool:
    if DB_ZODB_PATH.exists():
        return False
    if not LEGACY_MONOFLOW_FS.exists():
        return False
    LOG.info("Migrando MonoFlow ZODB a DeepFlow: %s -> %s", LEGACY_MONOFLOW_FS, DB_ZODB_PATH)
    DB_ZODB_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEGACY_MONOFLOW_FS, DB_ZODB_PATH)
    for ext in (".index",):
        src = Path(str(LEGACY_MONOFLOW_FS) + ext)
        if src.exists():
            shutil.copy2(src, Path(str(DB_ZODB_PATH) + ext))
    LOG.info("Migración MonoFlow ZODB completada")
    return True


def _find_json_source() -> Path | None:
    for path in (
        DB_PATH,
        DATA_DIR / "deepflow_db.json",
        LEGACY_MONOFLOW_JSON_DATA,
        LEGACY_JSON_PATH,
        LEGACY_MONOFLOW_JSON,
    ):
        if path.exists():
            return path
    return None


def _flat_to_v4(raw: dict) -> dict:
    columns = {kc["key"]: list(raw.get(kc["key"], []) or []) for kc in KANBAN_COLUMNS}
    transitions = raw.get("transitions") if isinstance(raw.get("transitions"), list) else []
    result = {"columns": columns, "transitions": transitions}
    return migrate_to_latest(result, 3)


def migrate_json_to_zodb_if_needed(json_path: Path | None = None) -> bool:
    zpath = get_zodb_path()
    if zpath != DB_ZODB_PATH:
        return False
    if zpath.exists():
        return False

    jpath = Path(json_path) if json_path else _find_json_source()
    if not jpath or not jpath.exists():
        return False

    data = load_board(jpath)
    for kc in KANBAN_COLUMNS:
        col = kc["key"]
        if col not in data or not isinstance(data.get(col), list):
            data[col] = []
    if "transitions" not in data or not isinstance(data["transitions"], list):
        data["transitions"] = []

    deepflow = _flat_to_v4(data)
    zpath.parent.mkdir(parents=True, exist_ok=True)
    repo = ZODBBoardRepository(zpath)
    ok = repo.save_board_data(deepflow)
    repo.close()
    if ok:
        LOG.info("Migración JSON a ZODB completada")
    else:
        LOG.error("Migración JSON a ZODB falló al guardar")
    return ok
