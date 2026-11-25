import logging
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from mongodb.conexion import connect_db


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BD_NAME = "mibase"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = Path(BASE_DIR / "ingesta" / "data" / "raw")
DIRECTORY_NAMES = ["2021"]  # Aqui se agregaran las siguientes carpetas de años
FILE_NAMES = ["alumnos.json", "calificaciones.json", "contenidos.json" , "cursos.json"]

def get_path(directory_name, file_name):
    return RAW_DIR / directory_name / file_name

def recorrer_directorios():
    for directory in DIRECTORY_NAMES:
        for file_name in FILE_NAMES:
            file_path = get_path(directory, file_name)
            if file_path.exists():
                procesar_archivo(db, file_path, file_name)
            else:
                logger.warning(f"Archivo no encontrado: {file_path}")
                continue

def get_collection_name(file_name):
    part_name = file_name.split(".")[0]
    return part_name

def procesar_archivo(db, file_path, file_name):
    collection_name = get_collection_name(file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        collection = db[collection_name]
        collection.insert_many(data)
        logger.info(f"Datos insertados en la colección: {collection_name}")

if __name__ == "__main__":
    db = connect_db(BD_NAME)
    recorrer_directorios()
