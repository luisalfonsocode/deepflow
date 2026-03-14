# Directorio `data/`

Contenido del directorio de datos de DeepFlow.

## Estructura

```
data/
├── db/                    # Base de datos (archivos de runtime)
│   ├── deepflow_db.fs     # ZODB – archivo principal (generado)
│   ├── deepflow_db.fs.index
│   ├── deepflow_db.fs.lock
│   ├── deepflow_db.fs.tmp
│   └── deepflow_db.json   # Legacy JSON (migrado a .fs si existe)
├── DIAGRAMA_BASE_DATOS.md   # Documentación: esquema y estructura
└── README.md                # Este archivo
```

## Base de datos (`db/`)

Archivos de la base de datos embebida ZODB:

| Archivo            | Descripción                                           |
|--------------------|-------------------------------------------------------|
| `deepflow_db.fs`   | Archivo principal – datos persistentes               |
| `.fs.index`        | Índice – generado automáticamente por ZODB          |
| `.fs.lock`         | Bloqueo – creado durante la ejecución                |
| `.fs.tmp`          | Temporal – usado durante transacciones              |

Estos archivos están en `.gitignore` (no se versionan). El directorio `db/` se preserva gracias a `.gitkeep`.

## Documentación

- **DIAGRAMA_BASE_DATOS.md**: diagrama del esquema (container deepflow, Task, Subtask, Transitions).
- **Análisis de BD embebida**: ver [docs/analisis/base-datos-embebida.md](../docs/analisis/base-datos-embebida.md) para la justificación de ZODB frente a SQLite, TinyDB, etc.

## Migraciones

Si existen `monoflow_db.fs` o `monoflow_db.json` (legacy), la aplicación los migra automáticamente a `db/deepflow_db.fs` en el primer arranque.
