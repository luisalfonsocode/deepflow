# Iconos de la aplicación

- **icon.ico**: Windows (ejecutable y barra de tareas)
- **icon.icns**: macOS (.app)
- **icon.png**: Origen / fallback

## Regenerar iconos

```bash
pip install Pillow
python script/generate_icons.py
```

Esto crea `icon.png`, `icon.ico` y `icon.icns` (en macOS).
