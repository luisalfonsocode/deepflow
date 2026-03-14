"""Carga de estilos; permite cambiar el tema sin tocar la lógica."""

from pathlib import Path

from config.base import PROJECT_ROOT


def load_styles(widget, stylesheet_path: Path | str | None = None) -> bool:
    """
    Aplica stylesheet al widget.
    Por defecto busca styles.qss en la raíz de la app (proyecto o directorio del exe).
    Retorna True si se cargó correctamente.
    """
    if stylesheet_path is None:
        stylesheet_path = PROJECT_ROOT / "styles.qss"
    path = Path(stylesheet_path)
    if not path.exists():
        return False
    with open(path, encoding="utf-8") as f:
        widget.setStyleSheet(f.read())
    return True
