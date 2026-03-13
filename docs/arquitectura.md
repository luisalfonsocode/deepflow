# DeepFlow – Arquitectura Técnica

## Principios aplicados

- **Separación diseño/lógica**: `ui/theme/` para constantes visuales, `styles.qss` para estilos
- **SOLID**: DIP (inyección de repositorios, ClipboardProvider), SRP (presenters, servicios)
- **Arquitectura hexagonal**: Puertos (Protocols) en core, adaptadores en adapters/
- **Composición root**: `ui/composition.py` como punto único de construcción de dependencias

## Flujo de datos (Hexagonal / Puertos y Adaptadores)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   main.py   │────▶│ MainShell /   │────▶│  BoardService   │
│ (entry)     │     │ MonoFlowWindow│     │ (taskboard)     │
└─────────────┘     └───────┬───────┘     └────────┬────────┘
                           │                       │
                           │  composition.py       │ BoardRepository (puerto)
                           ▼                       ▼
                   ┌──────────────┐     ┌────────────────────────────┐
                   │  Presenters  │     │ JsonFileBoardRepository    │
                   │  ReportsView │     │ (adapters/persistence)     │
                   │  + Excel     │     │   └─ json_file.py → .json   │
                   └──────────────┘     └────────────────────────────┘
```

---

## Módulos por capa

### core/modules/taskboard/

| Componente | Descripción |
|------------|-------------|
| **ports/board_repository.py** | Contrato de persistencia (Protocol) |
| **services/board_service.py** | CRUD del tablero (repository inyectado) |
| **constants.py** | COLUMNS, WIP_LIMIT_PER_COLUMN |
| **utils.py** | col_key_to_display, format_* |

### core/modules/reports/

| Componente | Descripción |
|------------|-------------|
| **ports/activity_exporter.py** | Contrato de exportación (Protocol) |
| **services/export_service.py** | Obtiene actividades del tablero para tabla/exportación |

### adapters/

| Componente | Descripción |
|------------|-------------|
| **persistence/** | JsonFileBoardRepository, json_file.py |
| **export/** | ExcelActivityExporter |
| **ui/** | QtClipboardProvider (implementa ClipboardProvider) |

### ui/

| Componente | Descripción |
|------------|-------------|
| **composition.py** | Composition root: create_board_service() |
| **presenters/** | TaskBoardPresenter, ReportsPresenter |
| **theme/constants.py** | ObjectNames, Layout (separación diseño) |
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
