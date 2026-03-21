"""Almacenamiento del tablero en archivo JSON."""

import json
import logging
import os
from pathlib import Path

LOG = logging.getLogger(__name__)
from typing import Any

from domain.taskboard.masters import KANBAN_COLUMNS
from infrastructure.persistence.config import DB_PATH


def _get_default_data() -> dict[str, Any]:
    return {kc["key"]: [] for kc in KANBAN_COLUMNS}


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_board(path: Path | str | None = None) -> dict[str, Any]:
    file_path = Path(path or DB_PATH)
    if not file_path.exists():
        LOG.debug("JSON no existe, usando datos por defecto: %s", file_path)
        return _get_default_data()
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        for kc in KANBAN_COLUMNS:
            col = kc["key"]
            if col not in data or not isinstance(data.get(col), list):
                data[col] = []
        LOG.debug("JSON cargado: %s", file_path)
        return data
    except (json.JSONDecodeError, OSError) as e:
        LOG.warning("Error al cargar JSON %s: %s", file_path, e)
        return _get_default_data()


def save_board(data: dict[str, Any], path: Path | str | None = None) -> bool:
    file_path = Path(path or DB_PATH)
    _ensure_dir(file_path)
    tmp = file_path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        try:
            os.replace(tmp, file_path)
        except OSError:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp.unlink(missing_ok=True)
        LOG.debug("JSON guardado: %s", file_path)
        return True
    except OSError as e:
        tmp.unlink(missing_ok=True)
        LOG.error("Error al guardar JSON %s: %s", file_path, e)
        return False
