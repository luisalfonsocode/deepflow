"""
Versionado de schema para ZODB.
  - schema_version 1: columnas + transitions
  - schema_version 2: campo ticket en tareas
  - schema_version 3: tribe_and_squad, requester, reporting_channel
  - schema_version 4: container deepflow, maestros, columns dict, Task campos
  - schema_version 5: maestros persistentes (tribu_squad, solicitante, canal_reporte)
  - schema_version 6: maestro categoria
  - schema_version 7: backfill finished_at en tareas en Done
  - schema_version 8: maestro kanban_columns (columnas con wip_limit configurable)
  - schema_version 9: blocked_periods en tareas (períodos bloqueados editables por usuario)
  - schema_version 10: order en subtareas (asignar 0,1,2,... si no existe, ordenar lista)
"""

import logging
from typing import Any

LOG = logging.getLogger(__name__)

from domain.taskboard.masters import (
    CATEGORIA_OPTIONS,
    default_kanban_columns_dicts,
    KANBAN_COLUMNS,
    KANBAN_COLUMNS_KEY,
    ORIGEN_OPTIONS,
    SOLICITANTE_OPTIONS,
    TRIBU_SQUAD_OPTIONS,
)


def migrate_to_latest(data: dict[str, Any], from_version: int) -> dict[str, Any]:
    """Migra datos desde from_version a la última versión (en secuencia v2, v3, ...)."""
    if from_version >= CURRENT_SCHEMA_VERSION:
        return data
    steps = [s for s in range(from_version + 1, CURRENT_SCHEMA_VERSION + 1) if s >= 2]
    LOG.info("Migrando schema de v%d a v%d (pasos: %s)", from_version, CURRENT_SCHEMA_VERSION, steps)
    result = data
    if from_version < 2:
        result = _migrate_v1_to_v2(result)
    if from_version < 3:
        result = _migrate_v2_to_v3(result)
    if from_version < 4:
        result = _migrate_v3_to_v4(result)
    if from_version < 5:
        result = _migrate_v4_to_v5(result)
    if from_version < 6:
        result = _migrate_v5_to_v6(result)
    if from_version < 7:
        result = _migrate_v6_to_v7(result)
    if from_version < 8:
        result = _migrate_v7_to_v8(result)
    if from_version < 9:
        result = _migrate_v8_to_v9(result)
    if from_version < 10:
        result = _migrate_v9_to_v10(result)
    LOG.debug("Migración de schema completada")
    return result


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    cols = data.get("columns") or _flat_cols(data)
    for col, tasks in cols.items():
        for task in tasks:
            if isinstance(task, dict) and "ticket" not in task:
                task["ticket"] = ""
    return data


def _migrate_v2_to_v3(data: dict[str, Any]) -> dict[str, Any]:
    cols = data.get("columns") or _flat_cols(data)
    for col, tasks in cols.items():
        for task in tasks:
            if isinstance(task, dict):
                if "tribe_and_squad" not in task:
                    task["tribe_and_squad"] = ""
                if "requester" not in task:
                    task["requester"] = ""
                if "reporting_channel" not in task:
                    task["reporting_channel"] = ""
                if "origen" not in task:
                    task["origen"] = ""
                if "solicitante" not in task:
                    task["solicitante"] = task.get("requester", "")
    return data


def _flat_cols(data: dict[str, Any]) -> dict[str, list]:
    return {
        kc["key"]: data.get(kc["key"], [])
        for kc in KANBAN_COLUMNS
        if isinstance(data.get(kc["key"]), list)
    }


