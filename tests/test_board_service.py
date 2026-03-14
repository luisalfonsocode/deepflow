"""
Tests de BoardService.
Ejecutar: pytest tests/test_board_service.py -v
"""

import pytest

from domain.taskboard.constants import COLUMNS, WIP_LIMIT_PER_COLUMN
from application.taskboard import BoardService

from tests.conftest import InMemoryBoardRepository


# --- create_task ---


def test_create_task_agrega_en_backlog(board_service):
    """create_task añade la tarea en Backlog y retorna el dict."""
    task = board_service.create_task("Mi tarea")
    assert task is not None
    assert task["name"] == "Mi tarea"
    assert "id" in task and len(task["id"]) > 0
    assert len(board_service.data["backlog"]) == 1


def test_create_task_nombre_vacio_usar_default(board_service):
    """Si name está vacío, usa 'Nueva tarea'."""
    task = board_service.create_task("")
    assert task["name"] == "Nueva tarea"


def test_create_task_nombre_solo_espacios_usar_default(board_service):
    """Si name son solo espacios, usa 'Nueva tarea'."""
    task = board_service.create_task("   ")
    assert task["name"] == "Nueva tarea"


def test_create_task_backlog_lleno_retorna_none(board_service):
    """Si Backlog tiene 3 tareas, create_task retorna None."""
    for _ in range(WIP_LIMIT_PER_COLUMN):
        board_service.create_task("x")
    task = board_service.create_task("otra")
    assert task is None
    assert len(board_service.data["backlog"]) == 3


def test_create_task_no_registra_started_finished(board_service):
    """create_task no pone started_at ni finished_at (solo en Backlog)."""
    task = board_service.create_task("test")
    assert "started_at" not in task or task.get("started_at") is None
    assert "finished_at" not in task or task.get("finished_at") is None


# --- create_task_from_clipboard ---


def test_create_task_from_clipboard_delega_a_create_task(board_service):
    """create_task_from_clipboard usa el texto como nombre."""
    task = board_service.create_task_from_clipboard("texto del portapapeles")
    assert task is not None
    assert task["name"] == "texto del portapapeles"


def test_create_task_in_crea_directamente_en_columna(board_service):
    """create_task_in crea la tarea directamente en la columna indicada."""
    task = board_service.create_task_in("Tarea directa", "in_progress")
    assert task is not None
    assert task["name"] == "Tarea directa"
    assert len(board_service.data["in_progress"]) == 1
    assert "started_at" in task


# --- update_task_name ---


def test_update_task_name_modifica_existente(board_service):
    """update_task_name cambia el nombre de una tarea existente."""
    t = board_service.create_task("Original")
    ok = board_service.update_task_name(t["id"], "Nuevo nombre")
    assert ok is True
    assert board_service.get_task(t["id"])["name"] == "Nuevo nombre"


def test_update_task_name_task_inexistente_retorna_false(board_service):
    """update_task_name retorna False si la tarea no existe."""
    ok = board_service.update_task_name("uuid-inexistente", "X")
    assert ok is False


def test_update_task_name_vacio_mantiene_nombre_actual(board_service):
    """Si new_name está vacío, mantiene el nombre actual de la tarea."""
    t = board_service.create_task("Algo")
    board_service.update_task_name(t["id"], "")
    assert board_service.get_task(t["id"])["name"] == "Algo"


# --- move_task ---


def test_move_task_mueve_entre_columnas(board_service):
    """move_task mueve la tarea correctamente."""
    t = board_service.create_task("Moverme")
    ok = board_service.move_task(t["id"], "todo")
    assert ok is True
    assert len(board_service.data["backlog"]) == 0
    assert len(board_service.data["todo"]) == 1


def test_move_task_a_in_progress_establece_started_at(board_service):
    """move_task a in_progress establece started_at (primera vez)."""
    t = board_service.create_task("X")
    board_service.move_task(t["id"], "todo")
    board_service.move_task(t["id"], "in_progress")
    task = board_service.get_task(t["id"])
    assert "started_at" in task
    assert task["started_at"]  # no vacío


def test_move_task_a_done_establece_finished_at(board_service):
    """move_task a done establece finished_at (última vez)."""
    t = board_service.create_task("X")
    board_service.move_task(t["id"], "in_progress")
    board_service.move_task(t["id"], "done")
    task = board_service.get_task(t["id"])
    assert "finished_at" in task
    assert task["finished_at"]


def test_started_at_solo_primera_vez(board_service):
    """started_at se establece solo la primera vez que llega a in_progress."""
    t = board_service.create_task("X")
    board_service.move_task(t["id"], "in_progress")
    first_started = board_service.get_task(t["id"])["started_at"]
    board_service.move_task(t["id"], "todo")
    board_service.move_task(t["id"], "in_progress")
    second_started = board_service.get_task(t["id"])["started_at"]
    assert first_started == second_started  # no se sobrescribe


