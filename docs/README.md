# DeepFlow – Índice de Documentación

Documentación ordenada por tipo: **análisis** (decisiones de diseño) y **código** (referencia técnica).

---

## 1. Análisis y decisiones de diseño

Documentos que analizan opciones, validan la arquitectura o justifican decisiones técnicas.

| Documento | Descripción |
|----------|-------------|
| [base-datos-embebida](analisis/base-datos-embebida.md) | Análisis ZODB vs SQLite, TinyDB, LMDB, JSON para persistencia local |
| [validacion-crecimiento](analisis/validacion-crecimiento.md) | Validación: la estructura soporta TaskBoard, Reporters y Alerts |

---

## 2. Documentación de código

Referencia técnica: estructura, arquitectura, guías de desarrollo y APIs de módulos.

### Estructura y arquitectura

| Documento | Descripción |
|----------|-------------|
| [estructura](codigo/estructura.md) | Mapa completo de archivos y directorios |
| [arquitectura-clean](codigo/arquitectura-clean.md) | Guía Clean Architecture (domain, application, infrastructure, presentation) |
| [arquitectura-tecnica](codigo/arquitectura-tecnica.md) | Flujo de datos, puertos, adaptadores |
| [desarrollo](codigo/desarrollo.md) | Principios SOLID, cómo añadir columnas, campos, exportadores |
| [infraestructura](codigo/infraestructura.md) | Persistencia ZODB, estilos QSS |
| [versionado-base-datos](codigo/versionado-base-datos.md) | Migraciones de schema |

### Módulos

| Módulo | Descripción |
|--------|-------------|
| [Widget](codigo/modulos/widget/README.md) | MainShell, HeaderBar, InProgressCompact |
| [TaskBoard](codigo/modulos/taskboard/README.md) | Kanban, tareas, WIP |
| [TaskBoard API](codigo/modulos/taskboard/API.md) | Métodos de BoardService, tests |
| [Reports](codigo/modulos/reports/README.md) | Reportes, exportación Excel |
| [Alerts](codigo/modulos/alerts/README.md) | Alertas (en desarrollo) |

---

## 3. Datos (fuera de docs/)

- **[data/DIAGRAMA_BASE_DATOS.md](../data/DIAGRAMA_BASE_DATOS.md)** – Esquema y estructura de la base de datos
