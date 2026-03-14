# Módulo Widget

Contenedor principal que lista todas las funcionalidades disponibles.

**Estado**: Activo.

---

## Responsabilidad

- Mostrar la lista visual de módulos (TaskBoard, Reports, Alerts)
- Cargar y mostrar la vista del módulo seleccionado
- Registrar metadata de módulos (id, título, descripción, icono, habilitado)

---

## Arquitectura

- **presentation/config/modules_registry.py**: Registro de módulos (`MODULES`)
- **presentation/modules/widget/**: MainShell, HeaderBar, InProgressCompact

---

## Flujo

1. MainShell arranca con HeaderBar (botones TaskBoard | Reports | Alerts)
2. Panel principal: InProgressCompact (In Progress + Detenidas)
3. Usuario hace clic en módulo → ModuleModal con la vista (TaskBoard, Reports, Alerts)
4. TaskBoard y Reports activos; Alerts en desarrollo
