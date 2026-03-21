"""
DeepFlow - Punto de entrada.
Separa lógica (core) de interfaz (ui) para facilitar cambios.
"""

import os
import sys

# Reducir avisos de Qt/macOS (fuentes, IMK)
os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

from config.logging_config import setup_logging

setup_logging()

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication

from config.base import RESOURCE_ROOT, PROJECT_ROOT
from presentation.composition import create_board_service, create_clipboard_provider
from presentation.modules.widget import MainShell
from presentation.style_loader import load_styles


def _find_icon_path() -> Path | None:
    """Busca icono para la ventana. En Mac prefiere icns (Retina); en Windows ico."""
    for base in (RESOURCE_ROOT, PROJECT_ROOT):
        assets = base / "assets"
        if sys.platform == "darwin":
            order = ("icon.icns", "icon.png", "icon.ico")  # icns nítido en Retina
        elif sys.platform == "win32":
            order = ("icon.ico", "icon.png", "icon.icns")  # ico nativo en Windows
        else:
            order = ("icon.png", "icon.ico", "icon.icns")
        for name in order:
            p = assets / name
            if p.exists():
                return p
    return None


def _default_font() -> QFont:
    """Fuente del sistema por plataforma; misma apariencia en Mac y Windows."""
    if sys.platform == "darwin":
        return QFont("Helvetica Neue", 13)
    if sys.platform == "win32":
        return QFont("Segoe UI", 13)
    return QFont(13)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DeepFlow")
    app.setFont(_default_font())
    icon_path = _find_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(str(icon_path)))
    # Fusion respeta mejor la paleta y QSS en tema oscuro que el estilo nativo de macOS
    app.setStyle("Fusion")
    load_styles(app)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f8fafc"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f1f5f9"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#94a3b8"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563eb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    board = create_board_service()
    clipboard = create_clipboard_provider()
    shell = MainShell(board_service=board, clipboard_provider=clipboard)
    app.aboutToQuit.connect(board.shutdown)

    shell.setObjectName("mainWindow")
    shell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    shell.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
