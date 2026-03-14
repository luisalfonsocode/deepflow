"""
Configuración de logging para DeepFlow.
Se invoca al arrancar la aplicación.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging(
    level: str | int | None = None,
    log_file: Path | str | None = None,
) -> None:
    """
    Configura el logging de la aplicación.
    - level: DEBUG, INFO, WARNING, ERROR (por defecto INFO; DEBUG si DEEPFLOW_DEBUG=1)
    - log_file: si se proporciona, escribe también a archivo (ej. data/deepflow.log)
    """
    if level is None:
        level = logging.DEBUG if os.environ.get("DEEPFLOW_DEBUG") else logging.INFO
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = []
    stream = logging.StreamHandler(sys.stderr)
    stream.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    handlers.append(stream)

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
            handlers.append(fh)
        except OSError:
            pass

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
        force=True,
    )
    logging.getLogger("ZODB").setLevel(logging.WARNING)
    logging.getLogger("transaction").setLevel(logging.WARNING)
    logging.getLogger("BTrees").setLevel(logging.WARNING)
