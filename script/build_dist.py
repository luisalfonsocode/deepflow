#!/usr/bin/env python3
"""
Script de build para DeepFlow.
Genera el ejecutable y la carpeta dist con archivos necesarios para producción.
La app puede ejecutarse en otro directorio; la BDD se crea en ./data junto al exe.

Uso:
  python script/build_dist.py           # Build normal (sin consola)
  python script/build_dist.py --debug   # Build con consola visible (para ver errores)
  python script/build_dist.py --update # Build + paquete de actualización (ZIP sin data/)
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Raíz del proyecto (script/ está dentro)
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
DIST_APP_NAME = "DeepFlow"
DIST_APP_NAME_DEBUG = "DeepFlow-debug"

# PyInstaller --add-data: src:dest (en Windows usa ;)
ADD_DATA_SEP = ";" if sys.platform == "win32" else ":"


def _app_folder(app_name: str) -> Path:
    """Ruta de la carpeta/paquete de salida. En Mac es .app, en Windows/Linux carpeta."""
    if sys.platform == "darwin":
        return DIST_DIR / f"{app_name}.app"
    return DIST_DIR / app_name


def ensure_pyinstaller() -> None:
    """Instala PyInstaller si no está presente."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller instalado.")


def build_executable(debug: bool = False) -> str:
    """Ejecuta PyInstaller en modo one-folder.
    debug=True: consola visible para ver errores.
    Retorna el nombre de la carpeta de salida (DeepFlow o DeepFlow-debug).
    """
    ensure_pyinstaller()
    work_dir = PROJECT_ROOT / "build"
    spec_dir = PROJECT_ROOT / "script"
    styles_src = PROJECT_ROOT / "styles.qss"
    config_src = PROJECT_ROOT / "config"
    app_name = DIST_APP_NAME_DEBUG if debug else DIST_APP_NAME

    if not styles_src.exists():
        sys.exit(f"Error: no existe {styles_src}")
    if not config_src.exists():
        sys.exit(f"Error: no existe {config_src}")

    # Iconos: incluir ambos formatos para paridad Mac/Windows (runtime elige el adecuado)
    assets_dir = PROJECT_ROOT / "assets"
    icon_files = []
    for name in ("icon.ico", "icon.icns", "icon.png"):
        p = assets_dir / name
        if p.exists():
            icon_files.append(p)
    icon_for_exe = assets_dir / "icon.ico" if sys.platform == "win32" else assets_dir / "icon.icns"
    if not icon_for_exe.exists():
        icon_for_exe = assets_dir / "icon.png" if (assets_dir / "icon.png").exists() else None

    add_data = [
        f"--add-data={styles_src}{ADD_DATA_SEP}.",
        f"--add-data={config_src}{ADD_DATA_SEP}config",
    ]
    for icon_file in icon_files:
        add_data.append(f"--add-data={icon_file}{ADD_DATA_SEP}assets")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--onedir",
        "--console" if debug else "--windowed",
        "--clean",
        "--noconfirm",
        f"--workpath={work_dir}",
        f"--specpath={spec_dir}",
        f"--distpath={DIST_DIR}",
        "--hidden-import", "yaml",
        "--hidden-import", "cffi",
        "--hidden-import", "_cffi_backend",
        "--collect-all", "PyQt6",
        *add_data,
        str(PROJECT_ROOT / "main.py"),
    ]
    if icon_for_exe and icon_for_exe.exists():
        cmd.extend(["--icon", str(icon_for_exe)])
        print(f"Icono exe: {icon_for_exe.name}")
    if icon_files:
        print(f"Iconos empaquetados: {[p.name for p in icon_files]}")

    mode = "debug (con consola)" if debug else "producción"
    print(f"Ejecutando PyInstaller... [{mode}]")
    subprocess.check_call(cmd)
    print("Build completado.")
    return app_name


def copy_portable_files(app_name: str) -> None:
    """Copia styles.qss donde la app lo busque (PROJECT_ROOT o Contents/MacOS en .app)."""
    app_folder = _app_folder(app_name)
    styles_src = PROJECT_ROOT / "styles.qss"
    if sys.platform == "darwin":
        styles_dst = app_folder / "Contents" / "MacOS" / "styles.qss"
    else:
        styles_dst = app_folder / "styles.qss"
    if styles_src.exists():
        styles_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(styles_src, styles_dst)
        print(f"Copiado styles.qss a {styles_dst.parent}")


