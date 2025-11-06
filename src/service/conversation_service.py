print("HEREEEE")

import logging
from datetime import datetime as Date
from typing import List

from business_object.conversation import Conversation
from business_object.echange import Echange
from dao.conversation_dao import ConversationDAO

print("ici")

from dao.prompt_dao import PromptDAO

logger = logging.getLogger(__name__)

print("Load - Conversation service : import")


class ErreurValidation(Exception):
    """Erreur levée quand les données reçues ne sont pas valides."""

    pass


class ErreurNonTrouvee(Exception):
    """Levée quand une ressource n'existe pas."""

    pass


class ConversationService:
    @staticmethod
    def _resolve_prompt_id(personnalisation):
        # Accepte None, "", "  "  => pas de prompt
        if personnalisation is None or (
            isinstance(personnalisation, str) and not personnalisation.strip()
        ):
            return None
        # Si int : vérifier qu'il existe
        if isinstance(personnalisation, int):
            if not PromptDAO.exists_id(personnalisation):
                raise ErreurValidation(f"prompt_id inexistant: {personnalisation}")
            return personnalisation
        # Si str : résoudre le nom -> id
        pid = PromptDAO.get_id_by_name(personnalisation.strip())
        if pid is None:
            raise ErreurValidation(f"Prompt inconnu: '{personnalisation}'")
        return pid

    @staticmethod
    def creer_conv(titre: str, personnalisation, id_proprietaire: int | None = None) -> str:
        if not titre or not str(titre).strip():
            raise ErreurValidation("Le titre est nécessaire.")
        if len(titre) > 255:
            raise ErreurValidation("Le titre est trop long (maximum 255 caractères).")

        # Normaliser vide -> None
        if isinstance(personnalisation, str) and not personnalisation.strip():
            personnalisation = None

        conv = Conversation(nom=str(titre).strip(), personnalisation=personnalisation)

        try:
            conv = ConversationDAO.creer_conversation(conv)

            # Rattacher l'utilisateur comme participant si fourni
            if id_proprietaire is not None:
                try:
                    ConversationDAO.ajouter_participant(
                        conversation_id=conv.id, id_user=id_proprietaire, role="proprietaire"
                    )
                except Exception as e:
                    # On loggue mais on n’empêche pas la création de la conversation
                    logger.warning(
                        "Ajout participant échoué (conv=%s, user=%s) : %s",
                        conv.id,
                        id_proprietaire,
                        e,
                    )

            logger.info("Conversation créée id=%s (prompt_id=%r)", conv.id, conv.personnalisation)
            return f"Conversation '{conv.nom}' créée (id={conv.id})."

        except ValueError as e:
            raise ErreurValidation(str(e)) from e
        except Exception as e:
            logger.error("Erreur création conversation: %s", e)
            raise

    def acceder_conversation(id_conversation: int):
        """Permet d'accéder à une conversation existante."""
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        try:
            conversation = ConversationDAO.trouver_par_id(id_conv=id_conversation)
            if conversation is None:
                raise ErreurNonTrouvee("Conversation introuvable.")
            logger.info(
                f"conversation d'id = {conversation.id} intitulée {conversation.nom} trouvée",
                conversation.id,
                conversation.nom,
            )
            return conversation
        except ErreurNonTrouvee:
            raise
        except ErreurValidation:
            raise
        except Exception as e:
            logger.error(
                "erreur lors de la recherche de la conversation d'id = %s : %s", id_conversation, e
            )
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
            succes = ConversationDAO.supprimer_conv(id_conv=id_conversation)
            if succes:
                logger.info("Conversation %s supprimée avec succès", id_conversation)
            else:
                logger.warning(
                    "Aucune conversation trouvée à supprimer pour id=%s", id_conversation
                )
            return succes
        except Exception as e:
            logger.error(
                "Erreur lors de la suppression de la conversation %s : %s", id_conversation, e
            )
            raise

    def lister_conversations(id_utilisateur: int, limite=None) -> List["Conversation"]:
        """Liste les conversations d'un utilisateur. Renvoie [] s'il n'y en a pas."""
        if id_utilisateur is None:
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")
        if limite is not None and limite < 1:
            raise ErreurValidation("La limite doit être plus grande ou égale à 1.")

        try:
            res = ConversationDAO.lister_conversations(id_user=id_utilisateur, n=limite)
            # Si la DAO renvoie une liste, on la passe telle quelle
            return res or []
        except Exception as e:
            # La DAO lève actuellement une Exception quand aucun résultat.
            # On transforme proprement en liste vide pour la vue.
            msg = str(e).lower()
            if "aucune conversation trouvée" in msg or "aucune conversation" in msg:
                return []
            # Autre erreur = vraie erreur
            logger.error(
                "Erreur lors de la récupération des conversations de l'utilisateur %s : %s",
                id_utilisateur,
                e,
            )
            raise

    def rechercher_conversations(
        id_utilisateur: int, mot_cle=None, date_recherche=None
    ) -> List["Conversation"]:
        """Recherche des conversations selon un mot-clé et une date."""
        if id_utilisateur is None:
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")

        try:
            if mot_cle and date_recherche:
                # Appel d'une méthode DAO combinant les deux critères
                res = ConversationDAO.rechercher_conv_motC_et_date(
                    id_user=id_utilisateur, mot_cle=mot_cle, date=date_recherche
                )
                logger.info("Recherche combinée par mot-clé et date effectuée.")

            elif mot_cle and not date_recherche:
                res = ConversationDAO.rechercher_mot_clef(id_user=id_utilisateur, mot_clef=mot_cle)
                logger.info("Recherche par mot-clé effectuée.")

            elif date_recherche and not mot_cle:
                res = ConversationDAO.rechercher_date(id_user=id_utilisateur, date=date_recherche)
                logger.info("Recherche par date effectuée.")

            else:
                res = ConversationDAO.lister_conversations(id_user=id_utilisateur)
                logger.info("Aucun critère fourni, listing général.")

            if res:
                logger.info("Conversations trouvées pour %s", id_utilisateur)
                return res
            else:
                logger.warning("Aucune conversation trouvée pour %s", id_utilisateur)
                return []
        except Exception as e:
            logger.error("Erreur lors de la recherche des conversations : %s", e)
            raise

    def lire_fil(id_conversation: int, decalage: int, limite: int):
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")

        # petites sécurités
        decalage = max(0, int(decalage or 0))
        limite = max(1, int(limite or 20))

        try:
            # La DAO n’a pas d’offset: on récupère un peu plus et on tranche côté Python
            brut = ConversationDAO.lire_echanges(id_conversation, limite + decalage)
            if not brut:
                logger.warning(f"Aucun échange trouvé pour la conversation {id_conversation}")
                return []

            return brut[decalage : decalage + limite]
        except Exception as e:
            logger.error(
                "Erreur lors de la lecture du fil de la conversation %s : %s", id_conversation, e
            )
            raise

    def rechercher_message(
        id_conversation: int, mot_cle: str, date_recherche: Date
    ) -> List["Echange"]:
        """Recherche un message dans une conversation."""
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not mot_cle and not date_recherche:
            raise ErreurValidation("Un mot-clé ou une date doivent être fournis.")
        try:
            res = ConversationDAO.rechercher_message(id_conversation, mot_cle, date_recherche)
            if res:
                logger.info(
                    f"Messages trouvés dans la conversation {id_conversation} (mot-clé: {mot_cle})"
                )
                return res
            else:
                logger.warning(
                    f"Aucun message trouvé dans la conversation {id_conversation} avec les critères donnés."
                )
        except Exception as e:
            logger.error(
                "Erreur lors de la recherche de messages dans la conversation %s : %s",
                id_conversation,
                e,
            )
            raise

    def ajouter_utilisateur(id_conversation: int, id_utilisateur: int, role: str) -> bool:
        """Ajoute un utilisateur à une conversation."""
        if not id_conversation or not id_utilisateur or not role:
            raise ErreurValidation(
                "Les champs id_conversation, id_utilisateur et rôle sont requis."
            )
        try:
            res = ConversationDAO.ajouter_utilisateur(id_conversation, id_utilisateur, role)
            if res:
                logger.info(
                    f"Utilisateur {id_utilisateur} ajouté à la conversation {id_conversation} avec le rôle {role}"
                )
                return res
            else:
                logger.warning(
                    f"Échec de l’ajout de l’utilisateur {id_utilisateur} à la conversation {id_conversation}"
                )
        except Exception as e:
            logger.error(
                "Erreur lors de l’ajout de l’utilisateur %s à la conversation %s : %s",
                id_utilisateur,
                id_conversation,
                e,
            )
            raise

    def retirer_utilisateur(id_conversation: int, id_utilisateur: int) -> bool:
        """Retire un utilisateur d'une conversation."""
        if not id_conversation or not id_utilisateur:
            raise ErreurValidation("Les champs id_conversation et id_utilisateur sont requis.")
        try:
            res = ConversationDAO.retirer_utilisateur(id_conversation, id_utilisateur)
            if res:
                logger.info(
                    f"Utilisateur {id_utilisateur} retiré de la conversation {id_conversation}"
                )
                return res
            else:
                logger.warning(
                    f"Aucun utilisateur {id_utilisateur} trouvé dans la conversation {id_conversation}"
                )
        except Exception as e:
            logger.error(
                "Erreur lors du retrait de l’utilisateur %s de la conversation %s : %s",
                id_utilisateur,
                id_conversation,
                e,
            )
            raise

    def mettre_a_jour_personnalisation(self, id_conversation: int, personnalisation: str) -> bool:
        """Met à jour le profil de personnalisation de la conversation."""
        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not personnalisation:
            raise ErreurValidation("Le champ personnalisation est requis.")
        try:
            succes = ConversationDAO.mettre_a_jour_personnalisation(
                id_conversation, personnalisation
            )
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
            logger.error(
                "Erreur lors de l'exportation de la conversation %s : %s", id_conversation, e
            )
            raise

    def demander_assistant(self, message: str, options=None):
        """Envoie un message à l'assistant et reçoit une réponse."""
        if not message or not message.strip():
            raise ErreurValidation("Le message est requis.")

        logger.info("Assistant appelé avec le message : %s", message[:50])

        reponse = f"Voici une réponse simulée à : {message[:50]}"

        echange = Echange(
            id_conversation=None, expediteur="assistant", message=reponse, date_echange=Date.today()
        )

        # self.dao.ajouter_echange(echange)
        return echange


print("Load : Conversation service")
