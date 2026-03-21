# Instalación de DeepFlow (Windows)

Guía para instalar y actualizar DeepFlow en Windows usando los artefactos de GitHub Actions.

> **Origen de los artefactos:** Si aún no tienes el pipeline configurado, ver [Tutorial GitHub Actions](tutorial-github-actions.md).

---

## Instalación inicial

### 1. Descargar el artefacto

- Entra en tu repositorio → **Actions** → selecciona el workflow que completó correctamente.
- Descarga el artefacto **DeepFlow-Windows**.
- Descomprime el ZIP. Obtendrás una carpeta `DeepFlow` con el ejecutable y los archivos necesarios.

### 2. Ubicación

Copia la carpeta `DeepFlow` al lugar donde quieras la aplicación, por ejemplo:

```
C:\Apps\DeepFlow\
```

### 3. Ejecutar

Doble clic en `DeepFlow.exe`. La base de datos se crea automáticamente en `DeepFlow\data\db\` la primera vez que abras la app.

---

## Actualizar (conservar tus datos)

Cuando haya una nueva versión, usa el artefacto **DeepFlow-update** para actualizar sin perder tus tareas.

### Pasos

1. **Cierra DeepFlow** si está abierto.

2. Descarga el artefacto **DeepFlow-update** desde Actions (es un ZIP más pequeño que el instalador completo).

3. Abre el ZIP y **extrae todo su contenido dentro** de la carpeta donde tienes DeepFlow instalado.

   Ejemplo: si DeepFlow está en `C:\Apps\DeepFlow\`:
   - Abre `DeepFlow-update.zip`.
   - Selecciona todo lo que hay dentro (carpeta `DeepFlow` y su contenido).
   - Extrae en `C:\Apps\` (o en la carpeta padre de tu instalación).
   - Confirma **Sobrescribir** cuando Windows pregunte por archivos existentes.

4. Tus datos se conservan porque el paquete de actualización **no incluye** la carpeta `data\`. Solo se reemplazan el ejecutable, las bibliotecas y la configuración. La base de datos (`data\db\deepflow_db.fs`) permanece intacta.

### Qué se reemplaza y qué no

| Se reemplaza | No se toca |
|--------------|------------|
| DeepFlow.exe | data\ (tus tareas) |
| _internal\   | config\yaml\deepflow.yaml (tu configuración personalizada) |
| config\ (plantillas) | |
| styles.qss   | |

---

## Resolución de problemas

### "No aparece la carpeta DeepFlow tras descomprimir"

Algunos descompresores crean una carpeta intermedia. Verifica que `DeepFlow.exe` esté dentro de la ruta que abres. La estructura correcta es:

```
DeepFlow\
├── DeepFlow.exe
├── _internal\
├── config\
├── data\
├── styles.qss
└── README.txt
```

### "Pierdo las tareas al actualizar"

Solo ocurre si extraes el ZIP en una carpeta distinta a la instalación actual. Siempre descomprime **en la misma carpeta** donde está `DeepFlow.exe`.
