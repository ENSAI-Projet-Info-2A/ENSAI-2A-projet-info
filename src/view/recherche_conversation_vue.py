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
        # 1) Sécurité : utilisateur connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter pour rechercher des conversations.")

        print("\n" + "-" * 50)
        print("Rechercher une conversation")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        try:
            # 2) Saisie des critères (facultatifs)
            mot_cle = inquirer.text(
                message="Mot-clé (laisser vide si aucun) : ", default=""
            ).execute()

            date_str = inquirer.text(
                message="Date (YYYY-MM-DD, laisser vide si aucune) : ", default=""
            ).execute()

            mot_cle = (mot_cle or "").strip() or None
            date_recherche = None

            # 3) Parsing de la date si fournie
            if (date_str or "").strip():
                try:
                    dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                except ValueError:
                    return RechercheConversationVue("Format de date invalide. Utilisez YYYY-MM-DD.")
                # Service : date vs datetime selon présence mot_cle (on garde ta logique)
                date_recherche = dt.date() if mot_cle else dt

            # 4) Appel service
            resultats = ConversationService.rechercher_conversations(
                id_utilisateur=utilisateur.id,
                mot_cle=mot_cle,
                date_recherche=date_recherche,
            )

            # 5) Si aucun résultat
            if not resultats:
                from src.view.menu_utilisateur_vue import MenuUtilisateurVue

                return MenuUtilisateurVue("Aucune conversation ne correspond à vos critères.")

            # 6) Menu Select pour choisir la conversation
            def fmt(conv) -> str:
                # robustesse sur la date
                try:
                    d = conv.date_creation.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    d = str(conv.date_creation) if conv.date_creation is not None else "?"
                nom = (conv.nom or "(sans titre)").strip()
                return f"[#{conv.id}] {nom}  —  créée le {d}"

            choices = [{"name": fmt(c), "value": c} for c in resultats]
            # Option retour
            choices.append({"name": "↩  Retour", "value": None})

            selection = inquirer.select(
                message="Choisissez une conversation :",
                choices=choices,
                default=choices[0]["value"],  # premier résultat par défaut
            ).execute()

            if selection is None:
                from src.view.menu_utilisateur_vue import MenuUtilisateurVue

                return MenuUtilisateurVue()

            # 7) Ouvrir la vue de reprise de la conversation sélectionnée
            return ReprendreConversationVue(selection)

        except ErreurValidation as e:
            return RechercheConversationVue(f"{e}")

        except Exception as e:
            logging.error(f"[RechercheConversationVue] Erreur inattendue : {e}")
            return RechercheConversationVue("Une erreur est survenue. Veuillez réessayer.")
