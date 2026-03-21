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
    """Modal con el contenido de un módulo. Hereda estilo del menú principal."""

    def __init__(self, title: str, content: QWidget, parent=None):
        super().__init__(parent)
        self.setObjectName("moduleModal")
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

        # Área principal: panel centrado, sin espacio vacío
        content = QWidget()
        content.setObjectName("mainContentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 8, 24, 12)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.in_progress = InProgressCompact(self._board, self._clipboard)
        self.in_progress.setFixedWidth(512)
        content_layout.addWidget(self.in_progress, 0, Qt.AlignmentFlag.AlignHCenter)

        main_layout.addWidget(content, 0)

        load_styles(self)

    def _on_module_click(self, module_id: str):
        module = next((m for m in MODULES if m["id"] == module_id), None)
        if not module or not module.get("enabled", True):
            return
        factory = module.get("factory")
        if not factory:
            return
        # Factory recibe dependencias según el módulo
        window_title = f"DeepFlow — {module['title']}"
        if module_id == "taskboard":
            content = factory(self._board, self._clipboard)
            modal = ModuleModal(window_title, content, self)
            modal.finished.connect(self._on_taskboard_modal_closed)
        elif module_id in ("reports", "masters"):
            content = factory(self._board, self._clipboard)
            modal = ModuleModal(window_title, content, self)
        else:
            content = factory()
            modal = ModuleModal(window_title, content, self)
        modal.exec()

    def _on_taskboard_modal_closed(self):
        self.in_progress.refresh()
