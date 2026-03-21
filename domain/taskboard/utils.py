"""Utilidades de dominio TaskBoard (funciones puras)."""

from datetime import datetime, timedelta

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


def normalize_key_from_label(label: str) -> str:
    """Deriva key interno desde label: minúsculas, espacios→_, ñ→n."""
    s = (label or "").strip()
    if not s:
        return ""
    return s.lower().replace(" ", "_").replace("ñ", "n")


def format_duration_in_activity(entered_at: str | None) -> str:
    """
    Formato de duración: '5d' si >= 1 día, '5h' si < 1 día.
    entered_at → end_time = now. Legado; preferir format_task_duration.
    """
    return _format_duration_between(entered_at, None)


def format_task_duration(
    started_at: str | None,
    finished_at: str | None,
    column_key: str,
) -> str:
    """
    Duración de trabajo desde la primera vez en In Progress.
    - in_progress (abierto): started_at → ahora
    - done (cerrado): started_at → finished_at
    - resto: "-"
    started_at se establece solo la primera vez que llega a in_progress.
    """
    if not started_at:
        return "-"
    if column_key == "in_progress":
        return _format_duration_between(started_at, None)  # end = now
    if column_key == "done" and finished_at:
        return _format_duration_between(started_at, finished_at)
    return "-"


def format_duration_for_display(
    task_id: str,
    started_at: str | None,
    finished_at: str | None,
    column_key: str,
    transitions: list | None,
) -> str:
    """
    Duración para mostrar en UI según columna.
    - in_progress: tiempo activo (started_at → ahora)
    - detenido: tiempo acumulado en Detenido (desde transiciones)
    - done: tiempo hasta finalizar (started_at → finished_at)
    """
    if column_key == "in_progress":
        return format_task_duration(started_at, None, "in_progress")
    if column_key == "detenido":
        _, detenido_secs = compute_time_in_columns(task_id, transitions or [], "detenido")
        return format_seconds_duration(detenido_secs)
    if column_key == "done":
        return format_task_duration(started_at, finished_at, "done")
    return format_task_duration(started_at, finished_at, column_key)


def _format_duration_between(
    start_iso: str | None,
    end_iso: str | None,
) -> str:
    """Diferencia entre start y end (o now si end es None). Formato: '5d' o '5h'."""
    if not start_iso:
        return "-"
    try:
        start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=TZ_APP)
        else:
            start = start.astimezone(TZ_APP)
        end = datetime.now(TZ_APP) if not end_iso else datetime.fromisoformat(
            end_iso.replace("Z", "+00:00")
        )
        if end.tzinfo is None:
            end = end.replace(tzinfo=TZ_APP)
        else:
            end = end.astimezone(TZ_APP)
        diff = (end - start).total_seconds()
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


