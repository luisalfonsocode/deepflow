"""Protocolo para acceso al portapapeles. Permite inyectar dependencia en tests."""

from typing import Protocol


class ClipboardProvider(Protocol):
    """Provee texto del portapapeles."""

    def get_text(self) -> str:
        """Retorna el texto actual del portapapeles."""
        ...
