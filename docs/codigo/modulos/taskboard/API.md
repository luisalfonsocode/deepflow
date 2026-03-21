# API TaskBoard – Documentación de Métodos

Referencia de todos los métodos públicos del módulo TaskBoard, su comportamiento y cobertura de tests.

**Ejecutar tests**: `pytest tests/ -v`

---

## BoardService

Servicio principal: orquesta dominio e infraestructura (repositorio) para CRUD del tablero Kanban.

---

### Persistencia y ciclo de vida

#### `load() -> None`

Recarga el estado desde el repositorio. Invalida la caché de mapeo key↔label.

#### `persist() -> bool`

Persiste el estado mediante el repositorio. Retorna `True` si se guardó correctamente.

#### `shutdown() -> None`

Cierra recursos del repositorio (ej. conexión ZODB). Llamar al salir de la aplicación.

#### Propiedad `data`

**Tipo**: `dict` con `columns`, `transitions`, maestros.

Estado completo del tablero. Las columnas también están en top level (`data['backlog']`, etc.) por compatibilidad.

---

### Maestros (kanban_columns, tribu_squad, solicitante, canal_reporte, categoría)

#### `get_master_list(master_key: str) -> list[dict[str, str]]`

Obtiene la lista de un maestro: `tribu_squad`, `solicitante`, `canal_reporte`, `categoria`, etc.

**Retorno**: Lista de `{key, label}`. Lista vacía si no existe o no es lista válida.

#### `save_master_list(master_key: str, items: list[dict[str, str]]) -> bool`

Persiste la lista de un maestro. Normaliza keys con `normalize_key_from_label` si no existe. Retorna `True` si se guardó.

#### `get_column_keys() -> tuple[str, ...]`

Claves de columnas del maestro `kanban_columns` (ordenadas por `order`).

#### `col_key_to_display(column_key: str) -> str`

Label visible de columna según maestro. Fallback a dominio (`domain.taskboard.utils.col_key_to_display`).

#### `display_to_column_key(display: str) -> str | None`

Convierte label visible a `column_key` según maestro. Retorna `None` si no existe.

#### `get_kanban_columns() -> list[dict[str, Any]]`

Obtiene el maestro `kanban_columns`: `key`, `label`, `order`, `wip_limit` (None = sin límite).

#### `save_kanban_columns(columns: list[dict[str, Any]]) -> bool`

Persiste el maestro `kanban_columns`. Invalida la caché key↔label. Retorna `False` si no hay columnas válidas. Cada ítem debe tener `key`; `wip_limit` vacío o `None` = sin límite.

---

### Creación de tareas

#### `create_task(name: str = "") -> dict | None`

Crea una tarea en Backlog.

**Implementación**:
- Valida que Backlog tenga espacio (límite WIP; sin límite por defecto)
- Genera UUID para la tarea
- Si `name` vacío o solo espacios → usa `"Nueva tarea"`
- Persiste

**Retorno**: `dict` con `{"id", "name", ...}` si OK, `None` si Backlog está lleno.

**Tests**: `test_create_task_*`

#### `create_task_from_clipboard(text: str) -> dict | None`

Crea tarea desde texto (ej. portapapeles). Delega a `create_task(text)`.

#### `create_task_in(name: str, column_key: str) -> dict | None`

Crea tarea directamente en la columna indicada. Retorna `None` si la columna está llena.

---

### Modificación de tareas

#### `update_task_name(task_id: str, new_name: str) -> bool`

Actualiza el nombre. Retorna `False` si la tarea no existe. Si `new_name` vacío, mantiene el actual.

#### `update_task_ticket(task_id: str, ticket: str) -> bool`

Actualiza el ticket (código externo, ej. Jira).

#### `update_task_tribe_and_squad(task_id: str, value: str) -> bool`

Actualiza tribu/squad.

#### `update_task_requester(task_id: str, value: str)` / `update_task_solicitante(task_id: str, value: str) -> bool`

Actualiza solicitante/requester. Ambos campos se mantienen sincronizados.

#### `update_task_reporting_channel(task_id: str, value: str) -> bool`

Actualiza canal de reporte/origen. Sincroniza `origen` y `reporting_channel`.

#### `update_task_prioridad(task_id: str, value: bool) -> bool`

Actualiza flag de prioridad alta.

#### `update_task_categoria(task_id: str, value: str) -> bool`

Actualiza categoría.

#### `update_task_detalle(task_id: str, value: str) -> bool`

Actualiza detalle/descripción.

#### `update_task_due_date(task_id: str, value: str) -> bool`

Actualiza fecha compromiso (ISO).

#### `update_task_created_at(task_id: str, iso_value: str) -> bool`