def _parse_ts(ts_str: str | None):
    """Parsea timestamp ISO a datetime en TZ_APP. None si falla."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=TZ_APP)
        return dt.astimezone(TZ_APP)
    except (ValueError, TypeError):
        return None


def compute_time_per_task_in_period(
    transitions: list[dict],
    from_date: datetime,
    to_date: datetime,
) -> dict[str, tuple[int, int]]:
    """
    Calcula (segundos_activo, segundos_detenido) por task_id en el rango [from_date, to_date].
    Solo cuenta tiempo que cae dentro del periodo.
    """
    from_date = from_date.replace(tzinfo=TZ_APP) if from_date.tzinfo is None else from_date
    to_date = to_date.replace(tzinfo=TZ_APP) if to_date.tzinfo is None else to_date
    now = datetime.now(TZ_APP)

    # Agrupar transiciones por task_id
    by_task: dict[str, list[dict]] = {}
    for t in transitions or []:
        if not t.get("task_id") or not t.get("timestamp"):
            continue
        tid = t["task_id"]
        if tid not in by_task:
            by_task[tid] = []
        by_task[tid].append(dict(t))

    result: dict[str, tuple[int, int]] = {}

    def clamp(start: datetime, end: datetime) -> int:
        """Segundos de [start, end] intersectado con [from_date, to_date]."""
        s = max(start, from_date)
        e = min(end, to_date)
        if s >= e:
            return 0
        return int((e - s).total_seconds())

    for task_id, trans_list in by_task.items():
        sorted_trans = sorted(trans_list, key=lambda x: x.get("timestamp", ""))
        active_secs = detenido_secs = 0
        col = sorted_trans[0].get("to_column")
        start = _parse_ts(sorted_trans[0]["timestamp"])
        if not start:
            continue

        for t in sorted_trans[1:]:
            ts = _parse_ts(t.get("timestamp", ""))
            if not ts:
                continue
            delta = clamp(start, ts)
            if col == "in_progress":
                active_secs += delta
            elif col == "detenido":
                detenido_secs += delta
            col = t.get("to_column")
            start = ts

        end_now = min(now, to_date)
        delta = clamp(start, end_now)
        if col == "in_progress":
            active_secs += delta
        elif col == "detenido":
            detenido_secs += delta

        if active_secs > 0 or detenido_secs > 0:
            result[task_id] = (active_secs, detenido_secs)

    return result


def compute_time_per_task_with_blocked_periods(
    board_data: dict,
    columns: list[str],
    transitions: list[dict],
    from_date: datetime,
    to_date: datetime,
) -> dict[str, tuple[int, int]]:
    """
    Calcula (active_secs, detenido_secs) por task_id combinando:
    - Barra temporal: started_at / finished_at (o now)
    - Detenido: transiciones (to_column=detenido) + task.blocked_periods
    Usa started_at/finished_at como fuente de verdad para la barra.
    """
    from_date = from_date.replace(tzinfo=TZ_APP) if from_date.tzinfo is None else from_date
    to_date = to_date.replace(tzinfo=TZ_APP) if to_date.tzinfo is None else to_date
    now = datetime.now(TZ_APP)

    time_from_trans = compute_time_per_task_in_period(transitions, from_date, to_date)
    time_from_dates = compute_time_per_task_from_task_dates(
        board_data, columns, from_date, to_date
    )

    result: dict[str, tuple[int, int]] = {}

    task_by_id: dict[str, dict] = {}
    for col in columns:
        for t in (board_data.get(col, []) or []):
            if isinstance(t, dict) and t.get("id"):
                task_by_id[t["id"]] = t

    for task_id, (total_secs, _) in time_from_dates.items():
        bar_start = bar_end = None
        task = task_by_id.get(task_id, {})
        if task:
            bar_start = _parse_ts(task.get("started_at"))
            bar_end = _parse_ts(task.get("finished_at")) or min(now, to_date)
        if not bar_start or not bar_end or bar_start >= bar_end:
            continue
        bar_start = max(bar_start, from_date)
        bar_end = min(bar_end, to_date)
        if bar_start >= bar_end:
            continue

        trans_detenido_stints = []
        stints = get_stints_per_task_in_period(transitions, from_date, to_date)
        for s in stints:
            if s.get("task_id") != task_id or s.get("column_key") != "detenido":
                continue
            start_s, end_s = s.get("start"), s.get("end")
            if not start_s or not end_s:
                continue
            s_c = max(start_s, bar_start)
            e_c = min(end_s, bar_end)
            if s_c < e_c:
                trans_detenido_stints.append({"start": s_c, "end": e_c})
        blocked_stints = get_blocked_period_stints_from_task(task, bar_start, bar_end)
        merged_stints = _merge_overlapping_detenido_stints(
            trans_detenido_stints + blocked_stints
        )
        merged_detenido = sum(
            int((s["end"] - s["start"]).total_seconds()) for s in merged_stints
        )
        active = max(0, total_secs - merged_detenido)
        result[task_id] = (active, merged_detenido)

    for task_id, (a, d) in time_from_trans.items():
        if task_id not in result and (a > 0 or d > 0):
            result[task_id] = (a, d)

    return result


def compute_time_per_task_from_task_dates(
    board_data: dict,
    columns: list[str],
    from_date: datetime,
    to_date: datetime,
) -> dict[str, tuple[int, int]]:
    """
    Calcula (active_secs, 0) por task_id usando started_at y finished_at de cada tarea.
    Incluye tanto tareas cerradas (con finished_at) como no cerradas (in_progress, detenido).
    Para tareas sin finished_at: bar_end = min(now, to_date).
    Prioridad sobre transiciones: las fechas editadas por el usuario son la fuente de verdad.
    Todo el tiempo se cuenta como activo; detenido_secs=0.
    """
    from_date = from_date.replace(tzinfo=TZ_APP) if from_date.tzinfo is None else from_date
    to_date = to_date.replace(tzinfo=TZ_APP) if to_date.tzinfo is None else to_date
    now = datetime.now(TZ_APP)

    result: dict[str, tuple[int, int]] = {}
    seen: set[str] = set()

    for col in columns:
        for t in (board_data.get(col, []) or []):
            if not isinstance(t, dict) or not t.get("id"):
                continue
            task_id = t["id"]
            if task_id in seen:
                continue
            started_iso = t.get("started_at")
            if not started_iso:
                continue
            bar_start = _parse_ts(started_iso)
            if not bar_start:
                continue
            seen.add(task_id)

            finished_iso = t.get("finished_at")
            bar_end = _parse_ts(finished_iso) if finished_iso else min(now, to_date)
            if not bar_end:
                bar_end = min(now, to_date)

            if bar_start >= to_date or bar_end <= from_date:
                continue
            s = max(bar_start, from_date)
            e = min(bar_end, to_date)
            if s >= e:
                continue
            secs = int((e - s).total_seconds())
            if secs > 0:
                result[task_id] = (secs, 0)

    return result


def get_blocked_period_stints_from_task(
    task: dict,
    bar_start: datetime,
    bar_end: datetime,
) -> list[dict]:
    """
    Parsea task.blocked_periods y retorna stints detenido en [bar_start, bar_end].
    Retorno: [{start, end, column_key: "detenido"}, ...]
    """
    periods = task.get("blocked_periods") or []
    if not periods or not bar_start or not bar_end:
        return []
    result = []
    for p in periods:
        if not isinstance(p, dict):
            continue
        start_dt = _parse_ts(p.get("start"))
        end_dt = _parse_ts(p.get("end"))
        if not start_dt or not end_dt or start_dt >= end_dt:
            continue
        s = max(start_dt, bar_start)
        e = min(end_dt, bar_end)
        if s < e:
            result.append({"start": s, "end": e, "column_key": "detenido"})
    return result


def _merge_overlapping_detenido_stints(stints: list[dict]) -> list[dict]:
    """Fusiona intervalos detenido solapados. Entrada y salida ordenados por start."""
    if not stints:
        return []
    sorted_stints = sorted(stints, key=lambda x: x.get("start") or datetime.min.replace(tzinfo=TZ_APP))
    merged = [dict(sorted_stints[0])]
    for s in sorted_stints[1:]:
        start, end = s.get("start"), s.get("end")
        if not start or not end:
            continue
        last = merged[-1]
        last_end = last.get("end")
        if last_end and start <= last_end:
            last["end"] = max(last_end, end)
        else:
            merged.append({"start": start, "end": end, "column_key": "detenido"})
    return merged


def merge_transition_and_blocked_stints(
    transition_stints: list[dict],
    blocked_stints: list[dict],
    bar_start: datetime,
    bar_end: datetime,
) -> list[dict]:
    """
    Combina stints de transiciones (in_progress y detenido) con stints de blocked_periods.
    Los blocked_periods se tratan como detenido. Fusiona intervalos detenido solapados.
    Retorno: lista de segmentos ordenados para el timeline.
    """
    detenido_from_trans = [s for s in transition_stints if s.get("column_key") == "detenido"]
    all_detenido = detenido_from_trans + blocked_stints
    merged_detenido = _merge_overlapping_detenido_stints(all_detenido)
    in_progress = [s for s in transition_stints if s.get("column_key") == "in_progress"]
    combined = sorted(
        in_progress + merged_detenido,
        key=lambda x: x.get("start") or bar_start,
    )
    return combined


def get_stints_per_task_in_period(
    transitions: list[dict],
    from_date: datetime,
    to_date: datetime,
) -> list[dict]:
    """
    Retorna lista de stints (períodos en columna) por tarea en el rango.
    Cada stint: {task_id, task_name, start, end, column_key}.
    Solo in_progress y detenido (para timeline).
    """
    from_date = from_date.replace(tzinfo=TZ_APP) if from_date.tzinfo is None else from_date
    to_date = to_date.replace(tzinfo=TZ_APP) if to_date.tzinfo is None else to_date
    now = datetime.now(TZ_APP)

    by_task: dict[str, list[dict]] = {}
    for t in transitions or []:
        if not t.get("task_id") or not t.get("timestamp"):
            continue
        tid = t["task_id"]
        if tid not in by_task:
            by_task[tid] = []
        by_task[tid].append(dict(t))

    result: list[dict] = []

    def clamp_interval(start: datetime, end: datetime) -> tuple[datetime, datetime] | None:
        s = max(start, from_date)
        e = min(end, to_date)
        if s >= e:
            return None
        return (s, e)

    for task_id, trans_list in by_task.items():
        sorted_trans = sorted(trans_list, key=lambda x: x.get("timestamp", ""))
        col = sorted_trans[0].get("to_column")
        start = _parse_ts(sorted_trans[0]["timestamp"])
        if not start:
            continue
        task_name = sorted_trans[0].get("task_name", "")

        for t in sorted_trans[1:]:
            ts = _parse_ts(t.get("timestamp", ""))
            if not ts:
                continue
            if col in ("in_progress", "detenido"):
                interval = clamp_interval(start, ts)
                if interval:
                    result.append({
                        "task_id": task_id,
                        "task_name": task_name,
                        "start": interval[0],
                        "end": interval[1],
                        "column_key": col,
                    })
            col = t.get("to_column")
            start = ts
            task_name = t.get("task_name", task_name)

        end_now = min(now, to_date)
        if col in ("in_progress", "detenido"):
            interval = clamp_interval(start, end_now)
            if interval:
                result.append({
                    "task_id": task_id,
                    "task_name": task_name,
                    "start": interval[0],
                    "end": interval[1],
                    "column_key": col,
                })

    return result


def get_task_bars_for_timeline(
    board_data: dict,
    columns: list[str],
    from_date: datetime,
    to_date: datetime,
) -> list[dict]:
    """
    Una barra por tarea usando started_at y finished_at de cada tarea.
    Incluye tareas cerradas y no cerradas (in_progress, detenido).
    Sin finished_at: bar_end = min(now, to_date).
    Solo tareas con started_at que se solapan con el periodo.
    """
    from_date = from_date.replace(tzinfo=TZ_APP) if from_date.tzinfo is None else from_date
    to_date = to_date.replace(tzinfo=TZ_APP) if to_date.tzinfo is None else to_date
    now = datetime.now(TZ_APP)

    result: list[dict] = []
    seen: set[str] = set()

    for col in columns:
        for t in (board_data.get(col, []) or []):
            if not isinstance(t, dict) or not t.get("id"):
                continue
            task_id = t["id"]
            if task_id in seen:
                continue
            started_iso = t.get("started_at")
            if not started_iso:
                continue
            bar_start = _parse_ts(started_iso)
            if not bar_start:
                continue
            seen.add(task_id)

            finished_iso = t.get("finished_at")
            bar_end = _parse_ts(finished_iso) if finished_iso else min(now, to_date)

            if bar_start >= to_date or bar_end <= from_date:
                continue
            bar_start_clamped = max(bar_start, from_date)
            bar_end_clamped = min(bar_end, to_date)
            if bar_start_clamped >= bar_end_clamped:
                continue

            result.append({
                "task_id": task_id,
                "task_name": t.get("name", "") or task_id,
                "bar_start": bar_start_clamped,
                "bar_end": bar_end_clamped,
                "started_at": bar_start,
                "finished_at": bar_end,
            })

    result.sort(key=lambda x: (x["bar_start"], x["task_name"]))
    return result


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


def default_blocked_period_start() -> str:
    """Inicio por defecto para tiempo bloqueado: hace 7 días, minutos redondeados a 0,10,20,30,40,50."""
    now = datetime.now(TZ_APP)
    start = now - timedelta(days=7)
    m = start.minute
    rounded_m = min(50, round(m / 10) * 10)
    start = start.replace(minute=int(rounded_m), second=0, microsecond=0)
    return start.isoformat()


def default_blocked_period_end() -> str:
    """Fin por defecto para tiempo bloqueado: ahora, minutos redondeados hacia abajo a 0,10,20,30,40,50."""
    now = datetime.now(TZ_APP)
    m = now.minute
    rounded_m = (m // 10) * 10
    now = now.replace(minute=rounded_m, second=0, microsecond=0)
    return now.isoformat()


def parse_date_to_iso(text: str) -> str | None:
    """
    Parsea texto a ISO 8601. Acepta:
    - dd/mm/yyyy o dd-mm-yyyy (ej: 13/03/2026)
    - dd/mm o dd-mm (ej: 13/03) → año actual
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
        if sep in date_part:
            p = date_part.split(sep)
            if len(p) >= 3:
                try:
                    d, m, y = int(p[0]), int(p[1]), int(p[2])
                    if 1 <= d <= 31 and 1 <= m <= 12 and 1900 <= y <= 2100:
                        dt = datetime(y, m, d, hour, minute, 0, tzinfo=TZ_APP)
                        return dt.isoformat()
                except (ValueError, TypeError, IndexError):
                    pass
            elif len(p) == 2:
                try:
                    d, m = int(p[0]), int(p[1])
                    if 1 <= d <= 31 and 1 <= m <= 12:
                        y = datetime.now(TZ_APP).year
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
