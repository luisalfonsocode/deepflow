"""Columna 4: In Progress y Detenidas. Dos filas clickeables, al clic se despliegan los tickets."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from adapters.ui import QtClipboardProvider
from ui.modules.taskboard import CompactTaskRow, open_task_detail
from ui.modules.taskboard.widgets import TaskInputDialog
from ui.style_loader import load_styles


class InProgressCompact(QWidget):
    """Columna con In Progress y Detenidas. Clic en una fila despliega sus tickets."""

    def __init__(self, board, parent=None):
        super().__init__(parent)
        self.board = board
        self.setObjectName("inProgressCompact")
        self._expanded_section = "in_progress"  # por defecto In Progress desplegado
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Fila 1: Detenidas
        self.detenidas_header = _SectionHeader(
            "Detenidas",
            on_click=lambda: self._select_section("detenido"),
            section="detenidas",
        )
        layout.addWidget(self.detenidas_header)

        # Fila 2: In Progress
        add_btn = QPushButton("+")
        add_btn.setObjectName("compactCreateBtn")
        add_btn.setToolTip("Nueva tarea (inicia en In Progress)")
        add_btn.clicked.connect(self._on_add_task)
        self.in_progress_header = _SectionHeader(
            "In Progress",
            on_click=lambda: self._select_section("in_progress"),
            right_widget=add_btn,
            section="in_progress",
        )
        layout.addWidget(self.in_progress_header)

        # Área de tickets: máx 3 tareas, altura fija, alineado al top
        self.tickets_container = QWidget()
        self.tickets_layout = QVBoxLayout(self.tickets_container)
        self.tickets_layout.setContentsMargins(0, 0, 0, 0)
        self.tickets_layout.setSpacing(2)
        self.tickets_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        tickets_wrapper = QWidget()
        tickets_wrapper.setObjectName("ticketsScrollWrapper")
        tickets_wrapper.setMinimumHeight(132)  # 3 filas × 40px + spacing
        wrapper_layout = QVBoxLayout(tickets_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper_layout.addWidget(self.tickets_container, 0, Qt.AlignmentFlag.AlignTop)
        wrapper_layout.addStretch()

        scroll = QScrollArea()
        scroll.setObjectName("widgetTicketsScroll")
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedHeight(140)
        scroll.setWidget(tickets_wrapper)
        layout.addWidget(scroll)

        self._refresh()

    def _select_section(self, section: str):
        self._expanded_section = section
        self._refresh()

    def _refresh(self):
        while self.tickets_layout.count():
            item = self.tickets_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks_in_progress = self.board.data.get("in_progress", [])
        tasks_detenidas = self.board.data.get("detenido", [])

        self.in_progress_header.set_count(len(tasks_in_progress))
        self.in_progress_header.set_selected(self._expanded_section == "in_progress")

        self.detenidas_header.set_count(len(tasks_detenidas))
        self.detenidas_header.set_selected(self._expanded_section == "detenido")

        add_btn = getattr(self.in_progress_header, "add_btn", None)
        if add_btn:
            add_btn.setEnabled(self.board.can_add_to("in_progress"))

        tasks = tasks_in_progress if self._expanded_section == "in_progress" else tasks_detenidas
        tasks = tasks[:3]  # Máximo 3 tareas en el widget
        if tasks:
            for t in tasks:
                row = CompactTaskRow(
                    t.get("name", ""),
                    entered_at=t.get("entered_at") or t.get("started_at"),
                    on_click=lambda tid=t["id"]: self._on_task_click(tid),
                    max_name_len=50,
                    ticket=t.get("ticket", ""),
                )
                self.tickets_layout.addWidget(row)
        else:
            msg = "No hay tareas en progreso" if self._expanded_section == "in_progress" else "No hay tareas detenidas"
            empty = QLabel(msg)
            empty.setObjectName("emptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tickets_layout.addWidget(empty)

    def refresh(self):
        """Actualiza la lista de tareas en progreso."""
        self.board.load()
        self._refresh()

    def _on_task_click(self, task_id: str):
        def deferred_refresh():
            QTimer.singleShot(100, self._refresh)

        open_task_detail(
            self.board, task_id, on_close_callback=deferred_refresh, parent=self.window()
        )

    def _on_add_task(self):
        if not self.board.can_add_to("in_progress"):
            return
        dialog = TaskInputDialog(
            clipboard_provider=QtClipboardProvider(),
            parent=self.window(),
        )
        load_styles(dialog)
        dialog.open_with_text("")
        if dialog.result() == dialog.DialogCode.Accepted:
            text = dialog.get_text()
            if self.board.create_task_in(text, "in_progress"):
                self._refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()


class _SectionHeader(QFrame):
    """Fila de sección (In Progress o Detenidas). Clic despliega sus tickets."""

    def __init__(self, title: str, on_click=None, right_widget=None, section: str = "", parent=None):
        super().__init__(parent)
        self.on_click = on_click
        self.add_btn = right_widget
        self.setObjectName("sectionHeader")
        if section:
            self.setProperty("section", section)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)
        self.label = QLabel(title)
        self.label.setObjectName("sectionHeaderLabel")
        layout.addWidget(self.label)
        self.count_label = QLabel("0")
        self.count_label.setObjectName("sectionHeaderCount")
        layout.addWidget(self.count_label)
        if right_widget:
            layout.addWidget(right_widget)
        layout.addStretch()
        self.arrow = QLabel("▼")
        self.arrow.setObjectName("sectionHeaderArrow")
        layout.addWidget(self.arrow)

    def set_count(self, n: int):
        self.count_label.setText(str(n))

    def set_selected(self, selected: bool):
        self.setProperty("selected", "true" if selected else "false")
        self.arrow.setText("▼" if selected else "›")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            self.on_click()
        super().mousePressEvent(event)
