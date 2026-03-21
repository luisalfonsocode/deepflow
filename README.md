# DeepFlow

Widget de escritorio para captura sin fricción y gestión de límites WIP (Work In Progress). Diseñado para eliminar la fricción en la captura de datos y forzar productividad mediante límites de trabajo en curso.

---

## Índice

- [Requisitos](#requisitos)
- [Instalación](#instalacion)
- [Ejecución](#ejecucion)
- [Tests](#tests)
- [Características](#caracteristicas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Arquitectura Clean](#arquitectura-clean)
- [Persistencia](#persistencia)
- [Atajos de teclado](#atajos-de-teclado)
- [Tema visual](#tema-visual)
- [Principios del proyecto](#principios-del-proyecto)
- [Documentación](#documentacion)
- [Despliegue y actualizaciones](docs/despliegue-updates.md)
- [Compatibilidad](#compatibilidad)

---

<a id="requisitos"></a>
## Requisitos

- **Python** 3.10+
- **PyQt6** ≥ 6.4.0

<a id="instalacion"></a>
## Instalación

```bash
pip install -r requirements.txt
```

<a id="ejecucion"></a>
## Ejecución

```bash
python main.py
```

En macOS, si es necesario:

```bash
python3 main.py
```

<a id="tests"></a>
## Tests

```bash
pytest tests/ -v
```

---

<a id="caracteristicas"></a>
## Características

### Tablero Kanban (5 columnas)

| Columna       | Función                    | Límite WIP |
|---------------|----------------------------|------------|
| **Backlog**   | Entrada inicial (+ / Ctrl+V)| Sin límite |
| **To Do**     | Selección para la sesión   | 3          |
| **In Progress** | Trabajo activo           | 3          |
| **Done**      | Tareas finalizadas         | Sin límite |
| **Detenido**  | Tareas bloqueadas          | 5          |

> Los límites son configurables en **Maestros → Columnas Kanban**. Vacío = sin límite.

### Creación de tareas

- **Botón +**: Abre un modal para crear nueva actividad.
- **Ctrl+V**: Abre el mismo modal con el contenido del portapapeles pre-pegado.
- **Modal**: Soporta contenido multilínea (hasta 50+ líneas) con:
  - Área de texto amplia
  - Botón **Pegar** para insertar del portapapeles
  - Botones Crear / Cancelar

### Movimiento de tareas

- **Arrastrar y soltar**: Arrastra tarjetas entre columnas.
- **Botones ◀ ▶**: Movimiento rápido entre columnas anterior/siguiente.

### Alerta de sobrecapacidad

Cuando una columna supera su límite WIP configurado:

- La cabecera de la columna se marca en rojo
- La barra de título muestra: **WARNING: OVERCAPACITY**

### Otras funciones

- **Minimizar**: Botón − en la barra de título.
- **Ventana siempre visible**: Always on Top.
- **Sin bordes**: Ventana minimalista con barra de título personalizada.
- **Arrastrar ventana**: Desde la barra de título.
- **Transiciones registradas**: Todos los movimientos se guardan para análisis posterior.

---

<a id="estructura-del-proyecto"></a>
## Estructura del proyecto

Ver **[docs/codigo/estructura.md](docs/codigo/estructura.md)** para el mapa completo de archivos y distribución.

```
deepflow/
├── main.py                 # Punto de entrada
├── export_transitions.py   # Exportar tareas a CSV
├── requirements.txt        # Dependencias
├── styles.qss              # Estilos (tema claro)
├── data/                   # Datos persistentes
│   ├── db/                 # Base de datos ZODB
│   │   ├── deepflow_db.fs  # ZODB (generada en runtime)
│   │   └── deepflow_db.json   # Legacy (migrado a .fs si existe)
│   ├── DIAGRAMA_BASE_DATOS.md
│   └── README.md
├── domain/                 # Capa de dominio
├── application/            # Capa de aplicación (casos de uso)
├── infrastructure/         # Capa de infraestructura
├── presentation/           # Capa de presentación (PyQt6)
├── tests/
└── docs/
```

---

<a id="arquitectura-clean"></a>
## Arquitectura Clean

El proyecto sigue **Clean Architecture** con cuatro capas:

| Capa | Carpeta | Contenido |
|------|---------|-----------|
| **Domain** | `domain/` | Entidades, reglas de negocio, constantes (COLUMNS, maestros, utils) |
| **Application** | `application/` | Casos de uso (BoardService, ExportService), puertos (BoardRepository) |
| **Infrastructure** | `infrastructure/` | Persistencia ZODB/JSON, exportación Excel, adaptador clipboard Qt |
| **Presentation** | `presentation/` | UI PyQt6, composition root, presenters |

### Estructura detallada

```
domain/
└── taskboard/
    ├── constants.py    # COLUMNS, WIP_LIMIT_PER_COLUMN
    ├── masters.py      # Maestros (origen, tribu, kanban)
    └── utils.py        # col_key_to_display, format_*, compute_time_in_columns

application/
├── ports/
│   └── board_repository.py   # Puerto de persistencia
├── taskboard/
│   └── board_service.py      # BoardService (CRUD tablero)
└── reports/
    └── export_service.py    # ExportService (datos para reportes)

infrastructure/
├── persistence/              # ZODBBoardRepository, migraciones, schema_versions
├── export/                  # ExcelActivityExporter
└── ui/                      # QtClipboardProvider

presentation/
├── composition.py           # Composition root: create_board_service()
├── config/modules_registry.py   # MODULES (TaskBoard, Reports, Alerts)
├── presenters/
├── ports/
├── theme/
├── style_loader.py
└── modules/
    ├── widget/              # MainShell, HeaderBar, InProgressCompact
    ├── taskboard/           # TaskBoardView, dialogs, widgets
    ├── reports/             # ReportsView
    └── alerts/              # AlertsView
```

### Reglas de dependencia

- **domain** → Sin dependencias externas
- **application** → Depende de `domain`, define puertos
- **infrastructure** → Implementa puertos, depende de `domain`
- **presentation** → Depende de `application` e `infrastructure`

---

<a id="persistencia"></a>
## Persistencia

### ZODB (`data/db/deepflow_db.fs`)

- **Base de datos embebida**: ZODB (Zope Object Database), archivo `data/db/deepflow_db.fs`.
- **Versionado**: `schema_version` en root para migraciones futuras (ver `infrastructure/persistence/schema_versions.py`).
- **Migración desde JSON**: Si existe `deepflow_db.json` o `monoflow_db.json` (en `data/` o raíz) y no existe `data/db/deepflow_db.fs`, se migra automáticamente.

### Exportar tareas a CSV

```bash
python export_transitions.py                    # Salida: deepflow_tasks.csv
python export_transitions.py -o mis_datos.csv   # Archivo personalizado
```

Campos del CSV: `task_id`, `ticket`, `task_name`, `started_at`, `finished_at`.

---

<a id="atajos-de-teclado"></a>
## Atajos de teclado

| Atajo    | Acción                                      |
|----------|---------------------------------------------|
| **Ctrl+V** | Abre modal de creación con portapapeles   |
| **Enter**  | Confirma en el modal de creación           |
| **Escape** | Cancela en el modal de creación           |

---

<a id="tema-visual"></a>
## Tema visual

Tema claro con paleta Slate + azul:

| Uso     | Código   |
|---------|----------|
| Fondo   | `#f8fafc` |
| Acento  | `#2563eb` |
| Alerta  | `#ff4444` |
| Detenido| `#f59e0b` |

---

<a id="principios-del-proyecto"></a>
## Principios del proyecto (.cursorrules)

1. **Finalizar sobre Empezar**: Priorizar completar tareas antes de iniciar nuevas.
2. **Simplicidad**: Solo el nombre de la tarea es obligatorio. Sin campos de descripción adicionales.
3. **Límite WIP inviolable**: Máximo 3 tareas por columna en cualquier refactorización o feature.

---

<a id="documentacion"></a>
## Documentación

Organizada por módulos. Ver **[docs/README.md](docs/README.md)** para el índice completo.

| Sección | Enlaces |
|---------|---------|
| **Estructura** | [Mapa del proyecto](docs/codigo/estructura.md) – Distribución de archivos y módulos |
| **Módulos** | [Widget](docs/codigo/modulos/widget/README.md) · [TaskBoard](docs/codigo/modulos/taskboard/README.md) · [Reports](docs/codigo/modulos/reports/README.md) · [Maestros](docs/codigo/modulos/masters/README.md) · [Alerts](docs/codigo/modulos/alerts/README.md) |
| **API** | [TaskBoard API](docs/codigo/modulos/taskboard/API.md) |
| **Arquitectura** | [Clean Architecture](docs/codigo/arquitectura-clean.md) · [Arquitectura técnica](docs/codigo/arquitectura-tecnica.md) · [Desarrollo](docs/codigo/desarrollo.md) · [Infraestructura](docs/codigo/infraestructura.md) · [Versionado BD](docs/codigo/versionado-base-datos.md) |
| **Despliegue** | [Build y actualizaciones](docs/despliegue-updates.md) – Paquete de update sin tocar `data/` |

<a id="compatibilidad"></a>
## Compatibilidad

- **Windows**: Objetivo principal.
- **macOS**: Compatible. Fuente por defecto: Helvetica Neue.
- **Linux**: Debería funcionar con PyQt6 instalado.
