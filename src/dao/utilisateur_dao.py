import logging

from utils.singleton import Singleton
from utils.log_decorator import log
from utils.securite import hash_password
from utils.securite import verifier_mot_de_passe

from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class Utilisateur_DAO(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Utilisateurs de la base de données"""

    @log
    def creer_utilisateur(self, utilisateur) -> bool:
        """Creation d'un utilisateur dans la base de données

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        created : bool
            True si la création est un succès
            False sinon
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO utilisateur(pseudo, mdp) VALUES         "
                        "(%(pseudo)s, %(mdp)s)                               "
                        " RETURNING id;                                      ",
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": hash_password(utilisateur.mdp),
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            utilisateur.id = res["id"]
            created = True

        return created

    @log
    def se_connecter(self, pseudo, mdp) -> Utilisateur:
        """se connecter grâce à son pseudo et son mot de passe

        Parameters
        ----------
        pseudo : str
            pseudo du joueur que l'on souhaite trouver
        mdp : str
            mot de passe du joueur

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur que l'on cherche
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM utilisateur                 "
                        " WHERE pseudo = %(pseudo)s;        ",
                        {"pseudo": pseudo},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        utilisateur = None

        if res:
            try:
                if verifier_mot_de_passe(mdp, hash_password(mdp)):
                    # Mot de passe correct
                    utilisateur = Utilisateur(
                        pseudo=res["pseudo"],
                        id=res["id"],
                    )
            except Exception as e:
                logging.info(f"Erreur vérification mot de passe: {e}")

        return utilisateur

    @log
    def get_par_id(self, id: int) -> Utilisateur:
        """trouver un utilisateur grace à son id

        Parameters
        ----------
        id : int
            numéro id de l'utilisateur que l'on souhaite trouver

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur que l'on cherche par id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM utilisateur                 "
                        " WHERE id = %(id)s;  ",
                        {"id": id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                id=res["id"],
            )

        return utilisateur

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Utilisateur:
        """trouver un utilisateur grace à son pseudo

        Parameters
        ----------
        pseudo : string
            pseudo de l'utilisateur que l'on souhaite trouver

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur que l'on cherche par pseudo
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM utilisateur                 "
                        " WHERE pseudo = %(pseudo)s;  ",
                        {"pseudo": pseudo},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                id=res["id"],
            )

        return utilisateur

    @log
    def supprimer(self, utilisateur) -> bool:
        """Suppression d'un utilisateur dans la base de données

        Parameters
        ----------
        utilisateur : Utilisateur
            utilisateur à supprimer de la base de données

        Returns
        -------
            True si l'utilisateur a bien été supprimé
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Supprimer le compte d'un utilisateur
                    cursor.execute(
                        "DELETE FROM utilisateur                   WHERE id=%(id)s      ",
                        {"id": utilisateur.id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise
        return res > 0
    
    @log
    def heures_utilisation(id: int) -> float:
        """
        Donne une approximation du temps passé sur l'application par un utilisateur.

        Parameters
        ----------
        id : int
            L'identifiant de l'utilisateur dans la base de données.

        Returns
        -------
        float
            Estimation du temps total passé sur l'application (en heures).
        """

        res = None  # toujours bien déclaré avant le try

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT SUM(EXTRACT(EPOCH FROM (deconnexion - connexion)) / 3600) AS total_heures
                        FROM session
                        WHERE id = %(id)s
                        AND deconnexion IS NOT NULL;
                        """,
                        {"id": id},
                    )
                    res = cursor.fetchone()

        except Exception as e:
            logging.error(
                f"Erreur lors du calcul des heures d'utilisation pour l'utilisateur {id}:{e}"
            )
            raise

        if res and res["total_heures"] is not None:
            return float(res["total_heures"])
        else:
            return 0.0
