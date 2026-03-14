"""
Vista del módulo Maestros.
Tabs: Tribu y Squad, Solicitante, Canal de reporte.
Tabla editable con Añadir / Eliminar.
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

from presentation.presenters.masters_presenter import MastersPresenter, MASTER_KEYS
from presentation.style_loader import load_styles
from presentation.theme import ObjectNames


class MastersView(QWidget):
    """Vista de maestros: tabs para Tribu y Squad, Solicitante, Canal de reporte."""

    def __init__(self, presenter: MastersPresenter, parent=None):
        super().__init__(parent)
        self._presenter = presenter
        self.setObjectName("mastersView")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Maestros")
        title.setObjectName(ObjectNames.REPORTS_TITLE)
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("reportsTabs")

        for master_key in MASTER_KEYS:
            tab = self._create_master_tab(master_key)
            self.tabs.addTab(tab, MASTER_KEYS[master_key])

        layout.addWidget(self.tabs, 1)
        load_styles(self)
        self._refresh_all()

    def _create_master_tab(self, master_key: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)

        btn_row = QHBoxLayout()
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

    def _refresh_all(self):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, "_master_key"):
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
                key = label.lower().replace(" ", "_").replace("ñ", "n")
            if label:  # Solo persistir filas con valor
                items.append({"key": key, "label": label})
        return items
