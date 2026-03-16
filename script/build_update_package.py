#!/usr/bin/env python3
"""
Genera un paquete de actualización (ZIP) con solo los archivos a reemplazar.
Excluye data/ para preservar la base de datos del usuario.

Uso:
  python script/build_update_package.py              # Requiere dist/ existente
  python script/build_dist.py && python script/build_update_package.py  # Build + update

El ZIP resultante se extrae sobre la instalación existente. NUNCA incluye data/.
"""

import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
APP_NAME = "DeepFlow"
# En macOS preferir .app (lo que el usuario copia); en Windows la carpeta
APP_FOLDER_NAMES = [f"{APP_NAME}.app", APP_NAME] if sys.platform == "darwin" else [APP_NAME]


def _should_exclude(rel_path: Path) -> bool:
    """True si el archivo no debe incluirse en el update (preserva datos de usuario)."""
    s = str(rel_path).replace("\\", "/")
    if "config/yaml/deepflow.yaml" in s and not s.endswith(".example"):
        return True
    # data/ y archivos ZODB
    if "/data/" in s or s.startswith("data/"):
        return True
    if any(ext in s for ext in [".fs", ".fs.index", ".fs.lock", ".fs.tmp"]):
        return True
    return False


def find_app_folder() -> Path | None:
    """Encuentra la carpeta de la app en dist (DeepFlow o DeepFlow.app)."""
    for name in APP_FOLDER_NAMES:
        candidate = DIST_DIR / name
        if candidate.exists():
            return candidate
    return None


def create_update_zip(app_folder: Path, out_zip: Path) -> None:
    """Crea ZIP con todo excepto data/ y config de usuario."""
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in app_folder.rglob("*"):
            if f.is_file():
                try:
                    rel = f.relative_to(app_folder)
                except ValueError:
                    continue
                if _should_exclude(rel):
                    continue
                # Incluir nombre de la app para que al extraer quede DeepFlow.app/ o DeepFlow/
                arcname = f"{app_folder.name}/{rel}"
                zf.write(f, arcname)
    print(f"Paquete de actualización: {out_zip}")


def main() -> None:
    app_folder = find_app_folder()
    if not app_folder:
        print("Error: no existe dist/DeepFlow o dist/DeepFlow.app")
        print("Ejecuta antes: python script/build_dist.py")
        sys.exit(1)

    out_zip = DIST_DIR / f"{APP_NAME}-update.zip"
    create_update_zip(app_folder, out_zip)

    # Comando para aplicar el update (imprimir siempre para no olvidar)
    if sys.platform == "darwin":
        ejemplo_destino = "/Applications"
    else:
        ejemplo_destino = "C:\\Apps"
    unzip_cmd = f"unzip -o {out_zip} -d {ejemplo_destino}"

    print("\n--- Aplicar update ---")
    print("  1. Cierra DeepFlow si está abierto")
    print("  2. Ejecuta (ajusta la ruta destino si hace falta):")
    print(f"     {unzip_cmd}")
    print("  data/ NO se toca; tus tareas se conservan")


if __name__ == "__main__":
    main()
