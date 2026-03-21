#!/usr/bin/env python3
"""
Genera icon.ico e icon.icns para el build.
Ejecutar: pip install Pillow && python script/generate_icons.py

- icon.png: 1024x1024 (base alta resolución para Retina/HiDPI)
- icon.ico: Windows (múltiples tamaños incl. 512)
- icon.icns: macOS (iconutil con todos los tamaños para Retina)
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS = PROJECT_ROOT / "assets"
ICONSET = ASSETS / "icon.iconset"
ICON_SIZE = 1024  # Alta resolución para Retina/HiDPI nítido


def create_icon_png() -> Path:
    """Crea icon.png en alta resolución (1024x1024) para Retina/HiDPI."""
    png_path = ASSETS / "icon.png"
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("Instala Pillow: pip install Pillow")

    need_create = True
    if png_path.exists():
        with Image.open(png_path) as img:
            if img.size[0] >= ICON_SIZE and img.size[1] >= ICON_SIZE:
                need_create = False

    if need_create:
        img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        r_center = ICON_SIZE // 2
        # Círculo teal #0d9488 (13, 148, 136)
        margin = int(ICON_SIZE * 0.05)
        draw.ellipse(
            [margin, margin, ICON_SIZE - margin, ICON_SIZE - margin],
            fill=(13, 148, 136, 255),
        )
        img.save(png_path, "PNG")
        print(f"Actualizado {png_path} ({ICON_SIZE}x{ICON_SIZE})")
    return png_path


def create_ico(png_path: Path) -> Path:
    """Convierte PNG a ICO (Windows) con múltiples tamaños para HiDPI."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Instala Pillow: pip install Pillow")
    ico_path = ASSETS / "icon.ico"
    img = Image.open(png_path).convert("RGBA")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256), (512, 512)]
    img.save(ico_path, format="ICO", sizes=sizes)
    print(f"Creado {ico_path}")
    return ico_path


def create_icns_iconutil(png_path: Path) -> Path | None:
    """Crea ICNS usando iconutil (macOS) - nítido en Retina."""
    if sys.platform != "darwin":
        print("icon.icns: omitido (solo se genera en macOS)")
        return None

    try:
        from PIL import Image
    except ImportError:
        return None

    ICONSET.mkdir(parents=True, exist_ok=True)
    img = Image.open(png_path).convert("RGBA")

    # Archivos requeridos por iconutil (nombre -> tamaño en píxeles)
    iconset_files = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]
    for name, size in iconset_files:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(ICONSET / name, "PNG")

    icns_path = ASSETS / "icon.icns"
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET), "-o", str(icns_path)],
        capture_output=True,
    )
    for f in ICONSET.glob("*.png"):
        f.unlink()
    ICONSET.rmdir()
    if result.returncode != 0:
        print(f"iconutil: {result.stderr.decode()}")
        return None
    print(f"Creado {icns_path} (Retina)")
    return icns_path


def create_icns_pillow(png_path: Path) -> Path | None:
    """Fallback: Pillow ICNS (menos tamaños que iconutil)."""
    icns_path = ASSETS / "icon.icns"
    if sys.platform != "darwin":
        return None
    try:
        from PIL import Image

        img = Image.open(png_path).convert("RGBA")
        if img.size[0] < 512:
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
        img.save(icns_path, format="ICNS")
        print(f"Creado {icns_path} (Pillow fallback)")
        return icns_path
    except Exception as e:
        print(f"icon.icns Pillow: {e}")
        return None


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    png = create_icon_png()
    create_ico(png)
    if not create_icns_iconutil(png):
        create_icns_pillow(png)
    print("Iconos listos para el build.")


if __name__ == "__main__":
    main()
