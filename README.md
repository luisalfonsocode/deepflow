# DeepFlow

Widget de escritorio para captura sin fricción y gestión de límites WIP. Elimina la fricción en la captura de tareas y aplica límites de trabajo en curso.

---

## Inicio rápido

```bash
pip install -r requirements.txt
python main.py
```

**Tests:** `pytest tests/ -v`

---

## Características

| Función | Descripción |
|---------|-------------|
| **Kanban** | 5 columnas: Backlog, To Do, In Progress, Done, Detenido |
| **Límites WIP** | To Do e In Progress: máx. 3. Detenido: máx. 5 |
| **Crear tareas** | Botón + o **Ctrl+V** (pega del portapapeles) |
| **Mover** | Arrastrar y soltar o botones ◀ ▶ |
| **Alerta** | Cabecera en rojo cuando se supera el límite WIP |
| **Reportes** | Exportación Excel, gráficos de tiempo por categoría |

Límites configurables en **Maestros → Columnas Kanban**.

**Atajos:** Ctrl+V (crear con portapapeles), Enter (confirmar), Escape (cancelar).

**Exportar a CSV:** `python export_transitions.py`

---

## Estructura

```
deepflow/
├── main.py              # Punto de entrada
├── domain/              # Entidades, reglas de negocio
├── application/         # Casos de uso (BoardService)
├── infrastructure/      # ZODB, Excel, clipboard
├── presentation/        # UI PyQt6
├── data/db/             # Base de datos (ZODB)
└── docs/                # Documentación
```

Ver [docs/codigo/estructura.md](docs/codigo/estructura.md) para el mapa completo.

---

## Documentación

→ **[docs/README.md](docs/README.md)** – Índice completo

### Accesos directos

| Para… | Ver |
|-------|-----|
| **Usuarios:** instalar o actualizar ejecutable Windows | [Guía de instalación](docs/instalacion.md) |
| **Mantenedores:** configurar pipeline (GitHub Actions) | [Tutorial CI/CD](docs/tutorial-github-actions.md) |
| **Desarrolladores:** compilar desde fuente | [Build y despliegue](docs/despliegue-updates.md) |
| **Código:** arquitectura y módulos | [docs/codigo](docs/codigo/README.md) |

---

## Compatibilidad

| Plataforma | Estado |
|------------|--------|
| **Windows** | Objetivo principal |
| **macOS** | Compatible |
| **Linux** | Compatible con PyQt6 |

---

## Principios del proyecto

1. **Finalizar sobre empezar** – Priorizar completar tareas.
2. **Simplicidad** – Solo el nombre de la tarea es obligatorio.
3. **Límite WIP inviolable** – Respetar los límites en cualquier cambio.
