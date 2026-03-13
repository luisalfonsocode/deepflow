"""
Almacenamiento del tablero en archivo JSON.
Operaciones de bajo nivel: leer y escribir monoflow_db.json de forma segura.
"""

import json
import os
from pathlib import Path
from typing import Any

from core.modules.taskboard.constants import COLUMNS, DB_PATH


def _get_default_data() -> dict[str, Any]:
    """Estructura por defecto del archivo de datos."""
    return {
        "backlog": [],
        "todo": [],
        "in_progress": [],
        "done": [],
        "detenido": [],
    }


def _ensure_dir(path: Path) -> None:
    """Asegura que el directorio del archivo existe."""
    path.parent.mkdir(parents=True, exist_ok=True)


def load_board(path: Path | str | None = None) -> dict[str, Any]:
    """
    Carga el tablero desde JSON de forma segura.
    Retorna la estructura por defecto si el archivo no existe o está corrupto.
    """
    file_path = Path(path or DB_PATH)
    if not file_path.exists():
        return _get_default_data()

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        for col in COLUMNS:
            if col not in data or not isinstance(data[col], list):
                data[col] = []
        return data
    except (json.JSONDecodeError, OSError):
        return _get_default_data()


def save_board(data: dict[str, Any], path: Path | str | None = None) -> bool:
    """
    Guarda el tablero en JSON de forma segura.
    Escribe a archivo temporal y renombra para evitar corrupción.
    """
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
        return True
    except OSError:
        tmp.unlink(missing_ok=True)
        return False
