"""
Configuración de persistencia.
Delega a config.settings (soporta local/production via .env).
Mantiene nombres legacy para compatibilidad con json_to_zodb, json_file, etc.
"""

from pathlib import Path

from config import settings

# Re-export para compatibilidad
DATA_DIR = settings.data_dir
DB_DIR = settings.db_dir
DB_PATH = settings.db_path
DB_ZODB_PATH = settings.db_zodb_path
LEGACY_JSON_PATH = settings.legacy_json_path
LEGACY_MONOFLOW_JSON = settings.legacy_monoflow_json
LEGACY_MONOFLOW_JSON_DATA = settings.legacy_monoflow_json_data
LEGACY_MONOFLOW_FS = settings.legacy_monoflow_fs


def get_zodb_path() -> Path:
    """Ruta ZODB efectiva (configurada via .env / DEEPFLOW_DB_PATH)."""
    return settings.zodb_path
