import logging

from InquirerPy import inquirer

from src.service.conversation_service import ConversationService, ErreurValidation
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class ConversationsVue(VueAbstraite):
    """Vue listant les conversations de l'utilisateur et actions associées."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        logging.debug("Entrée dans ConversationsVue (message=%r)", self.message)

        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            logging.warning(
                "[ConversationsVue] Accès sans utilisateur connecté, redirection vers AccueilVue."
            )
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour accéder à vos conversations.")

        # 2) En-tête
        print("\n" + "-" * 50)
        print(f"Mes conversations — {utilisateur.pseudo}")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        # 3) Charger la liste des conversations
        try:
            logging.debug(
                "[ConversationsVue] Chargement des conversations pour user_id=%s",
                utilisateur.id,
            )
            conversations = (
                ConversationService.lister_conversations(
                    id_utilisateur=utilisateur.id,
                    limite=None,
                )
                or []
            )
            logging.info(
                "[ConversationsVue] %s conversation(s) récupérée(s) pour user_id=%s",
                len(conversations),
                utilisateur.id,
            )
        except Exception as e:
            logging.error(f"[ConversationsVue] Erreur chargement conversations : {e}")
            from src.view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Impossible de charger vos conversations pour le moment.")

        if not conversations:
            # Aucun résultat -> proposer de créer une conversation ou revenir
            logging.info(
                "[ConversationsVue] Aucune conversation trouvée pour user_id=%s",
                utilisateur.id,
            )
            choix = inquirer.select(
                message="Vous n'avez encore aucune conversation.",
                choices=[
                    "Créer une nouvelle conversation",
                    "Retour au menu",
                ],
            ).execute()
            logging.info(
                "[ConversationsVue] Choix utilisateur sans conversation : %r",
                choix,
            )
            if choix == "Créer une nouvelle conversation":
                from src.view.nouvelle_conversation_vue import NouvelleConversationVue

                logging.info(
                    "[ConversationsVue] Redirection vers NouvelleConversationVue (création conv)."
                )
                return NouvelleConversationVue()
            from src.view.menu_utilisateur_vue import MenuUtilisateurVue

            logging.info(
                "[ConversationsVue] Redirection vers MenuUtilisateurVue (aucune conversation)."
            )
            return MenuUtilisateurVue()

        # 4) Construire la liste des choix
        mapping = {}
        items = []
        for conv in conversations:
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

            logging.info("[ConversationsVue] Conversation sélectionnée : %r", selection)

            if selection == "↩︎ Retour au menu":
                from src.view.menu_utilisateur_vue import MenuUtilisateurVue

                logging.info(
                    "[ConversationsVue] L'utilisateur a choisi de revenir au menu utilisateur."
                )
                return MenuUtilisateurVue()

            conv = mapping[selection]
            logging.debug(
                "[ConversationsVue] conv_id=%s sélectionnée (titre=%r)",
                conv.id,
                conv.nom,
            )

            # 5) Sous-menu d'actions sur la conversation choisie
            action = inquirer.select(
                message=f"Conversation « {conv.nom} » — que voulez-vous faire ?",
                choices=[
                    "Reprendre la discussion",
                    "Renommer",
                    "Supprimer",
                    "Exporter (.txt)",
                    "Exporter (.json)",
                    "↩︎ Retour à la liste",
                ],
                cycle=True,
            ).execute()

            logging.info(
                "[ConversationsVue] Action sélectionnée sur conv_id=%s : %r",
                conv.id,
                action,
            )

            match action:
                case "Reprendre la discussion":
                    from src.view.reprendre_conversation_vue import ReprendreConversationVue

                    logging.info(
                        "[ConversationsVue] Reprise de la discussion pour conv_id=%s",
                        conv.id,
                    )
                    return ReprendreConversationVue(conv)

                case "Renommer":
                    try:
                        nouveau = inquirer.text(
                            message="Nouveau titre : ",
                            default=conv.nom,
                            validate=lambda x: len(x.strip()) > 0 and len(x.strip()) <= 255,
                            invalid_message="Le titre ne doit pas être vide et ≤ 255 caractères.",
                        ).execute()
                        logging.debug(
                            "[ConversationsVue] Demande de renommage conv_id=%s -> %r",
                            conv.id,
                            nouveau,
                        )
                        ConversationService.renommer_conversation(conv.id, nouveau.strip())
                        logging.info(
                            "[ConversationsVue] Conversation %s renommée en %r",
                            conv.id,
                            nouveau.strip(),
                        )
                        return ConversationsVue(f"Titre modifié en « {nouveau.strip()} ».")

                    except ErreurValidation as e:
                        logging.warning(
                            "[ConversationsVue] Erreur validation lors du renommage conv_id=%s : %s",
                            conv.id,
                            e,
                        )
                        return ConversationsVue(str(e))
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur renommage conv={conv.id} : {e}")
                        return ConversationsVue("Échec du renommage, veuillez réessayer.")

                case "Supprimer":
                    logging.warning(
                        "[ConversationsVue] Demande de suppression pour conv_id=%s",
                        conv.id,
                    )
                    confirm = inquirer.confirm(
                        message=f"Supprimer définitivement « {conv.nom} » ?",
                        default=False,
                    ).execute()
                    logging.info(
                        "[ConversationsVue] Confirmation suppression conv_id=%s : %s",
                        conv.id,
                        confirm,
                    )
                    if not confirm:
                        return ConversationsVue()

                    try:
                        ConversationService.supprimer_conversation(
                            id_conversation=conv.id,
                            id_demandeur=utilisateur.id,
                        )
                        logging.info(
                            "[ConversationsVue] Conversation supprimée conv_id=%s",
                            conv.id,
                        )
                        return ConversationsVue("Conversation supprimée.")
                    except ErreurValidation as e:
                        # Par ex. utilisateur non propriétaire
                        logging.warning(
                            "[ConversationsVue] Erreur validation suppression conv_id=%s : %s",
                            conv.id,
                            e,
                        )
                        return ConversationsVue(f"Erreur : {e}")
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur suppression conv={conv.id} : {e}")
                        return ConversationsVue("Échec de la suppression, veuillez réessayer.")

                case "Exporter (.txt)":
                    logging.info(
                        "[ConversationsVue] Demande d'export .txt pour conv_id=%s",
                        conv.id,
                    )
                    try:
                        service = ConversationService()
                        service.exporter_conversation(conv.id, "txt")
                        logging.info(
                            "[ConversationsVue] Export .txt réussi pour conv_id=%s",
                            conv.id,
                        )
                        return ConversationsVue(
                            f"Conversation exportée dans le fichier 'conversation_{conv.id}.txt'."
                        )
                    except ErreurValidation as e:
                        logging.warning(
                            "[ConversationsVue] Erreur validation export conv_id=%s : %s",
                            conv.id,
                            e,
                        )
                        return ConversationsVue(str(e))
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur export conv={conv.id} : {e}")
                        return ConversationsVue("Échec de l'export, veuillez réessayer.")

                case "↩︎ Retour à la liste":
                    logging.info(
                        "[ConversationsVue] Retour à la liste des conversations pour user_id=%s",
                        utilisateur.id,
                    )
                    return ConversationsVue()

                case "Exporter (.json)":
                    logging.info(
                        "[ConversationsVue] Demande d'export .json pour conv_id=%s",
                        conv.id,
                    )
                    try:
                        service = ConversationService()
                        service.exporter_conversation(conv.id, "json")
                        logging.info(
                            "[ConversationsVue] Export .json réussi pour conv_id=%s",
                            conv.id,
                        )
                        return ConversationsVue(
                            f"Conversation exportée dans le fichier 'conversation_{conv.id}.json'."
                        )
                    except ErreurValidation as e:
                        logging.warning(
                            "[ConversationsVue] Erreur validation export conv_id=%s : %s",
                            conv.id,
                            e,
                        )
                        return ConversationsVue(str(e))
                    except Exception as e:
                        logging.error(f"[ConversationsVue] Erreur export conv={conv.id} : {e}")
                        return ConversationsVue("Échec de l'export, veuillez réessayer.")

        except Exception as e:
            logging.error(f"[ConversationsVue] Erreur : {e}")
            return ConversationsVue("Une erreur est survenue, veuillez réessayer.")
