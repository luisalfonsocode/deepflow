"""
Módulo Widget: contenedor principal con la lista de funcionalidades.
Registro de módulos disponibles (taskboard, reports, alerts).
"""

from core.modules.widget.registry import MODULES, get_module_index

__all__ = ["MODULES", "get_module_index"]
