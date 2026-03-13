"""Shell principal: dashboard con 4 columnas. Por ahora un único panel con contenido."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFrame, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget

from core.modules.taskboard import BoardService
from core.modules.widget import MODULES
from ui.composition import create_board_service
from ui.modules.widget.header_bar import HeaderBar
from ui.modules.widget.in_progress_compact import InProgressCompact
from ui.modules.taskboard import TaskBoardView
from ui.modules.reports import ReportsView
from ui.modules.alerts import AlertsView
from ui.presenters.reports_presenter import ReportsPresenter
from ui.style_loader import load_styles
from ui.theme import ObjectNames, Layout

class ModuleModal(QDialog):
    """Modal con el contenido de un módulo. Solo UI."""

    def __init__(self, title: str, content: QWidget, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(Layout.MODAL_MIN_WIDTH, Layout.MODAL_MIN_HEIGHT)
        self.resize(Layout.MODAL_DEFAULT_WIDTH, Layout.MODAL_DEFAULT_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(content)
        load_styles(self)


class MainShell(QMainWindow):
    """Dashboard con 4 columnas. Por ahora un único panel con contenido (In Progress)."""

    def __init__(self, board_service: BoardService | None = None):
        """
        Args:
            board_service: BoardService inyectado. Si None, se crea desde composition root.
        """
        super().__init__()
        self._board = board_service or create_board_service()

        self.setWindowTitle("DeepFlow")
        self.setMinimumSize(Layout.SHELL_MIN_WIDTH, Layout.SHELL_MIN_HEIGHT)
        self.resize(Layout.SHELL_DEFAULT_WIDTH, Layout.SHELL_DEFAULT_HEIGHT)

        central = QWidget()
        central.setObjectName(ObjectNames.MAIN_CENTRAL)
        central.setAutoFillBackground(True)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(HeaderBar(MODULES, self._on_module_click))

        # Dashboard: por ahora un único panel (In Progress). Las otras columnas se añadirán después.
        dashboard_layout = QHBoxLayout()
        dashboard_layout.setContentsMargins(8, 8, 8, 8)
        dashboard_layout.setSpacing(0)

        self.in_progress = InProgressCompact(self._board)
        dashboard_layout.addWidget(self.in_progress, 1)

        main_layout.addLayout(dashboard_layout)

        load_styles(self)

    def _on_module_click(self, module_id: str):
        if module_id == "taskboard":
            content = TaskBoardView(self._board)
            modal = ModuleModal("TaskBoard", content, self)
            modal.finished.connect(self._on_taskboard_modal_closed)
            modal.exec()
        elif module_id == "reports":
            presenter = ReportsPresenter(self._board)
            content = ReportsView(presenter)
            modal = ModuleModal("Reports", content, self)
            modal.exec()
        elif module_id == "alerts":
            content = AlertsView()
            modal = ModuleModal("Alerts", content, self)
            modal.exec()

    def _on_taskboard_modal_closed(self):
        self.in_progress.refresh()
