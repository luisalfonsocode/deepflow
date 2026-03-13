# MonoFlow – Infraestructura

## Persistencia

### Archivo `monoflow_db.json`

```json
{
  "backlog": [{ "id": "uuid", "name": "Nombre" }],
  "todo": [],
  "in_progress": [],
  "done": [],
  "detenido": [],
  "transitions": [
    {
      "task_id": "uuid",
      "task_name": "Nombre",
      "from_column": "backlog",
      "to_column": "todo",
      "timestamp": "2026-03-13T01:20:21.206051+00:00"
    }
  ]
}
```

- **Tareas**: `id` (UUID) y `name` (texto; puede ser multilínea)
- **Transiciones**: cada creación o movimiento genera un registro

### Exportar transiciones a CSV

```bash
python export_transitions.py
python export_transitions.py -o mis_datos.csv
```

Campos: `timestamp`, `task_id`, `task_name`, `from_column`, `to_column`.

---

## Estilos

### Ubicación

- `styles.qss` – definición de estilos
- `ui/style_loader.py` – carga de estilos

### Selectores principales

| Selector | Uso |
|----------|-----|
| `QWidget#titleBar` | Barra de título |
| `QWidget#titleBar[overcapacity="true"]` | Barra en modo alerta |
| `QWidget#column` | Contenedor de columna |
| `QFrame#taskCard` | Tarjeta de tarea |
| `QFrame#taskCard[column="done"]` | Tarjeta finalizada |
| `QFrame#taskCard[column="detenido"]` | Tarjeta bloqueada |
| `QPushButton#navBtn` | Botones ◀ ▶ |
| `QPushButton#createBtn` | Botón + |
| `QPushButton#minimizeBtn` | Botón minimizar |
| `QPushButton#actionBtn` | Botones ✎ ✕ |
| `QDialog#taskInputDialog` | Modal nueva/editar actividad |

### Personalización

1. Editar `styles.qss` directamente
2. Crear otro `.qss` y pasarlo a `load_styles(widget, "mi_tema.qss")`
