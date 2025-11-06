import logging
from typing import Optional

from psycopg2.extras import RealDictCursor

from src.business_object.utilisateur import Utilisateur
from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """Accès base de données pour les utilisateurs (table: utilisateurs)"""

    @log
    def creer_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """
        Insère l'utilisateur.
        On attend:
            - utilisateur.pseudo déjà normalisé en service
            - utilisateur.password_hash déjà calculé (BO/service)
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO utilisateurs(pseudo, mot_de_passe)
                        VALUES (%(pseudo)s, %(mot_de_passe)s)
                        RETURNING id;
                        """,
                        {
                            "pseudo": utilisateur.pseudo,
                            "mot_de_passe": utilisateur.password_hash,
                        },
                    )
                    res = cursor.fetchone()
        #except Exception as e:
        #    logging.info(e)
        except Exception as e:
            print("ERREUR SQL :", e)
            logging.info(e)

        if res:
            utilisateur.id = res["id"]
            return True
        return False

    @log
    def trouver_par_id(self, id: int) -> Optional[Utilisateur]:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, pseudo, mot_de_passe
                        FROM utilisateurs
                        WHERE id = %(id)s;
                        """,
                        {"id": id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not res:
            return None

        return Utilisateur(
            id=res["id"],
            pseudo=res["pseudo"],
            password_hash=res["mot_de_passe"],
        )

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Optional[Utilisateur]:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, pseudo, mot_de_passe
                        FROM utilisateurs
                        WHERE pseudo = %(pseudo)s;
                        """,
                        {"pseudo": pseudo},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not res:
            return None

        return Utilisateur(
            id=res["id"],
            pseudo=res["pseudo"],
            password_hash=res["mot_de_passe"],
        )

    @log
    def lister_tous(self) -> list[Utilisateur]:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, pseudo, mot_de_passe FROM utilisateurs;")
                    rows = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [
            Utilisateur(id=row["id"], pseudo=row["pseudo"], password_hash=row["mot_de_passe"])
            for row in rows
        ]

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM utilisateurs WHERE id = %(id)s;",
                        {"id": utilisateur.id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise

        return res > 0

    @log
    def heures_utilisation(self, user_id: int) -> float:
        """Somme des sessions terminées (en heures)."""
        try:
            with DBConnection().connection as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT COALESCE(
                          SUM(EXTRACT(EPOCH FROM (deconnexion - connexion))) / 3600.0, 0
                        ) AS total_heures
                        FROM sessions
                        WHERE user_id = %(uid)s
                          AND deconnexion IS NOT NULL;
                        """,
                        {"uid": user_id},
                    )
                    row = cur.fetchone()
                    return float(row["total_heures"] or 0.0)
        except Exception:
            logging.exception("Erreur heures_utilisation")
            raise

    @log
    def heures_utilisation_incl_courante(self, user_id: int) -> float:
        """Somme des sessions en tenant compte de la session en cours (NOW())."""
        try:
            with DBConnection().connection as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT COALESCE(
                          SUM(EXTRACT(EPOCH FROM (COALESCE(deconnexion, NOW()) - connexion))) / 3600.0, 0
                        ) AS total_heures
                        FROM sessions
                        WHERE user_id = %(uid)s;
                        """,
                        {"uid": user_id},
                    )
                    row = cur.fetchone()
                    return float(row["total_heures"] or 0.0)
        except Exception:
            logging.exception("Erreur heures_utilisation_incl_courante")
            raise
