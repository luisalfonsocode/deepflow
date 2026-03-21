"""Dashboard de pendientes: En progreso y Detenidas, máx 3 visibles cada una con scroll."""

from PyQt6.QtCore import Qt, QEvent, QObject, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from domain.taskboard.utils import format_duration_for_display
from presentation.modules.taskboard import CompactTaskRow, open_task_detail, open_task_create
from presentation.theme import ObjectNames

ROWS_VISIBLE = 3
ROW_HEIGHT = 34
ROW_SPACING = 4
# Altura exacta para mostrar 3 filas
LIST_HEIGHT = ROWS_VISIBLE * ROW_HEIGHT + (ROWS_VISIBLE - 1) * ROW_SPACING
WHEEL_STEP = ROW_HEIGHT + ROW_SPACING


class _SectionScrollFilter(QObject):
    """Reenvía rueda del mouse al scroll para desplazarse rápido sobre la sección."""

    def __init__(self, scroll_area: QScrollArea):
        super().__init__(scroll_area)
        self._scroll = scroll_area

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel and self._scroll.verticalScrollBar().isVisible():
            delta = event.angleDelta().y()
            if delta != 0:
                sb = self._scroll.verticalScrollBar()
                step = WHEEL_STEP * (2 if abs(delta) > 60 else 1)
                sb.setValue(sb.value() - (delta // 120) * step)
                return True
        return super().eventFilter(obj, event)


def _make_section_scrollarea(parent) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
    """Crea un QScrollArea con altura fija para 3 filas. Retorna (scroll, list_widget, list_layout)."""
    scroll = QScrollArea(parent)
    scroll.setObjectName("widgetTicketsScroll")
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setFixedHeight(LIST_HEIGHT)
    scroll.verticalScrollBar().setSingleStep(WHEEL_STEP)

    list_widget = QWidget()
    list_widget.setObjectName("sectionContent")
    list_layout = QVBoxLayout(list_widget)
    list_layout.setContentsMargins(12, 0, 12, 12)
    list_layout.setSpacing(ROW_SPACING)
    list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    scroll.setWidget(list_widget)
    return scroll, list_widget, list_layout


def _make_section_header(title: str, count: int, add_btn: QPushButton | None) -> tuple[QFrame, QLabel]:
    """Crea el encabezado de una sección con proporciones balanceadas."""
    frame = QFrame()
    frame.setObjectName("sectionBlock")
    frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(10, 6, 10, 6)
    layout.setSpacing(6)
    lbl = QLabel(title)
    lbl.setObjectName("sectionBlockLabel")
    layout.addWidget(lbl)
    count_lbl = QLabel(str(count))
    count_lbl.setObjectName("sectionBlockCount")
    layout.addWidget(count_lbl)
    layout.addStretch()
    if add_btn:
        layout.addWidget(add_btn)
    return frame, count_lbl


class InProgressCompact(QWidget):
    """Dashboard: En progreso y Detenidas. Máx 3 tareas visibles por sección, scroll para el resto."""

    def __init__(self, board, clipboard_provider, parent=None):
        super().__init__(parent)
        self.board = board
        self._clipboard = clipboard_provider
        self.setObjectName(ObjectNames.IN_PROGRESS_COMPACT)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("widgetCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Título del panel
        title = QLabel("Pendientes")
        title.setObjectName("dashboardCardTitle")
        card_layout.addWidget(title)

        # Contenedor de las dos columnas
        cols = QWidget()
        cols.setObjectName("dashboardColumnsWrapper")
        cols_layout = QHBoxLayout(cols)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(0)

        # === Columna Progreso ===
        prog_col = QWidget()
        prog_col.setObjectName("dashboardColumn")
        prog_col_layout = QVBoxLayout(prog_col)
        prog_col_layout.setContentsMargins(0, 0, 0, 0)
        prog_col_layout.setSpacing(0)
        self._add_btn = QPushButton("+")
        self._add_btn.setObjectName("compactCreateBtn")
        self._add_btn.setToolTip("Nueva tarea")
        self._add_btn.clicked.connect(self._on_add_task)
        prog_header, self._prog_count = _make_section_header("Progreso", 0, self._add_btn)
        prog_header.setProperty("section", "in_progress")
        prog_col_layout.addWidget(prog_header)
        self._prog_scroll, self._prog_list, self._prog_layout = _make_section_scrollarea(self)
        self._prog_list.setProperty("section", "in_progress")
        self._prog_scroll_filter = _SectionScrollFilter(self._prog_scroll)
        prog_header.installEventFilter(self._prog_scroll_filter)
        self._prog_list.installEventFilter(self._prog_scroll_filter)
        prog_col_layout.addWidget(self._prog_scroll)
        cols_layout.addWidget(prog_col, 1)

        # Separador
        sep = QFrame()
        sep.setObjectName("dashboardColumnSep")
        sep.setFixedWidth(1)
        cols_layout.addWidget(sep)

        # === Columna Detenido ===
        det_col = QWidget()
        det_col.setObjectName("dashboardColumn")
        det_col_layout = QVBoxLayout(det_col)
        det_col_layout.setContentsMargins(0, 0, 0, 0)
        det_col_layout.setSpacing(0)
        det_header, self._det_count = _make_section_header("Detenido", 0, None)
        det_header.setProperty("section", "detenidas")
        det_col_layout.addWidget(det_header)
        self._det_scroll, self._det_list, self._det_layout = _make_section_scrollarea(self)
        self._det_list.setProperty("section", "detenidas")
        self._det_scroll_filter = _SectionScrollFilter(self._det_scroll)
        det_header.installEventFilter(self._det_scroll_filter)
        self._det_list.installEventFilter(self._det_scroll_filter)
        det_col_layout.addWidget(self._det_scroll)
        cols_layout.addWidget(det_col, 1)

        card_layout.addWidget(cols)
        layout.addWidget(card, 1)

        self._refresh()

    def _clear_layout(self, layout: QVBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _refresh(self):
        self._clear_layout(self._prog_layout)
        self._clear_layout(self._det_layout)

        tasks_progress = self.board.data.get("in_progress", [])
        tasks_detenidas = self.board.data.get("detenido", [])

        self._prog_count.setText(str(len(tasks_progress)))
        self._det_count.setText(str(len(tasks_detenidas)))

        can_add = self.board.can_add_to("in_progress")
        self._add_btn.setEnabled(can_add)

        # En progreso
        for t in tasks_progress:
            row = CompactTaskRow(
                t.get("name", ""),
                started_at=t.get("started_at"),
                column_key="in_progress",
                on_click=lambda tid=t["id"]: self._on_task_click(tid),
                max_name_len=50,
                ticket=t.get("ticket", ""),
                section="in_progress",
            )
            row.installEventFilter(self._prog_scroll_filter)
            self._prog_layout.addWidget(row)
        if not tasks_progress:
            empty = QLabel("+ para crear")
            empty.setObjectName(ObjectNames.EMPTY_STATE)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._prog_layout.addWidget(empty)

        # Detenidas
        transitions = self.board.data.get("transitions", [])
        for t in tasks_detenidas:
            dur = format_duration_for_display(
                t["id"], t.get("started_at"), t.get("finished_at"), "detenido", transitions
            )
            row = CompactTaskRow(
                t.get("name", ""),
                started_at=t.get("started_at"),
                column_key="detenido",
                on_click=lambda tid=t["id"]: self._on_task_click(tid),
                max_name_len=50,
                ticket=t.get("ticket", ""),
                section="detenidas",
                duration_str=dur,
            )
            row.installEventFilter(self._det_scroll_filter)
            self._det_layout.addWidget(row)
        if not tasks_detenidas:
            empty = QLabel("—")
            empty.setObjectName(ObjectNames.EMPTY_STATE)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._det_layout.addWidget(empty)

    def refresh(self):
        self.board.load()
        self._refresh()

    def _on_task_click(self, task_id: str):
        def deferred_refresh():
            QTimer.singleShot(100, self._refresh)

        open_task_detail(
            self.board, task_id, on_close_callback=deferred_refresh, parent=self.window()
        )

    def _on_add_task(self):
        if not self.board.can_add_to("in_progress"):
            return
        open_task_create(
            self.board,
            "in_progress",
            on_close_callback=self._refresh,
            parent=self.window(),
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
