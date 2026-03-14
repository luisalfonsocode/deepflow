"""Vista resumen del TaskBoard: lista de tareas In Progress."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from application.taskboard import BoardService
from presentation.composition import create_board_service
from presentation.modules.taskboard.dialogs import open_task_detail
from presentation.style_loader import load_styles


class TaskSummaryRow(QFrame):
    """Fila de tarea en el resumen. Clic abre detalle."""

    def __init__(self, task_id: str, name: str, on_click, ticket: str = "", parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.on_click = on_click
        self.setObjectName("taskSummaryRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Placeholder semáforo (se implementará después)
        semaphore = QLabel("○")
        semaphore.setObjectName("semaphorePlaceholder")
        semaphore.setFixedWidth(20)
        layout.addWidget(semaphore)

        if ticket:
            ticket_lbl = QLabel(ticket)
            ticket_lbl.setObjectName("taskSummaryTicket")
            layout.addWidget(ticket_lbl, 0)

        name_lbl = QLabel(name[:80] + ("..." if len(name) > 80 else name))
        name_lbl.setObjectName("taskSummaryName")
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl, 1)

        self.setMinimumHeight(32)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.task_id)
        super().mousePressEvent(event)


class TaskBoardSummaryView(QWidget):
    """Resumen: lista de tareas In Progress con semáforo. Clic abre detalle."""

    def __init__(self, board: BoardService | None = None, parent=None):
        super().__init__(parent)
        self.board = board or create_board_service()
        self.setObjectName("taskboardSummaryView")
        self._build_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Tareas en progreso")
        title.setObjectName("summaryTitle")
        self.main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(2)
        scroll.setWidget(self.list_widget)
        self.main_layout.addWidget(scroll, 1)

    def _on_task_click(self, task_id: str):
        def on_close():
            self.board.load()
            self._refresh_list()

        open_task_detail(
            self.board, task_id, on_close_callback=on_close, parent=self.window()
        )
        self.board.load()
        self._refresh_list()

    def _refresh_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = self.board.data.get("in_progress", [])
        if not tasks:
            empty = QLabel("No hay tareas en progreso")
            empty.setObjectName("emptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty)
        else:
            for t in tasks:
                row = TaskSummaryRow(
                    t["id"],
                    t.get("name", ""),
                    self._on_task_click,
                    ticket=t.get("ticket", ""),
                )
                self.list_layout.addWidget(row)

    def showEvent(self, event):
        super().showEvent(event)
        self.board.load()
        self._refresh_list()
