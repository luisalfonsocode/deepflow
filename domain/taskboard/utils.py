"""Utilidades de dominio TaskBoard (funciones puras)."""

from datetime import datetime

from domain.taskboard.constants import TZ_APP


_COLUMN_DISPLAY = {
    "backlog": "Backlog",
    "todo": "To Do",
    "in_progress": "In Progress",
    "done": "Done",
    "detenido": "Detenido",
}
_DISPLAY_TO_COLUMN = {v: k for k, v in _COLUMN_DISPLAY.items()}


def column_key_to_display(key: str) -> str:
    """Convierte clave interna de columna a texto visible."""
    return _COLUMN_DISPLAY.get(key, key)


def display_to_column_key(display: str) -> str | None:
    """Convierte texto visible a clave interna. None si no existe."""
    val = (display or "").strip()
    return _DISPLAY_TO_COLUMN.get(val)


col_key_to_display = column_key_to_display


def format_duration_in_activity(entered_at: str | None) -> str:
    """
    Formato de duración en la actividad: '5d' si >= 1 día, '5h' si < 1 día.
    entered_at: ISO 8601 string (GMT-5).
    """
    if not entered_at:
        return "-"
    try:
        then = datetime.fromisoformat(entered_at.replace("Z", "+00:00"))
        now = datetime.now(TZ_APP)
        if then.tzinfo is None:
            then = then.replace(tzinfo=TZ_APP)
        else:
            then = then.astimezone(TZ_APP)
        diff = (now - then).total_seconds()
        if diff < 0:
            return "-"
        if diff >= 86400:
            return f"{int(diff // 86400)}d"
        hours = max(1, int(diff // 3600))
        return f"{hours}h"
    except (ValueError, TypeError):
        return "-"


_MESES = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")


def compute_time_in_columns(
    task_id: str, transitions: list[dict], current_column: str
) -> tuple[int, int]:
    """
    Calcula segundos en In Progress y en Detenido a partir de transiciones.
    Retorna (segundos_activo, segundos_detenido).
    """
    now = datetime.now(TZ_APP)
    task_transitions = sorted(
        [t for t in (transitions or []) if t.get("task_id") == task_id and t.get("timestamp")],
        key=lambda x: x["timestamp"],
    )
    if not task_transitions:
        return (0, 0)

    def parse_ts(s: str):
        try:
            dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=TZ_APP)
            return dt.astimezone(TZ_APP)
        except (ValueError, TypeError):
            return None

    active_secs = detenido_secs = 0
    col = task_transitions[0].get("to_column")
    start = parse_ts(task_transitions[0]["timestamp"])
    if not start:
        return (0, 0)

    for t in task_transitions[1:]:
        ts = parse_ts(t.get("timestamp", ""))
        if not ts:
            continue
        delta = max(0, (ts - start).total_seconds())
        if col == "in_progress":
            active_secs += delta
        elif col == "detenido":
            detenido_secs += delta
        col = t.get("to_column")
        start = ts

    delta = max(0, (now - start).total_seconds())
    if col == "in_progress":
        active_secs += delta
    elif col == "detenido":
        detenido_secs += delta
    return (int(active_secs), int(detenido_secs))


def format_seconds_duration(seconds: int) -> str:
    """Formato compacto: '5h', '2d', etc."""
    if seconds <= 0:
        return "-"
    if seconds >= 86400:
        return f"{seconds // 86400}d"
    return f"{max(1, seconds // 3600)}h"


def format_date_display(iso_string: str | None) -> str:
    """Formato de fecha legible en GMT-5: '13 Mar 2026'."""
    if not iso_string:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.astimezone(TZ_APP)
        else:
            dt = dt.replace(tzinfo=TZ_APP)
        return f"{dt.day:02d} {_MESES[dt.month - 1]} {dt.year}"
    except (ValueError, TypeError):
        return "-"


def iso_to_dd_mm_yyyy(iso_string: str | None) -> str:
    """Convierte ISO a dd/mm/yyyy para edición."""
    if not iso_string:
        return ""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.astimezone(TZ_APP)
        else:
            dt = dt.replace(tzinfo=TZ_APP)
        return f"{dt.day:02d}/{dt.month:02d}/{dt.year}"
    except (ValueError, TypeError):
        return ""


def iso_to_dd_mm_yyyy_hh_mm(iso_string: str | None) -> str:
    """Convierte ISO a dd/mm/yyyy HH:mm para edición (fecha + hora)."""
    if not iso_string:
        return ""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.astimezone(TZ_APP)
        else:
            dt = dt.replace(tzinfo=TZ_APP)
        return f"{dt.day:02d}/{dt.month:02d}/{dt.year} {dt.hour:02d}:{dt.minute:02d}"
    except (ValueError, TypeError):
        return ""


def parse_date_to_iso(text: str) -> str | None:
    """
    Parsea texto a ISO 8601. Acepta:
    - dd/mm/yyyy o dd-mm-yyyy (ej: 13/03/2026)
    - dd/mm/yyyy HH:mm (ej: 13/03/2026 14:30)
    - '13 Mar 2026' (formato display)
    - '2026-03-13'
    - '2026-03-13T10:30:00'
    Retorna ISO con timezone GMT-5; hora 12:00 si solo fecha, HH:mm si se indica.
    """
    t = (text or "").strip()
    if not t:
        return None
    raw = t[:25] if len(t) > 25 else t
    # Formato dd/mm/yyyy HH:mm o dd/mm/yyyy
    hour, minute = 12, 0
    date_part = raw
    if " " in raw:
        parts_space = raw.split(None, 1)
        date_part = parts_space[0]
        if len(parts_space) >= 2 and ":" in parts_space[1]:
            try:
                time_str = parts_space[1].strip()[:5]
                h, m = map(int, time_str.split(":"))
                if 0 <= h <= 23 and 0 <= m <= 59:
                    hour, minute = h, m
            except (ValueError, TypeError):
                pass
    for sep in ("/", "-"):
        if sep in date_part and date_part.count(sep) >= 2:
            p = date_part.split(sep)
            if len(p) >= 3:
                try:
                    d, m, y = int(p[0]), int(p[1]), int(p[2])
                    if 1 <= d <= 31 and 1 <= m <= 12 and 1900 <= y <= 2100:
                        dt = datetime(y, m, d, hour, minute, 0, tzinfo=TZ_APP)
                        return dt.isoformat()
                except (ValueError, TypeError, IndexError):
                    pass
            break
    # Formato "13 Mar 2026" (DD Mon YYYY)
    parts = raw.split()
    if len(parts) >= 3:
        for i, mes in enumerate(_MESES, 1):
            if mes in parts:
                try:
                    day = int(parts[0])
                    year = int(parts[2])
                    dt = datetime(year, i, day, 12, 0, 0, tzinfo=TZ_APP)
                    return dt.isoformat()
                except (ValueError, TypeError, IndexError):
                    pass
                break
    # ISO parcial: 2026-03-13 o 2026-03-13T10:30
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ_APP)
        else:
            dt = dt.astimezone(TZ_APP)
        return dt.isoformat()
    except (ValueError, TypeError):
        pass
    return None
