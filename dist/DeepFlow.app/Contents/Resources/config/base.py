"""Constantes y valores por defecto de configuración."""

import sys
from pathlib import Path


def _get_app_root() -> Path:
    """Raíz de la aplicación: directorio del exe (producción) o del proyecto (desarrollo).
    En macOS .app: usa Contents/Resources donde PyInstaller pone config y styles.
    """
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve()
        # macOS .app: exe está en App.app/Contents/MacOS/; recursos en Contents/Resources
        if sys.platform == "darwin" and "Contents/MacOS" in str(exe):
            return (exe.parent.parent / "Resources").resolve()
        return exe.parent
    return Path(__file__).parent.parent


# Raíz del proyecto (config/ está en la raíz)
PROJECT_ROOT = _get_app_root()

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
