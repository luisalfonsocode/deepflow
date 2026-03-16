"""Componente reutilizable de fila de tarea (nombre + duración en estado)."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy

from domain.taskboard.utils import format_task_duration


class CompactTaskRow(QFrame):
    """Fila compacta de tarea: nombre + duración (started_at → ahora o finished_at)."""

    def __init__(
        self,
        text: str,
        started_at: str | None = None,
        finished_at: str | None = None,
        column_key: str = "in_progress",
        on_click=None,
        max_name_len: int = 50,
        ticket: str = "",
        section: str = "in_progress",
        parent=None,
    ):
        super().__init__(parent)
        self.on_click = on_click
        self.setObjectName("compactTaskRow")
        self.setProperty("section", section)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        if ticket:
            ticket_lbl = QLabel(ticket)
            ticket_lbl.setObjectName("compactTaskTicket")
            layout.addWidget(ticket_lbl, 0)

        display_name = text[:max_name_len] + ("…" if len(text) > max_name_len else "")
        lbl = QLabel(display_name)
        lbl.setObjectName("compactTaskName")
        lbl.setWordWrap(False)
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(lbl, 1)

        duration = format_task_duration(started_at, finished_at, column_key)
        dur_lbl = QLabel(duration)
        dur_lbl.setObjectName("compactTaskDuration")
        dur_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        dur_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        layout.addWidget(dur_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
        self.setFixedHeight(34)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            QTimer.singleShot(0, self.on_click)
        super().mousePressEvent(event)
