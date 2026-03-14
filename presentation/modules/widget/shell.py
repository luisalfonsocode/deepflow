"""Shell principal: dashboard con panel In Progress y modal de módulos."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget

from application.taskboard import BoardService
from presentation.config import MODULES
from presentation.composition import create_board_service, create_clipboard_provider
from presentation.modules.widget.header_bar import HeaderBar
from presentation.modules.widget.in_progress_compact import InProgressCompact
from presentation.style_loader import load_styles
from presentation.theme import ObjectNames, Layout


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

    def __init__(
        self,
        board_service: BoardService | None = None,
        clipboard_provider=None,
    ):
        """
        Args:
            board_service: BoardService inyectado. Si None, se crea desde composition root.
            clipboard_provider: Proveedor de portapapeles. Si None, se crea desde composition.
        """
        super().__init__()
        self._board = board_service or create_board_service()
        self._clipboard = clipboard_provider or create_clipboard_provider()

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

        # Dashboard
        dashboard_layout = QHBoxLayout()
        dashboard_layout.setContentsMargins(8, 6, 8, 8)
        dashboard_layout.setSpacing(0)

        self.in_progress = InProgressCompact(self._board, self._clipboard)
        self.in_progress.setMinimumWidth(340)
        dashboard_layout.addWidget(self.in_progress, 1)

        main_layout.addLayout(dashboard_layout)

        load_styles(self)

    def _on_module_click(self, module_id: str):
        module = next((m for m in MODULES if m["id"] == module_id), None)
        if not module or not module.get("enabled", True):
            return
        factory = module.get("factory")
        if not factory:
            return
        # Factory recibe dependencias según el módulo
        if module_id == "taskboard":
            content = factory(self._board, self._clipboard)
            modal = ModuleModal(module["title"], content, self)
            modal.finished.connect(self._on_taskboard_modal_closed)
        elif module_id in ("reports", "masters"):
            content = factory(self._board, self._clipboard)
            modal = ModuleModal(module["title"], content, self)
        else:
            content = factory()
            modal = ModuleModal(module["title"], content, self)
        modal.exec()

    def _on_taskboard_modal_closed(self):
        self.in_progress.refresh()
