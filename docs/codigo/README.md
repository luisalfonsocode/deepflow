# Documentación de código

Referencia técnica: estructura, arquitectura y APIs. El índice completo está en [docs/README.md](../README.md).

---

## Documentos

| Documento | Descripción |
|-----------|-------------|
| [estructura](estructura.md) | Mapa de archivos y directorios |
| [arquitectura-clean](arquitectura-clean.md) | Capas: domain, application, infrastructure, presentation |
| [arquitectura-tecnica](arquitectura-tecnica.md) | Flujo de datos, puertos, adaptadores |
| [desarrollo](desarrollo.md) | SOLID, añadir columnas/campos/exportadores |
| [infraestructura](infraestructura.md) | Persistencia ZODB, estilos QSS |
| [versionado-base-datos](versionado-base-datos.md) | Migraciones de schema |

---

## Módulos

| Módulo | Descripción |
|--------|-------------|
| [Widget](modulos/widget/README.md) | MainShell, HeaderBar, InProgressCompact |
| [TaskBoard](modulos/taskboard/README.md) | Kanban, tareas, WIP |
| [TaskBoard API](modulos/taskboard/API.md) | Métodos de BoardService |
| [Reports](modulos/reports/README.md) | Reportes, exportación Excel |
| [Maestros](modulos/masters/README.md) | Tribu, Canal, Categoría, Columnas Kanban |
| [Alerts](modulos/alerts/README.md) | Alertas (en desarrollo) |
