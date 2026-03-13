# Scripts de pipeline y despliegue

Scripts para instalar cambios y mantener el proyecto. Ejecutar siempre desde la **raíz del proyecto**.

---

## Cómo se instalan los cambios

Cuando despliegas una nueva versión (código actualizado), sigue este orden:

```
1. Actualizar código (git pull, copiar archivos, etc.)
2. Instalar dependencias
3. Ejecutar tests (opcional en producción)
4. Arrancar la aplicación
```

### Orden de ejecución

| Paso | Comando | Qué hace |
|------|---------|----------|
| 1 | `pip install -r requirements.txt` | Instala/actualiza PyQt6, openpyxl, etc. |
| 2 | `python -m scripts.run_tests` | Verifica que todo funciona (recomendado en CI) |
| 3 | `python main.py` | Inicia la aplicación |

### Ejemplo completo

```bash
cd /ruta/al/proyecto/deepflow

# 1. Dependencias
pip install -r requirements.txt

# 2. Tests (recomendado antes de producción)
python -m scripts.run_tests

# 3. Arrancar
python main.py
```

---

## Scripts disponibles

| Script | Descripción | Cuándo usarlo |
|--------|-------------|---------------|
| `export_transitions` | Exporta tareas a CSV (started_at, finished_at) | Mantenimiento, reportes |
| `run_tests` | Ejecuta pytest | CI, antes de desplegar |

### Uso

```bash
python -m scripts.export_transitions -o reporte.csv
python -m scripts.run_tests
```

---

## Persistencia

Los datos se guardan en **ZODB** (`monoflow_db.fs`). Si existe `monoflow_db.json` y no existe `.fs`, se migra automáticamente al primer arranque.

### Versionado de schema

Ver **[docs/VERSIONADO_BASE_DATOS.md](../docs/VERSIONADO_BASE_DATOS.md)** para la guía completa.

---

## Resolución de problemas

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError` al ejecutar scripts | Ejecutar desde la raíz: `cd /ruta/deepflow` y luego `python -m scripts.xxx` |
| La app no ve los datos | Verificar que existe `monoflow_db.fs` (o `monoflow_db.json` para migración automática) |
| Tests fallan | `pip install -r requirements.txt` y `python -m scripts.run_tests` |
