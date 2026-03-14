# DeepFlow – Infraestructura

## Persistencia

### Persistencia principal: ZODB (`data/db/deepflow_db.fs`)

La app usa ZODB como base de datos en `data/db/`. Si existe `deepflow_db.json` o `monoflow_db.json` (legacy, en `data/` o raíz) y no hay `data/db/deepflow_db.fs`, se migra automáticamente.

**Estructura de datos:** Ver **[data/DIAGRAMA_BASE_DATOS.md](../../data/DIAGRAMA_BASE_DATOS.md)** para el diagrama completo.

- **Columnas**: backlog, todo, in_progress, done, detenido
- **Tareas**: `id`, `ticket`, `name`, `tribe_and_squad`, `requester`, `reporting_channel`, `entered_at`, `started_at`, `finished_at`, `subtasks`
- **Transiciones**: cada creación o movimiento genera un registro (`task_id`, `task_name`, `from_column`, `to_column`, `timestamp`)

### Exportar transiciones a CSV

```bash
python export_transitions.py
python export_transitions.py -o mis_datos.csv
```

Campos: `task_id`, `ticket`, `task_name`, `started_at`, `finished_at`.

---

## Estilos

### Ubicación

- `styles.qss` – definición de estilos
- `presentation/style_loader.py` – carga de estilos

### Selectores principales

| Selector | Uso |
|----------|-----|
| `QWidget#headerBar` | Barra de menú (TaskBoard | Reports | Alerts) |
| `QWidget#inProgressCompact` | Panel In Progress + Detenidas |
| `QFrame#sectionHeader` | Cabeceras de sección |
| `QFrame#compactTaskRow` | Fila de tarea en panel |
| `QWidget#column` | Contenedor de columna (TaskBoard) |
| `QFrame#taskCard` | Tarjeta de tarea |
| `QFrame#taskCard[column="done"]` | Tarjeta finalizada |
| `QFrame#taskCard[column="detenido"]` | Tarjeta bloqueada |
| `QPushButton#compactCreateBtn` | Botón + (In Progress) |
| `QPushButton#primaryBtn` | Botón primario (Exportar, Guardar) |
| `QDialog#taskInputDialog` | Modal nueva actividad |

### Personalización

1. Editar `styles.qss` directamente
2. Crear otro `.qss` y pasarlo a `load_styles(widget, "mi_tema.qss")`
