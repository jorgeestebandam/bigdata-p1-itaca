from pymongo import MongoClient
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from mongodb.conexion import connect_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BD_NAME = "mibase"
def aplanar(coleccion):

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
                "_id": 0,
                "familia": "$familia.nombre_cas",
                "grado": "$grado.nombre_cas",
                "ciclo": "$ciclo.nombre_cas",
                "ciclo_abreviatura": "$ciclo.abreviatura",
                "primseg": {"$arrayElemAt": [{"$split": ["$nombre_cas", " "]}, 0]},
                "curso_codigo": "$codigo",
                "curso_abreviatura": "$abreviatura",
            }
        },
        {"$out": "cursos_planos"},
    ]

    coleccion.aggregate(pipeline)
    logger.info("cursos_planos: %d documentos", coleccion.database["cursos_planos"].count_documents({}))


def main():
    db = connect_db(BD_NAME)
    coleccion = db["cursos"]
    aplanar(coleccion)


if __name__ == "__main__":
    main()
