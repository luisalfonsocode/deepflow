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

from application.taskboard import BoardService
from presentation.modules.taskboard.dialogs import open_task_detail, open_task_create
from presentation.modules.taskboard.widgets import TaskCard, ColumnWidget
from presentation.style_loader import load_styles
from presentation.theme import ObjectNames


class TaskBoardView(QWidget):
    """Vista del tablero Kanban. Embebible en Widget o ventana independiente."""

    overcapacity_changed = pyqtSignal(bool)

    def __init__(self, board: BoardService, clipboard_provider, parent=None):
        super().__init__(parent)
        self.board = board
        self._clipboard = clipboard_provider
        self.setObjectName(ObjectNames.TASKBOARD_VIEW)
        self._build_ui()

    def _build_ui(self):
        self.board.load()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(6, 6, 6, 6)
        columns_layout.setSpacing(4)

        self.columns: dict[str, ColumnWidget] = {}
        for col in self.board.get_column_keys():
            show_create = col == "backlog"
            cw = ColumnWidget(
                col,
                self._on_move,
                show_create_button=show_create,
                on_show_dialog=self._show_task_dialog if show_create else None,
                display_label=self.board.col_key_to_display(col),
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
        def on_close():
            QTimer.singleShot(50, self._rebuild_ui)

        open_task_create(
            self.board,
            "backlog",
            on_close_callback=on_close,
            parent=self.window(),
            initial_text=initial_text,
        )

    def _on_task_click(self, task_id: str):
        def on_close():
            QTimer.singleShot(50, self._rebuild_ui)

        open_task_detail(self.board, task_id, on_close_callback=on_close, parent=self.window())
        QTimer.singleShot(50, self._rebuild_ui)

    def _on_move(self, task_id: str, target_column: str):
        ok = self.board.move_task(task_id, target_column)
        QTimer.singleShot(50, self._rebuild_ui)
        if not ok:
            QMessageBox.warning(
                self.window(),
                "No se puede mover",
                f"La columna {self.board.col_key_to_display(target_column)} está llena (límite WIP alcanzado).",
            )

    def _rebuild_ui(self):
        self.board.load()
        for col in self.columns:
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
                    started_at=t.get("started_at"),
                    finished_at=t.get("finished_at"),
                    ticket=t.get("ticket", ""),
                    prioridad=bool(t.get("prioridad", False)),
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

        self.overcapacity_changed.emit(any(self.board.is_overcapacity(c) for c in self.columns))
