# MonoFlow – Índice de Documentación

Documentación ordenada según la definición de módulos.

---

## 1. Módulos

### 1.1 Widget
Contenedor principal con la lista de funcionalidades.

- **[Modulo Widget](modulos/widget/README.md)** – Shell, registro de módulos, flujo

### 1.2 TaskBoard
Tablero Kanban: creación, modificación, eliminación y consulta de tareas.

- **[Modulo TaskBoard](modulos/taskboard/README.md)** – Descripción, funcionalidades, ubicación
- **[API TaskBoard](modulos/taskboard/API.md)** – Métodos, parámetros, tests

### 1.3 Reports
Reportes, dashboards y métricas (en desarrollo).

- **[Modulo Reports](modulos/reports/README.md)** – Estado, ideas

### 1.4 Alerts
Notificaciones y alertas (en desarrollo).

- **[Modulo Alerts](modulos/alerts/README.md)** – Estado, ideas

---

## 2. Arquitectura y desarrollo

- **[Arquitectura técnica](arquitectura.md)** – Flujo de datos, puertos, adaptadores, validaciones WIP
- **[Guía de desarrollo](DESARROLLO.md)** – SOLID, separación UI/lógica, estructura

---

## 3. Infraestructura

- **[Persistencia](infraestructura.md#persistencia)** – ZODB, exportación CSV
- **[Estilos](infraestructura.md#estilos)** – QSS, selectores, personalización
- **[Versionado de base de datos](VERSIONADO_BASE_DATOS.md)** – Cómo migrar el schema cuando hay cambios

---

## 4. Crecimiento

- **[Validación para crecimiento](validacion-crecimiento.md)** – Soporte para Reporters y Alerts
