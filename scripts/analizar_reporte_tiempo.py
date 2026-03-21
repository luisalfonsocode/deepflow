#!/usr/bin/env python3
"""
Diagnóstico: analiza la data del reporte de tiempo.
Ejecutar desde la raíz: python scripts/analizar_reporte_tiempo.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Añadir raíz al path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from domain.taskboard import TZ_APP
from domain.taskboard.date_ranges import month_range, week_range
from domain.taskboard.utils import compute_time_per_task_in_period


def load_board_data():
    """Carga datos desde ZODB."""
    from application.taskboard.board_service import BoardService
    from infrastructure.persistence.zodb_repository import ZODBBoardRepository

    db_path = ROOT / "data" / "db" / "deepflow_db.fs"
    if not db_path.exists():
        print(f"⚠ No existe {db_path}")
        return None
    repo = ZODBBoardRepository(db_path)
    board = BoardService(repo)
    board.load()
    # BoardService.data añade columnas al top level
    data = board.data
    repo.close()
    return data


def main():
    data = load_board_data()
    if not data:
        return
    print("=" * 60)
    print("ANÁLISIS DE DATOS PARA REPORTE DE TIEMPO")
    print("=" * 60)

    cols = data.get("columns") or {}
    col_keys = list(cols.keys()) if isinstance(cols, dict) else []
    if not col_keys:
        col_keys = ["backlog", "todo", "in_progress", "done", "detenido"]

    # Board.data pone columnas al top level
    all_tasks = []
    for col in col_keys:
        tasks = data.get(col, []) or []
        all_tasks.extend([(t, col) for t in tasks if isinstance(t, dict) and t.get("id")])

    transitions = data.get("transitions", []) or []
    maestro_categoria = data.get("categoria", []) or []

    print(f"\n1. TAREAS TOTALES: {len(all_tasks)}")
    for col in col_keys:
        tasks = data.get(col, []) or []
        count = sum(1 for t in tasks if isinstance(t, dict) and t.get("id"))
        print(f"   - {col}: {count} tareas")

    print(f"\n2. TRANSICIONES: {len(transitions)}")

    print(f"\n3. MAESTRO CATEGORÍA: {len(maestro_categoria)} items")
    for i, item in enumerate(maestro_categoria):
        if isinstance(item, dict):
            print(f"   - {i+1}: {item.get('label', item.get('key', ''))}")

    print(f"\n4. CATEGORÍAS EN TAREAS (campo task.categoria):")
    cats_en_tareas = set()
    for t, col in all_tasks:
        cat = (t.get("categoria") or "").strip()
        cats_en_tareas.add(cat if cat else "(sin categoría)")
    for c in sorted(cats_en_tareas):
        print(f"   - {c!r}")

    print(f"\n5. TIME_PER_TASK (esta semana):")
    from_dt, to_dt = week_range()
    time_per_task = compute_time_per_task_in_period(transitions, from_dt, to_dt)
    print(f"   Tareas con tiempo en periodo: {len(time_per_task)}")
    task_info = {}
    for col in col_keys:
        for t in (data.get(col, []) or []):
            if isinstance(t, dict) and t.get("id"):
                task_info[t["id"]] = {
                    "categoria": (t.get("categoria") or "").strip() or "(sin categoría)",
                    "name": t.get("name", "")[:40],
                }
    for tid, (a, d) in list(time_per_task.items())[:15]:
        info = task_info.get(tid, {})
        cat = info.get("categoria", "?")
        name = info.get("name", "?")
        print(f"   - {tid[:8]}... | {cat!r} | {name}")

    print(f"\n6. CATEGORÍAS QUE APARECERÍAN EN EL REPORTE (semana):")
    detail_cats = set()
    for tid in time_per_task:
        info = task_info.get(tid, {})
        cat = info.get("categoria", "(sin categoría)")
        detail_cats.add(cat)
    for c in sorted(detail_cats):
        print(f"   - {c!r}")
    print(f"   Total: {len(detail_cats)} categorías con tiempo")

    print(f"\n7. CATEGORÍAS DEL MAESTRO SIN TIEMPO (añadidas con 0%):")
    maestro_labels = set()
    for item in maestro_categoria:
        if isinstance(item, dict):
            lbl = (item.get("label") or "").strip()
            if lbl:
                maestro_labels.add(lbl)
    sin_tiempo = maestro_labels - detail_cats
    for c in sorted(sin_tiempo):
        print(f"   - {c!r}")
    print(f"   Total: {len(sin_tiempo)} categorías del maestro con 0%")

    resumen_final = len(detail_cats) + len(sin_tiempo)
    if "(sin categoría)" not in detail_cats and "(sin categoría)" not in maestro_labels:
        resumen_final += 1
    print(f"\n8. RESUMEN ESPERADO EN PIE/TABLA: {resumen_final} categorías")
    print("=" * 60)


if __name__ == "__main__":
    main()