def _migrate_v3_to_v4(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v4. Solo columns + transitions; maestros vienen de domain."""
    if "columns" in data and isinstance(data["columns"], dict):
        cols = dict(data["columns"])
    else:
        cols = _flat_cols(data)
        for kc in KANBAN_COLUMNS:
            col = kc["key"]
            if col not in cols:
                cols[col] = []

    for kc in KANBAN_COLUMNS:
        key = kc.get("key")
        if key and key not in cols:
            cols[key] = []

    for col, tasks in cols.items():
        for task in tasks:
            if not isinstance(task, dict):
                continue
            if "prioridad" not in task:
                task["prioridad"] = False
            if "detalle" not in task:
                task["detalle"] = ""
            if "due_date" not in task:
                task["due_date"] = ""
            if "created_at" not in task and "entered_at" in task:
                task["created_at"] = task["entered_at"]
            elif "created_at" not in task:
                task["created_at"] = ""
            if "solicitante" not in task and "requester" in task:
                task["solicitante"] = task["requester"]
            elif "solicitante" not in task:
                task["solicitante"] = ""
            if "origen" not in task and "reporting_channel" in task:
                task["origen"] = task["reporting_channel"]
            elif "origen" not in task:
                task["origen"] = ""
            for st in task.get("subtasks", []):
                if isinstance(st, dict):
                    if "order" not in st:
                        st["order"] = 0
                    if "estado" not in st:
                        st["estado"] = "done" if st.get("done") else "pending"
                    if "name" not in st and "text" in st:
                        st["name"] = st["text"]

    data["columns"] = cols
    return {k: v for k, v in data.items() if k in ("columns", "transitions")}


def _migrate_v4_to_v5(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v5. Añade maestros persistentes (tribu_squad, solicitante, canal_reporte)."""
    defaults = {
        "tribu_squad": [dict(o) for o in TRIBU_SQUAD_OPTIONS],
        "solicitante": [dict(o) for o in SOLICITANTE_OPTIONS],
        "canal_reporte": [dict(o) for o in ORIGEN_OPTIONS],
    }
    for key, default_list in defaults.items():
        if key not in data or not isinstance(data.get(key), list):
            data[key] = default_list.copy()
    return data


def _migrate_v5_to_v6(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v6. Añade maestro categoria y campo en tareas."""
    if "categoria" not in data or not isinstance(data.get("categoria"), list):
        data["categoria"] = [dict(o) for o in CATEGORIA_OPTIONS]
    cols = data.get("columns") or {}
    for col, tasks in cols.items():
        for task in tasks:
            if isinstance(task, dict) and "categoria" not in task:
                task["categoria"] = ""
    return data


def _migrate_v6_to_v7(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v7. Rellena finished_at en tareas en Done que no lo tienen."""
    cols = data.get("columns") or {}
    done_tasks = cols.get("done", [])
    for task in done_tasks:
        if isinstance(task, dict) and not task.get("finished_at"):
            task["finished_at"] = (
                task.get("entered_at")
                or task.get("created_at")
                or ""
            )
    return data


def _migrate_v7_to_v8(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v8. Añade maestro kanban_columns con wip_limit configurable."""
    if KANBAN_COLUMNS_KEY not in data or not isinstance(data.get(KANBAN_COLUMNS_KEY), list):
        data[KANBAN_COLUMNS_KEY] = default_kanban_columns_dicts()
    return data


def _migrate_v8_to_v9(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v9. Añade blocked_periods (períodos bloqueados editables) en tareas."""
    cols = data.get("columns") or {}
    for col_tasks in cols.values():
        for task in col_tasks:
            if isinstance(task, dict) and "blocked_periods" not in task:
                task["blocked_periods"] = []
    return data


def _migrate_v9_to_v10(data: dict[str, Any]) -> dict[str, Any]:
    """Migra a v10. Asigna order 0,1,2,... a subtareas que no lo tienen; ordena la lista."""
    cols = data.get("columns") or {}
    for col_tasks in cols.values():
        for task in col_tasks:
            if not isinstance(task, dict):
                continue
            subtasks = task.get("subtasks")
            if not isinstance(subtasks, list) or not subtasks:
                continue
            valid = [s for s in subtasks if isinstance(s, dict)]
            for i, st in enumerate(valid):
                if "order" not in st:
                    st["order"] = i
                if "name" not in st and "text" in st:
                    st["name"] = st["text"]
                if "estado" not in st:
                    st["estado"] = "done" if st.get("done") else "pending"
            valid.sort(key=lambda x: x.get("order", 999))
            task["subtasks"] = valid
    return data


CURRENT_SCHEMA_VERSION = 10
