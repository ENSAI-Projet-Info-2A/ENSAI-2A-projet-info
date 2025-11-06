import logging
from datetime import datetime as Date
from typing import List

from business_object.conversation import Conversation
from business_object.echange import Echange
from dao.conversation_dao import ConversationDAO
from dao.prompt_dao import PromptDAO

logger = logging.getLogger(__name__)


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
            succes = ConversationDAO.renommer_conv(id_conversation, nouveau_titre)
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
        if id_utilisateur is None:
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")

        # Normaliser les entrées
        if isinstance(mot_cle, str):
            mot_cle = mot_cle.strip()
            if mot_cle == "":
                mot_cle = None

        try:
            if mot_cle is not None and date_recherche is not None:
                res = ConversationDAO.rechercher_conv_motC_et_date(
                    id_user=id_utilisateur, mot_cle=mot_cle, date=date_recherche
                )
                logger.info("Recherche combinée par mot-clé et date effectuée.")
            elif mot_cle is not None:
                res = ConversationDAO.rechercher_mot_clef(id_user=id_utilisateur, mot_clef=mot_cle)
                logger.info("Recherche par mot-clé effectuée.")
            elif date_recherche is not None:
                res = ConversationDAO.rechercher_date(id_user=id_utilisateur, date=date_recherche)
                logger.info("Recherche par date effectuée.")
            else:
                res = ConversationDAO.lister_conversations(id_user=id_utilisateur)
                logger.info("Aucun critère fourni, listing général.")

            return res or []

        except Exception as e:
            msg = str(e).lower()
            if "aucune conversation" in msg or "pas de messages" in msg:
                return []
            logger.error("Erreur lors de la recherche des conversations : %s", e)
            raise

    def lire_fil(id_conversation: int, decalage: int, limite: int):
        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")

        offset = max(0, int(decalage or 0))
        limit = max(1, int(limite or 20))

        try:
            # pagination/tri faits en SQL
            return ConversationDAO.lire_echanges(id_conversation, offset=offset, limit=limit) or []
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
            res = ConversationDAO.ajouter_participant(id_conversation, id_utilisateur, role)
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
            res = ConversationDAO.retirer_participant(id_conversation, id_utilisateur)
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
            echanges = ConversationDAO.lire_echanges(id_conversation, offset=0, limit=10000)
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

    def demander_assistant(self, message: str, options=None, id_conversation: int | None = None):
        """
        Envoie un message à l'assistant et reçoit une réponse du LLM.
        - Si une conversation est donnée, ajoute le message à son historique.
        - Récupère la réponse du modèle et la persiste (si possible).
        """
        from business_object.echange import Echange
        from client.llm_client import LLM_API

        if not message or not message.strip():
            raise ErreurValidation("Le message est requis.")

        logger.info("Assistant appelé avec le message : %s", message[:80])

        # Valeurs par défaut simples
        temperature = float(options.get("temperature", 0.7)) if options else 0.7
        top_p = float(options.get("top_p", 1.0)) if options else 1.0
        max_tokens = int(options.get("max_tokens", 512)) if options else 512
        stop = options.get("stop") if options and "stop" in options else None

        # Historique existant (si la conversation est connue)
        history = []
        if id_conversation:
            try:
                anciens = ConversationDAO.lire_echanges(id_conversation, offset=0, limit=1000) or []
                for e in anciens:
                    role = (
                        "assistant"
                        if getattr(e, "expediteur", "").lower() == "assistant"
                        else "user"
                    )
                    history.append({"role": role, "content": e.message})
            except Exception as e:
                logger.warning(
                    "Impossible de récupérer l'historique (conv=%s) : %s", id_conversation, e
                )

        # Ajouter le message utilisateur courant
        history.append({"role": "user", "content": message})

        # Appel au client LLM
        client = LLM_API()
        reponse = client.generate(
            history=[
                # Conversion vers Echange pour respecter l’API du client
                Echange(agent=h["role"], message=h["content"], agent_name=None)
                for h in history
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )

        # Création de l’objet Echange pour la réponse
        echange_assistant = Echange(
            id_conversation=id_conversation,
            expediteur="assistant",
            message=reponse.message,
            date_echange=Date.today(),
        )

        # Persistance du message utilisateur + réponse (si possible)
        if id_conversation:
            try:
                e_user = Echange(
                    id_conversation=id_conversation,
                    expediteur="user",
                    message=message,
                    date_echange=Date.today(),
                )
                if hasattr(ConversationDAO, "ajouter_echange"):
                    ConversationDAO.ajouter_echange(e_user)
                    ConversationDAO.ajouter_echange(echange_assistant)
                else:
                    logger.info("La DAO ne supporte pas encore l’ajout d’échanges.")
            except Exception as e:
                logger.warning("Échec de la persistance des échanges : %s", e)

        return echange_assistant
