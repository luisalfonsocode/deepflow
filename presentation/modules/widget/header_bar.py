"""Barra principal: marca + navegación de módulos."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class HeaderBar(QWidget):
    """Barra superior con branding y acceso a módulos."""

    def __init__(self, modules: list, on_module_click, parent=None):
        super().__init__(parent)
        self.setObjectName("headerBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(10)

        # Marca
        brand = QLabel("DeepFlow")
        brand.setObjectName("headerBrand")
        layout.addWidget(brand)

        layout.addSpacing(24)

        # Navegación
        for mod in modules:
            btn = QPushButton(f"{mod['icon']}  {mod['title']}")
            btn.setObjectName("menuNavBtn" if mod["enabled"] else "menuNavBtnDisabled")
            btn.setProperty("module_id", mod["id"])
            btn.setEnabled(mod["enabled"])
            btn.setCursor(
                Qt.CursorShape.PointingHandCursor if mod["enabled"] else Qt.CursorShape.ArrowCursor
            )
            if mod.get("desc"):
                btn.setToolTip(mod["desc"])
            btn.clicked.connect(lambda checked=False, m=mod: on_module_click(m["id"]))
            layout.addWidget(btn)

        layout.addStretch()
