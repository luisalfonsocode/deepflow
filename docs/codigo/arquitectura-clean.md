# Clean Architecture Clásica – Guía explicada

Este documento explica **qué va en cada carpeta** de la Clean Architecture y **por qué**, con ejemplos del proyecto DeepFlow.

---

## ¿Para qué sirve?

Separar el código en capas hace que:

- El **dominio** (reglas de negocio) no dependa de la base de datos ni de la UI.
- Se puedan **cambiar** la BD o la UI sin tocar la lógica.
- Los **tests** sean más fáciles (dominio puro, sin I/O).

---

## Las 4 capas (de adentro hacia afuera)

```
                    ┌─────────────────────┐
                    │     DOMAIN          │  ← Más interno, sin dependencias
                    │  (reglas puras)     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   APPLICATION      │  ← Casos de uso, orquesta
                    │  (qué hace la app)  │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
 ┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼───────┐
 │ INFRASTRUCTURE  │  │ INFRASTRUCTURE  │  │ PRESENTATION  │
 │ (persistencia)  │  │ (export, UI)    │  │ (interfaz)    │
 └─────────────────┘  └─────────────────┘  └───────────────┘
```

---

## 1. Domain (dominio)

### ¿Qué va aquí?

- Reglas de negocio puras.
- Constantes y conceptos del dominio.
- Funciones que no usan BD, red ni UI.

### ¿Qué NO va aquí?

- Rutas de archivos, conexiones a BD.
- Imports de PyQt, openpyxl, ZODB.
- Cualquier dependencia externa.

### Ejemplos en DeepFlow

| Archivo | Qué contiene |
|---------|---------------|
| `domain/taskboard/constants.py` | `COLUMNS`, `WIP_LIMIT_PER_COLUMN` |
| `domain/taskboard/masters.py` | Maestros (origen, tribu, kanban), `get_column_keys()`, `get_wip_limit()` |
| `domain/taskboard/utils.py` | `col_key_to_display`, `format_date_display`, `compute_time_in_columns` |

### Criterio para decidir

> ¿Necesita acceso a disco, red o UI? **NO** → probablemente va en domain.

---

### Ejemplos concretos en DeepFlow

#### 1. Constantes (`domain/taskboard/constants.py`)

```python
COLUMNS = ("backlog", "todo", "in_progress", "done", "detenido")
WIP_LIMIT_PER_COLUMN = 3
```

**Por qué van en domain:** Son conceptos del Kanban. No dependen de BD ni UI.  
**NO incluir aquí:** Rutas como `DB_PATH`, `get_zodb_path()` → van en infrastructure.

---

#### 2. Maestros (`domain/taskboard/masters.py`)

```python
ORIGEN_OPTIONS = [{"key": "teams", "label": "Teams"}, {"key": "correo", "label": "Correo"}]
KANBAN_COLUMNS = [{"key": "backlog", "label": "Backlog", "order": 1, "wip_limit": 3}, ...]

def get_column_keys(kanban_columns): ...
def get_wip_limit(kanban_columns, column_key): ...
```

**Por qué van en domain:** Son catálogos del dominio. Las funciones solo transforman datos.  
**NO incluir aquí:** Lógica que guarde o lea de BD.

---

#### 3. Utilidades puras (`domain/taskboard/utils.py`)

```python
def col_key_to_display(key: str) -> str:
    return {"backlog": "Backlog", "todo": "To Do", ...}.get(key, key)

def format_date_display(iso_string: str | None) -> str:
    """'2026-03-13T10:00:00' → '13 Mar 2026'"""
    ...

def compute_time_in_columns(task_id, transitions, current_column) -> tuple[int, int]:
    """Calcula segundos en In Progress y en Detenido. Solo usa los datos que recibe."""
    ...
```

**Por qué van en domain:** Reciben datos y devuelven resultados. No abren archivos ni muestran nada en pantalla.  
**NO incluir aquí:** `load_styles()`, `QMessageBox`, acceso a `repository` o `board.data` desde aquí.

---

#### 4. Ejemplo de algo que NO va en domain

```python
# ❌ NO va en domain (acceso a disco)
def load_board():
    with open(DB_PATH) as f:
        return json.load(f)

# ❌ NO va en domain (depende de UI)
def show_warning(message):
    QMessageBox.warning(None, "Aviso", message)

# ❌ NO va en domain (rutas de archivos)
DB_PATH = Path("data/db/deepflow_db.fs")
```

Eso va en **infrastructure** o **presentation**.

---

#### Checklist: ¿Esto va en domain?

| Si es… | Va en domain |
|--------|---------------|
| Constante o valor fijo del negocio | Sí (COLUMNS, WIP_LIMIT, maestros) |
| Función que solo recibe datos y devuelve resultado | Sí (format_date_display, col_key_to_display) |
| Lógica que usa solo `datetime`, matemática, listas/dicts | Sí (compute_time_in_columns) |
| Usa `open()`, `Path`, ZODB, `requests` | **No** → infrastructure |
| Usa PyQt6, QMessageBox, QWidget | **No** → presentation |

---

## 2. Application (aplicación)

### ¿Qué va aquí?

- Casos de uso: qué hace la app paso a paso.
- Orquestación entre dominio e infraestructura.
- Definición de puertos (interfaces que la infraestructura implementa).

