# Configuración DeepFlow

Todo desde **archivo de configuración** (`deepflow.yaml`). Sin variables de entorno.

## Estructura

```
config/
├── __init__.py           # Exporta settings
├── base.py               # Constantes por defecto
├── loader.py             # Carga YAML
├── settings.py           # Objeto Settings unificado
├── yaml/                 # Archivos de configuración (distinto de .py)
│   ├── deepflow.yaml     # Config activa
│   └── deepflow.yaml.example
└── README.md
```

## Uso

### Local

Editar `config/yaml/deepflow.yaml`:

```yaml
environment: local
data_dir: ./data
```

### Producción

```yaml
environment: production
data_dir: /var/lib/deepflow
# o ruta explícita:
# db_path: /var/lib/deepflow/deepflow_db.fs
```

## Opciones

| Clave | Uso | Default |
|-------|-----|---------|
| `environment` | `local` \| `production` | `local` |
| `data_dir` | Directorio base (data/) | `./data` |
| `db_path` | Ruta ZODB explícita (opcional) | (resuelta) |

## En código

```python
from config import settings

settings.zodb_path      # Ruta BD efectiva
settings.data_dir       # ./data o configurado
settings.is_production  # bool
```
