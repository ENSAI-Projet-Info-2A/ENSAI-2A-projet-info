import logging

from InquirerPy import inquirer

from src.dao.utilisateur_dao import UtilisateurDao
from src.service.auth_service import Auth_Service
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class MenuUtilisateurVue(VueAbstraite):
    """Vue principale du menu utilisateur (post-connexion)."""

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        """Affiche le menu utilisateur et gère la navigation."""
        # Vérifie que l'utilisateur est bien connecté
        utilisateur = Session().utilisateur
        if utilisateur is None:
            from src.view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter avant d'accéder au menu utilisateur.")

        print("\n" + "-" * 50)
        print(f"Menu Utilisateur — {utilisateur.pseudo}")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        try:
            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Voir mes conversations",
                    "Créer une nouvelle conversation",
                    "Rechercher une conversation",
                    "Voir mes statistiques",
                    "Infos de session",
                    "Se déconnecter",
                ],
            ).execute()

            match choix:
                case "Se déconnecter":
                    s = Session()
                    token = s.token
                    if token:
                        auth_service = Auth_Service(UtilisateurDao())
                        auth_service.se_deconnecter(token)
                    s.deconnexion()
                    from src.view.accueil.accueil_vue import AccueilVue

                    return AccueilVue("Déconnexion effectuée avec succès.")

                case "Infos de session":
                    return MenuUtilisateurVue(Session().afficher())

                case "Voir mes conversations":
                    from src.view.conversations_vue import ConversationsVue

                    return ConversationsVue()

                case "Créer une nouvelle conversation":
                    from src.view.nouvelle_conversation_vue import NouvelleConversationVue

                    return NouvelleConversationVue()

                case "Rechercher une conversation":
                    from src.view.recherche_conversation_vue import RechercheConversationVue

                    return RechercheConversationVue()

                case "Voir mes statistiques":
                    from src.view.stats_vue import StatsVue

                    return StatsVue()

        except Exception as e:
            logging.error(f"[MenuUtilisateurVue] Erreur : {e}")
            # Revenir sur la même vue avec un message d’erreur
            return MenuUtilisateurVue("Une erreur est survenue, veuillez réessayer.")

        # Par défaut, si rien n’a été choisi
        return MenuUtilisateurVue("Choix invalide ou annulé, veuillez réessayer.")
