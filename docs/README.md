# DeepFlow – Documentación

Índice central de la documentación. Todo está en `docs/`.

---

## Estructura

```
docs/
├── README.md                    ← Estás aquí
├── instalacion.md               Usuarios: instalar y actualizar (Windows)
├── tutorial-github-actions.md   Mantenedores: pipeline, ramas, artefactos
├── despliegue-updates.md        Desarrolladores: compilar desde fuente
├── analisis-reporte-tiempo.md   Análisis: viabilidad reporte de tiempo
├── analisis-reporte-tiempo-categorias.md
├── funcionalidades-habilitables.md
└── codigo/                      Referencia técnica del código
    ├── estructura.md
    ├── arquitectura-clean.md
    ├── arquitectura-tecnica.md
    ├── desarrollo.md
    ├── infraestructura.md
    ├── versionado-base-datos.md
    └── modulos/
```

---

## Inicio rápido

| Necesito… | Documento |
|-----------|-----------|
| **Instalar DeepFlow** (ejecutable Windows) | [Guía de instalación](instalacion.md) |
| **Actualizar sin perder datos** | [Guía de instalación → Actualizar](instalacion.md#actualizar-conservar-tus-datos) |
| **Configurar el pipeline** (GitHub Actions) | [Tutorial GitHub Actions](tutorial-github-actions.md) |
| **Compilar desde código fuente** | [Build y despliegue](despliegue-updates.md) |

---

## Código

### Arquitectura y estructura

| Documento | Descripción |
|-----------|-------------|
| [Estructura](codigo/estructura.md) | Mapa de archivos y directorios |
| [Arquitectura Clean](codigo/arquitectura-clean.md) | Capas: domain, application, infrastructure, presentation |
| [Arquitectura técnica](codigo/arquitectura-tecnica.md) | Flujo de datos, puertos, adaptadores |
| [Desarrollo](codigo/desarrollo.md) | SOLID, añadir columnas/campos/exportadores |
| [Infraestructura](codigo/infraestructura.md) | Persistencia ZODB, estilos QSS |
| [Versionado BD](codigo/versionado-base-datos.md) | Migraciones de schema |

### Módulos

| Módulo | Descripción |
|--------|-------------|
| [Widget](codigo/modulos/widget/README.md) | MainShell, HeaderBar, InProgressCompact |
| [TaskBoard](codigo/modulos/taskboard/README.md) | Kanban, tareas, WIP |
| [TaskBoard API](codigo/modulos/taskboard/API.md) | Métodos de BoardService |
| [Reports](codigo/modulos/reports/README.md) | Reportes, exportación Excel |
| [Maestros](codigo/modulos/masters/README.md) | Tribu, Canal, Categoría, Columnas Kanban |
| [Alerts](codigo/modulos/alerts/README.md) | Alertas (en desarrollo) |

---

## CI/CD y despliegue

| Documento | Audiencia | Descripción |
|-----------|-----------|-------------|
| [Tutorial GitHub Actions](tutorial-github-actions.md) | Mantenedores | Protección de ramas, workflow, artefactos |
| [Instalación (Windows)](instalacion.md) | Usuarios finales | Instalar y actualizar desde artefactos |
| [Build y despliegue](despliegue-updates.md) | Desarrolladores | Compilar desde fuente, schema BD |

---

## Análisis y decisiones

| Documento | Descripción |
|-----------|-------------|
| [Reporte de tiempo](analisis-reporte-tiempo.md) | Viabilidad de reporte semanal/mensual |
| [Reporte de tiempo (categorías)](analisis-reporte-tiempo-categorias.md) | Por qué aparecen solo N categorías |
| [Funcionalidades habilitables](funcionalidades-habilitables.md) | Módulos deshabilitados y placeholders |

---

## Datos

- **[data/DIAGRAMA_BASE_DATOS.md](../data/DIAGRAMA_BASE_DATOS.md)** – Esquema y estructura de la base de datos
