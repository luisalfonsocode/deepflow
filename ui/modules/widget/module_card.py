"""Tarjeta de módulo en el selector del Widget."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class ModuleCard(QFrame):
    """Tarjeta de módulo en el selector."""

    def __init__(self, module: dict, on_click, parent=None):
        super().__init__(parent)
        self.module = module
        self.on_click = on_click
        self.setObjectName("moduleCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if not module["enabled"]:
            self.setProperty("disabled", "true")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        icon_lbl = QLabel(module["icon"])
        icon_lbl.setObjectName("moduleCardIcon")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)
        title_lbl = QLabel(module["title"])
        title_lbl.setObjectName("moduleCardTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)
        desc_lbl = QLabel(module["desc"])
        desc_lbl.setObjectName("moduleCardDesc")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        self.setMinimumSize(140, 120)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.module["enabled"]:
            self.on_click(self.module["id"])
        super().mousePressEvent(event)
