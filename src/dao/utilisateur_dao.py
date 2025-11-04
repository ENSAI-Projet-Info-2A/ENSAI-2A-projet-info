import logging
import bcrypt

from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connection import DBConnection

from business_object.utilisateur import Utilisateur

class Utilisateur_DAO(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Utilisateurs de la base de données"""

    @log
    def créer_utilisateur(self, utilisateur) -> bool:
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
        mdp_hash = bcrypt.hashpw(
            utilisateur.mdp.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO utilisateur(pseudo, mdp) VALUES         "
                        "(%(pseudo)s, %(mdp)s)                               "
                        " RETURNING id;                                     ",
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": mdp_hash,
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
            # Vérifier le mot de passe avec bcrypt
            mdp_hash_stocke = res["mdp"]
            try:
                if bcrypt.checkpw(mdp.encode('utf-8'), mdp_hash_stocke.encode('utf-8')):
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
                        "  FROM utilisateur                      "
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
                        "  FROM utilisateur                      "
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
                        "DELETE FROM utilisateur                  "
                        " WHERE id=%(id)s      ",
                        {"id": utilisateur.id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise

        return res > 0

    @log
    def get_hash_par_pseudo(self, mdp_hash: str) -> Utilisateur:
        """Récupère un utilisateur à partir du hash de son mot de passe

        Parameters
        ----------
        mdp_hash : str
            Le hash du mot de passe à rechercher

        Returns
        -------
        Utilisateur
            L'utilisateur correspondant au hash (avec son id et pseudo)
            None si aucun utilisateur ne correspond à ce hash
        
        Raises
        ------
        Exception
            En cas d'erreur lors de la requête SQL
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, pseudo     "
                        "  FROM utilisateur                 "
                        " WHERE mdp = %(mdp_hash)s;         ",
                        {"mdp_hash": mdp_hash}
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
                        {"id": id}
                    )
                    res = cursor.fetchone()

        except Exception as e:
            logging.error(f"Erreur lors du calcul des heures d'utilisation pour l'utilisateur {id}:{e}")
            raise

        if res and res["total_heures"] is not None:
            return float(res["total_heures"])
        else:
            return 0.0

