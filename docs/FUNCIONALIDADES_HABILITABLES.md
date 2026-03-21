# Funcionalidades habilitables – DeepFlow

Documento de referencia: funcionalidades que existen en el código pero están deshabilitadas, o que tienen base lista para habilitarse con poco esfuerzo.

---

## 1. Módulos deshabilitados

### 1.1 Alerts (Alertas)

| Campo | Valor |
|-------|-------|
| **Estado** | `enabled: False` en `modules_registry.py` |
| **Ubicación** | `presentation/modules/alerts/view.py` |
| **Qué hace** | Placeholder: título "Alerts" y descripción "Notificaciones y alertas de WIP. Próximamente." |
| **Para habilitar** | Cambiar `enabled: True` en el módulo `alerts` de `MODULES` |
| **Para implementar** | Ver sección 2.1 |

---

## 2. Placeholders / pendientes de implementación

### 2.1 Módulo Alerts (implementación completa)

**Documentado en** `docs/codigo/modulos/alerts/README.md` y `data/DIAGRAMA_BASE_DATOS.md` (sección 6.4).

| Idea | Descripción | Base existente |
|------|-------------|----------------|
| Alertas de sobrecapacidad | Ya existe la lógica: `is_overcapacity(column_key)`, cabecera en rojo, "WARNING: OVERCAPACITY" en barra de título | ✅ BoardService |
| Recordatorios de tareas estancadas | Alertar si tarea en In Progress > N días sin movimiento | `compute_time_in_columns()`, transiciones |
| Notificaciones de escritorio | Toast/OS notification cuando se supera WIP | Requiere `infrastructure/notifications/` (nuevo adaptador) |

### 2.2 Semáforo en vista Resumen

| Campo | Valor |
|-------|-------|
| **Ubicación** | `presentation/modules/taskboard/summary_view.py`, `TaskSummaryRow` |
| **Estado actual** | Placeholder: muestra "○" fijo |
| **Intención** | Indicador visual de estado (ej. verde/ámbar/rojo según tiempo en columna) |
| **Base existente** | `domain/taskboard/utils.py`: `compute_time_in_columns()`, `format_task_duration()`, `format_seconds_duration()` |
| **Datos disponibles** | `(segundos_activo, segundos_detenido)` por tarea |

---

## 3. Funcionalidades ampliables con poco esfuerzo

### 3.1 Atajos de teclado

| Atajo actual | Acción |
|--------------|--------|
| Ctrl+V | Modal de creación con portapapeles |
| Enter | Confirmar en modal de creación |
| Escape | Cancelar en modal de creación |

**Posibles extensiones** (la app ya usa `QShortcut`, `eventFilter`):

- Ctrl+N: nueva tarea
- Ctrl+S: guardar en modal de detalle
- Flechas ↑↓ en listas/combos
- Tab para navegar entre campos

### 3.2 Exportación

| Formato | Estado | Ubicación |
|---------|--------|-----------|
| Excel | ✅ Activo | Reports → Exportar; `infrastructure/export/excel_exporter.py` |
| CSV | ✅ Activo | `export_transitions.py` |
| JSON | No existe | Fácil con estructura actual de datos |

### 3.3 Tema visual

- **Actual**: tema claro (paleta Slate + azul)
- **Base**: `styles.qss`, `presentation/style_loader.py`, paleta en `main.py`
- **Posible**: tema oscuro vía otro `.qss` o paleta dinámica

### 3.4 Campos de Subtask

**Esquema** (`data/DIAGRAMA_BASE_DATOS.md`): Subtask tiene `created_at`, `started_at`, `finished_at`, `estado`.

| Campo | En UI actual | Uso posible |
|-------|--------------|-------------|
| name/text | ✅ | Nombre editable |
| done/estado | ✅ | Checkbox completada |
| created_at, started_at, finished_at | No | Para métricas y reportes |
| order | Sí en normalización | Para reordenar subtareas |

---

## 4. Ideas de nuevas funcionalidades (sin código aún)

| Funcionalidad | Descripción | Dependencias |
|---------------|-------------|--------------|
| Búsqueda de tareas | Buscador por nombre, ticket | BoardService ya expone datos |
| Filtros en Reports | Filtrar por columna, tribu, fecha | ExportService, ReportsView |
| Reordenar columnas Kanban | Drag & drop de columnas (order) | Maestro `kanban_columns`, `save_kanban_columns` |
| Duplicar tarea | Copiar tarea con subtareas a nueva | `create_task`, `update_task_subtasks` |
| Archivo de tareas | Mover tareas "Done" antiguas a archivo | Nuevo concepto de datos |
| Configuración persistente | Guardar preferencias (tema, ventana) | Nuevo almacén o ampliar ZODB |

---

## 5. Cómo habilitar el módulo Alerts (sin implementar aún)

Si solo se quiere mostrar el placeholder de Alerts en el menú:

1. Abrir `presentation/config/modules_registry.py`
2. En el dict del módulo `alerts`, cambiar `"enabled": False` → `"enabled": True"`

El botón Alerts aparecerá en el HeaderBar (deshabilitado visualmente si `menuBtnDisabled` se aplica por `enabled`). Si el HeaderBar muestra los módulos según `enabled`, pasará a mostrarse como los demás.

---

## 6. Resumen rápido

| Prioridad | Funcionalidad | Esfuerzo | Cambio principal |
|-----------|---------------|----------|------------------|
| Baja | Habilitar módulo Alerts (placeholder) | Mínimo | 1 línea en `modules_registry.py` |
| Media | Semáforo en resumen | Bajo | `TaskSummaryRow` + `compute_time_in_columns` |
| Media | Más atajos de teclado | Bajo | `QShortcut`, `eventFilter` |
| Alta | Alerts completo (estancadas, notificaciones) | Alto | Nuevo servicio + adaptador notificaciones |
| Alta | Tema oscuro | Medio | Nuevo QSS + paleta |
| Variable | Búsqueda, filtros, duplicar | Medio | Nueva UI + casos de uso |
