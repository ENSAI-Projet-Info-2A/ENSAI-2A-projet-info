from src.business_object.statistiques import Statistiques
from src.dao.conversation_dao import ConversationDAO
from src.dao.utilisateur_dao import UtilisateurDao


class Statistiques_Service:
    """
    Service pour gérer les statistiques des utilisateurs et des conversations
    """

    def __init__(self):
        self.conv_dao = ConversationDAO()
        self.user_dao = UtilisateurDao()

    def stats_utilisateur(self, id_user: int) -> Statistiques:
        """
        Retourne les statistiques liées à un utilisateur donné

        Calcule:
          - nb_conversations : len(lister_conversations(id_user))
          - nb_messages      : somme(len(lire_echanges(conv.id))) sur ses conversations
          - sujets_plus_frequents : titres/nom des conversations (approx)
          - heures_utilisation : 0.0 (pas d'implémentation directe ici)

        Parameters
        ----------
        id_user : int
            Identifiant de l'utilisateur

        Returns
        -------
        Statistiques
        """
        stats = Statistiques()
        if id_user is None:
            return stats

        # 1) Compter les conversations via DAO :
        nb_convs = int(self.conv_dao.compter_conversations(id_user))
        stats.incrementer_conversations(nb_convs)

        # 1) Compter les messages via DAO :
        nb_msgs = int(self.conv_dao.compter_message_user(id_user))
        stats.incrementer_messages(nb_msgs)

        # 3) Top sujet :
        convs = self.conv_dao.lister_conversations(id_user) or []
        titres = [c.nom for c in convs if c.nom]
        stats.ajouter_sujets(titres)

        # 4) Heures d'utilisation (en incluant la session en cours)
        heures = float(self.user_dao.heures_utilisation_incl_courante(id_user))
        stats.ajouter_temps(heures)

        return stats

    # Inutile ou à repenser
    #
    # def stats_conversation(self, id_conv: int) -> Statistiques:
    #     """
    #     Retourne les statistiques liées à une conversation donnée

    #     Calcule:
    #         - Nb de message
    #         - ?

    #     Parameters
    #     ----------
    #     id_conv : int
    #         Identifiant de la conversation

    #     Returns
    #     -------
    #     Statistiques
    #     """
