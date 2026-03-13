"""
Exporta tareas con started_at y finished_at a CSV.
Uso: python -m scripts.export_transitions [--output tareas.csv]
"""

import argparse
import csv
import sys
from pathlib import Path

# Asegurar que el proyecto está en el path
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from adapters.persistence import ZODBBoardRepository
from adapters.persistence.json_to_zodb import migrate_json_to_zodb_if_needed
from core.modules.taskboard import BoardService
from core.modules.taskboard.constants import DB_PATH, DB_ZODB_PATH


def main():
    parser = argparse.ArgumentParser(
        description="Exportar tareas (started_at, finished_at) a CSV"
    )
    parser.add_argument(
        "-o", "--output",
        default="monoflow_tasks.csv",
        help="Archivo CSV de salida",
    )
    args = parser.parse_args()

    migrate_json_to_zodb_if_needed(DB_PATH)
    repo = ZODBBoardRepository(DB_ZODB_PATH)
    board = BoardService(repo)
    tasks = board.get_tasks_with_timestamps()

    out_path = Path(args.output)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["task_id", "ticket", "task_name", "started_at", "finished_at"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(tasks)

    print(f"Exportadas {len(tasks)} tareas a {out_path}")
    repo.close()


if __name__ == "__main__":
    main()
