"""
Vista del módulo Reports.
4 reportes: Tareas, Subtareas, Transiciones, Tiempo por categoría.
Tablas editables tipo Excel: editar celdas, insertar y eliminar filas.
"""

import logging
from datetime import datetime
from pathlib import Path

LOG = logging.getLogger(__name__)

from PyQt6.QtCore import QDate, QRect, QSize, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor
from presentation.widgets_common import ComboBoxNoWheelUnfocused
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStyledItemDelegate,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from domain.taskboard import TZ_APP
from domain.taskboard.utils import format_date_display, parse_date_to_iso
from infrastructure.system import open_with_default_app
from presentation.modules.reports.time_report_tab import TimeReportTab
from presentation.modules.taskboard.widgets import TaskInputDialog
from presentation.presenters.reports_presenter import ReportsPresenter
from presentation.style_loader import load_styles
from presentation.theme import ObjectNames


class _EmptyClipboard:
    """Proveedor dummy cuando no hay portapapeles (tests, etc.)."""

    def get_text(self) -> str:
        return ""


class SubtasksModal(QDialog):
    """Modal que muestra las subtareas de una tarea. Mismo contenido que la hoja Subtareas."""

    def __init__(self, task_id: str, task_name: str, presenter: ReportsPresenter, parent=None):
        super().__init__(parent)
        self._task_id = task_id
        self._task_name = task_name
        self._presenter = presenter
        title = task_name[:60] + ("..." if len(task_name) > 60 else "")
        self.setWindowTitle(f"Subtareas: {title}")
        self.setMinimumSize(500, 300)
        self.resize(560, 360)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        lbl = QLabel(f"Tarea: {self._task_name[:80]}")
        lbl.setObjectName("sectionLabel")
        layout.addWidget(lbl)
        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Añadir subtarea")
        btn_add.clicked.connect(self._on_add)
        btn_del = QPushButton("− Eliminar subtarea")
        btn_del.clicked.connect(self._on_delete)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.table = QTableWidget()
        self.table.setObjectName(ObjectNames.REPORTS_TABLE)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Subtarea", "Hecha"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellChanged.connect(self._on_subtask_text_changed)
        layout.addWidget(self.table)
        ok_btn = QPushButton("Cerrar")
        ok_btn.setObjectName(ObjectNames.PRIMARY_BTN)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, 0)
        self._load()

    def _load(self):
        self._loading = True
        try:
            subtasks = self._presenter.load_subtasks_for_task(self._task_id)
            self.table.blockSignals(True)
            self.table.setRowCount(len(subtasks))
            for row, s in enumerate(subtasks):
                task_id = self._task_id
                sub_idx = s.get("subtask_index", 0)
                it0 = QTableWidgetItem(s.get("subtask_text", "")[:80])
                it0.setData(Qt.ItemDataRole.UserRole, (task_id, sub_idx))
                self.table.setItem(row, 0, it0)
                chk = QCheckBox()
                chk.setChecked(bool(s.get("done")))
                chk.setStyleSheet("margin-left: 50%; margin-right: 50%;")
                chk.stateChanged.connect(
                    lambda _, r=row, tid=task_id, sid=sub_idx: self._on_checkbox_toggled(r, tid, sid)
                )
                wrapper = QWidget()
                wlay = QHBoxLayout(wrapper)
                wlay.setContentsMargins(0, 0, 0, 0)
                wlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                wlay.addWidget(chk)
                self.table.setCellWidget(row, 1, wrapper)
            self.table.blockSignals(False)
        finally:
            self._loading = False

    def _on_checkbox_toggled(self, row: int, task_id: str, sub_idx: int):
        if getattr(self, "_loading", False):
            return
        wrapper = self.table.cellWidget(row, 1)
        if wrapper and wrapper.findChild(QCheckBox):
            chk = wrapper.findChild(QCheckBox)
            done = chk.isChecked()
            text = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            if self._presenter.update_subtask(task_id, sub_idx, text, done):
                self._load()

    def _on_subtask_text_changed(self, row: int, col: int):
        if col != 0:
            return
        it = self.table.item(row, 0)
        meta = it.data(Qt.ItemDataRole.UserRole) if it else None
        if not meta or not isinstance(meta, tuple):
            return
        task_id, sub_idx = meta
        wrapper = self.table.cellWidget(row, 1)
        done = False
        if wrapper:
            chk = wrapper.findChild(QCheckBox)
            if chk:
                done = chk.isChecked()
        text = self.table.item(row, 0).text()
        if self._presenter.update_subtask(task_id, sub_idx, text, done):
            self._load()

    def _on_add(self):
        if self._presenter.create_subtask(self._task_id, "Nueva subtarea"):
            self._load()

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Eliminar", "Selecciona una fila.")
            return
        it = self.table.item(row, 0)
        meta = it.data(Qt.ItemDataRole.UserRole) if it else None
        if not meta or not isinstance(meta, tuple):
            return
        task_id, sub_idx = meta
        if QMessageBox.question(
            self, "Eliminar subtarea", "¿Eliminar esta subtarea?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            if self._presenter.delete_subtask(task_id, sub_idx):
                self._load()


class ComboBoxDelegate(QStyledItemDelegate):
    """Delegate para editar columna Estado. Solo permite columnas con espacio (WIP)."""

    def createEditor(self, parent, option, index):
        cb = ComboBoxNoWheelUnfocused(parent)
        reports_view = self.parent()
        current_col = ""
        column_items = []
        if hasattr(reports_view, "table_tareas") and hasattr(reports_view, "_presenter"):
            column_items = reports_view._presenter.get_column_items()
            row = index.row()
            it = reports_view.table_tareas.item(row, 1)
            current_col = it.data(Qt.ItemDataRole.UserRole) or "" if it else ""
            for label, key in column_items:
                if reports_view._presenter.can_add_to(key) or key == current_col:
                    cb.addItem(label, key)
        if cb.count() == 0:
            for label, key in column_items:
                cb.addItem(label, key)
        return cb

    def setEditorData(self, editor, index):
        editor.setCurrentText(index.data(Qt.ItemDataRole.DisplayRole) or "")

    def setModelData(self, editor, model, index):
        label = editor.currentText().strip()
        key = editor.currentData() or label
        model.setData(index, label, Qt.ItemDataRole.EditRole)
        model.setData(index, key, Qt.ItemDataRole.UserRole)


class ReportsView(QWidget):
    """Vista de reportes: 3 tabs (Tareas, Subtareas, Transiciones) y botón exportar."""

    def __init__(self, presenter: ReportsPresenter, clipboard_provider=None, parent=None):
        super().__init__(parent)
        self._presenter = presenter
        self._clipboard = clipboard_provider
        self.setObjectName(ObjectNames.REPORTS_VIEW)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Reportes")
        title.setObjectName(ObjectNames.REPORTS_TITLE)
        header.addWidget(title)
        header.addStretch()
        self.export_excel_btn = QPushButton("Exportar a Excel")
        self.export_excel_btn.setObjectName(ObjectNames.PRIMARY_BTN)
        self.export_excel_btn.clicked.connect(self._on_export_excel)
        header.addWidget(self.export_excel_btn)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("reportsTabs")

        # Tab Tareas: Actividad, Estado, fechas (abreviadas F.), Ticket, Subtareas
        self.table_tareas = self._create_table(
            [
                "Actividad",
                "Estado",
                "F. solicitud",
                "F. inicio",
                "F. fin",
                "F. compromiso",
                "Ticket",
                "Subtareas",
            ],
            editable=True,
        )
        # Columna F. compromiso más ancha para que la cabecera no se corte
        self.table_tareas.horizontalHeader().resizeSection(5, 110)
        self.table_tareas.setItemDelegateForColumn(1, ComboBoxDelegate(self))
        self.table_tareas.cellChanged.connect(self._on_tareas_cell_changed)
        self.table_tareas.cellClicked.connect(self._on_tareas_cell_clicked)
        self.empty_tareas = QLabel("No hay tareas")
        self.empty_tareas.setObjectName(ObjectNames.EMPTY_STATE)
        self.empty_tareas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_tareas = QWidget()
        layout_tareas = QVBoxLayout(tab_tareas)
        btn_tareas = QHBoxLayout()
        btn_add_tarea = QPushButton("+ Añadir tarea")
        btn_add_tarea.setObjectName("reportsAddTarea")
        btn_add_tarea.clicked.connect(self._on_add_tarea)
        btn_del_tarea = QPushButton("− Eliminar tarea")
        btn_del_tarea.setObjectName("reportsDelTarea")
        btn_del_tarea.clicked.connect(self._on_delete_tarea)
        btn_tareas.addWidget(btn_add_tarea)
        btn_tareas.addWidget(btn_del_tarea)
        btn_tareas.addStretch()
        layout_tareas.addLayout(btn_tareas)
        layout_tareas.addWidget(self.table_tareas, 1)
        layout_tareas.addWidget(self.empty_tareas)
        self.empty_tareas.hide()
        self.tabs.addTab(tab_tareas, "Tareas")

        # Tab Transiciones
        self.table_transitions = self._create_table(
            ["Tarea", "Desde", "Hacia", "Fecha/hora"]
        )
        self.empty_transitions = QLabel("No hay transiciones")
        self.empty_transitions.setObjectName(ObjectNames.EMPTY_STATE)
        self.empty_transitions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_transitions = QWidget()
        layout_trans = QVBoxLayout(tab_transitions)
        layout_trans.addWidget(self.table_transitions, 1)
        layout_trans.addWidget(self.empty_transitions)
        self.empty_transitions.hide()
        self.tabs.addTab(tab_transitions, "Transiciones")

        self.time_report_tab = TimeReportTab()
        self.time_report_tab.data_requested.connect(self._on_time_data_requested)
        self.time_report_tab.btn_export_summary.clicked.connect(self._on_export_time_summary)
        self.time_report_tab.btn_export_detail.clicked.connect(self._on_export_time_detail)
        self.tabs.addTab(self.time_report_tab, "Tiempo")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs, 1)

        self._refresh()

    def _create_table(self, headers: list[str], editable: bool = False) -> QTableWidget:
        t = QTableWidget()
        t.setObjectName(ObjectNames.REPORTS_TABLE)
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        hv = t.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hv.setMinimumSectionSize(55)
        for i in range(1, len(headers)):
            hv.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        t.verticalHeader().setDefaultSectionSize(36)
        t.verticalHeader().setFixedWidth(36)
        t.setAlternatingRowColors(True)
        if editable:
            t.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        else:
            t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        return t

    def _refresh(self):
        activities = self._presenter.load_activities()
        transitions = self._presenter.load_transitions()

        self._render_tareas(activities)
        self._render_transitions(transitions)

        self._toggle_empty(self.table_tareas, self.empty_tareas, len(activities) == 0)
        self._toggle_empty(self.table_transitions, self.empty_transitions, len(transitions) == 0)

    def _render_tareas(self, activities: list):
        # 0 Actividad, 1 Estado, 2 Fecha solicitud, 3 Fecha inicio, 4 Fecha fin,
        # 5 Fecha compromiso, 6 Ticket, 7 Subtareas
        self.table_tareas.blockSignals(True)
        try:
            self.table_tareas.setRowCount(len(activities))
            for row, t in enumerate(activities):
                task_id = t.get("id", "")
                it0 = QTableWidgetItem(t.get("name", "")[:80])
                it0.setData(Qt.ItemDataRole.UserRole, task_id)
                self.table_tareas.setItem(row, 0, it0)
                it1 = QTableWidgetItem(t.get("column_display", ""))
                it1.setData(Qt.ItemDataRole.UserRole, t.get("column", ""))
                self.table_tareas.setItem(row, 1, it1)
                created_at = t.get("created_at") or ""
                created = format_date_display(created_at) if created_at else "-"
                it2 = QTableWidgetItem(created)
                it2.setData(Qt.ItemDataRole.UserRole, created_at)
                self.table_tareas.setItem(row, 2, it2)
                started_at = t.get("started_at") or ""
                started = format_date_display(started_at) if started_at else "-"
                it3 = QTableWidgetItem(started)
                it3.setData(Qt.ItemDataRole.UserRole, started_at)
                self.table_tareas.setItem(row, 3, it3)
                finished_at = t.get("finished_at") or ""
                finished = format_date_display(finished_at) if finished_at else "-"
                it4 = QTableWidgetItem(finished)
                it4.setData(Qt.ItemDataRole.UserRole, finished_at)
                self.table_tareas.setItem(row, 4, it4)
                due_date = t.get("due_date") or ""
                due = format_date_display(due_date) if due_date else "-"
                it5 = QTableWidgetItem(due)
                it5.setData(Qt.ItemDataRole.UserRole, due_date)
                self.table_tareas.setItem(row, 5, it5)
                self.table_tareas.setItem(row, 6, QTableWidgetItem(t.get("ticket", "")[:20]))
                subtasks = t.get("subtasks", [])
                done_count = sum(1 for s in subtasks if s.get("done"))
                sub_str = f"{done_count}/{len(subtasks)}" if subtasks else "-"
                it7 = QTableWidgetItem(sub_str)
                it7.setFlags(it7.flags() & ~Qt.ItemFlag.ItemIsEditable)
                it7.setToolTip("Clic para ver y editar subtareas")
                it7.setForeground(QBrush(QColor("#2563eb")))
                self.table_tareas.setItem(row, 7, it7)
        finally:
            self.table_tareas.blockSignals(False)

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

    def _on_tareas_cell_clicked(self, row: int, col: int):
        if col == 7:
            task_id = self._get_tarea_task_id(row)
            if task_id:
                it0 = self.table_tareas.item(row, 0)
                task_name = it0.text() if it0 else ""
                modal = SubtasksModal(task_id, task_name, self._presenter, self.window())
                load_styles(modal)
                modal.exec()
                self._refresh()

    def _get_tarea_task_id(self, row: int) -> str | None:
        it = self.table_tareas.item(row, 0)
        return it.data(Qt.ItemDataRole.UserRole) if it else None

    def _on_tareas_cell_changed(self, row: int, col: int):
        task_id = self._get_tarea_task_id(row)
        if not task_id:
            return
        if col == 0:
            val = self.table_tareas.item(row, 0).text()
            if self._presenter.update_task_name(task_id, val):
                self._refresh()
        elif col == 1:
            it = self.table_tareas.item(row, 1)
            val = it.text().strip()
            col_key = self._presenter.display_to_column_key(val) or it.data(Qt.ItemDataRole.UserRole)
            if col_key:
                ok = self._presenter.update_task_state_by_key(task_id, col_key)
            else:
                ok = False
            if ok:
                self._refresh()
            else:
                self._refresh()
                if col_key:
                    QMessageBox.warning(
                        self, "No se pudo mover",
                        "La columna destino está llena (límite WIP alcanzado)."
                    )
                elif val:
                    QMessageBox.warning(
                        self, "Estado inválido",
                        "Estado no reconocido. Usa: Backlog, To Do, In Progress, Done, Detenido."
                    )
        elif col == 2:
            val = self.table_tareas.item(row, 2).text().strip()
            iso_val = parse_date_to_iso(val) if val and val != "-" else ""
            if iso_val is not None:
                if self._presenter.update_task_created_at(task_id, iso_val):
                    self._refresh()
            elif val:
                QMessageBox.warning(self, "Fecha inválida", "Formato: dd/mm/aaaa (ej: 13/03/2026)")
        elif col == 3:
            val = self.table_tareas.item(row, 3).text().strip()
            iso_val = parse_date_to_iso(val) if val and val != "-" else ""
            if iso_val is not None:
                if self._presenter.update_task_started_at(task_id, iso_val):
                    self._refresh()
            elif val:
                QMessageBox.warning(self, "Fecha inválida", "Formato: dd/mm/aaaa (ej: 13/03/2026)")
        elif col == 4:
            val = self.table_tareas.item(row, 4).text().strip()
            iso_val = parse_date_to_iso(val) if val and val != "-" else ""
            if iso_val is not None:
                if self._presenter.update_task_finished_at(task_id, iso_val):
                    self._refresh()
            elif val:
                QMessageBox.warning(self, "Fecha inválida", "Formato: dd/mm/aaaa (ej: 13/03/2026)")
        elif col == 5:
            val = self.table_tareas.item(row, 5).text().strip()
            iso_val = parse_date_to_iso(val) if val and val != "-" else ""
            if iso_val is not None:
                if self._presenter.update_task_due_date(task_id, iso_val):
                    self._refresh()
            elif val:
                QMessageBox.warning(self, "Fecha inválida", "Formato: dd/mm/aaaa (ej: 13/03/2026)")
        elif col == 6:
            val = self.table_tareas.item(row, 6).text()
            if self._presenter.update_task_ticket(task_id, val):
                self._refresh()

    def _on_add_tarea(self):
        clipboard = self._clipboard or _EmptyClipboard()
        if not self._presenter.can_add_to("backlog"):
            QMessageBox.warning(
                self, "Añadir tarea",
                "No se puede añadir: Backlog está lleno (límite WIP)."
            )
            return
        dialog = TaskInputDialog(
            clipboard_provider=clipboard,
            parent=self.window(),
        )
        load_styles(dialog)
        dialog.open_with_text("")
        if dialog.result() == dialog.DialogCode.Accepted:
            text = dialog.get_text()
            task = self._presenter.create_task(text, "backlog")
            if task:
                self._refresh()
            else:
                QMessageBox.warning(
                    self, "Añadir tarea",
                    "No se puede añadir: Backlog está lleno (límite WIP)."
                )

    def _on_delete_tarea(self):
        row = self.table_tareas.currentRow()
        if row < 0:
            QMessageBox.information(self, "Eliminar", "Selecciona una fila.")
            return
        task_id = self._get_tarea_task_id(row)
        if not task_id:
            return
        if QMessageBox.question(
            self, "Eliminar tarea",
            "¿Eliminar esta tarea?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            if self._presenter.delete_task(task_id):
                self._refresh()

    def _on_export_excel(self):
        """Exporta a Excel: Tareas, Subtareas, Transiciones y Reporte de tiempo (periodo del tab Tiempo)."""
        from_dt, to_dt = self.time_report_tab.get_date_range()
        activities = self._presenter.load_activities()
        subtasks = self._presenter.load_subtasks()
        transitions = self._presenter.load_transitions()
        if not activities and not subtasks and not transitions:
            QMessageBox.information(
                self, "Exportar", "No hay datos para exportar."
            )
            return

        default_name = self._presenter.suggest_filename_time_report()
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
            ok = self._presenter.export_time_report_to_excel(from_dt, to_dt, path_obj)
            if ok:
                open_with_default_app(path_obj)
                QMessageBox.information(
                    self, "Exportado",
                    "Exportado correctamente.\n"
                    "Incluye: Tareas, Subtareas, Transiciones y Reporte de tiempo por categoría."
                )
            else:
                QMessageBox.warning(
                    self, "Exportar",
                    "No se pudo exportar. Ejecuta en terminal:\npip install openpyxl"
                )
        except Exception as e:
            LOG.exception("Error al exportar a Excel")
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{e}")

    def _on_export_time_summary(self):
        """Exporta resumen por categoría del tab Tiempo a Excel."""
        from_dt, to_dt = self.time_report_tab.get_date_range()
        default = f"resumen_tiempo_{datetime.now(TZ_APP).strftime('%Y%m%d_%H%M')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar resumen", default, "Excel (*.xlsx);;Todos (*)"
        )
        if not path:
            return
        path_obj = Path(path)
        if path_obj.suffix.lower() != ".xlsx":
            path_obj = path_obj.with_suffix(".xlsx")
        try:
            if self._presenter.export_time_summary_to_excel(from_dt, to_dt, path_obj):
                open_with_default_app(path_obj)
                QMessageBox.information(self, "Exportado", "Resumen por categoría exportado.")
            else:
                QMessageBox.warning(self, "Exportar", "No se pudo exportar. pip install openpyxl")
        except Exception as e:
            LOG.exception("Error al exportar resumen")
            QMessageBox.critical(self, "Error", f"Error:\n{e}")

    def _on_export_time_detail(self):
        """Exporta detalle por tarea del tab Tiempo a Excel."""
        from_dt, to_dt = self.time_report_tab.get_date_range()
        default = f"detalle_tiempo_{datetime.now(TZ_APP).strftime('%Y%m%d_%H%M')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar detalle", default, "Excel (*.xlsx);;Todos (*)"
        )
        if not path:
            return
        path_obj = Path(path)
        if path_obj.suffix.lower() != ".xlsx":
            path_obj = path_obj.with_suffix(".xlsx")
        try:
            if self._presenter.export_time_detail_to_excel(from_dt, to_dt, path_obj):
                open_with_default_app(path_obj)
                QMessageBox.information(self, "Exportado", "Detalle por tarea exportado.")
            else:
                QMessageBox.warning(self, "Exportar", "No se pudo exportar. pip install openpyxl")
        except Exception as e:
            LOG.exception("Error al exportar detalle")
            QMessageBox.critical(self, "Error", f"Error:\n{e}")

    def _on_tab_changed(self, index: int):
        """Al cambiar al tab Tiempo, pedir datos (diferido para que el tab esté visible)."""
        tab_tiempo_index = 2
        if index == tab_tiempo_index:
            QTimer.singleShot(0, self.time_report_tab.request_initial_data)

    def _on_time_data_requested(self, from_dt: datetime, to_dt: datetime):
        """El tab Tiempo pide datos. Obtiene el reporte y actualiza el tab."""
        report = self._presenter.get_time_report(from_dt, to_dt)
        self.time_report_tab.set_report_data(report)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()
        self.time_report_tab.request_initial_data()
