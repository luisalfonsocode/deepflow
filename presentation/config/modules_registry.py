"""
Registro de módulos con factory de vista.
Cada módulo define id, título, descripción, icono y una función que crea el contenido.
"""

from typing import Callable, Any

ModuleDef = dict[str, Any]
ViewFactory = Callable[[], Any]  # Retorna QWidget


def _taskboard_factory(board, clipboard):
    from presentation.modules.taskboard import TaskBoardView
    return TaskBoardView(board, clipboard)


def _reports_factory(board, clipboard):
    from presentation.presenters.reports_presenter import ReportsPresenter
    from presentation.modules.reports import ReportsView
    presenter = ReportsPresenter(board)
    return ReportsView(presenter, clipboard_provider=clipboard)


def _masters_factory(board, clipboard):
    from presentation.presenters.masters_presenter import MastersPresenter
    from presentation.modules.masters import MastersView
    presenter = MastersPresenter(board)
    return MastersView(presenter)


def _alerts_factory():
    from presentation.modules.alerts import AlertsView
    return AlertsView()


MODULES = [
    {
        "id": "taskboard",
        "title": "TaskBoard",
        "desc": "Tablero Kanban: tareas, WIP, transiciones",
        "icon": "📋",
        "enabled": True,
        "factory": _taskboard_factory,
    },
    {
        "id": "reports",
        "title": "Reports",
        "desc": "Reportes y métricas",
        "icon": "📊",
        "enabled": True,
        "factory": _reports_factory,
    },
    {
        "id": "masters",
        "title": "Maestros",
        "desc": "Tribu, Solicitante, Canal de reporte, Categoría",
        "icon": "⚙️",
        "enabled": True,
        "factory": _masters_factory,
    },
    {
        "id": "alerts",
        "title": "Alerts",
        "desc": "Notificaciones y alertas",
        "icon": "🔔",
        "enabled": False,
        "factory": _alerts_factory,
    },
]
