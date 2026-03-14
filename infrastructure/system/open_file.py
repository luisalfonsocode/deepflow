"""Abrir archivos con la aplicación predeterminada del sistema."""

import logging
import os
import subprocess
import sys
from pathlib import Path

LOG = logging.getLogger(__name__)


def open_with_default_app(filepath: Path) -> None:
    """Abre el archivo con la aplicación predeterminada del sistema."""
    path_str = str(filepath.resolve())
    try:
        if sys.platform == "win32":
            os.startfile(path_str)
        elif sys.platform == "darwin":
            subprocess.run(["open", path_str], check=False)
        else:
            subprocess.run(["xdg-open", path_str], check=False)
    except Exception as e:
        LOG.warning("No se pudo abrir %s: %s", path_str, e)
