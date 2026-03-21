"""Utilidades de fechas: rangos semana/mes para reportes."""

from datetime import datetime, timedelta

from domain.taskboard.constants import TZ_APP


def week_range() -> tuple[datetime, datetime]:
    """Inicio y fin de la semana actual (lunes 00:00 a domingo 23:59:59)."""
    now = datetime.now(TZ_APP)
    start = now - timedelta(days=now.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return (start, end)


def month_range() -> tuple[datetime, datetime]:
    """Inicio y fin del mes actual."""
    now = datetime.now(TZ_APP)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        end = start.replace(year=now.year + 1, month=1) - timedelta(seconds=1)
    else:
        end = start.replace(month=now.month + 1) - timedelta(seconds=1)
    return (start, end)
