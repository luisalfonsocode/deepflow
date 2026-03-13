"""
Ventana del módulo TaskBoard (modo standalone).
Para uso embebido, usar TaskBoardView desde MainShell.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from core.modules.taskboard import BoardService
from ui.composition import create_board_service
from ui.widgets import TitleBar
from ui.modules.taskboard import TaskBoardView
from ui.style_loader import load_styles


class MonoFlowWindow(QMainWindow):
    """Ventana standalone del TaskBoard (con barra de título)."""

    def __init__(self, board: BoardService | None = None):
        super().__init__()
        self._board = board or create_board_service()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowTitle("DeepFlow - TaskBoard")
        self.setMinimumSize(520, 320)
        self.resize(560, 380)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar = TitleBar(on_minimize=self.showMinimized)
        self.taskboard = TaskBoardView(self._board)
        self.taskboard.overcapacity_changed.connect(self.title_bar.set_overcapacity)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.taskboard)
        load_styles(self)