### ¿Qué NO va aquí?

- Detalles de cómo se guarda en disco.
- Detalles de cómo se pinta en pantalla.
- Lógica pura de negocio (esa va en domain).

### Ejemplos en DeepFlow

| Archivo | Qué contiene |
|---------|---------------|
| `application/ports/board_repository.py` | Puerto `BoardRepository`: `get_board_data()`, `save_board_data()` |
| `application/taskboard/board_service.py` | Caso de uso: crear/mover/eliminar tareas, WIP, transiciones |
| `application/reports/export_service.py` | Caso de uso: obtener datos para reportes (tareas, subtareas, transiciones) |

### Criterio para decidir

> ¿Describe **qué** hace la app o qué necesita para hacerlo? **SÍ** → application.  
> ¿Implementa **cómo** se guarda o se muestra? **NO** → eso va en infrastructure o presentation.

---

## 3. Infrastructure (infraestructura)

### ¿Qué va aquí?

- Implementaciones concretas de los puertos.
- Acceso a BD, archivos, APIs externas.
- Adaptadores (clipboard, Excel, etc.).

### ¿Qué NO va aquí?

- Reglas de negocio (domain).
- Orquestación de casos de uso (application).
- Widgets o pantallas (presentation).

### Ejemplos en DeepFlow

| Archivo | Qué contiene |
|---------|---------------|
| `infrastructure/persistence/zodb_repository.py` | Implementa `BoardRepository` con ZODB |
| `infrastructure/persistence/json_file.py` | Leer/guardar JSON (legacy) |
| `infrastructure/persistence/schema_versions.py` | Migraciones de schema |
| `infrastructure/persistence/config.py` | Rutas de BD (`get_zodb_path`) |
| `infrastructure/export/excel_exporter.py` | Exportar a Excel |
| `infrastructure/ui/qt_clipboard.py` | Implementa acceso al portapapeles con Qt |

### Criterio para decidir

> ¿Habla con algo externo (disco, red, sistema operativo)? **SÍ** → infrastructure.  
> ¿Implementa un puerto definido en application? **SÍ** → infrastructure.

---

## 4. Presentation (presentación)

### ¿Qué va aquí?

- Interfaz de usuario: ventanas, botones, listas.
- Composición: unir capas (crear `BoardService` con su repositorio).
- Presenters que conectan la UI con los casos de uso.

### ¿Qué NO va aquí?

- Reglas de negocio (domain).
- Lógica de persistencia (infrastructure).
- Casos de uso puros (application) – pero sí se usan desde aquí.

### Ejemplos en DeepFlow

| Archivo / carpeta | Qué contiene |
|-------------------|--------------|
| `presentation/composition.py` | `create_board_service()` – crea repositorio y BoardService |
| `presentation/config/modules_registry.py` | Lista de módulos (TaskBoard, Reports, Alerts) para el menú |
| `presentation/modules/widget/` | MainShell, HeaderBar, InProgressCompact |
| `presentation/modules/taskboard/` | TaskBoardView, dialogs, TaskCard |
| `presentation/modules/reports/` | ReportsView (tabs, tabla, botón Excel) |
| `presentation/presenters/reports_presenter.py` | Conecta ReportsView con ExportService y Excel |
| `presentation/style_loader.py` | Carga `styles.qss` |
| `presentation/theme/` | Constantes de diseño (ObjectNames, Layout) |

### Criterio para decidir

> ¿Es un widget, una ventana o cómo se ve algo? **SÍ** → presentation.  
> ¿Construye dependencias (composition root)? **SÍ** → presentation.

---

## Resumen rápido: ¿dónde pongo esto?

| Tengo… | Carpeta |
|--------|---------|
| Constantes, maestros, funciones puras de formato | **domain** |
| Definición de un contrato (interface/protocol) | **application/ports** |
| Caso de uso (crear tarea, exportar reporte) | **application** |
| Implementación de guardado en ZODB/JSON | **infrastructure** |
| Llamada a Excel, clipboard, APIs | **infrastructure** |
| Rutas de archivos, config de BD | **infrastructure** |
| Ventana, botón, tabla, diálogo | **presentation** |
| Código que une domain + application + infrastructure | **presentation** (composition) |

---

## Reglas de dependencia

```
domain          → nada (es el centro)
application     → domain
infrastructure  → domain, application (solo implementa puertos)
presentation    → application, infrastructure, domain
```

- **domain** nunca importa de application, infrastructure ni presentation.
- **application** nunca importa de infrastructure ni presentation.
- **infrastructure** y **presentation** sí pueden importar de las capas internas.

---

## Flujo típico: crear una tarea

1. El usuario hace clic en "Crear" en la **presentation**.
2. La presentation llama a `board.create_task("Mi tarea")` de **application**.
3. **Application** (BoardService) usa su regla de negocio y llama a `repository.save_board_data()`.
4. **Infrastructure** (ZODBBoardRepository) implementa ese puerto y escribe en el archivo `.fs`.
5. La **presentation** refresca la vista con los datos que devuelve application.

La lógica de "solo 3 tareas por columna" está en application/domain.  
Cómo se guarda en disco está en infrastructure.  
Cómo se muestra está en presentation.
