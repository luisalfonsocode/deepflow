# API TaskBoard – Documentación de Métodos

Referencia de todos los métodos públicos del módulo TaskBoard, su comportamiento y cobertura de tests.

**Ejecutar tests**: `pytest tests/test_board_service.py -v`

---

## BoardService

### `create_task(name: str = "") -> dict | None`

**Descripción**: Crea una tarea en Backlog.

**Implementación**:
- Valida que Backlog tenga espacio (límite WIP = 3)
- Genera UUID para la tarea
- Si `name` está vacío o solo espacios → usa `"Nueva tarea"`
- Persiste en el repositorio

**Parámetros**:
| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|--------------|-------------|
| `name` | `str` | `""` | Nombre o actividad de la tarea |

**Retorno**: `dict` con `{"id": str, "name": str}` si OK, `None` si Backlog está lleno.

**Casos**:
- Backlog con < 3 tareas → crea y retorna la tarea
- Backlog con 3 tareas → retorna `None`
- `name="  "` → usa `"Nueva tarea"`

**Tests**: `test_create_task_*`

---

### `create_task_from_clipboard(text: str) -> dict | None`

**Descripción**: Crea tarea desde texto (p. ej. portapapeles). Delegado a `create_task(text)`.

**Retorno**: Igual que `create_task`.

**Tests**: `test_create_task_from_clipboard_*`

---

### `update_task_name(task_id: str, new_name: str) -> bool`

**Descripción**: Modifica el nombre de una tarea existente.

**Implementación**:
- Busca la tarea por `task_id`
- Si no existe → retorna `False`
- Si `new_name` vacío/espacios → mantiene el nombre actual de la tarea
- Persiste

**Retorno**: `True` si se actualizó, `False` si la tarea no existe.

**Tests**: `test_update_task_name_*`

---

### `move_task(task_id: str, target_column: str) -> bool`

**Descripción**: Mueve una tarea a otra columna.

**Implementación**:
- Comprueba si `target_column` admite más tareas (límite WIP)
- Extrae la tarea de la columna actual y la añade a destino
- Si destino es `in_progress` y la tarea no tiene `started_at` → lo establece (primera vez)
- Si destino es `done` → actualiza `finished_at` (última vez que termina)
- Persiste

**Retorno**: `True` si se movió, `False` si tarea no existe o columna destino está llena.

**Tests**: `test_move_task_*`

---

### `delete_task(task_id: str) -> bool`

**Descripción**: Elimina una tarea del tablero.

**Retorno**: `True` si se eliminó, `False` si no existe.

**Tests**: `test_delete_task_*`

---

### `get_task(task_id: str) -> dict | None`

**Descripción**: Obtiene una tarea por id (solo lectura).

**Retorno**: `dict` con `{"id", "name", "started_at"?, "finished_at"?}` si existe, `None` si no.

**Tests**: `test_get_task_*`

---

### `get_tasks_with_timestamps() -> list[dict]`

**Descripción**: Devuelve todas las tareas con `started_at` y `finished_at` para exportación.

**Retorno**: Lista con `task_id`, `task_name`, `started_at`, `finished_at` (ISO 8601 UTC; vacío si nunca llegó).

**Tests**: `test_get_tasks_with_timestamps_*`

---

### `can_add_to(column_key: str) -> bool`

**Descripción**: Indica si la columna admite más tareas (WIP).

**Retorno**: `True` si hay espacio, `False` si ya hay 3 tareas.

**Tests**: `test_can_add_to_*`

---

### `count(column_key: str) -> int`

**Descripción**: Cuenta tareas en una columna.

**Tests**: `test_count_*`

---

### `is_overcapacity(column_key: str) -> bool`

**Descripción**: Indica si la columna supera el límite WIP.

**Retorno**: `True` si hay más de 3 tareas.

**Tests**: `test_is_overcapacity_*`

---

### `load() -> None` / `persist() -> bool`

**Descripción**: Recarga desde el repositorio / persiste el estado.

**Tests**: `test_load_*`, `test_persist_*`

---

### Propiedad `data`

**Tipo**: `dict` con `columns` y `transitions`

Estado completo del tablero.

---

## BoardRepository (Protocol)

| Método | Descripción |
|--------|-------------|
| `get_board_data()` | Retorna el estado completo |
| `save_board_data(data)` | Persiste el estado |

---

## Constantes

| Nombre | Valor |
|--------|-------|
| `COLUMNS` | `("backlog", "todo", "in_progress", "done", "detenido")` |
| `WIP_LIMIT_PER_COLUMN` | `3` |

---

## Utilidades

### `col_key_to_display(key: str) -> str`

Mapea claves internas a texto visible (backlog → "Backlog", etc.).