Actualiza fecha de creación (ISO).

#### `update_task_entered_at(task_id: str, iso_value: str) -> bool`

Actualiza fecha de entrada en columna actual (ISO).

#### `update_task_started_at(task_id: str, iso_value: str) -> bool`

Actualiza fecha de inicio en In Progress (ISO).

#### `update_task_finished_at(task_id: str, iso_value: str) -> bool`

Actualiza fecha de finalización (ISO).

#### `update_task_subtasks(task_id: str, subtasks: list[dict]) -> bool`

Actualiza lista de subtareas. Normaliza `name`, `estado`, `order`.

---

### Movimiento y eliminación

#### `move_task(task_id: str, target_column: str) -> bool`

Mueve una tarea a otra columna.

**Implementación**:
- Comprueba si `target_column` admite más tareas (límite WIP)
- Extrae la tarea y la añade a destino
- Si destino es `in_progress` y no tiene `started_at` → lo establece
- Si destino es `done` → actualiza `finished_at`
- Registra transición y persiste

**Retorno**: `True` si se movió, `False` si tarea no existe o columna destino llena.

#### `delete_task(task_id: str) -> bool`

Elimina una tarea del tablero. Borrado físico; las transiciones quedan huérfanas (historial).

---

### Consultas

#### `get_task(task_id: str) -> dict | None`

Obtiene una tarea por id (solo lectura). Retorna `None` si no existe.

#### `get_task_column(task_id: str) -> str | None`

Retorna la columna donde está la tarea. `None` si no existe.

#### `get_tasks_with_timestamps() -> list[dict]`

Devuelve todas las tareas con `task_id`, `ticket`, `task_name`, `tribe_and_squad`, `requester`, `reporting_channel`, `started_at`, `finished_at` para exportación.

---

### Límites WIP

#### `can_add_to(column_key: str) -> bool`

Indica si la columna admite más tareas. `True` si hay espacio o no tiene límite (`wip_limit` None).

#### `count(column_key: str) -> int`

Cuenta tareas en una columna.

#### `is_overcapacity(column_key: str) -> bool`

Indica si la columna supera su límite WIP. `True` si hay más tareas que el límite configurado.

---

## BoardRepository (Protocol)

| Método | Descripción |
|--------|-------------|
| `get_board_data()` | Retorna el estado completo del tablero |
| `save_board_data(data)` | Persiste el estado |
| `close()` | Cierra recursos (opcional) |

---

## Constantes y maestros

| Nombre | Ubicación | Descripción |
|--------|-----------|-------------|
| `COLUMNS` | `domain.taskboard.constants` | Legacy: `("backlog", "todo", "in_progress", "done", "detenido")` |
| `WIP_LIMIT_PER_COLUMN` | `domain.taskboard.constants` | Legacy: `3` |
| `KANBAN_COLUMNS` | `domain.taskboard.masters` | Fuente de verdad: `key`, `label`, `order`, `wip_limit` |
| `KANBAN_COLUMNS_KEY` | `domain.taskboard.masters` | `"kanban_columns"` en BD |

**Límites por defecto** (maestro `kanban_columns`):
- Backlog, Done: sin límite (`wip_limit`: None)
- To Do, In Progress: 3
- Detenido: 5

---

## Utilidades de dominio (`domain.taskboard.utils`)

| Función | Descripción |
|---------|-------------|
| `col_key_to_display(key)` / `column_key_to_display(key)` | Clave → label visible (fallback estático) |
| `display_to_column_key(display)` | Label → clave. `None` si no existe |
| `normalize_key_from_label(label)` | Deriva key: minúsculas, espacios→_, ñ→n |
| `format_task_duration(started_at, finished_at, column_key)` | Duración: "5d" o "5h" |
| `compute_time_in_columns(task_id, transitions, current_column)` | Segundos en In Progress y Detenido |
| `format_date_display(iso_string)` | "13 Mar 2026" |
| `parse_date_to_iso(text)` | Parsea dd/mm/yyyy, ISO, etc. a ISO 8601 |
| `iso_to_dd_mm_yyyy(iso_string)` | ISO → dd/mm/yyyy |
| `iso_to_dd_mm_yyyy_hh_mm(iso_string)` | ISO → dd/mm/yyyy HH:mm |

---

## Maestros (`domain.taskboard.masters`)

| Función | Descripción |
|---------|-------------|
| `get_column_keys(kanban_columns)` | Claves ordenadas por `order` |
| `get_wip_limit(kanban_columns, column_key)` | Límite WIP. `None` = sin límite |
| `default_kanban_columns_dicts()` | Copia de `KANBAN_COLUMNS` para migración |
