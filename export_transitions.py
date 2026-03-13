"""
Exporta tareas con started_at y finished_at a CSV.
Uso: python export_transitions.py [--output tareas.csv]
"""

import argparse
import csv
from pathlib import Path

from adapters.persistence import JsonFileBoardRepository
from core.modules.taskboard import BoardService


def main():
    parser = argparse.ArgumentParser(description="Exportar tareas (started_at, finished_at) a CSV")
    parser.add_argument(
        "-o", "--output",
        default="monoflow_tasks.csv",
        help="Archivo CSV de salida",
    )
    args = parser.parse_args()

    repository = JsonFileBoardRepository()
    board = BoardService(repository)
    tasks = board.get_tasks_with_timestamps()

    out_path = Path(args.output)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["task_id", "task_name", "started_at", "finished_at"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(tasks)

    print(f"Exportadas {len(tasks)} tareas a {out_path}")


if __name__ == "__main__":
    main()
