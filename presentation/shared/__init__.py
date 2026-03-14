"""Componentes compartidos de la capa de presentación."""

from presentation.shared.dnd import (
    extract_task_id_from_mime,
    is_deepflow_drag,
    DeepFlowDropTargetMixin,
)

__all__ = [
    "extract_task_id_from_mime",
    "is_deepflow_drag",
    "DeepFlowDropTargetMixin",
]
