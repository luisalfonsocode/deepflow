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

- **core/modules/widget/**: Registro de módulos (`MODULES`)
- **ui/modules/widget/**: MainShell, ModuleCard, shell visual

---

## Flujo

1. MainShell arranca con sidebar mostrando tarjetas de módulos
2. Usuario selecciona un módulo → StackedWidget muestra la vista correspondiente
3. TaskBoard está habilitado; Reports y Alerts muestran placeholder hasta implementación
