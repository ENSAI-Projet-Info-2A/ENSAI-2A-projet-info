from InquirerPy import inquirer

from src.utils.reset_database import ResetDatabase
from src.view.session import Session
from src.view.vue_abstraite import VueAbstraite


class AccueilVue(VueAbstraite):
    """Vue d'accueil de l'application"""

    def choisir_menu(self):
        """Choix du menu suivant

        Return
        ------
        view
            Retourne la vue choisie par l'utilisateur dans le terminal
        """

        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Se connecter",
                "Créer un compte",
                "Ré-initialiser la base de données",
                "Infos de session",
                "Quitter",
            ],
        ).execute()

        match choix:
            case "Quitter":
                pass

            case "Se connecter":
                print("Here : Con 1")
                try:
                    from src.view.accueil.connexion_vue import ConnexionVue

                    print("Here : Con 2 (import OK)")
                    return ConnexionVue("Connexion à l'application")
                except Exception:
                    import traceback

                    print("Here : Con IMPORT FAILED")
                    traceback.print_exc()
                    from src.view.accueil.accueil_vue import AccueilVue
                return AccueilVue(f"Échec import ConnexionVue : {Exception}")

            case "Créer un compte":
                from src.view.accueil.inscription_vue import InscriptionVue

                return InscriptionVue("Création de compte joueur")

            case "Infos de session":
                return AccueilVue(Session().afficher())

            case "Ré-initialiser la base de données":
                succes = ResetDatabase().lancer()
                message = (
                    f"Ré-initilisation de la base de données - {'SUCCES' if succes else 'ECHEC'}"
                )
                return AccueilVue(message)
