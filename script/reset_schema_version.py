#!/usr/bin/env python3
"""
Resetea schema_version en la BD a 1.
Útil para probar migraciones o forzar re-migración.

¡CUIDADO! Haz backup de data/db antes. La próxima vez que abras la app
se ejecutarán todas las migraciones (v1→v2→...→v6).

Uso:
  python script/reset_schema_version.py
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from config.loader import get_zodb_path_resolved
    db_path = get_zodb_path_resolved()
    if not db_path.exists():
        print(f"No existe la base de datos: {db_path}")
        sys.exit(1)

    import ZODB
    from ZODB import FileStorage
    import transaction

    storage = FileStorage.FileStorage(str(db_path), read_only=False)
    db = ZODB.DB(storage)
    conn = db.open()
    try:
        root = conn.root()
        old = root.get("schema_version", 1)
        root["schema_version"] = 1
        transaction.commit()
        print(f"Schema version: {old} → 1")
        print("La próxima vez que abras la app se migrará a v6.")
    finally:
        conn.close()
        db.close()


if __name__ == "__main__":
    main()
