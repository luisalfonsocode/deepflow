"""
Caso de uso: exportación de actividades.
Obtiene datos del tablero y los transforma para Excel, CSV, etc.
"""

from datetime import datetime
from typing import Any

from domain.taskboard.utils import (
    compute_time_per_task_from_task_dates,
    compute_time_per_task_in_period,
    format_seconds_duration,
    get_stints_per_task_in_period,
    get_task_bars_for_timeline,
)


class ExportService:
    """Obtiene actividades del tablero y las exporta (Excel, etc.)."""

    def __init__(self, board_data: dict[str, Any], columns: list[str], col_key_to_display):
        self._board_data = board_data
        self._columns = columns
        self._col_key_to_display = col_key_to_display

    def get_all_activities(self) -> list[dict[str, Any]]:
        """Todas las actividades (tareas) con columna actual y subtareas."""
        result = []
        for col in self._columns:
            for t in self._board_data.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    result.append({
                        "id": t.get("id", ""),
                        "ticket": t.get("ticket", ""),
                        "name": t.get("name", ""),
                        "tribe_and_squad": t.get("tribe_and_squad", ""),
                        "requester": t.get("requester", ""),
                        "reporting_channel": t.get("reporting_channel", ""),
                        "column": col,
                        "estado": self._col_key_to_display(col),
                        "column_display": self._col_key_to_display(col),
                        "subtasks": [
                            {
                                "text": s.get("text", s.get("name", "")),
                                "done": bool(s.get("done", s.get("estado") == "done")),
                            }
                            for s in t.get("subtasks", [])
                        ],
                        "created_at": t.get("created_at") or t.get("entered_at") or "",
                        "started_at": t.get("started_at") or "",
                        "finished_at": t.get("finished_at") or "",
                        "due_date": t.get("due_date") or "",
                    })
        return result

    def get_all_transitions(self) -> list[dict[str, Any]]:
        """Todas las transiciones de tareas entre columnas."""
        result = []
        for t in self._board_data.get("transitions", []):
            if isinstance(t, dict) and t.get("task_id"):
                from_col = t.get("from_column")
                to_col = t.get("to_column")
                result.append({
                    "task_id": t.get("task_id", ""),
                    "task_name": t.get("task_name", ""),
                    "from_column": from_col or "",
                    "from_display": self._col_key_to_display(from_col) if from_col else "-",
                    "to_column": to_col or "",
                    "to_display": self._col_key_to_display(to_col) if to_col else "-",
                    "timestamp": t.get("timestamp", ""),
                })
        return result

    def get_all_subtasks(self) -> list[dict[str, Any]]:
        """Todas las subtareas aplanadas con info de la tarea padre."""
        result = []
        for col in self._columns:
            for t in self._board_data.get(col, []):
                if isinstance(t, dict) and t.get("id"):
                    task_id = t.get("id", "")
                    task_name = t.get("name", "")
                    task_ticket = t.get("ticket", "")
                    for idx, s in enumerate(t.get("subtasks", [])):
                        result.append({
                            "task_id": task_id,
                            "subtask_index": idx,
                            "task_ticket": task_ticket,
                            "task_name": task_name,
                            "subtask_text": s.get("text", s.get("name", "")),
                            "done": bool(s.get("done", s.get("estado") == "done")),
                            "column_display": self._col_key_to_display(col),
                        })
        return result

    def get_time_report(
        self,
        from_date: datetime,
        to_date: datetime,
    ) -> dict[str, Any]:
        """
        Reporte de tiempo por categoría en el periodo.
        Retorna:
          - summary_by_categoria: [{categoria, active_secs, detenido_secs, pct_total, task_count}, ...]
          - detail_by_task: [{task_id, name, ticket, categoria, active_secs, detenido_secs, active_fmt, detenido_fmt}, ...] ordenado por categoria
          - total_active_secs, total_detenido_secs
        """
        cols = self._columns
        transitions = self._board_data.get("transitions", [])

        # Construir task_id -> {name, ticket, categoria}
        task_info: dict[str, dict[str, Any]] = {}
        for col in cols:
            for t in (self._board_data.get(col, []) or []):
                if isinstance(t, dict) and t.get("id"):
                    task_info[t["id"]] = {
                        "name": t.get("name", ""),
                        "ticket": t.get("ticket", ""),
                        "categoria": (t.get("categoria") or "").strip() or "(sin categoría)",
                    }

        # Prioridad: started_at/finished_at (fechas editadas) sobre transiciones
        time_from_dates = compute_time_per_task_from_task_dates(
            self._board_data, cols, from_date, to_date
        )
        time_from_transitions = compute_time_per_task_in_period(
            transitions, from_date, to_date
        )
        time_per_task = dict(time_from_dates)
        for tid, (a, d) in time_from_transitions.items():
            if tid not in time_per_task:
                time_per_task[tid] = (a, d)

        # Detalle por tarea, ordenado por categoría
        detail: list[dict[str, Any]] = []
        for task_id, (active_secs, detenido_secs) in time_per_task.items():
            info = task_info.get(task_id, {})
            cat = info.get("categoria", "(sin categoría)")
            detail.append({
                "task_id": task_id,
                "name": info.get("name", ""),
                "ticket": info.get("ticket", ""),
                "categoria": cat,
                "active_secs": active_secs,
                "detenido_secs": detenido_secs,
                "active_fmt": format_seconds_duration(active_secs),
                "detenido_fmt": format_seconds_duration(detenido_secs),
            })
        detail.sort(key=lambda x: (x["categoria"], -x["active_secs"] - x["detenido_secs"]))

        # Agregar por categoría (tiempo en el periodo; task_count = tareas con tiempo)
        cat_totals: dict[str, dict[str, Any]] = {}
        for d in detail:
            cat = d["categoria"]
            if cat not in cat_totals:
                cat_totals[cat] = {"categoria": cat, "active_secs": 0, "detenido_secs": 0, "task_count": 0}
            cat_totals[cat]["active_secs"] += d["active_secs"]
            cat_totals[cat]["detenido_secs"] += d["detenido_secs"]
            cat_totals[cat]["task_count"] += 1

        # Incluir categorías de TODAS las tareas del tablero (aunque tengan 0 tiempo en el periodo)
        for info in task_info.values():
            cat = info.get("categoria", "(sin categoría)")
            if cat not in cat_totals:
                cat_totals[cat] = {
                    "categoria": cat,
                    "active_secs": 0,
                    "detenido_secs": 0,
                    "task_count": 0,
                }

        # Incluir categorías del maestro
        for item in self._board_data.get("categoria", []) or []:
            if isinstance(item, dict):
                lbl = (item.get("label") or "").strip()
                if lbl and lbl not in cat_totals:
                    cat_totals[lbl] = {
                        "categoria": lbl,
                        "active_secs": 0,
                        "detenido_secs": 0,
                        "task_count": 0,
                    }
        if "(sin categoría)" not in cat_totals:
            cat_totals["(sin categoría)"] = {
                "categoria": "(sin categoría)",
                "active_secs": 0,
                "detenido_secs": 0,
                "task_count": 0,
            }

        total_active = sum(t["active_secs"] for t in cat_totals.values())
        total_detenido = sum(t["detenido_secs"] for t in cat_totals.values())
        total_secs = total_active + total_detenido

        summary = []
        for cat, t in sorted(cat_totals.items(), key=lambda x: (-x[1]["active_secs"] - x[1]["detenido_secs"], x[1]["categoria"])):
            total_cat_secs = t["active_secs"] + t["detenido_secs"]
            pct = round(100 * total_cat_secs / total_secs, 1) if total_secs > 0 else 0
            tiempo_dias = round(total_cat_secs / 86400, 1)
            summary.append({
                **t,
                "active_fmt": format_seconds_duration(t["active_secs"]),
                "detenido_fmt": format_seconds_duration(t["detenido_secs"]),
                "pct_total": pct,
                "tiempo_dias": tiempo_dias,
            })

        timeline_bars = get_task_bars_for_timeline(self._board_data, cols, from_date, to_date)
        stints = get_stints_per_task_in_period(transitions, from_date, to_date)
        stints_by_task: dict[str, list[dict]] = {}
        for s in stints:
            tid = s.get("task_id", "")
            if tid:
                stints_by_task.setdefault(tid, []).append(s)

        for bar in timeline_bars:
            tid = bar.get("task_id", "")
            if tid and tid in task_info:
                bar["categoria"] = task_info[tid].get("categoria", "(sin categoría)")
            bar_start = bar.get("bar_start")
            bar_end = bar.get("bar_end")
            segments = []
            task_stints = stints_by_task.get(tid, [])
            task_stints.sort(key=lambda x: x.get("start"))
            if task_stints:
                for s in task_stints:
                    seg_start = s.get("start")
                    seg_end = s.get("end")
                    col_key = s.get("column_key", "in_progress")
                    if not seg_start or not seg_end:
                        continue
                    s_ = max(seg_start, bar_start) if bar_start else seg_start
                    e_ = min(seg_end, bar_end) if bar_end else seg_end
                    if s_ < e_:
                        segments.append({"start": s_, "end": e_, "column_key": col_key})
            if not segments and bar_start and bar_end:
                segments.append({"start": bar_start, "end": bar_end, "column_key": "in_progress"})
            bar["segments"] = segments

        return {
            "from_date": from_date,
            "to_date": to_date,
            "summary_by_categoria": summary,
            "detail_by_task": detail,
            "timeline_bars": timeline_bars,
            "total_active_secs": total_active,
            "total_detenido_secs": total_detenido,
            "total_secs": total_secs,
        }
