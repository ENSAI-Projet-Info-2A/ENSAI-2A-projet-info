import logging

from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connection import DBConnection

from business_object.utilisateur import Utilisateur

class Utilisateur_DAO(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Utilisateurs de la base de données"""

    @log
    def créer_utilisateur(self, utilisateur) -> bool
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
        pass

    def get_par_id(self, id: int) -> Utilisateur
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
        pass

    def trouver_par_pseudo(self, pseudo: string) -> Utilisateur
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
        pass

    def supprimer(self, utilisateur) -> bool
        """Suppression d'un utilisateur dans la base de données

        Parameters
        ----------
        utilisateur : Utilisateur
            utilisateur à supprimer de la base de données

        Returns
        -------
            True si l'utilisateur a bien été supprimé
        """
        pass

    def get_hash_par_pseudo(self, pseudo: string) : string
    """A voir plus tard si utile à garder ou non"""
        pass