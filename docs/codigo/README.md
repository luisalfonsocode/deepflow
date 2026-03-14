# Documentación de código

Referencia técnica: estructura del proyecto, arquitectura, guías de desarrollo y APIs de módulos.

---

## Documentos principales

| Documento | Descripción |
|-----------|-------------|
| [estructura.md](estructura.md) | Mapa completo de archivos y directorios |
| [arquitectura-clean.md](arquitectura-clean.md) | Guía Clean Architecture (domain, application, infrastructure, presentation) |
| [arquitectura-tecnica.md](arquitectura-tecnica.md) | Flujo de datos, puertos, adaptadores |
| [desarrollo.md](desarrollo.md) | Principios SOLID, cómo añadir columnas, campos, exportadores |
| [infraestructura.md](infraestructura.md) | Persistencia ZODB, estilos QSS |
| [versionado-base-datos.md](versionado-base-datos.md) | Migraciones de schema |

---

## Módulos

| Módulo | Descripción |
|--------|-------------|
| [Widget](modulos/widget/README.md) | MainShell, HeaderBar, InProgressCompact |
| [TaskBoard](modulos/taskboard/README.md) | Kanban, tareas, WIP |
| [TaskBoard API](modulos/taskboard/API.md) | Métodos de BoardService, tests |
| [Reports](modulos/reports/README.md) | Reportes, exportación Excel |
| [Alerts](modulos/alerts/README.md) | Alertas (en desarrollo) |
