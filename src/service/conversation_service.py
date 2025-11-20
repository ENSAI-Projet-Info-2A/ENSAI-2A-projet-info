import logging
from datetime import datetime as Date
from pathlib import Path
from typing import List

from src.business_object.conversation import Conversation
from src.business_object.echange import Echange
from src.dao.conversation_dao import ConversationDAO
from src.dao.prompt_dao import PromptDAO


class ErreurValidation(Exception):
    """Erreur levée quand les données reçues ne sont pas valides."""

    pass


class ErreurNonTrouvee(Exception):
    """Levée quand une ressource n'existe pas."""

    pass


class ConversationService:
    """
    Service métier pour la gestion des conversations et des échanges avec un assistant.

    Fournit des méthodes pour :
    - Créer, accéder, renommer, supprimer et lister des conversations.
    - Ajouter ou retirer des participants.
    - Rechercher des conversations ou des messages.
    - Lire le fil de messages d’une conversation.
    - Mettre à jour la personnalisation d’une conversation (prompt associé).
    - Exporter une conversation (actuellement JSON).
    - Interagir avec un assistant virtuel (LLM) et stocker les échanges.

    Attributs de classe
    -------------------
    DEFAULT_SYSTEM_PROMPT : str
        Texte par défaut à utiliser comme prompt système si aucune personnalisation n’est définie.
    """

    DEFAULT_SYSTEM_PROMPT = "Tu es un assistant utile."  # <- Pour la dernière fonction.

    @staticmethod
    def _resolve_prompt_id(personnalisation):
        """
        Résout un identifiant de prompt à partir de différentes entrées possibles.

        Parameters
        ----------
        personnalisation : int | str | None
            - None, "", "  " => pas de prompt
            - int => id du prompt, vérifié dans la base
            - str => nom du prompt, résolu en id via la DAO

        Returns
        -------
        int | None
            L’identifiant du prompt ou None si aucune personnalisation.

        Raises
        ------
        ErreurValidation
            Si le prompt n’existe pas.
        """
        logging.debug("Résolution du prompt_id pour personnalisation=%r", personnalisation)

        # Accepte None, "", "  "  => pas de prompt
        if personnalisation is None or (
            isinstance(personnalisation, str) and not personnalisation.strip()
        ):
            logging.debug("Aucune personnalisation fournie, retour None.")
            return None
        # Si int : vérifier qu'il existe
        if isinstance(personnalisation, int):
            if not PromptDAO.exists_id(personnalisation):
                logging.warning("prompt_id inexistant demandé: %s", personnalisation)
                raise ErreurValidation(f"prompt_id inexistant: {personnalisation}")
            logging.debug("Prompt_id %s résolu directement (int).", personnalisation)
            return personnalisation
        # Si str : résoudre le nom -> id
        pid = PromptDAO.get_id_by_name(personnalisation.strip())
        if pid is None:
            logging.warning("Prompt inexistant demandé par nom: %r", personnalisation)
            raise ErreurValidation(f"Prompt inconnu: '{personnalisation}'")
        logging.debug("Nom de prompt %r résolu en id=%s", personnalisation, pid)
        return pid

    DEFAULT_SYSTEM_PROMPT = "Tu es un assistant utile."

    @staticmethod
    def _resolve_system_prompt_for_conv(id_conversation: int | None) -> str:
        """
        Retourne le texte du prompt système à utiliser pour un LLM.

        Parameters
        ----------
        id_conversation : int | None
            Identifiant de la conversation. Si None, on renvoie le prompt par défaut.

        Returns
        -------
        str
            Texte du prompt système (personnalisé ou par défaut).
        """
        logging.debug(
            "Résolution du prompt système pour id_conversation=%r",
            id_conversation,
        )

        if not id_conversation:
            logging.debug(
                "Aucun id_conversation fourni pour le prompt système, utilisation du prompt par défaut."
            )
            return ConversationService.DEFAULT_SYSTEM_PROMPT

        try:
            conv = ConversationDAO.trouver_par_id(id_conv=id_conversation)
            prompt_id = getattr(conv, "personnalisation", None)
            if not prompt_id:
                logging.debug(
                    "Conversation %s sans personnalisation, utilisation du prompt par défaut.",
                    id_conversation,
                )
                return ConversationService.DEFAULT_SYSTEM_PROMPT

            from src.dao.prompt_dao import PromptDAO

            txt = PromptDAO.get_prompt_text_by_id(prompt_id)
            if txt:
                logging.debug(
                    "Prompt système personnalisé récupéré pour conv=%s (prompt_id=%s).",
                    id_conversation,
                    prompt_id,
                )
            else:
                logging.debug(
                    "Prompt_id=%s pour conv=%s sans texte, utilisation du prompt par défaut.",
                    prompt_id,
                    id_conversation,
                )
            return txt or ConversationService.DEFAULT_SYSTEM_PROMPT

        except Exception as e:
            logging.warning(
                "Impossible de résoudre le prompt système pour conv=%s, utilisation du prompt par défaut. Erreur: %s",
                id_conversation,
                e,
            )
            return ConversationService.DEFAULT_SYSTEM_PROMPT

    @staticmethod
    def creer_conv(titre: str, personnalisation, id_proprietaire: int | None = None) -> str:
        """
        Crée une nouvelle conversation et éventuellement rattache un utilisateur comme propriétaire.

        Parameters
        ----------
        titre : str
            Nom de la conversation (max 255 caractères)
        personnalisation : str | int | None
            Prompt associé à la conversation
        id_proprietaire : int | None
            Identifiant de l’utilisateur propriétaire (facultatif)

        Returns
        -------
        str
            Message de confirmation de création.

        Raises
        ------
        ErreurValidation
            Si le titre est absent ou trop long.
        """
        logging.debug(
            "Demande de création de conversation : titre=%r, personnalisation=%r, id_proprietaire=%r",
            titre,
            personnalisation,
            id_proprietaire,
        )

        if not titre or not str(titre).strip():
            raise ErreurValidation("Le titre est nécessaire.")
        if len(titre) > 255:
            raise ErreurValidation("Le titre est trop long (maximum 255 caractères).")

        # Normaliser vide -> None
        if isinstance(personnalisation, str) and not personnalisation.strip():
            personnalisation = None

        conv = Conversation(nom=str(titre).strip(), personnalisation=personnalisation)

        try:
            conv = ConversationDAO.creer_conversation(conv, proprietaire_id=id_proprietaire)

            if id_proprietaire is not None:
                try:
                    ConversationDAO.ajouter_participant(
                        conversation_id=conv.id, id_user=id_proprietaire, role="proprietaire"
                    )
                except Exception as e:
                    # On loggue mais on n’empêche pas la création de la conversation
                    logging.warning(
                        "Ajout participant échoué (conv=%s, user=%s) : %s",
                        conv.id,
                        id_proprietaire,
                        e,
                    )

            logging.info("Conversation créée id=%s (prompt_id=%r)", conv.id, conv.personnalisation)
            return f"Conversation '{conv.nom}' créée (id={conv.id})."

        except ValueError as e:
            raise ErreurValidation(str(e)) from e
        except Exception as e:
            logging.error("Erreur création conversation: %s", e)
            raise

    def acceder_conversation(id_conversation: int):
        """
        Récupère une conversation existante.

        Parameters
        ----------
        id_conversation : int
            Identifiant de la conversation à récupérer

        Returns
        -------
        Conversation
            Objet Conversation correspondant

        Raises
        ------
        ErreurValidation
            Si l’id est manquant.
        ErreurNonTrouvee
            Si la conversation n’existe pas.
        """
        logging.debug("Accès à la conversation id=%s", id_conversation)

        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        try:
            conversation = ConversationDAO.trouver_par_id(id_conv=id_conversation)
            if conversation is None:
                logging.warning("Conversation introuvable pour id=%s", id_conversation)
                raise ErreurNonTrouvee("Conversation introuvable.")
            logging.info(
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
            logging.error(
                "erreur lors de la recherche de la conversation d'id = %s : %s", id_conversation, e
            )
            raise Exception("erreur interne lors de la recherche de la conversation.") from e

    def renommer_conversation(id_conversation: int, nouveau_titre: str):
        """
        Renomme une conversation existante.

        Parameters
        ----------
        id_conversation : int
            Identifiant de la conversation
        nouveau_titre : str
            Nouveau nom de la conversation

        Returns
        -------
        bool
            True si renommage effectué, False sinon

        Raises
        ------
        ErreurValidation
            Si les paramètres sont invalides
        """
        logging.debug(
            "Demande de renommage de conversation id=%s vers nouveau_titre=%r",
            id_conversation,
            nouveau_titre,
        )

        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not nouveau_titre or not nouveau_titre.strip():
            raise ErreurValidation("Le nouveau titre est requis.")

        try:
            succes = ConversationDAO.renommer_conv(id_conversation, nouveau_titre)
            if succes:
                logging.info("Conversation %s renommée en '%s'", id_conversation, nouveau_titre)
            else:
                logging.warning("Aucune conversation trouvée pour id=%s", id_conversation)
            return succes
        except Exception as e:
            logging.error("Erreur lors du renommage de la conversation %s : %s", id_conversation, e)
            raise

    def supprimer_conversation(id_conversation: int, id_demandeur: int) -> bool:
        """
        Supprime une conversation existante.

        Parameters
        ----------
        id_conversation : int
            Identifiant de la conversation

        Returns
        -------
        bool
            True si suppression effectuée, False sinon

        Raises
        ------
        ErreurValidation
            Si l’id est manquant
        """
        logging.debug(
            "Demande de suppression de conversation id=%s par utilisateur id=%s",
            id_conversation,
            id_demandeur,
        )

        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not ConversationDAO.est_proprietaire(id_conversation, id_demandeur):
            logging.warning(
                "Tentative de suppression par un utilisateur non propriétaire (conv=%s, user=%s).",
                id_conversation,
                id_demandeur,
            )
            raise ErreurValidation(
                "Seul le propriétaire de la conversation peut gérer les participants."
            )
        try:
            succes = ConversationDAO.supprimer_conv(id_conv=id_conversation)
            if succes:
                logging.info("Conversation %s supprimée avec succès", id_conversation)
            else:
                logging.warning(
                    "Aucune conversation trouvée à supprimer pour id=%s", id_conversation
                )
            return succes
        except Exception as e:
            logging.error(
                "Erreur lors de la suppression de la conversation %s : %s", id_conversation, e
            )
            raise

    def lister_conversations(id_utilisateur: int, limite=None) -> List["Conversation"]:
        """
        Liste les conversations d’un utilisateur.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l’utilisateur
        limite : int | None
            Nombre maximum de conversations à retourner (facultatif)

        Returns
        -------
        List[Conversation]
            Liste des conversations, vide si aucune

        Raises
        ------
        ErreurValidation
            Si id_utilisateur manquant ou limite invalide
        """
        logging.debug(
            "Liste des conversations demandée pour utilisateur id=%s avec limite=%r",
            id_utilisateur,
            limite,
        )

        if id_utilisateur is None:
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")
        if limite is not None and limite < 1:
            raise ErreurValidation("La limite doit être plus grande ou égale à 1.")

        try:
            res = ConversationDAO.lister_conversations(id_user=id_utilisateur, n=limite)
            nb = len(res) if res else 0
            logging.info(
                "Liste des conversations récupérée pour utilisateur id=%s (nb=%s)",
                id_utilisateur,
                nb,
            )
            # Si la DAO renvoie une liste, on la passe telle quelle
            return res or []
        except Exception as e:
            # La DAO lève actuellement une Exception quand aucun résultat.
            # On transforme proprement en liste vide pour la vue.
            msg = str(e).lower()
            if "aucune conversation trouvée" in msg or "aucune conversation" in msg:
                logging.info(
                    "Aucune conversation trouvée pour utilisateur id=%s, retour liste vide.",
                    id_utilisateur,
                )
                return []
            # Autre erreur = vraie erreur
            logging.error(
                "Erreur lors de la récupération des conversations de l'utilisateur %s : %s",
                id_utilisateur,
                e,
            )
            raise

    def rechercher_conversations(
        id_utilisateur: int, mot_cle=None, date_recherche=None
    ) -> List["Conversation"]:
        """
        Recherche des conversations selon un mot-clé et/ou une date.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l’utilisateur
        mot_cle : str | None
            Mot-clé à rechercher
        date_recherche : datetime.date | None
            Date pour filtrer les conversations

        Returns
        -------
        List[Conversation]
            Liste des conversations correspondant aux critères

        Raises
        ------
        ErreurValidation
            Si id_utilisateur manquant
        """
        logging.debug(
            "Recherche de conversations pour utilisateur id=%s avec mot_cle=%r et date_recherche=%r",
            id_utilisateur,
            mot_cle,
            date_recherche,
        )

        if id_utilisateur is None:
            raise ErreurValidation("L'identifiant de l'utilisateur est requis.")

        # Normaliser les entrées
        if isinstance(mot_cle, str):
            mot_cle = mot_cle.strip()
            if mot_cle == "":
                mot_cle = None

        try:
            if mot_cle is not None and date_recherche is not None:
                res = ConversationDAO.rechercher_conv_mot_et_date(
                    id_user=id_utilisateur, mot_cle=mot_cle, date=date_recherche
                )
                logging.info("Recherche combinée par mot-clé et date effectuée.")
            elif mot_cle is not None:
                res = ConversationDAO.rechercher_mot_clef(id_user=id_utilisateur, mot_clef=mot_cle)
                logging.info("Recherche par mot-clé effectuée.")
            elif date_recherche is not None:
                res = ConversationDAO.rechercher_date(id_user=id_utilisateur, date=date_recherche)
                logging.info("Recherche par date effectuée.")
            else:
                res = ConversationDAO.lister_conversations(id_user=id_utilisateur)
                logging.info("Aucun critère fourni, listing général.")

            nb = len(res) if res else 0
            logging.debug("Résultat de recherche : %s conversations trouvées.", nb)
            return res or []

        except Exception as e:
            msg = str(e).lower()
            if "aucune conversation" in msg or "pas de messages" in msg:
                logging.info(
                    "Aucun résultat pour la recherche de conversations (user=%s, mot_cle=%r, date=%r).",
                    id_utilisateur,
                    mot_cle,
                    date_recherche,
                )
                return []
            logging.error("Erreur lors de la recherche des conversations : %s", e)
            raise

    @staticmethod
    def lire_fil(id_conversation: int, decalage: int = 0, limite: int | None = 20):
        """
        Lit le fil de messages d’une conversation.

        Parameters
        ----------
        id_conversation : int
            Identifiant de la conversation
        decalage : int
            Décalage pour pagination (offset)
        limite : int | None
            Nombre maximum de messages à lire

        Returns
        -------
        List[Echange]
            Liste des messages de la conversation

        Raises
        ------
        ErreurValidation
            Si id_conversation manquant
        """
        logging.debug(
            "Lecture du fil de conversation id=%s avec decalage=%r et limite=%r",
            id_conversation,
            decalage,
            limite,
        )

        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")

        offset = max(0, int(decalage or 0))

        if limite is None:
            limit = None
        else:
            limit = max(1, int(limite))

        try:
            echanges = (
                ConversationDAO.lire_echanges(id_conversation, offset=offset, limit=limit) or []
            )
            logging.debug(
                "Lecture du fil terminée (conv=%s, nb_messages=%s)",
                id_conversation,
                len(echanges),
            )
            return echanges
        except Exception as e:
            logging.error(
                "Erreur lors de la lecture du fil de la conversation %s : %s",
                id_conversation,
                e,
            )
            raise

    def rechercher_message(
        id_conversation: int, mot_cle: str, date_recherche: Date
    ) -> List["Echange"]:
        """
        Recherche des messages dans une conversation par mot-clé et/ou date.

        Parameters
        ----------
        id_conversation : int
        mot_cle : str
        date_recherche : datetime.date

        Returns
        -------
        List[Echange]
            Messages correspondants aux critères

        Raises
        ------
        ErreurValidation
            Si paramètres manquants
        """
        logging.debug(
            "Recherche de messages dans conv=%s avec mot_cle=%r et date_recherche=%r",
            id_conversation,
            mot_cle,
            date_recherche,
        )

        if id_conversation is None:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if not mot_cle and not date_recherche:
            raise ErreurValidation("Un mot-clé ou une date doivent être fournis.")
        try:
            res = ConversationDAO.rechercher_echange(id_conversation, mot_cle, date_recherche)
            if res:
                logging.info(
                    f"Messages trouvés dans la conversation {id_conversation} (mot-clé: {mot_cle})"
                )
                return res
            else:
                logging.warning(
                    f"Aucun message trouvé dans la conversation {id_conversation} avec les critères donnés."
                )
        except Exception as e:
            logging.error(
                "Erreur lors de la recherche de messages dans la conversation %s : %s",
                id_conversation,
                e,
            )
            raise

    def ajouter_utilisateur(
        id_conversation: int,
        id_utilisateur: int,
        role: str,
        id_demandeur: int,
    ) -> bool:
        """
        Ajoute un utilisateur à une conversation avec un rôle donné.

        Parameters
        ----------
        id_conversation : int
        id_utilisateur : int
        id_demandeur : int
        role : str

        Returns
        -------
        bool
            True si ajout réussi, False sinon

        Raises
        ------
        ErreurValidation
            Si paramètres manquants
        """
        logging.debug(
            "Demande d'ajout utilisateur=%s dans conv=%s avec role=%r par demandeur=%s",
            id_utilisateur,
            id_conversation,
            role,
            id_demandeur,
        )

        if not id_conversation or not id_utilisateur or not role:
            raise ErreurValidation(
                "Les champs id_conversation, id_utilisateur et rôle sont requis."
            )

        if not ConversationDAO.est_proprietaire(id_conversation, id_demandeur):
            raise ErreurValidation(
                "Seul le propriétaire de la conversation peut gérer les participants."
            )

        try:
            res = ConversationDAO.ajouter_participant(id_conversation, id_utilisateur, role)
            if res:
                logging.info(
                    f"Utilisateur {id_utilisateur} ajouté à la conversation {id_conversation} avec le rôle {role}"
                )
                return res
            else:
                logging.warning(
                    f"Échec de l’ajout de l’utilisateur {id_utilisateur} à la conversation {id_conversation}"
                )
        except Exception as e:
            logging.error(
                "Erreur lors de l’ajout de l’utilisateur %s à la conversation %s : %s",
                id_utilisateur,
                id_conversation,
                e,
            )
            raise

    def retirer_utilisateur(
        id_conversation: int,
        id_utilisateur: int,
        id_demandeur: int,
    ) -> bool:
        """
        Retire un utilisateur d’une conversation.

        Parameters
        ----------
        id_conversation : int
        id_utilisateur : int

        Returns
        -------
        bool
            True si retrait effectué, False sinon

        Raises
        ------
        ErreurValidation
            Si paramètres manquants
        """
        logging.debug(
            "Demande de retrait utilisateur=%s de conv=%s par demandeur=%s",
            id_utilisateur,
            id_conversation,
            id_demandeur,
        )

        if not id_conversation or not id_utilisateur:
            raise ErreurValidation("Les champs id_conversation et id_utilisateur sont requis.")

        if not ConversationDAO.est_proprietaire(id_conversation, id_demandeur):
            raise ErreurValidation(
                "Seul le propriétaire de la conversation peut gérer les participants."
            )

        try:
            res = ConversationDAO.retirer_participant(id_conversation, id_utilisateur)
            if res:
                logging.info(
                    f"Utilisateur {id_utilisateur} retiré de la conversation {id_conversation}"
                )
                return res
            else:
                logging.warning(
                    f"Aucun utilisateur {id_utilisateur} trouvé dans la conversation {id_conversation}"
                )
        except Exception as e:
            logging.error(
                "Erreur lors du retrait de l’utilisateur %s de la conversation %s : %s",
                id_utilisateur,
                id_conversation,
                e,
            )
            raise

    def mettre_a_jour_personnalisation(self, id_conversation: int, personnalisation: str) -> bool:
        """
        Met à jour le prompt associé à une conversation.

        Parameters
        ----------
        id_conversation : int
        personnalisation : str | int
            Prompt à appliquer à la conversation

        Returns
        -------
        bool
            True si mise à jour réussie

        Raises
        ------
        ErreurValidation
            Si paramètres manquants ou prompt inconnu
        """
        logging.debug(
            "Mise à jour de la personnalisation de conv=%s avec personnalisation=%r",
            id_conversation,
            personnalisation,
        )

        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if personnalisation is None:
            raise ErreurValidation("Le champ personnalisation est requis.")
        try:
            prompt_id = ConversationService._resolve_prompt_id(personnalisation)
            print(prompt_id)
            succes = ConversationDAO.mettre_a_j_preprompt_id(id_conversation, prompt_id)
            if succes:
                logging.info(
                    "Personnalisation mise à jour (prompt_id=%s) pour la conversation %s",
                    prompt_id,
                    id_conversation,
                )
            return succes
        except Exception as e:
            logging.error("Erreur lors de la mise à jour de la personnalisation : %s", e)
            raise

    def exporter_conversation(self, id_conversation: int, format_: str) -> bool:
        """
        Exporte une conversation dans un fichier.

        Parameters
        ----------
        id_conversation : int
            Identifiant de la conversation
        format_ : str
            Format d’export ("json" ou "txt")

        Returns
        -------
        bool
            True si export réussi

        Raises
        ------
        ErreurValidation
            Si format non supporté ou paramètres invalides
        """
        logging.debug(
            "Demande d'export de la conversation id=%s au format %r",
            id_conversation,
            format_,
        )

        if not id_conversation:
            raise ErreurValidation("L'identifiant de la conversation est requis.")
        if format_ not in ("json", "txt"):
            raise ErreurValidation("Format non supporté.")

        try:
            # Dossier d’export (relatif au répertoire où est lancée l’appli)
            export_dir = Path("exports")
            export_dir.mkdir(parents=True, exist_ok=True)

            # On récupère tous les échanges de la conversation
            echanges = ConversationDAO.lire_echanges(
                id_conversation,
                offset=0,
                limit=None,  # None = toute la conversation
            )

            if not echanges:
                logging.info(
                    "Export demandé pour conv=%s mais aucun échange trouvé.",
                    id_conversation,
                )

            if format_ == "json":
                import json

                filename = export_dir / f"conversation_{id_conversation}.json"
                with filename.open("w", encoding="utf-8") as fichier:
                    json.dump(
                        [e.__dict__ for e in echanges],
                        fichier,
                        ensure_ascii=False,
                        indent=2,
                    )

            elif format_ == "txt":
                # On récupère les métadonnées de la conversation
                try:
                    conv = ConversationDAO.trouver_par_id(id_conversation)
                    titre = conv.nom
                    date_creation = conv.date_creation
                except Exception:
                    conv = None
                    titre = f"Conversation #{id_conversation}"
                    date_creation = None

                filename = export_dir / f"conversation_{id_conversation}.txt"
                with filename.open("w", encoding="utf-8") as fichier:
                    # En-tête visuel propre
                    titre_affiche = titre.upper()
                    fichier.write("=" * 60 + "\n")
                    fichier.write(f"   CONVERSATION : {titre_affiche}\n")
                    fichier.write("=" * 60 + "\n")

                    if date_creation is not None:
                        fichier.write(f"Créée le : {date_creation:%Y-%m-%d %H:%M:%S}\n")

                    fichier.write(f"ID : {id_conversation}\n")
                    fichier.write("\n" + "-" * 60 + "\n\n")

                    # Corps de la conversation
                    for e in echanges:
                        if hasattr(e, "afficher_echange"):
                            ligne = e.afficher_echange()
                        else:
                            date_msg = getattr(e, "date_msg", None)
                            agent_name = getattr(e, "agent_name", getattr(e, "agent", ""))
                            message = getattr(e, "message", "")
                            if date_msg is not None:
                                try:
                                    ligne = (
                                        f"[{date_msg:%Y-%m-%d %H:%M:%S}] {agent_name}: {message}"
                                    )
                                except Exception:
                                    ligne = f"{agent_name}: {message}"
                            else:
                                ligne = f"{agent_name}: {message}"

                        fichier.write(ligne + "\n")

            logging.info(
                "Conversation %s exportée en %s dans %s",
                id_conversation,
                format_,
                export_dir,
            )
            return True
        except Exception as e:
            logging.error(
                "Erreur lors de l'exportation de la conversation %s : %s",
                id_conversation,
                e,
            )
            raise

    @staticmethod
    def demander_assistant(
        message: str,
        options=None,
        id_conversation: int | None = None,
        id_user: int | None = None,
    ):
        """
        Envoie un message à l’assistant (LLM) et reçoit une réponse.
        - Injecte un message 'system' en tête du history (non stocké en BDD).
        - Si id_conversation est fourni, charge l'historique et persiste les échanges.
        - id_user est recommandé pour satisfaire la contrainte BDD (utilisateur_id NOT NULL)
        lorsque emetteur='utilisateur'.

        Parameters
        ----------
        message : str
            Message utilisateur
        options : dict | None
            Options LLM : temperature, top_p, max_tokens, stop
        id_conversation : int | None
            Identifiant de conversation pour historiser les échanges
        id_user : int | None
            Identifiant utilisateur (requis si persisté dans la BDD)

        Returns
        -------
        Echange
            Objet représentant la réponse de l’assistant

        Raises
        ------
        ErreurValidation
            Si message vide
        Exception
            Si échec d’appel LLM ou persistance
        """
        from src.business_object.echange import Echange

        # Charger dynamiquement le client LLM (compat chemins)
        try:
            try:
                from src.client.llm_client import LLM_API
            except ImportError:
                from src.client.llm_client import LLM_API
        except Exception as imp_err:
            logging.error("Impossible de charger LLM_API: %s", imp_err)
            raise

        if not message or not message.strip():
            raise ErreurValidation("Le message est requis.")

        logging.info("Assistant appelé avec le message : %s", message[:200])

        # Hyperparamètres avec valeurs par défaut
        temperature = float(options.get("temperature", 0.7)) if options else 0.7
        top_p = float(options.get("top_p", 1.0)) if options else 1.0
        max_tokens = int(options.get("max_tokens", 1024)) if options else 1024
        stop = options.get("stop") if options and "stop" in options else None

        logging.debug(
            "Appel LLM avec options : temperature=%s, top_p=%s, max_tokens=%s, stop=%r",
            temperature,
            top_p,
            max_tokens,
            stop,
        )

        # 1) Prompt système (non persisté en BDD)
        try:
            system_prompt = ConversationService._resolve_system_prompt_for_conv(id_conversation)
        except Exception:
            system_prompt = getattr(
                ConversationService, "DEFAULT_SYSTEM_PROMPT", "Tu es un assistant utile."
            )

        # 2) Historique existant -> rôles LLM (user/assistant)
        history = [{"role": "system", "content": system_prompt}]
        if id_conversation:
            try:
                anciens = ConversationDAO.lire_echanges(id_conversation, offset=0, limit=None) or []
                for e in anciens:
                    emet = (
                        getattr(e, "expediteur", "")
                        or getattr(e, "agent", "")
                        or getattr(e, "emetteur", "")
                    ).lower()
                    role = "assistant" if emet in ("ia", "assistant") else "user"
                    contenu = getattr(e, "message", getattr(e, "contenu", "")) or ""
                    history.append({"role": role, "content": contenu})
            except Exception as e:
                logging.warning(
                    "Impossible de récupérer l'historique (conv=%s) : %s", id_conversation, e
                )

        # 3) Ajoute le message utilisateur courant à l'historique d'appel LLM
        history.append({"role": "user", "content": message})

        logging.debug(
            "Historique envoyé au LLM (conv=%r) : %s messages.",
            id_conversation,
            len(history),
        )

        # 4) Appel LLM (le client attend une liste d'Echange(agent, message))
        client = LLM_API()
        reponse = client.generate(
            history=[
                Echange(agent=h["role"], message=h["content"], agent_name=None) for h in history
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )

        # 5) Réponse pour la VUE (respecte le constructeur Echange)
        echange_assistant_vue = Echange(
            agent="assistant",
            message=getattr(reponse, "message", str(reponse)),
            agent_name="Assistant",
            date_msg=Date.today(),
        )

        logging.debug(
            "Réponse assistant générée (longueur message=%s caractères).",
            len(echange_assistant_vue.message or ""),
        )

        # 6) Persistance BDD (si id_conversation connu et méthode DAO présente)
        if id_conversation and hasattr(ConversationDAO, "ajouter_echange"):
            try:
                # Message utilisateur à persister
                e_user_db = Echange(agent="user", message=message)
                # Attributs attendus par la DAO (emetteur/ contenu / utilisateur_id)
                setattr(e_user_db, "emetteur", "utilisateur")
                setattr(e_user_db, "contenu", message)
                setattr(e_user_db, "utilisateur_id", id_user)  # requis si la BDD l'impose

                # Message assistant à persister
                e_assistant_db = Echange(agent="assistant", message=echange_assistant_vue.message)
                setattr(e_assistant_db, "emetteur", "ia")
                setattr(e_assistant_db, "contenu", echange_assistant_vue.message)
                setattr(e_assistant_db, "utilisateur_id", None)

                ConversationDAO.ajouter_echange(id_conversation, e_user_db)
                ConversationDAO.ajouter_echange(id_conversation, e_assistant_db)
            except Exception as e:
                logging.warning(
                    "Échec de la persistance des échanges (conv=%s) : %s", id_conversation, e
                )
        else:
            logging.info(
                "Historique non persisté (pas d'id_conversation ou DAO sans ajouter_echange)."
            )

        return echange_assistant_vue
