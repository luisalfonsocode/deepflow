"""
Pestaña Tiempo del módulo Reportes.
Desacoplada: emite data_requested(from_dt, to_dt); el contenedor busca datos y llama set_report_data.
"""

import colorsys
import math
from datetime import datetime, timedelta

from PyQt6.QtCore import QDate, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from domain.taskboard import TZ_APP
from domain.taskboard.date_ranges import month_range, week_range


class TimelineWidget(QWidget):
    """
    Línea de tiempo con una barra por tarea.
    Cada barra: fecha inicio (in_progress) → fecha fin (done).
    """

    ROW_HEIGHT = 28
    LABEL_WIDTH = 160
    AXIS_HEIGHT = 44
    LABELS_TOP = 8
    COLOR_ACTIVO = QColor("#2563eb")
    COLOR_DETENIDO = QColor("#dc2626")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._from_date = None
        self._to_date = None
        self._bars: list[dict] = []
        self.setMinimumWidth(400)

    def set_data(self, from_date: datetime, to_date: datetime, bars: list):
        self._from_date = from_date
        self._to_date = to_date
        self._bars = bars or []
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._from_date or not self._to_date or not self._bars:
            return
        total_secs = (self._to_date - self._from_date).total_seconds()
        if total_secs <= 0:
            return

        task_order = [
            (b.get("task_id", ""), ((b.get("task_name", "") or b.get("task_id", ""))[:30]))
            for b in self._bars
        ]
        n_rows = max(1, len(task_order))
        bar_area_width = max(200, self.width() - self.LABEL_WIDTH - 40)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bar_area_top = self.LABELS_TOP + self.AXIS_HEIGHT
        x0 = self.LABEL_WIDTH + 20

        num_ticks = 5
        painter.setPen(QColor("#64748b"))
        painter.setFont(self.font())
        for i in range(num_ticks + 1):
            frac = i / num_ticks if num_ticks > 0 else 0
            x_pos = x0 + bar_area_width * frac
            secs = frac * total_secs
            tick_date = self._from_date + timedelta(seconds=secs)
            label = tick_date.strftime("%d/%m")
            painter.drawText(
                int(x_pos) - 22, self.LABELS_TOP, 44, 20,
                Qt.AlignmentFlag.AlignCenter, label
            )

        painter.setPen(QPen(QColor("#e2e8f0"), 1))
        axis_y = bar_area_top - 4
        painter.drawLine(x0, axis_y, x0, bar_area_top + n_rows * self.ROW_HEIGHT)
        painter.drawLine(
            x0 + bar_area_width, axis_y,
            x0 + bar_area_width, bar_area_top + n_rows * self.ROW_HEIGHT,
        )
        for i in range(num_ticks + 1):
            frac = i / num_ticks if num_ticks > 0 else 0
            x_pos = x0 + bar_area_width * frac
            painter.drawLine(int(x_pos), axis_y, int(x_pos), axis_y + 6)

        for row, (tid, name) in enumerate(task_order):
            y = bar_area_top + row * self.ROW_HEIGHT
            painter.setPen(QColor("#64748b"))
            painter.drawText(4, y + 18, name[:25])

        task_to_row = {t[0]: i for i, t in enumerate(task_order)}
        for bar in self._bars:
            tid = bar.get("task_id", "")
            row = task_to_row.get(tid, 0)
            segments = bar.get("segments", [])
            if not segments:
                start_dt = bar.get("bar_start")
                end_dt = bar.get("bar_end")
                if start_dt and end_dt:
                    segments = [{"start": start_dt, "end": end_dt, "column_key": "in_progress"}]
            y = bar_area_top + row * self.ROW_HEIGHT + 4
            h = self.ROW_HEIGHT - 8
            for seg in segments:
                start_dt = seg.get("start")
                end_dt = seg.get("end")
                col_key = seg.get("column_key", "in_progress")
                if not start_dt or not end_dt:
                    continue
                start_sec = (start_dt - self._from_date).total_seconds()
                end_sec = (end_dt - self._from_date).total_seconds()
                x1 = x0 + bar_area_width * max(0, start_sec) / total_secs
                x2 = x0 + bar_area_width * min(total_secs, end_sec) / total_secs
                if x2 <= x1:
                    continue
                color = self.COLOR_DETENIDO if col_key == "detenido" else self.COLOR_ACTIVO
                painter.fillRect(QRectF(x1, y, x2 - x1, h), color)

        painter.end()

    def sizeHint(self):
        if not self._bars:
            return super().sizeHint()
        n = max(1, len(self._bars))
        w = self.LABEL_WIDTH + 500
        h = 8 + self.AXIS_HEIGHT + n * self.ROW_HEIGHT + 20
        return self.minimumSizeHint().expandedTo(QSize(w, h))


