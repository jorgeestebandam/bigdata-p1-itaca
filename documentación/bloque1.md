
## Fuentes de datos
 
### Mecanismo de acceso
 
Exportación en ficheros XML de ITACA (informes de *Análisis Académico*), colocados manualmente en `ingesta/data/exportaciones/Analisis_Academico/<curso>/`. No requiere credenciales ni conexión a ITACA desde el script.
 
Cursos académicos procesados: `2021-22`, `2022-23`, `2023-24`, `2024-25` y `2025-26`.
 
### Tablas y campos
 
Además de los campos listados, todos los registros incluyen `Anyo` (curso académico, p. ej. `2021-22`).
 
| Tabla | Campos |
|---|---|
| `alumnos` | `NIA`, `sexo`, `nacionalidad`, `provincia`, `municipio`, `ensenanza`, `curso`, `grupo`, `turno`, `linea`, `modalidad`, `repite`, `estado_matricula`, `tipo_matricula`, `fecha_matricula`, `fecha_ingreso_centro` |
| `cursos` | `codigo`, `nombre_cas`, `nombre_val`, `abreviatura`, `ensenanza`, `padre` |
| `calificaciones` | `evaluacion`, `alumno`, `ensenanza`, `curso`, `contenido`, `bloque_contenido`, `nota_numerica`, `tipo_nota` |
| `contenidos` | `codigo`, `nombre_cas`, `nombre_val`, `ensenanza`, `curso` |
| `grupos` | `Grupo`, `Nombre_Grupo`, `Turno`, `Modalidad`, `Capacidad` |
 

```
 
## Estructura de carpetas
 
```text
proyecto-1-itaca/
└── ingesta/
    ├── data/
    │   ├── exportaciones/
    │   │   └── Analisis_Academico/
    │   │       ├── 2021-22/    # XML de origen
    │   │       ├── 2022-23/
    │   │       └── ...
    │   └── raw/
    │       ├── 2021-22/
    │       └── ...
    └── scripts/
        └── ingesta_itaca_xml.py
```
 
## Preparación del entorno
 
```bash
cd proyecto-1-itaca
python -m venv .venv
source .venv/bin/activate      # En Windows: .venv\Scripts\activate
```
 
El script solo usa la biblioteca estándar de Python (`pathlib`, `xml.etree.ElementTree`, `json`, `hashlib`, `logging`), por lo que no necesita dependencias adicionales.
 
## Ejecución
 
```bash
python ingesta/scripts/ingesta_itaca_xml.py
```
 
## Funcionamiento del script
 
1. **Recorre los cursos** definidos en `EXPORT_DIRS`. Si una carpeta no existe, lo registra como aviso y continúa con la siguiente.
2. **Crea la carpeta de destino** `ingesta/data/raw/<curso>/` si no existe.
3. **Lista los `.xml`** de la carpeta del curso.
4. **Detecta la tabla** a partir del nombre del fichero (`alumnos`, `cursos`, `calificaciones`, `contenidos`, `grupos`). Los ficheros no reconocidos se ignoran con un aviso.
5. **Obtiene el mapa de campos** de la tabla con `mapa_campos` (una vez por fichero, no por nodo).
6. **Extrae los registros**: toma el primer elemento hijo de la raíz como contenedor y recorre sus nodos, leyendo los atributos definidos en `CAMPOS`.
7. **Limpia los valores**: elimina espacios y convierte cadenas vacías en `None` (`null` en JSON).
8. **Anonimiza el NIA** (ver siguiente apartado).
9. **Guarda un JSON** con el mismo nombre que el XML en `ingesta/data/raw/<curso>/`, en UTF-8 y con `ensure_ascii=False` para conservar tildes y eñes.
### Funciones principales
 
| Función | Responsabilidad |
|---|---|
| `obtener_archivos_xml` | Lista los XML de un directorio |
| `detectar_tabla` | Asocia un fichero a una tabla por su nombre |
| `mapa_campos` | Normaliza la definición de `CAMPOS` (lista o diccionario) a `{campo_json: atributo_xml}` |
| `extraer_registros` | Parsea el XML y construye la lista de registros |
| `limpiar` | Normaliza espacios y vacíos |
| `anonimizar_nia` | Sustituye el NIA por un identificador anónimo |
| `guardar_json` | Escribe el resultado en `ingesta/data/raw/` |
 
## Anonimización del NIA
 
El NIA es un dato identificativo, por lo que se sustituye antes de guardar nada en disco:
 
```python
def anonimizar_nia(nia: str) -> str:
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]
```
 
- Se aplica a los campos incluidos en `CAMPOS_ANONIMIZAR` (`NIA` en `alumnos` y `alumno` en `calificaciones`). La comprobación se hace contra el nombre del campo en el JSON.
- La función es **determinista**: un mismo NIA genera siempre el mismo identificador, por lo que `alumnos` y `calificaciones` siguen pudiendo cruzarse.
- No se guarda ningún mapa NIA → identificador, de modo que el proceso no deja rastro del dato original.
## Manejo de errores y logging
 
- `logging` en nivel `INFO`: informa de directorios creados, ficheros procesados y número de registros.
- `WARNING` para carpetas de curso inexistentes y ficheros de tabla no reconocida.
- `ERROR` para XML mal formados (`ET.ParseError`): se registra el fichero y se continúa con el resto.
## Verificación
 
Tras ejecutar el script, comprobar que:
 
- [x] Existe una carpeta por curso en `ingesta/data/raw/` con un JSON por cada XML.
- [x] No aparece ningún NIA real en los JSON.
- [x] El NIA anonimizado coincide entre `alumnos` (`NIA`) y `calificaciones` (`alumno`) para el mismo alumno.
- [x] Todo `contenido` de `calificaciones` existe en `contenidos` (mismo `Anyo` y `curso`).
- [x] Todo `grupo` de `alumnos` existe en `grupos`.
- [x] El número de registros del log coincide con el de nodos del XML.
## Próximos pasos
 
En el Bloque 2 se modelarán `calificaciones` y `contenidos` en MongoDB, pensando en las consultas del futuro dashboard de Power BI.
 

