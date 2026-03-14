DeepFlow - Despliegue
=====================

Ejecutar: ./DeepFlow

UBICACIÓN DE LA BASE DE DATOS
----------------------------
La base de datos (ZODB) se crea en:
  ./data/db/deepflow_db.fs

Es decir, en la carpeta 'data' junto al ejecutable.
Puedes copiar toda esta carpeta a otro directorio y la app seguirá funcionando.

CONFIGURACIÓN
-------------
Edita config/yaml/deepflow.yaml para cambiar:
  - data_dir: ruta del directorio de datos (por defecto ./data)
  - db_path: ruta explícita del archivo .fs (opcional)

ESTILOS
-------
styles.qss en esta carpeta. Puedes personalizarlo.
