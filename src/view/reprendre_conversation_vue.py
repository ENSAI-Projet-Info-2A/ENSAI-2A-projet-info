# view/reprendre_conversation_vue.py
import logging

from InquirerPy import inquirer

from service.conversation_service import ConversationService, ErreurValidation
from view.vue_abstraite import VueAbstraite


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

    def _afficher_messages(self, nb=20):
        try:
            echanges = (
                ConversationService.lire_fil(id_conversation=self.conv.id, decalage=0, limite=nb)
                or []
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
            auteur = getattr(e, "agent", getattr(e, "expediteur", "")) or ""
            contenu = getattr(e, "message", getattr(e, "contenu", "")) or ""
            date_msg = getattr(e, "date_msg", getattr(e, "date_echange", "")) or ""
            print(f"- {auteur} | {date_msg} : {contenu}")
        print("")

    def _envoyer_message(self):
        """Demande un input utilisateur et envoie le message via le Service, puis affiche la réponse."""
        texte = inquirer.text(message="Votre message :", default="").execute().strip()
        if not texte:
            return ReprendreConversationVue(self.conv, "Message vide, rien envoyé.")
        try:
            rep = ConversationService.demander_assistant(
                message=texte, options=None, id_conversation=self.conv.id
            )
            print(rep)
        except ErreurValidation as e:
            return ReprendreConversationVue(self.conv, f"Erreur de validation : {e}")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur envoyer message : {e}")
            return ReprendreConversationVue(self.conv, "Échec de l’envoi du message.")

        # Afficher la réponse
        reponse_txt = getattr(rep, "message", "") or "(réponse vide)"
        print("\n--- Réponse de l’agent ---")
        print(reponse_txt)
        print("--------------------------\n")

        # Rester dans la vue
        inquirer.text(message="Appuyez sur Entrée pour continuer...", default="").execute()
        return ReprendreConversationVue(self.conv)

    def _changer_personnalisation(self):
        """Appelle la mise à jour de la personnalisation via le Service (utilise la méthode d'instance)."""
        new_perso = (
            inquirer.text(
                message="Nouvelle personnalisation (nom de prompt ou ID) :",
                default="",
            )
            .execute()
            .strip()
        )
        if not new_perso:
            return ReprendreConversationVue(self.conv, "Personnalisation inchangée.")

        try:
            # La méthode est définie avec `self` dans ConversationService → instancier.
            svc = ConversationService()
            svc.mettre_a_jour_personnalisation(self.conv.id, new_perso)
            return ReprendreConversationVue(
                self.conv, f"Personnalisation mise à jour : {new_perso}"
            )
        except ErreurValidation as e:
            return ReprendreConversationVue(self.conv, f"Erreur : {e}")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur perso conv={self.conv.id} : {e}")
            return ReprendreConversationVue(
                self.conv, "Échec de la mise à jour de la personnalisation."
            )

    def _ajouter_participant(self):
        try:
            id_user = int(
                inquirer.text(message="ID de l'utilisateur à ajouter :", default="")
                .execute()
                .strip()
            )
        except ValueError:
            return ReprendreConversationVue(self.conv, "ID invalide.")

        try:
            # Le Service expose ajouter_utilisateur (qui délègue à la DAO)
            ConversationService.ajouter_utilisateur(self.conv.id, id_user, role="participant")
            return ReprendreConversationVue(self.conv, f"Utilisateur {id_user} ajouté.")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur ajout participant : {e}")
            return ReprendreConversationVue(self.conv, "Échec de l’ajout du participant.")

    def _retirer_participant(self):
        try:
            id_user = int(
                inquirer.text(message="ID de l'utilisateur à retirer :", default="")
                .execute()
                .strip()
            )
        except ValueError:
            return ReprendreConversationVue(self.conv, "ID invalide.")

        try:
            ConversationService.retirer_utilisateur(self.conv.id, id_user)
            return ReprendreConversationVue(self.conv, f"Utilisateur {id_user} retiré.")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur retrait participant : {e}")
            return ReprendreConversationVue(self.conv, "Échec du retrait du participant.")

    def _renommer(self):
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
            self.conv.nom = nouveau
            return ReprendreConversationVue(self.conv, f"Titre modifié en « {nouveau} ».")
        except ErreurValidation as e:
            return ReprendreConversationVue(self.conv, f"Erreur : {e}")
        except Exception as e:
            logging.error(f"[ReprendreConversationVue] Erreur renommage conv={self.conv.id} : {e}")
            return ReprendreConversationVue(self.conv, "Échec du renommage.")

    def _supprimer(self):
        confirm = inquirer.confirm(
            message=f"Supprimer définitivement « {self.conv.nom} » ?",
            default=False,
        ).execute()
        if not confirm:
            return ReprendreConversationVue(self.conv)

        try:
            ConversationService.supprimer_conversation(self.conv.id)
            from view.conversations_vue import ConversationsVue

            return ConversationsVue("Conversation supprimée.")
        except Exception as e:
            logging.error(
                f"[ReprendreConversationVue] Erreur suppression conv={self.conv.id} : {e}"
            )
            return ReprendreConversationVue(self.conv, "Échec de la suppression.")

    def choisir_menu(self):
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
                "Changer la personnalisation",
                "Ajouter un participant",
                "Retirer un participant",
                "Renommer la conversation",
                "Supprimer la conversation",
                "↩︎ Retour à la liste des conversations",
            ],
            cycle=True,
        ).execute()

        match choix:
            case "Envoyer un message":
                return self._envoyer_message()
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
