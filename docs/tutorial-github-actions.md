# Tutorial: GitHub Actions para DeepFlow

Guía completa para configurar el repositorio, el pipeline de build y la distribución del ejecutable Windows.

---

## Índice

1. [Protección de ramas (solo PRs)](#1-protección-de-ramas-solo-prs)
2. [Configuración del workflow](#2-configuración-del-workflow)
3. [Qué hace el pipeline](#3-qué-hace-el-pipeline)
4. [Ejecución y artefactos](#4-ejecución-y-artefactos)
5. [Instalar y actualizar](#5-instalar-y-actualizar)

---

## 1. Protección de ramas (solo PRs)

Para que el código solo entre en `main` mediante Pull Requests:

### 1.1 Entrar en la configuración del repositorio

1. Abre tu repositorio en GitHub.
2. Ve a **Settings** (Configuración).
3. En el menú izquierdo, **Branches**.
4. En **Branch protection rules**, haz clic en **Add rule** (o edita la regla existente).

### 1.2 Configurar la regla

| Campo | Valor recomendado | Descripción |
|-------|-------------------|-------------|
| **Branch name pattern** | `main` | Rama protegida (usa `master` si es tu rama principal). |
| **Require a pull request before merging** | Activado | Obliga a usar PRs. |
| **Require approvals** | 1 (opcional) | Al menos una aprobación antes de fusionar. |
| **Require status checks to pass before merging** | Activado | El workflow debe pasar. |
| **Require branches to be up to date before merging** | Activado | La rama debe estar actualizada con `main`. |
| **Status checks that are required** | `build` | Nombre del job (debe coincidir con el workflow). |
| **Do not allow bypassing the above settings** | Activado (admin) | Ni admins pueden saltarse la protección. |
| **Allow force pushes** | Desactivado | Evita `git push --force` sobre `main`. |
| **Allow deletions** | Desactivado | Evita borrar la rama principal. |

### 1.3 Guardar

Haz clic en **Create** o **Save changes**.

A partir de ahora, nadie podrá hacer push directo a `main`; todo deberá pasar por un PR y el build debe completar correctamente.

---

## 2. Configuración del workflow

### 2.1 Archivo del workflow

El workflow está en:

```
.github/workflows/build.yml
```

### 2.2 Contenido completo del workflow

El archivo `.github/workflows/build.yml` debe contener:

```yaml
name: Build

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt Pillow pyinstaller

      - name: Generate icons
        run: python script/generate_icons.py

      - name: Build
        run: python script/build_dist.py

      - name: Build update package
        run: python script/build_update_package.py

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: DeepFlow-Windows
          path: dist/

      - name: Upload update package
        uses: actions/upload-artifact@v4
        with:
          name: DeepFlow-update
          path: dist/DeepFlow-update.zip
```

> **Importante:** El nombre del job es `build`. Si lo cambias, actualiza también el *status check* en la regla de protección de ramas (paso 1.2).

### 2.3 Cuándo se ejecuta

- **Push** a `main` o `master`: build completo.
- **Pull request** hacia `main` o `master`: build para validar antes de fusionar.

### 2.4 Añadir el workflow si no existe

1. Crea la carpeta `.github/workflows/` en la raíz del repo.
2. Crea el archivo `build.yml` con el contenido de la [sección 2.2](#22-contenido-completo-del-workflow).
3. Haz commit y push:

   ```bash
   git add .github/workflows/build.yml
   git commit -m "Add GitHub Actions build workflow"
   git push
   ```

---

## 3. Qué hace el pipeline

| Paso | Descripción |
|------|-------------|
| Checkout | Clona el repositorio. |
| Set up Python | Instala Python 3.11. |
| Install dependencies | `requirements.txt` + Pillow + PyInstaller. |
| Generate icons | Genera `icon.png`, `icon.ico` para Windows. |
| Build | PyInstaller crea el ejecutable en `dist/DeepFlow/`. |
| Build update package | Crea `DeepFlow-update.zip` (sin `data/`). |
| Upload artifacts | Sube los artefactos para descarga. |

**Duración aproximada:** 5–10 minutos.

---

## 4. Ejecución y artefactos

### 4.1 Ver el estado del workflow

1. En GitHub, abre la pestaña **Actions**.
2. Selecciona el workflow **Build**.
3. Cada ejecución aparece con su rama, commit y estado (✔ / ❌).

### 4.2 Descargar artefactos

1. Haz clic en una ejecución que haya terminado con éxito.
2. En la parte inferior, en **Artifacts**, verás:
   - **DeepFlow-Windows**: instalador completo (`dist/`).
   - **DeepFlow-update**: paquete de actualización (ZIP).

### 4.3 Nota sobre Pull Requests

Los artefactos de un PR no están pensados para instalación en producción. Úsalos solo para probar el build antes de fusionar. Los artefactos de **producción** son los de los push a `main` (o `master`).

---

## 5. Instalar y actualizar

Tras descargar los artefactos, sigue la guía de instalación:

→ **[Guía de instalación (Windows)](instalacion.md)**

| Caso | Artefacto | Sección |
|------|-----------|---------|
| **Instalación desde cero** | DeepFlow-Windows | [Instalación inicial](instalacion.md#instalación-inicial) |
| **Actualizar (conservar tareas)** | DeepFlow-update | [Actualizar](instalacion.md#actualizar-conservar-tus-datos) |

---

## Flujo completo resumido

```
Desarrollo → PR → Build corre → Revisión → Merge a main
                                    ↓
                            Artefactos disponibles
                                    ↓
                    Instalación nueva o actualización
                                    ↓
                    Ver docs/instalacion.md
```
