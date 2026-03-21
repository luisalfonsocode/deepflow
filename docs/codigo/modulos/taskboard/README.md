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
| **Modificación** | ✅ | `update_task_name`, `update_task_ticket`, `update_task_*` en BoardService |
| **Eliminación** | ✅ | `delete_task(task_id)` en BoardService |
| **Consulta** | ✅ | `data`, `get_task`, `get_task_column`, `get_tasks_with_timestamps()`, exportar CSV |
| **Maestros / Kanban** | ✅ | `get_kanban_columns`, `save_kanban_columns`, `col_key_to_display` (ver Maestros) |

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
pytest tests/ -v
```

Ver [Maestros](../masters/README.md) para configuración de columnas Kanban y límites WIP.
