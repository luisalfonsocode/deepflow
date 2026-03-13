"""Barra del header con botones de menú para módulos."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class HeaderBar(QWidget):
    """Barra de header con botones pequeños tipo menú."""

    def __init__(self, modules: list, on_module_click, parent=None):
        super().__init__(parent)
        self.setObjectName("headerBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        for mod in modules:
            btn = QPushButton(f"{mod['icon']} {mod['title']}")
            btn.setObjectName("menuBtn" if mod["enabled"] else "menuBtnDisabled")
            btn.setProperty("module_id", mod["id"])
            btn.setEnabled(mod["enabled"])
            btn.setCursor(Qt.CursorShape.PointingHandCursor if mod["enabled"] else Qt.CursorShape.ArrowCursor)
            btn.clicked.connect(lambda checked=False, m=mod: on_module_click(m["id"]))
            layout.addWidget(btn)

        layout.addStretch()
