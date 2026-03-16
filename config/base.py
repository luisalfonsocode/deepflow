"""Constantes y valores por defecto de configuración."""

import sys
from pathlib import Path


def _get_resource_root() -> Path:
    """Dónde buscar recursos empaquetados (styles.qss, config/).
    PyInstaller 6+ en Windows/Linux: usa _internal (sys._MEIPASS).
    macOS .app: Contents/Resources.
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS).resolve()
        exe = Path(sys.executable).resolve()
        if sys.platform == "darwin" and "Contents/MacOS" in str(exe):
            return (exe.parent.parent / "Resources").resolve()
        return exe.parent
    return Path(__file__).parent.parent


def _get_exe_dir() -> Path:
    """Directorio del ejecutable. Para data_dir (./data) y datos de usuario."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).parent.parent


# Recursos empaquetados (estilos, config YAML)
RESOURCE_ROOT = _get_resource_root()

# Directorio del exe / proyecto. Base para data_dir y rutas relativas.
PROJECT_ROOT = _get_exe_dir()

# Entornos soportados
ENV_LOCAL = "local"
ENV_PRODUCTION = "production"

# Rutas por defecto (local)
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DB_DIR = DEFAULT_DATA_DIR / "db"
DEFAULT_DB_JSON = DEFAULT_DB_DIR / "deepflow_db.json"
DEFAULT_DB_ZODB = DEFAULT_DB_DIR / "deepflow_db.fs"

# Legacy (migración)
LEGACY_JSON_ROOT = PROJECT_ROOT / "deepflow_db.json"
LEGACY_MONOFLOW_JSON = PROJECT_ROOT / "monoflow_db.json"
LEGACY_MONOFLOW_JSON_DATA = DEFAULT_DATA_DIR / "monoflow_db.json"
LEGACY_MONOFLOW_FS = DEFAULT_DATA_DIR / "monoflow_db.fs"
