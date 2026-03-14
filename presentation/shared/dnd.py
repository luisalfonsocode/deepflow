"""
Helper para drag & drop de tareas (MIME deepflow:task_id).
Reduce duplicación entre TaskCard, ColumnWidget, _ColumnHeader, _ColumnDropZone.
"""

from PyQt6.QtCore import QMimeData

from presentation.theme.constants import MIME_TASK_PREFIX


def is_deepflow_drag(mime_data: QMimeData | None) -> bool:
    """Indica si el MIME contiene una tarea DeepFlow."""
    if not mime_data or not mime_data.hasText():
        return False
    return mime_data.text().startswith(MIME_TASK_PREFIX)


def extract_task_id_from_mime(mime_data: QMimeData) -> str | None:
    """Extrae el task_id del MIME. Retorna None si no es deepflow."""
    if not is_deepflow_drag(mime_data):
        return None
    return mime_data.text().replace(MIME_TASK_PREFIX, "").strip()


def make_task_mime_data(task_id: str) -> str:
    """Genera el texto MIME para arrastrar una tarea."""
    return f"{MIME_TASK_PREFIX}{task_id}"


class DeepFlowDropTargetMixin:
    """
    Mixin para widgets que aceptan drop de tareas.
    Requiere: self.column_key, self.on_move (o equivalente).
    Para TaskCard: además self.task_id y filtrar drops del mismo task.
    """

    def _get_column_key(self) -> str:
        return getattr(self, "column_key", "")

    def _get_on_move(self):
        return getattr(self, "on_move", None)

    def _should_accept_drop(self, task_id: str) -> bool:
        """Override en TaskCard para rechazar drop sobre la propia tarea."""
        return True

    def dragEnterEvent(self, event):
        if not is_deepflow_drag(event.mimeData()):
            return
        task_id = extract_task_id_from_mime(event.mimeData())
        if task_id and self._should_accept_drop(task_id):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if not is_deepflow_drag(event.mimeData()):
            return
        task_id = extract_task_id_from_mime(event.mimeData())
        if task_id and self._should_accept_drop(task_id):
            event.acceptProposedAction()

    def dropEvent(self, event):
        task_id = extract_task_id_from_mime(event.mimeData())
        on_move = self._get_on_move()
        col = self._get_column_key()
        if task_id and on_move and self._should_accept_drop(task_id):
            on_move(task_id, col)
        event.acceptProposedAction()
