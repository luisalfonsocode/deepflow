"""
DeepFlow - Punto de entrada.
Separa lógica (core) de interfaz (ui) para facilitar cambios.
"""

import os
import sys

# Reducir avisos de Qt/macOS (fuentes, IMK)
os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

from ui.modules.widget import MainShell
from ui.style_loader import load_styles


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DeepFlow")
    # Fusion respeta mejor la paleta y QSS en tema oscuro que el estilo nativo de macOS
    app.setStyle("Fusion")
    load_styles(app)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#2a2b2c"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e6e7e9"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#2e2f31"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#323335"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e6e7e9"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e6e7e9"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#6e7176"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#007acc"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    shell = MainShell()
    shell.setObjectName("mainWindow")
    shell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    shell.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
