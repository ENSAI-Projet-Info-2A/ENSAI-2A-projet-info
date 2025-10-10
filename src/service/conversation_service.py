from typing import List
from conversation import Conversation
from echange import Echange
from datetime import datetime as Date
from conversation_dao import ConversationDAO

class ValidationError(Exception):
    """Erreur levée quand les données reçues ne sont pas valides."""
    pass

class NotFoundError(Exception):
    """Levée quand une ressource n'existe pas."""
    pass

class ConversationService:

    def __init__(self, titre: str, personnalisation: str, owner_id: int):
        """
        Crée une nouvelle conversation.
        Parameters
        ----------
            titre : str
                le titre de la conversation
            personnalisation : str
                le nom du profil du LLM
            owner_id : int
                l'identifiant du créateur de la conversation

        Retourne l'objet Conversation.
        """
        if title is None:
            raise ValidationError("There is no title.")
        if len(title) > 255:
            raise ValidationError("Title too long (max 255 chars).")
        if personnalisation is None:
            raise ValidationError("There is no personalisation .")
        conv = self.dao.create_conversation(title, personnalisation, owner_id) #manque l'attribut id non ?
        logger.info("Created conversation id=%s", getattr(conv, "id", None))
        return conv 

    def acceder(self, id_conv: int) -> Conversation:
        """
        Permet d'accéder à la dernière conversation.
        Parameters
        ----------
            id_conv: int
                l'id de la conversation
        """
        if id_conv is None:
            raise ValidationError("There is no id_conv.")
        res = self.dao.get_conversation(id_conv)
        if res is None:
            raise NotFoundError("Conversation not found")
        return res

    def renommer_conv(self, id_conv: int, nouveau_nom: str) -> bool:
        pass

    def supprimer_conv(self, id_conv: int) -> bool:
        pass

    def lister_conv(self, id_user: int, limit: int) -> List[Conversation]:
        """
        Liste les conversations par updated_at descendant.
        """
        if id_user is None: 
            raise ValidationError("there is no id_user")
        if limit < 1 or limit > 100:
            raise ValidationError("limit must be between 1 and 200")
        return self.dao.list_conversations(id_user, limit=limit)


    def rechercher_conv(self, id_user: int, motcle: str, date: Date) -> List[Conversation]:
        pass

    def lire_fil(self, id_conv: int, offset: int, limit: int) -> List[Echange]:
        pass

    def rechercher_message(self, id_conv: int, motcle: str, date: Date) -> List[Echange]:
        pass

    def ajouter_utilisateur(self, id_conv: int, id_user: int, role: str) -> bool:
        pass

    def retirer_utilisateur(self, id_conv: int, id_user: int) -> bool:
        pass

    def mettre_a_jour_personnalisation(self, id_conv: int, personnalisation: str) -> bool:
        pass

    def exporter_conversation(self, id_conv: int, format: str) -> bool:
        pass

    def demander_assistant(self, message: str, options=None) -> Echange:
        pass