# Módulo Maestros

Gestión de catálogos y configuración del tablero. Maestros editables y columnas Kanban con límites WIP configurables.

---

## Responsabilidad

- Editar maestros: Tribu y Squad, Solicitante, Canal de reporte, Categoría
- Configurar **Columnas Kanban**: label, orden, límite WIP (vacío = sin límite)

---

## Funcionalidades

| Funcionalidad | Estado | Descripción |
|---------------|--------|-------------|
| **Tribu y Squad** | ✅ | Lista editable (key, label) |
| **Solicitante** | ✅ | Lista editable |
| **Canal de reporte** | ✅ | Lista editable (origen) |
| **Categoría** | ✅ | Lista editable |
| **Columnas Kanban** | ✅ | Tabla: Label, Orden, Límite WIP. Vacío = sin límite |

---

## Ubicación en el código

```
domain/taskboard/masters.py     # KANBAN_COLUMNS, get_column_keys, get_wip_limit
application/taskboard/board_service.py  # get_master_list, save_master_list, get/save_kanban_columns
presentation/
├── presenters/masters_presenter.py
└── modules/masters/
    ├── __init__.py
    └── view.py                 # MastersView (tabs + tabla Kanban)
```

---

## API (BoardService)

| Método | Descripción |
|--------|-------------|
| `get_master_list(master_key)` | Lista de un maestro |
| `save_master_list(master_key, items)` | Persiste maestro |
| `get_kanban_columns()` | Columnas Kanban actuales |
| `save_kanban_columns(columns)` | Persiste columnas Kanban |
| `get_column_keys()` | Claves de columnas ordenadas |
| `col_key_to_display(key)` | Label visible |
| `display_to_column_key(display)` | Label → clave |

Ver **[API TaskBoard](../taskboard/API.md)** para detalle completo.

---

## Maestros disponibles

| `master_key` | Título en UI |
|--------------|--------------|
| `tribu_squad` | Tribu y Squad |
| `solicitante` | Solicitante |
| `canal_reporte` | Canal de reporte |
| `categoria` | Categoría |

`kanban_columns` se gestiona con `get_kanban_columns` / `save_kanban_columns` (no es un maestro genérico).
