"""Componente reutilizable de fila de tarea (nombre + duración en estado)."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy

from core.modules.taskboard.utils import format_duration_in_activity


class CompactTaskRow(QFrame):
    """Fila compacta de tarea: nombre + tiempo en estado. Clic abre detalle/edición."""

    def __init__(
        self,
        text: str,
        entered_at: str | None = None,
        on_click=None,
        max_name_len: int = 50,
        ticket: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.on_click = on_click
        self.setObjectName("compactTaskRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(6)

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

        duration = format_duration_in_activity(entered_at)
        dur_lbl = QLabel(duration)
        dur_lbl.setObjectName("compactTaskDuration")
        dur_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        dur_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        layout.addWidget(dur_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
        self.setFixedHeight(40)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            QTimer.singleShot(0, self.on_click)
        super().mousePressEvent(event)
