# src/view/menu_utilisateur_vue.py

from InquirerPy import inquirer

from view.session import Session
from view.vue_abstraite import VueAbstraite


class MenuUtilisateurVue(VueAbstraite):
    """Vue du menu de l'utilisateur

    Attributes
    ----------
    message : str
        Message optionnel affiché en haut du menu.

    Returns
    -------
    view
        Retourne la prochaine vue, choisie par l'utilisateur.
    """

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        """Choix du menu suivant de l'utilisateur.

        Returns
        -------
        vue
            La vue suivante à afficher.
        """
        # Sécurité : si pas connecté, retour à l'accueil
        if Session().utilisateur is None:
            from view.accueil.accueil_vue import AccueilVue

            return AccueilVue("Veuillez vous connecter.")

        utilisateur = Session().utilisateur

        print("\n" + "-" * 50 + f"\nMenu Utilisateur — {utilisateur.pseudo}\n" + "-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Voir mes conversations",
                "Créer une nouvelle conversation",
                "Rechercher dans mes conversations",
                "Voir mes statistiques",
                "Personnaliser mon assistant",
                "Infos de session",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue

                return AccueilVue("Déconnexion effectuée.")

            case "Infos de session":
                return MenuUtilisateurVue(Session().afficher())

            case "Voir mes conversations":
                # Liste les conversations de l'utilisateur
                from view.conversations_vue import ConversationsVue

                return ConversationsVue()

            case "Créer une nouvelle conversation":
                from view.nouvelle_conversation_vue import NouvelleConversationVue

                return NouvelleConversationVue()

            case "Rechercher dans mes conversations":
                from view.recherche_vue import RechercheVue

                return RechercheVue()

            case "Voir mes statistiques":
                from view.stats_vue import StatsVue

                return StatsVue()

            case "Personnaliser mon assistant":
                from view.personnalisation_vue import PersonnalisationVue

                return PersonnalisationVue()
