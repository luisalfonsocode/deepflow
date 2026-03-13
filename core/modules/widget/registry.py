"""Registro de módulos disponibles en el Widget principal."""

MODULES = [
    {
        "id": "taskboard",
        "title": "TaskBoard",
        "desc": "Tablero Kanban: tareas, WIP, transiciones",
        "icon": "📋",
        "enabled": True,
    },
    {
        "id": "reports",
        "title": "Reports",
        "desc": "Reportes y métricas",
        "icon": "📊",
        "enabled": True,
    },
    {
        "id": "alerts",
        "title": "Alerts",
        "desc": "Notificaciones y alertas",
        "icon": "🔔",
        "enabled": False,
    },
]


def get_module_index(module_id: str) -> int:
    """Devuelve el índice de un módulo por su id."""
    for i, m in enumerate(MODULES):
        if m["id"] == module_id:
            return i
    return 0
