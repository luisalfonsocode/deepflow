"""Vista del módulo TaskBoard."""

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from core.modules.taskboard import BoardService, COLUMNS, col_key_to_display
from adapters.ui import QtClipboardProvider
from ui.modules.taskboard.dialogs import open_task_detail
from ui.modules.taskboard.widgets import TaskCard, ColumnWidget, TaskInputDialog
from ui.style_loader import load_styles


class TaskBoardView(QWidget):
    """Vista del tablero Kanban. Embebible en Widget o ventana independiente."""

    overcapacity_changed = pyqtSignal(bool)

    def __init__(self, board: BoardService, parent=None):
        super().__init__(parent)
        self.board = board
        self.setObjectName("taskboardView")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(6, 6, 6, 6)
        columns_layout.setSpacing(4)

        self.columns: dict[str, ColumnWidget] = {}
        for col in COLUMNS:
            show_create = col == "backlog"
            cw = ColumnWidget(
                col,
                self._on_move,
                show_create_button=show_create,
                on_show_dialog=self._show_task_dialog if show_create else None,
            )
            self.columns[col] = cw
            columns_layout.addWidget(cw, 1)

        layout.addLayout(columns_layout)
        load_styles(self)
        self._install_ctrl_v()
        self._rebuild_ui()

    def _install_ctrl_v(self):
        shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        shortcut.activated.connect(self._paste_from_clipboard)

    def _paste_from_clipboard(self):
        if not self.board.can_add_to("backlog"):
            return
        text = QApplication.clipboard().text().strip()
        self._show_task_dialog(text)

    def _show_task_dialog(self, initial_text: str = ""):
        dialog = TaskInputDialog(
            clipboard_provider=QtClipboardProvider(),
            parent=self.window(),
        )
        load_styles(dialog)
        dialog.open_with_text(initial_text)
        if dialog.result() == dialog.DialogCode.Accepted:
            text = dialog.get_text()
            task = self.board.create_task(text)
            if task:
                self._rebuild_ui()

    def _on_task_click(self, task_id: str):
        def on_close():
            QTimer.singleShot(50, self._rebuild_ui)

        open_task_detail(self.board, task_id, on_close_callback=on_close, parent=self.window())
        QTimer.singleShot(50, self._rebuild_ui)

    def _on_move(self, task_id: str, target_column: str):
        ok = self.board.move_task(task_id, target_column)
        if not ok:
            QMessageBox.warning(
                self.window(),
                "No se puede mover",
                f"La columna {col_key_to_display(target_column)} está llena (límite WIP).",
            )
        else:
            QTimer.singleShot(50, self._rebuild_ui)

    def _rebuild_ui(self):
        for col in COLUMNS:
            cw = self.columns[col]
            while cw.tasks_layout.count() > 1:  # keep drop_zone
                item = cw.tasks_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            tasks = self.board.data.get(col, [])
            for t in tasks:
                card = TaskCard(
                    t["id"],
                    t.get("name", ""),
                    col,
                    self._on_move,
                    on_click=self._on_task_click,
                    entered_at=t.get("entered_at"),
                    ticket=t.get("ticket", ""),
                    parent=cw.tasks_widget,
                )
                cw.tasks_layout.insertWidget(cw.tasks_layout.count() - 1, card)
            cw.count_label.setText(str(len(tasks)))
            over = self.board.is_overcapacity(col)
            cw.count_label.setProperty("overcapacity", "true" if over else "false")
            cw.count_label.style().unpolish(cw.count_label)
            cw.count_label.style().polish(cw.count_label)
            if col == "backlog" and cw.create_btn:
                cw.create_btn.setEnabled(self.board.can_add_to("backlog"))

        self.overcapacity_changed.emit(any(self.board.is_overcapacity(c) for c in COLUMNS))
