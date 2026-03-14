"""Capa de dominio: entidades, reglas de negocio, constantes."""

from domain.taskboard import COLUMNS, WIP_LIMIT_PER_COLUMN, col_key_to_display

__all__ = ["COLUMNS", "WIP_LIMIT_PER_COLUMN", "col_key_to_display"]