def copy_production_config(app_name: str) -> None:
    """Copia deepflow.yaml de producción a dist si no existe."""
    app_folder = _app_folder(app_name)
    if sys.platform == "darwin":
        config_yaml = app_folder / "Contents" / "Resources" / "config" / "yaml" / "deepflow.yaml"
    else:
        config_yaml = app_folder / "_internal" / "config" / "yaml" / "deepflow.yaml"
        if not config_yaml.parent.exists():
            config_yaml = app_folder / "config" / "yaml" / "deepflow.yaml"
    if not config_yaml.exists():
        example = PROJECT_ROOT / "config" / "yaml" / "deepflow.yaml.example"
        if example.exists():
            config_yaml.parent.mkdir(parents=True, exist_ok=True)
            config_yaml.write_text(
                "# DeepFlow – Configuración de producción\n"
                "# La base de datos se crea en ./data junto al ejecutable\n\n"
                "environment: production\n"
                "data_dir: ./data\n"
                "# db_path: ./data/db/deepflow_db.fs  # opcional, explícito\n",
                encoding="utf-8",
            )
            print(f"Creado {config_yaml}")
    else:
        print(f"Config ya existe: {config_yaml}")


def create_dist_readme(app_name: str) -> None:
    """Crea README en dist explicando ubicación de la BDD."""
    app_folder = _app_folder(app_name)
    readme = app_folder / "README.txt"
    readme.write_text(
        "DeepFlow - Despliegue\n"
        "=====================\n\n"
        "Ejecutar: " + (f"{app_name}.exe" if sys.platform == "win32" else f"./{app_name}") + "\n\n"
        "UBICACIÓN DE LA BASE DE DATOS\n"
        "----------------------------\n"
        "La base de datos (ZODB) se crea en:\n"
        "  ./data/db/deepflow_db.fs\n\n"
        "Es decir, en la carpeta 'data' junto al ejecutable.\n"
        "Puedes copiar toda esta carpeta a otro directorio y la app seguirá funcionando.\n\n"
        "CONFIGURACIÓN\n"
        "-------------\n"
        "Edita config/yaml/deepflow.yaml para cambiar:\n"
        "  - data_dir: ruta del directorio de datos (por defecto ./data)\n"
        "  - db_path: ruta explícita del archivo .fs (opcional)\n\n"
        "ESTILOS\n"
        "-------\n"
        "styles.qss en esta carpeta. Puedes personalizarlo.\n",
        encoding="utf-8",
    )
    print(f"Creado {readme}")


def ensure_data_folder(app_name: str) -> None:
    """Crea carpeta data vacía en dist para que el usuario sepa dónde va la BDD."""
    app_folder = _app_folder(app_name)
    if sys.platform == "darwin":
        data_dir = app_folder / "Contents" / "MacOS" / "data"  # junto al exe
    else:
        data_dir = app_folder / "data"
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        (data_dir / ".gitkeep").write_text("")
        print(f"Creada carpeta {data_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build DeepFlow")
    parser.add_argument("--debug", action="store_true", help="Build con consola visible (para ver errores)")
    parser.add_argument("--update", action="store_true", help="Generar además paquete de actualización (ZIP)")
    args = parser.parse_args()

    print("=== Build DeepFlow ===\n")
    app_name = build_executable(debug=args.debug)
    copy_portable_files(app_name)
    copy_production_config(app_name)
    create_dist_readme(app_name)
    ensure_data_folder(app_name)

    if args.update:
        print("\n--- Paquete de actualización ---")
        subprocess.check_call([sys.executable, str(PROJECT_ROOT / "script" / "build_update_package.py")])

    app_folder = _app_folder(app_name)
    print(f"\nListo. Salida en: {DIST_DIR}")
    if args.debug:
        exe_name = "DeepFlow-debug" + (".exe" if sys.platform == "win32" else "")
        print(f"  Ejecutable debug: {app_folder / exe_name}")
        print("  (Ejecutar desde terminal para ver logs y errores)")
    elif sys.platform == "darwin":
        print(f"  Ejecutar: open {app_folder}")
    else:
        print(f"  Ejecutable: {app_folder / app_name}{'.exe' if sys.platform == 'win32' else ''}")


if __name__ == "__main__":
    main()
