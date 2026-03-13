"""
Vista del módulo Reports.
Solo renderiza UI; la lógica está en ReportsPresenter.
"""

import os
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.modules.taskboard.utils import format_date_display
from ui.presenters.reports_presenter import ReportsPresenter
from ui.style_loader import load_styles


def _open_with_default_app(filepath: Path) -> None:
    """Abre el archivo con la aplicación predeterminada del sistema."""
    path_str = str(filepath.resolve())
    try:
        if sys.platform == "win32":
            os.startfile(path_str)
        elif sys.platform == "darwin":
            subprocess.run(["open", path_str], check=False)
        else:
            subprocess.run(["xdg-open", path_str], check=False)
    except Exception:
        pass


class ReportsView(QWidget):
    """Vista de reportes: tabla de actividades y botón exportar. Sin lógica de negocio."""

    def __init__(self, presenter: ReportsPresenter, parent=None):
        super().__init__(parent)
        self._presenter = presenter
        self.setObjectName("reportsView")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Reportes")
        title.setObjectName("reportsTitle")
        header.addWidget(title)
        header.addStretch()
        self.export_excel_btn = QPushButton("Exportar a Excel")
        self.export_excel_btn.setObjectName("primaryBtn")
        self.export_excel_btn.clicked.connect(self._on_export_excel)
        header.addWidget(self.export_excel_btn)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setObjectName("reportsTable")
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Actividad", "Estado", "Subtareas", "Inicio", "In Prog.", "Done"]
        )
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_view.setMinimumSectionSize(55)
        for i in range(1, 6):
            header_view.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 85)
        self.table.setColumnWidth(4, 85)
        self.table.setColumnWidth(5, 70)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.verticalHeader().setFixedWidth(36)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

        self.empty_label = QLabel("No hay actividades")
        self.empty_label.setObjectName("emptyState")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)
        self.empty_label.hide()

        self._refresh()

    def _refresh(self):
        activities = self._presenter.load_activities()
        self._render_table(activities)
        self._toggle_empty_state(len(activities) == 0)

    def _render_table(self, activities: list):
        self.table.setRowCount(len(activities))
        for row, t in enumerate(activities):
            self.table.setItem(row, 0, QTableWidgetItem(t.get("name", "")[:80]))
            self.table.setItem(row, 1, QTableWidgetItem(t.get("column_display", "")))
            subtasks = t.get("subtasks", [])
            done_count = sum(1 for s in subtasks if s.get("done"))
            sub_str = f"{done_count}/{len(subtasks)}" if subtasks else "-"
            self.table.setItem(row, 2, QTableWidgetItem(sub_str))
            entered = (
                format_date_display(t.get("entered_at")) if t.get("entered_at") else "-"
            )
            self.table.setItem(row, 3, QTableWidgetItem(entered))
            started = (
                format_date_display(t.get("started_at")) if t.get("started_at") else "-"
            )
            self.table.setItem(row, 4, QTableWidgetItem(started))
            finished = (
                format_date_display(t.get("finished_at")) if t.get("finished_at") else "-"
            )
            self.table.setItem(row, 5, QTableWidgetItem(finished))

    def _toggle_empty_state(self, is_empty: bool):
        if is_empty:
            self.table.hide()
            self.empty_label.show()
        else:
            self.table.show()
            self.empty_label.hide()

    def _on_export_excel(self):
        activities = self._presenter.load_activities()
        if not activities:
            QMessageBox.information(
                self, "Exportar", "No hay actividades para exportar."
            )
            return

        default_name = self._presenter.suggest_filename_excel()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar a Excel",
            default_name,
            "Excel (*.xlsx);;Todos los archivos (*)",
        )
        if not path:
            return

        path_obj = Path(path)
        if path_obj.suffix.lower() != ".xlsx":
            path_obj = path_obj.with_suffix(".xlsx")

        try:
            ok = self._presenter.export_to_excel(activities, path_obj)
            if ok:
                _open_with_default_app(path_obj)
            else:
                QMessageBox.warning(
                    self, "Exportar",
                    "No se pudo exportar. Ejecuta en terminal:\npip install openpyxl"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{e}")

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()
