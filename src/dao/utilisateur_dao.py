import logging
from typing import Optional

from psycopg2.extras import RealDictCursor

from src.business_object.utilisateur import Utilisateur
from src.dao.db_connection import DBConnection
from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """
    Data Access Object (DAO) pour la gestion des utilisateurs.

    Cette classe encapsule toutes les opérations CRUD et les requêtes
    spécifiques relatives à la table ``utilisateurs`` de la base de données.
    Elle utilise un pattern Singleton afin que l'accès aux utilisateurs
    se fasse via une instance unique partagée dans l'application.

    Table concernée
    ----------------
    Table : ``utilisateurs``  
    Colonnes :
    - ``id`` (int) : identifiant unique
    - ``pseudo`` (str) : nom d'utilisateur, unique
    - ``mot_de_passe`` (str) : hash du mot de passe

    Notes
    -----
    - Le hash du mot de passe est **déjà calculé au niveau métier** (Business Object `Utilisateur`).
    - Le décorateur ``@log`` permet de tracer automatiquement l’appel des méthodes
      pour faciliter le debugging.
    """
    @log
    def creer_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """
        Crée un nouvel utilisateur en base de données.

        Le pseudo et le mot de passe doivent déjà être correctement préparés au niveau
        du service (pseudo normalisé, mot de passe hashé).

        Parameters
        ----------
        utilisateur : Utilisateur
            L’objet métier à insérer.

        Returns
        -------
        bool
            True si l'insertion a réussi et que l'id a été récupéré,
            False sinon.
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
        """
        Recherche un utilisateur par son identifiant.

        Parameters
        ----------
        id : int
            Identifiant recherché.

        Returns
        -------
        Utilisateur | None
            L'utilisateur correspondant, ou None s'il n'existe pas.
        """
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
        """
        Recherche un utilisateur à partir de son pseudo.

        Parameters
        ----------
        pseudo : str
            Le pseudo exact à rechercher (déjà normalisé en amont).

        Returns
        -------
        Utilisateur | None
            L'utilisateur correspondant, ou None s'il n'existe pas.
        """
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
        """
        Retourne la liste complète des utilisateurs enregistrés.

        Returns
        -------
        list[Utilisateur]
            Liste d'objets utilisateurs.
        """
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
        """
        Supprime un utilisateur de la base.

        Parameters
        ----------
        utilisateur : Utilisateur
            L'utilisateur à supprimer (l'id doit être défini).

        Returns
        -------
        bool
            True si la suppression a touché au moins une ligne,
            False sinon.
        """
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
        """
        Calcule le temps total d’utilisation (sessions fermées uniquement).

        Seules les sessions dont ``deconnexion`` n'est pas NULL sont prises en compte.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.

        Returns
        -------
        float
            Nombre total d'heures d'utilisation.
        """
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
        """
        Calcule le temps total d'utilisation en comptabilisant également
        la session actuellement ouverte (si elle existe).

        La durée d'une session ouverte est : ``NOW() - connexion``.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur.

        Returns
        -------
        float
            Nombre total d'heures d'utilisation toutes sessions confondues.
        """
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
