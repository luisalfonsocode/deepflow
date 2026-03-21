# DeepFlow – Estructura y distribución del proyecto

Mapa completo de archivos y directorios para entender la organización del código.

---

## 1. Vista general

```
deepflow/
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias Python
├── styles.qss                 # Estilos QSS (tema de la interfaz)
├── .cursorrules               # Reglas del editor (WIP, simplicidad)
│
├── data/                      # Datos persistentes (no versionar archivos db/)
│   ├── db/                    # Base de datos (ZODB + legacy JSON)
│   │   ├── .gitkeep           # Mantiene el directorio en git
│   │   ├── deepflow_db.fs     # ZODB (generada en runtime)
│   │   └── deepflow_db.json   # Legacy JSON (migrado a .fs si existe)
│   ├── DIAGRAMA_BASE_DATOS.md
│   └── README.md
│
├── export_transitions.py      # Exportar tareas a CSV
├── domain/                    # Capa de dominio (entidades, reglas)
├── application/               # Capa de aplicación (casos de uso)
├── infrastructure/            # Capa de infraestructura (persistencia, export)
├── presentation/              # Capa de presentación (PyQt6)
├── tests/                     # Tests unitarios
└── docs/                      # Documentación
```

---

## 2. Raíz del proyecto

| Archivo          | Propósito |
|------------------|-----------|
| `main.py`        | Arranca la app: QApplication, paleta, estilos, MainShell |
| `requirements.txt` | PyQt6, ZODB, openpyxl, pytest |
| `styles.qss`     | Estilos visuales (tema claro, colores, componentes) |
| `.cursorrules`   | Convenciones del proyecto para el IDE |

**Directorio `data/`** (no versionar los archivos de base de datos):
- `data/db/deepflow_db.fs` – Base ZODB principal
- `data/db/deepflow_db.fs.index`, `.lock`, `.tmp`
- `data/db/deepflow_db.json` – JSON en carpeta datos
- Migración: si existe `deepflow_db.json` o `monoflow_db.json` (legacy) y no hay `data/db/deepflow_db.fs`, se migra automáticamente

---

## 3. Clean Architecture

### domain/ (dominio)

```
domain/
├── __init__.py
└── taskboard/
    ├── constants.py    # COLUMNS (legacy), WIP_LIMIT_PER_COLUMN, TZ_APP
    ├── masters.py      # KANBAN_COLUMNS, get_column_keys, get_wip_limit
    └── utils.py        # col_key_to_display, normalize_key_from_label, format_*, compute_time_in_columns
```

### application/ (casos de uso)

```
application/
├── ports/
│   └── board_repository.py   # Puerto de persistencia
├── taskboard/
│   └── board_service.py     # BoardService (CRUD tablero)
└── reports/
    └── export_service.py   # ExportService (datos para reportes)
```

### infrastructure/ (infraestructura)

```
infrastructure/
├── persistence/
│   ├── config.py            # Rutas DB (get_zodb_path)
│   ├── zodb_repository.py   # Implementa BoardRepository
│   ├── json_file.py         # load_board, save_board (legacy)
│   ├── json_to_zodb.py      # Migración JSON → ZODB
│   └── schema_versions.py   # Versionado y migraciones
├── export/
│   └── excel_exporter.py    # Exporta a Excel
└── ui/
    └── qt_clipboard.py      # QtClipboardProvider
```

### presentation/ (presentación)

```
presentation/
├── composition.py           # Composition root: create_board_service()
├── config/
│   └── modules_registry.py  # MODULES: TaskBoard, Reports, Alerts
├── presenters/
├── ports/
├── theme/
├── style_loader.py
└── modules/
    ├── taskboard/           # Vista Kanban
    ├── reports/             # Vista reportes
    ├── alerts/              # Vista alertas
    └── widget/              # Shell, HeaderBar, InProgressCompact
```

### Puertos y adaptadores

| Puerto (application) | Implementación (infrastructure) |
|-----------------------|--------------------------------|
| BoardRepository     | ZODBBoardRepository            |
| ClipboardProvider   | QtClipboardProvider            |

---

## 5. Presentation (presentación)

