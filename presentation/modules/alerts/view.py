"""Vista del módulo Alerts."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AlertsView(QWidget):
    """Vista del módulo Alerts. Placeholder hasta implementación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modulePlaceholder")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_lbl = QLabel("Alerts")
        title_lbl.setObjectName("placeholderTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("Notificaciones y alertas de WIP.\nPróximamente.")
        desc_lbl.setObjectName("placeholderDesc")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
