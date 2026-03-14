"""
Objeto de configuración unificado.
Acceso centralizado a rutas y opciones por entorno.
"""

from pathlib import Path

from config.base import ENV_LOCAL, ENV_PRODUCTION, PROJECT_ROOT
from config.loader import get_data_dir, get_environment, get_zodb_path_resolved


class Settings:
    """Configuración cargada según entorno."""

    def __init__(self) -> None:
        self._env = get_environment()
        self._data_dir = get_data_dir()
        self._zodb_path = get_zodb_path_resolved()

    @property
    def environment(self) -> str:
        """Entorno actual: local o production."""
        return self._env

    @property
    def is_local(self) -> bool:
        return self._env == ENV_LOCAL

    @property
    def is_production(self) -> bool:
        return self._env == ENV_PRODUCTION

    @property
    def data_dir(self) -> Path:
        """Directorio base de datos (data/)."""
        return self._data_dir

    @property
    def db_dir(self) -> Path:
        """Directorio de archivos de BD (data/db/)."""
        return self._data_dir / "db"

    @property
    def db_json_path(self) -> Path:
        """Ruta JSON legacy."""
        return self.db_dir / "deepflow_db.json"

    @property
    def db_zodb_path(self) -> Path:
        """Ruta ZODB por defecto (data/db/deepflow_db.fs)."""
        return self.db_dir / "deepflow_db.fs"

    @property
    def zodb_path(self) -> Path:
        """Ruta ZODB efectiva (resuelta con prioridades)."""
        return self._zodb_path

    # Rutas legacy para migraciones
    @property
    def legacy_json_path(self) -> Path:
        return PROJECT_ROOT / "deepflow_db.json"

    @property
    def db_path(self) -> Path:
        """Alias para json (load_board)."""
        return self.db_json_path

    @property
    def legacy_monoflow_json(self) -> Path:
        return PROJECT_ROOT / "monoflow_db.json"

    @property
    def legacy_monoflow_json_data(self) -> Path:
        return self._data_dir / "monoflow_db.json"

    @property
    def legacy_monoflow_fs(self) -> Path:
        return self._data_dir / "monoflow_db.fs"


# Singleton
settings = Settings()
