"""Carga de estilos; permite cambiar el tema sin tocar la lógica."""

from pathlib import Path

from config.base import PROJECT_ROOT, RESOURCE_ROOT


def _find_styles_path() -> Path | None:
    """Busca styles.qss en recursos (_internal) o junto al exe."""
    for base in (RESOURCE_ROOT, PROJECT_ROOT):
        p = base / "styles.qss"
        if p.exists():
            return p
    return None


def load_styles(widget, stylesheet_path: Path | str | None = None) -> bool:
    """
    Aplica stylesheet al widget.
    Busca styles.qss en RESOURCE_ROOT (_internal) o PROJECT_ROOT (exe dir).
    Retorna True si se cargó correctamente.
    """
    if stylesheet_path is None:
        path = _find_styles_path()
        if path is None:
            return False
    else:
        path = Path(stylesheet_path)
        if not path.exists():
            return False
    with open(path, encoding="utf-8") as f:
        widget.setStyleSheet(f.read())
    return True
