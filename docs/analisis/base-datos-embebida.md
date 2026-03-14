# Análisis: Base de datos embebida para DeepFlow

Documento de análisis para sustentar la elección de persistencia local en el proyecto.

---

## 1. Objetivos y requisitos


| Requisito                     | Descripción                                                      |
| ----------------------------- | ---------------------------------------------------------------- |
| **Archivos locales**          | Uno o varios archivos en disco, sin servidor externo             |
| **Capacidad de crecer**       | Soportar incremento de datos (tareas, transiciones) sin degradar |
| **Versionado**                | Posibilidad de migrar el schema cuando cambie el modelo de datos |
| **Instalación sencilla**      | `pip install` sin permisos de administrador                      |
| **Sin dependencias externas** | No requerir MySQL, PostgreSQL ni servicios de sistema            |
| **Portabilidad**              | Copiar la app + datos y funcionar en otra máquina                |


---

## 2. Candidatos analizados

### 2.1 ZODB (Zope Object Database)

**Instalación:** `pip install ZODB transaction` — Pure Python + extensiones opcionales. Sin permisos admin.


| Criterio         | Valoración                                                               |
| ---------------- | ------------------------------------------------------------------------ |
| Archivos locales | ✅ Uno o varios archivos `.fs` (FileStorage)                              |
| Crecimiento      | ✅ Append-only; escala bien con miles de objetos                          |
| Versionado       | ✅ `schema_version` en root + migraciones en código (`migrate_to_latest`) |
| Instalación pip  | ✅ ZODB y dependencias en PyPI                                            |
| Sin admin        | ✅ Instalación en user space                                              |


**Pros**

- Almacena objetos Python directamente: diccionarios, listas, clases propias.
- Transacciones ACID; integridad ante fallos.
- Sin mapeo ORM: el modelo en código es el modelo en disco.
- FileStorage: un archivo principal `.fs` (+ `.lock`, `.index`, `.tmp` opcionales).
- Muy maduro (Zope, Plone); usado en producción desde hace décadas.
- Migraciones de schema implementables en Python puro.

**Contras**

- Menos conocido que SQLite; curva de aprendizaje para equipos nuevos.
- FileStorage no compacta por defecto (puede crecer más de lo estrictamente necesario; hay `zodbpack` para compactar).
- Dependencias: `persistent`, `BTrees`, `transaction`.

---

### 2.2 SQLite

**Instalación:** Incluido en Python. Cero dependencias adicionales.


| Criterio         | Valoración                                              |
| ---------------- | ------------------------------------------------------- |
| Archivos locales | ✅ Un archivo `.db` o `.sqlite`                          |
| Crecimiento      | ✅ Excelente; hasta TB, bien optimizado                  |
| Versionado       | ✅ Migraciones con tablas `schema_version` + scripts SQL |
| Instalación pip  | ✅ `sqlite3` en stdlib                                   |
| Sin admin        | ✅ Totalmente portable                                   |


**Pros**

- Estándar de facto para bases embebidas.
- ACID, SQL estándar, transacciones, índices.
- Un solo archivo; fácil de copiar y respaldar.
- Muy documentado y con gran ecosistema de herramientas.
- Escala bien para el volumen típico de DeepFlow.

**Contras**

- Requiere definir tablas y mapear objetos ↔ filas (ORM o SQL manual).
- Más código para CRUD y migraciones que con un store de objetos.
- Para estructuras anidadas (listas de subtareas, transiciones) hay que diseñar tablas y relaciones.

---

### 2.3 TinyDB

**Instalación:** `pip install tinydb` — Pure Python, sin extensiones nativas.


| Criterio         | Valoración                                                |
| ---------------- | --------------------------------------------------------- |
| Archivos locales | ✅ JSON en disco                                           |
| Crecimiento      | ⚠️ Carga todo en memoria; poco adecuado para crecer mucho |
| Versionado       | ⚠️ Manual; no hay concepto de schema                      |
| Instalación pip  | ✅ Muy ligero                                              |
| Sin admin        | ✅ Totalmente portable                                     |


**Pros**

- API muy simple; tipo "diccionario con persistencia".
- Un solo archivo JSON legible y editable a mano.
- Sin dependencias pesadas; ideal para prototipos y demos.

**Contras**

- Carga todo el documento en RAM: con miles de tareas y transiciones puede ser un problema.
- No transaccional en el sentido ACID; riesgo de corrupción si la app termina mal.
- Versionado y migraciones: hay que implementarlos por cuenta propia.
- Pensado para datasets pequeños (< 10–20 MB típicamente).

---

### 2.4 LMDB (Lightning Memory-Mapped Database)

**Instalación:** `pip install lmdb` — Hay wheels precompilados; puede requerir compilador en algunos entornos.


