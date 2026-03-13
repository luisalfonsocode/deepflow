# Guía de desarrollo

Principios, estructura y buenas prácticas del proyecto DeepFlow.

---

## Arquitectura

### Capas

| Capa | Ubicación | Responsabilidad |
|------|-----------|-----------------|
| **Core** | `core/` | Lógica de negocio, puertos (Protocols), constantes |
| **Adapters** | `adapters/` | Implementaciones: persistencia (ZODB, JSON), export (Excel), UI (clipboard) |
| **UI** | `ui/` | Vistas PyQt6, presentadores, composición |
| **Scripts** | `scripts/` | Pipeline, exportación, tests |

### Principios SOLID aplicados

- **S (Single Responsibility)**: BoardService solo orquesta CRUD y reglas WIP. ExportService solo obtiene datos. Las vistas solo renderizan.
- **O (Open/Closed)**: Nuevos exportadores implementan `ActivityExporter`. Nuevos repositorios implementan `BoardRepository`.
- **L (Liskov)**: Cualquier implementación de `BoardRepository` es intercambiable.
- **I (Interface Segregation)**: `BoardRepository`, `ActivityExporter`, `ClipboardProvider` son contratos específicos.
- **D (Dependency Inversion)**: BoardService depende de `BoardRepository` (Protocol), no de ZODB. La UI recibe servicios inyectados.

### Separación UI / lógica

- **Vistas**: Solo construyen widgets, manejan eventos y delegan al presentador o servicio.
- **Presentadores**: Orquestan (ReportsPresenter). Reciben datos del servicio y los preparan para la vista.
- **Servicios**: Lógica de negocio pura. Sin imports de PyQt.
- **Core**: Sin dependencias de UI ni adapters.

---

## Estructura de carpetas

```
deepflow/
├── main.py                 # Punto de entrada
├── core/                   # Lógica de negocio
│   ├── modules/
│   │   ├── taskboard/      # Kanban: BoardService, ports, utils
│   │   ├── reports/        # ExportService
│   │   └── widget/         # Registro MODULES
│   ├── ports/              # Re-export BoardRepository
│   └── services/           # Re-export BoardService
├── adapters/
│   ├── persistence/        # ZODBBoardRepository, JsonFileBoardRepository
│   ├── export/             # ExcelActivityExporter
│   └── ui/                 # QtClipboardProvider
├── ui/
│   ├── composition.py      # Composition root
│   ├── presenters/         # ReportsPresenter
│   ├── theme/              # Constantes de diseño
│   ├── ports/              # ClipboardProvider
│   └── modules/            # Vistas por módulo
├── scripts/                # Pipeline, export, tests
├── tests/
└── docs/
```

---

## Cómo añadir

### Nueva columna en el tablero

1. `core/modules/taskboard/constants.py`: Añadir a `COLUMNS`
2. `core/modules/taskboard/utils.py`: Añadir en `col_key_to_display`
3. Las vistas que iteran `COLUMNS` se actualizan automáticamente

### Nuevo campo en tareas

1. Actualizar BoardService (create_task, etc.) para incluir el campo
2. Si hay datos existentes: ver [VERSIONADO_BASE_DATOS.md](VERSIONADO_BASE_DATOS.md)

### Nuevo exportador

1. Implementar `ActivityExporter` (método `export(activities, filepath) -> bool`)
2. Registrar en `ReportsPresenter` o `composition`

---

## Tests

```bash
pytest tests/ -v
python -m scripts.run_tests
```

Los tests usan `InMemoryBoardRepository` (conftest). No tocan la base de datos real.

---

## Documentación

- [docs/README.md](README.md) – Índice
- [docs/ARQUITECTURA.md](ARQUITECTURA.md) – Flujo, puertos, adaptadores
- [docs/VERSIONADO_BASE_DATOS.md](VERSIONADO_BASE_DATOS.md) – Migraciones de schema
- [scripts/README.md](../scripts/README.md) – Pipeline y despliegue
