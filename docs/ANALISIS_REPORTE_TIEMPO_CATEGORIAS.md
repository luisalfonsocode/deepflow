# Análisis: ¿Por qué solo aparecen 2 categorías en el reporte de tiempo?

## Flujo de datos

1. **`time_per_task`** = tareas con tiempo (in_progress o detenido) **dentro del periodo**.
   - Proviene de `compute_time_per_task_in_period(transitions, from_date, to_date)`.
   - Solo incluye tareas que pasaron tiempo en `in_progress` o `detenido` en esas fechas.

2. **`detail`** = lista de esas tareas con su categoría (de `task.categoria`).

3. **`cat_totals`** = agregado por categoría a partir de `detail`.

4. **Maestro categoría** = `board_data["categoria"]` (lista de `{label: "X"}`).
   - Se añaden al resumen con 0% si no tienen tiempo en el periodo.

5. **"(sin categoría)"** = si falta, se añade con 0%.

## Posibles motivos de ver solo 2 categorías

### A) Solo 2 tareas con tiempo en el periodo
- Si en el rango elegido (semana, mes, etc.) solo 2 tareas tienen tiempo en `in_progress` / `detenido`, y tienen categorías distintas, aparecerán solo esas 2.

### B) Todas las tareas con tiempo comparten 2 categorías
- Varias tareas con tiempo, pero repartidas solo en 2 categorías.

### C) Maestro categoría vacío o poco usado
- `CATEGORIA_OPTIONS` por defecto está vacío.
- Las categorías se amplían desde Maestros en la app.
- Si el maestro está vacío o no coincide con las etiquetas de las tareas, no se añaden más categorías con 0%.

### D) El gráfico circular solo dibuja sectores con tiempo
- El pie dibuja solo sectores con `pct > 0`.
- Las categorías con 0% sí aparecen en la **tabla** debajo, pero no en el **gráfico**.
- Si quieres ver todas las categorías (incluidas las de 0%), hay que mirar la tabla, no solo el pie.

### E) Acceso a `board_data` por columnas
- Las tareas vienen de `board_data.get(col, [])` para cada columna.
- `BoardService.data` deja las columnas accesibles al top level.
- Si la estructura no fuera la esperada, no se aplicarían bien las categorías.

## Cómo diagnosticar

Ejecuta el script de análisis **con la app cerrada**:

```bash
# Cierra la app (Ctrl+C si está en terminal) y luego:
python3 scripts/analizar_reporte_tiempo.py
```

El script mostrará:

- Nº de tareas por columna
- Nº de transiciones
- Categorías en el maestro
- Categorías usadas en tareas
- Tareas con tiempo en el periodo y sus categorías
- Qué categorías aparecerían en el reporte

## Comprobar si el comportamiento es correcto

- Si solo 2 tareas tienen tiempo en el periodo y tienen 2 categorías distintas → **es correcto** que solo aparezcan 2 categorías en el pie.
- Si esperas más categorías, revisa:
  1. Que haya más tareas con tiempo en ese rango.
  2. Que esas tareas tengan categorías distintas.
  3. Que las categorías del maestro estén definidas (Maestros → Categoría).
  4. Que mires también la tabla debajo del pie (muestra todas las categorías, incluidas las de 0%).
