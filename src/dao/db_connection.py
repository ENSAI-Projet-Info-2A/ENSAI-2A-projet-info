import logging
import os

import dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from src.utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Classe de connexion à la base de données.
    Gère une unique connexion (Singleton).
    """

    def __init__(self):
        """Ouverture de la connexion"""
        logging.debug("[DBConnection] Initialisation de la connexion BDD...")

        dotenv.load_dotenv()

        try:
            self.__connection = psycopg2.connect(
                host=os.environ["POSTGRES_HOST"],
                port=os.environ["POSTGRES_PORT"],
                database=os.environ["POSTGRES_DATABASE"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
                cursor_factory=RealDictCursor,
            )
            logging.info(
                "[DBConnection] Connexion établie avec succès vers la base '%s' (schema=%s).",
                os.environ.get("POSTGRES_DATABASE"),
                os.environ.get("POSTGRES_SCHEMA"),
            )

        except Exception as e:
            logging.error("[DBConnection] ERREUR de connexion à la base : %s", e)
            raise

    @property
    def connection(self):
        return self.__connection
