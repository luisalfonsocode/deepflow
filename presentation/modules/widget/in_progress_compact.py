"""Dashboard de pendientes: dos secciones visibles (En progreso + Detenidas)."""

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

from presentation.modules.taskboard import CompactTaskRow, open_task_detail, open_task_create
from presentation.theme import ObjectNames

_MAX_TASKS_PER_SECTION = 4


class InProgressCompact(QWidget):
    """Dashboard: En progreso y Detenidas visibles a la vez."""

    def __init__(self, board, clipboard_provider, parent=None):
        super().__init__(parent)
        self.board = board
        self._clipboard = clipboard_provider
        self.setObjectName(ObjectNames.IN_PROGRESS_COMPACT)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        header = QFrame()
        header.setObjectName("widgetHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        title = QLabel("Tus pendientes")
        title.setObjectName("widgetHeaderTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self._header_add_btn = QPushButton("+")
        self._header_add_btn.setObjectName("compactCreateBtn")
        self._header_add_btn.setToolTip("Nueva actividad")
        self._header_add_btn.clicked.connect(self._on_add_task)
        header_layout.addWidget(self._header_add_btn)
        self.summary_label = QLabel("0 activas · 0 detenidas")
        self.summary_label.setObjectName("widgetHeaderSummary")
        header_layout.addWidget(self.summary_label)
        layout.addWidget(header)

        card = QFrame()
        card.setObjectName("widgetCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("widgetTicketsScroll")
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(180)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

        # Sección En progreso
        prog_header = QFrame()
        prog_header.setObjectName("sectionBlock")
        prog_header.setProperty("section", "in_progress")
        prog_layout = QHBoxLayout(prog_header)
        prog_layout.setContentsMargins(10, 8, 10, 6)
        prog_layout.setSpacing(6)
        prog_label = QLabel("En progreso")
        prog_label.setObjectName("sectionBlockLabel")
        prog_layout.addWidget(prog_label)
        self._prog_count = QLabel("0")
        self._prog_count.setObjectName("sectionBlockCount")
        prog_layout.addWidget(self._prog_count)
        prog_layout.addStretch()
        self._add_btn = QPushButton("+")
        self._add_btn.setObjectName("compactCreateBtn")
        self._add_btn.setToolTip("Nueva tarea")
        self._add_btn.clicked.connect(self._on_add_task)
        prog_layout.addWidget(self._add_btn)
        self._content_layout.addWidget(prog_header)

        self._prog_list = QWidget()
        self._prog_list.setObjectName("sectionContent")
        self._prog_list.setProperty("section", "in_progress")
        self._prog_layout = QVBoxLayout(self._prog_list)
        self._prog_layout.setContentsMargins(10, 0, 10, 10)
        self._prog_layout.setSpacing(3)
        self._prog_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_layout.addWidget(self._prog_list)

        # Sección Detenidas
        det_header = QFrame()
        det_header.setObjectName("sectionBlock")
        det_header.setProperty("section", "detenidas")
        det_layout = QHBoxLayout(det_header)
        det_layout.setContentsMargins(10, 10, 10, 6)
        det_layout.setSpacing(6)
        det_label = QLabel("Detenidas")
        det_label.setObjectName("sectionBlockLabel")
        det_layout.addWidget(det_label)
        self._det_count = QLabel("0")
        self._det_count.setObjectName("sectionBlockCount")
        det_layout.addWidget(self._det_count)
        det_layout.addStretch()
        self._content_layout.addWidget(det_header)

        self._det_list = QWidget()
        self._det_list.setObjectName("sectionContent")
        self._det_list.setProperty("section", "detenidas")
        self._det_layout = QVBoxLayout(self._det_list)
        self._det_layout.setContentsMargins(10, 0, 10, 10)
        self._det_layout.setSpacing(3)
        self._det_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_layout.addWidget(self._det_list)

        scroll.setWidget(self._content)
        card_layout.addWidget(scroll, 1)
        layout.addWidget(card, 1)

        self._refresh()

    def _refresh(self):
        self._clear_layout(self._prog_layout)
        self._clear_layout(self._det_layout)

        tasks_progress = self.board.data.get("in_progress", [])
        tasks_detenidas = self.board.data.get("detenido", [])

        self.summary_label.setText(f"{len(tasks_progress)} activas · {len(tasks_detenidas)} detenidas")
        self._prog_count.setText(str(len(tasks_progress)))
        self._det_count.setText(str(len(tasks_detenidas)))

        can_add = self.board.can_add_to("in_progress")
        self._add_btn.setEnabled(can_add)
        self._header_add_btn.setEnabled(can_add)

        for t in tasks_progress[:_MAX_TASKS_PER_SECTION]:
            row = CompactTaskRow(
                t.get("name", ""),
                entered_at=t.get("entered_at") or t.get("started_at"),
                on_click=lambda tid=t["id"]: self._on_task_click(tid),
                max_name_len=50,
                ticket=t.get("ticket", ""),
                section="in_progress",
            )
            self._prog_layout.addWidget(row)
        if len(tasks_progress) == 0:
            empty = QLabel("Sin tareas · Clic + para crear")
            empty.setObjectName(ObjectNames.EMPTY_STATE)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._prog_layout.addWidget(empty)
        elif len(tasks_progress) > _MAX_TASKS_PER_SECTION:
            more = QLabel(f"+{len(tasks_progress) - _MAX_TASKS_PER_SECTION} más")
            more.setObjectName("sectionMoreLabel")
            self._prog_layout.addWidget(more)

        for t in tasks_detenidas[:_MAX_TASKS_PER_SECTION]:
            row = CompactTaskRow(
                t.get("name", ""),
                entered_at=t.get("entered_at") or t.get("started_at"),
                on_click=lambda tid=t["id"]: self._on_task_click(tid),
                max_name_len=50,
                ticket=t.get("ticket", ""),
                section="detenidas",
            )
            self._det_layout.addWidget(row)
        if len(tasks_detenidas) == 0:
            empty = QLabel("Sin tareas detenidas")
            empty.setObjectName(ObjectNames.EMPTY_STATE)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._det_layout.addWidget(empty)
        elif len(tasks_detenidas) > _MAX_TASKS_PER_SECTION:
            more = QLabel(f"+{len(tasks_detenidas) - _MAX_TASKS_PER_SECTION} más")
            more.setObjectName("sectionMoreLabel")
            self._det_layout.addWidget(more)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
        open_task_create(
            self.board,
            "in_progress",
            on_close_callback=self._refresh,
            parent=self.window(),
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()