```
presentation/
├── __init__.py              # Expone MainShell
├── composition.py           # Composition root: create_board_service()
├── style_loader.py          # Carga styles.qss
│
├── theme/
│   ├── __init__.py
│   └── constants.py        # ObjectNames, Layout (dimensiones, estilos)
│
├── ports/
│   ├── __init__.py
│   └── clipboard_provider.py   # Protocolo para portapapeles
│
├── presenters/
│   ├── __init__.py
│   ├── reports_presenter.py    # Orquesta Reports + ExportService + Excel
│   └── masters_presenter.py    # Orquesta MastersView + BoardService
│
└── modules/
    ├── __init__.py
    ├── widget/                  # Shell principal
    │   ├── __init__.py
    │   ├── shell.py             # MainShell, ModuleModal
    │   ├── header_bar.py        # Barra de menú (TaskBoard | Reports | Alerts)
    │   └── in_progress_compact.py   # Panel In Progress + Detenidas
    ├── taskboard/               # UI del Kanban
    │   ├── __init__.py
    │   ├── view.py              # TaskBoardView (columnas desde maestro)
    │   ├── widgets.py           # TaskCard, ColumnWidget, TaskInputDialog
    │   ├── dialogs.py           # TaskDetailDialog (detalle/edición)
    │   ├── task_row.py          # CompactTaskRow
    │   └── summary_view.py      # Vista resumen (lista tareas)
    ├── masters/                 # Vista Maestros (tribu, solicitante, kanban_columns)
    │   ├── __init__.py
    │   └── view.py              # MastersView (tabs editables)
    ├── reports/
    │   ├── __init__.py
    │   └── view.py              # ReportsView (3 tabs: Tareas, Subtareas, Transiciones)
    └── alerts/
        ├── __init__.py
        └── view.py              # AlertsView (placeholder)
```

### Flujo de la presentación

```
main.py
  └─ MainShell (shell.py)
       ├─ HeaderBar (botones de módulos)
       ├─ InProgressCompact (panel In Progress + Detenidas)
       └─ Al hacer clic en módulo → ModuleModal con:
            · TaskBoardView (Kanban)
            · ReportsView (tabs + Excel)
            · MastersView (Maestros + Columnas Kanban)
            · AlertsView (placeholder)
```

---

## 6. Exportar a CSV

```bash
python export_transitions.py [-o archivo.csv]
```

Exporta `task_id`, `ticket`, `task_name`, `started_at`, `finished_at`.

---

## 7. Tests

```
tests/
├── __init__.py
├── conftest.py               # InMemoryBoardRepository, fixtures
├── test_board_service.py     # Tests de BoardService (39 tests)
└── test_domain_utils.py      # Tests de domain.taskboard.utils (normalize_key_from_label, etc.)
```

---

## 8. Documentación

Ver [docs/README.md](../README.md) para el índice completo.

---

## 9. Dependencias entre capas

```
main.py
  └─ presentation (MainShell)
       └─ presentation/composition (create_board_service)
            └─ infrastructure/persistence (ZODBBoardRepository)
                 └─ application (BoardService, BoardRepository)

presentation/modules/widget/shell
  └─ application (BoardService, MODULES)
  └─ presentation/modules/taskboard (TaskBoardView)
  └─ presentation/modules/reports (ReportsView + ReportsPresenter)
  └─ presentation/modules/alerts (AlertsView)

ReportsPresenter
  └─ application (BoardService)
  └─ application/reports (ExportService)
  └─ infrastructure/export (ExcelActivityExporter)
```

**Regla**: `domain` no depende de capas externas. `application` define puertos; `infrastructure` los implementa.

---

## 10. Archivos de datos

| Ubicación | Cuándo se crea | Contenido |
|-----------|----------------|-----------|
| `data/db/deepflow_db.fs` | Al guardar datos | Base ZODB (tablero, transiciones) |
| `data/db/deepflow_db.json` | Manual o legacy | JSON; si existe y no hay .fs, se migra |
| Raíz `deepflow_db.json` o `monoflow_db.json` | Legacy | Si existe y no hay data/db/deepflow_db.fs, se migra |
| CSV exportado | `python export_transitions.py` | task_id, ticket, task_name, started_at, finished_at |
| Excel exportado | Botón en Reports | 3 hojas: Tareas, Subtareas, Transiciones |
