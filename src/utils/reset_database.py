import logging
import os

import dotenv

from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class ResetDatabase(metaclass=Singleton):
    """
    Réinitialisation de la base
    """

    @log
    def lancer(self, test_dao: bool = False) -> bool:
        dotenv.load_dotenv()

        # Schéma cible + script de population
        schema = "projet_test_dao" if test_dao else os.environ["POSTGRES_SCHEMA"]
        pop_path = "data/pop_db_test.sql" if test_dao else "data/pop_db.sql"

        # DDL schéma
        ddl = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        # Lire les scripts
        with open("data/init_db.sql", encoding="utf-8") as f:
            init_sql = f.read()
        with open(pop_path, encoding="utf-8") as f:
            pop_sql = f.read()

        # Exécution simple (les scripts contiennent du SQL exécutable)
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                # Recréation du schéma
                cur.execute(ddl)
                # Très important : on ajoute "public" pour voir pgcrypto (crypt/gen_salt)
                cur.execute(f"SET search_path TO {schema}, public;")

                # Init + seed
                cur.execute(init_sql)
                cur.execute(pop_sql)

        logging.info("[ResetDB] Terminé")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ResetDatabase().lancer()  # schéma = POSTGRES_SCHEMA du .env
    ResetDatabase().lancer(True)  # schéma = projet_test_dao
