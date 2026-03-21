"""Widgets del módulo TaskBoard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from domain.taskboard import format_task_duration
from domain.taskboard.utils import col_key_to_display
from presentation.shared.dnd import DeepFlowDropTargetMixin, make_task_mime_data
from presentation.theme import ObjectNames

if TYPE_CHECKING:
    from presentation.ports.clipboard_provider import ClipboardProvider


def _default_col_display(key: str) -> str:
    """Fallback cuando no se pasa display_label (ej. tests)."""
    return col_key_to_display(key)


class _ColumnHeader(DeepFlowDropTargetMixin, QWidget):
    """Cabecera de columna que también acepta drops."""

    def __init__(
        self,
        column_key: str,
        on_move: Callable[[str, str], None],
        show_create_button: bool = False,
        on_show_dialog: Callable[[str], None] | None = None,
        display_label: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.column_key = column_key
        self.on_move = on_move
        self.setObjectName("columnHeader")
        self.setAcceptDrops(True)

        header_layout = QHBoxLayout(self)
        header_layout.setContentsMargins(0, 0, 0, 4)

        title = display_label if display_label is not None else _default_col_display(column_key)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("columnTitle")
        header_layout.addWidget(self.title_label, 1)

        self.count_label = QLabel("0")
        self.count_label.setObjectName("columnCount")
        if column_key == "in_progress":
            self.count_label.setObjectName("wipCount")
        header_layout.addWidget(self.count_label)

        self.create_btn = None
        if show_create_button and on_show_dialog:
            create_btn = QPushButton("+")
            create_btn.setObjectName("createBtn")
            create_btn.setToolTip("Nueva actividad")
            create_btn.clicked.connect(lambda: on_show_dialog(""))
            header_layout.addWidget(create_btn)
            self.create_btn = create_btn


class _ColumnDropZone(DeepFlowDropTargetMixin, QFrame):
    """Zona de drop en espacio vacío de la columna."""

    def __init__(
        self,
        column_key: str,
        on_move: Callable[[str, str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.column_key = column_key
        self.on_move = on_move
        self.setAcceptDrops(True)
        self.setMinimumHeight(40)
        self.setObjectName("columnDropZone")


class TaskInputDialog(QDialog):
    """Modal para ingresar o editar actividad de tarea (máx. 50 caracteres)."""

    def __init__(self, clipboard_provider: "ClipboardProvider", edit_mode: bool = False, parent=None):
        super().__init__(parent)
        self._clipboard = clipboard_provider
        self.edit_mode = edit_mode
        self.setObjectName(ObjectNames.TASK_INPUT_DIALOG)
        self.setWindowTitle("Editar actividad" if edit_mode else "Nueva actividad")
        self.setMinimumSize(420, 180)
        self.resize(480, 180)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.text_edit = QLineEdit()
        self.text_edit.setObjectName(ObjectNames.TASK_INPUT_TEXT)
        self.text_edit.setPlaceholderText("Ingresa la actividad (máx. 50 caracteres)")
        self.text_edit.setMaxLength(50)
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        paste_btn = QPushButton("📋 Pegar")
        paste_btn.setObjectName("pasteBtn")
        paste_btn.setToolTip("Pegar del portapapeles")
        paste_btn.clicked.connect(self._do_paste)
        btn_layout.addWidget(paste_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Guardar" if edit_mode else "Crear")
        ok_btn.setObjectName("primaryBtn")
        ok_btn.setDefault(True)
        ok_btn.setAutoDefault(True)
        ok_btn.clicked.connect(self._do_accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def open_with_text(self, initial_text: str = ""):
        """Abre el diálogo con texto inicial y foco en el editor."""
        self.text_edit.setText(initial_text[:50])
        self.text_edit.setFocus(Qt.FocusReason.OtherFocusReason)
        self.exec()

    def _do_paste(self):
        text = self._clipboard.get_text()
        if text:
            self.text_edit.setText(text[:50])
            self.text_edit.setFocus(Qt.FocusReason.OtherFocusReason)

    def _do_accept(self):
        text = self.text_edit.text().strip()
        if not text:
            text = "Nueva tarea"
        self.accepted_text = text
        self.accept()

    def get_text(self) -> str:
        """Texto ingresado tras aceptar."""
        return getattr(self, "accepted_text", "") or self.text_edit.text().strip() or "Nueva tarea"


class TaskCard(DeepFlowDropTargetMixin, QFrame):
    """Tarjeta de tarea. Clic abre detalle; drag & drop entre columnas."""

    def __init__(
        self,
        task_id: str,
        name: str,
        column_key: str,
        on_move: Callable[[str, str], None],
        on_click: Callable[[str], None] | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
        ticket: str = "",
        prioridad: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.task_id = task_id
        self.column_key = column_key
        self.on_move = on_move
        self.on_click = on_click
        self.setObjectName(ObjectNames.TASK_CARD)
        self.setProperty("column", column_key)
        self.setProperty("prioridad", "true" if prioridad else "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)

        if prioridad:
            prioridad_label = QLabel("⭐")
            prioridad_label.setObjectName("taskPriority")
            layout.addWidget(prioridad_label, 0)
        if ticket:
            ticket_label = QLabel(ticket)
            ticket_label.setObjectName("taskTicket")
            layout.addWidget(ticket_label, 0)
        display_name = name[:50] + ("…" if len(name) > 50 else "")
        self.name_label = QLabel(display_name)
        self.name_label.setObjectName("taskName")
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumHeight(120)
        layout.addWidget(self.name_label, 1)

        duration_str = format_task_duration(started_at, finished_at, column_key)
        self.duration_label = QLabel(duration_str)
        self.duration_label.setObjectName("taskDuration")
        layout.addWidget(self.duration_label)

        self.setAcceptDrops(True)
        self.setMinimumHeight(36)

    def _should_accept_drop(self, task_id: str) -> bool:
        return task_id != self.task_id

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.pos()
            self.drag_started = False
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.on_click
            and not getattr(self, "drag_started", False)
        ):
            self.on_click(self.task_id)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if (
            hasattr(self, "drag_start")
            and hasattr(self, "drag_started")
            and not self.drag_started
            and event.buttons() & Qt.MouseButton.LeftButton
            and (event.pos() - self.drag_start).manhattanLength() > 15
        ):
            self.drag_started = True
            mime = QMimeData()
            mime.setText(make_task_mime_data(self.task_id))
            drag = QDrag(self)
            drag.setMimeData(mime)

            pixmap = self.grab()
            if not pixmap.isNull():
                drag.setPixmap(pixmap)
                drag.setHotSpot(event.pos() - self.drag_start)

            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(event)


class ColumnWidget(DeepFlowDropTargetMixin, QWidget):
    """Columna del tablero con cabecera y área de tareas."""

    def __init__(
        self,
        column_key: str,
        on_move: Callable[[str, str], None],
        show_create_button: bool = False,
        on_show_dialog: Callable[[str], None] | None = None,
        display_label: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.column_key = column_key
        self.on_move = on_move
        self.setObjectName("column")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        header = _ColumnHeader(
            column_key,
            on_move,
            show_create_button=show_create_button,
            on_show_dialog=on_show_dialog,
            display_label=display_label,
        )
        self.title_label = header.title_label
        self.count_label = header.count_label
        self.create_btn = header.create_btn
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setContentsMargins(0, 0, 4, 0)
        self.tasks_layout.setSpacing(2)

        drop_zone = _ColumnDropZone(column_key, on_move)
        self.tasks_layout.addWidget(drop_zone, 1)

        scroll.setWidget(self.tasks_widget)
        layout.addWidget(scroll)