class PieChartWidget(QWidget):
    """Gráfico circular con % de tiempo por categoría. Tabla de tareas abajo."""

    LEGEND_ROW_HEIGHT = 24
    PIE_SIDE = 140
    MARGIN_TOP = 24
    PIE_LEGEND_GAP = 24
    MIN_SLICE_DEG = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[dict] = []
        self.setMinimumSize(380, 260)

    def _color_for_index(self, i: int, n: int) -> QColor:
        hue = (i / max(1, n)) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.92)
        return QColor(int(r * 255), int(g * 255), int(b * 255))

    def set_data(self, summary: list[dict]):
        """summary_by_categoria: [{categoria, pct_total, task_count, tiempo_dias}, ...]"""
        self._items = [s for s in (summary or []) if isinstance(s, dict)]
        if self._items:
            legend_h = 32 + len(self._items) * self.LEGEND_ROW_HEIGHT
            min_h = self.MARGIN_TOP + self.PIE_SIDE + self.PIE_LEGEND_GAP + legend_h
            self.setMinimumHeight(int(min_h))
        self.updateGeometry()
        self._schedule_paint()

    def _schedule_paint(self):
        """Garantiza repintado aunque el widget esté oculto."""
        self.update()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self.update)

    def showEvent(self, event):
        super().showEvent(event)
        self.update()

    def sizeHint(self):
        if not self._items:
            return super().sizeHint()
        n = len(self._items)
        legend_h = 32 + n * self.LEGEND_ROW_HEIGHT
        h = self.MARGIN_TOP + self.PIE_SIDE + self.PIE_LEGEND_GAP + legend_h
        return QSize(360, max(320, h))

    def paintEvent(self, event):
        super().paintEvent(event)
        items_pct = [
            (
                s.get("categoria", "(sin categoría)"),
                float(s.get("pct_total", 0)),
                int(s.get("task_count", 0)),
                float(s.get("tiempo_dias", 0)),
            )
            for s in self._items
        ]
        total = sum(p for _, p, _, _ in items_pct)
        if not items_pct:
            painter = QPainter(self)
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Sin datos")
            painter.end()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        r = self.rect()
        cx = r.center().x()
        rect = QRectF(cx - self.PIE_SIDE // 2, self.MARGIN_TOP, self.PIE_SIDE, self.PIE_SIDE)
        n = len(items_pct)

        start_deg = 0.0
        total_nonzero = total if total > 0 else 1
        for i, (label, pct, task_count, tiempo_dias) in enumerate(items_pct):
            if pct <= 0:
                continue
            span = 360.0 * (pct / total_nonzero)
            color = self._color_for_index(i, n)
            painter.setBrush(color)
            painter.setPen(QPen(QColor("#1e293b"), 1))
            painter.drawPie(rect, int(start_deg * 16), int(span * 16))

            mid_deg = start_deg + span / 2
            if span >= self.MIN_SLICE_DEG:
                rad = math.radians(mid_deg)
                r_inner = rect.width() * 0.32
                tx = rect.center().x() + r_inner * math.cos(rad) - 14
                ty = rect.center().y() - r_inner * math.sin(rad) + 4
                painter.setPen(QColor("#0f172a"))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawText(int(tx), int(ty), f"{pct:.0f}%")

            start_deg += span

        y0 = self.MARGIN_TOP + self.PIE_SIDE + self.PIE_LEGEND_GAP
        painter.setFont(self.font())
        col_cat = 8
        col_pct = max(80, r.width() - 220)
        col_tareas = max(130, r.width() - 160)
        col_dias = r.width() - 50
        painter.setPen(QColor("#475569"))
        painter.drawText(col_cat, y0 - 4, "Categoría")
        painter.drawText(col_pct, y0 - 4, "%")
        painter.drawText(col_tareas - 40, y0 - 4, "Tareas")
        painter.drawText(col_dias - 50, y0 - 4, "Tiempo (d)")
        painter.drawLine(8, y0 + 4, r.width() - 8, y0 + 4)

        for i, (label, pct, task_count, tiempo_dias) in enumerate(items_pct):
            y = y0 + 16 + (i + 1) * self.LEGEND_ROW_HEIGHT
            color = self._color_for_index(i, n)
            painter.setBrush(color)
            painter.drawRect(col_cat, y - 10, 10, 10)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor("#334155"))
            lbl = (label[:22] + "…") if len(label) > 22 else label
            painter.drawText(col_cat + 18, y + 2, lbl)
            painter.drawText(col_pct, y + 2, f"{pct:.1f}%")
            painter.drawText(col_tareas - 36, y + 2, str(task_count))
            painter.drawText(col_dias - 45, y + 2, f"{tiempo_dias:.1f}")

        painter.end()