def test_move_task_destino_lleno_retorna_false(empty_repo):
    """move_task retorna False si la columna destino está llena."""
    data = {
        "backlog": [{"id": "a", "name": "A"}],
        "todo": [{"id": "b", "name": "B"}, {"id": "c", "name": "C"}, {"id": "d", "name": "D"}],
        "in_progress": [], "done": [], "detenido": [],
    }
    repo = InMemoryBoardRepository(data)
    svc = BoardService(repo)
    ok = svc.move_task("a", "todo")
    assert ok is False
    assert "a" in [t["id"] for t in svc.data["backlog"]]


def test_move_task_task_inexistente_retorna_false(board_service):
    """move_task retorna False si la tarea no existe."""
    ok = board_service.move_task("uuid-fake", "todo")
    assert ok is False


# --- delete_task ---


def test_delete_task_elimina_existente(board_service):
    """delete_task elimina la tarea del tablero."""
    t = board_service.create_task("Eliminar")
    ok = board_service.delete_task(t["id"])
    assert ok is True
    assert board_service.get_task(t["id"]) is None


def test_delete_task_inexistente_retorna_false(board_service):
    """delete_task retorna False si la tarea no existe."""
    ok = board_service.delete_task("uuid-fake")
    assert ok is False


# --- get_task ---


def test_get_task_retorna_existente(board_service):
    """get_task retorna la tarea si existe."""
    t = board_service.create_task("Buscar")
    found = board_service.get_task(t["id"])
    assert found is not None
    assert found["id"] == t["id"]


def test_get_task_inexistente_retorna_none(board_service):
    """get_task retorna None si no existe."""
    assert board_service.get_task("uuid-fake") is None


def test_get_task_column_retorna_columna_correcta(board_service):
    """get_task_column retorna la columna donde está la tarea."""
    t = board_service.create_task("X")
    assert board_service.get_task_column(t["id"]) == "backlog"
    board_service.move_task(t["id"], "in_progress")
    assert board_service.get_task_column(t["id"]) == "in_progress"


def test_get_task_column_inexistente_retorna_none(board_service):
    """get_task_column retorna None si la tarea no existe."""
    assert board_service.get_task_column("uuid-fake") is None


# --- get_tasks_with_timestamps ---


def test_get_tasks_with_timestamps_retorna_tareas(board_service):
    """get_tasks_with_timestamps retorna tareas con started_at y finished_at."""
    assert board_service.get_tasks_with_timestamps() == []
    t = board_service.create_task("X")
    board_service.move_task(t["id"], "in_progress")
    tasks = board_service.get_tasks_with_timestamps()
    assert len(tasks) == 1
    assert tasks[0]["task_id"] == t["id"]
    assert tasks[0]["started_at"]
    assert tasks[0]["finished_at"] == ""


# --- can_add_to ---


def test_can_add_to_true_cuando_hay_espacio(board_service):
    """can_add_to True cuando la columna tiene menos de 3."""
    assert board_service.can_add_to("backlog") is True


def test_can_add_to_false_cuando_lleno(board_service):
    """can_add_to False cuando la columna tiene 3 tareas."""
    for _ in range(3):
        board_service.create_task("x")
    assert board_service.can_add_to("backlog") is False


# --- count ---


def test_count_retorna_cantidad_correcta(board_service):
    """count retorna el número de tareas en la columna."""
    assert board_service.count("backlog") == 0
    board_service.create_task("A")
    assert board_service.count("backlog") == 1


# --- is_overcapacity ---


def test_is_overcapacity_false_cuando_ok(board_service):
    """is_overcapacity False cuando count <= 3."""
    assert board_service.is_overcapacity("backlog") is False


def test_is_overcapacity_true_cuando_excede(empty_repo):
    """is_overcapacity True cuando count > 3 (datos legacy)."""
    data = {
        "backlog": [{"id": f"x{i}", "name": f"X{i}"} for i in range(4)],
        "todo": [], "in_progress": [], "done": [], "detenido": [],
    }
    repo = InMemoryBoardRepository(data)
    svc = BoardService(repo)
    assert svc.is_overcapacity("backlog") is True


# --- load / persist ---


def test_load_recarga_datos(empty_repo):
    """load recarga los datos del repositorio."""
    svc = BoardService(empty_repo)
    svc.create_task("A")
    empty_repo._data["columns"]["backlog"] = []
    svc.load()
    assert len(svc.data["backlog"]) == 0


def test_persist_retorna_true(board_service):
    """persist retorna True cuando guarda correctamente."""
    board_service.create_task("X")
    assert board_service.persist() is True


# --- data ---


def test_data_tiene_todas_las_columnas(board_service):
    """data incluye todas las columnas definidas."""
    d = board_service.data
    for col in COLUMNS:
        assert col in d
        assert isinstance(d[col], list)
