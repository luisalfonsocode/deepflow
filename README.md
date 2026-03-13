# DeepFlow

Widget de escritorio para captura sin fricción y gestión de límites WIP (Work In Progress). Diseñado para eliminar la fricción en la captura de datos y forzar productividad mediante límites de trabajo en curso.

---

## Requisitos

- **Python** 3.10+
- **PyQt6** ≥ 6.4.0

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

En macOS, si es necesario:

```bash
python3 main.py
```

## Tests

```bash
pytest tests/ -v
```

---

## Características

### Tablero Kanban (5 columnas)

| Columna       | Función                    | Límite WIP |
|---------------|----------------------------|------------|
| **Backlog**   | Entrada inicial de tareas  | 3          |
| **To Do**     | Selección para la sesión   | 3          |
| **In Progress** | Trabajo activo           | 3          |
| **Done**      | Tareas finalizadas         | 3          |
| **Detenido**  | Tareas bloqueadas          | 3          |

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

Cuando una columna supera el límite de 3 tareas:

- La cabecera de la columna se marca en rojo
- La barra de título muestra: **WARNING: OVERCAPACITY**

### Otras funciones

- **Minimizar**: Botón − en la barra de título.
- **Ventana siempre visible**: Always on Top.
- **Sin bordes**: Ventana minimalista con barra de título personalizada.
- **Arrastrar ventana**: Desde la barra de título.
- **Transiciones registradas**: Todos los movimientos se guardan para análisis posterior.

---

## Estructura del proyecto

```
deepflow/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── monoflow_db.json       # Datos persistentes (generado automáticamente)
├── styles.qss             # Estilos (tema oscuro)
│
├── core/modules/           # Lógica de negocio por módulo
│   ├── widget/            # Registro de funcionalidades
│   ├── taskboard/         # Kanban: creación, modificación, consulta
│   ├── reports/           # (en desarrollo)
│   └── alerts/            # (en desarrollo)
│
├── adapters/               # Implementaciones
│   └── persistence/       # JsonFileBoardRepository, json_file
│
├── ui/modules/             # Interfaz por módulo
│   ├── widget/            # MainShell, ModuleCard (lista de módulos)
│   ├── taskboard/         # TaskBoardView, widgets Kanban
│   ├── reports/           # ReportsView (en desarrollo)
│   └── alerts/            # AlertsView (en desarrollo)
│
├── ui/widgets.py          # TitleBar (compartido)
├── ui/window.py           # MonoFlowWindow (standalone TaskBoard)
├── ui/style_loader.py     # Carga de estilos
│
└── export_transitions.py   # Exportar tareas (started_at, finished_at) a CSV
```

### Separación lógica/UI (Puertos y Adaptadores)

- **core/modules/taskboard/**: Puertos (BoardRepository), servicios (BoardService).
- **adapters/persistence**: JsonFileBoardRepository (JSON local). Futuro: ApiBoardRepository.
- **ui/**: Componentes visuales. Recibe callbacks; puede intercambiarse.
- **styles.qss**: Permite cambiar el tema sin modificar lógica.

---

## Persistencia

### Archivo `monoflow_db.json`

```json
{
  "backlog": [
    { "id": "uuid", "name": "Nombre o contenido de la tarea" }
  ],
  "todo": [],
  "in_progress": [],
  "done": [
    { "id": "uuid", "name": "Tarea", "started_at": "2026-03-13T01:20:00+00:00", "finished_at": "2026-03-13T02:00:00+00:00" }
  ],
  "detenido": []
}
```

- **Tareas**: `id` (UUID) y `name` (texto; puede ser multilínea).
- **started_at**: Primera vez que la tarea llega a *In Progress* (ISO 8601 UTC).
- **finished_at**: Última vez que la tarea llega a *Done* (ISO 8601 UTC).

### Exportar tareas a CSV

```bash
python export_transitions.py                    # Salida: monoflow_tasks.csv
python export_transitions.py -o mis_datos.csv   # Archivo personalizado
```

Campos del CSV: `task_id`, `task_name`, `started_at`, `finished_at`.

---

## Atajos de teclado

| Atajo    | Acción                                      |
|----------|---------------------------------------------|
| **Ctrl+V** | Abre modal de creación con portapapeles   |
| **Enter**  | Confirma en el modal de creación           |
| **Escape** | Cancela en el modal de creación           |

---

## Paleta de colores (tema oscuro)

| Uso     | Código   |
|---------|----------|
| Fondo   | `#1e1e1e` |
| Acento  | `#007acc` |
| Alerta  | `#ff4444` |
| Detenido| `#ff9800` |

---

## Principios del proyecto (.cursorrules)

1. **Finalizar sobre Empezar**: Priorizar completar tareas antes de iniciar nuevas.
2. **Simplicidad**: Solo el nombre de la tarea es obligatorio. Sin campos de descripción adicionales.
3. **Límite WIP inviolable**: Máximo 3 tareas por columna en cualquier refactorización o feature.

---

## Documentación

Organizada por módulos. Ver **[docs/README.md](docs/README.md)** para el índice completo.

| Sección | Enlaces |
|---------|---------|
| **Módulos** | [Widget](docs/modulos/widget/README.md) · [TaskBoard](docs/modulos/taskboard/README.md) · [Reports](docs/modulos/reports/README.md) · [Alerts](docs/modulos/alerts/README.md) |
| **API** | [TaskBoard API](docs/modulos/taskboard/API.md) |
| **Arquitectura** | [Arquitectura](docs/arquitectura.md) · [Infraestructura](docs/infraestructura.md) · [Validación crecimiento](docs/validacion-crecimiento.md) |

## Compatibilidad

- **Windows**: Objetivo principal.
- **macOS**: Compatible. Fuente por defecto: Helvetica Neue.
- **Linux**: Debería funcionar con PyQt6 instalado.
