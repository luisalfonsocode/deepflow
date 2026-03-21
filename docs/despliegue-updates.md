# Build y despliegue

Guía para **desarrolladores** que compilan DeepFlow desde el código fuente. Para instalar o actualizar el ejecutable descargando artefactos, ver [Guía de instalación](instalacion.md).

---

## 1. Compilar el ejecutable

### Requisitos

- Python 3.10+
- `pip install -r requirements.txt Pillow pyinstaller`

### Comandos

```bash
python script/generate_icons.py   # Genera iconos (opcional si ya existen)
python script/build_dist.py
```

### Salida

| Plataforma | Salida |
|------------|--------|
| **Windows** | `dist/DeepFlow/` con `DeepFlow.exe` |
| **macOS** | `dist/DeepFlow.app` |
| **Linux** | `dist/DeepFlow/` con binario |

---

## 2. Paquete de actualización

Para distribuir actualizaciones sin incluir los datos del usuario:

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

**Aplicar la actualización:** Ver [Guía de instalación → Actualizar](instalacion.md#actualizar-conservar-tus-datos).

---

## 3. Estrategia de datos

| Qué | Ubicación | En updates |
|-----|-----------|------------|
| Código/recursos | `DeepFlow.exe`, `_internal/`, `config/`, `styles.qss` | ✓ |
| Datos de usuario | `data/db/deepflow_db.fs` | ✗ |
| Config opcional | `config/yaml/deepflow.yaml` | ✗ |

La base de datos (ZODB) vive en `data/db/deepflow_db.fs`, relativo al ejecutable. **Nunca** se incluye en paquetes de actualización.

---

## 4. Versión del schema de la BD

Antes de actualizar, para ver la versión del schema:

```bash
python script/check_schema_version.py
```

O con ruta explícita:

```bash
python script/check_schema_version.py /ruta/a/DeepFlow/data/db
```

Si está en v1, v2, etc., al abrir la app nueva se migrará automáticamente.

---

## 5. macOS: datos fuera del bundle

Para actualizaciones más seguras en Mac, conviene mover los datos fuera del `.app`:

1. Edita `config/yaml/deepflow.yaml` dentro del `.app`
2. Cambia `data_dir` a una ruta fija:
   ```yaml
   data_dir: ~/Library/Application Support/DeepFlow
   ```
3. Copia `data/` a esa ruta
4. A partir de entonces, al reemplazar el `.app` completo, los datos no se pierden
