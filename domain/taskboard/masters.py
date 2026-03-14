"""
Maestros por defecto según DIAGRAMA_BASE_DATOS.md.
Estructura v4: origen, tribu_squad, solicitante, kanban_columns.
"""

from typing import Any

ORIGEN_OPTIONS: list[dict[str, str]] = [
    {"key": "teams", "label": "Teams"},
    {"key": "correo", "label": "Correo"},
]

TRIBU_SQUAD_OPTIONS: list[dict[str, str]] = [
    {"key": "tribu_supply", "label": "Tribu Supply"},
    {"key": "tribu_lealtad", "label": "Tribu Lealtad"},
]

SOLICITANTE_OPTIONS: list[dict[str, str]] = []

KANBAN_COLUMNS: list[dict[str, Any]] = [
    {"key": "backlog", "label": "Backlog", "order": 1, "wip_limit": 3},
    {"key": "todo", "label": "To Do", "order": 2, "wip_limit": 3},
    {"key": "in_progress", "label": "In Progress", "order": 3, "wip_limit": 3},
    {"key": "done", "label": "Done", "order": 4, "wip_limit": 3},
    {"key": "detenido", "label": "Detenido", "order": 5, "wip_limit": 3},
]


def get_column_keys(kanban_columns: list[dict[str, Any]]) -> tuple[str, ...]:
    """Devuelve las claves de columnas ordenadas por order."""
    sorted_cols = sorted(
        (c for c in kanban_columns if isinstance(c, dict) and c.get("key")),
        key=lambda c: c.get("order", 99),
    )
    return tuple(c["key"] for c in sorted_cols)


def get_wip_limit(kanban_columns: list[dict[str, Any]], column_key: str) -> int:
    """Devuelve wip_limit para una columna. Default 3."""
    for c in kanban_columns:
        if isinstance(c, dict) and c.get("key") == column_key:
            return int(c.get("wip_limit", 3))
    return 3
