"""
Vista del módulo Maestros.
Tabs: Tribu y Squad, Solicitante, Canal de reporte, Categoría, Columnas Kanban.
Tabla editable con Añadir / Eliminar.
Columnas Kanban: Label, Orden, Límite WIP (vacío = sin límite).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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

from domain.taskboard.utils import normalize_key_from_label
from presentation.presenters.masters_presenter import MastersPresenter, MASTER_KEYS
from presentation.style_loader import load_styles
from presentation.theme import ObjectNames

# Índices de columnas en la tabla Kanban (Label, Orden, Límite WIP)
_COL_LABEL, _COL_ORDER, _COL_WIP = 0, 1, 2


class MastersView(QWidget):
    """Vista de maestros: tabs Tribu/Squad, Solicitante, Canal de reporte, Categoría, Columnas Kanban."""

    def __init__(self, presenter: MastersPresenter, parent=None):
        super().__init__(parent)
        self._presenter = presenter
        self.setObjectName("mastersView")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("reportsTabs")

        for master_key in MASTER_KEYS:
            tab = self._create_master_tab(master_key)
            self.tabs.addTab(tab, MASTER_KEYS[master_key])

        self._tab_kanban = self._create_kanban_tab()
        self.tabs.addTab(self._tab_kanban, "Columnas Kanban")

        layout.addWidget(self.tabs, 1)
        load_styles(self)
        self._refresh_all()

    def _create_master_tab(self, master_key: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 12, 0, 0)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_add = QPushButton("+ Añadir")
        btn_add.setObjectName("reportsAddTarea")
        btn_add.clicked.connect(lambda: self._on_add(master_key))
        btn_del = QPushButton("− Eliminar")
        btn_del.setObjectName("reportsDelTarea")
        btn_del.clicked.connect(lambda: self._on_delete(master_key))
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        table = QTableWidget()
        table.setObjectName(ObjectNames.REPORTS_TABLE)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Valor"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(36)
        table.verticalHeader().setFixedWidth(36)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.cellChanged.connect(lambda: self._on_cell_changed(master_key))
        layout.addWidget(table, 1)

        empty = QLabel("No hay valores")
        empty.setObjectName(ObjectNames.EMPTY_STATE)
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(empty)
        empty.hide()

        tab._table = table
        tab._empty = empty
        tab._master_key = master_key
        return tab

    def _create_kanban_tab(self) -> QWidget:
        """Tab para editar kanban_columns: Label, Orden, Límite WIP."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 12, 0, 0)

        hint = QLabel("Límite WIP: número máximo de tareas. Vacío = sin límite.")
        hint.setObjectName("sectionLabel")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(hint)

        table = QTableWidget()
        table.setObjectName(ObjectNames.REPORTS_TABLE)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Label", "Orden", "Límite WIP"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setDefaultSectionSize(36)
        table.verticalHeader().setFixedWidth(36)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.cellChanged.connect(self._on_kanban_cell_changed)
        layout.addWidget(table, 1)

        empty = QLabel("No hay columnas")
        empty.setObjectName(ObjectNames.EMPTY_STATE)
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(empty)
        empty.hide()

        tab._table = table
        tab._empty = empty
        tab._is_kanban = True
        return tab

    def _refresh_all(self):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab is self._tab_kanban:
                self._refresh_kanban_tab(tab)
            elif hasattr(tab, "_master_key"):
                self._refresh_tab(tab)

    def _refresh_tab(self, tab: QWidget):
        master_key = tab._master_key
        table = tab._table
        empty = tab._empty
        items = self._presenter.load_master(master_key)

        table.blockSignals(True)
        table.setRowCount(len(items))
        for row, it in enumerate(items):
            label = it.get("label", "")
            cell = QTableWidgetItem(label)
            cell.setData(Qt.ItemDataRole.UserRole, it.get("key", ""))
            table.setItem(row, 0, cell)
        table.blockSignals(False)

        empty.setVisible(len(items) == 0)

    def _refresh_kanban_tab(self, tab: QWidget):
        columns = self._presenter.load_kanban_columns()
        table = tab._table
        empty = tab._empty

        table.blockSignals(True)
        table.setRowCount(len(columns))
        for row, col in enumerate(columns):
            label = col.get("label", "")
            order = col.get("order", row + 1)
            wip = col.get("wip_limit")
            table.setItem(row, _COL_LABEL, QTableWidgetItem(label))
            order_item = QTableWidgetItem(str(order))
            order_item.setData(Qt.ItemDataRole.UserRole, col.get("key", ""))
            table.setItem(row, _COL_ORDER, order_item)
            wip_str = "" if wip is None else str(wip)
            table.setItem(row, _COL_WIP, QTableWidgetItem(wip_str))
        table.blockSignals(False)

        empty.setVisible(len(columns) == 0)

    def _on_add(self, master_key: str):
        tab = self._tab_for(master_key)
        if not tab:
            return
        items = self._collect_items(tab._table)
        items.append({"key": "", "label": "Nuevo"})
        if self._presenter.save_master(master_key, items):
            self._refresh_tab(tab)
            tab._table.setCurrentCell(len(items) - 1, 0)
            tab._table.edit(tab._table.currentIndex())

    def _on_delete(self, master_key: str):
        tab = self._tab_for(master_key)
        if not tab:
            return
        row = tab._table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "Eliminar",
                "Selecciona una fila para eliminar.",
            )
            return
        items = self._collect_items(tab._table)
        items.pop(row)
        if self._presenter.save_master(master_key, items):
            self._refresh_tab(tab)

    def _on_cell_changed(self, master_key: str):
        tab = self._tab_for(master_key)
        if not tab:
            return
        items = self._collect_items(tab._table)
        if self._presenter.save_master(master_key, items):
            tab._empty.setVisible(len(items) == 0)

    def _on_kanban_cell_changed(self):
        items = self._collect_kanban_items(self._tab_kanban._table)
        if items and self._presenter.save_kanban_columns(items):
            self._tab_kanban._empty.setVisible(len(items) == 0)

    def _collect_kanban_items(self, table: QTableWidget) -> list[dict]:
        items = []
        for row in range(table.rowCount()):
            label_it = table.item(row, _COL_LABEL)
            order_it = table.item(row, _COL_ORDER)
            wip_it = table.item(row, _COL_WIP)
            label = (label_it.text() or "").strip() if label_it else ""
            key = (order_it.data(Qt.ItemDataRole.UserRole) or "") if order_it else ""
            if not key and label:
                key = normalize_key_from_label(label)
            order_str = (order_it.text() or "").strip() if order_it else ""
            order = int(order_str) if order_str.isdigit() else row + 1
            wip_str = (wip_it.text() or "").strip() if wip_it else ""
            wip = int(wip_str) if wip_str.isdigit() else None
            if key and label:
                items.append({"key": key, "label": label, "order": order, "wip_limit": wip})
        return items

    def _tab_for(self, master_key: str) -> QWidget | None:
        keys = list(MASTER_KEYS.keys())
        idx = keys.index(master_key) if master_key in keys else -1
        if idx >= 0:
            return self.tabs.widget(idx)
        return None

    def _collect_items(self, table: QTableWidget) -> list[dict]:
        items = []
        for row in range(table.rowCount()):
            it = table.item(row, 0)
            label = (it.text() or "").strip() if it else ""
            key = (it.data(Qt.ItemDataRole.UserRole) or "") if it else ""
            if not key and label:
                key = normalize_key_from_label(label)
            if label:  # Solo persistir filas con valor
                items.append({"key": key, "label": label})
        return items
