"""
Exportador de actividades a Excel.
Implementa la lógica de exportación separada de la UI.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _ensure_openpyxl() -> bool:
    """Verifica/openpyxl. Instala si no está. Retorna True si está disponible."""
    try:
        from openpyxl import Workbook  # noqa: F401
        return True
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "openpyxl"],
                check=True,
                capture_output=True,
                timeout=60,
            )
            return True
        except Exception:
            return False


class ExcelActivityExporter:
    """Exporta actividades a archivo Excel (.xlsx)."""

    def export(self, activities: list[dict[str, Any]], filepath: Path) -> bool:
        """
        Exporta actividades a Excel.
        Retorna True si tuvo éxito.
        """
        if not _ensure_openpyxl():
            return False

        from openpyxl import Workbook
        from openpyxl.styles import Font
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        ws = wb.active
        ws.title = "Actividades"

        headers = [
            "ID", "Actividad", "Estado", "Subtareas (JSON)",
            "Inicio en columna", "Inicio In Progress", "Fin (Done)"
        ]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = Font(bold=True)

        for row_idx, t in enumerate(activities, 2):
            ws.cell(row=row_idx, column=1, value=t.get("id", ""))
            ws.cell(row=row_idx, column=2, value=t.get("name", ""))
            ws.cell(row=row_idx, column=3, value=t.get("column_display", ""))
            subtasks = t.get("subtasks", [])
            subtasks_json = json.dumps(subtasks, ensure_ascii=False) if subtasks else ""
            ws.cell(row=row_idx, column=4, value=subtasks_json)
            entered = t.get("entered_at", "")[:19] if t.get("entered_at") else ""
            ws.cell(row=row_idx, column=5, value=entered)
            started = t.get("started_at", "")[:19] if t.get("started_at") else "-"
            ws.cell(row=row_idx, column=6, value=started)
            finished = t.get("finished_at", "")[:19] if t.get("finished_at") else "-"
            ws.cell(row=row_idx, column=7, value=finished)

        for col in range(1, 8):
            ws.column_dimensions[get_column_letter(col)].width = 18
        ws.column_dimensions["B"].width = 40
        ws.column_dimensions["D"].width = 50

        wb.save(filepath)
        return True
