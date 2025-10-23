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
        if not id_conv:
            raise ValidationError("id_conv est requis")
        if not nouveau_nom or not nouveau_nom.strip():
            raise ValidationError("Le nouveau nom est requis")

        try:
            success = self.dao.renommer_conv(id_conv, nouveau_nom)
            if success:
                logger.info("Conversation %s renommée en '%s'", id_conv, nouveau_nom)
            else:
                logger.warning("Aucune conversation trouvée pour id_conv=%s", id_conv)
            return success
        except Exception as e:
            logger.error("Erreur lors du renommage de la conversation %s : %s", id_conv, e)
            raise

    def supprimer_conv(self, id_conv: int) -> bool:
        if not id_conv:
            raise ValidationError("id_conv est requis")

        try:
            success = self.dao.supprimer_conv(id_conv)
            if success:
                logger.info("Conversation %s supprimée avec succès", id_conv)
            else:
                logger.warning("Aucune conversation trouvée à supprimer pour id_conv=%s", id_conv)
            return success
        except Exception as e:
            logger.error("Erreur lors de la suppression de la conversation %s : %s", id_conv, e)
            raise

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
        if id_user is None:
            raise ValidationError("there is no id_user")
        return self.dao.rechercher_conv(id_user, motcle, date)

    def lire_fil(self, id_conv: int, offset: int, limit: int) -> List[Echange]:
        if id_conv is None:
            raise ValidationError("id_conv is required")
        return self.dao.lire_fil(id_conv, offset, limit)

    def rechercher_message(self, id_conv: int, motcle: str, date: Date) -> List[Echange]:
        if id_conv is None:
            raise ValidationError("id_conv is required")
        if not motcle and not date:
            raise ValidationError("motcle or date must be provided")
        return self.dao.rechercher_message(id_conv, motcle, date)

    def ajouter_utilisateur(self, id_conv: int, id_user: int, role: str) -> bool:
        if not id_conv or not id_user or not role:
            raise ValidationError("id_conv, id_user and role are required")
        return self.dao.ajouter_utilisateur(id_conv, id_user, role)

    def retirer_utilisateur(self, id_conv: int, id_user: int) -> bool:
        if not id_conv or not id_user:
            raise ValidationError("id_conv and id_user are required")
        return self.dao.retirer_utilisateur(id_conv, id_user)

    def mettre_a_jour_personnalisation(self, id_conv: int, personnalisation: str) -> bool:
        if not id_conv:
            raise ValidationError("id_conv est requis")
        if not personnalisation:
            raise ValidationError("le champ personnalisation est requis")

        try:
            success = self.dao.mettre_a_jour_personnalisation(id_conv, personnalisation)
            if success:
                logger.info("Personnalisation mise à jour pour la conversation %s", id_conv)
            return success
        except Exception as e:
            logger.error("Erreur lors de la mise à jour de la personnalisation : %s", e)
            raise


    def exporter_conversation(self, id_conv: int, format: str) -> bool:
        if not id_conv:
            raise ValidationError("id_conv est requis")
        if format not in ("json"): # le seul format nécéssaire ?
            raise ValidationError("format non supporté")
        try:
            echanges = self.dao.lire_fil(id_conv, offset=0, limit=10000)  # récupère tous les messages
            if format == "json":
                import json
                with open(f"conversation_{id_conv}.json", "w", encoding="utf-8") as f:
                    json.dump([e.__dict__ for e in echanges], f, ensure_ascii=False, indent=2)

            logger.info("Conversation %s exportée en %s", id_conv, format)
            return True
        except Exception as e:
            logger.error("Erreur d'export pour la conversation %s : %s", id_conv, e)
            raise

    def demander_assistant(self, message: str, options=None) -> Echange:
        if not message or not message.strip():
            raise ValidationError("le message est requis")

        logger.info("Assistant appelé avec message: %s", message[:50])

        reponse = f"Voici une réponse simulée à: {message[:50]}"

        # Créer un objet Echange (tu dois avoir une classe Echange définie quelque part)
        echange = Echange(
            id_conv=None,        # pas forcément lié à une conversation
            sender="assistant",
            message=reponse,
            date_echange=date.today()
        )

        # Si tu veux, tu peux stocker ce message dans la BDD
        # self.dao.ajouter_echange(echange)

        return echange