"""Implementación del portapapeles usando Qt."""

from PyQt6.QtWidgets import QApplication


class QtClipboardProvider:
    """Provee texto del portapapeles de Qt."""

    def get_text(self) -> str:
        return (QApplication.clipboard().text() or "").strip()

