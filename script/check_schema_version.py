#!/usr/bin/env python3
"""
Muestra el schema_version de la base de datos DeepFlow.
Útil para saber en qué versión está prod antes de actualizar.

Uso:
  python script/check_schema_version.py                    # Usa data_dir por defecto
  python script/check_schema_version.py /ruta/a/data/db     # Ruta explícita
"""

import sys
from pathlib import Path

# Añadir raíz del proyecto al path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    db_path = None
    if len(sys.argv) >= 2:
        db_path = Path(sys.argv[1])
        if db_path.is_dir():
            db_path = db_path / "deepflow_db.fs"
        if not db_path.exists():
            print(f"Error: no existe {db_path}")
            sys.exit(1)
    else:
        # Usar config normal
        from config.loader import get_zodb_path_resolved
        db_path = get_zodb_path_resolved()
        if not db_path.exists():
            print(f"No existe la base de datos en {db_path}")
            print("Crea una tarea primero para que se genere.")
            sys.exit(1)

    import ZODB
    from ZODB import FileStorage
    storage = FileStorage.FileStorage(str(db_path), read_only=True)
    db = ZODB.DB(storage)
    conn = db.open()
    try:
        root = conn.root()
        version = root.get("schema_version", 1)
        from infrastructure.persistence.schema_versions import CURRENT_SCHEMA_VERSION
        print(f"Base de datos: {db_path}")
        print(f"Schema actual: v{version}")
        print(f"Schema esperado: v{CURRENT_SCHEMA_VERSION}")
        if version < CURRENT_SCHEMA_VERSION:
            print(f"→ Al abrir la app se migrará automáticamente a v{CURRENT_SCHEMA_VERSION}")
    finally:
        conn.close()
        db.close()


if __name__ == "__main__":
    main()