| Criterio         | Valoración                                                             |
| ---------------- | ---------------------------------------------------------------------- |
| Archivos locales | ✅ Directorio con archivos `data.mdb`, `lock.mdb`                       |
| Crecimiento      | ✅ Key-value de alto rendimiento                                        |
| Versionado       | ⚠️ Bajo nivel; versionado a implementar en la capa de aplicación       |
| Instalación pip  | ⚠️ Extensiones C; wheels en muchas plataformas, pero no 100% universal |
| Sin admin        | ✅ Generalmente sí                                                      |


**Pros**

- Muy rápido; clave-valor con orden lexicográfico.
- Multi-proceso; transacciones ACID.
- Mapeo en memoria; bueno para lecturas intensivas.

**Contras**

- Modelo clave-valor: hay que serializar/deserializar objetos (JSON, msgpack, pickle).
- No es un store de objetos; más trabajo para estructuras complejas.
- En entornos sin wheels (ej. algunas distros Linux antiguas) puede necesitar compilación.
- Versionado y migraciones hay que diseñarlos encima de LMDB.

---

### 2.5 JSON plano + lógica propia

**Instalación:** Solo stdlib (`json`, `pathlib`).


| Criterio         | Valoración                               |
| ---------------- | ---------------------------------------- |
| Archivos locales | ✅ Un `.json`                             |
| Crecimiento      | ❌ Reescribe el archivo entero; no escala |
| Versionado       | ⚠️ Manual; sin soporte nativo            |
| Instalación pip  | ✅ Nada que instalar                      |
| Sin admin        | ✅ Totalmente portable                    |


**Pros**

- Máxima simplicidad; sin dependencias.
- Formato legible y fácil de inspeccionar.

**Contras**

- Cada guardado reescribe todo el archivo: lento y arriesgado con muchos datos.
- Sin transacciones: riesgo de corrupción en cierres inesperados.
- Versionado y migraciones completamente manuales.
- No apto para crecer más allá de unos cientos de registros.

---

## 3. Comparativa resumida


| Criterio                        | ZODB  | SQLite       | TinyDB | LMDB | JSON     |
| ------------------------------- | ----- | ------------ | ------ | ---- | -------- |
| Archivo(s) local(es)            | ✅     | ✅            | ✅      | ✅    | ✅        |
| Crecimiento sin límite práctico | ✅     | ✅            | ❌      | ✅    | ❌        |
| Versionado / migraciones        | ✅     | ✅            | ⚠️     | ⚠️   | ⚠️       |
| pip install sin admin           | ✅     | N/A (stdlib) | ✅      | ⚠️   | N/A      |
| Objetos Python directos         | ✅     | ❌            | ✅      | ❌    | ✅        |
| Transacciones ACID              | ✅     | ✅            | ❌      | ✅    | ❌        |
| Un solo archivo principal       | ✅     | ✅            | ✅      | ❌    | ✅        |
| Complejidad de adopción         | Media | Media        | Baja   | Alta | Muy baja |


---

## 4. Conclusión: elección de ZODB

Para DeepFlow se recomienda **ZODB** porque:

1. **Objetos directos**
  El modelo (columnas, tareas, transiciones) son diccionarios y listas. ZODB los persiste sin mapeo ORM ni tablas.
2. **Un archivo principal**
  `data/db/deepflow_db.fs` concentra los datos; es fácil de copiar, respaldar y versionar en el directorio `data/db/`.
3. **Crecimiento**
  FileStorage es append-only y maneja bien el aumento de tareas y transiciones sin reescribir todo el archivo.
4. **Versionado**
  Ya usamos `schema_version` en root y `migrate_to_latest()` en `infrastructure/persistence/schema_versions.py`. Migrar nuevos campos o estructuras es cuestión de código Python.
5. **Instalación**
  `pip install ZODB transaction` en el entorno del usuario, sin privilegios de administrador.
6. **Portabilidad**
  Copiar el directorio `data/` (o el proyecto completo) a otra máquina y ejecutar con el mismo intérprete Python es suficiente.

**Alternativa válida:** SQLite sería una opción sólida si se priorizase el uso de SQL, herramientas gráficas estándar y máxima compatibilidad. Implicaría definir tablas, índices y migraciones, pero cumpliría igualmente los objetivos de archivos locales, crecimiento y versionado.

---

## 5. Referencias

- [ZODB – Zope Object Database](https://zodb.org/)
- [SQLite](https://www.sqlite.org/) – Incluido en Python
- [TinyDB](https://github.com/msiemens/tinydb) – JSON document store
- [LMDB](https://www.symas.com/lmdb) – Key-value store de alto rendimiento
- [Guía de versionado de base de datos](../codigo/versionado-base-datos.md) – Migraciones en DeepFlow
