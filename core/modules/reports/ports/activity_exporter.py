"""Contrato para exportación de actividades."""

from pathlib import Path
from typing import Any, Protocol


class ActivityExporter(Protocol):
    """Exporta actividades a un formato externo (Excel, CSV, etc.)."""

    def export(self, activities: list[dict[str, Any]], filepath: Path) -> bool:
        """
        Exporta la lista de actividades al archivo indicado.
        Retorna True si tuvo éxito.
        """
        ...
