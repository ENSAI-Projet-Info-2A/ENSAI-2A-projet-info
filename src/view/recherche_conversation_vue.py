import logging
from datetime import datetime

from InquirerPy import inquirer

from src.service.conversation_service import ConversationService, ErreurValidation
from src.view.reprendre_conversation_vue import ReprendreConversationVue
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class RechercheConversationVue(VueAbstraite):
    """Vue de recherche de conversations par mot-clé et/ou date."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        logging.debug("Entrée dans RechercheConversationVue (message=%r)", self.message)

        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            logging.warning(
                "[RechercheConversationVue] Accès sans utilisateur connecté → retour AccueilVue"
            )
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour rechercher des conversations.")

        logging.debug(
            "[RechercheConversationVue] Recherche demandée par user_id=%s, pseudo=%r",
            utilisateur.id,
            utilisateur.pseudo,
        )

        print("\n" + "-" * 50)
        print("Rechercher une conversation")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        try:
            # 2) Saisie des critères
            mot_cle = inquirer.text(
                message="Mot-clé (laisser vide si aucun) : ", default=""
            ).execute()
            date_str = inquirer.text(
                message="Date (YYYY-MM-DD, laisser vide si aucune) : ", default=""
            ).execute()

            logging.debug(
                "[RechercheConversationVue] Critères saisis : mot_cle=%r, date_raw=%r",
                mot_cle,
                date_str,
            )

            mot_cle = (mot_cle or "").strip() or None
            date_recherche = None

            # 3) Parsing de la date si fournie
            if (date_str or "").strip():
                try:
                    dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                    logging.debug(
                        "[RechercheConversationVue] Date parsée : %s (mot_cle=%r)",
                        dt,
                        mot_cle,
                    )
                except ValueError:
                    logging.warning(
                        "[RechercheConversationVue] Format date invalide : %r", date_str
                    )
                    return RechercheConversationVue("Format de date invalide. Utilisez YYYY-MM-DD.")
                date_recherche = dt.date() if mot_cle else dt

            logging.info(
                "[RechercheConversationVue] Lancement recherche avec mot_cle=%r, date=%r, user_id=%s",
                mot_cle,
                date_recherche,
                utilisateur.id,
            )

            # 4) Appel service
            resultats = ConversationService.rechercher_conversations(
                id_utilisateur=utilisateur.id,
                mot_cle=mot_cle,
                date_recherche=date_recherche,
            )

            logging.info(
                "[RechercheConversationVue] %s conversation(s) trouvée(s) pour user_id=%s",
                len(resultats),
                utilisateur.id,
            )

            # 5) Si aucun résultat
            if not resultats:
                from src.view.menu_utilisateur_vue import MenuUtilisateurVue

                logging.info(
                    "[RechercheConversationVue] Aucun résultat pour user_id=%s",
                    utilisateur.id,
                )
                return MenuUtilisateurVue("Aucune conversation ne correspond à vos critères.")

            # 6) Affichage liste
            def fmt(conv) -> str:
                try:
                    d = conv.date_creation.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    d = str(conv.date_creation) if conv.date_creation is not None else "?"
                nom = (conv.nom or "(sans titre)").strip()
                return f"[#{conv.id}] {nom}  —  créée le {d}"

            choices = [{"name": fmt(c), "value": c} for c in resultats]
            choices.append({"name": "↩  Retour", "value": None})

            logging.debug(
                "[RechercheConversationVue] Affichage des résultats (%s items)",
                len(choices) - 1,
            )

            selection = inquirer.select(
                message="Choisissez une conversation :",
                choices=choices,
                default=choices[0]["value"],
            ).execute()

            logging.info(
                "[RechercheConversationVue] Conversation sélectionnée : %r",
                selection.id if selection else None,
            )

            if selection is None:
                logging.info("[RechercheConversationVue] Retour au MenuUtilisateurVue")
                from src.view.menu_utilisateur_vue import MenuUtilisateurVue

                return MenuUtilisateurVue()

            # 7) Ouvrir la conversation choisie
            logging.info(
                "[RechercheConversationVue] Ouverture conversation conv_id=%s",
                selection.id,
            )
            return ReprendreConversationVue(selection)

        except ErreurValidation as e:
            logging.warning("[RechercheConversationVue] Erreur validation : %s", e)
            return RechercheConversationVue(f"{e}")

        except Exception as e:
            logging.error(f"[RechercheConversationVue] Erreur inattendue : {e}")
            return RechercheConversationVue("Une erreur est survenue. Veuillez réessayer.")
