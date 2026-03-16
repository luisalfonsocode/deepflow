# Despliegue y actualizaciones

## Ver versión del schema de la BD

Para saber qué versión tiene tu base de datos (útil antes de actualizar):

```bash
python script/check_schema_version.py
```

O con ruta explícita a la carpeta `data/db`:

```bash
python script/check_schema_version.py /ruta/a/DeepFlow/data/db
```

Si está en v1, v2, etc., al abrir la app nueva se migrará automáticamente a v6.

## Estrategia de datos

La base de datos (ZODB) vive en `data/db/deepflow_db.fs`, relativo al ejecutable. **Nunca** se incluye en paquetes de actualización.

| Qué | Ubicación |
|-----|-----------|
| **Código/recursos** | `DeepFlow.exe`, `_internal/`, `config/`, `styles.qss` |
| **Datos de usuario** | `data/db/deepflow_db.fs` (no versionar, no incluir en updates) |
| **Config opcional** | `config/yaml/deepflow.yaml` (el usuario puede personalizar) |

## Instalación inicial

```bash
python script/build_dist.py
```

- **macOS**: Copiar `dist/DeepFlow.app`
- **Windows**: Copiar toda la carpeta `dist/DeepFlow`

## Actualizaciones

### 1. Generar paquete de actualización

```bash
python script/build_dist.py --update
```

O si `dist/` ya existe:

```bash
python script/build_update_package.py
```

Se crea `dist/DeepFlow-update.zip` con todo **excepto**:
- `data/` (base de datos)
- `config/yaml/deepflow.yaml` (configuración del usuario)

### 2. Aplicar la actualización

1. **Cierra DeepFlow** si está abierto.
2. Descomprime `DeepFlow-update.zip` **sobre** la carpeta de instalación.
3. La carpeta `data/` no se toca; tus tareas se conservan.

En Windows, si DeepFlow está en `C:\Apps\DeepFlow\`:
- Abre el ZIP y extrae su contenido **dentro** de `C:\Apps\DeepFlow\`
- Acepta sobrescribir los archivos existentes (exe, _internal, etc.)
- `data/` no está en el ZIP, por tanto no se modifica

En macOS, si usas `DeepFlow.app`:
- El ZIP contiene la estructura del `.app`
- Reemplaza el `.app` antiguo por el nuevo, **o** extrae el contenido del ZIP dentro del `.app` existente (clic derecho → Mostrar contenido del paquete) para preservar `data` si está dentro.

### Recomendación para macOS

Para que las actualizaciones sean más seguras, conviene mover los datos fuera del bundle:

1. Edita `config/yaml/deepflow.yaml` dentro del `.app`
2. Cambia `data_dir` a una ruta fija, por ejemplo:
   ```yaml
   data_dir: ~/Library/Application Support/DeepFlow
   ```
3. Copia `data/` a esa ruta
4. A partir de entonces, al reemplazar el `.app` completo, los datos no se pierden
