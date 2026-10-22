from pathlib import Path
import logging
import xml.etree.ElementTree as ET
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = Path(BASE_DIR / "data" / "raw")

directory_21_22_path = Path(
    BASE_DIR / "data" / "exportaciones" / "Analisis_Academico" / "2021-22"
)
directory_22_23_path = Path(
    BASE_DIR / "data" / "exportaciones" / "Analisis_Academico" / "2022-23"
)
directory_23_24_path = Path(
    BASE_DIR / "data" / "exportaciones" / "Analisis_Academico" / "2023-24"
)
directory_24_25_path = Path(
    BASE_DIR / "data" / "exportaciones" / "Analisis_Academico" / "2024-25"
)
directory_25_26_path = Path(
    BASE_DIR / "data" / "exportaciones" / "Analisis_Academico" / "2025-26"
)

EXPORT_DIRS = [
    directory_21_22_path,
    directory_22_23_path,
    directory_23_24_path,
    directory_24_25_path,
    directory_25_26_path,
]

TABLAS = ["alumnos", "cursos", "calificaciones", "contenidos", "grupos"]

CAMPOS = {
    "alumnos": {
        "NIA": "NIA",
        "Curso": "curso",
        "Turno": "turno",
        "Grupo": "grupo",
    },
    "cursos": {
        "Curso": "codigo",
        "Nombre_Curso": "nombre_cas",
        "Nombre_Curso_Val": "nombre_val",
        "Abreviatura": "abreviatura",
        "Padre": "padre",
    },
    "calificaciones": {
        "NIA": "alumno",
        "Curso": "curso",
        "Modulo": "contenido",
        "Nota": "nota_numerica",
        "Evaluacion": "evaluacion",
    },
    "contenidos": {
        "Curso": "curso",
        "Modulo": "codigo",
        "Nombre_Modulo": "nombre_cas",
    },
    "grupos": {
        "Grupo": "codigo",
        "Nombre_Grupo": "nombre",
        "Turno": "turno",
        "Modalidad": "modalidad",
        "Capacidad": "capacidad",
    },
}

CAMPOS_ANONIMIZAR = {"NIA"}


def obtener_archivos_xml(directory_path):
    files = []
    for file in directory_path.iterdir():
        if file.is_file() and file.suffix == ".xml":
            files.append(file)
    return files


def extraer_fecha(directory_path):
    fecha = directory_path.name
    return fecha


def crear_nuevo_directorio(directory_path):
    fecha = extraer_fecha(directory_path)
    nuevo_directorio = RAW_DIR / fecha
    if nuevo_directorio.exists():
        logging.info(f"El directorio {nuevo_directorio} ya existe.")
    else:
        nuevo_directorio.mkdir(parents=True, exist_ok=True)
        logging.info(f"Se ha creado el directorio {nuevo_directorio}.")

    return nuevo_directorio


def crear_raw_directorios(directory_path):
    nuevo_directorio = crear_nuevo_directorio(directory_path)
    return nuevo_directorio


def recorrer_archivos(files, nuevo_directorio):
    for file in files:
        procesar_archivo(file, nuevo_directorio)


def procesar_archivo(file, nuevo_directorio):
    tabla = detectar_tabla(file)
    if tabla is None:
        logger.warning("Archivo ignorado (tabla no reconocida): %s", file.name)
        return

    anyo = nuevo_directorio.name  # "2021-22"

    try:
        registros = extraer_registros(file, tabla, anyo)
    except ET.ParseError as e:
        logger.error("XML mal formado en %s: %s", file.name, e)
        return

    ruta_json = guardar_json(registros, file, nuevo_directorio)
    logger.info(
        "%s -> %s (%d registros, tabla '%s')",
        file.name,
        ruta_json.name,
        len(registros),
        tabla,
    )


def detectar_tabla(file):
    nombre = file.stem.lower()
    for tabla in TABLAS:
        if tabla in nombre:
            return tabla
    return None


def extraer_registros(file, tabla, anyo):
    raiz = ET.parse(file).getroot()
    contenedor = next(iter(raiz), None)
    if contenedor is None:
        return []

    registros = []
    for nodo in contenedor:
        registro = {"Anyo": anyo}
        for campo_json, atributo_xml in CAMPOS[tabla].items():
            valor = limpiar(nodo.get(atributo_xml))
            if campo_json in CAMPOS_ANONIMIZAR and valor is not None:
                valor = anonimizar_nia(valor)
            registro[campo_json] = valor
        registros.append(registro)
    return registros


def guardar_json(registros, file, nuevo_directorio):
    """Guarda los registros en un .json con el mismo nombre que el .xml."""
    ruta_json = nuevo_directorio / f"{file.stem}.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    return ruta_json


def limpiar(valor):
    """Quita espacios; los valores vacíos o ' ' pasan a None."""
    if valor is None:
        return None
    valor = valor.strip()
    return valor or None


def anonimizar_nia(nia: str) -> str:
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]


def main():
    for directory_path in EXPORT_DIRS:
        if not directory_path.exists():
            logger.warning("No existe %s, se omite", directory_path.name)
            continue
        nuevo_directorio = crear_raw_directorios(directory_path)
        files = obtener_archivos_xml(directory_path)
        recorrer_archivos(files, nuevo_directorio)


if __name__ == "__main__":
    main()
