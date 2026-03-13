"""Componentes visuales compartidos entre módulos."""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class TitleBar(QWidget):
    """Barra de título con botón minimizar."""

    def __init__(self, on_minimize=None, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        self.label = QLabel("DeepFlow")
        layout.addWidget(self.label, 1)
        self._drag_pos = QPoint()

        if on_minimize:
            min_btn = QPushButton("−")
            min_btn.setObjectName("minimizeBtn")
            min_btn.setToolTip("Minimizar")
            min_btn.clicked.connect(on_minimize)
            layout.addWidget(min_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self._drag_pos
            win = self.window()
            if win:
                win.move(win.pos() + diff)
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def set_overcapacity(self, over: bool):
        self.setProperty("overcapacity", "true" if over else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if over:
            self.label.setText("WARNING: OVERCAPACITY")
        else:
            self.label.setText("DeepFlow")
