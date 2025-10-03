from business_object.statistiques import Statistiques


class Statistiques_Service:
    """
    Service pour gérer les statistiques des utilisateurs et des conversations
    """

    def stats_utilisateur(self, id_user: int) -> Statistiques:
        """
        Retourne les statistiques liées à un utilisateur donné

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur

        Returns
        -------
        Statistiques
        """
        pass

    def stats_conversation(self, id_conv: int) -> Statistiques:
        """
        Retourne les statistiques liées à une conversation donnée

        Parameters
        ----------
        id_conv : int
            Identifiant de la conversation

        Returns
        -------
        Statistiques
        """
        pass
