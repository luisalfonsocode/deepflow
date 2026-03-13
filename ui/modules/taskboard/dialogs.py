"""Diálogos del módulo TaskBoard. Modal unificado de detalle/edición de tarea."""

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.modules.taskboard import BoardService, COLUMNS, col_key_to_display
from core.modules.taskboard.utils import (
    compute_time_in_columns,
    format_date_display,
    format_duration_in_activity,
    format_seconds_duration,
)
from ui.style_loader import load_styles
from ui.theme import Layout


class _SubtaskCheckButton(QPushButton):
    """Botón circular para marcar subtarea como completada. Visible en fondo oscuro."""

    def __init__(self, checked: bool, on_toggled, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("subtaskCheckBtn")
        self.setFixedSize(28, 28)
        self.clicked.connect(on_toggled)
        self._checked = checked
        self._refresh_display()

    def _refresh_display(self):
        self.setText("✓" if self._checked else "○")
        self.setToolTip("Desmarcar" if self._checked else "Marcar como completada")
        self.setProperty("checked", "true" if self._checked else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class _SubtaskLabel(QLabel):
    """Label clickeable, una sola línea: al hacer clic marca/desmarca la subtarea."""

    def __init__(self, text: str, done: bool, on_toggle):
        display = (text[:50] + "…") if len(text) > 50 else text
        super().__init__(display)
        self.on_toggle = on_toggle
        self.setWordWrap(False)
        self.setMaximumHeight(24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if done:
            f = self.font()
            f.setStrikeOut(True)
            self.setFont(f)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.on_toggle:
            self.on_toggle()
        super().mousePressEvent(event)


def open_task_detail(board: BoardService, task_id: str, on_close_callback, parent=None) -> bool:
    """
    Abre el modal unificado de detalle/edición de tarea.
    Retorna True si se aceptó, False si se rechazó o la tarea no existe.
    """
    dialog = TaskDetailDialog(board, task_id, on_close_callback, parent)
    load_styles(dialog)
    return dialog.exec() == dialog.DialogCode.Accepted


class TaskDetailDialog(QDialog):
    """
    Modal unificado de detalle y edición de tarea.
    Usado desde: widget compacto, TaskBoard (clic en tarjeta), Summary.
    """

    def __init__(self, board, task_id: str, on_close_callback, parent=None):
        super().__init__(parent)
        self.board = board
        self.task_id = task_id
        self.on_close_callback = on_close_callback
        self.setWindowTitle("Tarea")
        self.setModal(True)
        self.setMinimumSize(Layout.TASK_DETAIL_MIN_WIDTH, Layout.TASK_DETAIL_MIN_HEIGHT)
        self.resize(Layout.TASK_DETAIL_DEFAULT_WIDTH, Layout.TASK_DETAIL_DEFAULT_HEIGHT)

        task = board.get_task(task_id)
        if not task:
            self.reject()
            return

        self._current_col = board.get_task_column(task_id) or "in_progress"
        self._combo_ready = False
        self._build_ui(task)
        self._combo_ready = True

        load_styles(self)

    def _build_ui(self, task: dict):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Dos paneles: izquierda (campos) | derecha (subtareas)
        panels = QHBoxLayout()
        panels.setSpacing(16)
        panels.setContentsMargins(0, 0, 0, 0)

        # Panel izquierdo: estado, actividad (50 chars), fechas
        left_panel = QWidget()
        left_panel.setObjectName("detailLeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # 1. Estado y combo (primero, alineado a la izquierda)
        header_row = QHBoxLayout()
        state_label = QLabel("Estado:")
        state_label.setObjectName("taskQuickEditInfo")
        header_row.addWidget(state_label, 0)
        self.state_combo = QComboBox()
        self.state_combo.setObjectName("stateCombo")
        self.state_combo.installEventFilter(self)
        self.state_combo.view().installEventFilter(self)
        for col in COLUMNS:
            if self.board.can_add_to(col) or col == self._current_col:
                self.state_combo.addItem(col_key_to_display(col), col)
        current_idx = self.state_combo.findData(self._current_col)
        if current_idx >= 0:
            self.state_combo.setCurrentIndex(current_idx)
        else:
            done_idx = self.state_combo.findData("done")
            if done_idx >= 0:
                self.state_combo.setCurrentIndex(done_idx)
        header_row.addWidget(self.state_combo, 0)
        self.state_combo.currentIndexChanged.connect(self._on_state_changed)
        left_layout.addLayout(header_row)

        # 2. Actividad (máx 50 caracteres)
        activity_label = QLabel("Actividad")
        activity_label.setObjectName("sectionLabel")
        left_layout.addWidget(activity_label)

        self.text_edit = QLineEdit()
        self.text_edit.setObjectName("taskQuickEditText")
        name = task.get("name", "")
        self.text_edit.setText(name[:50] if len(name) > 50 else name)
        self.text_edit.setMaxLength(50)
        self.text_edit.setPlaceholderText("Nombre de la actividad (máx. 50 caracteres)")
        self.text_edit.installEventFilter(self)
        left_layout.addWidget(self.text_edit)

        # 3. Fechas (al final)
        started_at = task.get("started_at")
        transitions = self.board.data.get("transitions", [])
        active_secs, detenido_secs = compute_time_in_columns(
            task.get("id", ""), transitions, self._current_col
        )
        if active_secs > 0 or detenido_secs > 0:
            time_text = (
                f"Inicio en In Progress: {format_date_display(started_at)}\n"
                f"Tiempo activo: {format_seconds_duration(active_secs)}  ·  "
                f"Tiempo detenido: {format_seconds_duration(detenido_secs)}"
            )
        else:
            entered_at = task.get("entered_at") or started_at
            time_text = (
                f"Inicio en In Progress: {format_date_display(started_at)}\n"
                f"En estado actual: {format_duration_in_activity(entered_at)}"
            )
        time_info = QLabel(time_text)
        time_info.setObjectName("taskTimeInfo")
        time_info.setWordWrap(True)
        left_layout.addWidget(time_info)

        # Ticket (código de solicitud externa) al final
        ticket_row = QHBoxLayout()
        ticket_label = QLabel("Ticket:")
        ticket_label.setObjectName("taskQuickEditInfo")
        ticket_row.addWidget(ticket_label, 0)
        self.ticket_edit = QLineEdit()
        self.ticket_edit.setObjectName("taskQuickEditText")
        self.ticket_edit.setText(task.get("ticket", ""))
        self.ticket_edit.setPlaceholderText("Ej: JIRA-123, INC-456 (código de solicitud externa)")
        self.ticket_edit.setMaxLength(32)
        self.ticket_edit.installEventFilter(self)
        ticket_row.addWidget(self.ticket_edit, 1)
        left_layout.addLayout(ticket_row)

        left_layout.addStretch()
        panels.addWidget(left_panel, 1)

        # Panel derecho: subtareas
        right_panel = QWidget()
        right_panel.setObjectName("detailRightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(0, 0, 0, 0)

        subtask_label = QLabel("Subtareas")
        subtask_label.setObjectName("sectionLabel")
        right_layout.addWidget(subtask_label)

        self._subtasks: list[dict] = [
            {"text": s.get("text", ""), "done": bool(s.get("done", False))}
            for s in task.get("subtasks", [])
        ]
        self._subtasks_container = QWidget()
        self._subtasks_container.setObjectName("subtasksContainer")
        self._subtasks_layout = QVBoxLayout(self._subtasks_container)
        self._subtasks_layout.setContentsMargins(0, 0, 0, 0)
        self._subtasks_layout.setSpacing(2)
        self._subtasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._rebuild_subtasks_ui()

        add_row = QHBoxLayout()
        self._subtask_input = QLineEdit()
        self._subtask_input.setObjectName("subtaskInput")
        self._subtask_input.setPlaceholderText("Añadir acción...")
        self._subtask_input.returnPressed.connect(self._on_add_subtask)
        self._subtask_input.installEventFilter(self)
        add_row.addWidget(self._subtask_input, 1)
        add_btn = QPushButton("Añadir")
        add_btn.setObjectName("secondaryBtn")
        add_btn.clicked.connect(self._on_add_subtask)
        add_row.addWidget(add_btn)
        right_layout.addLayout(add_row)

        scroll_wrapper = QWidget()
        scroll_wrapper.setObjectName("subtasksScrollWrapper")
        scroll_wrapper.setMinimumHeight(180)
        wrapper_layout = QVBoxLayout(scroll_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper_layout.addWidget(self._subtasks_container, 0, Qt.AlignmentFlag.AlignTop)
        wrapper_layout.addStretch()

        scroll = QScrollArea()
        scroll.setObjectName("subtasksScroll")
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setFixedHeight(180)
        scroll.setWidget(scroll_wrapper)
        right_layout.addWidget(scroll)

        right_layout.addStretch()
        panels.addWidget(right_panel, 1)

        layout.addLayout(panels)

        # Botones al final
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.setObjectName("saveBtnGradient")
        self.save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self.save_btn)

        btn_row.addStretch()
        delete_btn = QPushButton("Eliminar")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(delete_btn)
        layout.addLayout(btn_row)

    def _rebuild_subtasks_ui(self):
        while self._subtasks_layout.count():
            item = self._subtasks_layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        for i, st in enumerate(self._subtasks):
            row = QHBoxLayout()
            row.setSpacing(6)
            row.setContentsMargins(0, 0, 0, 0)

            def make_toggle(idx):
                def toggle():
                    if 0 <= idx < len(self._subtasks):
                        self._subtasks[idx]["done"] = not self._subtasks[idx]["done"]
                        self._rebuild_subtasks_ui()
                        self._persist_subtasks()
                return toggle

            check_btn = _SubtaskCheckButton(st["done"], make_toggle(i))
            row.addWidget(check_btn, 0)

            lbl = _SubtaskLabel(st["text"], st["done"], make_toggle(i))
            lbl.setObjectName("subtaskLabel")
            lbl.setProperty("done", "true" if st["done"] else "false")
            row.addWidget(lbl, 1)

            del_btn = QPushButton("Eliminar")
            del_btn.setObjectName("compactDangerBtn")
            del_btn.setToolTip("Eliminar subtarea")
            del_btn.clicked.connect(lambda _, idx=i: self._on_delete_subtask(idx))
            row.addWidget(del_btn, 0)

            wrap = QFrame()
            wrap.setObjectName("subtaskRow")
            wrap.setLayout(row)
            wrap.setFixedHeight(32)
            wrap.setProperty("done", "true" if st["done"] else "false")
            self._subtasks_layout.addWidget(wrap)

    def _persist_subtasks(self):
        """Guarda las subtareas inmediatamente en el backend."""
        self.board.update_task_subtasks(self.task_id, self._subtasks)

    def _on_add_subtask(self):
        text = self._subtask_input.text().strip()
        if not text:
            return
        self._subtasks.append({"text": text, "done": False})
        self._subtask_input.clear()
        self._rebuild_subtasks_ui()
        self._persist_subtasks()

    def _on_subtask_toggle(self, index: int, done: bool):
        if 0 <= index < len(self._subtasks):
            self._subtasks[index]["done"] = done
            self._rebuild_subtasks_ui()
            self._persist_subtasks()

    def _on_delete_subtask(self, index: int):
        if 0 <= index < len(self._subtasks):
            self._subtasks.pop(index)
            self._rebuild_subtasks_ui()
            self._persist_subtasks()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                if obj is self.state_combo or obj is self.state_combo.view():
                    return False
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if obj is self._subtask_input:
                    self._on_add_subtask()
                    return True
                if obj in (self.text_edit, self.ticket_edit):
                    self._on_save()
                    return True
                if obj is self.state_combo or obj is self.state_combo.view():
                    self._on_state_changed()
                    return True
        return super().eventFilter(obj, event)

    def _on_save(self):
        text = self.text_edit.text().strip()
        if not text:
            text = "Nueva tarea"
        ticket = self.ticket_edit.text().strip()
        ok_name = self.board.update_task_name(self.task_id, text)
        ok_ticket = self.board.update_task_ticket(self.task_id, ticket)
        ok_sub = self.board.update_task_subtasks(self.task_id, self._subtasks)
        if ok_name or ok_ticket or ok_sub:
            self._show_saved_effect()

    def _show_saved_effect(self):
        self.save_btn.setEnabled(False)
        self.save_btn.setText("✓ Guardado")
        self.save_btn.setProperty("saved", "true")
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)
        QTimer.singleShot(600, self._restore_save_btn)

    def _restore_save_btn(self):
        self.save_btn.setProperty("saved", "false")
        self.save_btn.setText("Guardar")
        self.save_btn.setEnabled(True)
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)
        self.on_close_callback()

    def _on_delete(self):
        reply = QMessageBox.question(
            self,
            "Eliminar tarea",
            "¿Eliminar esta tarea?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes and self.board.delete_task(self.task_id):
            self.on_close_callback()
            self.accept()

    def _on_state_changed(self):
        if not getattr(self, "_combo_ready", True):
            return
        self._on_move()

    def _on_move(self):
        target = self.state_combo.currentData()
        if not target:
            return
        text = self.text_edit.text().strip()
        if target == self._current_col:
            if self.board.get_task(self.task_id):
                self.board.update_task_name(self.task_id, text or "Nueva tarea")
                self.board.update_task_subtasks(self.task_id, self._subtasks)
            self.on_close_callback()
            self.accept()
            return
        if self.board.get_task(self.task_id):
            self.board.update_task_name(self.task_id, text or "Nueva tarea")
            self.board.update_task_subtasks(self.task_id, self._subtasks)
        if self.board.move_task(self.task_id, target):
            self.on_close_callback()
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "No se puede mover",
                f"La columna {col_key_to_display(target)} está llena.",
            )
