# Guía de versionado de base de datos (ZODB)

Esta guía explica cómo versionar y migrar la base de datos cuando se introducen cambios en el schema o la estructura de datos.

---

## Conceptos

### Schema version

Cada versión del schema se identifica con un número entero (`1`, `2`, `3`...). La versión actual se guarda en el root de ZODB como `schema_version`.

### Migración

Cuando el schema cambia (nuevos campos, tablas, o cambios de estructura), se escribe lógica de migración que transforma datos antiguos al nuevo formato.

---

## Dónde está el código

| Archivo | Responsabilidad |
|---------|-----------------|
| `infrastructure/persistence/schema_versions.py` | Define `CURRENT_SCHEMA_VERSION` (10) y `migrate_to_latest()` |
| `infrastructure/persistence/zodb_repository.py` | Lee `schema_version` del root y aplica migraciones |

### Versiones de schema actuales

| Versión | Cambio |
|---------|--------|
| 1 | Columnas + transitions |
| 2 | Campo `ticket` en tareas |
| 3 | tribe_and_squad, requester, reporting_channel |
| 4 | Container deepflow, maestros, columns dict |
| 5 | Maestros persistentes (tribu_squad, solicitante, canal_reporte) |
| 6 | Maestro categoria |
| 7 | Backfill finished_at en tareas en Done |
| 8 | Maestro kanban_columns (wip_limit configurable por columna) |
| 9 | blocked_periods en tareas (períodos bloqueados editables) |
| 10 | order en subtareas (asignar 0,1,2,... si no existe; ordenar lista) |

---

## Cómo versionar un cambio nuevo

### Paso 1: Incrementar la versión

En `infrastructure/persistence/schema_versions.py`:

```python
CURRENT_SCHEMA_VERSION = 2  # Era 1, ahora 2
```

### Paso 2: Añadir la migración

En `migrate_to_latest()`, añadir la lógica para migrar desde la versión anterior:

```python
def migrate_to_latest(data: dict[str, Any], from_version: int) -> dict[str, Any]:
    result = data
    if from_version < 2:
        result = _migrate_v1_to_v2(result)
    # if from_version < 3:
    #     result = _migrate_v2_to_v3(result)
    return result


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Ejemplo: añadir campo 'tags' a todas las tareas."""
    from domain.taskboard.masters import KANBAN_COLUMNS

    cols = data.get("columns") or {kc["key"]: data.get(kc["key"], []) for kc in KANBAN_COLUMNS}
    for col, tasks in cols.items():
        for task in tasks:
            if isinstance(task, dict) and "tags" not in task:
                task["tags"] = []
    return data
```

### Paso 3: Probar

1. Crear una base de datos con schema v1 (o usar una existente).
2. Arrancar la app: al leer, se aplicará la migración.
3. Hacer un cambio (crear/mover tarea) y guardar: se persistirá con v2.
4. Verificar que los datos se ven correctamente.

---

## Reglas importantes

### 1. No modificar migraciones ya aplicadas

Si ya hay datos en producción con v2, **no cambies** `_migrate_v1_to_v2`. Añade una nueva `_migrate_v2_to_v3` para el siguiente cambio.

### 2. Migraciones idempotentes

Cada migración debe poder ejecutarse varias veces sin efectos secundarios. Usa `setdefault`, comprueba `if "campo" not in task`, etc.

### 3. Orden de migraciones

Las migraciones se aplican en secuencia: v1→v2, v2→v3, etc. `migrate_to_latest` debe cubrir todos los saltos desde `from_version` hasta `CURRENT_SCHEMA_VERSION`.

### 4. Actualizar schema_version al guardar

En `infrastructure/persistence/zodb_repository.save_board_data()`, se guarda siempre `root["schema_version"] = CURRENT_SCHEMA_VERSION`. No hace falta tocarlo al añadir migraciones.

---

## Ejemplo completo: añadir prioridad a tareas

**Cambio**: Cada tarea tendrá un campo `priority` (int, 0 por defecto).

```python
# schema_versions.py

CURRENT_SCHEMA_VERSION = 2

def migrate_to_latest(data: dict[str, Any], from_version: int) -> dict[str, Any]:
    result = data
    if from_version < 2:
        result = _migrate_v1_to_v2(result)
    return result


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Añade priority=0 a tareas que no lo tienen."""
    from domain.taskboard.masters import KANBAN_COLUMNS

    cols = data.get("columns") or {kc["key"]: data.get(kc["key"], []) for kc in KANBAN_COLUMNS}
    for col, tasks in cols.items():
        for task in tasks:
            if isinstance(task, dict):
                task.setdefault("priority", 0)
    return data
```

---

## Flujo en runtime

```
App arranca
    ↓
ZODBBoardRepository.get_board_data()
    ↓
_ensure_schema(root)
    ↓
schema_version = root.get("schema_version", 1)
    ↓
Si schema_version < CURRENT_SCHEMA_VERSION:
    data = migrate_to_latest(data, schema_version)
    ↓
Retorna data (en memoria; no se persiste la migración hasta el próximo save)
    ↓
Usuario hace un cambio → BoardService.persist()
    ↓
save_board_data() guarda con schema_version = CURRENT_SCHEMA_VERSION
```

---

## Checklist para un nuevo cambio de schema

- [ ] Incrementar `CURRENT_SCHEMA_VERSION` en `schema_versions.py`
- [ ] Añadir `if from_version < N: result = _migrate_vNminus1_to_vN(result)` en `migrate_to_latest`
- [ ] Implementar `_migrate_vNminus1_to_vN` con la lógica de transformación
- [ ] Actualizar el código que usa los datos (BoardService, vistas, etc.) para el nuevo campo/estructura
- [ ] Probar con una base de datos existente (v1) que se migre correctamente
- [ ] Documentar el cambio en el changelog o en este archivo
