"""Constantes de dominio TaskBoard."""

from datetime import timezone, timedelta

COLUMNS = ("backlog", "todo", "in_progress", "done", "detenido")
WIP_LIMIT_PER_COLUMN = 3

# Zona horaria de la aplicación: GMT-5 (Colombia)
TZ_APP = timezone(timedelta(hours=-5))