class TimeReportTab(QWidget):
    """
    Pestaña Tiempo: filtros, timeline, pie, exportar.
    Desacoplada: emite data_requested(from_dt, to_dt).
    El contenedor debe conectar, obtener el reporte y llamar set_report_data(report).
    """

    data_requested = pyqtSignal(object, object)  # from_dt, to_dt

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()
        self._apply_period_dates()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Periodo:"))
        self.period_combo = QComboBox()
        self.period_combo.addItem("Esta semana", "week")
        self.period_combo.addItem("Este mes", "month")
        self.period_combo.addItem("Rango de fechas", "range")
        filter_row.addWidget(self.period_combo)

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        filter_row.addWidget(QLabel("Desde:"))
        filter_row.addWidget(self.from_date)
        filter_row.addWidget(QLabel("Hasta:"))
        filter_row.addWidget(self.to_date)
        self.from_date.hide()
        self.to_date.hide()

        self.range_label = QLabel()
        self.range_label.setObjectName("sectionLabel")
        filter_row.addWidget(self.range_label, 1)

        self.btn_refresh = QPushButton("Actualizar")
        self.btn_refresh.setObjectName("secondaryBtn")
        filter_row.addWidget(self.btn_refresh)

        self.btn_export_summary = QPushButton("Exportar resumen")
        self.btn_export_summary.setObjectName("secondaryBtn")
        self.btn_export_summary.setToolTip("Exporta resumen por categoría a Excel")
        filter_row.addWidget(self.btn_export_summary)

        self.btn_export_detail = QPushButton("Exportar detalle")
        self.btn_export_detail.setObjectName("secondaryBtn")
        self.btn_export_detail.setToolTip("Exporta detalle por tarea a Excel")
        filter_row.addWidget(self.btn_export_detail)

        layout.addLayout(filter_row)

        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 16, 0, 0)
        content_row.setSpacing(16)

        timeline_layout = QVBoxLayout()
        timeline_layout.addWidget(
            QLabel("Línea de tiempo (Inicio → Fin) — Azul: activo | Rojo: bloqueado")
        )
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True)
        timeline_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        timeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        timeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.timeline = TimelineWidget()
        self.timeline.setMinimumHeight(200)
        self.timeline.setMinimumWidth(400)
        timeline_scroll.setWidget(self.timeline)
        timeline_layout.addWidget(timeline_scroll, 1)
        content_row.addLayout(timeline_layout, 1)

        pie_layout = QVBoxLayout()
        pie_layout.setSpacing(12)
        pie_layout.setContentsMargins(0, 12, 0, 12)
        pie_layout.addWidget(QLabel("Tiempo por categoría (%)"))
        self.pie = PieChartWidget()
        pie_scroll = QScrollArea()
        pie_scroll.setWidgetResizable(True)
        pie_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        pie_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        pie_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        pie_scroll.setWidget(self.pie)
        pie_scroll.setMinimumWidth(360)
        pie_scroll.setMinimumHeight(400)
        pie_layout.addWidget(pie_scroll)
        pie_layout.addStretch()
        content_row.addLayout(pie_layout, 0)

        layout.addLayout(content_row, 1)

    def _connect_signals(self):
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        self.from_date.dateChanged.connect(self._on_range_date_changed)
        self.to_date.dateChanged.connect(self._on_range_date_changed)
        self.btn_refresh.clicked.connect(self._request_data)

    def _on_period_changed(self):
        is_range = self.period_combo.currentData() == "range"
        self.from_date.setVisible(is_range)
        self.to_date.setVisible(is_range)
        if not is_range:
            self._apply_period_dates()
        self._request_data()

    def _on_range_date_changed(self):
        if self.period_combo.currentData() == "range":
            self._request_data()

    def _apply_period_dates(self):
        """Actualiza from/to según periodo. NO modifica en modo range."""
        period = self.period_combo.currentData()
        if period == "range":
            return
        if period == "week":
            start, end = week_range()
        else:
            start, end = month_range()
        self.from_date.blockSignals(True)
        self.to_date.blockSignals(True)
        try:
            self.from_date.setDate(QDate(start.year, start.month, start.day))
            self.to_date.setDate(QDate(end.year, end.month, end.day))
        finally:
            self.from_date.blockSignals(False)
            self.to_date.blockSignals(False)

    def get_date_range(self) -> tuple[datetime, datetime]:
        """Retorna (from_dt, to_dt) para el periodo/fechas actuales."""
        period = self.period_combo.currentData()
        if period == "week":
            return week_range()
        if period == "month":
            return month_range()
        qd_from = self.from_date.date()
        qd_to = self.to_date.date()
        from_dt = datetime(
            qd_from.year(), qd_from.month(), qd_from.day(), 0, 0, 0, tzinfo=TZ_APP
        )
        to_dt = datetime(
            qd_to.year(), qd_to.month(), qd_to.day(), 23, 59, 59, tzinfo=TZ_APP
        )
        return (from_dt, to_dt)

    def _request_data(self):
        """Emite data_requested con el rango actual."""
        if self.period_combo.currentData() != "range":
            self._apply_period_dates()
        from_dt, to_dt = self.get_date_range()
        self.range_label.setText(
            f"{from_dt.strftime('%d/%m/%Y')} — {to_dt.strftime('%d/%m/%Y')}"
        )
        self.data_requested.emit(from_dt, to_dt)

    def set_report_data(self, report: dict):
        """Recibe el reporte y actualiza timeline y pie."""
        from_dt = report.get("from_date")
        to_dt = report.get("to_date")
        timeline_bars = report.get("timeline_bars", [])
        summary = report.get("summary_by_categoria", [])

        self.timeline.set_data(from_dt, to_dt, timeline_bars)
        self.pie.set_data(summary)

    def request_initial_data(self):
        """Llamar al mostrar el tab o al abrir Reportes. Inicializa fechas y pide datos."""
        self._apply_period_dates()
        self._request_data()
