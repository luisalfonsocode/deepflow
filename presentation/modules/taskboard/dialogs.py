"""Diálogos del módulo TaskBoard. Modal unificado de detalle/edición de tarea."""

from PyQt6.QtCore import QEvent, QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from presentation.widgets_common import ComboBoxNoWheelUnfocused

from datetime import datetime

from application.taskboard import BoardService
from domain.taskboard.constants import TZ_APP
from domain.taskboard.utils import (
    compute_time_in_columns,
    default_blocked_period_end,
    default_blocked_period_start,
    format_date_display,
    format_seconds_duration,
    format_task_duration,
    iso_to_dd_mm_yyyy_hh_mm,
    parse_date_to_iso,
)

_FMT_FECHA_HORA = "dd/mm/aaaa hh:mm (ej: 21/03/2025 14:30)"
from presentation.style_loader import load_styles
from presentation.theme import Layout


class _SubtaskDoneBtn(QPushButton):
    """Botón compacto para marcar como completada (✓) o pendiente (○). Mismo estilo que eliminar."""

    def __init__(self, checked: bool, on_toggled, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("subtaskDoneBtn")
        self.setFixedSize(24, 24)
        self._checked = checked
        self._on_toggled = on_toggled
        self.clicked.connect(self._toggle)
        self._refresh()

    def _toggle(self):
        self._checked = not self._checked
        self._refresh()
        self._on_toggled(self._checked)

    def _refresh(self):
        self.setText("✓" if self._checked else "○")
        self.setToolTip("Desmarcar" if self._checked else "Marcar como completada")
        self.setProperty("checked", "true" if self._checked else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class _SubtaskNameDisplay(QWidget):
    """Muestra el nombre como label; doble clic activa edición con QLineEdit."""

    def __init__(self, text: str, done: bool, on_text_changed, parent=None):
        super().__init__(parent)
        self._on_text_changed = on_text_changed
        self._done = done
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._stack = QStackedWidget()
        self._label = QLabel(text[:200] if text else "")
        self._label.setObjectName("subtaskNameLabel")
        self._label.setWordWrap(False)
        self._label.setCursor(Qt.CursorShape.IBeamCursor)
        self._label.installEventFilter(self)
        self._edit = QLineEdit()
        self._edit.setObjectName("subtaskNameEdit")
        self._edit.setPlaceholderText("Nombre de la subtarea")
        self._edit.setMaxLength(200)
        self._edit.editingFinished.connect(self._finish_edit)
        self._edit.returnPressed.connect(self._edit.clearFocus)
        self._stack.addWidget(self._label)
        self._stack.addWidget(self._edit)
        layout.addWidget(self._stack, 1)
        self._update_done_style()

    def _update_done_style(self):
        for w in (self._label, self._edit):
            w.setProperty("done", "true" if self._done else "false")
            w.style().unpolish(w)
            w.style().polish(w)

    def set_done(self, done: bool):
        self._done = done
        self._update_done_style()

    def _on_double_click(self):
        self._edit.setText(self._label.text())
        self._stack.setCurrentWidget(self._edit)
        self._edit.setFocus()
        self._edit.selectAll()

    def _finish_edit(self):
        new_text = self._edit.text().strip()
        if new_text:
            self._label.setText(new_text)
            self._on_text_changed()
        self._stack.setCurrentWidget(self._label)

    def get_text(self) -> str:
        return self._edit.text().strip() if self._stack.currentWidget() is self._edit else self._label.text()

    def set_text(self, text: str):
        self._label.setText(text[:200] if text else "")

    def eventFilter(self, obj, event):
        if obj is self._label and event.type() == QEvent.Type.MouseButtonDblClick:
            self._on_double_click()
            return True
        return super().eventFilter(obj, event)


class _SubtaskListWidget(QListWidget):
    """Lista de subtareas con drag-and-drop para reordenar."""

    def __init__(self, on_order_changed, parent=None):
        super().__init__(parent)
        self._on_order_changed = on_order_changed
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setFrameShape(QListWidget.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSpacing(2)

    def dropEvent(self, event):
        super().dropEvent(event)
        self._on_order_changed()


def open_task_detail(board: BoardService, task_id: str, on_close_callback, parent=None) -> bool:
    """
    Abre el modal unificado de detalle/edición de tarea.
    Retorna True si se aceptó, False si se rechazó o la tarea no existe.
    """
    dialog = TaskDetailDialog(board, task_id=task_id, on_close_callback=on_close_callback, parent=parent)
    load_styles(dialog)
    return dialog.exec() == dialog.DialogCode.Accepted


def open_task_create(board: BoardService, column_key: str, on_close_callback, parent=None, initial_text: str = "") -> bool:
    """
    Abre el mismo modal que edición pero en modo creación.
    Oculta campos que no aplican (estado fijo, fechas, eliminar).
    initial_text: texto previo para el campo Actividad (ej. del portapapeles).
    """
    dialog = TaskDetailDialog(
        board,
        task_id=None,
        on_close_callback=on_close_callback,
        parent=parent,
        column_key=column_key,
        initial_text=initial_text or "",
    )
    load_styles(dialog)
    return dialog.exec() == dialog.DialogCode.Accepted


class TaskDetailDialog(QDialog):
    """
    Modal unificado de detalle y edición de tarea.
    Usado desde: widget compacto, TaskBoard (clic en tarjeta), Summary.
    En modo creación (task_id=None, column_key dado): mismo componente, ocultando campos no aplicables.
    """

    def __init__(
        self,
        board,
        task_id: str | None = None,
        on_close_callback=None,
        parent=None,
        column_key: str | None = None,
        initial_text: str = "",
    ):
        super().__init__(parent)
        self.board = board
        self.task_id = task_id
        self.on_close_callback = on_close_callback or (lambda: None)
        self._create_mode = task_id is None and column_key is not None
        self._current_col = column_key if self._create_mode else (board.get_task_column(task_id) or "in_progress")
        self._initial_text = (initial_text or "")[:100]

        self.setWindowTitle("Nueva tarea" if self._create_mode else "Tarea")
        self.setModal(True)
        self.setMinimumSize(Layout.TASK_DETAIL_MIN_WIDTH, Layout.TASK_DETAIL_MIN_HEIGHT)
        self.resize(Layout.TASK_DETAIL_DEFAULT_WIDTH, Layout.TASK_DETAIL_DEFAULT_HEIGHT)

        self._restore_timer = None
        self._is_showing_saved = False
        if not self._create_mode:
            task = board.get_task(task_id)
            if not task:
                self.reject()
                return
        else:
            task = {"name": self._initial_text}

        self._combo_ready = False
        self._build_ui(task)
        self._combo_ready = True

        load_styles(self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self._is_showing_saved:
                event.accept()
                return
            event.accept()
            self._cancel_restore_timer()
            QTimer.singleShot(0, self.reject)
            return
        super().keyPressEvent(event)

    def _cancel_restore_timer(self):
        """Cancela el timer de _restore_save_btn para evitar segfault al cerrar con ESC."""
        if getattr(self, "_restore_timer", None) is not None:
            self._restore_timer.stop()
            self._restore_timer = None
        self._is_showing_saved = False

    def reject(self):
        self._cancel_restore_timer()
        super().reject()

    def _make_master_combo(self, master_key: str, current_value: str):
        """Crea QComboBox poblado desde el maestro. Incluye opción vacía y valor actual si no está en la lista."""
        items = self.board.get_master_list(master_key)
        combo = ComboBoxNoWheelUnfocused()
        combo.setObjectName("stateCombo")
        combo.addItem("", "")
        labels = set()
        for it in items:
            label = it.get("label", "")
            if label and label not in labels:
                combo.addItem(label, it.get("key", label))
                labels.add(label)
        if current_value and current_value not in labels:
            combo.insertItem(1, current_value, current_value)
        idx = combo.findText(current_value) if current_value else 0
        if idx >= 0:
            combo.setCurrentIndex(idx)
        return combo

    def _add_section_frame(self, title: str, layout: QVBoxLayout) -> QFrame:
        """Crea un frame de sección con título y añade al layout."""
        frame = QFrame()
        frame.setObjectName("detailSection")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 10, 12, 10)
        frame_layout.setSpacing(8)
        lbl = QLabel(title)
        lbl.setObjectName("sectionLabel")
        frame_layout.addWidget(lbl)
        layout.addWidget(frame)
        return frame

    def _add_field_row(self, parent_layout, label_text: str, widget, stretch_widget: bool = True):
        """Añade fila label + widget con alineación consistente."""
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label_text + ":")
        lbl.setObjectName("taskQuickEditInfo")
        lbl.setMinimumWidth(85)
        row.addWidget(lbl, 0)
        row.addWidget(widget, 1 if stretch_widget else 0)
        parent_layout.addLayout(row)

    def _build_ui(self, task: dict):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Contenido scrolleable
        scroll = QScrollArea()
        scroll.setObjectName("detailScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(340)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(16, 16, 16, 12)
        scroll.setWidget(scroll_content)

        panels = QHBoxLayout()
        panels.setSpacing(20)
        panels.setContentsMargins(0, 0, 0, 0)

        left_panel = QWidget()
        left_panel.setObjectName("detailLeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # === ZONA 1: Identificación ===
        sec_id = self._add_section_frame("Identificación", left_layout)
        sec_id_layout = sec_id.layout()

        self.text_edit = QLineEdit()
        self.text_edit.setObjectName("taskQuickEditText")
        name = task.get("name", "")
        self.text_edit.setText(name[:100] if len(name) > 100 else name)
        self.text_edit.setMaxLength(100)
        self.text_edit.setPlaceholderText("Nombre de la actividad")
        self.text_edit.installEventFilter(self)
        self._add_field_row(sec_id_layout, "Actividad", self.text_edit)

        cat_row = QHBoxLayout()
        cat_label = QLabel("Categoría:")
        cat_label.setObjectName("taskQuickEditInfo")
        cat_label.setMinimumWidth(85)
        cat_row.addWidget(cat_label, 0)
        self.categoria_combo = self._make_master_combo("categoria", task.get("categoria", ""))
        self.categoria_combo.installEventFilter(self)
        cat_row.addWidget(self.categoria_combo, 1)
        sec_id_layout.addLayout(cat_row)

        state_row = QHBoxLayout()
        state_label = QLabel("Estado:")
        state_label.setObjectName("taskQuickEditInfo")
        state_label.setMinimumWidth(85)
        state_row.addWidget(state_label, 0)
        if self._create_mode:
            state_static = QLabel(self.board.col_key_to_display(self._current_col))
            state_static.setObjectName("taskQuickEditInfo")
            state_row.addWidget(state_static, 0)
            self.state_combo = None
        else:
            self.state_combo = ComboBoxNoWheelUnfocused()
            self.state_combo.setObjectName("stateCombo")
            self.state_combo.installEventFilter(self)
            self.state_combo.view().installEventFilter(self)
            self.board.load()
            for col in self.board.get_column_keys():
                if self.board.can_add_to(col) or col == self._current_col:
                    self.state_combo.addItem(self.board.col_key_to_display(col), col)
            current_idx = self.state_combo.findData(self._current_col)
            if current_idx >= 0:
                self.state_combo.setCurrentIndex(current_idx)
            else:
                done_idx = self.state_combo.findData("done")
                if done_idx >= 0:
                    self.state_combo.setCurrentIndex(done_idx)
            state_row.addWidget(self.state_combo, 0)
            self.state_combo.currentIndexChanged.connect(self._on_state_changed)
        sec_id_layout.addLayout(state_row)

        # === ZONA 2: Fechas y tiempos ===
        sec_fechas = self._add_section_frame("Fechas y tiempos", left_layout)
        sec_fechas_layout = sec_fechas.layout()

        if not self._create_mode:
            started_at = task.get("started_at")
            transitions = self.board.data.get("transitions", [])
            active_secs, detenido_secs = compute_time_in_columns(
                task.get("id", ""), transitions, self._current_col
            )

            # --- Atención: fechas de inicio y fin de la atención ---
            atencion_label = QLabel("Atención (inicio y fin)")
            atencion_label.setObjectName("detailSectionSubtitle")
            sec_fechas_layout.addWidget(atencion_label)

            started_row = QHBoxLayout()
            started_row.setSpacing(8)
            sl = QLabel("Inicio:")
            sl.setObjectName("taskQuickEditInfo")
            sl.setMinimumWidth(85)
            started_row.addWidget(sl, 0)
            self.started_at_edit = QLineEdit()
            self.started_at_edit.setObjectName("taskQuickEditText")
            self.started_at_edit.setText(iso_to_dd_mm_yyyy_hh_mm(started_at) if started_at else "")
            self.started_at_edit.setPlaceholderText(_FMT_FECHA_HORA)
            self.started_at_edit.setMaxLength(18)
            self.started_at_edit.installEventFilter(self)
            started_row.addWidget(self.started_at_edit, 1)
            sec_fechas_layout.addLayout(started_row)

            finished_at = task.get("finished_at")
            finished_row = QHBoxLayout()
            finished_row.setSpacing(8)
            fl = QLabel("Fin:")
            fl.setObjectName("taskQuickEditInfo")
            fl.setMinimumWidth(85)
            finished_row.addWidget(fl, 0)
            self.finished_at_edit = QLineEdit()
            self.finished_at_edit.setObjectName("taskQuickEditText")
            self.finished_at_edit.setText(iso_to_dd_mm_yyyy_hh_mm(finished_at) if finished_at else "")
            self.finished_at_edit.setPlaceholderText("dd/mm/aaaa hh:mm — opcional")
            self.finished_at_edit.setMaxLength(18)
            self.finished_at_edit.installEventFilter(self)
            finished_row.addWidget(self.finished_at_edit, 1)
            fin_clear = QPushButton("✕")
            fin_clear.setObjectName("compactDangerBtn")
            fin_clear.setFixedSize(24, 24)
            fin_clear.setToolTip("Quitar fecha de fin")
            fin_clear.clicked.connect(lambda: self.finished_at_edit.clear())
            finished_row.addWidget(fin_clear, 0)
            sec_fechas_layout.addLayout(finished_row)

            if active_secs > 0 or detenido_secs > 0:
                time_text = (
                    f"Tiempo activo: {format_seconds_duration(active_secs)}  ·  "
                    f"Tiempo detenido: {format_seconds_duration(detenido_secs)}"
                )
            else:
                time_text = f"Duración: {format_task_duration(started_at, task.get('finished_at'), self._current_col)}"
            time_info = QLabel(time_text)
            time_info.setObjectName("taskTimeInfo")
            time_info.setWordWrap(True)
            sec_fechas_layout.addWidget(time_info)

            # --- Fecha de compromiso ---
            self.due_date_edit = QLineEdit()
            self.due_date_edit.setObjectName("taskQuickEditText")
            due_raw = task.get("due_date", "")
            self.due_date_edit.setText(iso_to_dd_mm_yyyy_hh_mm(due_raw) if due_raw else "")
            self.due_date_edit.setPlaceholderText("dd/mm/aaaa hh:mm (opcional)")
            self.due_date_edit.setMaxLength(18)
            self.due_date_edit.installEventFilter(self)
            self._add_field_row(sec_fechas_layout, "Fecha de compromiso", self.due_date_edit)

            # --- Tiempo detenido: períodos bloqueados ---
            detenido_label = QLabel("Tiempo detenido")
            detenido_label.setObjectName("detailSectionSubtitle")
            sec_fechas_layout.addWidget(detenido_label)
            blocked_hint = QLabel("Períodos en que la tarea estuvo bloqueada o pausada (dd/mm/aaaa hh:mm):")
            blocked_hint.setObjectName("detailSectionHint")
            blocked_hint.setWordWrap(True)
            sec_fechas_layout.addWidget(blocked_hint)
            self._blocked_periods_container = QWidget()
            self._blocked_periods_layout = QVBoxLayout(self._blocked_periods_container)
            self._blocked_periods_layout.setContentsMargins(0, 2, 0, 0)
            self._blocked_periods_layout.setSpacing(4)
            self._blocked_period_rows: list[tuple[QLineEdit, QLineEdit, QPushButton]] = []
            for p in task.get("blocked_periods") or []:
                self._add_blocked_period_row(
                    iso_to_dd_mm_yyyy_hh_mm(p.get("start", "")),
                    iso_to_dd_mm_yyyy_hh_mm(p.get("end", "")),
                )
            add_blocked_btn = QPushButton("+ Añadir tiempo bloqueado")
            add_blocked_btn.setObjectName("taskQuickEditBtn")
            add_blocked_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_blocked_btn.clicked.connect(lambda: self._add_blocked_period_row("", ""))
            self._blocked_periods_layout.addWidget(add_blocked_btn)
            sec_fechas_layout.addWidget(self._blocked_periods_container)
        else:
            # Modo creación: solo fecha de compromiso
            self.due_date_edit = QLineEdit()
            self.due_date_edit.setObjectName("taskQuickEditText")
            due_raw = task.get("due_date", "")
            self.due_date_edit.setText(iso_to_dd_mm_yyyy_hh_mm(due_raw) if due_raw else "")
            self.due_date_edit.setPlaceholderText("dd/mm/aaaa hh:mm (opcional)")
            self.due_date_edit.setMaxLength(18)
            self.due_date_edit.installEventFilter(self)
            self._add_field_row(sec_fechas_layout, "Fecha de compromiso", self.due_date_edit)

        left_layout.addStretch()
        panels.addWidget(left_panel, 1)

        # === Panel derecho: Metadatos + Subtareas ===
        right_panel = QWidget()
        right_panel.setObjectName("detailRightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Metadatos (arriba)
        sec_meta = self._add_section_frame("Metadatos", right_layout)
        sec_meta_layout = sec_meta.layout()

        ticket_prio_row = QHBoxLayout()
        ticket_prio_row.setSpacing(8)
        tl = QLabel("Ticket:")
        tl.setObjectName("taskQuickEditInfo")
        tl.setMinimumWidth(85)
        ticket_prio_row.addWidget(tl, 0)
        self.ticket_edit = QLineEdit()
        self.ticket_edit.setObjectName("taskQuickEditText")
        self.ticket_edit.setText(task.get("ticket", ""))
        self.ticket_edit.setPlaceholderText("JIRA-123")
        self.ticket_edit.setMaxLength(32)
        self.ticket_edit.installEventFilter(self)
        ticket_prio_row.addWidget(self.ticket_edit, 1)
        self.priority_check = QCheckBox("Prioridad")
        self.priority_check.setChecked(bool(task.get("prioridad", False)))
        self.priority_check.installEventFilter(self)
        ticket_prio_row.addWidget(self.priority_check, 0)
        sec_meta_layout.addLayout(ticket_prio_row)

        self.tribe_combo = self._make_master_combo("tribu_squad", task.get("tribe_and_squad", ""))
        self.tribe_combo.installEventFilter(self)
        self._add_field_row(sec_meta_layout, "Tribu y Squad", self.tribe_combo)

        self.requester_combo = self._make_master_combo("solicitante", task.get("solicitante") or task.get("requester", ""))
        self.requester_combo.installEventFilter(self)
        self._add_field_row(sec_meta_layout, "Solicitante", self.requester_combo)

        self.reporting_channel_combo = self._make_master_combo("canal_reporte", task.get("reporting_channel") or task.get("origen", ""))
        self.reporting_channel_combo.installEventFilter(self)
        self._add_field_row(sec_meta_layout, "Canal de reporte", self.reporting_channel_combo)

        # Subtareas: añadir al inicio, luego lista
        subtask_label = QLabel("Subtareas")
        subtask_label.setObjectName("sectionLabel")
        right_layout.addWidget(subtask_label)

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

        raw_subs = task.get("subtasks") or []
        valid_subs = [s for s in raw_subs if isinstance(s, dict)]
        valid_subs.sort(key=lambda x: x.get("order", 999))
        self._subtasks = [
            {"text": s.get("name", s.get("text", "")), "done": bool(s.get("done", False))}
            for s in valid_subs
        ]
        self._subtasks_list = _SubtaskListWidget(self._sync_subtasks_from_list, parent=right_panel)
        self._subtasks_list.setObjectName("subtasksList")
        self._subtasks_list.setMinimumHeight(100)
        self._subtasks_list.setMaximumHeight(180)
        right_layout.addWidget(self._subtasks_list)

        self._rebuild_subtasks_ui()

        right_layout.addStretch()
        panels.addWidget(right_panel, 1)

        scroll_layout.addLayout(panels)

        # Botones fijos al pie
        btn_container = QWidget()
        btn_container.setObjectName("detailFooter")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(12, 10, 12, 12)
        btn_layout.setSpacing(0)
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Crear" if self._create_mode else "Guardar")
        self.save_btn.setObjectName("saveBtnGradient")
        self.save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self.save_btn)

        btn_row.addStretch()
        if not self._create_mode:
            delete_btn = QPushButton("Eliminar")
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(self._on_delete)
            btn_row.addWidget(delete_btn)
        btn_layout.addLayout(btn_row)

        layout.addWidget(scroll)
        layout.addWidget(btn_container)

    def _add_blocked_period_row(self, start_text: str = "", end_text: str = ""):
        """Añade una fila de período bloqueado (Inicio, Fin, Eliminar).
        Si ambos vacíos: inicio = hace 7 días (min redondeados a :00,:10,:20,:30,:40,:50),
        fin = ahora (min redondeados hacia abajo)."""
        if not hasattr(self, "_blocked_period_rows"):
            return
        if not start_text and not end_text:
            start_text = iso_to_dd_mm_yyyy_hh_mm(default_blocked_period_start())
            end_text = iso_to_dd_mm_yyyy_hh_mm(default_blocked_period_end())
        row = QHBoxLayout()
        row.setSpacing(6)
        row.setContentsMargins(0, 0, 0, 0)
        start_edit = QLineEdit()
        start_edit.setObjectName("taskQuickEditText")
        start_edit.setPlaceholderText("dd/mm/aaaa hh:mm o dd/mm (año actual)")
        start_edit.setMaxLength(18)
        start_edit.setText(start_text)
        end_edit = QLineEdit()
        end_edit.setObjectName("taskQuickEditText")
        end_edit.setPlaceholderText("dd/mm/aaaa hh:mm o dd/mm (año actual)")
        end_edit.setMaxLength(18)
        end_edit.setText(end_text)
        del_btn = QPushButton("✕")
        del_btn.setObjectName("compactDangerBtn")
        del_btn.setFixedWidth(28)
        del_btn.setToolTip("Eliminar período")
        row.addWidget(start_edit, 1)
        row.addWidget(end_edit, 1)
        row.addWidget(del_btn, 0)
        row_widget = QWidget()
        row_widget.setLayout(row)
        self._blocked_period_rows.append((start_edit, end_edit, del_btn))
        insert_idx = max(0, self._blocked_periods_layout.count() - 1)
        self._blocked_periods_layout.insertWidget(insert_idx, row_widget)

        def on_delete():
            idx = next(
                (i for i, (s, e, b) in enumerate(self._blocked_period_rows)
                 if b is del_btn),
                -1,
            )
            if idx >= 0:
                self._blocked_period_rows.pop(idx)
                row_widget.setParent(None)
                row_widget.deleteLater()

        del_btn.clicked.connect(on_delete)

    def _rebuild_subtasks_ui(self):
        self._subtasks_list.clear()
        self._subtask_names = []
        for i, st in enumerate(self._subtasks):
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, st)
            item.setSizeHint(self._size_hint_for_subtask_row())

            def make_toggle(idx):
                def toggle(checked):
                    if 0 <= idx < len(self._subtasks):
                        self._subtasks[idx]["done"] = checked
                        self._rebuild_subtasks_ui()
                        self._persist_subtasks()
                return toggle

            def make_text_update(idx):
                def update():
                    if 0 <= idx < len(self._subtask_names) and idx < len(self._subtasks):
                        new_text = self._subtask_names[idx].get_text().strip()
                        if new_text:
                            self._subtasks[idx]["text"] = new_text
                            self._persist_subtasks()
                return update

            row = QHBoxLayout()
            row.setSpacing(4)
            row.setContentsMargins(4, 2, 4, 2)
            grip = QLabel("⋮⋮")
            grip.setObjectName("subtaskGrip")
            grip.setToolTip("Arrastrar para reordenar")
            grip.setFixedWidth(14)
            grip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            row.addWidget(grip, 0)
            done_btn = _SubtaskDoneBtn(st["done"], make_toggle(i))
            row.addWidget(done_btn, 0)
            name_display = _SubtaskNameDisplay(
                st.get("text", ""), st["done"], make_text_update(i)
            )
            self._subtask_names.append(name_display)
            row.addWidget(name_display, 1)
            del_btn = QPushButton("✕")
            del_btn.setObjectName("compactDangerBtn")
            del_btn.setFixedSize(24, 24)
            del_btn.setToolTip("Eliminar subtarea")
            del_btn.clicked.connect(lambda _, idx=i: self._on_delete_subtask(idx))
            row.addWidget(del_btn, 0)

            wrap = QWidget()
            wrap.setObjectName("subtaskRow")
            wrap.setLayout(row)
            wrap.setProperty("done", "true" if st["done"] else "false")
            self._subtasks_list.addItem(item)
            self._subtasks_list.setItemWidget(item, wrap)

    def _size_hint_for_subtask_row(self):
        return QSize(200, 32)

    def _sync_subtasks_from_list(self):
        """Sincroniza _subtasks con el orden actual del list widget (tras drag-and-drop)."""
        new_order = []
        for i in range(self._subtasks_list.count()):
            item = self._subtasks_list.item(i)
            st = item.data(Qt.ItemDataRole.UserRole)
            if st is not None:
                w = self._subtasks_list.itemWidget(item)
                if w and w.layout() and w.layout().count() >= 4:
                    name_w = w.layout().itemAt(2).widget()
                    if name_w and hasattr(name_w, "get_text"):
                        st["text"] = name_w.get_text().strip()
                new_order.append(st)
        if new_order != self._subtasks:
            self._subtasks[:] = new_order
            self._persist_subtasks()

    def _sync_subtasks_from_edits(self):
        """Sincroniza el texto actual de los nombres a _subtasks (antes de guardar)."""
        for i, name_w in enumerate(getattr(self, "_subtask_names", [])):
            if i < len(self._subtasks) and hasattr(name_w, "get_text"):
                self._subtasks[i]["text"] = name_w.get_text().strip()

    def _persist_subtasks(self):
        """Guarda las subtareas inmediatamente en el backend (solo en edición)."""
        if not self._create_mode:
            self._sync_subtasks_from_edits()
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
            if key == Qt.Key.Key_Escape:
                if self._is_showing_saved:
                    event.accept()
                    return True
                event.accept()
                self._cancel_restore_timer()
                QTimer.singleShot(0, self.reject)
                return True
            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                if self.state_combo and (obj is self.state_combo or obj is self.state_combo.view()):
                    return False
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if obj is self._subtask_input:
                    self._on_add_subtask()
                    return True
                save_objs = [
                    self.text_edit,
                    self.ticket_edit,
                    self.due_date_edit,
                    self.tribe_combo,
                    self.requester_combo,
                    self.reporting_channel_combo,
                    self.categoria_combo,
                ]
                if hasattr(self, "priority_check") and self.priority_check:
                    save_objs.append(self.priority_check)
                if hasattr(self, "started_at_edit") and self.started_at_edit:
                    save_objs.append(self.started_at_edit)
                if hasattr(self, "finished_at_edit") and self.finished_at_edit:
                    save_objs.append(self.finished_at_edit)
                if obj in save_objs:
                    self._on_save()
                    return True
                if self.state_combo and (obj is self.state_combo or obj is self.state_combo.view()):
                    self._on_state_changed()
                    return True
        return super().eventFilter(obj, event)

    def _on_save(self):
        text = self.text_edit.text().strip()
        if not text:
            text = "Nueva tarea"
        ticket = self.ticket_edit.text().strip()
        tribe = (self.tribe_combo.currentText() or "").strip()
        requester = (self.requester_combo.currentText() or "").strip()
        reporting_channel = (self.reporting_channel_combo.currentText() or "").strip()
        due_date_raw = self.due_date_edit.text().strip()
        due_date = ""
        if due_date_raw:
            due_date = parse_date_to_iso(due_date_raw) or ""
            if not due_date:
                QMessageBox.warning(self, "Formato inválido", f"Fecha de compromiso: formato requerido {_FMT_FECHA_HORA}")
                return

        if self._create_mode:
            task = self.board.create_task_in(text, self._current_col)
            if not task:
                QMessageBox.warning(
                    self,
                    "No se puede crear",
                    f"La columna {self.board.col_key_to_display(self._current_col)} está llena (límite WIP alcanzado)."
                )
                return
            self.task_id = task["id"]
            self.board.update_task_ticket(self.task_id, ticket)
            self.board.update_task_prioridad(self.task_id, self.priority_check.isChecked())
            self.board.update_task_tribe_and_squad(self.task_id, tribe)
            self.board.update_task_solicitante(self.task_id, requester)
            self.board.update_task_reporting_channel(self.task_id, reporting_channel)
            self.board.update_task_categoria(self.task_id, self.categoria_combo.currentText().strip())
            self.board.update_task_due_date(self.task_id, due_date)
            if self._subtasks:
                self._sync_subtasks_from_edits()
                self.board.update_task_subtasks(self.task_id, self._subtasks)
            self.on_close_callback()
            self._cancel_restore_timer()
            self.accept()
        else:
            ok_name = self.board.update_task_name(self.task_id, text)
            ok_ticket = self.board.update_task_ticket(self.task_id, ticket)
            ok_priority = self.board.update_task_prioridad(self.task_id, self.priority_check.isChecked())
            ok_tribe = self.board.update_task_tribe_and_squad(self.task_id, tribe)
            ok_req = self.board.update_task_solicitante(self.task_id, requester)
            ok_chan = self.board.update_task_reporting_channel(self.task_id, reporting_channel)
            ok_cat = self.board.update_task_categoria(self.task_id, self.categoria_combo.currentText().strip())
            ok_due = self.board.update_task_due_date(self.task_id, due_date)
            self._sync_subtasks_from_edits()
            ok_sub = self.board.update_task_subtasks(self.task_id, self._subtasks)

            # Inicio y Fin (datetime picker)
            ok_started = False
            if hasattr(self, "started_at_edit"):
                started_raw = self.started_at_edit.text().strip()
                if started_raw:
                    started_iso = parse_date_to_iso(started_raw)
                    if not started_iso:
                        QMessageBox.warning(self, "Formato inválido", f"Inicio: formato requerido {_FMT_FECHA_HORA}")
                        return
                    ok_started = self.board.update_task_started_at(self.task_id, started_iso)

            ok_finished = False
            if hasattr(self, "finished_at_edit"):
                finished_raw = self.finished_at_edit.text().strip()
                finished_iso = parse_date_to_iso(finished_raw) if finished_raw else ""
                if finished_raw and not finished_iso:
                    QMessageBox.warning(self, "Formato inválido", f"Fin: formato requerido {_FMT_FECHA_HORA}")
                    return
                ok_finished = self.board.update_task_finished_at(self.task_id, finished_iso or "")

            # Períodos bloqueados
            ok_blocked = False
            if hasattr(self, "_blocked_period_rows"):
                periods = []
                for start_edit, end_edit, _ in self._blocked_period_rows:
                    start_raw = start_edit.text().strip()
                    end_raw = end_edit.text().strip()
                    if start_raw and end_raw:
                        start_iso = parse_date_to_iso(start_raw)
                        end_iso = parse_date_to_iso(end_raw)
                        if start_iso and end_iso and start_iso < end_iso:
                            periods.append({"start": start_iso, "end": end_iso})
                        else:
                            QMessageBox.warning(
                                self,
                                "Período inválido",
                                f"Inicio y fin deben ser fechas válidas con inicio antes que fin.\n"
                                f"Fila: {start_raw} – {end_raw}"
                            )
                            return
                    elif start_raw or end_raw:
                        QMessageBox.warning(
                            self,
                            "Período incompleto",
                            "Cada período debe tener inicio y fin, o elimina la fila vacía."
                        )
                        return
                ok_blocked = self.board.update_task_blocked_periods(self.task_id, periods)

            if ok_name or ok_ticket or ok_priority or ok_tribe or ok_req or ok_chan or ok_cat or ok_due or ok_sub or ok_started or ok_finished or ok_blocked:
                self._show_saved_effect()

    def _show_saved_effect(self):
        self._cancel_restore_timer()
        self._is_showing_saved = True
        self.save_btn.setEnabled(False)
        self.save_btn.setText("✓ Guardado")
        self.save_btn.setProperty("saved", "true")
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)
        self._restore_timer = QTimer(self)
        self._restore_timer.setSingleShot(True)
        self._restore_timer.timeout.connect(self._restore_save_btn)
        self._restore_timer.start(600)

    def _restore_save_btn(self):
        self._is_showing_saved = False
        self.save_btn.setProperty("saved", "false")
        self.save_btn.setText("Guardar")
        self.save_btn.setEnabled(True)
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)
        # No llamar on_close_callback aquí: evita segfault al pulsar ESC
        # El tablero se refresca al cerrar el diálogo (open_task_detail retorna)

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
            self._cancel_restore_timer()
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
        ticket = self.ticket_edit.text().strip()
        tribe = (self.tribe_combo.currentText() or "").strip()
        requester = (self.requester_combo.currentText() or "").strip()
        reporting_channel = (self.reporting_channel_combo.currentText() or "").strip()
        categoria = (self.categoria_combo.currentText() or "").strip()
        due_date_raw = self.due_date_edit.text().strip()
        due_date = (parse_date_to_iso(due_date_raw) or "") if due_date_raw else ""
        if due_date_raw and not due_date:
            QMessageBox.warning(self, "Formato inválido", f"Fecha de compromiso: formato requerido {_FMT_FECHA_HORA}")
            return
        if target == self._current_col:
            if self.board.get_task(self.task_id):
                self.board.update_task_name(self.task_id, text or "Nueva tarea")
                self.board.update_task_ticket(self.task_id, ticket)
                self.board.update_task_prioridad(self.task_id, self.priority_check.isChecked())
                self.board.update_task_tribe_and_squad(self.task_id, tribe)
                self.board.update_task_solicitante(self.task_id, requester)
                self.board.update_task_reporting_channel(self.task_id, reporting_channel)
                self.board.update_task_categoria(self.task_id, categoria)
                self.board.update_task_due_date(self.task_id, due_date)
                self._sync_subtasks_from_edits()
                self.board.update_task_subtasks(self.task_id, self._subtasks)
                if hasattr(self, "started_at_edit"):
                    started_raw = self.started_at_edit.text().strip()
                    if started_raw and (iso_val := parse_date_to_iso(started_raw)):
                        self.board.update_task_started_at(self.task_id, iso_val)
                if hasattr(self, "finished_at_edit"):
                    finished_raw = self.finished_at_edit.text().strip()
                    self.board.update_task_finished_at(
                        self.task_id, parse_date_to_iso(finished_raw) or "" if finished_raw else ""
                    )
                if hasattr(self, "_blocked_period_rows"):
                    periods = []
                    for start_edit, end_edit, _ in self._blocked_period_rows:
                        start_raw, end_raw = start_edit.text().strip(), end_edit.text().strip()
                        if start_raw and end_raw:
                            start_iso = parse_date_to_iso(start_raw)
                            end_iso = parse_date_to_iso(end_raw)
                            if start_iso and end_iso and start_iso < end_iso:
                                periods.append({"start": start_iso, "end": end_iso})
                    self.board.update_task_blocked_periods(self.task_id, periods)
                # Si está en Done sin fecha de fin y no la editaron, asignar ahora
                if target == "done":
                    task = self.board.get_task(self.task_id)
                    finished_raw = self.finished_at_edit.text().strip() if hasattr(self, "finished_at_edit") else ""
                    if not task.get("finished_at") and not (finished_raw and parse_date_to_iso(finished_raw)):
                        self.board.update_task_finished_at(
                            self.task_id, datetime.now(TZ_APP).isoformat()
                        )
            self.on_close_callback()
            self._cancel_restore_timer()
            self.accept()
            return
        # Validar formatos de fechas antes de mover
        if hasattr(self, "started_at_edit"):
            started_raw = self.started_at_edit.text().strip()
            if started_raw and not parse_date_to_iso(started_raw):
                QMessageBox.warning(self, "Formato inválido", f"Inicio: formato requerido {_FMT_FECHA_HORA}")
                return
        if hasattr(self, "finished_at_edit"):
            finished_raw = self.finished_at_edit.text().strip()
            if finished_raw and not parse_date_to_iso(finished_raw):
                QMessageBox.warning(self, "Formato inválido", f"Fin: formato requerido {_FMT_FECHA_HORA}")
                return

        if self.board.get_task(self.task_id):
            self.board.update_task_name(self.task_id, text or "Nueva tarea")
            self.board.update_task_ticket(self.task_id, ticket)
            self.board.update_task_prioridad(self.task_id, self.priority_check.isChecked())
            self.board.update_task_tribe_and_squad(self.task_id, tribe)
            self.board.update_task_solicitante(self.task_id, requester)
            self.board.update_task_reporting_channel(self.task_id, reporting_channel)
            self.board.update_task_categoria(self.task_id, categoria)
            self.board.update_task_due_date(self.task_id, due_date)
            self._sync_subtasks_from_edits()
            self.board.update_task_subtasks(self.task_id, self._subtasks)
            if hasattr(self, "started_at_edit"):
                started_raw = self.started_at_edit.text().strip()
                if started_raw and (iso_val := parse_date_to_iso(started_raw)):
                    self.board.update_task_started_at(self.task_id, iso_val)
            if hasattr(self, "finished_at_edit"):
                finished_raw = self.finished_at_edit.text().strip()
                self.board.update_task_finished_at(
                    self.task_id, parse_date_to_iso(finished_raw) or "" if finished_raw else ""
                )
            if hasattr(self, "_blocked_period_rows"):
                periods = []
                for start_edit, end_edit, _ in self._blocked_period_rows:
                    start_raw, end_raw = start_edit.text().strip(), end_edit.text().strip()
                    if start_raw and end_raw:
                        start_iso = parse_date_to_iso(start_raw)
                        end_iso = parse_date_to_iso(end_raw)
                        if start_iso and end_iso and start_iso < end_iso:
                            periods.append({"start": start_iso, "end": end_iso})
                self.board.update_task_blocked_periods(self.task_id, periods)
        if self.board.move_task(self.task_id, target):
            self.on_close_callback()
            self._cancel_restore_timer()
            self.accept()
        else:
            self.state_combo.blockSignals(True)
            idx = self.state_combo.findData(self._current_col)
            if idx >= 0:
                self.state_combo.setCurrentIndex(idx)
            self.state_combo.blockSignals(False)
            QMessageBox.warning(
                self,
                "No se puede mover",
                f"La columna {self.board.col_key_to_display(target)} está llena (límite WIP alcanzado)."
            )
