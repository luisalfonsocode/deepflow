"""Módulos de UI: Widget (shell), TaskBoard, Reports, Alerts."""

from presentation.modules.widget import MainShell
from presentation.modules.taskboard import TaskBoardView
from presentation.modules.reports import ReportsView
from presentation.modules.alerts import AlertsView

__all__ = ["MainShell", "TaskBoardView", "ReportsView", "AlertsView"]
