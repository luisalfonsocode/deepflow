# Módulo TaskBoard

Gestión del tablero Kanban, tareas y flujo WIP. Módulo principal de DeepFlow.

---

## Responsabilidad

- Creación, modificación, eliminación y consulta de tareas
- Control de límites WIP por columna
- Registro de transiciones para análisis

---

## Funcionalidades

| Funcionalidad | Estado | Descripción |
|---------------|--------|-------------|
| **Creación** | ✅ | Crear tarea en Backlog (modal, Ctrl+V, botón +) |
| **Modificación de nombre** | ✅ | `update_task_name(task_id, new_name)` en BoardService |
| **Eliminación** | ✅ | `delete_task(task_id)` en BoardService |
| **Consulta** | ✅ | `data`, `get_task(task_id)`, `get_tasks_with_timestamps()`, exportar CSV |

---

## Ubicación en el código

```
domain/taskboard/
├── constants.py       # COLUMNS, WIP_LIMIT_PER_COLUMN
├── masters.py         # Maestros, get_column_keys, get_wip_limit
└── utils.py           # col_key_to_display, format_*, compute_time_*

application/
├── ports/board_repository.py
└── taskboard/board_service.py

infrastructure/persistence/   # ZODBBoardRepository
presentation/modules/taskboard/   # TaskBoardView, TaskCard, ColumnWidget, dialogs
```

---

## API y tests

Ver **[API TaskBoard](API.md)** para documentación de métodos y cobertura de tests.

```bash
pytest tests/test_board_service.py -v
```
