# Módulo Reports

Reportes, dashboards, métricas y análisis de datos.

**Estado**: Activo.

---

## Responsabilidad

- Tres reportes: **Tareas**, **Subtareas**, **Transiciones**
- Exportación a Excel con una hoja por reporte
- Dashboard compacto (In Progress + Detenidas)

---

## Implementación actual

| Reporte    | Descripción                                      |
|-----------|---------------------------------------------------|
| **Tareas**| Tabla con id, nombre, columna, ticket, fechas     |
| **Subtareas** | Subtareas con padre, tiempo en columna        |
| **Transiciones** | Movimientos entre columnas con timestamps    |

- **Export**: `infrastructure/export/excel_exporter.py` (3 hojas)
- **Vista**: `presentation/modules/reports/view.py` (3 pestañas)

---

## Dependencia

- Lee datos del tablero vía `BoardRepository.get_board_data()` o `BoardService`.
