import logging
from utils.singleton import Singleton
from utils.log_decorator import log
from dao.db_connection import DBConnection
from business_object.utilisateur import Utilisateur


class UtilisateurDao(metaclass=Singleton):
    """Accès BDD pour les Utilisateurs"""

    @log
    def creer(self, utilisateur: Utilisateur) -> bool:
        """Insère un utilisateur et renseigne son id"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO utilisateur(pseudo, password_hash) "
                        "VALUES (%(pseudo)s, %(password_hash)s) "
                        "RETURNING id; ",
                        {
                            "pseudo": utilisateur.pseudo,
                            "password_hash": utilisateur.password_hash,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        if res:
            utilisateur.id = res["id"]
            return True
        return False

    @log
    def trouver_par_id(self, user_id: int) -> Utilisateur | None:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, pseudo, password_hash "
                        "FROM utilisateur "
                        "WHERE id = %(id)s; ",
                        {"id": user_id},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not row:
            return None
        return Utilisateur(
            id=row["id"], pseudo=row["pseudo"], password_hash=row["password_hash"]
        )

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Utilisateur | None:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, pseudo, password_hash "
                        "FROM utilisateur "
                        "WHERE pseudo = %(pseudo)s; ",
                        {"pseudo": pseudo},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not row:
            return None
        return Utilisateur(
            id=row["id"], pseudo=row["pseudo"], password_hash=row["password_hash"]
        )

    @log
    def get_hash_par_pseudo(self, pseudo: str) -> str | None:
        """Renvoie le hash du mot de passe (ou None si absent)"""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT password_hash FROM utilisateur "
                        "WHERE pseudo = %(pseudo)s; ",
                        {"pseudo": pseudo},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            return None
        return row["password_hash"] if row else None

    @log
    def lister_tous(self) -> list[Utilisateur]:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, pseudo, password_hash FROM utilisateur; "
                    )
                    rows = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [
            Utilisateur(id=r["id"], pseudo=r["pseudo"], password_hash=r["password_hash"])
            for r in rows or []
        ]

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM utilisateur WHERE id = %(id)s; ",
                        {"id": utilisateur.id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise
        return res > 0