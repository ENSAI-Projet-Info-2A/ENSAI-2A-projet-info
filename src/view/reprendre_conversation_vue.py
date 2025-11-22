import logging

from InquirerPy import inquirer

from src.dao.prompt_dao import PromptDAO
from src.service.conversation_service import ConversationService, ErreurValidation
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class ReprendreConversationVue(VueAbstraite):
    """
    Vue d'une conversation ouverte :
    - Affiche les derniers messages
    - Permet d'envoyer un message à l'agent
    - Permet de gérer la personnalisation et les participants
    """

    def __init__(self, conversation, message: str = ""):
        """
        :param conversation: objet Conversation (id, nom, ...)
        :param message: message flash optionnel à afficher en haut
        """
        self.conv = conversation
        self.message = message

    def _afficher_messages(self, nb=None):
        logging.debug(
            "[ReprendreConversationVue] Affichage des derniers messages conv_id=%s, nb=%r",
            getattr(self.conv, "id", None),
            nb,
        )
        try:
            echanges = (
                ConversationService.lire_fil(id_conversation=self.conv.id, decalage=0, limite=nb)
                or []
            )
            logging.info(
                "[ReprendreConversationVue] %s message(s) récupéré(s) pour conv_id=%s",
                len(echanges),
                self.conv.id,
            )
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur lire_fil conv={self.conv.id} : {e}")
            print("\n(Impossible d'afficher les messages pour l’instant)\n")
            return

        print("\n" + "-" * 60)
        print(f"Conversation « {self.conv.nom} » — derniers messages")
        print("-" * 60 + "\n")

        if not echanges:
            print("(Aucun message pour l’instant)\n")
            return

        # echange.agent / echange.message / echange.date_msg (ou expediteur / contenu / date_echange)
        for e in echanges:
            auteur = (
                getattr(e, "agent_name", None)
                or getattr(e, "agent", getattr(e, "expediteur", ""))
                or ""
            )
            contenu = getattr(e, "message", getattr(e, "contenu", "")) or ""
            date_msg = getattr(e, "date_msg", getattr(e, "date_echange", "")) or ""
            print(f"- {auteur} | {date_msg} : {contenu}")
        print("")

    def _afficher_tous_les_messages(self):
        logging.debug(
            "[ReprendreConversationVue] Affichage de tous les messages conv_id=%s",
            getattr(self.conv, "id", None),
        )
        try:
            echanges = (
                ConversationService.lire_fil(id_conversation=self.conv.id, decalage=0, limite=None)
                or []
            )
            logging.info(
                "[ReprendreConversationVue] %s message(s) récupéré(s) (tous) pour conv_id=%s",
                len(echanges),
                self.conv.id,
            )
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur lire_fil conv={self.conv.id} : {e}")
            print("\n(Impossible d'afficher les messages pour l’instant)\n")
            return

        print("\n" + "-" * 60)
        print(f"Conversation « {self.conv.nom} » — tous les messages")
        print("-" * 60 + "\n")

        if not echanges:
            print("(Aucun message pour l’instant)\n")
            return

        for e in echanges:
            auteur = (
                getattr(e, "agent_name", None)
                or getattr(e, "agent", getattr(e, "expediteur", ""))
                or ""
            )
            contenu = getattr(e, "message", getattr(e, "contenu", "")) or ""
            date_msg = getattr(e, "date_msg", getattr(e, "date_echange", "")) or ""
            print(f"- {auteur} | {date_msg} : {contenu}")
        print("")

        inquirer.text(message="Appuyez sur Entrée pour revenir au menu...", default="").execute()
        return ReprendreConversationVue(self.conv)

    def _envoyer_message(self):
        logging.debug(
            "[ReprendreConversationVue] Demande d'envoi de message pour conv_id=%s",
            getattr(self.conv, "id", None),
        )
        texte = inquirer.text(message="Votre message :", default="").execute().strip()
        if not texte:
            logging.info(
                "[ReprendreConversationVue] Message vide, envoi annulé pour conv_id=%s",
                self.conv.id,
            )
            return ReprendreConversationVue(self.conv, "Message vide, rien envoyé.")

        try:
            user = Session().utilisateur  # ← utilisateur courant
            logging.info(
                "[ReprendreConversationVue] Envoi message user_id=%s pour conv_id=%s (len=%s)",
                getattr(user, "id", None) if user else None,
                self.conv.id,
                len(texte),
            )
            rep = ConversationService.demander_assistant(
                message=texte,
                options=None,
                id_conversation=self.conv.id,
                id_user=(user.id if user else None),
            )
        except ErreurValidation as e:
            logging.warning(
                "[ReprendreConversationVue] Erreur de validation lors de l'envoi de message : %s",
                e,
            )
            return ReprendreConversationVue(self.conv, f"Erreur de validation : {e}")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur envoyer message : {e}")
            return ReprendreConversationVue(self.conv, "Échec de l’envoi du message.")

        # Afficher la réponse
        reponse_txt = getattr(rep, "message", "") or "(réponse vide)"
        logging.info(
            "[ReprendreConversationVue] Réponse reçue de l'assistant pour conv_id=%s (len=%s)",
            self.conv.id,
            len(reponse_txt),
        )
        print("\n--- Réponse de l’agent ---")
        print(reponse_txt)
        print("--------------------------\n")

        inquirer.text(message="Appuyez sur Entrée pour continuer...", default="").execute()
        return ReprendreConversationVue(self.conv)

    def _changer_personnalisation(self):
        """Change la personnalisation de la conversation via un menu interactif."""
        logging.debug(
            "[ReprendreConversationVue] Changement de personnalisation demandé pour conv_id=%s",
            getattr(self.conv, "id", None),
        )

        # 1) Récupérer la liste des prompts
        try:
            prompts = PromptDAO.lister_prompts()
            logging.info(
                "[ReprendreConversationVue] %s prompt(s) récupéré(s) depuis la BDD",
                len(prompts) if prompts else 0,
            )
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur récupération prompts : {e}")
            print("\n(Impossible de récupérer la liste des prompts.)\n")
            return ReprendreConversationVue(self.conv, "Personnalisation inchangée.")

        if not prompts:
            print("\n(Aucun prompt n'est défini dans la base.)\n")
            return ReprendreConversationVue(self.conv, "Personnalisation inchangée.")

        # 2) Construire les choix pour InquirerPy
        choices = [
            {
                "name": f"[{p['id']}] {p['nom']}",
                "value": p["id"],  # on renvoie l'ID (int)
            }
            for p in prompts
        ]

        # Option pour ne rien changer / annuler
        choices.insert(
            0, {"name": "<- Annuler (laisser la personnalisation actuelle)", "value": None}
        )

        # 3) Menu interactif
        selection = inquirer.select(
            message="Choisir une nouvelle personnalisation :",
            choices=choices,
        ).execute()

        logging.info(
            "[ReprendreConversationVue] Sélection personnalisation pour conv_id=%s : %r",
            self.conv.id,
            selection,
        )

        if selection is None:
            # L'utilisateur a choisi "Annuler"
            return ReprendreConversationVue(self.conv, "Personnalisation inchangée.")

        try:
            svc = ConversationService()
            # selection est un int (prompt_id) → compatible avec _resoudre_id_prompt
            svc.mettre_a_jour_personnalisation(self.conv.id, selection)
            logging.info(
                "[ReprendreConversationVue] Personnalisation mise à jour conv_id=%s -> prompt_id=%s",
                self.conv.id,
                selection,
            )
            return ReprendreConversationVue(
                self.conv,
                f"Personnalisation mise à jour (prompt_id={selection}).",
            )
        except ErreurValidation as e:
            logging.warning(
                "[ReprendreConversationVue] Erreur de validation personnalisation conv_id=%s : %s",
                self.conv.id,
                e,
            )
            return ReprendreConversationVue(self.conv, f"Erreur : {e}")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur perso conv={self.conv.id} : {e}")
            return ReprendreConversationVue(
                self.conv, "Échec de la mise à jour de la personnalisation."
            )

    def _ajouter_participant(self):
        logging.debug(
            "[ReprendreConversationVue] Ajout participant demandé pour conv_id=%s",
            getattr(self.conv, "id", None),
        )
        try:
            id_user = int(
                inquirer.text(message="ID de l'utilisateur à ajouter :", default="")
                .execute()
                .strip()
            )
        except ValueError:
            logging.warning(
                "[ReprendreConversationVue] ID invalide saisi pour ajout participant (conv_id=%s)",
                self.conv.id,
            )
            return ReprendreConversationVue(self.conv, "ID invalide.")

        try:
            ConversationService.ajouter_utilisateur(
                id_conversation=self.conv.id,
                id_utilisateur=id_user,
                role="participant",
                id_demandeur=Session().utilisateur.id,
            )
            logging.info(
                "[ReprendreConversationVue] Participant ajouté conv_id=%s, user_id=%s",
                self.conv.id,
                id_user,
            )
            return ReprendreConversationVue(self.conv, f"Utilisateur {id_user} ajouté.")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur ajout participant : {e}")
            return ReprendreConversationVue(self.conv, "Échec de l’ajout du participant.")

    def _retirer_participant(self):
        logging.debug(
            "[ReprendreConversationVue] Retrait participant demandé pour conv_id=%s",
            getattr(self.conv, "id", None),
        )
        try:
            id_user = int(
                inquirer.text(message="ID de l'utilisateur à retirer :", default="")
                .execute()
                .strip()
            )
        except ValueError:
            logging.warning(
                "[ReprendreConversationVue] ID invalide saisi pour retrait participant (conv_id=%s)",
                self.conv.id,
            )
            return ReprendreConversationVue(self.conv, "ID invalide.")

        try:
            ConversationService.retirer_utilisateur(
                id_conversation=self.conv.id,
                id_utilisateur=id_user,
                id_demandeur=Session().utilisateur.id,
            )
            logging.info(
                "[ReprendreConversationVue] Participant retiré conv_id=%s, user_id=%s",
                self.conv.id,
                id_user,
            )
            return ReprendreConversationVue(self.conv, f"Utilisateur {id_user} retiré.")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur retrait participant : {e}")
            return ReprendreConversationVue(self.conv, "Échec du retrait du participant.")

    def _renommer(self):
        logging.debug(
            "[ReprendreConversationVue] Renommage demandé pour conv_id=%s (titre actuel=%r)",
            getattr(self.conv, "id", None),
            getattr(self.conv, "nom", None),
        )
        nouveau = (
            inquirer.text(
                message="Nouveau titre : ",
                default=self.conv.nom,
                validate=lambda x: len(x.strip()) > 0 and len(x.strip()) <= 255,
                invalid_message="Le titre ne doit pas être vide et ≤ 255 caractères.",
            )
            .execute()
            .strip()
        )

        try:
            ConversationService.renommer_conversation(self.conv.id, nouveau)
            logging.info(
                "[ReprendreConversationVue] Conversation renommée conv_id=%s -> %r",
                self.conv.id,
                nouveau,
            )
            self.conv.nom = nouveau
            return ReprendreConversationVue(self.conv, f"Titre modifié en « {nouveau} ».")
        except ErreurValidation as e:
            logging.warning(
                "[ReprendreConversationVue] Erreur validation renommage conv_id=%s : %s",
                self.conv.id,
                e,
            )
            return ReprendreConversationVue(self.conv, f"Erreur : {e}")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur renommage conv={self.conv.id} : {e}")
            return ReprendreConversationVue(self.conv, "Échec du renommage.")

    def _supprimer(self):
        logging.debug(
            "[ReprendreConversationVue] Demande de suppression pour conv_id=%s",
            getattr(self.conv, "id", None),
        )
        confirm = inquirer.confirm(
            message=f"Supprimer définitivement « {self.conv.nom} » ?",
            default=False,
        ).execute()
        logging.info(
            "[ReprendreConversationVue] Confirmation suppression conv_id=%s : %s",
            self.conv.id,
            confirm,
        )
        if not confirm:
            return ReprendreConversationVue(
                self.conv,
                "Suppression annulée.",
            )

        # Récupérer l'utilisateur courant
        utilisateur = Session().utilisateur
        if utilisateur is None:
            logging.warning(
                "[ReprendreConversationVue] Suppression refusée : aucun utilisateur en session."
            )
            # Au choix : tu peux interdire la suppression si pas connecté
            return ReprendreConversationVue(self.conv, "Vous devez être connecté pour supprimer.")

        try:
            ConversationService.supprimer_conversation(
                id_conversation=self.conv.id,
                id_demandeur=utilisateur.id,
            )
            logging.info(
                "[ReprendreConversationVue] Conversation supprimée conv_id=%s par user_id=%s",
                self.conv.id,
                utilisateur.id,
            )
            from src.view.conversations_vue import ConversationsVue

            return ConversationsVue("Conversation supprimée.")
        except ErreurValidation as e:
            # Erreur "propriétaire" ou autre validation
            logging.warning(
                "[ReprendreConversationVue] Erreur validation suppression conv_id=%s : %s",
                self.conv.id,
                e,
            )
            return ReprendreConversationVue(self.conv, f"Erreur : {e}")
        except Exception as e:
            logging.error(
                f"[ReprendreConversationVue] Erreur suppression conv={self.conv.id} : {e}"
            )
            return ReprendreConversationVue(self.conv, "Échec de la suppression.")

    def choisir_menu(self):
        logging.debug(
            "[ReprendreConversationVue] Affichage menu principal conv_id=%s, titre=%r, message=%r",
            getattr(self.conv, "id", None),
            getattr(self.conv, "nom", None),
            self.message,
        )
        # En-tête + message flash
        print("\n" + "=" * 60)
        print(f"Reprendre la discussion — « {self.conv.nom} »")
        print("=" * 60 + "\n")
        if self.message:
            print(self.message + "\n")

        # Afficher les derniers messages
        self._afficher_messages(nb=20)

        # Boucle d'action
        choix = inquirer.select(
            message="Que voulez-vous faire ?",
            choices=[
                "Envoyer un message",
                "Voir tous les messages",
                "Changer la personnalisation",
                "Ajouter un participant",
                "Retirer un participant",
                "Renommer la conversation",
                "Supprimer la conversation",
                "↩︎ Retour à la liste des conversations",
            ],
            cycle=True,
        ).execute()

        logging.info(
            "[ReprendreConversationVue] Choix utilisateur pour conv_id=%s : %r",
            self.conv.id,
            choix,
        )

        match choix:
            case "Envoyer un message":
                return self._envoyer_message()
            case "Voir tous les messages":
                self._afficher_tous_les_messages()
                return ReprendreConversationVue(self.conv)
            case "Changer la personnalisation":
                return self._changer_personnalisation()
            case "Ajouter un participant":
                return self._ajouter_participant()
            case "Retirer un participant":
                return self._retirer_participant()
            case "Renommer la conversation":
                return self._renommer()
            case "Supprimer la conversation":
                return self._supprimer()
            case "↩︎ Retour à la liste des conversations":
                from view.conversations_vue import ConversationsVue

                return ConversationsVue()
