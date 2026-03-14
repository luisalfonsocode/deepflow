# DeepFlow – Arquitectura Técnica

## Principios aplicados

- **Separación diseño/lógica**: `presentation/theme/` para constantes visuales, `styles.qss` para estilos
- **SOLID**: DIP (inyección de repositorios, ClipboardProvider), SRP (presenters, servicios)
- **Clean Architecture**: domain, application, infrastructure, presentation
- **Composición root**: `presentation/composition.py` como punto único de construcción de dependencias

## Flujo de datos (Hexagonal / Puertos y Adaptadores)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   main.py   │────▶│  MainShell   │────▶│  BoardService   │
│ (entry)     │     │ (widget)     │     │ (taskboard)     │
└─────────────┘     └───────┬───────┘     └────────┬────────┘
                           │                       │
                           │  composition.py       │ BoardRepository (puerto)
                           ▼                       ▼
                   ┌──────────────┐     ┌────────────────────────────┐
                   │  Presenters  │     │ ZODBBoardRepository        │
                   │  ReportsView │     │ (infrastructure/persistence)│
                   │  + Excel     │     │   └─ data/db/deepflow_db.fs │
                   └──────────────┘     └────────────────────────────┘
```

---

## Módulos por capa

### domain/taskboard/

| Componente | Descripción |
|------------|-------------|
| **constants.py** | COLUMNS, WIP_LIMIT_PER_COLUMN |
| **masters.py** | Maestros (origen, tribu, kanban) |
| **utils.py** | col_key_to_display, format_* |

### application/

| Componente | Descripción |
|------------|-------------|
| **ports/board_repository.py** | Puerto de persistencia (Protocol) |
| **taskboard/board_service.py** | CRUD del tablero (caso de uso) |
| **reports/export_service.py** | Datos para reportes (tareas, subtareas, transiciones) |

### infrastructure/

| Componente | Descripción |
|------------|-------------|
| **persistence/** | ZODBBoardRepository, schema_versions, migraciones |
| **export/** | ExcelActivityExporter |
| **ui/** | QtClipboardProvider |

### Base de datos ZODB y versionado

- **ZODB** (`data/db/deepflow_db.fs`): base de datos embebida orientada a objetos
- **schema_version**: en root de ZODB; `schema_versions.py` define migraciones
- **Evolución**: incrementar `CURRENT_SCHEMA_VERSION` y añadir lógica en `migrate_to_latest()`
- **Migración desde JSON**: si existe `deepflow_db.json` (en data/ o raíz) y no existe `data/db/deepflow_db.fs`, se migra automáticamente

### presentation/

| Componente | Descripción |
|------------|-------------|
| **composition.py** | Composition root: create_board_service() |
| **presenters/** | ReportsPresenter |
| **theme/constants.py** | ObjectNames, Layout |
| **ports/clipboard_provider.py** | Protocol para portapapeles |
| **style_loader.py** | Carga de styles.qss |

---

## Validaciones WIP

- Cada columna tiene límite `WIP_LIMIT_PER_COLUMN = 3`
- `can_add_to()` comprueba `len(column) < 3`
- Los botones ◀ ▶ se deshabilitan si la columna destino está llena
- El botón + se deshabilita cuando Backlog está lleno

---

## Transiciones

Cada transición se registra con:

```python
{
    "task_id": str,
    "task_name": str,
    "from_column": str | None,  # None = creación
    "to_column": str,
    "timestamp": str  # ISO 8601 UTC
}
```

Se registran en `create_task()` y `move_task()`.
