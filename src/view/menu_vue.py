from InquirerPy import inquirer

from view.session import Session
from view.vue_abstraite import VueAbstraite


class MenuUtilisateurVue(VueAbstraite):
    """
    Vue du menu principal de l'utilisateur (tableau de bord ensaiGPT).
    """

    def __init__(self, message: str = ""):
        self.message = message

    def choisir_menu(self):
        """Affiche le menu principal et renvoie la prochaine vue à afficher."""

        print("\n" + "-" * 50)
        print(f"Bienvenue, {Session().utilisateur.pseudo} !")
        print("-" * 50 + "\n")

        if self.message:
            print(self.message + "\n")

        choix = inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=[
                "Voir mes conversations",
                "Créer une nouvelle conversation",
                "Rechercher dans mes conversations",
                "Voir mes statistiques",
                "Personnaliser mon assistant",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                Session().deconnexion()
                from view.accueil.connexion_vue import ConnexionVue

                return ConnexionVue()

            case "Voir mes conversations":
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
