# Análisis: Reporte de tiempo semanal/mensual

**Objetivo**: Evidenciar dónde va el tiempo de la persona que usa la app (semanal o mensualmente), para identificar oportunidades de mejora y reorientar prioridades.

---

## 1. ¿La estructura actual lo permite?

**Sí.** La estructura actual es suficiente para implementar un reporte de tiempo. Los datos necesarios ya existen.

---

## 2. Fuentes de datos disponibles

### 2.1 Transiciones (`transitions`)

Cada movimiento de tarea entre columnas se registra:

| Campo       | Descripción                              |
|-------------|------------------------------------------|
| `task_id`   | ID de la tarea                           |
| `task_name` | Nombre en el momento del movimiento      |
| `from_column` | Columna origen (null si creación)      |
| `to_column`  | Columna destino                         |
| `timestamp` | Fecha/hora ISO 8601 del movimiento      |

**Esto es la base**: entre dos transiciones consecutivas de una tarea, podemos calcular cuánto tiempo estuvo en cada columna.

### 2.2 Lógica existente

`domain/taskboard/utils.py`:

- **`compute_time_in_columns(task_id, transitions, current_column)`**  
  Ya calcula segundos en **In Progress** y **Detenido** por tarea. La lógica recorre las transiciones cronológicamente y acumula el tiempo en cada columna.
- **`format_seconds_duration(seconds)`**  
  Formato legible: "5h", "2d".

### 2.3 Metadatos de tarea para segmentar

| Campo              | Uso en reporte                                      |
|--------------------|------------------------------------------------------|
| `tribe_and_squad`  | Agrupar por tribu/squad                              |
| `solicitante`      | Tiempo por solicitante (para quién se trabaja)       |
| `reporting_channel`| Por canal de reporte                                |
| `categoria`        | Por categoría                                       |
| `prioridad`        | Alta vs normal                                      |
| `ticket`           | Código externo (Jira, etc.)                         |

---

## 3. Qué se puede calcular

### 3.1 Tiempo por columna (estado Kanban)

Para un periodo (semana, mes):

| Columna      | Interpretación                                          |
|--------------|----------------------------------------------------------|
| **Backlog**  | Tiempo en captura / cola (poca acción directa)          |
| **To Do**    | Tiempo en selección / planeación                         |
| **In Progress** | Tiempo en trabajo activo (foco principal)             |
| **Done**     | Tiempo “completada” hasta salir del tablero             |
| **Detenido** | Tiempo bloqueado / esperando                              |

### 3.2 Métricas derivadas

- **Ratio Activo vs Detenido**: cuánto tiempo productivo frente a bloqueos.
- **Tiempo en In Progress por tarea**: qué tareas consumen más atención.
- **Tareas más tiempo en Detenido**: posibles cuellos de botella.

### 3.3 Filtros temporales

- `timestamp` en ISO 8601 permite filtrar por rango de fechas.
- Ejemplos: “esta semana”, “este mes”, “últimos 7 días”, etc.

---

## 4. Limitaciones y supuestos

### 4.1 Tiempo ≠ tiempo real trabajado

El tiempo se infiere del flujo de tareas entre columnas.  
Ejemplo: “2h en In Progress” = la tarea estuvo 2h en esa columna, no necesariamente 2h de trabajo continuo.

### 4.2 Una sola persona

La app es personal: todas las tareas pertenecen al usuario. No hay multi-usuario ni asignación explícita de “quién trabajó”.

### 4.3 Fin de periodo abierto

Si una tarea sigue en una columna después del final del periodo, se usa `end_date` (o “ahora”) para truncar el intervalo y no contar tiempo futuro.

### 4.4 Transiciones como única fuente

Si no hay transiciones (p. ej. migración o datos antiguos), no hay tiempo calculable para esas tareas.

---

## 5. Cambios necesarios en el código

### 5.1 Dominio: nueva función

Generalizar el cálculo de tiempo a **todas** las columnas y a un periodo acotado:

```
compute_time_per_column_period(
    task_id: str,
    transitions: list[dict],
    from_date: datetime,
    to_date: datetime,
) -> dict[str, int]
```

Retorna segundos por columna (`backlog`, `todo`, `in_progress`, `done`, `detenido`) durante el rango `[from_date, to_date]`.

Variante más general para agregar por tarea:

```
compute_all_tasks_time_per_column(
    transitions: list[dict],
    from_date: datetime,
    to_date: datetime,
) -> list[dict]  # [{task_id, task_name, column_key: seconds, ...}]
```

### 5.2 Aplicación: caso de uso

Nuevo servicio o método en `ExportService`:

```
get_time_report(from_date, to_date) -> dict
```

Con salida estructurada:

- Total de segundos por columna.
- Desglose por tarea (opcional).
- Desglose por `tribe_and_squad`, `solicitante`, etc. (opcional).

### 5.3 Infraestructura: exportación

- **Excel**: nueva hoja “Reporte de tiempo” con:
  - Resumen: horas por columna.
  - Detalle: por tarea y columna.
  - Gráficos si se desea (p. ej.饼 chart).
- **Vista Reports**: nueva pestaña “Tiempo” con:
  - Selector de periodo (semana / mes).
  - Tabla o gráfico de distribución de tiempo.

### 5.4 Arquitectura

| Capa          | Cambio                                                    |
|---------------|-----------------------------------------------------------|
| Domain        | `compute_time_per_column_period` (o similar) en `utils.py` |
| Application   | Método en `ExportService` o servicio `TimeReportService`   |
| Infrastructure| Opcional: exportador específico de reporte de tiempo       |
| Presentation  | Pestaña “Tiempo” en Reports, filtros de fechas            |

---

## 6. Ejemplo de salida

### Resumen semanal

| Columna      | Horas | %   |
|--------------|-------|-----|
| In Progress  | 18    | 45% |
| Detenido     | 12    | 30% |
| To Do        | 5     | 12% |
| Done         | 3     | 8%  |
| Backlog      | 2     | 5%  |
| **Total**    | 40    | 100%|

### Detalle por tarea (Top 5 tiempo en In Progress)

| Tarea              | Ticket   | In Progress | Detenido |
|--------------------|----------|-------------|----------|
| Implementar login  | JIRA-123 | 8h          | 2h       |
| Revisar PRs        | -        | 5h          | 1h       |
| ...                |          |             |          |

---

## 7. Conclusión

| Pregunta                    | Respuesta                                                  |
|----------------------------|------------------------------------------------------------|
| ¿Los datos bastan?          | Sí. Transiciones + timestamps.                             |
| ¿Hay lógica reutilizable?  | Sí. `compute_time_in_columns` y `format_seconds_duration` |
| ¿Qué falta implementar?   | Generalizar a todas las columnas, filtrar por periodo, UI  |
| ¿Es viable?                | Sí. Estimación: bajo–medio esfuerzo.                      |

La estructura actual permite implementar un reporte de tiempo semanal/mensual que muestre dónde se va el tiempo por columna y por tarea, facilitando identificar oportunidades de mejora y reorientar prioridades.
