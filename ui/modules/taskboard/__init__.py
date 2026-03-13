"""Módulo TaskBoard: vista Kanban, widgets y diálogos."""

from ui.modules.taskboard.dialogs import TaskDetailDialog, open_task_detail
from ui.modules.taskboard.task_row import CompactTaskRow
from ui.modules.taskboard.view import TaskBoardView

__all__ = [
    "CompactTaskRow",
    "open_task_detail",
    "TaskBoardView",
    "TaskDetailDialog",
]
