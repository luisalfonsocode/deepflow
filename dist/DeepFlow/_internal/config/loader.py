"""
Carga configuración desde archivo YAML (deepflow.yaml).
Sin variables de entorno: todo desde el archivo de configuración.
En producción (ejecutable): busca config junto al exe.
"""

from pathlib import Path

from config.base import (
    DEFAULT_DATA_DIR,
    ENV_LOCAL,
    ENV_PRODUCTION,
    PROJECT_ROOT,
)

# YAML: en producción junto al exe (config/yaml/deepflow.yaml)
CONFIG_DIR = PROJECT_ROOT / "config" / "yaml"
CONFIG_PATH = CONFIG_DIR / "deepflow.yaml"


def _load_config() -> dict:
    """Carga deepflow.yaml. Retorna dict vacío si no existe o hay error."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        import yaml
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _get(key: str, default: str = "") -> str:
    """Obtiene valor del config."""
    cfg = _load_config()
    val = cfg.get(key, default)
    return str(val).strip() if val else default


def get_environment() -> str:
    """Entorno: local o production. Default: local."""
    env = _get("environment", ENV_LOCAL).lower()
    return env if env in (ENV_LOCAL, ENV_PRODUCTION) else ENV_LOCAL


def get_data_dir() -> Path:
    """Directorio de datos. Default: ./data.
    Rutas relativas se resuelven desde PROJECT_ROOT (exe dir en producción).
    """
    path = _get("data_dir")
    if path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = (PROJECT_ROOT / p).resolve()
        else:
            p = p.resolve()
        return p
    return DEFAULT_DATA_DIR


def get_zodb_path_resolved() -> Path:
    """
    Ruta del archivo ZODB.
    Prioridad:
    1. db_path en config (si está definido)
    2. Si existe deepflow_db.fs en data_dir/db/
    3. Si existe monoflow_db.fs (legacy)
    4. data_dir/db/deepflow_db.fs
    """
    db_path = _get("db_path")
    if db_path:
        p = Path(db_path).expanduser()
        if not p.is_absolute():
            p = (PROJECT_ROOT / p).resolve()
        else:
            p = p.resolve()
        return p

    data_dir = get_data_dir()
    db_dir = data_dir / "db"
    default_zodb = db_dir / "deepflow_db.fs"
    legacy_fs = data_dir / "monoflow_db.fs"

    if default_zodb.exists():
        return default_zodb
    if legacy_fs.exists():
        return legacy_fs
    return default_zodb
