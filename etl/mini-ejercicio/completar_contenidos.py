from pymongo import MongoClient
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from mongodb.conexion import connect_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BD_NAME = "mibase"

def crear_contenidos_completos(db):
    db["cursos_planos"].create_index("curso_codigo")

    pipeline = [
        {
            "$lookup": {
                "from": "cursos_planos",
                "localField": "curso",
                "foreignField": "curso_codigo",
                "as": "datos_curso",
            }
        },
        {"$unwind": "$datos_curso"},
        {"$unset": "datos_curso._id"},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$datos_curso"]}}},
        {"$project": {"datos_curso": 0}},
        {"$out": "contenidos_completos"},
    ]

    db["contenidos"].aggregate(pipeline)

    total_origen = db["contenidos"].count_documents({})
    total_destino = db["contenidos_completos"].count_documents({})
    logger.info("contenidos_completos: %d de %d contenidos", total_destino, total_origen)
    if total_destino < total_origen:
        logger.warning(
            "%d módulos sin curso en cursos_planos", total_origen - total_destino
        )

def main():
    db = connect_db(BD_NAME)
    crear_contenidos_completos(db)


if __name__ == "__main__":
    main()
