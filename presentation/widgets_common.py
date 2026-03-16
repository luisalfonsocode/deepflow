"""Widgets compartidos con comportamiento mejorado."""

from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QComboBox


class ComboBoxNoWheelUnfocused(QComboBox):
    """QComboBox que ignora la rueda del ratón cuando no está seleccionado.
    Evita que el combo cambie de valor al hacer scroll mientras se pasa el mouse por encima.
    """

    def wheelEvent(self, event: QWheelEvent):
        if not self.hasFocus():
            event.ignore()
            return
        super().wheelEvent(event)
