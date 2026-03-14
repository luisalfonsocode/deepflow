# Validación: Estructura para el Crecimiento

## Resumen

La estructura actual **sí soporta** el crecimiento previsto (TaskBoard, Reporters, Alerts).

---

## Reglas de dependencia

| Desde     | Hacia                    | Permitido |
|-----------|--------------------------|-----------|
| TaskBoard | Reporters, Alerts        | ❌ No     |
| Reporters | TaskBoard (solo lectura)| ✅ Sí     |
| Alerts    | TaskBoard (solo lectura)| ✅ Sí     |
| UI        | Cualquier módulo         | ✅ Sí     |

---

## Integración de módulos futuros

- **Reporters**: Inyectar `BoardRepository` y usar `get_board_data()` para transiciones.
- **Alerts**: Inyectar `BoardRepository` y un adaptador de notificaciones.
- **Adaptadores nuevos**: `infrastructure/export/`, `infrastructure/notifications/`.

---

## Estructura de UI al crecer

```
presentation/
├── modules/
│   ├── taskboard/   # Ventana y widgets del Kanban
│   ├── reports/    # Vistas de reportes
│   └── alerts/     # Panel de alertas
└── style_loader.py
```
