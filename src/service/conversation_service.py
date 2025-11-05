from typing import List
from business_object.conversation import Conversation
from business_object.echange import Echange
from datetime import datetime as Date
from dao.conversation_dao import ConversationDAO

class ErreurValidation(Exception):
    """Erreur levée quand les données reçues ne sont pas valides."""
    pass

class ErreurNonTrouvee(Exception):
    """Levée quand une ressource n'existe pas."""
    pass

class ConversationService:

    def creer_conv(titre: str, personnalisation: str, id_proprietaire: int):
        """
        Crée une nouvelle conversation.

        Paramètres
        ----------
            titre : str
                Le titre de la conversation.
            personnalisation : str
                Le nom du profil du LLM.
            id_proprietaire : int
                L'identifiant du créateur de la conversation.

        Retourne
        --------
            Message de succès de l'implémentation dans la DAO
        """
        if titre is None:
            raise ErreurValidation("Le titre est nécéssaire.")
        if len(titre) > 255:
            raise ErreurValidation("Le titre est trop long (maximum 255 caractères).")
        if personnalisation is None:
            raise ErreurValidation("La personnalisation est obligatoire.")
        conv = Conversation(nom = titre, personnalisation=personnalisation,id = id_proprietaire )
        try :
            res = ConversationDAO.creer_conversation(conv)
            if not res: 
                raise Exception("l'implémentation de la conversation dans la base de donnée a échouée")
            
            logger.info("Conversation créée avec id=%s", getattr(conv, "id", None))
            
            return(f"conversation {titre} créée (id propriétaire = {id_proprietaire})")
        
        except Exception as e:
            logger.error("erreur lors de la création de la conversation : %s", e)
            raise

    def acceder_conversation(id_conversation: int):
        """Permet d'accéder à une conversation existante."""
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        try:
            conversation = ConversationDAO.trouver_par_id(id_conv = id_conversation)
            if conversation is None:
                raise ErreurNonTrouvee("Conversation introuvable.")
            logger.info(f"conversation d'id = {conversation.id} intitulée {conversation.nom} trouvée", conversation.id, conversation.nom)
            return conversation
        except ErreurNonTrouvee:
            raise
        except ErreurValidation:
            raise
        except Exception as e: 
            logger.error("erreur lors de la recherche de la conversation d'id = %s : %s",id_conversation, e)
            raise Exception("erreur interne lors de la recherche de la conversation.") from e

    def renommer_conversation(id_conversation: int, nouveau_titre: str):
        """Renomme une conversation existante."""
        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not nouveau_titre or not nouveau_titre.strip():
            raise ErreurValidation("Le nouveau titre est requis.")

        try:
            succes = ConversationDAO.renommer_conversation(id_conversation, nouveau_titre)
            if succes:
                logger.info("Conversation %s renommée en '%s'", id_conversation, nouveau_titre)
            else:
                logger.warning("Aucune conversation trouvée pour id=%s", id_conversation)
            return succes
        except Exception as e:
            logger.error("Erreur lors du renommage de la conversation %s : %s", id_conversation, e)
            raise

    def supprimer_conversation(id_conversation: int) -> bool:
        """Supprime une conversation existante."""
        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        try:
            succes = ConversationDAO.supprimer_conv(id_conv = id_conversation)
            if succes:
                logger.info("Conversation %s supprimée avec succès", id_conversation)
            else:
                logger.warning("Aucune conversation trouvée à supprimer pour id=%s", id_conversation)
            return succes
        except Exception as e:
            logger.error("Erreur lors de la suppression de la conversation %s : %s", id_conversation, e)
            raise

    def lister_conversations(id_utilisateur: int, limite=None) -> List['Conversation']:
        """Liste n conversations de la """
        if id_utilisateur is None: 
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")
        if limite < 1 or limite > 100:
            raise ErreurValidation("La limite doit être comprise entre 1 et 100.")
        try:
            res = ConversationDAO.lister_conversations(id_user = id_utilisateur, n=limite)
            if res:
                logger.info(f"Conversations de {id_utilisateur} listées avec succès")
                return res
            else:
                logger.warning(f"Aucune conversation trouvée pour l'id {id_utilisateur}")
        except Exception as e:
            logger.error("Erreur lors de la récupération des conversations de l'utilisateur %s : %s", id_utilisateur, e)
            raise
                

    def rechercher_conversations(id_utilisateur: int, mot_cle: str, date_recherche: date) -> List['Conversation']:
        """Recherche des conversations selon un mot-clé et une date."""
        if id_utilisateur is None:
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")
        return ConversationDAO.rechercher_conversation(id_utilisateur, mot_cle, date_recherche)

    def lire_fil(id_conversation: int, decalage: int, limite: int) -> List['Echange']:
        """Lit les échanges d'une conversation avec pagination."""
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        return ConversationDAO.lire_fil(id_conversation, decalage, limite)

    def rechercher_message(self, id_conversation: int, mot_cle: str, date_recherche: date) -> List['Echange']:
        """Recherche un message dans une conversation."""
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not mot_cle and not date_recherche:
            raise ErreurValidation("Un mot-clé ou une date doivent être fournis.")
        return ConversationDAO.rechercher_message(id_conversation, mot_cle, date_recherche)

    def ajouter_utilisateur(self, id_conversation: int, id_utilisateur: int, role: str) -> bool:
        """Ajoute un utilisateur à une conversation."""
        if not id_conversation or not id_utilisateur or not role:
            raise ErreurValidation("Les champs id_conversation, id_utilisateur et rôle sont requis.")
        return ConversationDAO.ajouter_utilisateur(id_conversation, id_utilisateur, role)

    def retirer_utilisateur(self, id_conversation: int, id_utilisateur: int) -> bool:
        """Retire un utilisateur d'une conversation."""
        if not id_conversation or not id_utilisateur:
            raise ErreurValidation("Les champs id_conversation et id_utilisateur sont requis.")
        return ConversationDAO.retirer_utilisateur(id_conversation, id_utilisateur)

    def mettre_a_jour_personnalisation(self, id_conversation: int, personnalisation: str) -> bool:
        """Met à jour le profil de personnalisation de la conversation."""
        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not personnalisation:
            raise ErreurValidation("Le champ personnalisation est requis.")
        try:
            succes = ConversationDAO.mettre_a_jour_personnalisation(id_conversation, personnalisation)
            if succes:
                logger.info("Personnalisation mise à jour pour la conversation %s", id_conversation)
            return succes
        except Exception as e:
            logger.error("Erreur lors de la mise à jour de la personnalisation : %s", e)
            raise

    def exporter_conversation(self, id_conversation: int, format_: str) -> bool:
        """Exporte la conversation dans un fichier (actuellement au format JSON uniquement)."""
        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if format_ not in ("json",):
            raise ErreurValidation("Format non supporté.")
        try:
            echanges = ConversationDAO.lire_fil(id_conversation, decalage=0, limite=10000)
            if format_ == "json":
                import json
                with open(f"conversation_{id_conversation}.json", "w", encoding="utf-8") as fichier:
                    json.dump([e.__dict__ for e in echanges], fichier, ensure_ascii=False, indent=2)

            logger.info("Conversation %s exportée en %s", id_conversation, format_)
            return True
        except Exception as e:
            logger.error("Erreur lors de l'exportation de la conversation %s : %s", id_conversation, e)
            raise

    def demander_assistant(self, message: str, options=None):
        """Envoie un message à l'assistant et reçoit une réponse."""
        if not message or not message.strip():
            raise ErreurValidation("Le message est requis.")

        logger.info("Assistant appelé avec le message : %s", message[:50])

        reponse = f"Voici une réponse simulée à : {message[:50]}"

        echange = Echange(
            id_conversation=None,
            expediteur="assistant",
            message=reponse,
            date_echange=date.today()
        )

        # self.dao.ajouter_echange(echange)
        return echange