"""Módulo TaskBoard: vista Kanban, widgets y diálogos."""

from presentation.modules.taskboard.dialogs import TaskDetailDialog, open_task_detail, open_task_create
from presentation.modules.taskboard.task_row import CompactTaskRow
from presentation.modules.taskboard.view import TaskBoardView

__all__ = [
    "CompactTaskRow",
    "open_task_detail",
    "open_task_create",
    "TaskBoardView",
    "TaskDetailDialog",
]
