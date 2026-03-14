# Guía de desarrollo

Principios, estructura y buenas prácticas del proyecto DeepFlow.

---

## Arquitectura

### Capas

| Capa | Ubicación | Responsabilidad |
|------|-----------|-----------------|
| **Domain** | `domain/` | Reglas de negocio, constantes, maestros |
| **Application** | `application/` | Casos de uso, puertos (Protocols) |
| **Infrastructure** | `infrastructure/` | Implementaciones: persistencia (ZODB), export (Excel), clipboard |
| **Presentation** | `presentation/` | Vistas PyQt6, presentadores, composición |
| **Export** | `export_transitions.py` | Exportar tareas a CSV |

### Principios SOLID aplicados

- **S (Single Responsibility)**: BoardService solo orquesta CRUD y reglas WIP. ExportService solo obtiene datos. Las vistas solo renderizan.
- **O (Open/Closed)**: Nuevos repositorios implementan `BoardRepository`. Nuevos exportadores siguen la interfaz de ExcelActivityExporter.
- **L (Liskov)**: Cualquier implementación de `BoardRepository` es intercambiable.
- **I (Interface Segregation)**: `BoardRepository`, `ClipboardProvider` son contratos específicos.
- **D (Dependency Inversion)**: BoardService depende de `BoardRepository` (Protocol), no de ZODB. La UI recibe servicios inyectados.

### Separación UI / lógica

- **Vistas**: Solo construyen widgets, manejan eventos y delegan al presentador o servicio.
- **Presentadores**: Orquestan (ReportsPresenter). Reciben datos del servicio y los preparan para la vista.
- **Servicios**: Lógica de negocio pura. Sin imports de PyQt.
- **Domain**: Sin dependencias de UI ni infrastructure.

---

## Estructura de carpetas

```
deepflow/
├── main.py                 # Punto de entrada
├── domain/                 # Reglas de negocio
│   └── taskboard/          # constants, masters, utils
├── application/            # Casos de uso
│   ├── ports/              # BoardRepository, ClipboardProvider
│   ├── taskboard/          # BoardService
│   └── reports/            # ExportService
├── infrastructure/         # Implementaciones
│   ├── persistence/        # ZODBBoardRepository
│   ├── export/             # ExcelActivityExporter
│   └── ui/                 # QtClipboardProvider
├── presentation/           # Interfaz
│   ├── composition.py      # Composition root
│   ├── presenters/         # ReportsPresenter
│   ├── theme/              # Constantes de diseño
│   └── modules/            # Vistas por módulo
├── export_transitions.py   # Exportar tareas a CSV
├── tests/
└── docs/
```

---

## Cómo añadir

### Nueva columna en el tablero

1. `domain/taskboard/constants.py`: Añadir a `COLUMNS`
2. `domain/taskboard/masters.py`: Añadir en `KANBAN_COLUMNS` y en `col_key_to_display` (utils)
3. Las vistas que iteran las columnas se actualizan automáticamente

### Nuevo campo en tareas

1. Actualizar BoardService (create_task, etc.) para incluir el campo
2. Si hay datos existentes: ver [versionado-base-datos.md](versionado-base-datos.md)

### Nuevo exportador

1. Crear clase con método `export(activities, subtasks, transitions, filepath) -> bool`
2. Registrar en `ReportsPresenter` (inyección o por defecto)

---

## Tests

```bash
pytest tests/ -v
```

Los tests usan `InMemoryBoardRepository` (conftest). No tocan la base de datos real.

---

## Documentación

- [docs/README.md](../README.md) – Índice
- [arquitectura-tecnica.md](arquitectura-tecnica.md) – Flujo, puertos, adaptadores
- [estructura.md](estructura.md) – Mapa completo del proyecto
- [versionado-base-datos.md](versionado-base-datos.md) – Migraciones de schema
