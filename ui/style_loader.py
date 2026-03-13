"""Carga de estilos; permite cambiar el tema sin tocar la lógica."""

from pathlib import Path


def load_styles(widget, stylesheet_path: Path | str | None = None) -> bool:
    """
    Aplica stylesheet al widget.
    Por defecto busca styles.qss en el directorio del proyecto.
    Retorna True si se cargó correctamente.
    """
    if stylesheet_path is None:
        base = Path(__file__).parent.parent
        stylesheet_path = base / "styles.qss"
    path = Path(stylesheet_path)
    if not path.exists():
        return False
    with open(path, encoding="utf-8") as f:
        widget.setStyleSheet(f.read())
    return True
