"""
Vista del módulo Reports.
3 reportes: Tareas, Subtareas, Transiciones.
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
    QTabWidget,
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
    """Vista de reportes: 3 tabs (Tareas, Subtareas, Transiciones) y botón exportar."""

    def __init__(self, presenter: ReportsPresenter, parent=None):
        super().__init__(parent)
        self._presenter = presenter
        self.setObjectName("reportsView")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

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

        self.tabs = QTabWidget()
        self.tabs.setObjectName("reportsTabs")

        # Tab Tareas
        self.table_tareas = self._create_table(
            ["Ticket", "Actividad", "Estado", "Subtareas", "Inicio", "In Prog.", "Done"]
        )
        self.empty_tareas = QLabel("No hay tareas")
        self.empty_tareas.setObjectName("emptyState")
        self.empty_tareas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_tareas = QWidget()
        layout_tareas = QVBoxLayout(tab_tareas)
        layout_tareas.addWidget(self.table_tareas, 1)
        layout_tareas.addWidget(self.empty_tareas)
        self.empty_tareas.hide()
        self.tabs.addTab(tab_tareas, "Tareas")

        # Tab Subtareas
        self.table_subtasks = self._create_table(
            ["Ticket", "Tarea", "Subtarea", "Hecha", "Estado tarea"]
        )
        self.empty_subtasks = QLabel("No hay subtareas")
        self.empty_subtasks.setObjectName("emptyState")
        self.empty_subtasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_subtasks = QWidget()
        layout_sub = QVBoxLayout(tab_subtasks)
        layout_sub.addWidget(self.table_subtasks, 1)
        layout_sub.addWidget(self.empty_subtasks)
        self.empty_subtasks.hide()
        self.tabs.addTab(tab_subtasks, "Subtareas")

        # Tab Transiciones
        self.table_transitions = self._create_table(
            ["Tarea", "Desde", "Hacia", "Fecha/hora"]
        )
        self.empty_transitions = QLabel("No hay transiciones")
        self.empty_transitions.setObjectName("emptyState")
        self.empty_transitions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_transitions = QWidget()
        layout_trans = QVBoxLayout(tab_transitions)
        layout_trans.addWidget(self.table_transitions, 1)
        layout_trans.addWidget(self.empty_transitions)
        self.empty_transitions.hide()
        self.tabs.addTab(tab_transitions, "Transiciones")

        layout.addWidget(self.tabs, 1)

        self._refresh()

    def _create_table(self, headers: list[str]) -> QTableWidget:
        t = QTableWidget()
        t.setObjectName("reportsTable")
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        hv = t.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hv.setMinimumSectionSize(55)
        for i in range(1, len(headers)):
            hv.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        t.verticalHeader().setDefaultSectionSize(32)
        t.verticalHeader().setFixedWidth(36)
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        return t

    def _refresh(self):
        activities = self._presenter.load_activities()
        subtasks = self._presenter.load_subtasks()
        transitions = self._presenter.load_transitions()

        self._render_tareas(activities)
        self._render_subtasks(subtasks)
        self._render_transitions(transitions)

        self._toggle_empty(self.table_tareas, self.empty_tareas, len(activities) == 0)
        self._toggle_empty(self.table_subtasks, self.empty_subtasks, len(subtasks) == 0)
        self._toggle_empty(self.table_transitions, self.empty_transitions, len(transitions) == 0)

    def _render_tareas(self, activities: list):
        self.table_tareas.setRowCount(len(activities))
        for row, t in enumerate(activities):
            self.table_tareas.setItem(row, 0, QTableWidgetItem(t.get("ticket", "")[:20]))
            self.table_tareas.setItem(row, 1, QTableWidgetItem(t.get("name", "")[:80]))
            self.table_tareas.setItem(row, 2, QTableWidgetItem(t.get("column_display", "")))
            subtasks = t.get("subtasks", [])
            done_count = sum(1 for s in subtasks if s.get("done"))
            sub_str = f"{done_count}/{len(subtasks)}" if subtasks else "-"
            self.table_tareas.setItem(row, 3, QTableWidgetItem(sub_str))
            entered = format_date_display(t.get("entered_at")) if t.get("entered_at") else "-"
            self.table_tareas.setItem(row, 4, QTableWidgetItem(entered))
            started = format_date_display(t.get("started_at")) if t.get("started_at") else "-"
            self.table_tareas.setItem(row, 5, QTableWidgetItem(started))
            finished = format_date_display(t.get("finished_at")) if t.get("finished_at") else "-"
            self.table_tareas.setItem(row, 6, QTableWidgetItem(finished))

    def _render_subtasks(self, subtasks: list):
        self.table_subtasks.setRowCount(len(subtasks))
        for row, s in enumerate(subtasks):
            self.table_subtasks.setItem(row, 0, QTableWidgetItem(s.get("task_ticket", "")[:20]))
            self.table_subtasks.setItem(row, 1, QTableWidgetItem(s.get("task_name", "")[:60]))
            self.table_subtasks.setItem(row, 2, QTableWidgetItem(s.get("subtask_text", "")[:80]))
            self.table_subtasks.setItem(row, 3, QTableWidgetItem("Sí" if s.get("done") else "No"))
            self.table_subtasks.setItem(row, 4, QTableWidgetItem(s.get("column_display", "")))

    def _render_transitions(self, transitions: list):
        self.table_transitions.setRowCount(len(transitions))
        for row, tr in enumerate(transitions):
            self.table_transitions.setItem(row, 0, QTableWidgetItem(tr.get("task_name", "")[:60]))
            self.table_transitions.setItem(row, 1, QTableWidgetItem(tr.get("from_display", "")))
            self.table_transitions.setItem(row, 2, QTableWidgetItem(tr.get("to_display", "")))
            ts = tr.get("timestamp", "")
            self.table_transitions.setItem(row, 3, QTableWidgetItem(ts[:19] if ts else "-"))

    def _toggle_empty(self, table: QTableWidget, empty_label: QLabel, is_empty: bool):
        if is_empty:
            table.hide()
            empty_label.show()
        else:
            table.show()
            empty_label.hide()

    def _on_export_excel(self):
        activities = self._presenter.load_activities()
        subtasks = self._presenter.load_subtasks()
        transitions = self._presenter.load_transitions()
        if not activities and not subtasks and not transitions:
            QMessageBox.information(
                self, "Exportar", "No hay datos para exportar."
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
            ok = self._presenter.export_to_excel(path_obj)
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
