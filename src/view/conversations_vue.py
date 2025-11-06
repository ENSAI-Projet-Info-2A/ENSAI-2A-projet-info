import logging

from InquirerPy import inquirer

from service.conversation_service import ConversationService, ErreurValidation
from view.session import Session
from view.vue_abstraite import VueAbstraite


class ConversationsVue(VueAbstraite):
    """Vue listant les conversations de l'utilisateur et actions associées."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            from view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour accéder à vos conversations.")

        # 2) En-tête
        print("\n" + "-" * 50)
        print(f"Mes conversations — {utilisateur.pseudo}")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        # 3) Charger la liste des conversations
        try:
            conversations = (
                ConversationService.lister_conversations(id_utilisateur=utilisateur.id, limite=None)
                or []
            )
        except Exception as e:
            logging.error(f"[ConversationsVue] Erreur chargement conversations : {e}")
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Impossible de charger vos conversations pour le moment.")

        if not conversations:
            # Aucun résultat -> proposer de créer une conversation ou revenir
            choix = inquirer.select(
                message="Vous n'avez encore aucune conversation.",
                choices=[
                    "Créer une nouvelle conversation",
                    "Retour au menu",
                ],
            ).execute()
            if choix == "Créer une nouvelle conversation":
                from view.nouvelle_conversation_vue import NouvelleConversationVue

                return NouvelleConversationVue()
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue()

        # 4) Construire la liste des choix
        mapping = {}
        items = []
        for conv in conversations:
            # conv.nom / conv.id présents selon ton BO
            label = f"[{conv.id}] {conv.nom}"
            items.append(label)
            mapping[label] = conv

        items.append("↩︎ Retour au menu")

        try:
            selection = inquirer.select(
                message="Sélectionnez une conversation :",
                choices=items,
                cycle=True,
            ).execute()

            if selection == "↩︎ Retour au menu":
                from view.menu_utilisateur_vue import MenuUtilisateurVue

                return MenuUtilisateurVue()

            conv = mapping[selection]

            # 5) Sous-menu d'actions sur la conversation choisie
            action = inquirer.select(
                message=f"Conversation « {conv.nom} » — que voulez-vous faire ?",
                choices=[
                    "Ouvrir (voir les derniers messages)",
                    "Renommer",
                    "Supprimer",
                    "↩︎ Retour à la liste",
                ],
                cycle=True,
            ).execute()

            match action:
                case "Ouvrir (voir les derniers messages)":
                    # On lit les 20 derniers messages (offset 0, limit 20)
                    try:
                        echanges = (
                            ConversationService.lire_fil(
                                id_conversation=conv.id, decalage=0, limite=20
                            )
                            or []
                        )
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur lire_fil conv={conv.id} : {e}")
                        return ConversationsVue(
                            "Impossible d'afficher les messages de cette conversation."
                        )

                    print("\n" + "-" * 50)
                    print(f"Conversation « {conv.nom} » — derniers messages")
                    print("-" * 50 + "\n")

                    if not echanges:
                        print("(Aucun message pour l’instant)\n")
                    else:
                        # echange.agent / echange.message / echange.date_msg selon ton BO côté DAO
                        for e in echanges:
                            auteur = getattr(e, "agent", getattr(e, "expediteur", ""))
                            contenu = getattr(e, "message", getattr(e, "contenu", ""))
                            date_msg = getattr(e, "date_msg", getattr(e, "date_echange", ""))
                            print(f"- {auteur} | {date_msg} : {contenu}")

                        print()

                    # Attendre entrée pour revenir à la liste
                    inquirer.text(
                        message="Appuyez sur Entrée pour revenir à la liste...",
                        default="",
                    ).execute()
                    return ConversationsVue()

                case "Renommer":
                    try:
                        nouveau = inquirer.text(
                            message="Nouveau titre : ",
                            default=conv.nom,
                            validate=lambda x: len(x.strip()) > 0 and len(x.strip()) <= 255,
                            invalid_message="Le titre ne doit pas être vide et ≤ 255 caractères.",
                        ).execute()
                        ConversationService.renommer_conversation(conv.id, nouveau.strip())
                        return ConversationsVue(
                            f"Titre modifié en « {nouveau.strip()} »."
                        )  # refresh
                    except ErreurValidation as e:
                        return ConversationsVue(str(e))
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur renommage conv={conv.id} : {e}")
                        return ConversationsVue("Échec du renommage, veuillez réessayer.")

                case "Supprimer":
                    confirm = inquirer.confirm(
                        message=f"Supprimer définitivement « {conv.nom} » ?",
                        default=False,
                    ).execute()
                    if not confirm:
                        return ConversationsVue()

                    try:
                        ConversationService.supprimer_conversation(conv.id)
                        return ConversationsVue("Conversation supprimée.")
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur suppression conv={conv.id} : {e}")
                        return ConversationsVue("Échec de la suppression, veuillez réessayer.")

                case "↩︎ Retour à la liste":
                    return ConversationsVue()

        except Exception as e:
            logging.error(f"[ConversationsVue] Erreur : {e}")
            return ConversationsVue("Une erreur est survenue, veuillez réessayer.")
