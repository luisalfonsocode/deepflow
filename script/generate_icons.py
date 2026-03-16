#!/usr/bin/env python3
"""
Genera icon.ico e icon.icns para el build.
Ejecutar una vez: pip install Pillow && python script/generate_icons.py

- icon.ico: Windows (obligatorio)
- icon.icns: macOS (opcional; se puede usar icon.png si PyInstaller tiene Pillow)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS = PROJECT_ROOT / "assets"


def create_icon_png() -> Path:
    """Crea icon.png mínimo (gradiente azul/teal) si no existe."""
    png_path = ASSETS / "icon.png"
    if png_path.exists():
        return png_path
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("Instala Pillow: pip install Pillow")
    # 256x256, gradiente azul
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Círculo con gradiente simulado (azul #1e3a5f a teal #0d9488)
    for i in range(128, 0, -2):
        alpha = 255 - (i * 2)
        r = int(30 + (13 - 30) * (1 - i/128))
        g = int(58 + (148 - 58) * (1 - i/128))
        b = int(95 + (136 - 95) * (1 - i/128))
        draw.ellipse([128-i, 128-i, 128+i, 128+i], fill=(r, g, b, min(255, alpha)))
    img.save(png_path)
    print(f"Creado {png_path}")
    return png_path


def create_ico(png_path: Path) -> Path:
    """Convierte PNG a ICO (Windows)."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Instala Pillow: pip install Pillow")
    ico_path = ASSETS / "icon.ico"
    img = Image.open(png_path).convert("RGBA")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=sizes)
    print(f"Creado {ico_path}")
    return ico_path


def create_icns(png_path: Path) -> Path | None:
    """Convierte PNG a ICNS (macOS). Solo en macOS."""
    icns_path = ASSETS / "icon.icns"
    if sys.platform != "darwin":
        print("icon.icns: omitido (solo se genera en macOS)")
        return None
    try:
        from PIL import Image
    except ImportError:
        return None
    # Pillow puede escribir icns solo en macOS
    try:
        img = Image.open(png_path).convert("RGBA")
        img.save(icns_path, format="ICNS")
        print(f"Creado {icns_path}")
        return icns_path
    except Exception as e:
        print(f"icon.icns: no generado ({e}). Usa icon.png en el build.")
        return None


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    png = create_icon_png()
    create_ico(png)
    create_icns(png)
    print("Iconos listos para el build.")


if __name__ == "__main__":
    main()
