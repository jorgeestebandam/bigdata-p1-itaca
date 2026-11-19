import logging
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_db(bd_name):
    try:
        password = os.getenv("MONGO_PASSWORD")
        cliente = MongoClient(f"mongodb://admin:{password}@localhost:27017/")
        db = cliente[bd_name]
        logger.info("Conexión a la base de datos establecida correctamente.")
        return db
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise