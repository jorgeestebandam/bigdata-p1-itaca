import logging
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

sys.path.append(str(Path(__file__).resolve().parents[2]))
from mongodb.conexion import connect_db

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BD_NAME = os.getenv("DB_NAME")
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = Path(BASE_DIR / "ingesta" / "data" / "raw")
DIRECTORY_NAMES = ["2021", "2022", "2023", "2024", "2025"]
FILE_NAMES = ["alumnos.json", "calificaciones.json", "cursos.json", "contenidos.json"]
VARIABLES = {
    "alumnos": {
        "NIA": "nia",
        "anyo": "anyo",
        "fecha_nac": "fecha_nac",
        "turno": "turno",
        "curso": "curso",
        "grupo": "grupo",
        "sexo": "sexo",
        "repite": "repite",
        "estado_matricula": "estado_matricula",
    },
    "calificaciones": {
        "alumno": "nia",
        "anyo": "anyo",
        "curso": "curso",
        "contenido": "modulo",
        "nota_numerica": "nota",
        "evaluacion": "evaluacion",
    },
    "modulos": {
        "anyo": "anyo",
        "curso": "curso",
        "codigo": "modulo",
        "nombre_cas": "nombre_modulo",
    },
}
CAMPOS_CURSO = ["ciclo", "familia", "primseg", "grado"]
COLECCIONES = ["alumnos", "calificaciones", "modulos", "cursos"]


def limpiar_bd(db):
    # Recarga completa: se borran las colecciones (y sus índices) antes de cargar
    for col in COLECCIONES:
        db[col].drop()
    logger.info("Colecciones borradas")


def crear_indices(db):
    db["calificaciones"].create_index([("curso", 1), ("anyo", 1), ("evaluacion", 1)])
    db["calificaciones"].create_index("nia")
    db["alumnos"].create_index([("nia", 1), ("anyo", 1)])
    db["alumnos"].create_index([("curso", 1), ("anyo", 1)])
    db["modulos"].create_index([("modulo", 1), ("anyo", 1), ("curso", 1)], unique=True)
    logger.info("Índices creados")


def get_path(directory_name, file_name):
    return RAW_DIR / directory_name / file_name


def recorrer_directorios(db):
    for directory in DIRECTORY_NAMES:
        for file_name in FILE_NAMES:
            file_path = get_path(directory, file_name)
            if file_path.exists():
                procesar_archivo(db, file_path, file_name)
            else:
                logger.warning(f"Archivo no encontrado: {file_path}")


def get_collection_name(file_name):

    part_name = file_name.split(".")[0]
    return part_name


def extraer_datos(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def limpiar_datos(data, collection_name):
    data_limpio = []

    mapeo = VARIABLES[collection_name]

    for fila in data:
        registro = {}
        for campo_origen, campo_destino in mapeo.items():
            registro[campo_destino] = fila.get(campo_origen)
        data_limpio.append(registro)

    return data_limpio


def insertar_datos(db, collection_name, datos_limpios):

    collection = db[collection_name]
    collection.insert_many(datos_limpios)
    logger.info(f"Datos insertados en la colección: {collection_name}")


def aplanar_cursos(db):

    collection = db["cursos"]

    pipeline = [
        {"$match": {"nombre_cas": {"$regex": "^(Primero|Segundo)"}}},
        {
            "$lookup": {
                "from": "cursos",
                "localField": "padre",
                "foreignField": "codigo",
                "as": "ciclo",
            }
        },
        {"$unwind": "$ciclo"},
        {
            "$lookup": {
                "from": "cursos",
                "localField": "ciclo.padre",
                "foreignField": "codigo",
                "as": "grado",
            }
        },
        {"$unwind": "$grado"},
        {
            "$lookup": {
                "from": "cursos",
                "localField": "grado.padre",
                "foreignField": "codigo",
                "as": "familia",
            }
        },
        {"$unwind": "$familia"},
        {
            "$project": {
                # el _id se mantiene para poder actualizar el mismo documento
                "familia": "$familia.nombre_cas",
                "grado": "$grado.nombre_cas",
                "ciclo": "$ciclo.nombre_cas",
                "ciclo_abreviatura": "$ciclo.abreviatura",
                "primseg": {"$arrayElemAt": [{"$split": ["$nombre_cas", " "]}, 0]},
                "curso_codigo": "$codigo",
                "curso_abreviatura": "$abreviatura",
            }
        },
        {
            "$merge": {
                "into": "cursos",
                "on": "_id",
                "whenMatched": "merge",
                "whenNotMatched": "discard",
            }
        },
    ]

    collection.aggregate(pipeline)


def data_modulos(file_path, db):
    data = extraer_datos(file_path)
    data_limpio = limpiar_datos(data, "modulos")
    aplanar_cursos(db)

    insertar_datos(db, "modulos", data_limpio)

    pipeline = [
        {"$match": {"anyo": data_limpio[0]["anyo"]}},
        {
            "$lookup": {
                "from": "cursos",
                "localField": "curso",
                "foreignField": "codigo",
                "as": "curso_info",
            }
        },
        {"$unwind": {"path": "$curso_info", "preserveNullAndEmptyArrays": True}},
        {
            "$set": {
                "ciclo": "$curso_info.ciclo",
                "familia": "$curso_info.familia",
                "primseg": "$curso_info.primseg",
                "grado": "$curso_info.grado",
            }
        },
        {"$unset": "curso_info"},
        {"$merge": {"into": "modulos", "on": "_id", "whenMatched": "merge"}},
    ]
    db["modulos"].aggregate(pipeline)
    db["cursos"].drop()


def procesar_archivo(db, file_path, file_name):
    collection_name = get_collection_name(file_name)

    if collection_name == "cursos":
        data = extraer_datos(file_path)
        insertar_datos(db, "cursos", data)
        return

    if collection_name == "contenidos":
        data_modulos(file_path, db)
        return

    data = extraer_datos(file_path)
    datos = limpiar_datos(data, collection_name)
    insertar_datos(db, collection_name, datos)


if __name__ == "__main__":
    db = connect_db(BD_NAME)
    limpiar_bd(db)
    crear_indices(db)
    recorrer_directorios(db)
